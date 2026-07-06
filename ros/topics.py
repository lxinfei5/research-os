"""Topic registry + scaffolding.

ONE topic == one topics/<slug>/ directory == one independent knowledge.db (+ sources.db) == one
full L0–L3 world knowledge. There is no global topic_id; physical isolation IS the multi-copy
requirement (DESIGN.md §3). topics/_index.yaml is a human-readable registry with alias resolution so
"geopolitics" and "地缘政治" can't fork into two databases for the same research thread.
"""
from __future__ import annotations

import re
import sqlite3
import unicodedata

from . import paths
from .storage import intake, knowledge

try:
    import yaml
except ModuleNotFoundError as e:  # pragma: no cover
    raise SystemExit(
        "ResearchOS needs PyYAML. Install it:  pip install -r requirements.txt") from e


# ---------------------------------------------------------------------------
# slug + index helpers
# ---------------------------------------------------------------------------
def slugify(name: str) -> str:
    """ascii-ish kebab slug; non-ascii (e.g. Chinese titles) fall back to a normalized unicode token.

    The result is always path-safe: any run of non-word chars (incl. '/', spaces, punctuation)
    collapses to '_'. CJK characters are kept (Python's \\w matches them under unicode).
    """
    name = (name or "").strip()
    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^a-zA-Z0-9]+", "_", ascii_name).strip("_").lower()
    if s:
        return s
    return re.sub(r"[^\w]+", "_", name, flags=re.UNICODE).strip("_").lower() or "topic"


def _load_index() -> dict:
    fp = paths.index_path()
    if not fp.is_file():
        return {"topics": []}
    data = yaml.safe_load(fp.read_text(encoding="utf-8")) or {}
    data.setdefault("topics", [])
    return data


def _save_index(data: dict) -> None:
    fp = paths.index_path()
    fp.parent.mkdir(parents=True, exist_ok=True)
    fp.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def _index_entry(data: dict, slug: str) -> dict | None:
    for t in data.get("topics", []):
        if t.get("slug") == slug:
            return t
    return None


# ---------------------------------------------------------------------------
# resolution
# ---------------------------------------------------------------------------
def resolve_slug(name: str) -> str | None:
    """Match a user-supplied name to an existing topic by slug / title / alias (case-insensitive).

    Returns the canonical slug, or None if no existing topic matches.
    """
    if not name:
        return None
    needle = name.strip().lower()
    data = _load_index()
    for t in data.get("topics", []):
        candidates = [t.get("slug", ""), t.get("title", "")] + list(t.get("aliases") or [])
        if any(needle == str(c).strip().lower() for c in candidates if c):
            return t.get("slug")
    # also accept a not-yet-registered slug that already has a directory
    if paths.topic_dir(slugify(name)).is_dir():
        return slugify(name)
    return None


def exists(slug: str) -> bool:
    return paths.knowledge_db(slug).is_file()


# ---------------------------------------------------------------------------
# lifecycle
# ---------------------------------------------------------------------------
def new_topic(name: str, *, title: str | None = None, aliases: list[str] | None = None) -> dict:
    """Scaffold a new topic: directory tree + knowledge.db + sources.db + topic.yaml + registry.

    Refuses to fork an existing thread: if `name` (or any given alias) resolves to an existing topic,
    raises with the canonical slug so the caller can `ros topic open` it instead.
    """
    existing = resolve_slug(name)
    if existing:
        raise ValueError(f"topic already exists as '{existing}' — use `ros topic open {existing}`")
    for a in aliases or []:
        hit = resolve_slug(a)
        if hit:
            raise ValueError(f"alias '{a}' already maps to topic '{hit}'")

    slug = slugify(name)
    title = title or name
    paths.ensure_topic_tree(slug)

    # init both per-topic databases
    knowledge.init_db(paths.knowledge_db(slug)).close()
    intake.init_store(paths.sources_db(slug)).close()

    now = _utc_now()
    manifest = {
        "slug": slug,
        "title": title,
        "status": "open",
        "created_at": now,
        "aliases": list(aliases or []),
        "facets": [],
        "media_prompt": title,        # whisper domain-bias prompt (per-topic, Phase 2)
        "methodology_versions": {"layering": "v1", "credibility": "v1"},
        "stage": "scoping",
        "schema_version": knowledge.current_schema_version(),
    }
    _write_manifest(slug, manifest)

    data = _load_index()
    data["topics"].append({
        "slug": slug, "title": title, "aliases": list(aliases or []),
        "status": "open", "created_at": now, "last_grown_at": None,
        "coverage": "L0=0 L1=0 L2=0 L3=0", "related": [],
    })
    _save_index(data)
    return manifest


def load_manifest(slug: str) -> dict:
    fp = paths.topic_yaml(slug)
    if not fp.is_file():
        raise KeyError(f"topic.yaml not found for '{slug}'")
    return yaml.safe_load(fp.read_text(encoding="utf-8")) or {}


def _write_manifest(slug: str, manifest: dict) -> None:
    paths.topic_yaml(slug).write_text(
        yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False), encoding="utf-8")


def set_active(slug: str) -> None:
    ptr = paths.active_pointer()
    ptr.parent.mkdir(parents=True, exist_ok=True)
    ptr.write_text(slug + "\n", encoding="utf-8")


def active() -> str | None:
    ptr = paths.active_pointer()
    if not ptr.is_file():
        return None
    return (ptr.read_text(encoding="utf-8").strip() or None)


