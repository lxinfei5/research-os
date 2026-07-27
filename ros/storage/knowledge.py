"""Per-topic knowledge.db storage layer (canonical L0–L3).

Ported from AStockOS data/storage/sqlite.py. Iron rules honored here:
  * Python NEVER reasons / calls an LLM — it only orchestrates, counts, validates, persists.
  * Whole-blob read-modify-write upserts + an append-only audit (knowledge_change_log).
  * Real FKs, controlled vocab, the URL gate (trigger), provenance freeze.
  * Forward-only schema evolution: schema_knowledge.sql is the FROZEN v0 baseline; every change is a
    numbered migration in storage/migrations/ tracked by PRAGMA user_version.

There is ONE knowledge.db PER TOPIC — callers pass the topic's db path to get_conn/init_db.
"""
from __future__ import annotations

import json
import hashlib
import re
import sqlite3
import uuid
from pathlib import Path
from typing import Any

from .. import paths

LARGE_JSON_CAP_BYTES = 256 * 1024


# ---------------------------------------------------------------------------
# CONNECTION
# ---------------------------------------------------------------------------
def get_conn(path: str | Path) -> sqlite3.Connection:
    """Open a connection with FK enforcement ON and a busy timeout.

    Rollback-journal mode (no WAL): each db is a small per-topic file and WAL would add sidecar
    -wal/-shm files. 30s busy_timeout lets an overlapping writer wait out a commit window.
    """
    conn = sqlite3.connect(str(path), timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 30000")
    return conn


def init_db(path: str | Path, *, reset: bool = False) -> sqlite3.Connection:
    """Create schema + seed controlled vocab + apply pending migrations + assert triggers.

    schema_knowledge.sql is the frozen v0 baseline; evolution lives as forward-only migrations
    tracked by PRAGMA user_version. Idempotent; reset=True drops the file first.
    """
    path = Path(path)
    if reset and path.exists():
        path.unlink()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = get_conn(path)
    conn.executescript(paths.SCHEMA_KNOWLEDGE_PATH.read_text(encoding="utf-8"))
    conn.executescript(paths.VOCAB_SEED_PATH.read_text(encoding="utf-8"))
    apply_migrations(conn)          # also reapply_triggers() at the end
    conn.commit()
    return conn


def restore_from_snapshot(slug: str, snapshot_path: Path | None = None) -> Path:
    """Rebuild the live knowledge.db from a committed snapshot SQL dump.

    The live .db is gitignored (disposable working copy); the snapshot is the durable artifact.
    Used in worktree/fresh-clone mode where the .db is absent — and by `ros topic restore` to
    discard a corrupted/clobbered live DB and return to the last committed state. Overwrites
    any existing live .db.
    """
    if snapshot_path is None:
        snapshot_path = paths.latest_snapshot_path(slug)
    if snapshot_path is None or not snapshot_path.is_file():
        raise FileNotFoundError(
            f"no snapshot found for '{slug}' under {paths.snapshots_dir(slug)}")
    db_path = paths.knowledge_db(slug)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    conn = sqlite3.connect(str(db_path))
    try:
        conn.executescript(snapshot_path.read_text(encoding="utf-8"))
        # iterdump() doesn't preserve PRAGMA user_version — re-derive via idempotent migrations
        # (CREATE ... IF NOT EXISTS), which also re-asserts the write-gate triggers.
        apply_migrations(conn)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.commit()
    finally:
        conn.close()
    return db_path


def ensure_knowledge_db(slug: str) -> None:
    """Ensure the topic's knowledge.db exists with a usable schema. No-op when the live .db is
    present; when missing (worktree / fresh clone), restore from the latest committed snapshot,
    or init a fresh schema if no snapshot exists yet.

    Called from topics.require_slug() so every CLI command auto-materializes the DB on first
    access — git worktrees get a working DB without manual setup.
    """
    db_path = paths.knowledge_db(slug)
    if db_path.is_file():
        return
    snap = paths.latest_snapshot_path(slug)
    if snap is not None:
        restore_from_snapshot(slug, snap)
    else:
        init_db(db_path)


# ---------------------------------------------------------------------------
# SCHEMA MIGRATION — forward-only, PRAGMA user_version gated
# ---------------------------------------------------------------------------
_MIGRATION_SEQ_RE = re.compile(r"^(\d+)")
_PRAGMA_FK_RE = re.compile(r"^\s*PRAGMA\s+foreign_keys\b", re.IGNORECASE)
_TXN_CTL_RE = re.compile(r"^\s*(BEGIN|COMMIT|END)\s*;?\s*$", re.IGNORECASE)


class MigrationError(RuntimeError):
    """A migration failed to apply atomically (rolled back; user_version unchanged)."""


def _discover_migrations() -> list[tuple[int, Path]]:
    """Return [(seq, path)] for storage/migrations/NNNN_*.sql, sorted by seq."""
    if not paths.MIGRATIONS_DIR.is_dir():
        return []
    out: list[tuple[int, Path]] = []
    for p in sorted(paths.MIGRATIONS_DIR.glob("*.sql")):
        m = _MIGRATION_SEQ_RE.match(p.stem)
        if m:
            out.append((int(m.group(1)), p))
    out.sort(key=lambda t: t[0])
    return out


def current_schema_version() -> int:
    """Highest available migration seq (0 when none exist)."""
    migs = _discover_migrations()
    return migs[-1][0] if migs else 0


def db_user_version(conn: sqlite3.Connection) -> int:
    return int(conn.execute("PRAGMA user_version").fetchone()[0])


def _split_statements(sql: str) -> list[str]:
    """Split a migration into complete SQL statements, trigger-aware (sqlite3.complete_statement)."""
    out: list[str] = []
    buf = ""
    for line in sql.splitlines(keepends=True):
        buf += line
        if sqlite3.complete_statement(buf):
            s = buf.strip()
            if s:
                out.append(s)
            buf = ""
    if buf.strip():
        out.append(buf.strip())
    return out


def _is_comment_or_empty(stmt: str) -> bool:
    for line in stmt.splitlines():
        s = line.strip()
        if s and not s.startswith("--"):
            return False
    return True


# Known write-gate triggers. Dropped before re-assert so triggers.sql body updates take effect
# (CREATE TRIGGER IF NOT EXISTS alone is a no-op when an older definition already exists).
_WRITE_GATE_TRIGGERS = (
    "trg_source_ref_url_gate",
    "trg_l3_snapshot_provenance",
    "trg_l2_snapshot_provenance",
    "trg_l1_snapshot_provenance",
    "trg_l0_snapshot_provenance",
)


def reapply_triggers(conn: sqlite3.Connection) -> None:
    """Re-assert every write-gate trigger from triggers.sql (idempotent). Self-heals a rebuild
    and applies trigger-body changes from triggers.sql (drop-then-create)."""
    if not paths.TRIGGERS_PATH.is_file():
        return
    for name in _WRITE_GATE_TRIGGERS:
        conn.execute(f"DROP TRIGGER IF EXISTS {name}")
    conn.executescript(paths.TRIGGERS_PATH.read_text(encoding="utf-8"))
    conn.commit()


def _apply_one_migration(conn: sqlite3.Connection, seq: int, text: str) -> None:
    """Apply ONE migration body + its user_version bump ATOMICALLY (sqlite.org rebuild recipe)."""
    conn.execute("PRAGMA foreign_keys = OFF")   # MUST be outside a txn (no-op inside one)
    conn.execute("BEGIN")
    try:
        for stmt in _split_statements(text):
            if _is_comment_or_empty(stmt) or _PRAGMA_FK_RE.match(stmt) or _TXN_CTL_RE.match(stmt):
                continue
            conn.execute(stmt)
        conn.execute(f"PRAGMA user_version = {seq}")
        violations = conn.execute("PRAGMA foreign_key_check").fetchall()
        if violations:
            conn.execute("ROLLBACK")
            raise MigrationError(
                f"migration {seq}: foreign_key_check failed ({len(violations)} row(s)); rolled back")
        conn.execute("COMMIT")
    except BaseException:
        try:
            conn.execute("ROLLBACK")
        except sqlite3.OperationalError:
            pass
        raise
    finally:
        conn.execute("PRAGMA foreign_keys = ON")


def apply_migrations(conn: sqlite3.Connection) -> list[str]:
    """Apply every migration with seq > user_version, in order, each ATOMICALLY. Then reassert triggers."""
    applied: list[str] = []
    prev_isolation = conn.isolation_level
    conn.isolation_level = None   # autocommit: the engine owns BEGIN/COMMIT + the outside-txn PRAGMA
    try:
        for seq, path in _discover_migrations():
            if seq <= db_user_version(conn):
                continue
            _apply_one_migration(conn, seq, path.read_text(encoding="utf-8"))
            applied.append(path.name)
    finally:
        conn.isolation_level = prev_isolation
    reapply_triggers(conn)
    return applied


# ---------------------------------------------------------------------------
# SMALL HELPERS
# ---------------------------------------------------------------------------
def gen_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def stable_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def content_sha256(content: Any) -> str:
    return hashlib.sha256(str(content if content is not None else "").encode("utf-8")).hexdigest()


def _nonempty_json_list(name: str, value: list | None) -> str:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{name} must be a non-empty list")
    return json.dumps(value, ensure_ascii=False)


def _trace_json(name: str, value: Any) -> str:
    if isinstance(value, (dict, list)):
        if not value:
            raise ValueError(f"{name} must be non-empty")
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, str) and value.strip() not in ("", "{}", "[]", "null"):
        return value
    raise ValueError(f"{name} must be a non-empty JSON object/array or string")


