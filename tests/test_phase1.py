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


# ---------------------------------------------------------------------------
# L0 version chain — each genuinely-new synthesize result is a new version; the
# predecessor is archived; exactly one L0 stays active; supersedes_id is real.
# ---------------------------------------------------------------------------
def _run_disk_stub(stage, in_path):
    """Invoke the on-disk stub_agent.py for one stage (subprocess, like the real condense path)."""
    import os
    import subprocess
    env = {**os.environ, "ROS_AGENT_IN": str(in_path), "ROS_AGENT_STAGE": stage}
    return subprocess.run([sys.executable, STUB, "--", ""], capture_output=True, text=True,
                          env=env, check=True).stdout


def _stub_worldview(proposition: str):
    """A fake synthesize agent: run the disk stub, then override the L0 proposition. Used to simulate
    the agent revising its world model between runs (so a genuinely-new version is produced)."""
    import json as _j

    def _fake(stage, in_path, payload):
        out = _j.loads(_run_disk_stub(stage, in_path))
        out["worldview"]["proposition"] = proposition
        return _j.dumps(out, ensure_ascii=False)
    return _fake


def test_l0_version_chain(root, monkeypatch):
    monkeypatch.setenv("ROS_AGENT_CMD", f"{sys.executable} {STUB}")
    topics.new_topic("geo")
    _seed_sources("geo")

    # round 1 → first L0 version
    condense_run.condense("geo", "all")
    conn = api.get_conn(paths.knowledge_db("geo"))
    try:
        v1 = conn.execute("SELECT id, proposition, supersedes_id, status FROM l0_worldview").fetchall()
    finally:
        conn.close()
    assert len(v1) == 1
    assert v1[0]["status"] == "active"
    assert v1[0]["supersedes_id"] is None          # first version has no predecessor

    # round 2: invalidate synthesize cache, agent revises the proposition → a NEW version
    condense_run._invalidate("geo", "synthesize")
    import ros.run.condense as CM
    monkeypatch.setattr(CM, "_run_agent",
                        _stub_worldview("修订后的世界模型：局面已显著升级。"))
    condense_run.condense("geo", "synthesize")

    conn = api.get_conn(paths.knowledge_db("geo"))
    try:
        rows = conn.execute(
            "SELECT id, proposition, supersedes_id, status FROM l0_worldview "
            "ORDER BY updated_at").fetchall()
        active = conn.execute(
            "SELECT id, supersedes_id FROM l0_worldview WHERE status='active'").fetchall()
        archived = conn.execute(
            "SELECT id, supersedes_id FROM l0_worldview WHERE status='archived'").fetchall()
        # snapshot surface still returns ONLY active rows (consumers are unaffected)
        snap = api.knowledge_snapshot(conn)
    finally:
        conn.close()

    assert len(rows) == 2                           # two versions now
    assert len(active) == 1                         # exactly one active
    assert len(archived) == 1                       # the predecessor archived
    cur = dict(active[0])
    old = dict(archived[0])
    assert cur["supersedes_id"] == old["id"]        # active points at the real predecessor
    assert cur["id"] != old["id"]                   # genuinely different ids (not self-reference)
    assert len(snap["l0_worldview"]) == 1           # snapshot = active only
    assert snap["l0_worldview"][0]["id"] == cur["id"]


def test_l0_idempotent_run_reuses_version(root, monkeypatch):
    """A re-run with identical content must NOT churn a new version (whole-blob upsert on same row)."""
    monkeypatch.setenv("ROS_AGENT_CMD", f"{sys.executable} {STUB}")
    topics.new_topic("geo")
    _seed_sources("geo")
    condense_run.condense("geo", "all")

    # invalidate + re-run synthesize with identical content (same stub) → same id, still 1 row
    condense_run._invalidate("geo", "synthesize")
    condense_run.condense("geo", "synthesize")
    conn = api.get_conn(paths.knowledge_db("geo"))
    try:
        rows = conn.execute("SELECT id, status FROM l0_worldview").fetchall()
    finally:
        conn.close()
    assert len(rows) == 1                           # no version churn on identical content


# ---------------------------------------------------------------------------
# open_question closure — the synthesize agent marks which old questions are
# now answered; the engine closes them (status=answered, answered_by_l_id set),
# so the feedback loop shrinks each round instead of only growing.
# ---------------------------------------------------------------------------
def test_open_questions_get_answered(root, monkeypatch):
    monkeypatch.setenv("ROS_AGENT_CMD", f"{sys.executable} {STUB}")
    topics.new_topic("geo")
    _seed_sources("geo")
    condense_run.condense("geo", "all")            # seeds open_questions

    conn = api.get_conn(paths.knowledge_db("geo"))
    try:
        open_before = [dict(r) for r in conn.execute(
            "SELECT id, question, status FROM open_question WHERE status='open'")]
        cov_open_before = api.coverage(conn)["open_questions"]
    finally:
        conn.close()
    assert len(open_before) >= 2                    # the stub emits >= 2 open questions

    # round 2: invalidate synthesize; the default stub answers the FIRST open question
    condense_run._invalidate("geo", "synthesize")
    condense_run.condense("geo", "synthesize")

    conn = api.get_conn(paths.knowledge_db("geo"))
    try:
        answered = [dict(r) for r in conn.execute(
            "SELECT id, status, answered_by_l_id FROM open_question WHERE id=?",
            (open_before[0]["id"],))]
        still_open = conn.execute(
            "SELECT count(*) FROM open_question WHERE status='open'").fetchone()[0]
        cov_open_after = api.coverage(conn)["open_questions"]
        # the L0 that answered it exists and is the current active worldview
        active_l0 = conn.execute(
            "SELECT id FROM l0_worldview WHERE status='active'").fetchone()["id"]
    finally:
        conn.close()

    assert answered[0]["status"] == "answered"
    assert answered[0]["answered_by_l_id"] == active_l0
    assert cov_open_after == cov_open_before - 1    # the closed one no longer counts as 'open'
    assert still_open == len(open_before) - 1       # others remain open
