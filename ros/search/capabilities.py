"""Source acquisition POLICY gate — the unbypassable enforcement point for collector rules.

Loads source_capabilities.yaml and validates that a capture used an ALLOWED collector for its
source. The load-bearing rule for ResearchOS: Xiaohongshu search must use `xiaohongshu-mcp`;
`kimi-webbridge` / `browser` are forbidden. This runs inside record_capture (capture time), so no
raw item can enter the system via a forbidden path.

Python only checks the declared collector against policy — it does not fetch. Adapters declare which
collector they require; the agent does the fetching via the matching skill.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

_POLICY_PATH = Path(__file__).resolve().parent / "source_capabilities.yaml"

SEARCH_CAPTURE_KINDS = {"search", "detail", "fetch"}

# Alias → canonical source/platform id. The gate normalizes through this so a capture can't dodge
# the policy by spelling Xiaohongshu as "小红书" / "xhs". Keep in sync with vocab_seed.sql.
_ALIASES = {
    "小红书": "xiaohongshu", "xhs": "xiaohongshu", "rednote": "xiaohongshu", "redbook": "xiaohongshu",
    "抖音": "douyin",
    "twitter": "x", "x(twitter)": "x",
    "微信": "wechat",
    "web_page": "web", "website": "web", "google": "web", "bing": "web", "baidu": "web",
}


class CollectorPolicyError(ValueError):
    """A capture declared a collector forbidden (or not permitted) for its source."""


def canonical(name: str | None) -> str:
    """Normalize a source/platform name to its canonical id (lowercased, alias-resolved)."""
    n = (name or "").strip().lower()
    return _ALIASES.get(n, n)


@lru_cache(maxsize=1)
def _policy() -> dict:
    data = yaml.safe_load(_POLICY_PATH.read_text(encoding="utf-8")) or {}
    return data.get("sources", {})


def known_sources() -> list[str]:
    return sorted(_policy().keys())


def source_policy(source: str) -> dict:
    return _policy().get(canonical(source), {})


def _as_list(v) -> list[str]:
    if v is None:
        return []
    return list(v) if isinstance(v, (list, tuple)) else [v]


def required_collectors(source: str) -> list[str]:
    return _as_list(source_policy(source).get("required_search_collector"))


def forbidden_collectors(source: str) -> list[str]:
    return _as_list(source_policy(source).get("forbidden_search_collectors"))


def validate_collector(source: str, collector: str | None, *, capture_kind: str = "search") -> None:
    """Raise CollectorPolicyError if `collector` is not permitted for `source` search captures.

    Rules (only enforced for search-like capture kinds):
      * collector in forbidden_search_collectors  → reject  (e.g. xiaohongshu + kimi-webbridge)
      * required_search_collector set and collector given but not in it → reject
      * required_search_collector set, collector_optional is false, and collector missing → reject
    Unknown sources are permitted (no policy = no constraint), but a forbidden list still applies.
    """
    if capture_kind not in SEARCH_CAPTURE_KINDS:
        return
    pol = source_policy(source)
    coll = (collector or "").strip() or None

    forbidden = forbidden_collectors(source)
    if coll and coll in forbidden:
        raise CollectorPolicyError(
            f"source '{source}' forbids collector '{coll}' for search "
            f"(forbidden: {forbidden}). Use the required collector instead.")

    required = required_collectors(source)
    if not required:
        return
    if coll is None:
        if pol.get("collector_optional"):
            return
        raise CollectorPolicyError(
            f"source '{source}' search captures must declare collector (one of {required})")
    if coll not in required:
        raise CollectorPolicyError(
            f"source '{source}' search captures must use collector in {required}; got '{coll}'"
            + (f" (forbidden: {forbidden})" if forbidden else ""))


def enforce_capture(source: str, collector: str | None, capture_kind: str,
                    item_platforms: list[str] | None = None) -> None:
    """Airtight capture gate: validate the declared source AND every item's platform.

    Validating per-item platforms (not just the session source) closes the spoof where a capture
    declares `source: web` but smuggles xiaohongshu items collected via kimi-webbridge. Only
    platforms that carry a forbidden/required collector policy are re-checked (web/manual are free).
    """
    validate_collector(source, collector, capture_kind=capture_kind)
    seen = {canonical(source)}
    for p in item_platforms or []:
        cp = canonical(p)
        if cp in seen:
            continue
        seen.add(cp)
        pol = source_policy(cp)
        if pol.get("forbidden_search_collectors") or pol.get("required_search_collector"):
            validate_collector(cp, collector, capture_kind=capture_kind)


def search_entry(source: str) -> str | None:
    pol = source_policy(source)
    return pol.get("search_entry") or pol.get("search_entry_url")
