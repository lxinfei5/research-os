#!/usr/bin/env bash
set -euo pipefail
ROOT="${GROK_WORKSPACE_ROOT:-${CLAUDE_PROJECT_DIR:-$(pwd)}}"
bash "$ROOT/tools/social_mcp/social_mcp_daemon.sh" cleanup 2>/dev/null || true