def require_slug(name: str | None) -> str:
    """Resolve a slug from an explicit name or the active pointer; raise if neither resolves.

    Auto-materializes the live knowledge.db when absent (worktree / fresh clone) by restoring
    from the latest committed snapshot — so every CLI command works out-of-the-box in a worktree.
    """
    if name:
        slug = resolve_slug(name) or (name if exists(name) else None)
        if not slug:
            raise KeyError(f"no topic matches '{name}' (try `ros topic ls`)")
    else:
        cur = active()
        if not cur:
            raise KeyError("no active topic — pass a <slug> or run `ros topic open <slug>` first")
        slug = cur
    knowledge.ensure_knowledge_db(slug)
    return slug


def open_topic(name: str) -> dict:
    slug = require_slug(name)
    if not exists(slug):
        raise KeyError(f"topic '{slug}' has no knowledge.db (was it scaffolded?)")
    set_active(slug)
    return show_topic(slug)


def show_topic(slug: str) -> dict:
    slug = require_slug(slug)
    manifest = load_manifest(slug)
    conn = knowledge.get_conn(paths.knowledge_db(slug))
    try:
        cov = knowledge.coverage(conn)
    finally:
        conn.close()
    return {"slug": slug, "manifest": manifest, "coverage": cov, "active": active() == slug}


def list_topics() -> list[dict]:
    data = _load_index()
    out = []
    for t in data.get("topics", []):
        out.append({"slug": t.get("slug"), "title": t.get("title"),
                    "status": t.get("status"), "coverage": t.get("coverage"),
                    "last_grown_at": t.get("last_grown_at")})
    return out


def archive_topic(name: str) -> str:
    slug = require_slug(name)
    data = _load_index()
    entry = _index_entry(data, slug)
    if entry:
        entry["status"] = "archived"
        _save_index(data)
    manifest = load_manifest(slug)
    manifest["status"] = "archived"
    _write_manifest(slug, manifest)
    return slug


def update_coverage(slug: str) -> str:
    """Refresh the registry's coverage string from the topic's live knowledge.db counts."""
    conn = knowledge.get_conn(paths.knowledge_db(slug))
    try:
        cov = knowledge.coverage(conn)
    finally:
        conn.close()
    s = f"L0={cov['l0']} L1={cov['l1']} L2={cov['l2']} L3={cov['l3']} src={cov['sources']}"
    data = _load_index()
    entry = _index_entry(data, slug)
    if entry:
        entry["coverage"] = s
        _save_index(data)
    return s


def merge_topic(src_name: str, dst_name: str) -> dict:
    """Merge `src` into `dst` when they turn out to be the same research thread (escape hatch for
    topic-identity drift). Respects the iron rule: NO evidence rows are copied — instead every source
    `src` retained is LINKED into `dst` (dst re-distills them under its own lens), and `src` is
    archived. Idempotent on sources already in dst.
    """
    src = require_slug(src_name)
    dst = require_slug(dst_name)
    if src == dst:
        raise ValueError("cannot merge a topic into itself")
    from .storage import intake, knowledge
    sconn = knowledge.get_conn(paths.knowledge_db(src))
    try:
        hashes = [r[0] for r in sconn.execute(
            "SELECT DISTINCT content_hash FROM source_ref WHERE content_hash IS NOT NULL").fetchall()]
    finally:
        sconn.close()
    dconn = knowledge.get_conn(paths.knowledge_db(dst))
    linked = 0
    try:
        for h in hashes:
            try:
                res = intake.link_source(dconn, h, topic_slug=dst)
                linked += 0 if res.get("already_linked") else 1
            except (KeyError, ValueError):
                continue
    finally:
        dconn.close()
    archive_topic(src)
    update_related()
    return {"src": src, "dst": dst, "linked_sources": linked,
            "note": f"'{src}' archived; run `ros condense {dst}` to distill the linked sources"}


def update_related() -> dict[str, list[str]]:
    """Recompute shares_source edges from the global library and write them into _index.yaml.

    Two topics that both reference the same retained source (same content hash) get a
    `related: [{slug, relation: shares_source}]` edge — navigation only, never knowledge merging.
    """
    from . import library
    co: dict[str, set[str]] = {}
    for rec in library.shared_sources():
        slugs = rec.get("referenced_by_topics") or []
        for s in slugs:
            co.setdefault(s, set()).update(x for x in slugs if x != s)
    data = _load_index()
    for entry in data.get("topics", []):
        peers = sorted(co.get(entry["slug"], set()))
        entry["related"] = [{"slug": p, "relation": "shares_source"} for p in peers]
    _save_index(data)
    return {k: sorted(v) for k, v in co.items()}


def add_facet(name: str | None, question: str) -> dict:
    """Add a research facet (sub-question) to a topic — recorded in topic.yaml + the facet table."""
    slug = require_slug(name)
    fid = "f_" + slugify(question)[:32].strip("_") if slugify(question) else knowledge.gen_id("f")
    conn = knowledge.get_conn(paths.knowledge_db(slug))
    try:
        knowledge.upsert_facet(conn, id=fid, question=question)
        conn.commit()
    finally:
        conn.close()
    manifest = load_manifest(slug)
    facets = manifest.setdefault("facets", [])
    if not any(f.get("id") == fid for f in facets):
        facets.append({"id": fid, "question": question, "status": "open"})
        _write_manifest(slug, manifest)
    return {"slug": slug, "facet_id": fid, "question": question}


def _utc_now() -> str:
    conn = sqlite3.connect(":memory:")
    try:
        return str(conn.execute("SELECT datetime('now')").fetchone()[0])
    finally:
        conn.close()
