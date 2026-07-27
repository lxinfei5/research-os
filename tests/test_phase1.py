"""Phase 1 acceptance: the Xiaohongshu collector-policy gate, the full condense chain
(source → L3 → L2 → L1 → L0) driven by a deterministic stub agent, and the world_model.md render."""
from __future__ import annotations

import json
import sqlite3
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
def test_xhs_allows_browser_and_mcp_collectors(root):
    """XHS multi-path + soft gate: preferred collectors and off-list both write."""
    topics.new_topic("g")
    xhs_item = {"platform": "xiaohongshu", "source_kind": "note",
                "url": "https://www.xiaohongshu.com/explore/abc", "content": "笔记正文"}

    def cap(collector):
        return {"query": "q", "source": "xiaohongshu", "collector": collector,
                "capture_kind": "search", "items": [xhs_item]}

    for ok_coll in ("xiaohongshu-mcp", "webbridge-mcp", "kimi-webbridge"):
        res = api.record_capture(cap(ok_coll), path=paths.sources_db("g"))
        assert res["count"] == 1
        assert not res.get("warnings")
    # missing collector → soft warn, still writes
    res_miss = api.record_capture({"query": "q2", "source": "xiaohongshu", "capture_kind": "search",
                                   "items": [xhs_item]}, path=paths.sources_db("g"))
    assert res_miss["count"] == 1
    assert res_miss.get("warnings")
    # off-list collector name → soft warn, still writes
    res_off = api.record_capture(cap("browser"), path=paths.sources_db("g"))
    assert res_off["count"] == 1
    assert any("preferred" in w or "soft gate" in w for w in res_off.get("warnings", []))


def test_xhs_alias_and_browser_path_accepted(root):
    topics.new_topic("g")
    # alias source "小红书" + kimi-webbridge → accepted (multi-path)
    res = api.record_capture({"query": "q", "source": "小红书", "collector": "kimi-webbridge",
        "items": [{"platform": "小红书", "source_kind": "note",
                   "url": "https://www.xiaohongshu.com/x", "content": "c"}]},
        path=paths.sources_db("g"))
    assert res["count"] == 1
    # session=manual + xhs item via webbridge-mcp also accepted (per-item allow-list)
    res2 = api.record_capture({"query": "q", "source": "manual", "collector": "webbridge-mcp",
        "items": [{"platform": "xiaohongshu", "source_kind": "note",
                   "url": "https://www.xiaohongshu.com/y", "content": "c"}]},
        path=paths.sources_db("g"))
    assert res2["count"] == 1


def test_collector_policy_unit():
    # web preferred list is optional — missing collector is fine (no warn when optional)
    assert capabilities.validate_collector("web", None) == []
    assert capabilities.validate_collector("web", "web_search") == []
    # x preferred: off-list → warn, not raise
    warns = capabilities.validate_collector("x", "xiaohongshu-mcp")
    assert warns and "preferred" in warns[0]
    assert capabilities.validate_collector("x", "kimi-webbridge") == []
    # required-collector soft rule only for search-like kinds
    assert capabilities.validate_collector("x", None, capture_kind="favorites") == []
    # XHS multi-path preferred collectors clean
    assert capabilities.validate_collector("xiaohongshu", "xiaohongshu-mcp", capture_kind="favorites") == []
    assert capabilities.validate_collector("xiaohongshu", "kimi-webbridge", capture_kind="favorites") == []
    assert capabilities.validate_collector("xiaohongshu", "webbridge-mcp", capture_kind="note") == []


def test_x_and_douyin_intake_gate(root):
    """x / 抖音: preferred collectors clean; off-list / missing still write with warnings."""
    topics.new_topic("g")
    for src, item in (
        ("x", {"platform": "x", "source_kind": "post",
               "url": "https://x.com/kol/status/1", "content": "某 KOL 的观点"}),
        ("douyin", {"platform": "douyin", "source_kind": "video",
                    "url": "https://www.douyin.com/video/1", "content": "短视频转写文本"}),
    ):
        base = {"query": "q", "source": src, "capture_kind": "search", "items": [item]}
        res_ok = api.record_capture({**base, "collector": "kimi-webbridge"},
                                    path=paths.sources_db("g"))
        assert res_ok["count"] == 1
        assert not res_ok.get("warnings")
        # off-list collector soft-accepted
        for off in ("xiaohongshu-mcp", "browser"):
            r = api.record_capture({**base, "collector": off, "query": f"q-{off}-{src}"},
                                   path=paths.sources_db("g"))
            assert r["count"] == 1
            assert r.get("warnings")
        # missing collector soft-accepted
        r_miss = api.record_capture({**base, "query": f"q-miss-{src}"}, path=paths.sources_db("g"))
        assert r_miss["count"] == 1
        assert r_miss.get("warnings")


