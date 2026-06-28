#!/usr/bin/env bash
# ros/run/claude_cmd.sh — the SINGLE SOURCE for "how to invoke claude in headless batch mode".
# Used by ros/run/condense.py's AGENT step (one process per condense unit). Ported from AStockOS
# run/claude_cmd.sh.
#
# Usage: ros/run/claude_cmd.sh "<prompt>"
#
# The prompt is forwarded to `claude -p` after a `--` separator. The separator is REQUIRED because
# skill prompts begin with YAML frontmatter (`---`), which the CLI would otherwise parse as an
# option. (stdin instead of a positional arg hangs and is unsupported.)
#
# This script does NOT reason. It only constructs and executes the claude invocation; all reasoning
# happens in the agent process claude launches.
#
# Env:
#   ROS_MODEL / CLAUDE_MODEL    — pin the model (optional).
#   ROS_AGENT_DRY_RUN=1         — print the constructed command (prompt elided) instead of running.
set -uo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: ros/run/claude_cmd.sh \"<prompt>\"" >&2
  exit 2
fi
prompt="$1"

command -v claude >/dev/null 2>&1 || {
  echo "ResearchOS: claude CLI not found (required for headless condense). Set ROS_AGENT_CMD to a stub for offline runs." >&2
  exit 2
}

model="${ROS_MODEL:-${CLAUDE_MODEL:-}}"
cmd=(claude)
[ -n "$model" ] && cmd+=(--model "$model")
cmd+=(-p -- "$prompt")

if [ "${ROS_AGENT_DRY_RUN:-}" = "1" ]; then
  printf '%s -p -- <prompt>\n' "${cmd[0]}"
  exit 0
fi

exec "${cmd[@]}"
