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
    "red": "xiaohongshu",   # RED = Xiaohongshu's international app name (crown-jewel alias completeness)
    "抖音": "douyin",
    "twitter": "x", "x(twitter)": "x",
    "微信": "wechat",
    "web_page": "web", "website": "web", "google": "web", "bing": "web", "baidu": "web",
}

# Distinctive, XHS-EXCLUSIVE stems. Any source/platform string CONTAINING one means Xiaohongshu, so it
# canonicalizes to xiaohongshu even when the exact spelling isn't enumerated in _ALIASES — the domain
# `www.xiaohongshu.com`, traditional `小紅書`, `小红书APP` / `小红书网`, etc. This makes the crown-jewel
# forbid FAIL CLOSED for the one source whose mis-collection is irreversible (account ban), instead of
# playing whack-a-mole on _ALIASES. Stems are long + XHS-only, so no legit web/x/douyin source hits them.
# (`xhs`/`red` stay EXACT aliases above — too short to substring-match safely.) The CJK stems cover all
# four simplified/traditional combinations of 小[红|紅][书|書] so script-mixing can't dodge it; the pinyin
# stem covers the romanized name + domain. NB: this gate audits the DECLARED source — it is not a sandbox
# against an adversary hand-crafting Unicode homoglyphs (who could defeat any declared-value gate anyway).
_XHS_STEMS = ("xiaohongshu", "小红书", "小紅書", "小红書", "小紅书", "rednote", "redbook")


class CollectorPolicyError(ValueError):
    """A capture declared a collector forbidden (or not permitted) for its source."""


def canonical(name: str | None) -> str:
    """Normalize a source/platform name to its canonical id (lowercased, alias-resolved).

    After the exact-alias lookup, fall back to XHS-stem containment so an off-list spelling of
    Xiaohongshu (its domain, traditional Chinese, `…APP`/`…网` suffixes) still resolves to xiaohongshu
    and hits the crown-jewel forbid — the ban must not be dodgeable by an unenumerated spelling.
    """
    n = (name or "").strip().lower()
    if n in _ALIASES:
        return _ALIASES[n]
    if any(stem in n for stem in _XHS_STEMS):
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


def validate_collector(source: str, collector: str | None, *, capture_kind: str = "search") -> None:
    """Raise CollectorPolicyError if `collector` is not permitted for `source`.

    Two rules with DELIBERATELY different scopes:
      * forbidden_search_collectors → rejected for EVERY capture_kind. A forbidden browser bridge
        (xiaohongshu + kimi-webbridge / browser / webbridge-mcp) is forbidden ABSOLUTELY — the ban
        must not be dodgeable by declaring an off-list capture_kind like "note"/"favorites"/"likes".
        This is the crown-jewel invariant, so it runs BEFORE the search-kind early-out. (Before this
        was gated behind SEARCH_CAPTURE_KINDS too, which let any non-search kind no-op the whole gate.)
      * required_search_collector → enforced only for search-like kinds (search/detail/fetch); other
        kinds (e.g. a raw non-search snapshot) needn't declare a search collector.
    Unknown sources are permitted (no policy = no constraint), but a forbidden list still applies.
    """
    # Collector names are a lowercase controlled vocabulary. Case-fold (like source names go through
    # canonical()) so a case-variant spelling — "Kimi-Webbridge", "WEBBRIDGE-MCP" — can't slip past a
    # forbidden browser bridge. Compare against case-folded policy lists too (belt-and-suspenders in
    # case a list is ever authored with uppercase).
    coll = (collector or "").strip().lower() or None

    # (1) forbidden collectors are ABSOLUTE — checked for every capture_kind (crown jewel).
    forbidden = forbidden_collectors(source)
    if coll and coll in {f.strip().lower() for f in forbidden}:
        raise CollectorPolicyError(
            f"source '{source}' forbids collector '{collector}' "
            f"(forbidden: {forbidden}). Use the required collector instead.")

    # (2) the required-collector rule only applies to search-like captures.
    if capture_kind not in SEARCH_CAPTURE_KINDS:
        return
    pol = source_policy(source)
    required = required_collectors(source)
    if not required:
        return
    if coll is None:
        if pol.get("collector_optional"):
            return
        raise CollectorPolicyError(
            f"source '{source}' search captures must declare collector (one of {required})")
    if coll not in {r.strip().lower() for r in required}:
        raise CollectorPolicyError(
            f"source '{source}' search captures must use collector in {required}; got '{collector}'"
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