def _maybe_json(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False) if value else None
    if isinstance(value, str):
        return value if value.strip() not in ("", "{}", "[]", "null") else None
    return None


def _rows(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> list[dict]:
    return [dict(r) for r in conn.execute(sql, params).fetchall()]


# ---------------------------------------------------------------------------
# AUDIT
# ---------------------------------------------------------------------------
def _audit_change(conn: sqlite3.Connection, *, table_name: str, row_id: str, column_name: str,
                  change_kind: str, old_blob: str | None = None, new_blob: str | None = None,
                  diff_summary: str | None = None, changed_by: str,
                  audit_note: str | None = None) -> None:
    """Append a row to knowledge_change_log (whole-blob read-modify-write audit)."""
    conn.execute(
        "INSERT INTO knowledge_change_log "
        "(table_name,row_id,column_name,change_kind,old_blob,new_blob,diff_summary,changed_by,audit_note) "
        "VALUES (?,?,?,?,?,?,?,?,?)",
        (table_name, str(row_id), column_name, change_kind, old_blob, new_blob,
         diff_summary, changed_by, audit_note),
    )


def record_audit_change(conn: sqlite3.Connection, **kw: Any) -> None:
    """Public audit append helper for downstream deterministic tools."""
    _audit_change(conn, **kw)


def _warn_large_json(conn: sqlite3.Connection, *, table: str, row_id: str, column: str,
                     blob: str | None, changed_by: str) -> None:
    if not blob:
        return
    n = len(blob.encode("utf-8"))
    if n > LARGE_JSON_CAP_BYTES:
        _audit_change(conn, table_name=table, row_id=row_id, column_name=column,
                      change_kind="json_warn", changed_by=changed_by,
                      diff_summary=f"{n}B > {LARGE_JSON_CAP_BYTES}B cap",
                      audit_note="over-cap JSON written as-is (warn-only)")


# ---------------------------------------------------------------------------
# CREDIBILITY
# ---------------------------------------------------------------------------
_CRED_LEVELS = ("low", "medium", "high")
_CRED_SUBJECTS = ("l3_claim", "l2_finding", "l1_viewpoint", "l0_worldview")


def record_credibility(conn: sqlite3.Connection, *, subject_type: str, subject_id: str,
                       level: str, rationale: str, filter_trace: Any,
                       independence_note: str | None = None, echo_chamber_flag: int = 0,
                       calibration_basis: dict | None = None, run_id: str | None = None,
                       cid: str | None = None) -> str:
    """Record an agent-judged 5-axis credibility verdict. rationale + filter_trace required.

    echo_chamber_flag is stored as a signal for the agent/reader; Python does NOT mechanically
    cap level (AStockOSV2: capability back to the model). When the flag is set and level is not
    already low, a non-destructive note is prepended to rationale so the flag is visible in prose.
    """
    if subject_type not in _CRED_SUBJECTS:
        raise ValueError(f"subject_type must be one of {_CRED_SUBJECTS}")
    if level not in _CRED_LEVELS:
        raise ValueError("level must be low/medium/high")
    if not rationale or not rationale.strip():
        raise ValueError("credibility rationale is required (never silent)")
    filt = _trace_json("filter_trace", filter_trace)
    if echo_chamber_flag and level != "low" and "[echo_chamber_flag]" not in rationale:
        # Advisory only — agent chose the level; we surface the flag without rewriting it.
        rationale = f"[echo_chamber_flag] {rationale}"
    cid = cid or gen_id("cred")
    conn.execute(
        "INSERT INTO credibility_assessment "
        "(id,subject_type,subject_id,level,rationale,filter_trace,independence_note,"
        "echo_chamber_flag,calibration_basis,run_id) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (cid, subject_type, subject_id, level, rationale, filt, independence_note,
         1 if echo_chamber_flag else 0,
         json.dumps(calibration_basis, ensure_ascii=False) if calibration_basis else None, run_id),
    )
    return cid


