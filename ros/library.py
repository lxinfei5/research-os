"""Global content-addressed original-source store: library/sources/<sha256>.json.

The same URL fetched under two topics is stored ONCE (keyed by content hash) with a
referenced_by_topics[] list — the expensive fetch/transcription is shared, while each topic's
provenance (source_ref rows, L-rows) stays independent in that topic's knowledge.db.

Video/image content is already converted to text BEFORE it reaches here, so cached_full_text /
media_transcript are always text. This module does only deterministic file I/O — no reasoning.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from . import paths


def _read(path: Path) -> dict | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def read_source(content_hash: str) -> dict | None:
    """Return the global library record for a content hash, or None."""
    return _read(paths.library_source_path(content_hash))


def list_sources() -> list[dict]:
    """All global library records (one per retained original)."""
    d = paths.library_sources_dir()
    if not d.is_dir():
        return []
    out = []
    for fp in sorted(d.glob("*.json")):
        rec = _read(fp)
        if rec:
            out.append(rec)
    return out


def shared_sources() -> list[dict]:
    """Library records referenced by more than one topic (the cross-topic overlap)."""
    return [r for r in list_sources() if len(r.get("referenced_by_topics") or []) > 1]


def record_source(content_hash: str, *, topic_slug: str, url: str, platform: str,
                  source_kind: str, cached_full_text: str | None = None,
                  title: str | None = None, author: str | None = None,
                  media_transcript: str | None = None, ocr_text: str | None = None,
                  screenshot_path: str | None = None, captured_at: str | None = None,
                  raw_metadata: Any = None) -> Path:
    """Upsert the global library entry for a source; register topic_slug as a referrer.

    Idempotent: re-recording the same hash merges referenced_by_topics and fills any newly-provided
    text fields without clobbering existing non-empty ones. Returns the library file path.
    """
    paths.library_sources_dir().mkdir(parents=True, exist_ok=True)
    fp = paths.library_source_path(content_hash)
    existing = _read(fp) or {}

    referrers = set(existing.get("referenced_by_topics") or [])
    referrers.add(topic_slug)

    def _keep(old: Any, new: Any) -> Any:
        # Prefer an existing non-empty value; otherwise take the new one.
        return old if (old not in (None, "")) else new

    record = {
        "content_hash": content_hash,
        "url": _keep(existing.get("url"), url),
        "platform": _keep(existing.get("platform"), platform),
        "source_kind": _keep(existing.get("source_kind"), source_kind),
        "title": _keep(existing.get("title"), title),
        "author": _keep(existing.get("author"), author),
        "cached_full_text": _keep(existing.get("cached_full_text"), cached_full_text),
        "media_transcript": _keep(existing.get("media_transcript"), media_transcript),
        "ocr_text": _keep(existing.get("ocr_text"), ocr_text),
        "screenshot_path": _keep(existing.get("screenshot_path"), screenshot_path),
        "captured_at": _keep(existing.get("captured_at"), captured_at),
        "raw_metadata": existing.get("raw_metadata") if existing.get("raw_metadata") else raw_metadata,
        "referenced_by_topics": sorted(referrers),
        "first_seen_at": existing.get("first_seen_at") or captured_at,
        "last_seen_at": captured_at or existing.get("last_seen_at"),
    }
    fp.write_text(json.dumps(record, ensure_ascii=False, indent=1), encoding="utf-8")
    return fp


def write_topic_cache(topic_slug: str, content_hash: str, text: str, *,
                      url: str | None = None, title: str | None = None) -> Path:
    """Write the per-topic cached-text snapshot (link + cached text). Returns the file path."""
    paths.cache_dir(topic_slug).mkdir(parents=True, exist_ok=True)
    fp = paths.cache_path(topic_slug, content_hash)
    header = []
    if title:
        header.append(f"# {title}")
    if url:
        header.append(f"<{url}>")
    header.append(f"`content_hash: {content_hash}`\n")
    fp.write_text("\n".join(header) + "\n" + (text or ""), encoding="utf-8")
    return fp
