"""ResearchOS command surface: `ros <noun> <verb>`.

The single gated entrypoint. Runners and (future) skills shell out to `ros`; they never open a
db directly. Phase 0 covers the foundation: topic lifecycle, facet seeding, capture, promote
(URL gate), and db verify/dump. Later phases add: brief / search / media / condense / report / gaps.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

from . import api, paths, topics
from .assembly import context as brief_ctx, gap as gap_mod, stage as stage_mod
from .boundary import gates as boundary_gates
from .media import image_ocr, transcribe as transcribe_mod
from .run import condense as condense_run, report as report_run
from .search import capabilities


# ---------------------------------------------------------------------------
# small output helpers
# ---------------------------------------------------------------------------
def _emit(obj, as_json: bool) -> None:
    if as_json:
        print(json.dumps(obj, ensure_ascii=False, indent=2, default=str))
    else:
        print(obj if isinstance(obj, str) else json.dumps(obj, ensure_ascii=False, indent=2, default=str))


def _coverage_line(cov: dict) -> str:
    return (f"L0={cov['l0']} L1={cov['l1']} L2={cov['l2']} L3={cov['l3']} "
            f"src={cov['sources']} facets={len(cov['facets'])} "
            f"open_q={cov['open_questions']} schema=v{cov['schema_version']}")


# ---------------------------------------------------------------------------
# topic
# ---------------------------------------------------------------------------
def cmd_topic_new(a) -> int:
    m = topics.new_topic(a.name, title=a.title, aliases=a.alias or [])
    print(f"✓ created topic '{m['slug']}'  ({m['title']})")
    print(f"  knowledge.db: {paths.knowledge_db(m['slug'])}")
    print(f"  sources.db:   {paths.sources_db(m['slug'])}")
    topics.set_active(m["slug"])
    print(f"  → active topic set to '{m['slug']}'")
    return 0


def cmd_topic_open(a) -> int:
    info = topics.open_topic(a.name)
    m = info["manifest"]
    print(f"● topic '{info['slug']}'  ({m.get('title')})   stage={m.get('stage')}  status={m.get('status')}")
    print(f"  coverage: {_coverage_line(info['coverage'])}")
    facets = info["coverage"]["facets"]
    if facets:
        print("  facets:")
        for f in facets:
            print(f"    - [{f['status']}] {f['id']}: {f['question']}")
    else:
        print("  facets: (none yet — `ros facet add \"<question>\"`)")
    print(f"  → active topic set to '{info['slug']}'")
    return 0


def cmd_topic_ls(a) -> int:
    rows = topics.list_topics()
    if not rows:
        print("(no topics yet — `ros topic new <name>`)")
        return 0
    cur = topics.active()
    for t in rows:
        mark = "●" if t["slug"] == cur else " "
        print(f"{mark} {t['slug']:<28} [{t.get('status')}]  {t.get('coverage','')}   {t.get('title','')}")
    return 0


def cmd_topic_show(a) -> int:
    info = topics.show_topic(topics.require_slug(a.name))
    _emit(info, a.json)
    return 0


def cmd_topic_archive(a) -> int:
    slug = topics.archive_topic(a.name)
    print(f"✓ archived topic '{slug}'")
    return 0


def cmd_topic_merge(a) -> int:
    res = topics.merge_topic(a.src, a.dst)
    print(f"✓ merged '{res['src']}' → '{res['dst']}': linked {res['linked_sources']} source(s)")
    print(f"  {res['note']}")
    return 0


# ---------------------------------------------------------------------------
# facet
# ---------------------------------------------------------------------------
def cmd_facet_add(a) -> int:
    res = topics.add_facet(a.topic, a.question)
    print(f"✓ facet {res['facet_id']} added to '{res['slug']}': {res['question']}")
    return 0


# ---------------------------------------------------------------------------
# capture / promote
# ---------------------------------------------------------------------------
def _load_payload(src: str) -> dict:
    text = sys.stdin.read() if src == "-" else Path(src).read_text(encoding="utf-8")
    return json.loads(text)


def cmd_capture(a) -> int:
    slug = topics.require_slug(a.topic)
    payload = _load_payload(a.payload)
    res = api.record_capture(payload, path=paths.sources_db(slug))
    print(f"✓ captured {res['count']} item(s) into '{slug}' (session {res['session_id']}, source={res['source']})")
    for it in res["items"]:
        tag = "restricted(no-url)" if it["restricted"] else "url"
        print(f"    - {it['item_id']}  [{tag}]  hash={it['content_hash'][:12]}")
    if a.auto_promote:
        return _do_promote(slug, item_id=None)
    print(f"  → promote with: ros promote --topic {slug}")
    return 0


def _do_promote(slug: str, *, item_id: str | None) -> int:
    conn = api.get_conn(paths.knowledge_db(slug))
    try:
        if item_id:
            res = api.promote_item(conn, item_id, topic_slug=slug, path=paths.sources_db(slug))
            tag = "already-promoted" if res.get("already_promoted") else "promoted"
            print(f"✓ {tag}: {res['item_id']} → source_ref {res['source_ref_id']}")
        else:
            res = api.bulk_promote(conn, topic_slug=slug, path=paths.sources_db(slug))
            c = res["counts"]
            print(f"✓ promote: {c['promoted']} promoted, {c['skipped']} skipped (url-gate), {c['errors']} error(s)")
            for s in res["skipped"]:
                print(f"    - skipped {s['item_id']}: {s['reason']}")
            for e in res["errors"]:
                print(f"    ✗ error {e['item_id']}: {e['error']}")
    finally:
        conn.close()
    cov = topics.update_coverage(slug)
    print(f"  coverage now: {cov}")
    return 0


def cmd_promote(a) -> int:
    slug = topics.require_slug(a.topic)
    return _do_promote(slug, item_id=a.item)


# ---------------------------------------------------------------------------
# search (Phase 1: plan + policy gate; the fetch itself is agent-driven via a skill)
# ---------------------------------------------------------------------------
def cmd_search(a) -> int:
    slug = topics.require_slug(a.topic)
    sources = [s.strip() for s in (a.source or "web").split(",") if s.strip()]
    print(f"● search plan for topic '{slug}': \"{a.query}\"")
    for src in sources:
        pol = capabilities.source_policy(src)
        if not pol:
            print(f"  ✗ {src}: unknown source (known: {', '.join(capabilities.known_sources())})")
            continue
        req = capabilities.required_collectors(src) or ["—"]
        forb = capabilities.forbidden_collectors(src)
        entry = capabilities.search_entry(src) or "—"
        print(f"  • {src}: collector∈{req}" + (f"  forbidden={forb}" if forb else ""))
        print(f"      entry: {entry}")
    # durably log the search (per-topic) so the next brief won't re-run it
    conn = api.get_conn(paths.knowledge_db(slug))
    try:
        for src in sources:
            api.record_search(conn, query=a.query, source=src, facet=a.facet)
        conn.commit()
    finally:
        conn.close()
    print("\n  → Drive the fetch with the researchos-search skill, then:")
    if any(capabilities.canonical(s) in ("web", "web_search") for s in sources):
        print("      web: 3-tier fallback — zhipu web-search-prime → WebSearch → multi-search-engine")
        print("           skill (quota-free). Record raw_tool_status.fallback_chain every search.")
        print("           → methodology/web_search_provider_playbook.md")
    print(f"      ros capture <payload.json> --topic {slug} --auto-promote")
    print(f"      ros condense {slug} && ros report {slug}")
    return 0


# ---------------------------------------------------------------------------
# brief / gaps / review (priming the next round)
# ---------------------------------------------------------------------------
def cmd_brief(a) -> int:
    slug = topics.require_slug(a.topic)
    res = brief_ctx.write_brief(slug, facet=a.facet)
    print(res["brief_md"])
    print(f"_(brief saved → {res['path']} · snapshot {res['snapshot_id']})_")
    return 0


def cmd_grow(a) -> int:
    """One growth cycle's priming step: freeze the brief and print the loop plan. The agent then
    runs the researchos-grow skill (search thin facets → capture → condense → report → reassess)."""
    slug = topics.require_slug(a.topic)
    res = brief_ctx.write_brief(slug, facet=a.facet)
    print(res["brief_md"])
    print(f"_(brief frozen → snapshot {res['snapshot_id']})_\n")
    print("下一步（agent 执行 researchos-grow 技能）：")
    print("  1) 针对上面的稀薄 facet / 开放问题检索：web→三层降级链 web-search-prime→WebSearch→")
    print("     multi-search-engine(免额度兜底)；x/douyin→kimi-webbridge，小红书→xiaohongshu-mcp（绝不 kimi-webbridge）")
    print(f"  2) ros capture <payload.json> --topic {slug} --auto-promote")
    print(f"  3) ros condense {slug} && ros report {slug}")
    print(f"  4) ros gaps {slug} / ros review {slug}  → 回到 1 直到覆盖充分")
    print(f"  5) ros snapshot {slug}  （耐久知识入 git）")
    return 0


def cmd_gaps(a) -> int:
    slug = topics.require_slug(a.topic)
    conn = api.get_conn(paths.knowledge_db(slug))
    try:
        gaps = gap_mod.facet_gaps(conn)
    finally:
        conn.close()
    if not gaps:
        print(f"(no facets yet for '{slug}' — `ros facet add`)")
        return 0
    print(f"● facet coverage for '{slug}':")
    print(f"  {'facet':<26} {'cover':<12} L3 L2 印证  时效(d)  最近检索")
    for g in gaps:
        print(f"  {g['facet']:<26} {g['coverage']:<12} {g['l3']:>2} {g['l2']:>2} {g['corroborated_l2']:>3}"
              f"   {str(g['recency_days'] or '—'):>6}   {g['last_searched_at'] or '—'}")
    return 0


def cmd_review(a) -> int:
    slug = topics.require_slug(a.topic)
    conn = api.get_conn(paths.knowledge_db(slug))
    try:
        snap = api.knowledge_snapshot(conn)
        contested = [v for v in snap["l1_viewpoint"] if v.get("stance") in ("contested", "refuted")]
        conflicts = [f for f in snap["l2_finding"] if f.get("conflict_note")]
        st = stage_mod.resolve_stage(conn)
    finally:
        conn.close()
    print(f"● review '{slug}'  stage={st}")
    wv = snap["l0_worldview"]
    print("  worldview:", (wv[0]["proposition"] if wv else "（尚无 L0）"))
    print(f"  contested/refuted viewpoints: {len(contested)}")
    for v in contested:
        print(f"    - [{v['stance']}] {report_run._oneline(v['narrative'])}")
    print(f"  conflicting findings (needs review): {len(conflicts)}")
    for f in conflicts:
        print(f"    - ⚠ {report_run._oneline(f['statement'])}")
    return 0


# ---------------------------------------------------------------------------
# media → text
# ---------------------------------------------------------------------------
def cmd_media(a) -> int:
    if a.kind == "transcribe":
        res = transcribe_mod.transcribe(a.path, slug=topics.require_slug(a.topic) if a.topic else None,
                                        prompt=a.prompt)
    else:
        res = image_ocr.ocr(a.path)
    _emit(res, True)
    return 0 if res.get("status") in ("transcribed", "recognized", "agent_required") else 1


# ---------------------------------------------------------------------------
# condense / report
# ---------------------------------------------------------------------------
def cmd_condense(a) -> int:
    slug = topics.require_slug(a.topic)
    res = condense_run.condense(slug, stage=a.stage)
    for stage, r in res.items():
        print(f"  [{stage}] units={r['units']} ran={r['ran']} skipped={r['skipped']} "
              f"rows_written={r['rows_written']} reduce_failed={r['reduce_failed']}")
    cov = topics.update_coverage(slug)
    print(f"✓ condense '{slug}' done. coverage: {cov}")
    return 0


def cmd_report(a) -> int:
    slug = topics.require_slug(a.topic)
    if a.session:
        fp = report_run.write_session_report(slug, facet=a.facet, query=a.query)
        print(f"✓ appended session report → {fp}")
    else:
        fp = report_run.write_world_model(slug)
        print(f"✓ rendered world model → {fp}")
    return 0


# ---------------------------------------------------------------------------
# xhs (Xiaohongshu MCP bridge — the non-kimi-webbridge path)
# ---------------------------------------------------------------------------
def cmd_xhs(a) -> int:
    from .lib.xiaohongshu_mcp_bridge import (
        BRIDGE_TRANSPORT, XiaohongshuMcpBridge, XiaohongshuMcpBridgeError, default_endpoint)
    endpoint = a.endpoint or default_endpoint()
    try:
        client = XiaohongshuMcpBridge(endpoint=endpoint, allow_remote=a.allow_remote,
                                      timeout_sec=a.timeout_sec)
        if a.subcmd == "status":
            result = client.call_tool("check_login_status", allow_destructive=a.allow_destructive)
        elif a.subcmd == "tools":
            result = client.list_tools()
        elif a.subcmd == "call":
            args = json.loads(a.args_json or "{}")
            if not isinstance(args, dict):
                raise ValueError("--args-json must decode to a JSON object")
            result = client.call_tool(a.tool, arguments=args, allow_destructive=a.allow_destructive)
        else:  # pragma: no cover
            raise ValueError(f"unknown xhs subcommand: {a.subcmd}")
    except (XiaohongshuMcpBridgeError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "failed", "bridge_transport": BRIDGE_TRANSPORT,
                          "endpoint": endpoint, "error_type": type(exc).__name__,
                          "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    return 0


# ---------------------------------------------------------------------------
# method lane (M0/M1) — Phase 4
# ---------------------------------------------------------------------------
def cmd_method_add(a) -> int:
    slug = topics.require_slug(a.topic)
    valid_if = json.loads(a.valid_if) if a.valid_if else None
    conn = api.get_conn(paths.knowledge_db(slug))
    try:
        rid = api.method_upsert(conn, level=a.level, proposition=a.proposition,
                                valid_if=valid_if, wrong_if=a.wrong_if, status=a.status)
        conn.commit()
    finally:
        conn.close()
    print(f"✓ method {a.level} {rid} added to '{slug}' [{a.status}]")
    return 0


def cmd_method_ls(a) -> int:
    slug = topics.require_slug(a.topic)
    conn = api.get_conn(paths.knowledge_db(slug))
    try:
        rules = api.method_list(conn, level=a.level, status=a.status)
    finally:
        conn.close()
    if not rules:
        print(f"(no method rules for '{slug}')")
        return 0
    for r in rules:
        vif = f"  valid_if={r['valid_if']}" if r.get("valid_if") else ""
        print(f"  [{r['level']} · {r['status']}] {r['id']}  {r['proposition']}{vif}")
    return 0


def cmd_method_export(a) -> int:
    slug = topics.require_slug(a.topic)
    res = api.method_export(slug, a.rule_id)
    print(f"✓ exported {a.rule_id} from '{slug}' → shared method store ({res['shared']})")
    return 0


def cmd_method_import(a) -> int:
    slug = topics.require_slug(a.topic)
    if a.rule_id:
        res = api.method_import(a.rule_id, slug)
        print(f"✓ imported {a.rule_id} → '{slug}' as {res['imported_as']} [{res['status']}] — {res['note']}")
    else:
        shared = api.method_list_shared()
        if not shared:
            print("(shared method store is empty)")
            return 0
        print("shared method candidates (import with `ros method import <slug> <rule_id>`):")
        for r in shared:
            print(f"  [{r['level']}] {r['id']}  (from {r.get('origin_topic')})  {r['proposition']}")
    return 0


# ---------------------------------------------------------------------------
# library (global content-addressed original store, cross-topic)
# ---------------------------------------------------------------------------
def cmd_library_ls(a) -> int:
    recs = api.shared_sources() if a.shared else api.list_sources()
    if not recs:
        print("(library empty)" if not a.shared else "(no cross-topic shared sources)")
        return 0
    for r in recs:
        refs = ",".join(r.get("referenced_by_topics") or [])
        print(f"  {r['content_hash'][:12]}  [{r.get('platform','—')}]  refs={refs}  {r.get('title') or r.get('url')}")
    return 0


def cmd_library_show(a) -> int:
    rec = api.read_source(a.hash)
    if rec is None:
        print(f"error: no library source for hash {a.hash}", file=sys.stderr)
        return 2
    _emit(rec, True)
    return 0


def cmd_library_link(a) -> int:
    slug = topics.require_slug(a.topic)
    conn = api.get_conn(paths.knowledge_db(slug))
    try:
        res = api.link_source(conn, a.hash, topic_slug=slug)
    finally:
        conn.close()
    tag = "already-linked" if res.get("already_linked") else "linked"
    print(f"✓ {tag}: library {a.hash[:12]} → '{slug}' as {res['source_ref_id']} (no re-fetch)")
    topics.update_related()
    print("  (refreshed cross-topic shares_source edges in _index.yaml)")
    return 0


# ---------------------------------------------------------------------------
# db
# ---------------------------------------------------------------------------
def cmd_db_verify(a) -> int:
    slug = topics.require_slug(a.topic)
    conn = api.get_conn(paths.knowledge_db(slug))
    try:
        fk = conn.execute("PRAGMA foreign_key_check").fetchall()
        integ = conn.execute("PRAGMA integrity_check").fetchone()[0]
        ver = api.db_user_version(conn)
        cur = api.current_schema_version()
        cov = api.coverage(conn)
    finally:
        conn.close()
    ok = (not fk) and integ == "ok" and ver == cur
    print(f"{'✓' if ok else '✗'} db verify '{slug}'")
    print(f"  integrity_check: {integ}")
    print(f"  foreign_key_check: {'clean' if not fk else f'{len(fk)} VIOLATION(S)'}")
    print(f"  schema: db=v{ver} available=v{cur} {'(up to date)' if ver == cur else '(PENDING MIGRATIONS)'}")
    print(f"  coverage: {_coverage_line(cov)}")
    return 0 if ok else 1


def _dump_knowledge(slug: str) -> str:
    out = paths.snapshots_dir(slug) / f"{_today()}.sql"
    out.parent.mkdir(parents=True, exist_ok=True)
    conn = api.get_conn(paths.knowledge_db(slug))
    try:
        with out.open("w", encoding="utf-8") as f:
            for line in conn.iterdump():
                f.write(line + "\n")
    finally:
        conn.close()
    return str(out)


def cmd_db_dump(a) -> int:
    slug = topics.require_slug(a.topic)
    print(f"✓ dumped knowledge.db → {_dump_knowledge(slug)}")
    return 0


def cmd_snapshot(a) -> int:
    """Export the topic's durable knowledge to snapshots/<date>.sql (the git-committed artifact —
    the live .db is gitignored)."""
    slug = topics.require_slug(a.topic)
    out = _dump_knowledge(slug)
    print(f"✓ snapshot '{slug}' → {out}")
    print("  (commit this SQL dump for durable knowledge; the live knowledge.db stays gitignored)")
    return 0


def cmd_resediment(a) -> int:
    slug = topics.require_slug(a.topic)
    res = condense_run.resediment(slug, force=a.force)
    for stage, r in res.items():
        print(f"  [{stage}] rows_written={r['rows_written']} reduce_failed={r['reduce_failed']}")
    cov = topics.update_coverage(slug)
    print(f"✓ resediment '{slug}' done. coverage: {cov}")
    return 0


# ---------------------------------------------------------------------------
# lint (boundary gates: schema/collector/provenance/acl/db-safety + l0-integrity)
# ---------------------------------------------------------------------------
def cmd_lint(a) -> int:
    print(f"ros lint — schema v{api.current_schema_version()}, {len(topics.list_topics())} topic(s)")
    results = boundary_gates.run_all()
    total = 0
    for name, ok, problems in results:
        print(f"  {'✓' if ok else '✗'} {name}" + ("" if ok else f"  ({len(problems)} problem(s))"))
        for p in problems:
            print(f"      - {p}")
        total += len(problems)
    print(f"  → {total} problem(s)")
    return 0 if total == 0 else 1


def _today() -> str:
    conn = sqlite3.connect(":memory:")
    try:
        return str(conn.execute("SELECT date('now')").fetchone()[0])
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# parser
# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="ros", description="ResearchOS — multi-topic L0–L3 research system")
    p.add_argument("--json", action="store_true", help="emit JSON where supported")
    sub = p.add_subparsers(dest="noun", required=True)

    # topic
    tp = sub.add_parser("topic", help="topic lifecycle").add_subparsers(dest="verb", required=True)
    t_new = tp.add_parser("new", help="scaffold a new topic (+ knowledge.db + sources.db)")
    t_new.add_argument("name")
    t_new.add_argument("--title")
    t_new.add_argument("--alias", action="append", help="repeatable alias for resolution")
    t_new.set_defaults(func=cmd_topic_new)
    t_open = tp.add_parser("open", help="set active topic and print its world-model summary")
    t_open.add_argument("name")
    t_open.set_defaults(func=cmd_topic_open)
    t_ls = tp.add_parser("ls", help="list topics")
    t_ls.set_defaults(func=cmd_topic_ls)
    t_show = tp.add_parser("show", help="show a topic manifest + coverage")
    t_show.add_argument("name", nargs="?")
    t_show.set_defaults(func=cmd_topic_show)
    t_arch = tp.add_parser("archive", help="archive a topic")
    t_arch.add_argument("name", nargs="?")
    t_arch.set_defaults(func=cmd_topic_archive)
    t_merge = tp.add_parser("merge", help="merge src topic into dst (same thread; links sources, archives src)")
    t_merge.add_argument("src")
    t_merge.add_argument("dst")
    t_merge.set_defaults(func=cmd_topic_merge)

    # facet
    fp = sub.add_parser("facet", help="research facets").add_subparsers(dest="verb", required=True)
    f_add = fp.add_parser("add", help="add a research facet (sub-question)")
    f_add.add_argument("question")
    f_add.add_argument("--topic")
    f_add.set_defaults(func=cmd_facet_add)

    # search (plan + policy gate)
    sp = sub.add_parser("search", help="print the per-source search plan + collector policy")
    sp.add_argument("query")
    sp.add_argument("--topic")
    sp.add_argument("--source", default="web", help="comma list: web,x,douyin,xiaohongshu")
    sp.add_argument("--facet", help="facet this search targets (logged for priming)")
    sp.set_defaults(func=cmd_search)

    # brief (priming the next round)
    bp = sub.add_parser("brief", help="assemble + freeze the priming brief from current knowledge")
    bp.add_argument("topic", nargs="?")
    bp.add_argument("--facet")
    bp.set_defaults(func=cmd_brief)

    # grow (one closed-loop cycle: prime → [agent searches] → condense → report)
    grp = sub.add_parser("grow", help="prime + plan one growth cycle (agent runs researchos-grow)")
    grp.add_argument("topic", nargs="?")
    grp.add_argument("--facet")
    grp.set_defaults(func=cmd_grow)

    # gaps
    gp = sub.add_parser("gaps", help="per-facet coverage metrics (what to search next)")
    gp.add_argument("topic", nargs="?")
    gp.set_defaults(func=cmd_gaps)

    # review
    vp = sub.add_parser("review", help="worldview + contested viewpoints + needs-review queue")
    vp.add_argument("topic", nargs="?")
    vp.set_defaults(func=cmd_review)

    # media
    mp = sub.add_parser("media", help="media → text (transcribe video / ocr image)").add_subparsers(
        dest="kind", required=True)
    m_t = mp.add_parser("transcribe", help="video/audio → text (whisper)")
    m_t.add_argument("path")
    m_t.add_argument("--topic")
    m_t.add_argument("--prompt", help="domain-bias prompt (default: topic.media_prompt)")
    m_t.set_defaults(func=cmd_media, kind="transcribe")
    m_o = mp.add_parser("ocr", help="image/screenshot → text (zai-mcp agent path / local fallback)")
    m_o.add_argument("path")
    m_o.add_argument("--topic")
    m_o.add_argument("--prompt", required=False)
    m_o.set_defaults(func=cmd_media, kind="ocr")

    # condense
    cd = sub.add_parser("condense", help="run the condense chain: source → L3 → L2 → L1 → L0")
    cd.add_argument("topic", nargs="?")
    cd.add_argument("--stage", choices=["all", "distill", "aggregate", "synthesize"], default="all")
    cd.set_defaults(func=cmd_condense)

    # report
    rp = sub.add_parser("report", help="render reports/world_model.md (or --session) from knowledge.db")
    rp.add_argument("topic", nargs="?")
    rp.add_argument("--session", action="store_true", help="append an immutable session report")
    rp.add_argument("--facet", help="session report: scope to one facet")
    rp.add_argument("--query", help="session report: the query this round answered")
    rp.set_defaults(func=cmd_report)

    # xhs bridge
    xp = sub.add_parser("xhs", help="xiaohongshu-mcp bridge (non-kimi-webbridge XHS path)")
    xp.add_argument("subcmd", choices=["status", "tools", "call"])
    xp.add_argument("--tool", help="tool name (for call)")
    xp.add_argument("--args-json", dest="args_json", help="JSON object of tool args (for call)")
    xp.add_argument("--endpoint", help="override (default http://localhost:18060/mcp or ROS_XHS_MCP_URL)")
    xp.add_argument("--allow-remote", action="store_true")
    xp.add_argument("--allow-destructive", action="store_true")
    xp.add_argument("--timeout-sec", type=float, default=20.0)
    xp.set_defaults(func=cmd_xhs)

    # capture
    cap = sub.add_parser("capture", help="record an agent-gathered capture into sources.db")
    cap.add_argument("payload", help="path to a capture JSON file, or '-' for stdin")
    cap.add_argument("--topic")
    cap.add_argument("--auto-promote", action="store_true")
    cap.set_defaults(func=cmd_capture)

    # promote
    pr = sub.add_parser("promote", help="URL-gate raw items into retained source_refs")
    pr.add_argument("--topic")
    pr.add_argument("--item", help="promote a single item id (default: bulk)")
    pr.set_defaults(func=cmd_promote)

    # method lane (M0/M1)
    mtp = sub.add_parser("method", help="method lane (M0/M1): how-to-research invariants").add_subparsers(
        dest="verb", required=True)
    m_add = mtp.add_parser("add", help="add a method rule")
    m_add.add_argument("--topic")
    m_add.add_argument("--level", choices=["M0", "M1"], required=True)
    m_add.add_argument("--proposition", required=True)
    m_add.add_argument("--valid-if", dest="valid_if", help="M1 JSON {stage,facet,condition}")
    m_add.add_argument("--wrong-if", dest="wrong_if")
    m_add.add_argument("--status", choices=["active", "draft", "retired"], default="active")
    m_add.set_defaults(func=cmd_method_add)
    m_ls = mtp.add_parser("ls", help="list method rules")
    m_ls.add_argument("--topic")
    m_ls.add_argument("--level", choices=["M0", "M1"])
    m_ls.add_argument("--status", choices=["active", "draft", "retired"])
    m_ls.set_defaults(func=cmd_method_ls)
    m_ex = mtp.add_parser("export", help="export a rule to the shared cross-topic store")
    m_ex.add_argument("rule_id")
    m_ex.add_argument("--topic")
    m_ex.set_defaults(func=cmd_method_export)
    m_im = mtp.add_parser("import", help="import a shared rule (lands as draft; list candidates if no id)")
    m_im.add_argument("rule_id", nargs="?")
    m_im.add_argument("--topic")
    m_im.set_defaults(func=cmd_method_import)

    # library (cross-topic content-addressed store)
    lib = sub.add_parser("library", help="global cross-topic original store").add_subparsers(
        dest="verb", required=True)
    l_ls = lib.add_parser("ls", help="list retained sources (--shared: only cross-topic)")
    l_ls.add_argument("--shared", action="store_true")
    l_ls.set_defaults(func=cmd_library_ls)
    l_show = lib.add_parser("show", help="show one library record by content hash")
    l_show.add_argument("hash")
    l_show.set_defaults(func=cmd_library_show)
    l_link = lib.add_parser("link", help="reuse a retained source into another topic (no re-fetch)")
    l_link.add_argument("hash")
    l_link.add_argument("--topic")
    l_link.set_defaults(func=cmd_library_link)

    # db
    dbp = sub.add_parser("db", help="database ops").add_subparsers(dest="verb", required=True)
    d_v = dbp.add_parser("verify", help="integrity + FK + schema-version check")
    d_v.add_argument("--topic")
    d_v.set_defaults(func=cmd_db_verify)
    d_d = dbp.add_parser("dump", help="export knowledge.db to snapshots/<date>.sql")
    d_d.add_argument("--topic")
    d_d.set_defaults(func=cmd_db_dump)

    # snapshot (git-durable knowledge export)
    snp = sub.add_parser("snapshot", help="export durable knowledge → snapshots/<date>.sql (git)")
    snp.add_argument("topic", nargs="?")
    snp.set_defaults(func=cmd_snapshot)

    # resediment (drift re-condense)
    rs = sub.add_parser("resediment", help="re-derive knowledge from current sources (drift re-condense)")
    rs.add_argument("topic", nargs="?")
    rs.add_argument("--force", action="store_true", help="also re-distill every source (expensive)")
    rs.set_defaults(func=cmd_resediment)

    # lint (boundary gates)
    lp = sub.add_parser("lint",
        help="run all boundary gates (schema/collector/provenance/acl/db-safety/l0-integrity)")
    lp.set_defaults(func=cmd_lint)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except (ValueError, KeyError, FileNotFoundError, RuntimeError, json.JSONDecodeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
