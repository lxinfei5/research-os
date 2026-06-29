"""Boundary gates (see anti_corruption.md). Each gate returns (name, ok, problems[]). Pure checks —
no writes. run_all() aggregates; `ros lint` prints + exits nonzero on any failure."""
from __future__ import annotations

import re
from pathlib import Path

from .. import paths, topics
from ..search import capabilities
from ..storage import intake, knowledge as K

Gate = tuple[str, bool, list[str]]


def _result(name: str, problems: list[str]) -> Gate:
    return (name, not problems, problems)


# ---------------------------------------------------------------------------
def lint_schema_drift() -> Gate:
    cur = K.current_schema_version()
    problems = []
    for t in topics.list_topics():
        slug = t["slug"]
        db = paths.knowledge_db(slug)
        if not db.is_file():
            problems.append(f"{slug}: missing knowledge.db")
            continue
        conn = K.get_conn(db)
        try:
            v = K.db_user_version(conn)
        finally:
            conn.close()
        if v != cur:
            problems.append(f"{slug}: schema v{v} != current v{cur} (run a migration)")
    return _result("schema_drift", problems)


# ---------------------------------------------------------------------------
def lint_collector_policy() -> Gate:
    problems = []
    for t in topics.list_topics():
        slug = t["slug"]
        sdb = paths.sources_db(slug)
        if not sdb.is_file():
            continue
        conn = intake.get_conn(sdb)
        try:
            sessions = {r["id"]: dict(r) for r in conn.execute(
                "SELECT id, source, collector, capture_kind FROM source_session").fetchall()}
            items = conn.execute(
                "SELECT session_id, platform FROM source_item").fetchall()
        finally:
            conn.close()
        for sid, s in sessions.items():
            try:
                capabilities.validate_collector(s["source"], s["collector"],
                                                capture_kind=s["capture_kind"])
            except capabilities.CollectorPolicyError as e:
                problems.append(f"{slug}/{sid}: {e}")
        by_session = {sid: s for sid, s in sessions.items()}
        for it in items:
            s = by_session.get(it["session_id"])
            if not s or not it["platform"]:
                continue
            try:
                capabilities.validate_collector(it["platform"], s["collector"],
                                                capture_kind=s["capture_kind"])
            except capabilities.CollectorPolicyError as e:
                problems.append(f"{slug}/{it['session_id']} item platform={it['platform']}: {e}")
    return _result("collector_policy", problems)


# ---------------------------------------------------------------------------
_L_TABLES = ("l3_claim", "l2_finding", "l1_viewpoint", "l0_worldview")


def lint_snapshot_provenance() -> Gate:
    problems = []
    for t in topics.list_topics():
        slug = t["slug"]
        db = paths.knowledge_db(slug)
        if not db.is_file():
            continue
        conn = K.get_conn(db)
        try:
            for tbl in _L_TABLES:
                bad = conn.execute(
                    f"SELECT count(*) FROM {tbl} WHERE context_snapshot_id IS NOT NULL "
                    f"AND trim(context_snapshot_id) <> '' AND context_snapshot_id NOT IN "
                    f"(SELECT snapshot_id FROM context_snapshot_log)").fetchone()[0]
                if bad:
                    problems.append(f"{slug}/{tbl}: {bad} row(s) cite a missing context_snapshot")
        finally:
            conn.close()
    return _result("snapshot_provenance", problems)


# ---------------------------------------------------------------------------
_STORAGE_FORBIDDEN = re.compile(r"^\s*(from\s+\.\.|import\s+ros\.)(run|assembly|cli)\b", re.M)
_STORAGE_FORBIDDEN2 = re.compile(r"^\s*from\s+\.\.(run|assembly)\s+import", re.M)
_CLI_STORAGE = re.compile(r"^\s*(from\s+\.storage\s+import|from\s+ros\.storage\s+import|import\s+ros\.storage)", re.M)


def lint_import_acl() -> Gate:
    problems = []
    pkg = paths.PKG_DIR
    cli = (pkg / "cli.py").read_text(encoding="utf-8")
    if _CLI_STORAGE.search(cli):
        problems.append("ros/cli.py imports ros.storage.* directly (use ros.api)")
    for fp in (pkg / "storage").glob("*.py"):
        src = fp.read_text(encoding="utf-8")
        if _STORAGE_FORBIDDEN.search(src) or _STORAGE_FORBIDDEN2.search(src):
            problems.append(f"ros/storage/{fp.name} imports upward (run/assembly/cli)")
    return _result("import_acl", problems)


# ---------------------------------------------------------------------------
def lint_db_git_safety() -> Gate:
    problems = []
    gi = paths.root() / ".gitignore"
    if not gi.is_file():
        return _result("db_git_safety", ["no .gitignore at repo root"])
    text = gi.read_text(encoding="utf-8")
    for pat in ("topics/*/knowledge.db", "topics/*/sources.db"):
        if pat not in text:
            problems.append(f".gitignore missing live-DB pattern: {pat}")
    return _result("db_git_safety", problems)


# ---------------------------------------------------------------------------
def lint_l0_version_integrity() -> Gate:
    """The L0 version chain invariant: exactly ONE active world model per topic, and any non-empty
    supersedes_id on an active row must point at a row that actually exists (a real predecessor,
    not a self-reference or a dangling pointer)."""
    problems = []
    for t in topics.list_topics():
        slug = t["slug"]
        db = paths.knowledge_db(slug)
        if not db.is_file():
            continue
        conn = K.get_conn(db)
        try:
            active = conn.execute(
                "SELECT id, supersedes_id FROM l0_worldview WHERE status='active'").fetchall()
            if len(active) > 1:
                problems.append(f"{slug}: {len(active)} active L0 rows (expected exactly 1)")
            for r in active:
                sup = r["supersedes_id"]
                if not sup:
                    continue
                if sup == r["id"]:
                    problems.append(f"{slug}: active L0 {r['id']} supersedes itself")
                elif conn.execute(
                        "SELECT 1 FROM l0_worldview WHERE id=?", (sup,)).fetchone() is None:
                    problems.append(f"{slug}: active L0 {r['id']} supersedes missing id {sup}")
        finally:
            conn.close()
    return _result("l0_version_integrity", problems)


# ---------------------------------------------------------------------------
ALL_GATES = (lint_schema_drift, lint_collector_policy, lint_snapshot_provenance,
             lint_import_acl, lint_db_git_safety, lint_l0_version_integrity)


def run_all() -> list[Gate]:
    return [g() for g in ALL_GATES]
