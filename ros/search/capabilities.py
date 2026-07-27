"""Source acquisition POLICY — soft routing hints, hard ban only for explicit forbids.

Loads source_capabilities.yaml. Philosophy (AStockOSV2-aligned):
  * preferred collectors are routing hints (warn when off-list / missing)
  * only `forbidden_search_collectors` hard-reject
  * agent records which path actually worked; Python does not ban working tools by name

Python only checks the declared collector — it does not fetch.
"""
from __future__ import annotations

import re
import urllib.parse
from functools import lru_cache
from pathlib import Path

import yaml

_POLICY_PATH = Path(__file__).resolve().parent / "source_capabilities.yaml"

SEARCH_CAPTURE_KINDS = {"search", "detail", "fetch"}

# Alias → canonical source/platform id. Keep in sync with vocab_seed.sql.
_ALIASES = {
    "小红书": "xiaohongshu", "xhs": "xiaohongshu", "rednote": "xiaohongshu", "redbook": "xiaohongshu",
    "red": "xiaohongshu",   # RED = Xiaohongshu's international app name
    "抖音": "douyin",
    "twitter": "x", "x(twitter)": "x",
    "微信": "wechat",
    "web_page": "web", "website": "web", "google": "web", "bing": "web", "baidu": "web",
}

# XHS-exclusive name stems for canonical() (domain / traditional CJK / app suffixes).
_XHS_STEMS = ("xiaohongshu", "小红书", "小紅書", "小红書", "小紅书", "rednote", "redbook")

# XHS URL HOSTS — transport truth for honest platform labeling (host/platform lint).
# Not a browse denylist: browser access to XHS is allowed; we only insist retained rows
# with an XHS host declare platform=xiaohongshu (not 'web').
XHS_HOST_STEMS = ("xiaohongshu.com", "xhslink.com", "xhs.cn", "rednote.com", "xhscdn.com")


def host_is_xhs(url: str | None) -> bool:
    """True iff url's host is a Xiaohongshu origin. Used for platform-label honesty, not bans."""
    if not url:
        return False
    try:
        h = (urllib.parse.urlparse(str(url)).hostname or "").lower()
    except ValueError:
        return False
    if h.startswith("www."):
        h = h[4:]
    return any(h == s or h.endswith("." + s) for s in XHS_HOST_STEMS)


class CollectorPolicyError(ValueError):
    """Hard rejection — only for collectors on an explicit forbidden list."""


def canonical(name: str | None) -> str:
    """Normalize a source/platform name to its canonical id (lowercased, alias-resolved)."""
    n = (name or "").strip().lower()
    if n in _ALIASES:
        return _ALIASES[n]
    if any(stem in n for stem in _XHS_STEMS):
        return "xiaohongshu"
    # 'RED Note' / 'RED.Note' → collapse punctuation so romanized rebrands still resolve.
    compact = re.sub(r"[^a-z0-9]+", "", n)
    if compact and compact != n and any(stem in compact for stem in _XHS_STEMS):
        return "xiaohongshu"
    return n


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


def validate_collector(source: str, collector: str | None, *, capture_kind: str = "search") -> list[str]:
    """Validate collector against policy.

    Hard-raises CollectorPolicyError only for explicitly forbidden collectors.
    Returns a list of advisory warning strings for:
      * missing collector when a preferred list exists
      * collector not on the preferred allow-list
    Off-list / unknown collectors are ACCEPTED (AStockOSV2: don't ban working tools by name).
    """
    warnings: list[str] = []
    coll = (collector or "").strip().lower() or None

    # (1) explicit denylist only — hard reject
    forbidden = forbidden_collectors(source)
    if coll and coll in {f.strip().lower() for f in forbidden}:
        raise CollectorPolicyError(
            f"source '{source}' forbids collector '{collector}' "
            f"(forbidden: {forbidden}). Use a permitted collector instead.")

    # (2) preferred allow-list is advisory for search-like captures
    if capture_kind not in SEARCH_CAPTURE_KINDS:
        return warnings
    pol = source_policy(source)
    required = required_collectors(source)
    if not required:
        return warnings
    pref = {r.strip().lower() for r in required}
    if coll is None:
        if pol.get("collector_optional"):
            return warnings  # explicit optional: no warn
        warnings.append(
            f"source '{source}' search capture has no collector declared "
            f"(preferred: {required}); recorded anyway")
        return warnings
    if coll not in pref:
        warnings.append(
            f"source '{source}' collector '{collector}' not in preferred list {required}; "
            f"recorded anyway (soft gate)")
    return warnings


def enforce_capture(source: str, collector: str | None, capture_kind: str,
                    item_platforms: list[str] | None = None) -> list[str]:
    """Validate session source + per-item platforms. Raises only on forbidden; returns warnings."""
    warnings = list(validate_collector(source, collector, capture_kind=capture_kind))
    seen = {canonical(source)}
    for p in item_platforms or []:
        cp = canonical(p)
        if cp in seen:
            continue
        seen.add(cp)
        pol = source_policy(cp)
        if pol.get("forbidden_search_collectors") or pol.get("required_search_collector"):
            warnings.extend(validate_collector(cp, collector, capture_kind=capture_kind))
    return warnings


def search_entry(source: str) -> str | None:
    pol = source_policy(source)
    return pol.get("search_entry") or pol.get("search_entry_url")
