"""Condense pipeline — raw retained sources → L3 → L2 → L1 → L0 (per topic).

Three map-reduce stages, each MAP → AGENT → REDUCE (the AStockOS social_sediment pattern):

  distill     each un-distilled source_ref → one L3 claim (+ credibility)
  aggregate   L3 claims grouped by facet → corroborated L2 findings (+ credibility)
  synthesize  L2 findings → L1 viewpoints (per facet) + the L0 worldview (+ open questions)

Iron rule: Python NEVER reasons. The AGENT step shells out to an isolated agent (claude -p via
ros/run/claude_cmd.sh, or ROS_AGENT_CMD for offline/stub runs) that reads the versioned methodology
markdown + a single unit payload and emits STRICT JSON. MAP and REDUCE are deterministic: MAP builds
the unit payloads, REDUCE validates and writes through the gated storage layer. Resumable: a unit
whose .out.json exists is skipped. Deterministic ids make re-writes idempotent upserts.

STALENESS GUARD: when distill writes new/changed L3, the aggregate + synthesize work caches are
invalidated so L2/L1/L0 re-derive instead of skipping as resumable (the recurring "L3 refreshed but
L2/L0 stayed stale" bug).

Usage (in-process): condense(slug, stage="all"|"distill"|"aggregate"|"synthesize").
"""
from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

from .. import api, paths
from ..storage import knowledge as K


def _methodology_dir() -> Path:
    return paths.root() / "control_plane" / "reasoning" / "methodology"


CLAUDE_CMD = paths.PKG_DIR / "run" / "claude_cmd.sh"

STAGE_PROTOCOLS = {
    "distill": ["knowledge_layering.md", "credibility_guide.md", "l3_distill_protocol.md"],
    "aggregate": ["knowledge_layering.md", "credibility_guide.md", "l2_aggregate_protocol.md"],
    "synthesize": ["knowledge_layering.md", "credibility_guide.md", "l1l0_synthesize_protocol.md"],
}
STAGE_ORDER = ["distill", "aggregate", "synthesize"]


# ---------------------------------------------------------------------------
# agent invocation (pluggable; deterministic stub via ROS_AGENT_CMD)
# ---------------------------------------------------------------------------
def _build_prompt(stage: str, payload: dict) -> str:
    parts = []
    mdir = _methodology_dir()
    for fname in STAGE_PROTOCOLS[stage]:
        fp = mdir / fname
        if fp.is_file():
            parts.append(fp.read_text(encoding="utf-8"))
    parts.append(
        "\n\n---\n\nTASK PAYLOAD (one condense unit; read it and emit STRICT JSON per the protocol):\n"
        + json.dumps(payload, ensure_ascii=False)
        + "\n\nOutput ONLY the JSON object described by the protocol. No prose, no code fences.")
    return "\n\n".join(parts)


def _run_agent(stage: str, in_path: Path, payload: dict) -> str:
    """Run ONE agent unit. Returns raw stdout. ROS_AGENT_CMD overrides the default claude -p path
    (used by tests/offline). The unit payload path + stage are exposed via env for simple stubs."""
    prompt = _build_prompt(stage, payload)
    env = {**os.environ, "ROS_AGENT_IN": str(in_path), "ROS_AGENT_STAGE": stage}
    override = os.environ.get("ROS_AGENT_CMD")
    if override:
        argv = shlex.split(override) + ["--", prompt]
    else:
        argv = ["bash", str(CLAUDE_CMD), prompt]
    try:
        result = subprocess.run(argv, capture_output=True, text=True, timeout=300, env=env)
    except FileNotFoundError as e:
        raise RuntimeError(f"agent command not found: {e}") from e
    if result.returncode != 0 and not result.stdout.strip():
        raise RuntimeError(f"agent failed (rc={result.returncode}): {result.stderr.strip()[-300:]}")
    return result.stdout


def _extract_json(text: str) -> dict:
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError(f"no JSON object in agent output: {text[:200]!r}")
    return json.loads(text[start:end + 1])


# ---------------------------------------------------------------------------
# workdir / cache
# ---------------------------------------------------------------------------
def _workdir(slug: str, stage: str) -> Path:
    d = paths.artifacts_dir(slug) / "condense" / stage
    d.mkdir(parents=True, exist_ok=True)
    return d


def _invalidate(slug: str, stage: str) -> None:
    d = paths.artifacts_dir(slug) / "condense" / stage
    if d.exists():
        shutil.rmtree(d)


