#!/usr/bin/env bash
# social_mcp_daemon.sh — unified process manager for ResearchOS social-media MCP servers.
#
# Manages exactly two servers, both HTTP MCP:
#   xiaohongshu-mcp  :18060  external Go binary (~/Documents/Xiaohongshu/xiaohongshu-mcp),
#                            MUST run with that dir as cwd (cookies.json is resolved relatively).
#   webbridge-mcp    :18061  this project's Go binary (tools/social_mcp/webbridge_mcp),
#                            fronts the Kimi WebBridge daemon so workflow SUB-AGENTS can reach
#                            X / 抖音 / login-gated web via mcp__webbridge-mcp__* (a skill can't).
#
# The Kimi WebBridge daemon (:10086) is a DEPENDENCY we only HEALTH-CHECK — never start or
# stop it. It is owned by the Kimi app; touching its lifecycle would fight the app.
#
# X access has no dedicated server: X search/read go through webbridge-mcp against the user's
# real Chrome (twscrape / independent x-mcp were rejected in security review — account ban vector
# could not be controlled at acceptable cost; see social_access_playbook.md §四·1). Douyin also
# rides webbridge-mcp (loaded only on explicit request).
#
# State (pids/logs) is collected under $ROS_SOCIAL_HOME (default ~/.researchos/social_mcp),
# NOT inside the repo, so nothing here is git-tracked.
#
# Usage:
#   ./tools/social_mcp/social_mcp_daemon.sh start-all      # build (if needed) + start both MCPs
#   ./tools/social_mcp/social_mcp_daemon.sh stop-all       # stop both MCPs (never touches :10086)
#   ./tools/social_mcp/social_mcp_daemon.sh status         # process + port + binary summary
#   ./tools/social_mcp/social_mcp_daemon.sh health-check   # deep health (ports + WebBridge /status + MCP /health); exit 0 iff all healthy
#   ./tools/social_mcp/social_mcp_daemon.sh build          # go build webbridge-mcp
#   ./tools/social_mcp/social_mcp_daemon.sh start   <name>  # webbridge-mcp | xiaohongshu-mcp
#   ./tools/social_mcp/social_mcp_daemon.sh stop    <name>
#   ./tools/social_mcp/social_mcp_daemon.sh restart <name>
#   ./tools/social_mcp/social_mcp_daemon.sh logs    <name>
#   ./tools/social_mcp/social_mcp_daemon.sh cleanup        # reap rod-Chrome orphans (xiaohongshu-mcp)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# ---- state dirs (outside the repo) ----
SOCIAL_HOME="${ROS_SOCIAL_HOME:-$HOME/.researchos/social_mcp}"
LOG_DIR="$SOCIAL_HOME/logs"
PID_DIR="$SOCIAL_HOME/pids"
mkdir -p "$LOG_DIR" "$PID_DIR"

# ---- Kimi WebBridge daemon (dependency, health-check only) ----
WEBBRIDGE_PORT=10086
WEBBRIDGE_STATUS_URL="http://127.0.0.1:${WEBBRIDGE_PORT}/status"
WEBBRIDGE_START_HINT="$HOME/.kimi-webbridge/bin/kimi-webbridge start"

# ---- xiaohongshu-mcp (external Go binary; cwd is a hard dependency) ----
XHS_MCP_DIR="${ROS_XHS_MCP_DIR:-$HOME/Documents/Xiaohongshu/xiaohongshu-mcp}"
XHS_MCP_BIN="${ROS_XHS_MCP_BIN:-$XHS_MCP_DIR/xiaohongshu-mcp-darwin-arm64}"
XHS_MCP_PORT=18060
XHS_MCP_PID_FILE="$PID_DIR/xiaohongshu-mcp.pid"
XHS_MCP_LOG="$LOG_DIR/xiaohongshu-mcp.log"

