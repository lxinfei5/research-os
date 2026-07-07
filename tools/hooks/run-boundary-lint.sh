#!/usr/bin/env bash
set -euo pipefail
ROOT="${GROK_WORKSPACE_ROOT:-${CLAUDE_PROJECT_DIR:-$(pwd)}}"
STAMP="${TMPDIR:-/tmp}/ros-lint-hook.ts"
NOW=$(date +%s)
if [ -f "$STAMP" ]; then
  LAST=$(cat "$STAMP" 2>/dev/null || echo 0)
  if [ "$((NOW - LAST))" -lt 3 ]; then
    exit 0
  fi
fi
LOCKDIR="${TMPDIR:-/tmp}/ros-lint-hook.lock.d"
if ! mkdir "$LOCKDIR" 2>/dev/null; then
  exit 0
fi
trap 'rmdir "$LOCKDIR" 2>/dev/null || true' EXIT
echo "$NOW" > "$STAMP"
cd "$ROOT"
PYTHONPATH="$ROOT" python3 -m ros lint
