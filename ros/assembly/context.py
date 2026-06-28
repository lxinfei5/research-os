"""Assemble + freeze the priming BRIEF — "use today's knowledge to aim tomorrow's search".

Deterministic load-all (no semantic trimming): the topic's current L0 worldview + open questions +
L1 viewpoints + per-facet gaps + recent search queries → a frozen context_snapshot (so any knowledge
written this round binds to exactly what was primed) → a brief the search agent reads. The brief
tells the agent: what's already established (skip re-searching), which thin/contested facets and open
questions to pursue, and which recent queries NOT to repeat.

At larger scale a curator (LLM keep-list under a token budget) would trim this; at MVP scale
load-all is fine and stays faithful to "Python never reasons".
"""
from __future__ import annotations

from .. import paths
from ..storage import knowledge as K
from . import gap, stage


def assemble_brief(slug: str, *, facet: str | None = None, recent_limit: int = 15) -> dict:
    conn = K.get_conn(paths.knowledge_db(slug))
    try:
        snap = K.knowledge_snapshot(conn)
        open_qs = [r["question"] for r in K._rows(
            conn, "SELECT question FROM open_question WHERE status='open' ORDER BY created_at")]
        gaps = gap.facet_gaps(conn)
        thin = gap.thin_facets(conn)
        recent = K.recent_searches(conn, limit=recent_limit, facet=facet)
        st = stage.resolve_stage(conn)

        payload = {
            "kind": "research_brief.v1",
            "topic": slug,
            "facet": facet,
            "stage": st,
            "worldview": [w["proposition"] for w in snap["l0_worldview"]],
            "viewpoints": [{"facet": v.get("facet"), "stance": v.get("stance"),
                            "narrative": v["narrative"]} for v in snap["l1_viewpoint"]],
            "open_questions": open_qs,
            "facet_gaps": gaps,
            "recent_queries": _dedupe_keep_order([r["query"] for r in recent]),
            "counts": snap["coverage"],
        }
        snapshot_id = K.record_context_snapshot(conn, payload=payload)
        conn.commit()
    finally:
        conn.close()

    brief_md = _render_brief(slug, payload, thin, snapshot_id)
    _stamp_stage(slug, st)
    return {"snapshot_id": snapshot_id, "stage": st, "brief_md": brief_md,
            "facet_gaps": gaps, "thin_facets": thin, "recent_queries": payload["recent_queries"]}


def _render_brief(slug: str, p: dict, thin: list, snapshot_id: str) -> str:
    L = [f"# 检索唤起 Brief — {slug}",
         f"_stage: **{p['stage']}** · context_snapshot: `{snapshot_id}` · "
         f"coverage: L0={p['counts']['l0']} L1={p['counts']['l1']} L2={p['counts']['l2']} L3={p['counts']['l3']}_\n"]

    L.append("## 已确立（避免重复检索）")
    if p["worldview"]:
        for w in p["worldview"]:
            L.append(f"- {w}")
    else:
        L.append("_（尚无 L0 世界模型）_")
    for v in p["viewpoints"]:
        L.append(f"- _({v['facet']} · {v.get('stance') or '—'})_ {_clip(v['narrative'])}")
    L.append("")

    L.append("## 该追什么（开放问题 / 稀薄 facet）")
    for q in p["open_questions"]:
        L.append(f"- [ ] {q}")
    for g in thin:
        L.append(f"- ⚑ facet `{g['facet']}` [{g['coverage']}] — {g.get('question')} "
                 f"(L3={g['l3']} L2={g['l2']} 印证={g['corroborated_l2']})")
    if not p["open_questions"] and not thin:
        L.append("_（覆盖较完整；可做时效刷新或开新 facet）_")
    L.append("")

    if p["recent_queries"]:
        L.append("## 近期已检索（不要重复）")
        for q in p["recent_queries"]:
            L.append(f"- ~~{q}~~")
        L.append("")

    L.append("---")
    L.append("_用本 brief 定向下一轮 `ros search` / 捕获；新结果 `ros condense` 后回馈 L0–L3，闭环生长。_")
    return "\n".join(L) + "\n"


def _stamp_stage(slug: str, st: str) -> None:
    try:
        from .. import topics
        m = topics.load_manifest(slug)
        if m.get("stage") != st:
            m["stage"] = st
            topics._write_manifest(slug, m)
    except Exception:  # noqa: BLE001 — stage stamping is best-effort
        pass


def write_brief(slug: str, *, facet: str | None = None) -> dict:
    """Assemble the brief and persist it to artifacts/brief_<snapshot>.md. Returns the result dict."""
    res = assemble_brief(slug, facet=facet)
    d = paths.artifacts_dir(slug) / "briefs"
    d.mkdir(parents=True, exist_ok=True)
    fp = d / f"{res['snapshot_id']}.md"
    fp.write_text(res["brief_md"], encoding="utf-8")
    res["path"] = str(fp)
    return res


def _clip(s: str, n: int = 100) -> str:
    s = " ".join((s or "").split())
    return s if len(s) <= n else s[: n - 1] + "…"


def _dedupe_keep_order(xs: list) -> list:
    seen, out = set(), []
    for x in xs:
        if x and x not in seen:
            seen.add(x)
            out.append(x)
    return out