def _require_credibility(conn: sqlite3.Connection, cred_id: str, subject_type: str,
                         subject_id: str) -> str:
    """Validate a credibility row exists and is bound to THIS subject (guards id mix-ups)."""
    row = conn.execute(
        "SELECT subject_type, subject_id FROM credibility_assessment WHERE id=?", (cred_id,)
    ).fetchone()
    if row is None:
        raise ValueError(f"credibility_id {cred_id!r} does not exist (write the credibility row first)")
    if row["subject_type"] != subject_type or str(row["subject_id"]) != str(subject_id):
        raise ValueError(
            f"credibility_id {cred_id!r} is bound to {row['subject_type']}:{row['subject_id']}, "
            f"not {subject_type}:{subject_id}")
    return cred_id


# ---------------------------------------------------------------------------
# PROVENANCE — source_ref (URL gate enforced by trigger) + context freeze
# ---------------------------------------------------------------------------
def add_source_ref(conn: sqlite3.Connection, *, platform: str, source_kind: str, url: str,
                   subject_type: str | None = None, subject_id: str | None = None,
                   author: str | None = None, title: str | None = None,
                   content_hash: str | None = None, cached_text_path: str | None = None,
                   media_transcript_path: str | None = None, intake_item_id: str | None = None,
                   captured_at: str | None = None, captured_by: str | None = None,
                   src_id: str | None = None) -> str:
    """Insert a retained source. The URL gate trigger ABORTs empty/'dataset' urls and off-vocab
    platform/source_kind. Returns the source_ref id."""
    src_id = src_id or gen_id("src")
    conn.execute(
        "INSERT INTO source_ref "
        "(id,subject_type,subject_id,platform,source_kind,url,author,title,content_hash,"
        "cached_text_path,media_transcript_path,intake_item_id,captured_at,captured_by) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (src_id, subject_type, subject_id, platform, source_kind, url, author, title,
         content_hash, cached_text_path, media_transcript_path, intake_item_id,
         captured_at, captured_by),
    )
    return src_id


