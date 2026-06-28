"""Phase 4 acceptance: the method lane (M0/M1), cross-topic export/import with the fresh-condense
(draft) gate, and topic merge (links sources, archives src, no evidence-row copy)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

from ros import api, paths, topics
from ros.run import condense as condense_run

STUB = str(Path(__file__).resolve().parent / "stub_agent.py")


@pytest.fixture()
def root(tmp_path, monkeypatch):
    monkeypatch.setenv("ROS_ROOT", str(tmp_path))
    return tmp_path


def _cap_promote(slug, url, content):
    api.record_capture({"query": "q", "source": "web", "collector": "web_search",
                        "items": [{"platform": "web", "source_kind": "article", "url": url,
                                   "content": content}]}, path=paths.sources_db(slug))
    conn = api.get_conn(paths.knowledge_db(slug))
    try:
        api.bulk_promote(conn, topic_slug=slug, path=paths.sources_db(slug))
    finally:
        conn.close()


# ---------------------------------------------------------------------------
def test_method_lane_m0_m1(root):
    topics.new_topic("geo")
    conn = api.get_conn(paths.knowledge_db("geo"))
    try:
        m0 = api.method_upsert(conn, level="M0", proposition="交叉验证行动而非声明")
        api.method_upsert(conn, level="M1", proposition="印证期转向跨平台",
                          valid_if={"stage": "corroborating"})
        conn.commit()
        rules = api.method_list(conn)
        assert {r["level"] for r in rules} == {"M0", "M1"}
        m1 = [r for r in rules if r["level"] == "M1"][0]
        assert '"stage"' in m1["valid_if"]                      # valid_if persisted as JSON
        # method rows carry NO credibility / source columns (pure logic, physically isolated)
        cols = {c[1] for c in conn.execute("PRAGMA table_info(method_rule)").fetchall()}
        assert "credibility_id" not in cols and "source_ref_ids" not in cols
        assert m0.startswith("mr-")
    finally:
        conn.close()


def test_method_export_import_is_draft_gated(root):
    topics.new_topic("geo")
    topics.new_topic("trade")
    conn = api.get_conn(paths.knowledge_db("geo"))
    try:
        rid = api.method_upsert(conn, level="M0", proposition="官方表态与行动常背离")
        conn.commit()
    finally:
        conn.close()

    api.method_export("geo", rid)
    assert any(r["id"] == rid for r in api.method_list_shared())

    res = api.method_import(rid, "trade")
    assert res["status"] == "draft"                            # fresh-condense gate
    conn = api.get_conn(paths.knowledge_db("trade"))
    try:
        imported = api.method_list(conn)
        assert len(imported) == 1
        assert imported[0]["status"] == "draft"               # not auto-active
        assert imported[0]["id"].startswith("mr-imp-")
    finally:
        conn.close()


# ---------------------------------------------------------------------------
def test_topic_merge_links_sources_and_archives_src(root, monkeypatch):
    monkeypatch.setenv("ROS_AGENT_CMD", f"{sys.executable} {STUB}")
    topics.new_topic("ai_chips")
    topics.new_topic("geopolitics")
    _cap_promote("ai_chips", "https://example.com/chip", "芯片出口管制原文")
    _cap_promote("geopolitics", "https://example.com/geo", "地缘政治原文")

    res = topics.merge_topic("ai_chips", "geopolitics")
    assert res["linked_sources"] == 1

    # geopolitics now references BOTH sources; no evidence rows were copied (it must re-distill)
    conn = api.get_conn(paths.knowledge_db("geopolitics"))
    try:
        urls = {r[0] for r in conn.execute("SELECT url FROM source_ref")}
        assert urls == {"https://example.com/geo", "https://example.com/chip"}
        assert conn.execute("SELECT count(*) FROM l3_claim").fetchone()[0] == 0  # not yet condensed
    finally:
        conn.close()

    # src archived
    assert any(t["slug"] == "ai_chips" and t["status"] == "archived" for t in topics.list_topics())

    # and a re-condense distills the linked source under the dst's lens
    condense_run.condense("geopolitics", "all")
    conn = api.get_conn(paths.knowledge_db("geopolitics"))
    try:
        assert conn.execute("SELECT count(*) FROM l3_claim").fetchone()[0] == 2
    finally:
        conn.close()
