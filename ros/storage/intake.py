"""Per-topic raw-intake sidecar: sources.db (one per topic, sibling of knowledge.db).

Deliberately simpler evolution model than the canonical knowledge.db (per AStockOS sidecar
pattern): an inline SCHEMA + idempotent check-then-ALTER (_migrate_store_schema), stamped with
PRAGMA user_version. The sidecar holds REPLAYABLE raw material an agent gathered; nothing here is
canonical knowledge. Python does not fetch or interpret material — it records what the agent passes
and gates promotion on a real URL *or* a first-party empirical exception.

Flow:  agent searches → `ros capture <payload>` → record_capture() writes source_item rows
       → `ros promote` → promote_item() URL-gates each, writes source_ref + cache + library entry.

First-party empirical (researcher field tests / quota tables): no public URL by nature. Eligible
items (platform manual/first_party + first-party source_kind, or provenance_class flag) promote
with a minted `researchos://first-party/<content_hash>` locator. Incomplete social cards still
require restricted_reason and stay raw-only.
"""
from __future__ import annotations

import json
import sqlite3
import uuid
from pathlib import Path
from typing import Any

from . import knowledge as K
from .. import library, paths
from ..search import capabilities

SCHEMA_VERSION = 1

# Structural allow-list for first-party promote (no public URL). Checked by shape only —
# Python does not judge the content's truth (iron rule).
FIRST_PARTY_PLATFORMS = frozenset({"manual", "first_party", "researcher"})
FIRST_PARTY_SOURCE_KINDS = frozenset({
    "first_party_empirical",
    "first_party_empirical_table",
    "first_party_field_note",
    "empirical_table",   # alias
    "field_note",        # alias
})
FIRST_PARTY_PROVENANCE_CLASS = "first_party_empirical"
FIRST_PARTY_URL_PREFIX = "researchos://first-party/"


def _parse_raw_metadata(raw: Any) -> dict:
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str) and raw.strip():
        try:
            obj = json.loads(raw)
            return obj if isinstance(obj, dict) else {}
        except json.JSONDecodeError:
            return {}
    return {}


def is_first_party_item(item: dict) -> bool:
    """True iff the item is structurally first-party empirical (eligible for no-public-URL promote).

    Criteria (all structural — no semantic judgment):
      * platform ∈ {manual, first_party, researcher}  (defense: cannot relabel XHS as first-party)
      * AND (source_kind ∈ first-party kinds OR raw_metadata.provenance_class == first_party_empirical)
      * AND content is non-empty
    """
    platform = (_norm(item.get("platform")) or "").lower()
    if platform not in FIRST_PARTY_PLATFORMS:
        return False
    content = item.get("content")
    if content is None or (isinstance(content, str) and not content.strip()):
        return False
    sk = (_norm(item.get("source_kind")) or "").lower()
    if sk in FIRST_PARTY_SOURCE_KINDS:
        return True
    meta = _parse_raw_metadata(item.get("raw_metadata"))
    return meta.get("provenance_class") == FIRST_PARTY_PROVENANCE_CLASS


def first_party_provenance_url(content_hash: str) -> str:
    """Deterministic non-HTTP provenance locator for a first-party retained source."""
    ch = (content_hash or "").strip()
    if not ch:
        raise ValueError("first-party provenance URL requires a non-empty content_hash")
    return f"{FIRST_PARTY_URL_PREFIX}{ch}"


def is_public_or_first_party_url(url: str | None) -> bool:
    """Structural check mirroring trg_source_ref_url_gate (http(s) or researchos://first-party/)."""
    u = (url or "").strip().lower()
    if not u or u == "dataset":
        return False
    return u.startswith("http://") or u.startswith("https://") or u.startswith(FIRST_PARTY_URL_PREFIX)

