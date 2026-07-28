"""Phase 2 acceptance: the search_log migration, gap/stage metrics, brief assembly + context freeze
(the priming loop), media→text ladders, and the session report."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

from ros import api, paths, topics
from ros.assembly import context as brief_ctx, gap as gap_mod, stage as stage_mod
from ros.media import image_ocr, transcribe
from ros.run import condense as condense_run, report as report_run

STUB = str(Path(__file__).resolve().parent / "stub_agent.py")


@pytest.fixture()
def root(tmp_path, monkeypatch):
    monkeypatch.setenv("ROS_ROOT", str(tmp_path))
    return tmp_path


def _seed_and_condense(slug: str):
    payload = {"query": "q", "source": "web", "collector": "web_search",
               "items": [{"platform": "web", "source_kind": "article",
                          "url": f"https://example.com/{i}", "title": f"T{i}",
                          "content": f"原文 {i}"} for i in range(1, 4)]}
    api.record_capture(payload, path=paths.sources_db(slug))
    conn = api.get_conn(paths.knowledge_db(slug))
    try:
        api.bulk_promote(conn, topic_slug=slug, path=paths.sources_db(slug))
    finally:
        conn.close()
    condense_run.condense(slug, "all")


# ---------------------------------------------------------------------------
def test_migration_applies_search_log(root):
    topics.new_topic("t")
    conn = api.get_conn(paths.knowledge_db("t"))
    try:
        assert api.db_user_version(conn) == api.current_schema_version() >= 1
        sid = api.record_search(conn, query="台海", source="web", facet="f_x")
        conn.commit()
        assert sid.startswith("sl-")
        rec = api.recent_searches(conn, limit=5)
        assert rec and rec[0]["query"] == "台海"
        # FK + integrity still clean after a real migration
        assert conn.execute("PRAGMA foreign_key_check").fetchall() == []
    finally:
        conn.close()


def test_gap_metrics_and_stage(root, monkeypatch):
    monkeypatch.setenv("ROS_AGENT_CMD", f"{sys.executable} {STUB}")
    topics.new_topic("geo")
    topics.add_facet("geo", "一个尚未检索的子问题")        # thin facet (0 L3)
    _seed_and_condense("geo")                              # condense assigns facet 'f_main'

    conn = api.get_conn(paths.knowledge_db("geo"))
    try:
        gaps = {g["facet"]: g for g in gap_mod.facet_gaps(conn)}
        assert "f_main" in gaps and gaps["f_main"]["l3"] == 3
        assert gaps["f_main"]["coverage"] in ("developing", "corroborated")
        thin = gap_mod.thin_facets(conn)
        assert any(g["coverage"] == "thin" for g in thin)   # the declared empty facet
        assert stage_mod.resolve_stage(conn) == "deepening"  # has L2, no cross-platform corroboration
    finally:
        conn.close()


def test_brief_assembles_freezes_and_primes(root, monkeypatch):
    monkeypatch.setenv("ROS_AGENT_CMD", f"{sys.executable} {STUB}")
    topics.new_topic("geo", title="地缘政治")
    _seed_and_condense("geo")
    # record a prior search so the brief can tell the agent NOT to repeat it
    conn = api.get_conn(paths.knowledge_db("geo"))
    try:
        api.record_search(conn, query="已经搜过的旧查询", source="web")
        conn.commit()
    finally:
        conn.close()

    res = brief_ctx.assemble_brief("geo")
    assert res["snapshot_id"].startswith("ctx-")
    md = res["brief_md"]
    assert "stub 世界模型" in md                    # established worldview primes (avoid re-search)
    assert "下一轮应检索什么？" in md                  # open questions to pursue
    assert "已经搜过的旧查询" in md                    # recent query listed under "don't repeat"

    # the context was frozen durably, and the topic stage was stamped
    conn = api.get_conn(paths.knowledge_db("geo"))
    try:
        n = conn.execute("SELECT count(*) FROM context_snapshot_log WHERE snapshot_id=?",
                         (res["snapshot_id"],)).fetchone()[0]
        assert n == 1
    finally:
        conn.close()
    assert topics.load_manifest("geo")["stage"] == "deepening"


def test_repeated_synthesize_does_not_self_supersede(root, monkeypatch):
    # Regression (lint l0_version_integrity): an in-place L0 upsert — the agent re-emits a
    # byte-identical worldview, so l0_id == prev_id — must PRESERVE the row's existing predecessor,
    # never write supersedes_id = its own id. Before the fix, the 2nd identical synthesize set
    # supersedes_id = prev_id = self, corrupting the version chain.
    monkeypatch.setenv("ROS_AGENT_CMD", f"{sys.executable} {STUB}")
    topics.new_topic("geo")
    _seed_and_condense("geo")                       # 1st synthesize → active L0, supersedes=NULL
    condense_run.condense("geo", "synthesize")      # 2nd: identical content → in-place upsert
    condense_run.condense("geo", "synthesize")      # 3rd: in-place again
    conn = api.get_conn(paths.knowledge_db("geo"))
    try:
        active = conn.execute(
            "SELECT id, supersedes_id FROM l0_worldview WHERE status='active'").fetchall()
        assert len(active) == 1, "exactly one active L0"
        assert active[0]["supersedes_id"] != active[0]["id"], "active L0 must not supersede itself"
        assert conn.execute(
            "SELECT COUNT(*) FROM l0_worldview WHERE supersedes_id=id").fetchone()[0] == 0
    finally:
        conn.close()


# ---------------------------------------------------------------------------
def test_media_transcribe_stub_and_graceful_failure(root):
    topics.new_topic("t")
    stub = transcribe.transcribe("/tmp/whatever.mp4", slug="t", backend="stub")
    assert stub["status"] == "transcribed" and stub["transcript_text"]
    assert Path(stub["transcript_path"]).is_file()

    # whisper backend with no model configured → graceful 'failed', never crashes
    missing = transcribe.transcribe(str(root), backend="whisper")
    assert missing["status"] == "failed" and missing["transcript_text"] is None


def test_image_ocr_default_is_agent_path(root):
    # default zai-mcp path tells the agent to do it (Python can't call the MCP server)
    res = image_ocr.ocr("/tmp/x.png")
    assert res["status"] == "agent_required" and res["engine"] == "zai-mcp"
    # stub path returns text
    assert image_ocr.ocr("/tmp/x.png", backend="stub")["status"] == "recognized"


def test_session_report_has_sections_and_provenance(root, monkeypatch):
    monkeypatch.setenv("ROS_AGENT_CMD", f"{sys.executable} {STUB}")
    topics.new_topic("geo")
    _seed_and_condense("geo")
    fp = report_run.write_session_report("geo", facet="f_main", query="台海")
    md = Path(fp).read_text(encoding="utf-8")
    assert "## 1. 核心要点" in md
    assert "## 2. 论点与证据逻辑链" in md
    assert "https://example.com/1" in md
    assert Path(fp).parent == paths.report_sessions_dir("geo")