def record_context_snapshot(conn: sqlite3.Connection, *, payload: dict,
                            freeze_policy: str = "context_freeze_policy.v1",
                            snapshot_id: str | None = None) -> str:
    """Freeze a primed-context payload so a knowledge write can bind to exactly what it saw."""
    snapshot_id = snapshot_id or gen_id("ctx")
    blob = stable_json(payload)
    conn.execute(
        "INSERT INTO context_snapshot_log (snapshot_id,payload,content_hash,freeze_policy) "
        "VALUES (?,?,?,?)",
        (snapshot_id, blob, content_sha256(blob), freeze_policy),
    )
    return snapshot_id


# ---------------------------------------------------------------------------
# CORROBORATION (L2) — Python only COUNTS; the agent judges whether it implies trust.
# ---------------------------------------------------------------------------
def _corroborate(source_ref_ids: list, corroboration_count: int | None,
                 cross_platform_count: int | None,
                 corroboration_sources: Any) -> tuple[int, int, str | None]:
    n = len(source_ref_ids) if isinstance(source_ref_ids, list) else 0
    cc = corroboration_count if corroboration_count is not None else max(1, n)
    cpc = cross_platform_count if cross_platform_count is not None else 1
    if cc < 1:
        raise ValueError("corroboration_count must be >= 1")
    if cpc < 1:
        raise ValueError("cross_platform_count must be >= 1")
    src_json = None
    if corroboration_sources is not None:
        if isinstance(corroboration_sources, (list, dict)):
            if corroboration_sources:
                src_json = json.dumps(corroboration_sources, ensure_ascii=False)
        elif isinstance(corroboration_sources, str) and \
                corroboration_sources.strip() not in ("", "[]", "{}", "null"):
            src_json = corroboration_sources
    return cc, cpc, src_json


# ---------------------------------------------------------------------------
# UPSERTS — whole-blob read-modify-write + audit (the AStockOS pattern).
# ---------------------------------------------------------------------------
_L3_KINDS = ("fact", "analysis", "rumor", "breaking", "opinion", "data", "other")