SCHEMA = """
PRAGMA foreign_keys = ON;

-- One collector run (a search/fetch session the agent performed).
CREATE TABLE IF NOT EXISTS source_session (
    id              TEXT PRIMARY KEY,
    query           TEXT NOT NULL,
    source          TEXT NOT NULL,             -- web / x / douyin / xiaohongshu / manual / ...
    collector       TEXT,                      -- which mechanism (web_search / xiaohongshu-mcp / ...)
    capture_kind    TEXT NOT NULL DEFAULT 'search',
    searched_at     TEXT NOT NULL,
    expires_at      TEXT,
    captured_by     TEXT,
    result_count    INTEGER,
    degraded_reason TEXT,
    raw_tool_status TEXT,
    run_id          TEXT,
    notes           TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- One raw item captured in a session.
CREATE TABLE IF NOT EXISTS source_item (
    id                     TEXT PRIMARY KEY,
    session_id             TEXT NOT NULL REFERENCES source_session(id),
    platform               TEXT,
    source_kind            TEXT,
    url                    TEXT,                -- nullable ONLY when restricted_reason explains why
    title                  TEXT,
    content                TEXT NOT NULL,       -- the captured text (media already transcribed)
    author                 TEXT,
    captured_at            TEXT,
    raw_metadata           TEXT,                -- JSON
    content_hash           TEXT NOT NULL,
    needs_review           INTEGER NOT NULL DEFAULT 1,
    restricted_reason      TEXT,
    promoted_source_ref_id TEXT,               -- set once promoted into knowledge.db
    created_at             TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_source_item_hash ON source_item(content_hash);
CREATE INDEX IF NOT EXISTS idx_source_item_promoted ON source_item(promoted_source_ref_id);

-- Cross-session inventory: what we've seen for a (platform, surface, external_id).
CREATE TABLE IF NOT EXISTS source_inventory (
    platform      TEXT NOT NULL,
    surface       TEXT NOT NULL,               -- search / favorites / likes / detail / ...
    external_id   TEXT NOT NULL,
    first_seen_at TEXT NOT NULL,
    last_seen_at  TEXT NOT NULL,
    title         TEXT,
    url           TEXT,
    PRIMARY KEY (platform, surface, external_id)
);
"""