def test_webbridge_mcp_intake_gate(root):
    """webbridge-mcp accepted for x / 抖音 / web / 小红书 (multi-path social)."""
    topics.new_topic("g")
    sdb = paths.sources_db("g")

    for src, item in (
        ("x", {"platform": "x", "source_kind": "post",
               "url": "https://x.com/kol/status/2", "content": "子 agent 直抓的 KOL 观点"}),
        ("douyin", {"platform": "douyin", "source_kind": "video",
                    "url": "https://www.douyin.com/video/2", "content": "子 agent 直抓的短视频转写"}),
        ("xiaohongshu", {"platform": "xiaohongshu", "source_kind": "note",
                         "url": "https://www.xiaohongshu.com/explore/wb1", "content": "浏览器抓的笔记"}),
    ):
        assert api.record_capture(
            {"query": "q", "source": src, "capture_kind": "search",
             "collector": "webbridge-mcp", "items": [item]}, path=sdb)["count"] == 1

    # web accepts webbridge-mcp as the fetch-Tier-3 browser reader
    assert api.record_capture(
        {"query": "q", "source": "web", "capture_kind": "fetch", "collector": "webbridge-mcp",
         "items": [{"platform": "web", "source_kind": "article",
                    "url": "https://spa.example.com/x", "content": "JS 渲染页浏览器兜底读到的正文"}]},
        path=sdb)["count"] == 1

    # alias 小红书 + webbridge-mcp accepted
    assert api.record_capture(
        {"query": "q", "source": "小红书", "capture_kind": "search", "collector": "webbridge-mcp",
         "items": [{"platform": "小红书", "source_kind": "note",
                    "url": "https://www.xiaohongshu.com/x", "content": "x"}]}, path=sdb)["count"] == 1


def test_xhs_canonical_resolves_off_list_spellings(root):
    """Off-list XHS spellings still canonicalize so platform labeling stays honest."""
    topics.new_topic("g")
    sdb = paths.sources_db("g")
    for spelling in ("www.xiaohongshu.com", "小紅書", "小红书APP"):
        assert capabilities.canonical(spelling) == "xiaohongshu"
        res = api.record_capture(
            {"query": "q", "source": spelling, "capture_kind": "search",
             "collector": "kimi-webbridge",
             "items": [{"platform": spelling, "source_kind": "note",
                        "url": "https://www.xiaohongshu.com/explore/aaa",
                        "content": "scraped via real browser"}]}, path=sdb)
        assert res["count"] == 1


