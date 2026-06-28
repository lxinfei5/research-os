"""Method lane (M0/M1) — durable "how to research this topic" invariants, the logic-generality axis.

Pure logic: NO source_ref, NO credibility (unlike the evidence lane). Physically isolated from
evidence so a high-density single-source claim can never masquerade as a verified method. M0 =
topic-general method invariant; M1 = stage/facet conditional heuristic (valid_if JSON).

method_rule lives in each topic's knowledge.db (defined in the frozen baseline). An OPTIONAL shared
store (topics/_shared/method.db) lets a rule be reused across topics — but import lands the rule as
status='draft' (the "fresh condense" gate): the borrowing topic's agent must re-validate it before it
counts. We NEVER auto-copy evidence rows across topics; only pure-logic method rules, and only opt-in.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

from .. import paths
from . import knowledge as K

# Standalone DDL for the shared store (mirrors the method_rule shape in schema_knowledge.sql).
SHARED_SCHEMA = """
CREATE TABLE IF NOT EXISTS method_rule (
    id           TEXT PRIMARY KEY,
    level        TEXT NOT NULL CHECK (level IN ('M0','M1')),
    proposition  TEXT NOT NULL,
    valid_if     TEXT,
    wrong_if     TEXT,
    status       TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','retired','draft')),
    origin_topic TEXT,
    created_at   TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at   TEXT NOT NULL DEFAULT (datetime('now')),
    updated_by   TEXT NOT NULL DEFAULT 'analysis'
);
"""

_LEVELS = ("M0", "M1")
_STATUSES = ("active", "retired", "draft")


def init_shared_store() -> sqlite3.Connection:
    paths.shared_dir().mkdir(parents=True, exist_ok=True)
    conn = K.get_conn(paths.shared_method_db())
    conn.executescript(SHARED_SCHEMA)
    conn.commit()
    return conn


def upsert(conn: sqlite3.Connection, *, level: str, proposition: str, id: str | None = None,
           valid_if=None, wrong_if: str | None = None, status: str = "active",
           updated_by: str = "analysis", audit: bool = True) -> str:
    """Upsert a method rule into a conn that has a method_rule table (topic knowledge.db or shared)."""
    if level not in _LEVELS:
        raise ValueError(f"level must be one of {_LEVELS}")
    if status not in _STATUSES:
        raise ValueError(f"status must be one of {_STATUSES}")
    if not proposition or not proposition.strip():
        raise ValueError("proposition required")
    vif = K._maybe_json(valid_if) if valid_if is not None else None
    rid = id or ("mr-" + K.content_sha256(f"{level}|{proposition}")[:12])
    existing = conn.execute("SELECT * FROM method_rule WHERE id=?", (rid,)).fetchone()
    if existing is None:
        conn.execute(
            "INSERT INTO method_rule (id,level,proposition,valid_if,wrong_if,status,updated_by) "
            "VALUES (?,?,?,?,?,?,?)", (rid, level, proposition, vif, wrong_if, status, updated_by))
        if audit and _has_audit(conn):
            K._audit_change(conn, table_name="method_rule", row_id=rid, column_name="*",
                            change_kind="insert", changed_by=updated_by,
                            diff_summary=f"level={level} status={status}")
    else:
        conn.execute(
            "UPDATE method_rule SET level=?,proposition=?,valid_if=?,wrong_if=?,status=?,"
            "updated_at=datetime('now'),updated_by=? WHERE id=?",
            (level, proposition, vif, wrong_if, status, updated_by, rid))
        if audit and _has_audit(conn):
            K._audit_change(conn, table_name="method_rule", row_id=rid, column_name="*",
                            change_kind="update", changed_by=updated_by,
                            diff_summary=f"level={level} status={status}")
    return rid


def list_rules(conn: sqlite3.Connection, *, level: str | None = None,
               status: str | None = None) -> list[dict]:
    sql = "SELECT * FROM method_rule"
    clauses, params = [], []
    if level:
        clauses.append("level=?")
        params.append(level)
    if status:
        clauses.append("status=?")
        params.append(status)
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY level, created_at"
    return [dict(r) for r in conn.execute(sql, tuple(params)).fetchall()]


# ---------------------------------------------------------------------------
# cross-topic export / import (opt-in; import = draft = fresh-condense gate)
# ---------------------------------------------------------------------------
def export_to_shared(topic_slug: str, rule_id: str) -> dict:
    tconn = K.get_conn(paths.knowledge_db(topic_slug))
    try:
        row = tconn.execute("SELECT * FROM method_rule WHERE id=?", (rule_id,)).fetchone()
        if row is None:
            raise KeyError(f"method_rule {rule_id} not in topic '{topic_slug}'")
        r = dict(row)
    finally:
        tconn.close()
    sconn = init_shared_store()
    try:
        sconn.execute(
            "INSERT OR REPLACE INTO method_rule (id,level,proposition,valid_if,wrong_if,status,origin_topic) "
            "VALUES (?,?,?,?,?,?,?)",
            (r["id"], r["level"], r["proposition"], r.get("valid_if"), r.get("wrong_if"),
             "active", topic_slug))
        sconn.commit()
    finally:
        sconn.close()
    return {"rule_id": rule_id, "from": topic_slug, "shared": str(paths.shared_method_db())}


def list_shared() -> list[dict]:
    if not paths.shared_method_db().is_file():
        return []
    conn = K.get_conn(paths.shared_method_db())
    try:
        return list_rules(conn)
    finally:
        conn.close()


def import_from_shared(rule_id: str, topic_slug: str) -> dict:
    """Copy a shared method rule into a topic as a DRAFT (fresh-condense gate). The borrowing topic's
    agent must re-validate (promote draft → active) before it counts — never an auto row-copy."""
    if not paths.shared_method_db().is_file():
        raise FileNotFoundError("no shared method store yet")
    sconn = K.get_conn(paths.shared_method_db())
    try:
        row = sconn.execute("SELECT * FROM method_rule WHERE id=?", (rule_id,)).fetchone()
        if row is None:
            raise KeyError(f"shared method_rule {rule_id} not found")
        r = dict(row)
    finally:
        sconn.close()
    tconn = K.get_conn(paths.knowledge_db(topic_slug))
    try:
        new_id = upsert(tconn, id="mr-imp-" + rule_id.split("-", 1)[-1], level=r["level"],
                        proposition=r["proposition"], valid_if=r.get("valid_if"),
                        wrong_if=r.get("wrong_if"), status="draft", updated_by="method-import")
        tconn.commit()
    finally:
        tconn.close()
    return {"imported_as": new_id, "into": topic_slug, "status": "draft",
            "note": "re-validate (draft→active) before it counts"}


def _has_audit(conn: sqlite3.Connection) -> bool:
    return conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='knowledge_change_log'").fetchone() is not None
