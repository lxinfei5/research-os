// webbridge-mcp — a Streamable-HTTP MCP server that fronts the Kimi WebBridge
// daemon (http://127.0.0.1:10086) so ResearchOS workflow sub-agents can drive the
// user's REAL Chrome session via mcp__webbridge-mcp__* tools instead of a skill
// (a skill is advisory prose that does NOT propagate to spawned sub-agents).
//
// It only proxies to :10086 and health-checks it; it never starts/stops that
// daemon (which is owned by the Kimi app). See tools/social_mcp/README.md and
// control_plane/reasoning/methodology/social_access_playbook.md §二.
//
// Ported from AStockOS tools/social_mcp/webbridge_mcp (same daemon protocol).
package main

import (
	"flag"

	"github.com/sirupsen/logrus"
)

func main() {
	// Default binds LOOPBACK only: this server re-exposes the user's REAL logged-in
	// Chrome (evaluate/cdp) — it must never listen on 0.0.0.0. Sub-agents are local,
	// so 127.0.0.1 suffices. Override only with an explicit host:port you trust.
	port := flag.String("port", "127.0.0.1:18061", "MCP server listen address (keep loopback — exposes the real browser)")
	flag.Parse()

	server := NewWebBridgeMCPServer()
	logrus.Infof("webbridge-mcp starting on %s (proxying Kimi WebBridge :10086)", *port)
	if err := server.Start(*port); err != nil {
		logrus.Fatalf("webbridge-mcp exited: %v", err)
	}
}