# ---- webbridge-mcp (this project) ----
WBMCP_DIR="$SCRIPT_DIR/webbridge_mcp"
WBMCP_BIN="$WBMCP_DIR/webbridge-mcp"
WBMCP_PORT=18061
WBMCP_PID_FILE="$PID_DIR/webbridge-mcp.pid"
WBMCP_LOG="$LOG_DIR/webbridge-mcp.log"

# ---- output helpers ----
if [ -t 1 ]; then RED=$'\033[0;31m'; GREEN=$'\033[0;32m'; YELLOW=$'\033[1;33m'; NC=$'\033[0m'; else RED=; GREEN=; YELLOW=; NC=; fi
log_info()  { echo "${GREEN}[INFO]${NC}  $*"; }
log_warn()  { echo "${YELLOW}[WARN]${NC}  $*"; }
log_error() { echo "${RED}[ERROR]${NC} $*" >&2; }

port_pid() { lsof -nP -iTCP:"$1" -sTCP:LISTEN -t 2>/dev/null | head -1; }

# Stop a server by pid-file, then by port as a fallback. Only used for the two MCPs we own.
stop_owned() {
	local name="$1" port="$2" pid_file="$3"
	local stopped=0
	if [ -f "$pid_file" ]; then
		local pid; pid="$(cat "$pid_file" 2>/dev/null || true)"
		if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
			kill "$pid" 2>/dev/null || true; sleep 0.5
			kill -0 "$pid" 2>/dev/null && kill -9 "$pid" 2>/dev/null || true
			stopped=1
		fi
		rm -f "$pid_file"
	fi
	local ppid; ppid="$(port_pid "$port" || true)"
	if [ -n "$ppid" ]; then kill -9 "$ppid" 2>/dev/null || true; stopped=1; fi
	[ "$stopped" = 1 ] && log_info "$name stopped" || log_info "$name was not running"
}

# ---- WebBridge daemon: health-check ONLY (never start/stop) ----
check_webbridge() {
	local body
	if ! body="$(curl -s --max-time 3 "$WEBBRIDGE_STATUS_URL" 2>/dev/null)"; then
		log_warn "Kimi WebBridge daemon (:$WEBBRIDGE_PORT) unreachable — start it yourself: $WEBBRIDGE_START_HINT"
		log_warn "(this manager never starts/stops :$WEBBRIDGE_PORT — it is owned by the Kimi app)"
		return 1
	fi
	if echo "$body" | grep -q '"extension_connected":true'; then
		log_info "Kimi WebBridge daemon healthy (running + extension connected)"
		return 0
	fi
	log_warn "Kimi WebBridge daemon up but extension NOT connected — commands will fail. Check the Kimi browser extension."
	return 1
}

# ---- build ----
build_webbridge_mcp() {
	command -v go >/dev/null 2>&1 || { log_error "go toolchain not found; cannot build webbridge-mcp"; return 1; }
	log_info "Building webbridge-mcp..."
	( cd "$WBMCP_DIR" && go build -o webbridge-mcp . ) || { log_error "webbridge-mcp build failed"; return 1; }
	log_info "webbridge-mcp built at $WBMCP_BIN"
}

# ---- xiaohongshu-mcp ----
start_xhs_mcp() {
	if [ -n "$(port_pid "$XHS_MCP_PORT" || true)" ]; then log_info "xiaohongshu-mcp already running on :$XHS_MCP_PORT"; return 0; fi
	if [ ! -x "$XHS_MCP_BIN" ]; then log_error "xiaohongshu-mcp binary not found/executable at $XHS_MCP_BIN (set ROS_XHS_MCP_BIN)"; return 1; fi
	log_info "Starting xiaohongshu-mcp on :$XHS_MCP_PORT (cwd=$XHS_MCP_DIR for cookies.json)..."
	( cd "$XHS_MCP_DIR" && nohup "$XHS_MCP_BIN" >> "$XHS_MCP_LOG" 2>&1 & echo $! > "$XHS_MCP_PID_FILE" )
	sleep 2
	if [ -n "$(port_pid "$XHS_MCP_PORT" || true)" ]; then log_info "xiaohongshu-mcp started (pid $(cat "$XHS_MCP_PID_FILE"))"; else log_error "xiaohongshu-mcp failed to start — see $XHS_MCP_LOG"; return 1; fi
}
stop_xhs_mcp() { stop_owned "xiaohongshu-mcp" "$XHS_MCP_PORT" "$XHS_MCP_PID_FILE"; }

