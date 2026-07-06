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

import fcntl
import json
import os
import shlex
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
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


def _agent_timeout() -> int:
    """Per-unit agent timeout (seconds). Default 600: under concurrency the Claude API can queue/
    rate-limit a request, inflating per-call latency well past the ~60s serial baseline; 300s was
    too tight and let a single slow unit abort the whole batch. Override via ROS_AGENT_TIMEOUT."""
    raw = os.environ.get("ROS_AGENT_TIMEOUT", "600")
    try:
        return max(60, int(raw))
    except ValueError:
        return 600


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
        result = subprocess.run(argv, capture_output=True, text=True,
                                timeout=_agent_timeout(), env=env)
    except FileNotFoundError as e:
        raise RuntimeError(f"agent command not found: {e}") from e
    if result.returncode != 0 and not result.stdout.strip():
        raise RuntimeError(f"agent failed (rc={result.returncode}): {result.stderr.strip()[-300:]}")
    return result.stdout


def _extract_json(text: str) -> dict:
    """Extract the first balanced JSON object from agent output.

    Output is supposed to be STRICT JSON, but the agent sometimes decorates it with prose or a
    ```json fence. The naive first-'{' to last-'}' slice breaks when prose contains braces (a
    '{ref: §2}' note, a fenced block) — json.loads rejects the prefix/trailing garbage and a valid
    unit is needlessly marked bad-json (W-20). Strip fences first; if the naive slice still fails,
    scan for the first balanced object with raw_decode (tolerates trailing prose)."""
    s = (text or "").strip()
    # strip one wrapping code fence (```json ... ``` / ``` ... ```)
    if s.startswith("```"):
        s = s.split("\n", 1)[1] if "\n" in s else ""
        if s.endswith("```"):
            s = s[:-3]
        s = s.strip()
    # fast path: first '{' to matching last '}'
    start, end = s.find("{"), s.rfind("}")
    if start != -1 and end != -1 and end >= start:
        try:
            obj = json.loads(s[start:end + 1])
            if isinstance(obj, dict):
                return obj
        except json.JSONDecodeError:
            pass
    # slow path: raw_decode at each '{' until one parses a balanced object
    dec = json.JSONDecoder()
    for i in range(len(s)):
        if s[i] == "{":
            try:
                obj, _consumed = dec.raw_decode(s[i:])
                if isinstance(obj, dict):
                    return obj
            except json.JSONDecodeError:
                continue
    raise ValueError(f"no JSON object in agent output: {text[:200]!r}")


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
def _concurrency() -> int:
    """Agent-call fan-out for the MAP step. 1 = legacy serial. claude -p is subprocess-bound, so
    threads are sufficient (the GIL is released during subprocess.run). Sweet spot ~4–6: higher
    invites Claude API rate-limiting, which makes it slower, not faster."""
    raw = os.environ.get("ROS_CONCURRENCY", "4")
    try:
        n = int(raw)
    except ValueError:
        n = 4
    return max(1, n)


def _claim_unit(wd: Path, unit_id: str) -> bool:
    """Atomically claim a unit so concurrent workers don't run the same one twice. O_CREAT|O_EXCL
    is atomic across threads/processes; a unit already in flight (or whose .out.json a prior run
    left) returns False. On success the caller owns it and must clean up the lock."""
    lock = wd / f"{unit_id}.lock"
    try:
        fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.close(fd)
        return True
    except FileExistsError:
        return False


