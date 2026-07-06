package main

import (
	"net/url"
	"strings"
)

// xhsDeniedHosts mirrors capabilities.XHS_HOST_STEMS in ros/search/capabilities.py — the
// crown-jewel Xiaohongshu domain set. webbridge-mcp is the ONLY component that sees the real
// navigate URL independent of agent-declared source/platform labels (the capture gate inspects
// only DECLARED values, so a relabeled 'source: web' scrape passes it). The crown-jewel control —
// XHS search/detail MUST go through xiaohongshu-mcp, NEVER a general browser bridge — therefore
// fires HERE, at the transport layer, BEFORE the ban-risky page load reaches the user's REAL
// logged-in Chrome at :10086. Keep this list in sync with the Python XHS_HOST_STEMS (Go and Python
// cannot share source).
var xhsDeniedHosts = []string{"xiaohongshu.com", "xhslink.com", "xhs.cn", "rednote.com", "xhscdn.com"}

// xhsDeniedURL reports whether raw targets a Xiaohongshu origin. Returns the matched host when
// denied so the refusal is specific. Empty/unparseable strings are NOT denied (let the daemon
// judge them) — this guards real navigations, not arbitrary evaluate args.
func xhsDeniedURL(raw string) (string, bool) {
	if raw == "" {
		return "", false
	}
	u, err := url.Parse(raw)
	if err != nil || u.Host == "" {
		return "", false
	}
	h := strings.ToLower(u.Hostname())
	if strings.HasPrefix(h, "www.") {
		h = strings.TrimPrefix(h, "www.")
	}
	for _, stem := range xhsDeniedHosts {
		if h == stem || strings.HasSuffix(h, "."+stem) {
			return h, true
		}
	}
	return "", false
}

// xhsDenyReason is the refusal surfaced to the agent. It explains WHY (account ban risk) so the
// agent routes to xiaohongshu-mcp instead of retrying — the transport gate fires even when the
// caller's prompt omitted the negative XHS constraint (the documented prior failure mode).
const xhsDenyReason = "crown-jewel refusal: Xiaohongshu search/detail must go through " +
	"xiaohongshu-mcp, NEVER a general browser bridge (webbridge-mcp). Driving the real Chrome to " +
	"an XHS origin fingerprints the logged-in session and risks an irreversible account ban — route " +
	"via mcp__xiaohongshu-mcp__search_feeds / get_feed_detail instead"
