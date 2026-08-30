# Retired — do not build or start this tree

This directory used to ship a ResearchOS-local `webbridge-mcp` that proxied
Kimi WebBridge (`:10086`) without the later security hardening.

**The fenced runtime is the sibling / user-level binary, not this folder.**

| Live | Path |
|---|---|
| Source of truth | sibling module `github.com/lxinfei/webbridge-mcp` |
| Typical checkout | `~/.webbridge-mcp/` |
| Listen | `127.0.0.1:18061` (loopback only) |
| Supervisor | launchd `webbridge-mcp` or `~/.webbridge-mcp/daemon.sh` |

That runtime wraps snapshot/evaluate in `<untrusted_content>`, gates
`evaluate` / `cdp` / `upload`, audits to jsonl, and exposes a gated
`POST /command`. The Go that used to live here did none of that.

ResearchOS `tools/social_mcp/social_mcp_daemon.sh` **refuses** to compile,
`nohup`, or `kill` `:18061`. If the port is down, start the fenced binary:

```bash
~/.webbridge-mcp/daemon.sh start
# or, if launchd owns it:
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/webbridge-mcp.plist
```

Do **not** `curl http://127.0.0.1:10086/command` from agents. Sub-agents
must use `mcp__webbridge-mcp__*` on `:18061/mcp`. A skill does not
propagate to spawned agents and has no fence.
