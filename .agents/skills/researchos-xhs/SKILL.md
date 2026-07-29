---
name: researchos-xhs
description: Search Xiaohongshu (小红书) for ResearchOS. Multi-path — prefer the real main Chrome (webbridge-mcp / kimi-webbridge); fall back to the local xiaohongshu-mcp server on anti-bot/EOF. Use whenever a ResearchOS search needs Xiaohongshu content.
---

# ResearchOS — Xiaohongshu (小红书)

**Path policy (multi-path, aligned with AStockOSV2):** XHS search + note detail PREFER the user's
real main Chrome — `mcp__webbridge-mcp__*` (sub-agent reachable) or the `kimi-webbridge` skill
(main loop). Fall back to the local `xiaohongshu-mcp` server on anti-bot / headless EOF. Use ANY of
these collectors — record the one actually used in the capture. There is no Python gate; the
discipline below is what you self-enforce. Full rationale + anti-detection pacing:
`rules/xiaohongshu_search_playbook.md`.

## Path

1. **Prefer the real main Chrome**: `mcp__webbridge-mcp__navigate`+`snapshot` (sub-agent) or the
   `kimi-webbridge` skill (main loop) on the user's logged-in session.
2. **Fall back to `xiaohongshu-mcp`** when the browser keeps hitting anti-bot/EOF — prefer the
   **native** MCP tools if the runtime exposes them (`search_feeds`, note-detail tools).
3. Otherwise reach the local server directly (`http://localhost:18060/mcp`, streamable-HTTP):
   `check_login_status`, `list tools`, `search_feeds {"keyword":"..."}`. Loopback-only; destructive
   tools stay off. (Endpoint override via `ROS_XHS_MCP_URL`.)

## Discipline

XHS anti-bot is **progressive**: empty results → internal errors (EOF) → QR wall. Be restrained
*before* the wall, not after. Full protocol: `rules/source_health_and_degradation.md`.

- **Verify alive the right way**: an MCP handshake. Never judge liveness by a bare `curl` — a
  `405 Method Not Allowed` *means the server is up* (streamable-HTTP rejects bare GET); only
  connection-refused/timeout means it's down.
- **First success is scarce**: after one working `search_feeds`, parse + record high-value
  ids/tokens — don't immediately fire a second search (re-searching often returns empty, a
  pre-风控 signal).
- **❌ Anti-pattern (real pitfall): re-running `search_feeds` just to "re-parse structured output."**
  The first response JSON **already contains each feed's `xsecToken`** (camelCase) — you already
  hold the tokens. **Correct sequence: one successful search → parse xsec_token from *that* JSON →
  immediately call `get_feed_detail` for the 1–3 highest-value notes. Never re-search.**
- **Detail budget to top items only**: `get_feed_detail` triggers 风控 faster than search. Take
  detail for just 1–3 highest-interaction notes, serial, 5–8s apart. Never bulk.
- **Empty result ≠ no data**: a 2nd search returning empty/less than the 1st is a warning — don't
  keep swapping keywords; lower frequency or switch sources (X/抖音→web) for that facet.
- Never navigate a bare `/explore/{noteId}` (QR wall). Reach detail via `xsec_token` through MCP.
- **Any** internal-error / EOF / "not available" / QR text → **STOP this source, do not retry**
  (retry invalidates the user's login session).
- **Walled ≠ lost evidence**: list cards (title + interactions + id + xsec_token) are valid B-class
  evidence. Capture with `restricted_reason`, mark body as todo. Detail may be retried via the
  main-Chrome path, but never hammer the same note in a short window.
- After use, clean up rod Chrome orphans: `pkill -f 'rod/user-data'`.

## Capture

Normalize hits into a capture payload with `source:"xiaohongshu"`, `collector:` set to the path
ACTUALLY used (`webbridge-mcp` | `kimi-webbridge` | `xiaohongshu-mcp`), written to
`topics/<slug>/captures/<session>.json`. OCR any image-heavy notes to text first
(`researchos-media`), then condense into `knowledge.md` per `researchos-condense`.