def upsert_l3_claim(conn: sqlite3.Connection, *, id: str, proposition: str, claim_kind: str,
                    single_source_ref_id: str, source_ref_ids: list, credibility_id: str,
                    filter_trace: Any, facet: str | None = None, source_kind: str | None = None,
                    verbatim_excerpt: str | None = None, cached_text_hash: str | None = None,
                    analysis_note: str | None = None, debate_trace: Any = None,
                    parent_l2_id: str | None = None, lifecycle: str | None = None,
                    run_id: str | None = None, context_snapshot_id: str | None = None,
                    context_hash: str | None = None, updated_by: str = "analysis",
                    audit_note: str | None = None) -> str:
    """L3 = a single-source claim distilled from one original item."""
    if claim_kind not in _L3_KINDS:
        raise ValueError(f"claim_kind must be one of {_L3_KINDS}")
    if not proposition or not proposition.strip():
        raise ValueError("proposition required")
    if not single_source_ref_id or not str(single_source_ref_id).strip():
        raise ValueError("single_source_ref_id required (L3 carries exactly one source)")
    sri = _nonempty_json_list("source_ref_ids", source_ref_ids)
    sri_list = json.loads(sri)
    if str(single_source_ref_id) not in [str(x) for x in sri_list]:
        sri_list = [single_source_ref_id] + sri_list
        sri = json.dumps(sri_list, ensure_ascii=False)
    cred = _require_credibility(conn, credibility_id, "l3_claim", id)
    filt = _trace_json("filter_trace", filter_trace)
    debate = _maybe_json(debate_trace)
    _warn_large_json(conn, table="l3_claim", row_id=id, column="filter_trace", blob=filt, changed_by=updated_by)
    existing = conn.execute("SELECT * FROM l3_claim WHERE id=?", (id,)).fetchone()
    cols = (facet, proposition, claim_kind, source_kind, single_source_ref_id, sri,
            verbatim_excerpt, cached_text_hash, analysis_note, filt, debate, cred,
            parent_l2_id, lifecycle, run_id, context_snapshot_id, context_hash)
    if existing is None:
        conn.execute(
            "INSERT INTO l3_claim (id,facet,proposition,claim_kind,source_kind,single_source_ref_id,"
            "source_ref_ids,verbatim_excerpt,cached_text_hash,analysis_note,filter_trace,debate_trace,"
            "credibility_id,parent_l2_id,lifecycle,run_id,context_snapshot_id,context_hash,updated_by,"
            "audit_note) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (id, *cols, updated_by, audit_note),
        )
        _audit_change(conn, table_name="l3_claim", row_id=id, column_name="*", change_kind="insert",
                      changed_by=updated_by, diff_summary=f"kind={claim_kind} facet={facet}",
                      audit_note=audit_note)
        return id
    old_blob = json.dumps(dict(existing), ensure_ascii=False, default=str)
    conn.execute(
        "UPDATE l3_claim SET facet=?,proposition=?,claim_kind=?,source_kind=?,single_source_ref_id=?,"
        "source_ref_ids=?,verbatim_excerpt=?,cached_text_hash=?,analysis_note=?,filter_trace=?,"
        "debate_trace=?,credibility_id=?,parent_l2_id=?,lifecycle=?,run_id=?,context_snapshot_id=?,"
        "context_hash=?,updated_at=datetime('now'),updated_by=?,audit_note=? WHERE id=?",
        (*cols, updated_by, audit_note, id),
    )
    new_row = conn.execute("SELECT * FROM l3_claim WHERE id=?", (id,)).fetchone()
    _audit_change(conn, table_name="l3_claim", row_id=id, column_name="*", change_kind="update",
                  changed_by=updated_by, old_blob=old_blob,
                  new_blob=json.dumps(dict(new_row), ensure_ascii=False, default=str),
                  diff_summary=f"kind={claim_kind} facet={facet}", audit_note=audit_note)
    return id


_L2_TYPES = ("fact", "event", "figure", "claim", "trend", "other")


