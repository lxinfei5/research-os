"""Phase 3 acceptance: cross-topic library sharing (no contamination), library link (no re-fetch),
boundary gates, snapshot export, and drift re-condense."""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

from ros import api, paths, topics
from ros.boundary import gates
from ros.run import condense as condense_run

STUB = str(Path(__file__).resolve().parent / "stub_agent.py")


@pytest.fixture()
def root(tmp_path, monkeypatch):
    monkeypatch.setenv("ROS_ROOT", str(tmp_path))
    return tmp_path


SHARED_URL = "https://example.com/shared-report"
SHARED = {"platform": "web", "source_kind": "article", "url": SHARED_URL,
          "title": "共享原文", "content": "同一篇报道，被两个主题引用。"}


def _capture_promote(slug, item):
    api.record_capture({"query": "q", "source": "web", "collector": "web_search", "items": [item]},
                       path=paths.sources_db(slug))
    conn = api.get_conn(paths.knowledge_db(slug))
    try:
        api.bulk_promote(conn, topic_slug=slug, path=paths.sources_db(slug))
    finally:
        conn.close()


# ---------------------------------------------------------------------------
def test_same_source_shared_one_library_entry_independent_provenance(root):
    topics.new_topic("geopolitics")
    topics.new_topic("chips")
    _capture_promote("geopolitics", SHARED)
    _capture_promote("chips", SHARED)

    shared = api.shared_sources()
    assert len(shared) == 1
    rec = shared[0]
    assert rec["referenced_by_topics"] == ["chips", "geopolitics"]   # both, sorted
    ch = rec["content_hash"]
    # ONE global library entry, but each topic has its OWN source_ref + cache (independent provenance)
    for slug in ("geopolitics", "chips"):
        conn = api.get_conn(paths.knowledge_db(slug))
        try:
            assert conn.execute("SELECT count(*) FROM source_ref WHERE content_hash=?",
                                (ch,)).fetchone()[0] == 1
        finally:
            conn.close()
        assert paths.cache_path(slug, ch).is_file()


def test_related_edges_computed(root):
    topics.new_topic("a")
    topics.new_topic("b")
    _capture_promote("a", SHARED)
    _capture_promote("b", SHARED)
    co = topics.update_related()
    assert co.get("a") == ["b"] and co.get("b") == ["a"]
    # persisted into _index.yaml
    import yaml
    idx = yaml.safe_load(paths.index_path().read_text(encoding="utf-8"))
    edges = {t["slug"]: t.get("related") for t in idx["topics"]}
    assert edges["a"] == [{"slug": "b", "relation": "shares_source"}]


def test_library_link_reuses_without_refetch(root):
    topics.new_topic("a")
    topics.new_topic("b")
    _capture_promote("a", SHARED)           # only 'a' captured it
    ch = api.list_sources()[0]["content_hash"]

    conn = api.get_conn(paths.knowledge_db("b"))
    try:
        res = api.link_source(conn, ch, topic_slug="b")
        assert res["already_linked"] is False
        assert conn.execute("SELECT count(*) FROM source_ref WHERE content_hash=?",
                            (ch,)).fetchone()[0] == 1
        # idempotent
        assert api.link_source(conn, ch, topic_slug="b")["already_linked"] is True
    finally:
        conn.close()
    # 'b' never captured into its sources.db, yet now references the shared original
    assert api.list_items(paths.sources_db("b")) == []
    assert api.read_source(ch)["referenced_by_topics"] == ["a", "b"]
    assert paths.cache_path("b", ch).is_file()


def test_multi_topic_no_cross_contamination(root, monkeypatch):
    monkeypatch.setenv("ROS_AGENT_CMD", f"{sys.executable} {STUB}")
    topics.new_topic("geo")
    topics.new_topic("trade")
    _capture_promote("geo", {"platform": "web", "source_kind": "article",
                             "url": "https://example.com/geo", "content": "地缘政治原文"})
    _capture_promote("trade", {"platform": "web", "source_kind": "article",
                               "url": "https://example.com/trade", "content": "交易方法论原文"})
    condense_run.condense("geo", "all")
    condense_run.condense("trade", "all")

    cg = api.get_conn(paths.knowledge_db("geo"))
    ct = api.get_conn(paths.knowledge_db("trade"))
    try:
        geo_src = {r[0] for r in cg.execute("SELECT url FROM source_ref")}
        trade_src = {r[0] for r in ct.execute("SELECT url FROM source_ref")}
    finally:
        cg.close()
        ct.close()
    assert geo_src == {"https://example.com/geo"}
    assert trade_src == {"https://example.com/trade"}   # zero bleed between topic DBs


