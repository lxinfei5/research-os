"""Locks in the AStockOS search-capability port: the Tier-3 quota-free multi-search-engine skill,
the web 3-tier fallback collector policy (incl. the fetch-Tier-3 browser reader), the static
registry lint gate, and XHS multi-path allow-list (browser + mcp).

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


# ── X / 抖音 preferred collectors (soft gate: off-list warns, does not raise) ──
def test_x_and_douyin_soft_preferred_collectors():
    for src in ("x", "douyin"):
        assert capabilities.validate_collector(src, "kimi-webbridge", capture_kind="search") == []
        for off in ("xiaohongshu-mcp", "browser", "multi-search-engine"):
            warns = capabilities.validate_collector(src, off, capture_kind="search")
            assert warns and "preferred" in warns[0]
        # missing → warn, not raise
        warns_miss = capabilities.validate_collector(src, None, capture_kind="search")
        assert warns_miss
    # alias 抖音
    assert capabilities.validate_collector("抖音", "xiaohongshu-mcp", capture_kind="search")


# ── XHS multi-path: real Chrome + mcp (AStockOSV2-aligned) ───────────────────
def test_xiaohongshu_allows_browser_and_mcp():
    for ok in ("webbridge-mcp", "kimi-webbridge", "xiaohongshu-mcp"):
        assert capabilities.validate_collector("xiaohongshu", ok, capture_kind="search") == []
        assert capabilities.validate_collector("小红书", ok, capture_kind="search") == []
    assert not capabilities.forbidden_collectors("xiaohongshu")
    # per-item XHS with browser collector is allowed
    assert not capabilities.enforce_capture(
        "web", "kimi-webbridge", "search", item_platforms=["xiaohongshu"])
    # off-list name → soft warn only
    warns = capabilities.validate_collector("xiaohongshu", "browser", capture_kind="search")
    assert warns and "soft gate" in warns[0]


# ── webbridge-mcp: the sub-agent-reachable real-Chrome transport ─────────────
def test_webbridge_mcp_is_an_allowed_peer_for_x_douyin_xhs_and_web():
    for src in ("x", "douyin", "xiaohongshu"):
        capabilities.validate_collector(src, "webbridge-mcp", capture_kind="search")
        capabilities.validate_collector(src, "kimi-webbridge", capture_kind="search")
    assert "webbridge-mcp" in capabilities.required_collectors("抖音")
    assert "webbridge-mcp" in capabilities.required_collectors("xiaohongshu")
    for src in ("web", "web_search"):
        capabilities.validate_collector(src, "webbridge-mcp", capture_kind="fetch")
        assert "webbridge-mcp" in capabilities.required_collectors(src)


def test_xhs_collector_case_insensitive_allow():
    """Allow-list collectors are case-folded; variants of allowed paths still pass."""
    for src in ("xiaohongshu", "小红书", "XHS", "RedNote", "RED"):
        for coll in ("WebBridge-MCP", "Kimi-Webbridge", "Xiaohongshu-MCP", "  WEBBRIDGE-MCP  "):
            capabilities.validate_collector(src, coll, capture_kind="search")
    capabilities.validate_collector("x", "WebBridge-MCP", capture_kind="search")


def test_xhs_canonical_off_list_spellings_still_resolve():
    """canonical() still maps domain / traditional / APP spellings to xiaohongshu (label honesty)."""
    for spelling in ("www.xiaohongshu.com", "XIAOHONGSHU.COM", "小紅書", "小红书APP", "小红书网",
                     "https://www.xiaohongshu.com/explore/abc"):
        assert capabilities.canonical(spelling) == "xiaohongshu"
        # browser path accepted under those spellings
        capabilities.validate_collector(spelling, "kimi-webbridge", capture_kind="search")
        capabilities.enforce_capture("web", "webbridge-mcp", "search", item_platforms=[spelling])
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