def upsert_l2_finding(conn: sqlite3.Connection, *, id: str, finding_type: str, statement: str,
                      source_ref_ids: list, credibility_id: str, facet: str | None = None,
                      value_text: str | None = None, value_num: float | None = None,
                      unit: str | None = None, valid_from: str | None = None,
                      valid_to: str | None = None, corroboration_count: int | None = None,
                      cross_platform_count: int | None = None, corroboration_sources: Any = None,
                      conflict_note: str | None = None, l3_ids: list | None = None,
                      parent_l1_id: str | None = None, run_id: str | None = None,
                      context_snapshot_id: str | None = None, context_hash: str | None = None,
                      updated_by: str = "analysis", audit_note: str | None = None) -> str:
    """L2 = a multi-source corroborated finding. corroboration is COUNTED here, judged by the agent."""
    if finding_type not in _L2_TYPES:
        raise ValueError(f"finding_type must be one of {_L2_TYPES}")
    if not statement or not statement.strip():
        raise ValueError("statement required")
    sri = _nonempty_json_list("source_ref_ids", source_ref_ids)
    cc, cpc, src_json = _corroborate(source_ref_ids, corroboration_count, cross_platform_count,
                                     corroboration_sources)
    cred = _require_credibility(conn, credibility_id, "l2_finding", id)
    l3 = json.dumps(l3_ids, ensure_ascii=False) if l3_ids else None
    existing = conn.execute("SELECT * FROM l2_finding WHERE id=?", (id,)).fetchone()
    cols = (facet, finding_type, statement, value_text, value_num, unit, valid_from, valid_to,
            cc, cpc, src_json, conflict_note, sri, cred, l3, parent_l1_id, run_id,
            context_snapshot_id, context_hash)
    if existing is None:
        conn.execute(
            "INSERT INTO l2_finding (id,facet,finding_type,statement,value_text,value_num,unit,"
            "valid_from,valid_to,corroboration_count,cross_platform_count,corroboration_sources,"
            "conflict_note,source_ref_ids,credibility_id,l3_ids,parent_l1_id,run_id,"
            "context_snapshot_id,context_hash,updated_by,audit_note) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (id, *cols, updated_by, audit_note),
        )
        _audit_change(conn, table_name="l2_finding", row_id=id, column_name="*", change_kind="insert",
                      changed_by=updated_by,
                      diff_summary=f"type={finding_type} corrob={cc}/{cpc}", audit_note=audit_note)
        return id
    old_blob = json.dumps(dict(existing), ensure_ascii=False, default=str)
    conn.execute(
        "UPDATE l2_finding SET facet=?,finding_type=?,statement=?,value_text=?,value_num=?,unit=?,"
        "valid_from=?,valid_to=?,corroboration_count=?,cross_platform_count=?,corroboration_sources=?,"
        "conflict_note=?,source_ref_ids=?,credibility_id=?,l3_ids=?,parent_l1_id=?,run_id=?,"
        "context_snapshot_id=?,context_hash=?,updated_at=datetime('now'),updated_by=?,audit_note=? "
        "WHERE id=?",
        (*cols, updated_by, audit_note, id),
    )
    new_row = conn.execute("SELECT * FROM l2_finding WHERE id=?", (id,)).fetchone()
    _audit_change(conn, table_name="l2_finding", row_id=id, column_name="*", change_kind="update",
                  changed_by=updated_by, old_blob=old_blob,
                  new_blob=json.dumps(dict(new_row), ensure_ascii=False, default=str),
                  diff_summary=f"type={finding_type} corrob={cc}/{cpc}", audit_note=audit_note)
    return id


_L1_KINDS = ("theme", "sub_question", "viewpoint", "contrarian")


def upsert_l1_viewpoint(conn: sqlite3.Connection, *, id: str, synthesis_kind: str, narrative: str,
                        source_ref_ids: list, credibility_id: str, facet: str | None = None,
                        sub_question: str | None = None, viewpoint_scope: Any = None,
                        stance: str | None = None, l2_ids: list | None = None,
                        open_questions: list | None = None, confidence: str | None = None,
                        parent_l0_id: str | None = None, rank: int | None = None,
                        run_id: str | None = None, context_snapshot_id: str | None = None,
                        context_hash: str | None = None, updated_by: str = "analysis",
                        audit_note: str | None = None) -> str:
    """L1 = a synthesized viewpoint per facet / sub-question / angle."""
    if synthesis_kind not in _L1_KINDS:
        raise ValueError(f"synthesis_kind must be one of {_L1_KINDS}")
    if not narrative or not narrative.strip():
        raise ValueError("narrative required")
    sri = _nonempty_json_list("source_ref_ids", source_ref_ids)
    cred = _require_credibility(conn, credibility_id, "l1_viewpoint", id)
    scope = _maybe_json(viewpoint_scope)
    l2 = json.dumps(l2_ids, ensure_ascii=False) if l2_ids else None
    oq = json.dumps(open_questions, ensure_ascii=False) if open_questions else None
    existing = conn.execute("SELECT * FROM l1_viewpoint WHERE id=?", (id,)).fetchone()
    cols = (facet, sub_question, scope, synthesis_kind, narrative, stance, l2, oq, confidence,
            sri, cred, parent_l0_id, rank, run_id, context_snapshot_id, context_hash)
    if existing is None:
        conn.execute(
            "INSERT INTO l1_viewpoint (id,facet,sub_question,viewpoint_scope,synthesis_kind,narrative,"
            "stance,l2_ids,open_questions,confidence,source_ref_ids,credibility_id,parent_l0_id,rank,"
            "run_id,context_snapshot_id,context_hash,updated_by,audit_note) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (id, *cols, updated_by, audit_note),
        )
        _audit_change(conn, table_name="l1_viewpoint", row_id=id, column_name="*", change_kind="insert",
                      changed_by=updated_by, diff_summary=f"kind={synthesis_kind} stance={stance}",
                      audit_note=audit_note)
        return id
    old_blob = json.dumps(dict(existing), ensure_ascii=False, default=str)
    conn.execute(
        "UPDATE l1_viewpoint SET facet=?,sub_question=?,viewpoint_scope=?,synthesis_kind=?,narrative=?,"
        "stance=?,l2_ids=?,open_questions=?,confidence=?,source_ref_ids=?,credibility_id=?,"
        "parent_l0_id=?,rank=?,run_id=?,context_snapshot_id=?,context_hash=?,"
        "updated_at=datetime('now'),updated_by=?,audit_note=? WHERE id=?",
        (*cols, updated_by, audit_note, id),
    )
    new_row = conn.execute("SELECT * FROM l1_viewpoint WHERE id=?", (id,)).fetchone()
    _audit_change(conn, table_name="l1_viewpoint", row_id=id, column_name="*", change_kind="update",
                  changed_by=updated_by, old_blob=old_blob,
                  new_blob=json.dumps(dict(new_row), ensure_ascii=False, default=str),
                  diff_summary=f"kind={synthesis_kind} stance={stance}", audit_note=audit_note)
    return id