def get_conn(path: str | Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(path), timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 30000")
    return conn


def _migrate_store_schema(conn: sqlite3.Connection) -> None:
    """Idempotent check-then-ALTER evolution (no-op at v1; future versions add columns here)."""
    # (No post-v1 columns yet — this is where check-then-ALTER would go.)
    conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")


def init_store(path: str | Path) -> sqlite3.Connection:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = get_conn(path)
    conn.executescript(SCHEMA)
    _migrate_store_schema(conn)
    conn.commit()
    return conn


def _now(conn: sqlite3.Connection) -> str:
    return str(conn.execute("SELECT datetime('now')").fetchone()[0])


def _norm(v: Any) -> str | None:
    if v is None:
        return None
    s = str(v).strip()
    return s or None


def record_capture(payload: dict, *, path: str | Path) -> dict:
    """Record an agent-gathered capture into the sources.db sidecar.

    Required payload keys: query, source (or source_type), items[]. Each item needs platform,
    source_kind, content, and either a url OR a restricted_reason OR a first-party empirical
    declaration (source_kind in first-party kinds / provenance_class). content_hash dedups
    identical (platform,url,content) within the sidecar. Returns a summary.
    """
    if not isinstance(payload, dict):
        raise ValueError("capture payload must be a JSON object")
    query = _norm(payload.get("query"))
    source = _norm(payload.get("source") or payload.get("source_type"))
    items = payload.get("items")
    if not query or not source:
        raise ValueError("capture requires 'query' and 'source'")
    if not isinstance(items, list) or not items:
        raise ValueError("capture requires a non-empty 'items' array")

    capture_kind = _norm(payload.get("capture_kind")) or "search"
    collector = _norm(payload.get("collector"))
    # POLICY GATE (unbypassable): reject a capture that used a forbidden/disallowed collector for
    # its source OR any item's platform — e.g. xiaohongshu via kimi-webbridge, even if the session
    # lies about `source`. Runs BEFORE any row is written.
    item_platforms = [it.get("platform") for it in items if isinstance(it, dict) and it.get("platform")]
    capabilities.enforce_capture(source, collector, capture_kind, item_platforms)

    conn = init_store(path)
    # W-08 (#28): a caller-supplied id collision must NOT silently overwrite prior evidence. INSERT
    # OR REPLACE used to clobber a prior session's degraded_reason / fallback_chain (a 限流 signal
    # destroyed) when an id was reused. Validate every caller id is fresh BEFORE any row is written.
    sid_given = _norm(payload.get("id"))
    if sid_given and conn.execute(
            "SELECT 1 FROM source_session WHERE id=?", (sid_given,)).fetchone():
        raise ValueError(
            f"capture session id '{sid_given}' already exists; refusing to overwrite prior "
            f"evidence (omit 'id' for an auto-generated unique id)")
    dup_items = [_norm(it.get("id")) for it in items
                 if isinstance(it, dict) and _norm(it.get("id")) and conn.execute(
                     "SELECT 1 FROM source_item WHERE id=?", (_norm(it.get("id")),)).fetchone()]
    if dup_items:
        raise ValueError(
            f"capture item id(s) already exist: {dup_items}; refusing to overwrite "
            f"(omit item 'id' for auto-generated unique ids)")
    now = _now(conn)
    session_id = sid_given or f"rs-{uuid.uuid4().hex[:12]}"
    conn.execute(
        "INSERT INTO source_session "
        "(id,query,source,collector,capture_kind,searched_at,expires_at,captured_by,result_count,"
        "degraded_reason,raw_tool_status,run_id,notes) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (session_id, query, source, _norm(payload.get("collector")), capture_kind,
         _norm(payload.get("searched_at")) or now, _norm(payload.get("expires_at")),
         _norm(payload.get("captured_by")) or "agent",
         payload.get("result_count") if isinstance(payload.get("result_count"), int) else len(items),
         _norm(payload.get("degraded_reason")),
         json.dumps(payload.get("raw_tool_status"), ensure_ascii=False) if payload.get("raw_tool_status") else None,
         _norm(payload.get("run_id")), _norm(payload.get("notes"))),
    )

    written: list[dict] = []
    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"items[{idx}] must be a JSON object")
        platform = _norm(item.get("platform")) or source
        source_kind = _norm(item.get("source_kind"))
        content = item.get("content")
        url = _norm(item.get("url"))
        restricted_reason = _norm(item.get("restricted_reason"))
        missing = [k for k, v in (("source_kind", source_kind), ("content", content))
                   if v is None or (isinstance(v, str) and not v.strip())]
        if missing:
            raise ValueError(f"items[{idx}] missing required keys: {', '.join(missing)}")
        # Normalize platform for first-party check on the in-memory item shape.
        probe = {**item, "platform": platform, "source_kind": source_kind, "content": content}
        first_party = is_first_party_item(probe)
        if not url and not restricted_reason and not first_party:
            raise ValueError(
                f"items[{idx}] without a url must include a restricted_reason "
                f"OR declare first-party empirical (source_kind in "
                f"{sorted(FIRST_PARTY_SOURCE_KINDS)} / provenance_class="
                f"{FIRST_PARTY_PROVENANCE_CLASS!r})")
        # Auto-stamp provenance_class so promote stays eligible even if only source_kind was set.
        meta = _parse_raw_metadata(item.get("raw_metadata"))
        if first_party and meta.get("provenance_class") != FIRST_PARTY_PROVENANCE_CLASS:
            meta = {**meta, "provenance_class": FIRST_PARTY_PROVENANCE_CLASS}
        if first_party and not restricted_reason:
            # Record why there is no public URL (audit trail); does NOT block promote for first-party.
            restricted_reason = "first_party_empirical_no_public_url"

        item_id = _norm(item.get("id")) or f"ri-{uuid.uuid4().hex[:12]}"
        ch = K.content_sha256("|".join([platform, source_kind, url or "", str(content)]))
        conn.execute(
            "INSERT INTO source_item "
            "(id,session_id,platform,source_kind,url,title,content,author,captured_at,raw_metadata,"
            "content_hash,needs_review,restricted_reason) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (item_id, session_id, platform, source_kind, url, _norm(item.get("title")), str(content),
             _norm(item.get("author")), _norm(item.get("captured_at")) or now,
             json.dumps(meta, ensure_ascii=False) if meta else None,
             ch, 0 if item.get("needs_review") is False else 1, restricted_reason),
        )
        written.append({
            "item_id": item_id, "content_hash": ch, "url": url,
            "restricted": restricted_reason is not None and not first_party,
            "first_party": first_party,
        })
    conn.commit()
    return {"session_id": session_id, "source": source, "items": written,
            "count": len(written)}


