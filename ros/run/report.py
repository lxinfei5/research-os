"""Deterministic report renderer: knowledge.db → reports/world_model.md.

The semantic prose (worldview, viewpoints, findings) was written into the DB by agents during
condense; THIS step is pure Python string assembly — no reasoning. The world model is a LIVE
document: regenerated (overwritten) from the current DB each time, so it always reflects the topic's
accumulated knowledge. Fixed sections (DESIGN.md §7.2).
"""
from __future__ import annotations

import json

from .. import api, paths
from ..storage import knowledge as K


def _j(v):
    if not v:
        return []
    try:
        return json.loads(v) if isinstance(v, str) else list(v)
    except (json.JSONDecodeError, TypeError):
        return []


def render_world_model(slug: str) -> str:
    conn = api.get_conn(paths.knowledge_db(slug))
    try:
        snap = api.knowledge_snapshot(conn)
        cov = snap["coverage"]
        open_qs = K._rows(conn, "SELECT question FROM open_question WHERE status='open' ORDER BY created_at")
        cred = {r["id"]: r for r in K._rows(conn, "SELECT id, level FROM credibility_assessment")}
        needs_review = K._rows(conn,
            "SELECT id, statement FROM l2_finding WHERE status='active' AND conflict_note IS NOT NULL")
        history = K.l0_history(conn)
    finally:
        conn.close()

    src_by_id = {s["id"]: s for s in snap["source_ref"]}
    L = []
    title = _manifest_title(slug)
    L.append(f"# {title} — 世界模型 (world_model)")
    L.append(f"_自动生成 · 覆盖度: L0={cov['l0']} L1={cov['l1']} L2={cov['l2']} L3={cov['l3']} "
             f"来源={cov['sources']} · schema v{cov['schema_version']}_\n")

    # ① Worldview (current active) + version history (archived predecessors)
    L.append("## 1. 主题概览 / Worldview")
    wv = snap["l0_worldview"]
    if wv:
        for w in wv:
            L.append(f"- **{w['proposition']}**  _(confidence: {w.get('confidence') or '—'})_")
    else:
        L.append("_（尚未综合出 L0 世界模型 — 运行 `ros condense`）_")
    L.append("")

    archived = [h for h in history if h.get("status") != "active"]
    if len(history) > 1 and archived:
        L.append("### 版本历史 / Version History")
        L.append("_世界模型随每次 condense 迭代；下方为已被取代的旧版本（当前版本见上）。_")
        for h in archived:
            prop = _oneline(h.get("proposition") or "")
            stamp = (h.get("updated_at") or "")[:16]
            sup = h.get("supersedes_id") or "—"
            L.append(f"- _[{stamp}]_ {prop}  _(supersedes: `{sup}`)_")
        L.append("")

    # ② Open questions
    L.append("## 2. 开放问题 / Open Questions")
    oqs = [q["question"] for q in open_qs]
    for w in wv:
        oqs.extend(_j(w.get("open_questions")))
    oqs = _dedupe(oqs)
    if oqs:
        for q in oqs:
            L.append(f"- [ ] {q}")
    else:
        L.append("_（暂无 — 下一轮检索可由此驱动）_")
    L.append("")

    # ③ Themes (L1)
    L.append("## 3. 分主题综合 / Themes (L1)")
    if snap["l1_viewpoint"]:
        for v in snap["l1_viewpoint"]:
            badge = f"[{v.get('stance') or '—'} · {v.get('confidence') or '—'}]"
            facet = f" _(facet: {v['facet']})_" if v.get("facet") else ""
            L.append(f"### {badge} {v.get('synthesis_kind','theme')}{facet}")
            L.append(v["narrative"])
            L.append("")
    else:
        L.append("_（尚无 L1 视角）_\n")

    # ④ Corroborated findings (L2)
    L.append("## 4. 已证实发现 / Corroborated Findings (L2)")
    if snap["l2_finding"]:
        L.append("| # | 发现 | 印证数 | 跨平台 | 可信度 | 冲突 |")
        L.append("|---|------|--------|--------|--------|------|")
        for i, f in enumerate(snap["l2_finding"], 1):
            lvl = cred.get(f["credibility_id"], {}).get("level", "—")
            conflict = "⚠" if f.get("conflict_note") else ""
            L.append(f"| {i} | {_oneline(f['statement'])} | {f['corroboration_count']} | "
                     f"{f['cross_platform_count']} | {lvl} | {conflict} |")
    else:
        L.append("_（尚无 L2 发现）_")
    L.append("")

    # ⑤ Source index (L3 + source_ref)
    L.append("## 5. 来源索引 / Source Index")
    if snap["l3_claim"]:
        L.append("| # | 主张 | 平台 | 链接 | 可信度 | 缓存 |")
        L.append("|---|------|------|------|--------|------|")
        for i, c in enumerate(snap["l3_claim"], 1):
            s = src_by_id.get(c["single_source_ref_id"], {})
            lvl = cred.get(c["credibility_id"], {}).get("level", "—")
            url = s.get("url", "")
            link = f"[link]({url})" if url else "—"
            cache = s.get("cached_text_path") or "—"
            L.append(f"| {i} | {_oneline(c['proposition'])} | {s.get('platform','—')} | "
                     f"{link} | {lvl} | `{cache}` |")
    else:
        L.append("_（尚无 L3 主张）_")
    L.append("")

    # ⑥ Needs review
    if needs_review:
        L.append("## 6. 待复核 / Needs Review")
        for r in needs_review:
            L.append(f"- ⚠ {_oneline(r['statement'])}")
        L.append("")

    # ⑦ Facet coverage
    L.append("## 7. Facet 覆盖")
    if cov["facets"]:
        L.append("| facet | 问题 | 状态 |")
        L.append("|-------|------|------|")
        for f in cov["facets"]:
            L.append(f"| `{f['id']}` | {f['question']} | {f['status']} |")
    else:
        L.append("_（尚无 facet）_")
    L.append("")

    L.append("---")
    L.append("_声明：本报告为信息关联与凝练，非投资/行动建议。每条主张均附来源链接与缓存路径，可回溯。_")
    return "\n".join(L) + "\n"


