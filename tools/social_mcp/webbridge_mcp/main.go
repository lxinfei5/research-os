// webbridge-mcp — a Streamable-HTTP MCP server that fronts the Kimi WebBridge
// daemon (http://127.0.0.1:10086) so ResearchOS workflow sub-agents can drive the
// user's REAL Chrome session via mcp__webbridge-mcp__* tools instead of a skill
// (a skill is advisory prose that does NOT propagate to spawned sub-agents).
//
// It only proxies to :10086 and health-checks it; it never starts/stops that
// daemon (which is owned by the Kimi app). See tools/social_mcp/README.md and
// control_plane/reasoning/methodology/fetch-matrix.md §二.
//
// Ported from AStockOS tools/social_mcp/webbridge_mcp (same daemon protocol).
package main

import (
	"flag"
	"net"
	"os"
	"strings"

	"github.com/sirupsen/logrus"
)

// isLoopbackAddr reports whether addr binds a loopback interface ONLY. An empty host (":18061")
// means ALL interfaces (0.0.0.0 / [::]) and is rejected — webbridge-mcp re-exposes the user's REAL
// logged-in Chrome (evaluate/cdp), so a non-loopback bind turns a local session-theft vector into a
// remote one (W-05/#32).
func isLoopbackAddr(addr string) bool {
	host := addr
	if h, _, err := net.SplitHostPort(addr); err == nil {
		host = h
	}
	switch host {
	case "localhost", "127.0.0.1", "::1":
		return true
	}
	return false
}

func main() {
	// Default binds LOOPBACK only: this server re-exposes the user's REAL logged-in
	// Chrome (evaluate/cdp) — it must never listen on 0.0.0.0. Sub-agents are local,
	// so 127.0.0.1 suffices.
	defaultPort := strings.TrimSpace(os.Getenv("SOCIAL_MCP_WEBBRIDGE_MCP_ADDR"))
	if defaultPort == "" {
		defaultPort = strings.TrimSpace(os.Getenv("ROS_WEBBRIDGE_MCP_ADDR"))
	}
	if defaultPort == "" {
		defaultPort = "127.0.0.1:18061"
	}
	port := flag.String("port", defaultPort, "MCP server listen address (MUST be loopback — exposes the real browser)")
	flag.Parse()
	if !isLoopbackAddr(*port) {
		logrus.Fatalf("refusing non-loopback bind %q — webbridge-mcp re-exposes the user's REAL logged-in "+
			"Chrome (evaluate/cdp); bind 127.0.0.1 (an empty host ':18061' means 0.0.0.0 and is rejected)", *port)
	}

	server := NewWebBridgeMCPServer()
	logrus.Infof("webbridge-mcp starting on %s (proxying Kimi WebBridge :10086)", *port)
	if err := server.Start(*port); err != nil {
		logrus.Fatalf("webbridge-mcp exited: %v", err)
	}
}