def _map_unit(wd: Path, stage: str, unit_id: str, payload: dict) -> tuple[str, str]:
    """Run ONE agent unit under a worker. Returns (unit_id, status): 'ran' / 'skipped' /
    'claimed-by-other' / 'bad-json' / 'error'. Writes {id}.out.json on success. Idempotent: a
    pre-existing .out.json means skip. The .lock guards against two workers picking the same unit
    in the gap between "out.json absent" and "out.json written".

    CRITICAL: this must never raise. Under concurrency, one slow/timed-out unit (the Claude API
    rate-limits/queues under fan-out, inflating per-call latency) must not abort the whole batch —
    every other worker's progress would be lost. Any agent exception is captured to {id}.err and
    reported as 'error'; the unit stays un-done and will be retried on the next `ros condense`."""
    out_path = wd / f"{unit_id}.out.json"
    if out_path.exists():
        return unit_id, "skipped"
    if not _claim_unit(wd, unit_id):
        return unit_id, "claimed-by-other"
    try:
        try:
            raw = _run_agent(stage, wd / f"{unit_id}.in.json", payload)
        except Exception as e:  # noqa: BLE001 — timeout/runtime failure → log + skip, don't abort
            (wd / f"{unit_id}.err").write_text(f"{type(e).__name__}: {e}", encoding="utf-8")
            return unit_id, "error"
        try:
            obj = _extract_json(raw)
        except (ValueError, json.JSONDecodeError) as e:
            (wd / f"{unit_id}.err").write_text(f"{e}\n---\n{raw[:1000]}", encoding="utf-8")
            return unit_id, "bad-json"
        out_path.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")
        return unit_id, "ran"
    except Exception as e:  # noqa: BLE001 — W-15: an IO error (disk full / perms on .out.json write,
                           # or the .err write itself) must not abort the whole batch's REDUCE. The
                           # comment contract is "this must never raise"; honor it by capturing the
                           # IO failure to .err and reporting 'error' like an agent failure, so the
                           # unit retries next condense and every OTHER unit's .out.json still reduces.
        try:
            (wd / f"{unit_id}.err").write_text(f"io: {type(e).__name__}: {e}", encoding="utf-8")
        except Exception:
            pass
        return unit_id, "error"
    finally:
        try:
            (wd / f"{unit_id}.lock").unlink()
        except FileNotFoundError:
            pass


def _run_stage(slug: str, stage: str, *, log=print) -> dict:
    """Per-topic flock around the whole stage (W-14). Two concurrent `ros condense <slug>` used to
    race on the per-unit *.lock reap (_run_stage_inner deletes every *.lock at entry, defeating
    O_EXCL): process B deleted A's live unit locks, then O_EXCL-reclaimed A's in-flight units →
    double agent cost + a broken L0 supersedes chain. A topic-level exclusive flock held for the
    stage makes the per-unit reap safe — only one process is ever inside here per topic. Different
    topics get different lockfiles, so they don't block each other."""
    flock_path = paths.artifacts_dir(slug) / ".condense.flock"
    flock_path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(flock_path), os.O_CREAT | os.O_RDWR)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)  # blocks until exclusive (advisory; per-topic)
        return _run_stage_inner(slug, stage, log=log)
    finally:
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)


