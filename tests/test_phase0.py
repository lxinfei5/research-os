"""Phase 0 acceptance: topic scaffolding, the URL gate, whole-blob upsert + audit, and the
capture → promote roundtrip. Each test runs against an isolated ROS_ROOT temp dir."""
from __future__ import annotations

import json
import sqlite3

import pytest

from ros import api, paths, topics


@pytest.fixture()
def root(tmp_path, monkeypatch):
    monkeypatch.setenv("ROS_ROOT", str(tmp_path))
    return tmp_path


# ---------------------------------------------------------------------------
# topic scaffolding
# ---------------------------------------------------------------------------
def test_topic_new_builds_dbs_and_registry(root):
    m = topics.new_topic("geopolitics", title="2026 地缘政治格局", aliases=["地缘政治"])
    assert m["slug"] == "geopolitics"
    assert paths.knowledge_db("geopolitics").is_file()
    assert paths.sources_db("geopolitics").is_file()
    assert paths.topic_yaml("geopolitics").is_file()
    assert paths.index_path().is_file()

    # schema is at the current version and FK-clean
    conn = api.get_conn(paths.knowledge_db("geopolitics"))
    try:
        assert api.db_user_version(conn) == api.current_schema_version()
        assert conn.execute("PRAGMA foreign_key_check").fetchall() == []
        assert conn.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    finally:
        conn.close()


def test_alias_resolution_prevents_fork(root):
    topics.new_topic("geopolitics", aliases=["地缘政治"])
    # same name, an alias, and the title all resolve to the existing topic
    assert topics.resolve_slug("地缘政治") == "geopolitics"
    with pytest.raises(ValueError):
        topics.new_topic("地缘政治")
    with pytest.raises(ValueError):
        topics.new_topic("trading", aliases=["地缘政治"])


# ---------------------------------------------------------------------------
# URL gate (trigger) + controlled vocab
# ---------------------------------------------------------------------------
def test_url_gate_rejects_bad_sources(root):
    topics.new_topic("g")
    conn = api.get_conn(paths.knowledge_db("g"))
    try:
        # good source passes
        sid = api.add_source_ref(conn, platform="web", source_kind="article",
                                 url="https://example.com/a")
        assert sid.startswith("src-")
        conn.commit()
        # empty url rejected
        with pytest.raises(sqlite3.IntegrityError):
            api.add_source_ref(conn, platform="web", source_kind="article", url="")
        # 'dataset' placeholder rejected
        with pytest.raises(sqlite3.IntegrityError):
            api.add_source_ref(conn, platform="web", source_kind="article", url="dataset")
        # off-vocab platform rejected
        with pytest.raises(sqlite3.IntegrityError):
            api.add_source_ref(conn, platform="not_a_platform", source_kind="article",
                               url="https://x.com/1")
        # off-vocab source_kind rejected
        with pytest.raises(sqlite3.IntegrityError):
            api.add_source_ref(conn, platform="web", source_kind="not_a_kind",
                               url="https://x.com/1")
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# whole-blob upsert + audit + credibility binding
# ---------------------------------------------------------------------------
def test_l3_upsert_writes_audit_and_binds_credibility(root):
    topics.new_topic("g")
    conn = api.get_conn(paths.knowledge_db("g"))
    try:
        src = api.add_source_ref(conn, platform="x", source_kind="post",
                                 url="https://x.com/u/status/1")
        l3_id = api.gen_id("sc")
        cred = api.record_credibility(conn, subject_type="l3_claim", subject_id=l3_id,
                                      level="medium", rationale="single tier-2 source",
                                      filter_trace={"independence": "single"})
        api.upsert_l3_claim(conn, id=l3_id, proposition="X 将于近期采取 Y 行动", claim_kind="analysis",
                            single_source_ref_id=src, source_ref_ids=[src], credibility_id=cred,
                            filter_trace={"hype": "low"}, facet="f_taiwan")
        conn.commit()

        row = conn.execute("SELECT * FROM l3_claim WHERE id=?", (l3_id,)).fetchone()
        assert row["proposition"].startswith("X 将")
        assert src in json.loads(row["source_ref_ids"])

        # insert was audited
        audits = conn.execute(
            "SELECT change_kind FROM knowledge_change_log WHERE table_name='l3_claim' AND row_id=?",
            (l3_id,)).fetchall()
        assert [a["change_kind"] for a in audits] == ["insert"]

        # update path also audits, with old_blob captured
        api.upsert_l3_claim(conn, id=l3_id, proposition="修订后的论点", claim_kind="analysis",
                            single_source_ref_id=src, source_ref_ids=[src], credibility_id=cred,
                            filter_trace={"hype": "low"}, facet="f_taiwan")
        conn.commit()
        kinds = [r["change_kind"] for r in conn.execute(
            "SELECT change_kind FROM knowledge_change_log WHERE table_name='l3_claim' AND row_id=? "
            "ORDER BY id", (l3_id,)).fetchall()]
        assert kinds == ["insert", "update"]

        # credibility bound to the WRONG subject is rejected
        bad = api.record_credibility(conn, subject_type="l3_claim", subject_id="some-other-id",
                                     level="low", rationale="x", filter_trace={"a": 1})
        with pytest.raises(ValueError):
            api.upsert_l3_claim(conn, id=l3_id, proposition="p", claim_kind="fact",
                                single_source_ref_id=src, source_ref_ids=[src], credibility_id=bad,
                                filter_trace={"a": 1})
    finally:
        conn.close()