# ---- webbridge-mcp ----
start_wbmcp() {
	if [ -n "$(port_pid "$WBMCP_PORT" || true)" ]; then log_info "webbridge-mcp already running on :$WBMCP_PORT"; return 0; fi
	[ -x "$WBMCP_BIN" ] || build_webbridge_mcp || return 1
	log_info "Starting webbridge-mcp on 127.0.0.1:$WBMCP_PORT..."
	# Loopback only — this server re-exposes the user's real logged-in Chrome; never 0.0.0.0.
	nohup "$WBMCP_BIN" -port "127.0.0.1:$WBMCP_PORT" >> "$WBMCP_LOG" 2>&1 &
	echo $! > "$WBMCP_PID_FILE"
	sleep 1.5
	if [ -n "$(port_pid "$WBMCP_PORT" || true)" ]; then log_info "webbridge-mcp started (pid $(cat "$WBMCP_PID_FILE"))"; else log_error "webbridge-mcp failed to start — see $WBMCP_LOG"; return 1; fi
}
stop_wbmcp() { stop_owned "webbridge-mcp" "$WBMCP_PORT" "$WBMCP_PID_FILE"; }

# ---- rod-Chrome orphan cleanup (xiaohongshu-mcp uses rod; argv-scoped, never touches real Chrome) ----
# ResearchOS ships no dedicated reaper hook, so reap directly by the canonical argv token. This only
# kills Chrome processes whose argv contains 'rod/user-data' — the user's real Chrome, kimi-webbridge,
# and chrome-devtools-mcp profiles never carry that token. See social_access_playbook.md §四·6.
cleanup_rod() {
	log_info "Reaping rod-Chrome orphans (pkill -f 'rod/user-data' — argv-scoped, never the real browser)..."
	pkill -f 'rod/user-data' 2>/dev/null || true
}

# ---- status / health ----
show_status() {
	echo "Social MCP status  (state: $SOCIAL_HOME)"
	echo "=================================================="
	_row() {
		local name="$1" port="$2" note="$3"
		local p; p="$(port_pid "$port" || true)"
		if [ -n "$p" ]; then printf "  %-16s :%-6s ${GREEN}RUNNING${NC} (pid %s)  %s\n" "$name" "$port" "$p" "$note"
		else printf "  %-16s :%-6s ${RED}STOPPED${NC}          %s\n" "$name" "$port" "$note"; fi
	}
	_row "xiaohongshu-mcp" "$XHS_MCP_PORT" "(managed)"
	_row "webbridge-mcp"   "$WBMCP_PORT"   "(managed)"
	_row "Kimi WebBridge"  "$WEBBRIDGE_PORT" "(dependency — health-check only, NOT managed)"
	local rod; rod="$(pgrep -f 'rod/user-data' 2>/dev/null | wc -l | tr -d ' ')"
	echo "  rod-Chrome procs: $rod  (>~4 = orphans piling up; run: $0 cleanup)"
}