def _run_stage_inner(slug: str, stage: str, *, log=print) -> dict:
    conn = api.get_conn(paths.knowledge_db(slug))
    try:
        units = _MAP[stage](conn, slug)
    finally:
        conn.close()
    wd = _workdir(slug, stage)
    # Reap orphan claim-locks left by a prior interrupted run. Any .lock present at stage start is
    # necessarily stale: workers only live inside this function, so no legitimate holder exists.
    for stale in wd.glob("*.lock"):
        try:
            stale.unlink()
        except FileNotFoundError:
            pass
    # Materialize every payload first (cheap IO), then fan out only the un-done units.
    todo: list[tuple[str, dict]] = []
    skipped = 0
    for unit_id, payload in units:
        (wd / f"{unit_id}.in.json").write_text(json.dumps(payload, ensure_ascii=False),
                                               encoding="utf-8")
        if (wd / f"{unit_id}.out.json").exists():
            skipped += 1
        else:
            todo.append((unit_id, payload))

    workers = _concurrency()
    ran = 0
    errors = 0
    if workers == 1 or len(todo) <= 1:
        # Serial path — keeps stderr logs ordered and matches the legacy single-process behavior.
        for unit_id, payload in todo:
            _unit_id, status = _map_unit(wd, stage, unit_id, payload)
            if status == "bad-json":
                log(f"  [{stage}] unit {unit_id}: bad agent JSON", file=sys.stderr)
            elif status == "error":
                errors += 1
                log(f"  [{stage}] unit {unit_id}: agent error (see .err)", file=sys.stderr)
            ran += status == "ran"
    else:
        done = 0
        total = len(todo)
        with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="ros-agent") as pool:
            futures = {pool.submit(_map_unit, wd, stage, uid, pl): uid for uid, pl in todo}
            for fut in as_completed(futures):
                _unit_id, status = fut.result()
                if status == "bad-json":
                    log(f"  [{stage}] unit {_unit_id}: bad agent JSON", file=sys.stderr)
                elif status == "error":
                    errors += 1
                    log(f"  [{stage}] unit {_unit_id}: agent error (see .err)", file=sys.stderr)
                ran += status == "ran"
                done += 1
                log(f"  [{stage}] {done}/{total} done (ran={ran})", file=sys.stderr)

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
            "errors": errors, "rows_written": written, "reduce_failed": failed}


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
def _aggregate_chunk_size() -> int:
    """Max L3 claims per aggregate unit. A single agent call must read every claim in the bucket and
    emit corroborated findings, so a giant bucket (e.g. all un-filed claims) makes one prompt huge
    and slow enough to hit the agent timeout. Splitting a bucket into chunks keeps each call bounded;
    cross-chunk corroboration is recovered at the synthesize stage. Override via ROS_AGG_CHUNK."""
    raw = os.environ.get("ROS_AGG_CHUNK", "25")
    try:
        return max(5, int(raw))
    except ValueError:
        return 25


def _map_aggregate(conn, slug):
    claims = K._rows(conn, "SELECT * FROM l3_claim WHERE status='active'")
    by_facet: dict[str, list] = {}
    for c in claims:
        by_facet.setdefault(c.get("facet") or "_unfileted", []).append(c)
    chunk = _aggregate_chunk_size()
    units = []
    for facet, rows in by_facet.items():
        # Split oversized buckets into chunks so no single agent call gets an unbounded payload.
        # Each chunk keeps the real facet label (L2 ids are content-hashed, so chunked findings under
        # the same facet dedupe correctly); only the unit_id carries the chunk suffix.
        shards = [rows[i:i + chunk] for i in range(0, len(rows), chunk)] if chunk else [rows]
        for i, shard in enumerate(shards):
            uid = _facet_unit_id(facet) if len(shards) == 1 else f"{_facet_unit_id(facet)}__{i}"
            units.append((uid, {
                "facet": facet,
                "claims": [{
                    "l3_id": c["id"], "proposition": c["proposition"], "claim_kind": c["claim_kind"],
                    "source_ref_id": c["single_source_ref_id"], "platform": _platform_of(conn, c["single_source_ref_id"]),
                } for c in shard],
            }))
    return units


# finding_type CHECK constraint whitelist (must mirror the l2_finding schema CHECK). The agent
# sometimes emits a near-synonym ("data", "analysis") that violates the CHECK and — without
# per-finding tolerance — would abort the whole chunk's REDUCE, losing every finding in it.
# 'other' is the NEUTRAL bucket (migration 0003): an unrecognized type maps to 'other', NOT to the
# meaning-bearing 'claim' (which would be a Python semantic decision — an iron-rule violation).
_L2_FINDING_TYPES = {"fact", "event", "figure", "claim", "trend", "other"}


