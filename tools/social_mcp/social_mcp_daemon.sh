#!/usr/bin/env bash
# social_mcp_daemon.sh — process manager for ResearchOS social-media MCP servers.
#
# Owns:
#   xiaohongshu-mcp  :18060  external Go binary (~/Documents/Xiaohongshu/rednote-mcp).
#                            UNFENCED residual (not in the sibling webbridge-mcp fence).
#                            cwd must be that repo (cookies.json is relative).
#
# Does NOT own:
#   webbridge-mcp    :18061  fenced user-level runtime (launchd or ~/.webbridge-mcp).
#                            This script health-checks only. It never builds, nohup, or
#                            kill-9 whoever is on :18061 (that used to displace the fence
#                            with the retired in-tree copy under webbridge_mcp/).
#   Kimi WebBridge   :10086  Kimi app. Health-check only. Never start/stop. Never curl /command.
#
# X / 抖音 ride mcp__webbridge-mcp__* against the user's real Chrome (the fenced :18061
# proxy). Sub-agents do not inherit skills; they need the MCP tool names.
#
# State (pids/logs for xhs only) under $ROS_SOCIAL_HOME (default ~/.researchos/social_mcp).
#
# Usage:
#   ./tools/social_mcp/social_mcp_daemon.sh start-all      # start xhs; check :18061 (do not launch it)
#   ./tools/social_mcp/social_mcp_daemon.sh stop-all       # stop xhs only (never :18061 / :10086)
#   ./tools/social_mcp/social_mcp_daemon.sh status
#   ./tools/social_mcp/social_mcp_daemon.sh health-check
#   ./tools/social_mcp/social_mcp_daemon.sh start|stop|restart|logs  xiaohongshu-mcp
#   ./tools/social_mcp/social_mcp_daemon.sh cleanup        # reap rod-Chrome orphans (xiaohongshu-mcp)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# ---- state dirs (outside the repo) ----
SOCIAL_HOME="${SOCIAL_MCP_HOME:-${ROS_SOCIAL_HOME:-$HOME/.researchos/social_mcp}}"
LOG_DIR="$SOCIAL_HOME/logs"
PID_DIR="$SOCIAL_HOME/pids"
mkdir -p "$LOG_DIR" "$PID_DIR"

# ---- Kimi WebBridge daemon (dependency, health-check only) ----
WEBBRIDGE_URL="${SOCIAL_MCP_KIMI_URL:-${ROS_WEBBRIDGE_URL:-http://127.0.0.1:${SOCIAL_MCP_KIMI_PORT:-10086}}}"
WEBBRIDGE_STATUS_URL="${WEBBRIDGE_URL%/}/status"
WEBBRIDGE_PORT="${SOCIAL_MCP_KIMI_PORT:-10086}"
WEBBRIDGE_START_HINT="kimi-webbridge start"

# ---- xiaohongshu-mcp (external Go binary; cwd is a hard dependency) ----
XHS_MCP_DIR="${SOCIAL_MCP_XHS_REPO:-${ROS_XHS_MCP_DIR:-$HOME/Documents/Xiaohongshu/rednote-mcp}}"
if [ -n "${SOCIAL_MCP_XHS_BIN:-}" ]; then
	XHS_MCP_BIN="$SOCIAL_MCP_XHS_BIN"
elif [ -n "${ROS_XHS_MCP_BIN:-}" ]; then
	XHS_MCP_BIN="$ROS_XHS_MCP_BIN"
elif [ -x "$XHS_MCP_DIR/bin/xhs-mcp" ]; then
	XHS_MCP_BIN="$XHS_MCP_DIR/bin/xhs-mcp"
else
	XHS_MCP_BIN="$XHS_MCP_DIR/xiaohongshu-mcp-darwin-arm64"
fi
XHS_MCP_PORT="${SOCIAL_MCP_XHS_PORT:-18060}"
XHS_MCP_PID_FILE="$PID_DIR/xiaohongshu-mcp.pid"
XHS_MCP_LOG="$LOG_DIR/xiaohongshu-mcp.log"

# ---- webbridge-mcp (fenced user-level runtime; this script does not own the process) ----
WBMCP_PORT="${SOCIAL_MCP_WEBBRIDGE_MCP_PORT:-18061}"
WBMCP_START_HINT="${HOME}/.webbridge-mcp/daemon.sh start"

# ---- output helpers ----
if [ -t 1 ]; then RED=$'\033[0;31m'; GREEN=$'\033[0;32m'; YELLOW=$'\033[1;33m'; NC=$'\033[0m'; else RED=; GREEN=; YELLOW=; NC=; fi
log_info()  { echo "${GREEN}[INFO]${NC}  $*"; }
log_warn()  { echo "${YELLOW}[WARN]${NC}  $*"; }
log_error() { echo "${RED}[ERROR]${NC} $*" >&2; }

port_pid() { lsof -nP -iTCP:"$1" -sTCP:LISTEN -t 2>/dev/null | head -1; }

# Stop a server THIS SCRIPT started (pid-file). Never SIGKILL a foreign listener
# (launchd / ~/.webbridge-mcp may own :18061).
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
	if [ -n "$ppid" ]; then
		if [ "$stopped" = 1 ]; then
			log_warn "$name :$port still listening (pid $ppid) after stopping our pid-file process — not killing (may be launchd)"
		else
			log_warn "$name :$port is listening (pid $ppid) but was not started by this script — not killing (may be launchd)"
		fi
	elif [ "$stopped" = 1 ]; then
		log_info "$name stopped"
	else
		log_info "$name was not running"
	fi
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

