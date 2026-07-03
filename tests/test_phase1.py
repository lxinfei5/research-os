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
    # the REQUIRED-collector rule is only enforced for search-like kinds: a non-search intake needn't
    # declare a search collector, and an allowed collector is fine.
    capabilities.validate_collector("x", None, capture_kind="favorites")                       # required skipped
    capabilities.validate_collector("xiaohongshu", "xiaohongshu-mcp", capture_kind="favorites")  # allowed collector
    # but a FORBIDDEN collector stays ABSOLUTE across ALL capture kinds (crown jewel — capture_kind is
    # unconstrained agent input and must not be usable to dodge the XHS browser-bridge ban).
    with pytest.raises(capabilities.CollectorPolicyError):
        capabilities.validate_collector("xiaohongshu", "kimi-webbridge", capture_kind="favorites")


def test_x_and_douyin_intake_gate(root):
    """x / 抖音 captures must pass through the FULL record_capture intake gate (not just the pure
    policy fn): the required kimi-webbridge collector is accepted end-to-end; any other collector —
    or none — is rejected at capture time (both are pinned, not collector_optional)."""
    topics.new_topic("g")
    for src, item in (
        ("x", {"platform": "x", "source_kind": "post",
               "url": "https://x.com/kol/status/1", "content": "某 KOL 的观点"}),
        ("douyin", {"platform": "douyin", "source_kind": "video",
                    "url": "https://www.douyin.com/video/1", "content": "短视频转写文本"}),
    ):
        base = {"query": "q", "source": src, "capture_kind": "search", "items": [item]}
        # required collector accepted through the full intake path
        assert api.record_capture({**base, "collector": "kimi-webbridge"},
                                  path=paths.sources_db("g"))["count"] == 1
        # wrong collector rejected at capture time
        for bad in ("xiaohongshu-mcp", "browser"):
            with pytest.raises(capabilities.CollectorPolicyError):
                api.record_capture({**base, "collector": bad}, path=paths.sources_db("g"))
        # missing collector rejected (x/douyin are not collector_optional)
        with pytest.raises(capabilities.CollectorPolicyError):
            api.record_capture(base, path=paths.sources_db("g"))