def _reduce_aggregate(conn, slug, unit_id, original, obj):
    # deterministic map l3_id -> (source_ref_id, platform) for Python-side corroboration counting
    claim_idx = {c["l3_id"]: c for c in original.get("claims", [])}
    facet = original.get("facet")
    written = 0
    for f in obj.get("findings", []):
        # Per-finding tolerance: one malformed finding (bad finding_type, missing statement, an
        # l3_id the CHECK rejects) must not discard the other ~24 in the chunk. Drop just this one.
        try:
            l3_ids = [x for x in (f.get("l3_ids") or []) if x in claim_idx]
            if not l3_ids:
                continue
            src_ids = _dedupe([claim_idx[i]["source_ref_id"] for i in l3_ids])
            platforms = _dedupe([claim_idx[i].get("platform") for i in l3_ids if claim_idx[i].get("platform")])
            l2_id = "sf-" + api.content_sha256(f"{facet}|{f.get('statement','')}")[:12]
            # CROSS-CHUNK UNION (W-10): when a facet's claims are split into >ROS_AGG_CHUNK chunks,
            # two chunks can independently surface the same statement → identical l2_id. Previously
            # the second chunk's upsert OVERWROTE source_ref_ids / corroboration_count with a
            # strictly smaller set (the "cross-chunk corroboration is recovered at synthesize"
            # comment was FALSE — _map_synthesize forwards L2's stored counts verbatim, never
            # re-counting from L3). Union with the existing row so corroboration only ever grows.
            existing = conn.execute(
                "SELECT source_ref_ids, corroboration_sources, l3_ids FROM l2_finding WHERE id=?",
                (l2_id,)).fetchone()
            if existing is not None:
                src_ids = _dedupe(_json_list(existing["source_ref_ids"]) + src_ids)
                platforms = _dedupe(_json_list(existing["corroboration_sources"]) + platforms)
                l3_ids = _dedupe(_json_list(existing["l3_ids"]) + l3_ids)
            cred = f.get("credibility") or {}
            cred_id = api.record_credibility(
                conn, subject_type="l2_finding", subject_id=l2_id,
                level=cred.get("level", "low"), rationale=cred.get("rationale") or "agent aggregate",
                filter_trace=cred.get("filter_trace") or {"phase": "aggregate"},
                echo_chamber_flag=1 if cred.get("echo_chamber_flag") else 0)
            ftype = f.get("finding_type", "claim")
            if ftype not in _L2_FINDING_TYPES:  # agent synonym → NEUTRAL 'other', not 'claim' (W-13)
                ftype = "other"
            api.upsert_l2_finding(
                conn, id=l2_id, finding_type=ftype, statement=f["statement"],
                facet=facet, source_ref_ids=src_ids, credibility_id=cred_id,
                corroboration_count=len(src_ids), cross_platform_count=max(1, len(platforms)),
                corroboration_sources=platforms or None, conflict_note=f.get("conflict_note"),
                l3_ids=l3_ids, updated_by="condense-aggregate")
            written += 1
        except Exception:  # noqa: BLE001 — skip one bad finding, keep the rest of the chunk
            continue
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
    # current open questions, so the agent can mark which ones this round's L0/L2 actually answer
    # (the feedback loop's "open_questions shrink each round" closure). The agent decides; Python
    # only forwards them with stable ids it can echo back.
    open_qs = K._rows(conn, "SELECT id, question FROM open_question WHERE status='open'")
    payload = {
        "facets": [{
            "facet": facet,
            "findings": [{
                "l2_id": f["id"], "statement": f["statement"], "finding_type": f["finding_type"],
                "corroboration_count": f["corroboration_count"], "cross_platform_count": f["cross_platform_count"],
                "source_ref_ids": json.loads(f["source_ref_ids"]),
            } for f in rows],
        } for facet, rows in by_facet.items()],
        "open_questions": [{"oq_id": q["id"], "question": q["question"]} for q in open_qs],
    }
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
        # TRUE VERSION CHAIN: each run produces a new L0 row whose id encodes the new content
        # (slug + proposition + the cited L1 set). The prior active row is archived and the new
        # row's supersedes_id points at that real predecessor — not at itself. When the agent
        # re-emits byte-identical content, we reuse the prior id (whole-blob upsert, no version
        # churn). The "what counts as the same" decision is a pure string comparison, NOT a
        # semantic judgement — the agent owns all meaning.
        content_key = f"{slug}|{wv['proposition']}|{'|'.join(sorted(l1_ids))}"
        l0_id = "wv-" + api.content_sha256(content_key)[:16]
        prev = conn.execute(
            "SELECT id, proposition, l1_ids FROM l0_worldview "
            "WHERE status='active' ORDER BY updated_at DESC LIMIT 1").fetchone()
        prev_id = prev["id"] if prev else None
        prev_l1 = _json_set(prev["l1_ids"]) if prev else set()
        _archive_prev_id = None
        if prev_id and _json_set(json.dumps(l1_ids, ensure_ascii=False)) == prev_l1 \
                and prev["proposition"] == wv["proposition"]:
            # identical content → in-place upsert on the same row (no new version)
            l0_id = prev_id
        elif prev_id:
            # genuinely new version. Defer archiving the predecessor until AFTER the new row
            # inserts (W-09): the old archive→insert order left ZERO active L0 rows when upsert
            # raised (bad summary_kind / empty proposition) — the per-unit except swallowed the
            # error and conn.commit() persisted a lone archive, deleting the world model from
            # every consumer (ros report / ros topic open / world_model.md).
            _archive_prev_id = prev_id

        src_ids = _dedupe(all_src)
        cred = wv.get("credibility") or {}
        cred_id = api.record_credibility(
            conn, subject_type="l0_worldview", subject_id=l0_id,
            level=cred.get("level", "low"), rationale=cred.get("rationale") or "agent worldview",
            filter_trace=cred.get("filter_trace") or {"phase": "synthesize"})
        api.upsert_l0_worldview(
            conn, id=l0_id, summary_kind=wv.get("summary_kind", "state_of_understanding"),
            proposition=wv["proposition"], confidence=wv.get("confidence"),
            key_findings=wv.get("key_findings"), open_questions=wv.get("open_questions"),
            l1_ids=l1_ids, source_ref_ids=src_ids,
            credibility_id=cred_id, supersedes_id=prev_id,
            updated_by="condense-synthesize",
            audit_note=("version update" if l0_id == prev_id else "new version"))
        if _archive_prev_id is not None:
            # insert succeeded → retire the predecessor now so exactly one L0 stays active
            conn.execute(
                "UPDATE l0_worldview SET status='archived', "
                "audit_note=COALESCE(audit_note,'') || 'superseded by ' || ? WHERE id=?",
                (l0_id, _archive_prev_id))
            K._audit_change(conn, table_name="l0_worldview", row_id=_archive_prev_id, column_name="*",
                            change_kind="archive", changed_by="condense-synthesize",
                            diff_summary=f"archived → superseded by {l0_id}")
        _write_open_questions(conn, wv.get("open_questions") or [], l0_id)
        # close open questions the agent says this round actually answered (feedback-loop closure)
        _answer_open_questions(conn, obj.get("answered_oq_ids") or [], l0_id)
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