def list_items(path: str | Path, *, promoted: bool | None = None,
               limit: int | None = None) -> list[dict]:
    if not Path(path).exists():
        return []
    conn = get_conn(path)
    sql = "SELECT * FROM source_item"
    if promoted is True:
        sql += " WHERE promoted_source_ref_id IS NOT NULL"
    elif promoted is False:
        sql += " WHERE promoted_source_ref_id IS NULL"
    sql += " ORDER BY created_at"
    if limit:
        sql += f" LIMIT {int(limit)}"
    return [dict(r) for r in conn.execute(sql).fetchall()]


def dump_store(path: str | Path, out_path: str | Path) -> bool:
    """iterdump the sources.db sidecar to out_path for `ros snapshot` durability (W-08/#6).

    The live sources.db is gitignored; without a dump, every source_session.degraded_reason /
    raw_tool_status.fallback_chain / source_item.restricted_reason (the 限流 / 风控-wall evidence)
    evaporates on worktree deletion — and url-less restricted items can never reach L3, so that
    evidence has no other durable home. Returns False (no-op) when the sidecar doesn't exist."""
    path = Path(path)
    if not path.is_file():
        return False
    conn = get_conn(path)
    try:
        with open(out_path, "w", encoding="utf-8") as f:
            for line in conn.iterdump():
                f.write(line + "\n")
    finally:
        conn.close()
    return True


def promote_item(knowledge_conn: sqlite3.Connection, item_id: str, *, topic_slug: str,
                 path: str | Path, changed_by: str = "agent") -> dict:
    """Promote one raw source_item into a retained source_ref in knowledge.db.

    URL gate:
      * public items need a real http(s) URL;
      * first-party empirical items (no public URL) mint researchos://first-party/<content_hash>;
      * generic restricted captures (login wall / paywall / incomplete card) stay raw-only.

    On promotion we (1) write the global library entry + per-topic cache snapshot and (2) insert a
    source_ref (the URL gate trigger re-validates platform/source_kind/url). Idempotent.
    """
    conn = get_conn(path)
    row = conn.execute("SELECT * FROM source_item WHERE id=?", (item_id,)).fetchone()
    if row is None:
        raise KeyError(f"source_item not found: {item_id}")
    item = dict(row)
    if item.get("promoted_source_ref_id"):
        return {"item_id": item_id, "source_ref_id": item["promoted_source_ref_id"],
                "already_promoted": True}

    ch = item["content_hash"]
    url = item.get("url")
    first_party = False
    if not url:
        if not is_first_party_item(item):
            raise ValueError(
                "cannot promote a source_item without a real URL (restricted capture); "
                "first-party empirical requires platform=manual and "
                f"source_kind in {sorted(FIRST_PARTY_SOURCE_KINDS)} "
                f"(or raw_metadata.provenance_class={FIRST_PARTY_PROVENANCE_CLASS!r})")
        url = first_party_provenance_url(ch)
        first_party = True
    elif not is_public_or_first_party_url(url):
        raise ValueError(
            f"cannot promote: url {url!r} is not http(s)://… or {FIRST_PARTY_URL_PREFIX}<hash>")
    else:
        first_party = url.lower().startswith(FIRST_PARTY_URL_PREFIX) or is_first_party_item(item)

    raw_meta = _parse_raw_metadata(item.get("raw_metadata"))
    if first_party:
        raw_meta = {**raw_meta, "provenance_class": FIRST_PARTY_PROVENANCE_CLASS,
                    "first_party_promote": True}

    library.record_source(
        ch, topic_slug=topic_slug, url=url, platform=item["platform"],
        source_kind=item["source_kind"], cached_full_text=item["content"],
        title=item.get("title"), author=item.get("author"), captured_at=item.get("captured_at"),
        raw_metadata=raw_meta or None)
    cache_fp = library.write_topic_cache(topic_slug, ch, item["content"],
                                         url=url, title=item.get("title"))
    rel_cache = str(cache_fp.relative_to(paths.root())) if cache_fp.is_relative_to(paths.root()) else str(cache_fp)

    # Normalize platform to a vocab canonical when first_party alias was used.
    platform = item["platform"]
    if (platform or "").lower() in ("first_party", "researcher"):
        platform = "manual"

    src_id = K.add_source_ref(
        knowledge_conn, platform=platform, source_kind=item["source_kind"],
        url=url, subject_type="pending", author=item.get("author"),
        title=item.get("title"), content_hash=ch, cached_text_path=rel_cache,
        intake_item_id=item_id, captured_at=item.get("captured_at"), captured_by=changed_by)
    knowledge_conn.commit()

    conn.execute("UPDATE source_item SET promoted_source_ref_id=? WHERE id=?", (src_id, item_id))
    conn.commit()
    return {"item_id": item_id, "source_ref_id": src_id, "content_hash": ch,
            "cached_text_path": rel_cache, "already_promoted": False,
            "first_party": first_party, "url": url}