def test_degraded_all_providers_failed_capture(root):
    """Loud empty slot: items=[] requires degraded_reason; placeholder shape still works."""
    topics.new_topic("g")
    sdb = paths.sources_db("g")

    # (1) silent empty items → rejected
    with pytest.raises(ValueError, match="degraded_reason"):
        api.record_capture({"query": "乌克兰 停火", "source": "web",
                            "collector": "multi-search-engine", "capture_kind": "search",
                            "items": []}, path=sdb)

    # (1b) empty items + degraded_reason → accepted (loud empty slot, no fake placeholder)
    res_empty = api.record_capture({
        "query": "乌克兰 停火 empty", "source": "web", "collector": "multi-search-engine",
        "capture_kind": "search", "result_count": 0,
        "degraded_reason": "all_search_engines_failed",
        "items": [],
        "raw_tool_status": {"fallback_chain": [{"tier": 3, "provider": "multi-search-engine",
                                                "status": "failed"}]},
    }, path=sdb)
    assert res_empty["count"] == 0
    assert res_empty["degraded"] is True

    # (2) the degraded placeholder shape is still accepted and its audit trail persists
    res = api.record_capture({
        "query": "乌克兰 停火", "source": "web", "collector": "multi-search-engine",
        "capture_kind": "search", "result_count": 0,
        "degraded_reason": "all_search_engines_failed",
        "items": [{"platform": "web", "source_kind": "search_result", "needs_review": True,
                   "restricted_reason": "all_search_engines_failed",
                   "content": "All Tier-3 engines failed; no candidates (see fallback_chain)."}],
        "raw_tool_status": {"engines_attempted": ["Baidu", "Bing CN"], "engines_succeeded": [],
                            "engines_failed": {"Baidu": "403", "Bing CN": "captcha"},
                            "fallback_chain": [{"tier": 3, "provider": "multi-search-engine",
                                                "status": "failed"}]},
    }, path=sdb)
    assert res["count"] == 1
    assert res["items"][0]["restricted"] is True           # url-less placeholder marked restricted

    conn = sqlite3.connect(str(sdb))
    conn.row_factory = sqlite3.Row
    try:
        sess = conn.execute("SELECT degraded_reason, raw_tool_status FROM source_session "
                            "WHERE id=?", (res["session_id"],)).fetchone()
    finally:
        conn.close()
    assert sess["degraded_reason"] == "all_search_engines_failed"
    rts = json.loads(sess["raw_tool_status"])
    assert rts["fallback_chain"][0]["provider"] == "multi-search-engine"
    assert rts["engines_failed"]["Baidu"] == "403"

    # (3) the placeholder is raw-only: no url → bulk_promote SKIPS it (URL gate never lifts it)
    kconn = api.get_conn(paths.knowledge_db("g"))
    try:
        bp = api.bulk_promote(kconn, topic_slug="g", path=sdb)
    finally:
        kconn.close()
    assert bp["counts"]["promoted"] == 0 and bp["counts"]["skipped"] == 1


def test_web_tier3_fallback_shape_round_trips_through_intake(root):
    """The 3-tier web fallback capture shape must survive the FULL record_capture intake path: a
    Tier-3 multi-search-engine search AND a fetch-Tier-3 kimi-webbridge browser read both pass the
    web gate, and raw_tool_status.fallback_chain / quota_status persist verbatim for audit."""
    topics.new_topic("g")
    sdb = paths.sources_db("g")

    res = api.record_capture({
        "query": "HBM 供应链", "source": "web", "collector": "multi-search-engine",
        "capture_kind": "search",
        "items": [{"platform": "web", "source_kind": "search_result", "needs_review": True,
                   "url": "https://example.com/hbm", "title": "HBM", "content": "线索片段"}],
        "raw_tool_status": {
            "fallback_chain": [
                {"tier": 1, "provider": "web-search-prime", "status": "quota_exhausted", "error": "429"},
                {"tier": 2, "provider": "WebSearch", "status": "failed", "error": "0 results"},
                {"tier": 3, "provider": "multi-search-engine", "status": "partial"}],
            "quota_status": {"zhipu_search": "exhausted", "zhipu_reader": "available"},
            "engines_attempted": ["Baidu", "Bing CN"]},
    }, path=sdb)
    assert res["count"] == 1

    # fetch-Tier-3 browser read (kimi-webbridge) of a JS/anti-bot page also passes the web gate
    res2 = api.record_capture({
        "query": "HBM 供应链", "source": "web", "collector": "kimi-webbridge",
        "capture_kind": "fetch",
        "items": [{"platform": "web", "source_kind": "web_page",
                   "url": "https://example.com/js-page", "content": "浏览器渲染后的正文"}],
    }, path=sdb)
    assert res2["count"] == 1

    # the audit trail round-trips: fallback_chain + quota_status persisted verbatim on the session
    conn = sqlite3.connect(str(sdb))
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute("SELECT raw_tool_status FROM source_session WHERE id=?",
                           (res["session_id"],)).fetchone()
    finally:
        conn.close()
    rts = json.loads(row["raw_tool_status"])
    assert [c["tier"] for c in rts["fallback_chain"]] == [1, 2, 3]
    assert rts["quota_status"]["zhipu_search"] == "exhausted"


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
