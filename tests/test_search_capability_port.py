"""Locks in the AStockOS search-capability port: the Tier-3 quota-free multi-search-engine skill,
the web 3-tier fallback collector policy (incl. the fetch-Tier-3 browser reader), the static
registry lint gate, and the crown-jewel XHS collector gate that must survive the port unchanged.

All checks are static/pure (no network, no built .db), so they run in the deterministic suite.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from ros import paths
from ros.boundary import gates
from ros.search import capabilities

REPO = paths.PKG_DIR.parent
SKILL_DIR = REPO / ".agents" / "skills" / "multi-search-engine"
METHOD = REPO / "control_plane" / "reasoning" / "methodology"


# ── the Tier-3 skill actually exists (not a dangling policy reference) ────────
def test_multi_search_engine_skill_and_registry_exist():
    assert (SKILL_DIR / "SKILL.md").is_file()
    cfg = SKILL_DIR / "config.json"
    engines = json.loads(cfg.read_text(encoding="utf-8"))["engines"]
    assert engines, "engine registry must be non-empty (engines_attempted audit source)"
    for e in engines:
        assert e.get("name") and "{keyword}" in e["url"], f"bad engine entry: {e}"
    names = {e["name"] for e in engines}
    # a domestic + an international engine both present (language routing needs both sides)
    assert {"Baidu", "Google"} <= names


# ── web is a 3-tier chain, not a single provider ─────────────────────────────
def test_web_policy_allows_tier3_search_and_fetch_fallbacks():
    for src in ("web", "web_search"):
        allowed = capabilities.required_collectors(src)
        # search Tier-3 (quota-free) + fetch Tier-3 (browser reader) both whitelisted
        assert "multi-search-engine" in allowed, f"{src} lost the quota-free Tier-3 fallback"
        assert "kimi-webbridge" in allowed, f"{src} lost the fetch-Tier-3 browser reader"
        assert "zhipu" in allowed and "web-reader" in allowed


def test_web_capture_may_declare_any_tier_collector():
    # a Tier-3 search capture and a browser-read fetch capture both pass the gate
    capabilities.validate_collector("web", "multi-search-engine", capture_kind="search")
    capabilities.validate_collector("web", "kimi-webbridge", capture_kind="fetch")
    capabilities.validate_collector("web", None, capture_kind="search")  # collector_optional


# ── X / 抖音 are pinned to the real-login browser collector (kimi-webbridge) ──
def test_x_and_douyin_are_pinned_to_kimi_webbridge():
    # both KOL-social sources depend on the user's real browser/login → kimi-webbridge only
    for src in ("x", "douyin"):
        capabilities.validate_collector(src, "kimi-webbridge", capture_kind="search")
        for bad in ("xiaohongshu-mcp", "browser", "multi-search-engine"):
            with pytest.raises(capabilities.CollectorPolicyError):
                capabilities.validate_collector(src, bad, capture_kind="search")
        # neither is collector_optional → an undeclared collector is rejected too
        with pytest.raises(capabilities.CollectorPolicyError):
            capabilities.validate_collector(src, None, capture_kind="search")
    # alias 抖音 normalizes to douyin and stays pinned
    with pytest.raises(capabilities.CollectorPolicyError):
        capabilities.validate_collector("抖音", "xiaohongshu-mcp", capture_kind="search")


# ── the crown-jewel gate must survive the port unchanged ─────────────────────
def test_xiaohongshu_still_forbids_kimi_webbridge_and_browser():
    for bad in ("kimi-webbridge", "browser"):
        with pytest.raises(capabilities.CollectorPolicyError):
            capabilities.validate_collector("xiaohongshu", bad, capture_kind="search")
    # alias spoofing still normalized + rejected
    with pytest.raises(capabilities.CollectorPolicyError):
        capabilities.validate_collector("小红书", "kimi-webbridge", capture_kind="search")
    # per-item platform spoof (session says web, item is xhs via kimi-webbridge) still caught
    with pytest.raises(capabilities.CollectorPolicyError):
        capabilities.enforce_capture("web", "kimi-webbridge", "search", item_platforms=["xiaohongshu"])


# ── webbridge-mcp: the sub-agent-reachable real-Chrome transport ─────────────
def test_webbridge_mcp_is_an_allowed_peer_for_x_douyin_and_web():
    # webbridge-mcp (MCP, sub-agent reachable) is an equal peer of the kimi-webbridge skill wherever
    # the real browser is allowed — X, 抖音, and the web fetch-Tier-3 browser reader all accept it.
    for src in ("x", "douyin"):
        capabilities.validate_collector(src, "webbridge-mcp", capture_kind="search")
        capabilities.validate_collector(src, "kimi-webbridge", capture_kind="search")  # skill peer still ok
    assert "webbridge-mcp" in capabilities.required_collectors("抖音")  # alias resolves + allows it
    for src in ("web", "web_search"):
        capabilities.validate_collector(src, "webbridge-mcp", capture_kind="fetch")
        assert "webbridge-mcp" in capabilities.required_collectors(src)


def test_webbridge_mcp_is_forbidden_for_xiaohongshu_crown_jewel():
    # the crown jewel: a general browser bridge — whether it reaches Chrome as an MCP (webbridge-mcp)
    # or a skill (kimi-webbridge) — must NEVER scrape XHS. Only xiaohongshu-mcp.
    for src in ("xiaohongshu", "小红书"):
        with pytest.raises(capabilities.CollectorPolicyError):
            capabilities.validate_collector(src, "webbridge-mcp", capture_kind="search")
    assert "webbridge-mcp" in capabilities.forbidden_collectors("xiaohongshu")
    # per-item spoof (session says web, item is xhs via webbridge-mcp) still caught
    with pytest.raises(capabilities.CollectorPolicyError):
        capabilities.enforce_capture("web", "webbridge-mcp", "search", item_platforms=["xiaohongshu"])


def test_forbidden_collector_is_absolute_across_all_capture_kinds():
    """Regression for the crown-jewel bypass: the forbidden-collector check must fire for EVERY
    capture_kind, not just search-like ones. capture_kind is agent-supplied free text with no enum,
    so if the forbid were gated behind {search,detail,fetch} a capture declaring capture_kind="note"
    (or any off-list value) would no-op the gate and let webbridge-mcp/kimi-webbridge scrape XHS."""
    for bad in ("webbridge-mcp", "kimi-webbridge", "browser"):
        for kind in ("search", "detail", "fetch", "note", "favorites", "likes", "web_page", "", "x"):
            with pytest.raises(capabilities.CollectorPolicyError):
                capabilities.validate_collector("xiaohongshu", bad, capture_kind=kind)
            # per-item spoof under a non-search kind is caught too
            with pytest.raises(capabilities.CollectorPolicyError):
                capabilities.enforce_capture("web", bad, kind, item_platforms=["小红书"])
    # meanwhile the REQUIRED-collector rule stays search-only: a non-search intake needn't declare one
    capabilities.validate_collector("x", None, capture_kind="note")        # required skipped off-search
    capabilities.validate_collector("web", None, capture_kind="web_page")  # non-search web intake ok
    capabilities.validate_collector("xiaohongshu", "xiaohongshu-mcp", capture_kind="detail")  # allowed


def test_forbidden_collector_is_case_insensitive():
    """Collector names are a lowercase controlled vocabulary; a forbidden browser bridge must be caught
    regardless of case (else "Kimi-Webbridge"/"WEBBRIDGE-MCP" slips past the case-sensitive membership
    test). The XHS source name is already alias+case-normalized via canonical(); the collector must be
    case-folded too on both the value and the policy list."""
    for src in ("xiaohongshu", "小红书", "XHS", "RedNote", "RED"):  # source normalization (+red alias)
        for bad in ("Kimi-Webbridge", "KIMI-WEBBRIDGE", "kimi-Webbridge", "Browser", "BROWSER",
                    "WebBridge-MCP", "WEBBRIDGE-MCP", "  Kimi-Webbridge  "):
            for kind in ("search", "note", "favorites"):
                with pytest.raises(capabilities.CollectorPolicyError):
                    capabilities.validate_collector(src, bad, capture_kind=kind)
    # a case-variant of the ALLOWED collector still passes (case-fold is symmetric, not a new block)
    capabilities.validate_collector("xiaohongshu", "Xiaohongshu-MCP", capture_kind="search")
    capabilities.validate_collector("x", "WebBridge-MCP", capture_kind="search")


def test_xhs_forbid_fails_closed_on_off_list_source_spellings():
    """The crown-jewel forbid must not be dodgeable by spelling Xiaohongshu with an id that isn't in
    _ALIASES: the real domain www.xiaohongshu.com, traditional 小紅書, 小红书APP/网. canonical() fails
    CLOSED via XHS-exclusive stem containment, so these resolve to xiaohongshu and hit the forbid."""
    for spelling in ("www.xiaohongshu.com", "XIAOHONGSHU.COM", "小紅書", "小红书APP", "小红书网",
                     "https://www.xiaohongshu.com/explore/abc"):
        assert capabilities.canonical(spelling) == "xiaohongshu"
        with pytest.raises(capabilities.CollectorPolicyError):
            capabilities.validate_collector(spelling, "kimi-webbridge", capture_kind="note")
        # per-item spoof: session=web, item is an off-list XHS spelling via a browser bridge
        with pytest.raises(capabilities.CollectorPolicyError):
            capabilities.enforce_capture("web", "webbridge-mcp", "note", item_platforms=[spelling])
    # stems are XHS-exclusive → legit sources are NOT swept up
    for legit in ("web", "x", "douyin", "manual", "wechat", "web_search"):
        assert capabilities.canonical(legit) != "xiaohongshu"


# ── the static registry lint gate ────────────────────────────────────────────
def test_search_provider_registry_gate_passes():
    name, ok, problems = gates.lint_search_provider_registry()
    assert name == "search_provider_registry"
    assert ok, f"registry gate failed: {problems}"
    assert gates.lint_search_provider_registry in gates.ALL_GATES


def test_webbridge_mcp_registry_gate_passes_and_is_wired():
    name, ok, problems = gates.lint_webbridge_mcp_registry()
    assert name == "webbridge_mcp_registry"
    assert ok, f"webbridge-mcp registry gate failed: {problems}"
    assert gates.lint_webbridge_mcp_registry in gates.ALL_GATES
    # the registration is real: .mcp.json declares webbridge-mcp on the :18061 proxy port
    servers = json.loads((REPO / ".mcp.json").read_text(encoding="utf-8"))["mcpServers"]
    assert "18061" in servers["webbridge-mcp"]["url"]
    # and the Go source tree the registration points at exists (not a dangling reference)
    src = REPO / "tools" / "social_mcp" / "webbridge_mcp"
    for f in ("main.go", "server.go", "proxy.go", "tools.go", "go.mod"):
        assert (src / f).is_file(), f"missing webbridge-mcp source: {f}"


# ── the new methodology docs are present and cross-referenced ────────────────
def test_new_methodology_docs_present():
    web_doc = METHOD / "web_search_provider_playbook.md"
    social_doc = METHOD / "social_access_playbook.md"
    assert web_doc.is_file() and social_doc.is_file()
    wtext = web_doc.read_text(encoding="utf-8")
    assert "fallback_chain" in wtext and "multi-search-engine" in wtext
    stext = social_doc.read_text(encoding="utf-8")
    # the sub-agent reachability ruling (why MCP not skill) must be captured
    assert "子 agent" in stext and "kimi-webbridge" in stext
