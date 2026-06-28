"""Phase 1 acceptance: the Xiaohongshu collector-policy gate, the full condense chain
(source → L3 → L2 → L1 → L0) driven by a deterministic stub agent, and the world_model.md render."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from ros import api, paths, topics
from ros.run import condense as condense_run, report as report_run
from ros.search import capabilities

STUB = str(Path(__file__).resolve().parent / "stub_agent.py")


@pytest.fixture()
def root(tmp_path, monkeypatch):
    monkeypatch.setenv("ROS_ROOT", str(tmp_path))
    return tmp_path


# ---------------------------------------------------------------------------
# Xiaohongshu hard constraint — the collector policy gate
# ---------------------------------------------------------------------------
def test_xhs_must_not_use_kimi_webbridge(root):
    topics.new_topic("g")
    xhs_item = {"platform": "xiaohongshu", "source_kind": "note",
                "url": "https://www.xiaohongshu.com/explore/abc", "content": "笔记正文"}

    def cap(collector):
        return {"query": "q", "source": "xiaohongshu", "collector": collector,
                "capture_kind": "search", "items": [xhs_item]}

    # forbidden collectors rejected
    for bad in ("kimi-webbridge", "browser"):
        with pytest.raises(capabilities.CollectorPolicyError):
            api.record_capture(cap(bad), path=paths.sources_db("g"))
    # missing collector rejected (xhs is not collector_optional and has a required collector)
    with pytest.raises(capabilities.CollectorPolicyError):
        api.record_capture({"query": "q", "source": "xiaohongshu", "capture_kind": "search",
                            "items": [xhs_item]}, path=paths.sources_db("g"))
    # the required collector is accepted
    res = api.record_capture(cap("xiaohongshu-mcp"), path=paths.sources_db("g"))
    assert res["count"] == 1


def test_xhs_gate_airtight_against_alias_and_spoof(root):
    topics.new_topic("g")
    # (a) alias source "小红书" + kimi-webbridge → rejected (alias normalized to xiaohongshu)
    with pytest.raises(capabilities.CollectorPolicyError):
        api.record_capture({"query": "q", "source": "小红书", "collector": "kimi-webbridge",
            "items": [{"platform": "小红书", "source_kind": "note",
                       "url": "https://www.xiaohongshu.com/x", "content": "c"}]},
            path=paths.sources_db("g"))
    # (b) spoof: source=manual (unconstrained) but smuggling a xiaohongshu item via kimi-webbridge
    #     → rejected by the per-item-platform check
    with pytest.raises(capabilities.CollectorPolicyError):
        api.record_capture({"query": "q", "source": "manual", "collector": "kimi-webbridge",
            "items": [{"platform": "xiaohongshu", "source_kind": "note",
                       "url": "https://www.xiaohongshu.com/y", "content": "c"}]},
            path=paths.sources_db("g"))


def test_collector_policy_unit():
    # web is collector-optional (any tier) — missing collector is fine
    capabilities.validate_collector("web", None)
    capabilities.validate_collector("web", "web_search")
    # x requires kimi-webbridge
    with pytest.raises(capabilities.CollectorPolicyError):
        capabilities.validate_collector("x", "xiaohongshu-mcp")
    capabilities.validate_collector("x", "kimi-webbridge")
    # non-search capture kinds are not gated
    capabilities.validate_collector("xiaohongshu", "kimi-webbridge", capture_kind="favorites")


# ---------------------------------------------------------------------------
# full condense chain via the stub agent
# ---------------------------------------------------------------------------
def _seed_sources(slug: str) -> None:
    payload = {
        "query": "地缘政治 台海", "source": "web", "collector": "web_search",
        "items": [
            {"platform": "web", "source_kind": "article", "url": f"https://example.com/{i}",
             "title": f"文章{i}", "author": "作者", "content": f"原文内容 {i}：某项关键进展……"}
            for i in range(1, 4)
        ],
    }
    api.record_capture(payload, path=paths.sources_db(slug))
    conn = api.get_conn(paths.knowledge_db(slug))
    try:
        api.bulk_promote(conn, topic_slug=slug, path=paths.sources_db(slug))
    finally:
        conn.close()


def test_condense_builds_full_ladder(root, monkeypatch):
    monkeypatch.setenv("ROS_AGENT_CMD", f"{sys.executable} {STUB}")
    topics.new_topic("geo", title="地缘政治")
    _seed_sources("geo")

    res = condense_run.condense("geo", "all")
    assert res["distill"]["rows_written"] == 3

    conn = api.get_conn(paths.knowledge_db("geo"))
    try:
        cov = api.coverage(conn)
        assert cov["l3"] == 3
        assert cov["l2"] >= 1
        assert cov["l1"] >= 1
        assert cov["l0"] == 1
        # open questions from the worldview were recorded
        oq = conn.execute("SELECT count(*) FROM open_question WHERE status='open'").fetchone()[0]
        assert oq >= 2
        # every evidence row is bound to a credibility row (NOT NULL FK held)
        for tbl in ("l3_claim", "l2_finding", "l1_viewpoint", "l0_worldview"):
            missing = conn.execute(
                f"SELECT count(*) FROM {tbl} WHERE credibility_id IS NULL").fetchone()[0]
            assert missing == 0
        assert conn.execute("PRAGMA foreign_key_check").fetchall() == []
    finally:
        conn.close()


def test_condense_is_idempotent_and_resumable(root, monkeypatch):
    monkeypatch.setenv("ROS_AGENT_CMD", f"{sys.executable} {STUB}")
    topics.new_topic("geo")
    _seed_sources("geo")
    condense_run.condense("geo", "all")

    # second run: distill units all cached (.out.json present) → ran=0, counts unchanged
    res2 = condense_run.condense("geo", "all")
    assert res2["distill"]["ran"] == 0
    conn = api.get_conn(paths.knowledge_db("geo"))
    try:
        cov = api.coverage(conn)
        assert cov["l3"] == 3 and cov["l0"] == 1
    finally:
        conn.close()


def test_world_model_render_has_provenance(root, monkeypatch):
    monkeypatch.setenv("ROS_AGENT_CMD", f"{sys.executable} {STUB}")
    topics.new_topic("geo", title="地缘政治")
    _seed_sources("geo")
    condense_run.condense("geo", "all")

    fp = report_run.write_world_model("geo")
    md = Path(fp).read_text(encoding="utf-8")
    assert "世界模型" in md
    assert "stub 世界模型" in md                      # L0 proposition rendered
    assert "https://example.com/1" in md             # source link retained
    assert "topics/geo/cache/" in md                 # cached-text snapshot path retained
    assert "## 2. 开放问题" in md                      # open-questions section present
    assert Path(paths.reports_dir("geo") / "world_model.md").is_file()