# ---------------------------------------------------------------------------
def test_boundary_gates_pass_on_healthy_topic(root, monkeypatch):
    monkeypatch.setenv("ROS_AGENT_CMD", f"{sys.executable} {STUB}")
    topics.new_topic("geo")
    _capture_promote("geo", SHARED)
    condense_run.condense("geo", "all")
    # write the repo .gitignore patterns into the temp root so db_git_safety passes there
    (root / ".gitignore").write_text("topics/*/knowledge.db\ntopics/*/sources.db\n", encoding="utf-8")
    results = {name: (ok, probs) for name, ok, probs in gates.run_all()}
    for name, (ok, probs) in results.items():
        assert ok, f"{name} failed: {probs}"


def test_collector_policy_gate_catches_injected_violation(root):
    topics.new_topic("geo")
    api.init_store(paths.sources_db("geo"))
    # bypass the capture-time gate by writing a forbidden session straight into sources.db
    conn = sqlite3.connect(paths.sources_db("geo"))
    conn.execute("INSERT INTO source_session (id,query,source,collector,capture_kind,searched_at) "
                 "VALUES ('rs-bad','q','xiaohongshu','kimi-webbridge','search',datetime('now'))")
    conn.commit()
    conn.close()
    name, ok, problems = gates.lint_collector_policy()
    assert not ok and any("kimi-webbridge" in p for p in problems)


def test_boundary_gates_survive_a_hollow_knowledge_db(root):
    """A hollow knowledge.db — the file exists (an aborted command merely opened a sqlite connection,
    which creates it) but has no L tables — must NOT crash run_all() with `no such table`. schema_drift
    owns the report; the provenance/version gates skip it."""
    topics.new_topic("geo")
    db = paths.knowledge_db("geo")
    db.unlink()                                   # drop the schema-full db new_topic built
    sqlite3.connect(str(db)).close()              # recreate hollow (0 tables), like the aborted command
    results = {name: (ok, probs) for name, ok, probs in gates.run_all()}   # must not raise
    assert results["snapshot_provenance"][0] is True     # skipped, not crashed
    assert results["l0_version_integrity"][0] is True     # skipped, not crashed
    assert results["schema_drift"][0] is False            # schema_drift catches the hollow db


def test_snapshot_export(root, monkeypatch):
    monkeypatch.setenv("ROS_AGENT_CMD", f"{sys.executable} {STUB}")
    topics.new_topic("geo")
    _capture_promote("geo", SHARED)
    condense_run.condense("geo", "all")
    from ros.cli import _dump_knowledge
    out = Path(_dump_knowledge("geo"))
    assert out.is_file() and out.parent == paths.snapshots_dir("geo")
    sql = out.read_text(encoding="utf-8")
    assert "CREATE TABLE" in sql and "l3_claim" in sql


def test_resediment_is_idempotent(root, monkeypatch):
    monkeypatch.setenv("ROS_AGENT_CMD", f"{sys.executable} {STUB}")
    topics.new_topic("geo")
    _capture_promote("geo", SHARED)
    _capture_promote("geo", {"platform": "web", "source_kind": "article",
                             "url": "https://example.com/2", "content": "第二篇"})
    condense_run.condense("geo", "all")
    conn = api.get_conn(paths.knowledge_db("geo"))
    try:
        before = api.coverage(conn)
    finally:
        conn.close()
    condense_run.resediment("geo", force=True)
    conn = api.get_conn(paths.knowledge_db("geo"))
    try:
        after = api.coverage(conn)
    finally:
        conn.close()
    assert (before["l0"], before["l1"], before["l2"], before["l3"]) == \
           (after["l0"], after["l1"], after["l2"], after["l3"])