health_check() {
	local ok=0
	echo "Social MCP deep health-check:"
	# WebBridge dependency
	check_webbridge || ok=1
	# xiaohongshu-mcp: port + MCP /health
	if [ -n "$(port_pid "$XHS_MCP_PORT" || true)" ]; then
		if curl -s --max-time 3 "http://127.0.0.1:$XHS_MCP_PORT/health" >/dev/null 2>&1; then log_info "xiaohongshu-mcp healthy (:$XHS_MCP_PORT /health)"; else log_warn "xiaohongshu-mcp listening but /health not OK"; ok=1; fi
	else log_error "xiaohongshu-mcp not running (:$XHS_MCP_PORT)"; ok=1; fi
	# webbridge-mcp: /health (which itself reflects :10086)
	if [ -n "$(port_pid "$WBMCP_PORT" || true)" ]; then
		if curl -s --max-time 5 "http://127.0.0.1:$WBMCP_PORT/health" | grep -q '"status":"healthy"'; then log_info "webbridge-mcp healthy (:$WBMCP_PORT /health)"; else log_warn "webbridge-mcp listening but degraded (WebBridge daemon/extension?)"; ok=1; fi
	else log_error "webbridge-mcp not running (:$WBMCP_PORT)"; ok=1; fi
	[ "$ok" = 0 ] && echo "${GREEN}All social MCP services healthy${NC}" || echo "${RED}Some services unhealthy${NC}"
	return $ok
}

show_logs() {
	case "${1:-}" in
		xiaohongshu-mcp) tail -f "$XHS_MCP_LOG" ;;
		webbridge-mcp)   tail -f "$WBMCP_LOG" ;;
		*) echo "Usage: $0 logs {xiaohongshu-mcp|webbridge-mcp}"; return 1 ;;
	esac
}

# ---- main ----
cmd="${1:-status}"; arg="${2:-}"
case "$cmd" in
	start-all)
		log_info "Starting social MCP services (WebBridge :10086 is checked, not started)..."
		check_webbridge || log_warn "Continuing without a healthy WebBridge — webbridge-mcp will error until :10086 is up."
		start_xhs_mcp || true
		start_wbmcp || true
		echo; show_status ;;
	stop-all)
		log_info "Stopping managed MCP services (leaving Kimi WebBridge :10086 untouched)..."
		stop_wbmcp
		stop_xhs_mcp
		cleanup_rod ;;
	status)        show_status ;;
	health-check)  health_check ;;
	build)         build_webbridge_mcp ;;
	start)
		case "$arg" in
			xiaohongshu-mcp) start_xhs_mcp ;;
			webbridge-mcp)   start_wbmcp ;;
			all)             start_xhs_mcp; start_wbmcp ;;
			*) echo "Usage: $0 start {xiaohongshu-mcp|webbridge-mcp|all}"; exit 1 ;;
		esac ;;
	stop)
		case "$arg" in
			xiaohongshu-mcp) stop_xhs_mcp ;;
			webbridge-mcp)   stop_wbmcp ;;
			all)             stop_wbmcp; stop_xhs_mcp; cleanup_rod ;;
			*) echo "Usage: $0 stop {xiaohongshu-mcp|webbridge-mcp|all}"; exit 1 ;;
		esac ;;
	restart)
		case "$arg" in
			xiaohongshu-mcp) stop_xhs_mcp; sleep 1; start_xhs_mcp ;;
			webbridge-mcp)   stop_wbmcp;  sleep 1; start_wbmcp ;;
			*) echo "Usage: $0 restart {xiaohongshu-mcp|webbridge-mcp}"; exit 1 ;;
		esac ;;
	logs)     show_logs "$arg" ;;
	cleanup)  cleanup_rod ;;
	*)
		cat <<EOF
Usage: $0 {start-all|stop-all|status|health-check|build|start|stop|restart|logs|cleanup} [name]

Managed servers: xiaohongshu-mcp (:$XHS_MCP_PORT), webbridge-mcp (:$WBMCP_PORT)
Dependency (health-check only, never started/stopped): Kimi WebBridge (:$WEBBRIDGE_PORT)
State dir: $SOCIAL_HOME  (override with ROS_SOCIAL_HOME)
EOF
		;;
esac