def write_world_model(slug: str) -> str:
    """Render + overwrite topics/<slug>/reports/world_model.md. Returns the file path (str)."""
    md = render_world_model(slug)
    paths.reports_dir(slug).mkdir(parents=True, exist_ok=True)
    fp = paths.reports_dir(slug) / "world_model.md"
    fp.write_text(md, encoding="utf-8")
    return str(fp)


def render_session_report(slug: str, *, facet: str | None = None, query: str | None = None,
                          snapshot_id: str | None = None) -> str:
    """Three-section session report for one research round (immutable, append-only)."""
    conn = api.get_conn(paths.knowledge_db(slug))
    try:
        where = "facet=?" if facet else "1=1"
        params = (facet,) if facet else ()
        l2 = K._rows(conn, f"SELECT * FROM l2_finding WHERE status='active' AND {where} ORDER BY corroboration_count DESC", params)
        l3 = K._rows(conn, f"SELECT * FROM l3_claim WHERE status='active' AND {where} ORDER BY created_at", params)
        cred = {r["id"]: r["level"] for r in K._rows(conn, "SELECT id, level FROM credibility_assessment")}
        src = {s["id"]: s for s in K._rows(conn, "SELECT * FROM source_ref")}
        needs = [r for r in l2 if r.get("conflict_note")]
    finally:
        conn.close()

    L = [f"# 会话报告 — {_manifest_title(slug)}",
         f"_facet: {facet or '(all)'} · query: {query or '—'} · snapshot: `{snapshot_id or '—'}`_\n",
         "## 1. 核心要点"]
    if l2:
        for f in l2:
            L.append(f"- **{_oneline(f['statement'])}** _(印证 {f['corroboration_count']}/跨平台 {f['cross_platform_count']}, "
                     f"可信度 {cred.get(f['credibility_id'],'—')})_")
    else:
        L.append("_（本轮暂无 L2 发现）_")

    L.append("\n## 2. 论点与证据逻辑链")
    for c in l3:
        s = src.get(c["single_source_ref_id"], {})
        url = s.get("url", "")
        L.append(f"- {_oneline(c['proposition'])}  "
                 f"[{cred.get(c['credibility_id'],'—')}] "
                 f"([来源]({url}) · `{s.get('cached_text_path') or '—'}`)")
    if not l3:
        L.append("_（暂无 L3 证据）_")

    L.append("\n## 3. 来源索引 + 待复核")
    for i, (sid, s) in enumerate(src.items(), 1):
        L.append(f"{i}. {s.get('title') or s.get('platform')} — [{s.get('platform')}]({s.get('url')})  `{s.get('cached_text_path') or '—'}`")
    if needs:
        L.append("\n**待人工复核：**")
        for r in needs:
            L.append(f"- ⚠ {_oneline(r['statement'])} — {r['conflict_note']}")

    L.append("\n---\n_声明：信息关联与凝练，非投资/行动建议。可回溯至留存原文。_")
    return "\n".join(L) + "\n"


def write_session_report(slug: str, *, facet: str | None = None, query: str | None = None,
                         snapshot_id: str | None = None) -> str:
    """Append a timestamped immutable session report under reports/sessions/. Returns the path."""
    md = render_session_report(slug, facet=facet, query=query, snapshot_id=snapshot_id)
    d = paths.report_sessions_dir(slug)
    d.mkdir(parents=True, exist_ok=True)
    import sqlite3
    stamp = sqlite3.connect(":memory:").execute("SELECT strftime('%Y%m%d_%H%M%S','now')").fetchone()[0]
    fp = d / f"{stamp}_{facet or 'all'}.md"
    fp.write_text(md, encoding="utf-8")
    return str(fp)


def _manifest_title(slug: str) -> str:
    try:
        from .. import topics
        return topics.load_manifest(slug).get("title", slug)
    except Exception:  # noqa: BLE001
        return slug


def _oneline(s: str, n: int = 80) -> str:
    s = " ".join((s or "").split())
    return s if len(s) <= n else s[: n - 1] + "…"


def _dedupe(xs):
    seen, out = set(), []
    for x in xs:
        if x and x not in seen:
            seen.add(x)
            out.append(x)
    return out