def test_echo_chamber_circuit_breaker_caps_level_low(root):
    topics.new_topic("g")
    conn = api.get_conn(paths.knowledge_db("g"))
    try:
        cred = api.record_credibility(conn, subject_type="l2_finding", subject_id="sf-1",
                                      level="high", rationale="many reposts",
                                      filter_trace={"x": 1}, echo_chamber_flag=1)
        row = conn.execute("SELECT level, rationale FROM credibility_assessment WHERE id=?",
                           (cred,)).fetchone()
        assert row["level"] == "low"
        assert "CIRCUIT BREAKER" in row["rationale"]
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# capture → promote roundtrip (the URL gate end-to-end)
# ---------------------------------------------------------------------------
def test_capture_then_promote_roundtrip(root):
    topics.new_topic("g")
    payload = {
        "query": "台海 半导体",
        "source": "web",
        "collector": "web_search",
        "items": [
            {"platform": "web", "source_kind": "article", "url": "https://example.com/a",
             "title": "A", "content": "全文 A（媒体已转写）"},
            {"platform": "web", "source_kind": "article",
             "restricted_reason": "detail behind paywall", "content": "摘要卡片"},
        ],
    }
    res = api.record_capture(payload, path=paths.sources_db("g"))
    assert res["count"] == 2

    conn = api.get_conn(paths.knowledge_db("g"))
    try:
        out = api.bulk_promote(conn, topic_slug="g", path=paths.sources_db("g"))
        assert out["counts"] == {"promoted": 1, "skipped": 1, "errors": 0}
        cov = api.coverage(conn)
        assert cov["sources"] == 1
    finally:
        conn.close()

    # the promoted item produced a library entry + a per-topic cache snapshot
    items = api.list_items(paths.sources_db("g"), promoted=True)
    assert len(items) == 1
    ch = items[0]["content_hash"]
    assert paths.library_source_path(ch).is_file()
    assert paths.cache_path("g", ch).is_file()
    lib = json.loads(paths.library_source_path(ch).read_text(encoding="utf-8"))
    assert lib["referenced_by_topics"] == ["g"]
    assert lib["url"] == "https://example.com/a"

    # promotion is idempotent
    conn = api.get_conn(paths.knowledge_db("g"))
    try:
        again = api.bulk_promote(conn, topic_slug="g", path=paths.sources_db("g"))
        assert again["counts"]["promoted"] == 0
        assert api.coverage(conn)["sources"] == 1
    finally:
        conn.close()


def test_restricted_item_cannot_be_promoted(root):
    topics.new_topic("g")
    api.record_capture({"query": "q", "source": "xiaohongshu", "collector": "xiaohongshu-mcp",
        "items": [{"platform": "xiaohongshu", "source_kind": "note",
                   "restricted_reason": "login wall", "content": "card only"}]},
        path=paths.sources_db("g"))
    item = api.list_items(paths.sources_db("g"))[0]
    conn = api.get_conn(paths.knowledge_db("g"))
    try:
        with pytest.raises(ValueError):
            api.promote_item(conn, item["id"], topic_slug="g", path=paths.sources_db("g"))
    finally:
        conn.close()