def test_webbridge_mcp_intake_gate(root):
    """webbridge-mcp is the sub-agent-reachable transport that fronts the same real Chrome as the
    kimi-webbridge skill. Through the FULL record_capture intake gate: x / 抖音 ACCEPT it end-to-end;
    web ACCEPTS it as the fetch-Tier-3 browser reader; and — the crown jewel — xiaohongshu REJECTS it
    (a general browser bridge, MCP or skill, must never scrape XHS), including a per-item platform spoof
    that declares source:web but smuggles an xhs item collected via webbridge-mcp."""
    topics.new_topic("g")
    sdb = paths.sources_db("g")

    # x + 抖音 accept webbridge-mcp through the full intake path (sub-agent transport)
    for src, item in (
        ("x", {"platform": "x", "source_kind": "post",
               "url": "https://x.com/kol/status/2", "content": "子 agent 直抓的 KOL 观点"}),
        ("douyin", {"platform": "douyin", "source_kind": "video",
                    "url": "https://www.douyin.com/video/2", "content": "子 agent 直抓的短视频转写"}),
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

    # crown jewel: xiaohongshu REJECTS webbridge-mcp at capture time (direct + alias)
    for src in ("xiaohongshu", "小红书"):
        with pytest.raises(capabilities.CollectorPolicyError):
            api.record_capture(
                {"query": "q", "source": src, "capture_kind": "search", "collector": "webbridge-mcp",
                 "items": [{"platform": src, "source_kind": "note",
                            "url": "https://www.xiaohongshu.com/x", "content": "x"}]}, path=sdb)

    # per-item spoof: session says web, item is an xhs note grabbed via webbridge-mcp → still caught
    with pytest.raises(capabilities.CollectorPolicyError):
        api.record_capture(
            {"query": "q", "source": "web", "capture_kind": "search", "collector": "webbridge-mcp",
             "items": [{"platform": "xiaohongshu", "source_kind": "note",
                        "url": "https://www.xiaohongshu.com/y", "content": "smuggled"}]}, path=sdb)


def test_crown_jewel_survives_off_search_capture_kind(root):
    """Regression: the XHS forbid must hold for ANY capture_kind. capture_kind is agent-supplied free
    text with no enum; the gate used to skip forbidden-collector checks for kinds outside
    {search,detail,fetch}, so `capture_kind:"note"` let webbridge-mcp/kimi-webbridge scrape XHS
    through the FULL record_capture path (and ros lint re-validated with the same stored kind, so it
    was invisible there too). Every off-search kind must now still be rejected at capture time."""
    topics.new_topic("g")
    sdb = paths.sources_db("g")
    for bad in ("webbridge-mcp", "kimi-webbridge", "browser"):
        for kind in ("note", "favorites", "likes", "web_page", "detail"):
            # direct: source=xiaohongshu (+ alias) with a forbidden bridge under an off-search kind
            for src in ("xiaohongshu", "小红书"):
                with pytest.raises(capabilities.CollectorPolicyError):
                    api.record_capture(
                        {"query": "q", "source": src, "capture_kind": kind, "collector": bad,
                         "items": [{"platform": src, "source_kind": "note",
                                    "url": "https://www.xiaohongshu.com/z", "content": "x"}]}, path=sdb)
            # per-item spoof: session=web, xhs item, forbidden bridge, off-search kind → still caught
            with pytest.raises(capabilities.CollectorPolicyError):
                api.record_capture(
                    {"query": "q", "source": "web", "capture_kind": kind, "collector": bad,
                     "items": [{"platform": "xiaohongshu", "source_kind": "note",
                                "url": "https://www.xiaohongshu.com/w", "content": "smuggled"}]}, path=sdb)


def test_crown_jewel_fails_closed_on_off_list_xhs_source_spelling(root):
    """Regression: the XHS forbid must hold even when the source/platform is spelled with an id that
    isn't enumerated in _ALIASES — the real domain, traditional Chinese, `…APP`. canonical() fails
    closed on XHS stems, so record_capture rejects these instead of writing a real XHS row via a
    browser bridge (the strongest bypass the adversarial re-verify found)."""
    topics.new_topic("g")
    sdb = paths.sources_db("g")
    for spelling in ("www.xiaohongshu.com", "小紅書", "小红书APP"):
        # declared source is the off-list XHS spelling
        with pytest.raises(capabilities.CollectorPolicyError):
            api.record_capture(
                {"query": "q", "source": spelling, "capture_kind": "note", "collector": "kimi-webbridge",
                 "items": [{"platform": spelling, "source_kind": "note",
                            "url": "https://www.xiaohongshu.com/explore/aaa",
                            "content": "scraped via real browser"}]}, path=sdb)
        # spoof: session=web, item platform is the off-list XHS spelling via a browser bridge
        with pytest.raises(capabilities.CollectorPolicyError):
            api.record_capture(
                {"query": "q", "source": "web", "capture_kind": "note", "collector": "webbridge-mcp",
                 "items": [{"platform": spelling, "source_kind": "note",
                            "url": "https://www.xiaohongshu.com/explore/bbb", "content": "smuggled"}]},
                path=sdb)


def test_degraded_all_providers_failed_capture(root):
    """Fail-visible contract: record_capture REJECTS an empty items:[] (never a silent drop) and
    ACCEPTS the degraded shape — one url-less placeholder item + restricted_reason, with
    degraded_reason + raw_tool_status.fallback_chain persisted for audit. The placeholder stays
    raw-only: with no url the URL gate never promotes it (bulk_promote skips it)."""
    topics.new_topic("g")
    sdb = paths.sources_db("g")

    # (1) empty items → rejected with the guard's ValueError (not a silent empty capture)
    with pytest.raises(ValueError, match="non-empty"):
        api.record_capture({"query": "乌克兰 停火", "source": "web",
                            "collector": "multi-search-engine", "capture_kind": "search",
                            "items": []}, path=sdb)

    # (2) the degraded placeholder shape is accepted and its audit trail persists
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
