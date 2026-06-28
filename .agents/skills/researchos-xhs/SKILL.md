---
name: researchos-xhs
description: Search Xiaohongshu (小红书) for ResearchOS via the local xiaohongshu-mcp server (the mandatory non-kimi-webbridge path). Use whenever a ResearchOS search needs Xiaohongshu content.
---

# ResearchOS — Xiaohongshu (小红书) via xiaohongshu-mcp

**Hard rule:** XHS search + note detail go through `xiaohongshu-mcp` ONLY. kimi-webbridge / browser
are forbidden for XHS search and the `ros capture` gate will reject them. Full rationale +
anti-detection discipline: `control_plane/reasoning/methodology/xiaohongshu_search_playbook.md`.

## Path

1. Prefer the **native** `xiaohongshu-mcp` MCP tools if the runtime exposes them (`search_feeds`,
   note-detail tools).
2. Otherwise use the **bridge CLI** to the local server (`http://localhost:18060/mcp`):
   ```bash
   ros xhs status                                             # check_login_status
   ros xhs tools                                              # list tools
   ros xhs call --tool search_feeds --args-json '{"keyword":"地缘政治"}'
   ```
   Override the endpoint with `ROS_XHS_MCP_URL`. Loopback-only by default; destructive tools blocked
   unless `--allow-destructive`.

## Discipline

- Never navigate a bare `/explore/{noteId}` (triggers the "open the App / scan QR" wall). Reach
  detail via the `xsec_token` from `search_feeds` results, through MCP.
- Captcha / forced-logout / QR wall → STOP. Do not retry.
- If MCP is unavailable: degrade to list-card evidence with `restricted_reason` + `needs_review`.
  Never fall back to the browser for detail.
- After use, clean up rod Chrome orphans: `pkill -f 'rod/user-data'`.

## Capture

Normalize hits into a capture payload with `source:"xiaohongshu"`, `collector:"xiaohongshu-mcp"`,
OCR any image-heavy notes to text first, then `ros capture <file.json> --topic <slug>`.
