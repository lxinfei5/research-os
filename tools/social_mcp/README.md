# tools/social_mcp — optional browser bridge

Optional **loopback MCP** so coding agents **without** native browser tools can drive the user’s real Chrome via Kimi WebBridge.

**Not required by ResearchOS.** The product is multi-angle corroboration on user-trusted sources; browser is only one optional channel (see `pillars/discovery/fetch-matrix.md`).

| Piece | Role |
|---|---|
| `webbridge_mcp/` | Go Streamable-HTTP MCP → proxies `127.0.0.1:10086` |
| `social_mcp_daemon.sh` / `.ps1` | Build/start/status helpers |

## When you need this

| Runtime | Need this? |
|---|---|
| Codex with browser | **No** — use native browser |
| Claude Code / others | **Optional** — or use `kimi-webbridge` skill alone |

## Security

- Default bind **loopback only** (`127.0.0.1`) — re-exposes a real logged-in browser.  
- Never commit cookies.  
- See `pillars/discovery/fetch-matrix.md` for product-level fetch policy.

## Quick

```bash
# see runtime-config.example.env
./tools/social_mcp/social_mcp_daemon.sh status
./tools/social_mcp/social_mcp_daemon.sh build   # webbridge-mcp
```

This directory is an **adapter**, not the research method. The method lives in `rules/floor-*.md`.