# ---- webbridge-mcp: never compile or launch the retired in-tree copy ----
refuse_in_tree_webbridge() {
	log_error "webbridge-mcp is not owned by ResearchOS. The in-tree Go under tools/social_mcp/webbridge_mcp is RETIRED (unfenced)."
	log_error "Start the fenced runtime: $WBMCP_START_HINT"
	log_error "If launchd owns it: launchctl bootstrap gui/\$(id -u) ~/Library/LaunchAgents/webbridge-mcp.plist"
	return 1
}
build_webbridge_mcp() { refuse_in_tree_webbridge; }

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

# ---- webbridge-mcp (health-check only; never bind :18061 from this tree) ----
start_wbmcp() {
	if [ -n "$(port_pid "$WBMCP_PORT" || true)" ]; then
		log_info "webbridge-mcp already listening on :$WBMCP_PORT (user-level / launchd — this script did not start it)"
		return 0
	fi
	log_error "webbridge-mcp not listening on :$WBMCP_PORT"
	refuse_in_tree_webbridge
}
stop_wbmcp() {
	log_error "Refusing to stop webbridge-mcp — this script does not own :$WBMCP_PORT (launchd / ~/.webbridge-mcp)."
	log_error "Stop with: $HOME/.webbridge-mcp/daemon.sh stop   or   launchctl bootout gui/\$(id -u)/webbridge-mcp"
	return 1
}

# ---- rod-Chrome orphan cleanup (xiaohongshu-mcp uses rod; argv-scoped, never touches real Chrome) ----
# SessionEnd hook calls tools/hooks/cleanup-social-mcp.sh → this cleanup path. Reap directly by the canonical argv token. This only
# kills Chrome processes whose argv contains 'rod/user-data' — the user's real Chrome, kimi-webbridge,
# and chrome-devtools-mcp profiles never carry that token. See fetch-matrix.md §四·6.
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
	_row "xiaohongshu-mcp" "$XHS_MCP_PORT" "(managed — UNFENCED residual)"
	_row "webbridge-mcp"   "$WBMCP_PORT"   "(fenced user-level — health-check only, NOT managed)"
	_row "Kimi WebBridge"  "$WEBBRIDGE_PORT" "(dependency — health-check only, NOT managed; never curl /command)"
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
		webbridge-mcp)
			log_error "webbridge-mcp logs are not in this repo. launchd: /tmp/webbridge-mcp.log  daemon.sh: ~/.webbridge-mcp/logs/"
			return 1 ;;
		*) echo "Usage: $0 logs xiaohongshu-mcp"; return 1 ;;
	esac
}

# ---- main ----
cmd="${1:-status}"; arg="${2:-}"
case "$cmd" in
	start-all)
		log_info "Starting xiaohongshu-mcp; checking fenced webbridge-mcp (:$WBMCP_PORT) and Kimi (:$WEBBRIDGE_PORT)..."
		check_webbridge || log_warn "Kimi :$WEBBRIDGE_PORT unhealthy — fenced :$WBMCP_PORT will error until the extension is up."
		start_xhs_mcp || true
		start_wbmcp || log_warn "webbridge-mcp :$WBMCP_PORT down — start it with: $WBMCP_START_HINT"
		echo; show_status ;;
	stop-all)
		log_info "Stopping managed xiaohongshu-mcp (leaving :$WBMCP_PORT and :$WEBBRIDGE_PORT untouched)..."
		stop_xhs_mcp
		cleanup_rod ;;
	status)        show_status ;;
	health-check)  health_check ;;
	build)         build_webbridge_mcp ;;
	start)
		case "$arg" in
			xiaohongshu-mcp) start_xhs_mcp ;;
			webbridge-mcp)   start_wbmcp ;;
			all)             start_xhs_mcp; start_wbmcp || true ;;
			*) echo "Usage: $0 start {xiaohongshu-mcp|webbridge-mcp|all}"; exit 1 ;;
		esac ;;
	stop)
		case "$arg" in
			xiaohongshu-mcp) stop_xhs_mcp ;;
			webbridge-mcp)   stop_wbmcp ;;
			all)             stop_xhs_mcp; cleanup_rod ;;
			*) echo "Usage: $0 stop {xiaohongshu-mcp|webbridge-mcp|all}"; exit 1 ;;
		esac ;;
	restart)
		case "$arg" in
			xiaohongshu-mcp) stop_xhs_mcp; sleep 1; start_xhs_mcp ;;
			webbridge-mcp)   stop_wbmcp ;;
			*) echo "Usage: $0 restart xiaohongshu-mcp"; exit 1 ;;
		esac ;;
	logs)     show_logs "$arg" ;;
	cleanup)  cleanup_rod ;;
	*)
		cat <<EOF
Usage: $0 {start-all|stop-all|status|health-check|start|stop|restart|logs|cleanup} [name]

Managed (this script): xiaohongshu-mcp (:$XHS_MCP_PORT) — UNFENCED residual
Not managed:           webbridge-mcp (:$WBMCP_PORT, fenced user-level) ; Kimi (:$WEBBRIDGE_PORT)
Start fenced webbridge: $WBMCP_START_HINT
State dir: $SOCIAL_HOME  (override with ROS_SOCIAL_HOME)
EOF
		;;
esac