_L0_KINDS = ("state_of_understanding", "consensus", "tension", "frontier", "other")


def upsert_l0_worldview(conn: sqlite3.Connection, *, id: str, summary_kind: str, proposition: str,
                        source_ref_ids: list, credibility_id: str, scope: Any = None,
                        key_findings: list | None = None, open_questions: list | None = None,
                        confidence: str | None = None, supersedes_id: str | None = None,
                        l1_ids: list | None = None, run_id: str | None = None,
                        context_snapshot_id: str | None = None, context_hash: str | None = None,
                        updated_by: str = "analysis", audit_note: str | None = None) -> str:
    """L0 = the topic world model + open questions (NEVER pruned). supersedes_id chains old → new."""
    if summary_kind not in _L0_KINDS:
        raise ValueError(f"summary_kind must be one of {_L0_KINDS}")
    if not proposition or not proposition.strip():
        raise ValueError("proposition required")
    sri = _nonempty_json_list("source_ref_ids", source_ref_ids)
    cred = _require_credibility(conn, credibility_id, "l0_worldview", id)
    sc = _maybe_json(scope)
    kf = json.dumps(key_findings, ensure_ascii=False) if key_findings else None
    oq = json.dumps(open_questions, ensure_ascii=False) if open_questions else None
    l1 = json.dumps(l1_ids, ensure_ascii=False) if l1_ids else None
    existing = conn.execute("SELECT * FROM l0_worldview WHERE id=?", (id,)).fetchone()
    cols = (summary_kind, proposition, sc, kf, oq, confidence, supersedes_id, l1, sri, cred,
            run_id, context_snapshot_id, context_hash)
    if existing is None:
        conn.execute(
            "INSERT INTO l0_worldview (id,summary_kind,proposition,scope,key_findings,open_questions,"
            "confidence,supersedes_id,l1_ids,source_ref_ids,credibility_id,run_id,context_snapshot_id,"
            "context_hash,updated_by,audit_note) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (id, *cols, updated_by, audit_note),
        )
        _audit_change(conn, table_name="l0_worldview", row_id=id, column_name="*", change_kind="insert",
                      changed_by=updated_by, diff_summary=f"kind={summary_kind}", audit_note=audit_note)
        return id
    old_blob = json.dumps(dict(existing), ensure_ascii=False, default=str)
    conn.execute(
        "UPDATE l0_worldview SET summary_kind=?,proposition=?,scope=?,key_findings=?,open_questions=?,"
        "confidence=?,supersedes_id=?,l1_ids=?,source_ref_ids=?,credibility_id=?,run_id=?,"
        "context_snapshot_id=?,context_hash=?,updated_at=datetime('now'),updated_by=?,audit_note=? "
        "WHERE id=?",
        (*cols, updated_by, audit_note, id),
    )
    new_row = conn.execute("SELECT * FROM l0_worldview WHERE id=?", (id,)).fetchone()
    _audit_change(conn, table_name="l0_worldview", row_id=id, column_name="*", change_kind="update",
                  changed_by=updated_by, old_blob=old_blob,
                  new_blob=json.dumps(dict(new_row), ensure_ascii=False, default=str),
                  diff_summary=f"kind={summary_kind}", audit_note=audit_note)
    return id