def _cached_text(content_hash: str | None) -> str:
    if not content_hash:
        return ""
    fp = paths.library_source_path(content_hash)
    if not fp.is_file():
        return ""
    try:
        rec = json.loads(fp.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return ""
    return rec.get("cached_full_text") or rec.get("media_transcript") or rec.get("ocr_text") or ""


# ---------------------------------------------------------------------------
# generic per-stage runner: MAP -> (AGENT per unit) -> REDUCE
# ---------------------------------------------------------------------------
def _run_stage(slug: str, stage: str, *, log=print) -> dict:
    conn = api.get_conn(paths.knowledge_db(slug))
    try:
        units = _MAP[stage](conn, slug)
    finally:
        conn.close()
    wd = _workdir(slug, stage)
    ran = skipped = 0
    for unit_id, payload in units:
        out_path = wd / f"{unit_id}.out.json"
        in_path = wd / f"{unit_id}.in.json"
        in_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        if out_path.exists():
            skipped += 1
            continue
        raw = _run_agent(stage, in_path, payload)
        try:
            obj = _extract_json(raw)
        except (ValueError, json.JSONDecodeError) as e:
            (wd / f"{unit_id}.err").write_text(f"{e}\n---\n{raw[:1000]}", encoding="utf-8")
            log(f"  [{stage}] unit {unit_id}: bad agent JSON ({e})", file=sys.stderr)
            continue
        out_path.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")
        ran += 1

    # REDUCE: write every .out.json through the gated storage layer.
    conn = api.get_conn(paths.knowledge_db(slug))
    written = failed = 0
    try:
        for out_path in sorted(wd.glob("*.out.json")):
            unit_id = out_path.name[: -len(".out.json")]
            in_path = wd / f"{unit_id}.in.json"
            try:
                obj = json.loads(out_path.read_text(encoding="utf-8"))
                original = json.loads(in_path.read_text(encoding="utf-8")) if in_path.exists() else {}
                n = _REDUCE[stage](conn, slug, unit_id, original, obj)
                written += n
            except Exception as e:  # noqa: BLE001 — one bad unit must not abort the batch
                failed += 1
                (wd / f"{unit_id}.reduce.err").write_text(str(e), encoding="utf-8")
                log(f"  [{stage}] reduce {unit_id} failed: {e}", file=sys.stderr)
        conn.commit()
    finally:
        conn.close()
    return {"stage": stage, "units": len(units), "ran": ran, "skipped": skipped,
            "rows_written": written, "reduce_failed": failed}


# ===========================================================================
# DISTILL — source_ref → L3
# ===========================================================================
def _map_distill(conn, slug):
    rows = K._rows(conn,
        "SELECT s.* FROM source_ref s WHERE NOT EXISTS "
        "(SELECT 1 FROM l3_claim c WHERE c.single_source_ref_id = s.id)")
    units = []
    for s in rows:
        units.append((s["id"], {
            "source_ref_id": s["id"],
            "url": s["url"], "platform": s["platform"], "source_kind": s["source_kind"],
            "title": s.get("title"), "author": s.get("author"),
            "content_hash": s.get("content_hash"),
            "cached_text": _cached_text(s.get("content_hash")),
        }))
    return units


def _reduce_distill(conn, slug, unit_id, original, obj):
    src_id = original.get("source_ref_id") or unit_id
    l3_id = "sc-" + src_id.split("-", 1)[-1]
    cred = obj.get("credibility") or {}
    cred_id = api.record_credibility(
        conn, subject_type="l3_claim", subject_id=l3_id,
        level=cred.get("level", "low"), rationale=cred.get("rationale") or "agent distill",
        filter_trace=cred.get("filter_trace") or {"phase": "distill"},
        independence_note=cred.get("independence_note"),
        echo_chamber_flag=1 if cred.get("echo_chamber_flag") else 0)
    api.upsert_l3_claim(
        conn, id=l3_id, proposition=obj["proposition"], claim_kind=obj.get("claim_kind", "other"),
        single_source_ref_id=src_id, source_ref_ids=[src_id], credibility_id=cred_id,
        filter_trace=obj.get("filter_trace") or cred.get("filter_trace") or {"phase": "distill"},
        facet=obj.get("facet"), source_kind=_l3_source_kind(original.get("source_kind")),
        verbatim_excerpt=obj.get("verbatim_excerpt"), analysis_note=obj.get("analysis_note"),
        cached_text_hash=original.get("content_hash"), updated_by="condense-distill")
    return 1


def _l3_source_kind(intake_kind: str | None) -> str | None:
    # map intake source_kind (article/note/post/video/image/...) onto l3_claim.source_kind CHECK set
    m = {"article": "article", "web_page": "article", "news": "article", "report": "paper",
         "paper": "paper", "post": "post", "note": "post", "video": "video", "image": "image",
         "screenshot": "image", "forum": "forum"}
    return m.get((intake_kind or "").lower(), "other") if intake_kind else None


# ===========================================================================
# AGGREGATE — L3 (by facet) → L2 corroborated findings
# ===========================================================================
def _map_aggregate(conn, slug):
    claims = K._rows(conn, "SELECT * FROM l3_claim WHERE status='active'")
    by_facet: dict[str, list] = {}
    for c in claims:
        by_facet.setdefault(c.get("facet") or "_unfileted", []).append(c)
    units = []
    for facet, rows in by_facet.items():
        units.append((_facet_unit_id(facet), {
            "facet": facet,
            "claims": [{
                "l3_id": c["id"], "proposition": c["proposition"], "claim_kind": c["claim_kind"],
                "source_ref_id": c["single_source_ref_id"], "platform": _platform_of(conn, c["single_source_ref_id"]),
            } for c in rows],
        }))
    return units


def _reduce_aggregate(conn, slug, unit_id, original, obj):
    # deterministic map l3_id -> (source_ref_id, platform) for Python-side corroboration counting
    claim_idx = {c["l3_id"]: c for c in original.get("claims", [])}
    facet = original.get("facet")
    written = 0
    for f in obj.get("findings", []):
        l3_ids = [x for x in (f.get("l3_ids") or []) if x in claim_idx]
        if not l3_ids:
            continue
        src_ids = _dedupe([claim_idx[i]["source_ref_id"] for i in l3_ids])
        platforms = _dedupe([claim_idx[i].get("platform") for i in l3_ids if claim_idx[i].get("platform")])
        l2_id = "sf-" + api.content_sha256(f"{facet}|{f.get('statement','')}")[:12]
        cred = f.get("credibility") or {}
        cred_id = api.record_credibility(
            conn, subject_type="l2_finding", subject_id=l2_id,
            level=cred.get("level", "low"), rationale=cred.get("rationale") or "agent aggregate",
            filter_trace=cred.get("filter_trace") or {"phase": "aggregate"},
            echo_chamber_flag=1 if cred.get("echo_chamber_flag") else 0)
        api.upsert_l2_finding(
            conn, id=l2_id, finding_type=f.get("finding_type", "claim"), statement=f["statement"],
            facet=facet, source_ref_ids=src_ids, credibility_id=cred_id,
            corroboration_count=len(src_ids), cross_platform_count=max(1, len(platforms)),
            corroboration_sources=platforms or None, conflict_note=f.get("conflict_note"),
            l3_ids=l3_ids, updated_by="condense-aggregate")
        written += 1
    return written


# ===========================================================================
# SYNTHESIZE — L2 → L1 viewpoints (per facet) + L0 worldview
# ===========================================================================
def _map_synthesize(conn, slug):
    findings = K._rows(conn, "SELECT * FROM l2_finding WHERE status='active'")
    if not findings:
        return []
    by_facet: dict[str, list] = {}
    for f in findings:
        by_facet.setdefault(f.get("facet") or "_unfileted", []).append(f)
    payload = {"facets": [{
        "facet": facet,
        "findings": [{
            "l2_id": f["id"], "statement": f["statement"], "finding_type": f["finding_type"],
            "corroboration_count": f["corroboration_count"], "cross_platform_count": f["cross_platform_count"],
            "source_ref_ids": json.loads(f["source_ref_ids"]),
        } for f in rows],
    } for facet, rows in by_facet.items()]}
    return [("topic", payload)]


def _reduce_synthesize(conn, slug, unit_id, original, obj):
    # l2_id -> source_ref_ids (for deterministic union up the ladder)
    l2_idx = {}
    for fb in original.get("facets", []):
        for fnd in fb.get("findings", []):
            l2_idx[fnd["l2_id"]] = fnd.get("source_ref_ids", [])
    written = 0
    l1_ids: list[str] = []
    all_src: list[str] = []
    for vp in obj.get("viewpoints", []):
        cited = [x for x in (vp.get("l2_ids") or []) if x in l2_idx]
        src_ids = _dedupe([s for i in cited for s in l2_idx.get(i, [])])
        if not src_ids:
            continue
        l1_id = "vp-" + api.content_sha256(f"{vp.get('facet')}|{vp.get('narrative','')[:80]}")[:12]
        cred = vp.get("credibility") or {}
        cred_id = api.record_credibility(
            conn, subject_type="l1_viewpoint", subject_id=l1_id,
            level=cred.get("level", "low"), rationale=cred.get("rationale") or "agent synthesize",
            filter_trace=cred.get("filter_trace") or {"phase": "synthesize"})
        api.upsert_l1_viewpoint(
            conn, id=l1_id, synthesis_kind=vp.get("synthesis_kind", "theme"),
            narrative=vp["narrative"], facet=vp.get("facet"), stance=vp.get("stance"),
            l2_ids=cited, open_questions=vp.get("open_questions"), confidence=vp.get("confidence"),
            source_ref_ids=src_ids, credibility_id=cred_id, updated_by="condense-synthesize")
        l1_ids.append(l1_id)
        all_src.extend(src_ids)
        written += 1

    wv = obj.get("worldview")
    if wv and l1_ids:
        l0_id = "wv-" + api.content_sha256(slug)[:12]
        src_ids = _dedupe(all_src)
        cred = wv.get("credibility") or {}
        cred_id = api.record_credibility(
            conn, subject_type="l0_worldview", subject_id=l0_id,
            level=cred.get("level", "low"), rationale=cred.get("rationale") or "agent worldview",
            filter_trace=cred.get("filter_trace") or {"phase": "synthesize"})
        existing = conn.execute("SELECT id FROM l0_worldview WHERE id=?", (l0_id,)).fetchone()
        api.upsert_l0_worldview(
            conn, id=l0_id, summary_kind=wv.get("summary_kind", "state_of_understanding"),
            proposition=wv["proposition"], confidence=wv.get("confidence"),
            key_findings=wv.get("key_findings"), open_questions=wv.get("open_questions"),
            l1_ids=l1_ids, source_ref_ids=src_ids,
            credibility_id=cred_id, supersedes_id=l0_id if existing else None,
            updated_by="condense-synthesize")
        _write_open_questions(conn, wv.get("open_questions") or [], l0_id)
        written += 1
    return written


def _write_open_questions(conn, questions, l0_id):
    for q in questions:
        if not q or not str(q).strip():
            continue
        oq_id = "oq-" + api.content_sha256(str(q))[:12]
        exists = conn.execute("SELECT id FROM open_question WHERE id=?", (oq_id,)).fetchone()
        if not exists:
            conn.execute(
                "INSERT INTO open_question (id,question,status,spawned_from_l_id) VALUES (?,?,?,?)",
                (oq_id, str(q), "open", l0_id))


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _facet_unit_id(facet: str) -> str:
    return "facet_" + api.content_sha256(facet)[:12]


def _platform_of(conn, src_id: str) -> str | None:
    row = conn.execute("SELECT platform FROM source_ref WHERE id=?", (src_id,)).fetchone()
    return row["platform"] if row else None


def _dedupe(xs):
    seen, out = set(), []
    for x in xs:
        if x is not None and x not in seen:
            seen.add(x)
            out.append(x)
    return out


_MAP = {"distill": _map_distill, "aggregate": _map_aggregate, "synthesize": _map_synthesize}
_REDUCE = {"distill": _reduce_distill, "aggregate": _reduce_aggregate, "synthesize": _reduce_synthesize}


# ---------------------------------------------------------------------------
# orchestration + staleness guard
# ---------------------------------------------------------------------------
def _l3_count(slug: str) -> int:
    conn = api.get_conn(paths.knowledge_db(slug))
    try:
        return int(conn.execute("SELECT count(*) FROM l3_claim").fetchone()[0])
    finally:
        conn.close()


def condense(slug: str, stage: str = "all", *, log=print) -> dict:
    """Run the condense chain (or a single stage). Returns a per-stage summary dict."""
    results = {}
    if stage != "all":
        results[stage] = _run_stage(slug, stage, log=log)
        return results

    # full chain with the L3-staleness guard
    before = _l3_count(slug)
    results["distill"] = _run_stage(slug, "distill", log=log)
    after = _l3_count(slug)
    if after != before or results["distill"]["rows_written"] > 0:
        _invalidate(slug, "aggregate")
        _invalidate(slug, "synthesize")
        log(f"[guard] L3 changed ({before}->{after}); invalidated aggregate+synthesize caches")
    results["aggregate"] = _run_stage(slug, "aggregate", log=log)
    # L2 changed → synthesize cache stale
    if results["aggregate"]["rows_written"] > 0:
        _invalidate(slug, "synthesize")
    results["synthesize"] = _run_stage(slug, "synthesize", log=log)
    return results


def resediment(slug: str, *, force: bool = False, log=print) -> dict:
    """Drift re-condense: invalidate work caches so knowledge re-derives from the CURRENT sources.

    Use after a source was enriched (e.g. a video transcribed / image OCR'd post-hoc) or L3 was
    edited outside the normal flow. `force` also clears the distill cache (re-distills every source —
    expensive); otherwise only L2/L1/L0 re-derive from existing L3. Upserts are idempotent, so this
    is safe to re-run.
    """
    if force:
        _invalidate(slug, "distill")
    _invalidate(slug, "aggregate")
    _invalidate(slug, "synthesize")
    log(f"[resediment] cleared caches (force={force}); re-condensing '{slug}'")
    return condense(slug, "all", log=log)
