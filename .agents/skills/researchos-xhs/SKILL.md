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

XHS anti-bot is **progressive**: empty results → internal errors (EOF) → QR wall. Be restrained
*before* the wall, not after. Full protocol: `source_health_and_degradation.md`.

- **Verify alive the right way**: `ros xhs status` (MCP handshake). Never judge liveness by a bare
  `curl` — a `405 Method Not Allowed` *means the server is up* (streamable-HTTP rejects bare GET);
  only connection-refused/timeout means it's down.
- **First success is scarce**: after one working `search_feeds`, parse + record high-value ids/tokens
  — don't immediately fire a second search. Re-searching often returns empty (a pre-风控 signal).
- **❌ Anti-pattern (real pitfall): re-running `search_feeds` just to "re-parse structured output."**
  The first response JSON **already contains each feed's `xsecToken`** (camelCase) — you already hold
  the tokens, no need to search again. Futile re-searches pushed the session into 风控 (empty→EOF→QR
  wall), so `get_feed_detail` got nothing. **Correct sequence: one successful search → parse
  xsec_token from *that* JSON → immediately call `get_feed_detail` for the 1–3 highest-value notes.
  Never re-search.** "Re-run search to get structured output" is a non-need.
- **Detail budget to top items only**: `get_feed_detail` triggers 风控 faster than search. Take
  detail for just 1–3 highest-interaction notes, serial, 5–8s apart. Never bulk.
- **Empty result ≠ no data**: a 2nd search returning empty/less than the 1st is a warning — don't
  keep swapping keywords; lower frequency or switch sources (X/抖音→web) for that facet.
- Never navigate a bare `/explore/{noteId}` (QR wall). Reach detail via `xsec_token` through MCP.
- **Any** internal-error / EOF / "not available" / QR text → **STOP this source, do not retry**
  (retry invalidates the user's login session).
- **Walled ≠ lost evidence**: list cards (title + interactions + id + xsec_token) are valid B-class
  evidence. Capture with `restricted_reason` + `needs_review`, mark body as todo. Never fall back to
  the browser for detail.
- After use, clean up rod Chrome orphans: `pkill -f 'rod/user-data'`.

## Capture

Normalize hits into a capture payload with `source:"xiaohongshu"`, `collector:"xiaohongshu-mcp"`,
OCR any image-heavy notes to text first, then `ros capture <file.json> --topic <slug>`.