def link_source(knowledge_conn: sqlite3.Connection, content_hash: str, *, topic_slug: str,
                changed_by: str = "agent") -> dict:
    """Reuse an ALREADY-retained source (in the global library) into another topic WITHOUT
    re-fetching — the expensive fetch/transcript is shared, but provenance stays independent: a
    fresh source_ref is minted in THIS topic's knowledge.db and the topic is added as a library
    referrer. Idempotent per (topic, content_hash). Cross-topic铁律: no L-row is ever copied; the
    new topic will distill its own L3 from the shared cached text.
    """
    rec = library.read_source(content_hash)
    if rec is None:
        raise KeyError(f"library has no source for hash {content_hash}")
    if not rec.get("url"):
        raise ValueError("library record has no url; cannot link (URL gate)")

    # already linked into this topic?
    existing = knowledge_conn.execute(
        "SELECT id FROM source_ref WHERE content_hash=?", (content_hash,)).fetchone()
    if existing is not None:
        return {"topic_slug": topic_slug, "source_ref_id": existing[0],
                "content_hash": content_hash, "already_linked": True}

    cache_fp = library.write_topic_cache(topic_slug, content_hash,
                                         rec.get("cached_full_text") or "",
                                         url=rec.get("url"), title=rec.get("title"))
    rel_cache = str(cache_fp.relative_to(paths.root())) if cache_fp.is_relative_to(paths.root()) else str(cache_fp)
    src_id = K.add_source_ref(
        knowledge_conn, platform=rec["platform"], source_kind=rec["source_kind"], url=rec["url"],
        subject_type="pending", author=rec.get("author"), title=rec.get("title"),
        content_hash=content_hash, cached_text_path=rel_cache,
        media_transcript_path=None, captured_at=rec.get("captured_at"), captured_by=changed_by)
    knowledge_conn.commit()
    library.record_source(content_hash, topic_slug=topic_slug, url=rec["url"],
                          platform=rec["platform"], source_kind=rec["source_kind"])
    return {"topic_slug": topic_slug, "source_ref_id": src_id, "content_hash": content_hash,
            "already_linked": False}


def bulk_promote(knowledge_conn: sqlite3.Connection, *, topic_slug: str, path: str | Path,
                 changed_by: str = "agent") -> dict:
    """Promote every promotable un-promoted item (http(s) URL or first-party empirical).

    Each row in its own try/except (one bad row can't abort the batch). Idempotent.
    Generic restricted (url-less, not first-party) items are reported as skipped.
    """
    promoted, skipped, errors = [], [], []
    for item in list_items(path, promoted=False):
        if not item.get("url") and not is_first_party_item(item):
            skipped.append({"item_id": item["id"], "reason": "no url (restricted)"})
            continue
        try:
            res = promote_item(knowledge_conn, item["id"], topic_slug=topic_slug, path=path,
                               changed_by=changed_by)
            promoted.append(res)
        except Exception as e:  # noqa: BLE001 — surface per-row failures, keep going
            errors.append({"item_id": item["id"], "error": str(e)})
    return {"promoted": promoted, "skipped": skipped, "errors": errors,
            "counts": {"promoted": len(promoted), "skipped": len(skipped), "errors": len(errors)}}