def _answer_open_questions(conn, oq_ids, l0_id):
    """Close the open_questions the agent says this round's worldview actually answered.

    The agent owns the semantic "is this question now resolved?" judgement. Python only: (1) applies
    the agent's explicit id list, (2) validates each id exists and is still 'open' (never blindly
    resurrects an already-answered/stale one), (3) records which L0 answered it. No string matching
    or heuristic is used to decide closure — that would violate the iron rule.
    """
    seen = set()
    for oid in oq_ids:
        if not oid or oid in seen:
            continue
        seen.add(oid)
        row = conn.execute(
            "SELECT id FROM open_question WHERE id=? AND status='open'", (oid,)).fetchone()
        if not row:
            continue
        conn.execute(
            "UPDATE open_question SET status='answered', answered_by_l_id=? WHERE id=?",
            (l0_id, oid))


def _json_set(j: str | None) -> set:
    """Best-effort parse of a stored JSON array into a set (for content-equality comparison)."""
    if not j:
        return set()
    try:
        v = json.loads(j)
        return set(v) if isinstance(v, list) else {v}
    except (json.JSONDecodeError, TypeError):
        return set()


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


def _json_list(s):
    """Parse a stored JSON array column into a list (defensive: [] on any parse issue). Used by the
    cross-chunk L2 union to read an existing row's source_ref_ids / corroboration_sources / l3_ids."""
    if not s:
        return []
    try:
        v = json.loads(s)
    except (json.JSONDecodeError, TypeError):
        return []
    return v if isinstance(v, list) else []


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