# ---------------------------------------------------------------------------
# SEARCH LOG (migration 0001) — durable per-topic record of executed searches.
# ---------------------------------------------------------------------------
def record_search(conn: sqlite3.Connection, *, query: str, source: str | None = None,
                  facet: str | None = None, run_id: str | None = None,
                  result_note: str | None = None) -> str:
    """Log a search so the next brief can avoid re-running it and can age facets. Touches
    facet.last_searched_at when a facet is targeted."""
    sid = gen_id("sl")
    conn.execute(
        "INSERT INTO search_log (id,query,source,facet,run_id,result_note) VALUES (?,?,?,?,?,?)",
        (sid, query, source, facet, run_id, result_note))
    if facet:
        conn.execute("UPDATE facet SET last_searched_at=datetime('now') WHERE id=?", (facet,))
    return sid


def recent_searches(conn: sqlite3.Connection, *, limit: int = 20,
                    facet: str | None = None) -> list[dict]:
    sql = "SELECT query, source, facet, searched_at FROM search_log"
    params: tuple = ()
    if facet:
        sql += " WHERE facet=?"
        params = (facet,)
    sql += " ORDER BY searched_at DESC, id DESC LIMIT ?"
    return _rows(conn, sql, params + (int(limit),))


# ---------------------------------------------------------------------------
# FACETS
# ---------------------------------------------------------------------------
def upsert_facet(conn: sqlite3.Connection, *, id: str, question: str,
                 status: str = "open") -> str:
    existing = conn.execute("SELECT id FROM facet WHERE id=?", (id,)).fetchone()
    if existing is None:
        conn.execute("INSERT INTO facet (id,question,status) VALUES (?,?,?)", (id, question, status))
    else:
        conn.execute("UPDATE facet SET question=?,status=? WHERE id=?", (question, status, id))
    return id


# ---------------------------------------------------------------------------
# READ — coverage / snapshot
# ---------------------------------------------------------------------------
def coverage(conn: sqlite3.Connection) -> dict:
    """Deterministic counts used for topic 'coverage' display + gap analysis."""
    def _n(sql: str, params: tuple = ()) -> int:
        return int(conn.execute(sql, params).fetchone()[0])

    facets = _rows(conn, "SELECT id,question,status,last_searched_at FROM facet ORDER BY created_at")
    return {
        "schema_version": db_user_version(conn),
        "l0": _n("SELECT count(*) FROM l0_worldview WHERE status='active'"),
        "l1": _n("SELECT count(*) FROM l1_viewpoint WHERE status='active'"),
        "l2": _n("SELECT count(*) FROM l2_finding WHERE status='active'"),
        "l3": _n("SELECT count(*) FROM l3_claim WHERE status='active'"),
        "sources": _n("SELECT count(*) FROM source_ref"),
        "facets": facets,
        "open_questions": _n("SELECT count(*) FROM open_question WHERE status='open'"),
    }


def knowledge_snapshot(conn: sqlite3.Connection) -> dict:
    """Read surface for report rendering / context assembly (Phase 1+)."""
    return {
        "l0_worldview": _rows(conn, "SELECT * FROM l0_worldview WHERE status='active'"),
        "l1_viewpoint": _rows(conn, "SELECT * FROM l1_viewpoint WHERE status='active' ORDER BY rank"),
        "l2_finding": _rows(conn, "SELECT * FROM l2_finding WHERE status='active'"),
        "l3_claim": _rows(conn, "SELECT * FROM l3_claim WHERE status='active'"),
        "source_ref": _rows(conn, "SELECT * FROM source_ref"),
        "coverage": coverage(conn),
    }


def l0_history(conn: sqlite3.Connection) -> list[dict]:
    """All L0 versions, newest first, with the supersedes chain. Used by the report's version-history
    section and by `ros review`. Every consumer of the *current* worldview still reads
    knowledge_snapshot()['l0_worldview'] (active only) — this is the explicit history surface."""
    return _rows(conn,
                 "SELECT id, summary_kind, proposition, confidence, supersedes_id, status, "
                 "key_findings, open_questions, created_at, updated_at, updated_by, audit_note "
                 "FROM l0_worldview ORDER BY updated_at DESC")
