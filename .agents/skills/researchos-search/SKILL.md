---
name: researchos-search
description: Drive a multi-source research search for a ResearchOS topic, then hand captures back to the gated CLI. Use when the user wants to search/research a topic across public web + X + Douyin + Xiaohongshu and grow its world knowledge.
---

# ResearchOS — Search

You are the FETCH layer. Python never fetches; you drive search via the right collector per source,
normalize results, and write them back through `ros capture`. The engine condenses + retains.

## Loop

1. **Resolve topic + plan.** `ros topic open <slug>` to see the current world model + open facets.
   `ros search <slug> "<query>" --source <s>` prints the per-source policy (required collector,
   entry) — treat it as the plan. Prefer querying what the open questions / thin facets ask for.

2. **Verify each source is ALIVE — the right way — before fetching.** Social sources (XHS MCP,
   kimi-webbridge) ride the **user's real login**; misjudging their liveness wastes the search budget.
   Never judge liveness by a bare `curl` status code. See
   `control_plane/reasoning/methodology/source_health_and_degradation.md` for the full protocol:
   - **XHS MCP** (:18060) → `ros xhs status` (MCP handshake). A `405` on bare curl means it's *up*
     (streamable-HTTP rejects GET); only connection-refused/timeout means down.
   - **real-Chrome bridge** → sub-agents/main loop: `mcp__webbridge-mcp__status` (health-checks the
     underlying :10086; `extension_connected=false` means commands fail even if the daemon is up).
     Main loop may also use the `kimi-webbridge` skill: `list_tabs` returns `{"ok":true}` (daemon up),
     then `navigate` + `snapshot` to confirm the target site's login state.
   - **zhipu** MCP → needs `ZHIPU_API_KEY` in `.env`; if absent, degrade to runtime
     `WebSearch`/`WebFetch` this round.

3. **Fetch per source with the READY skills/tools (respect the collector policy):**
   - **web** — a **3-tier fallback chain** (never a single provider). Search: zhipu
     **`web-search-prime`** MCP → runtime **`WebSearch`** → the **`multi-search-engine`** skill
     (quota-free URL scraping — the last-resort fallback when the metered tiers are exhausted).
     Fetch full text: zhipu **`web-reader`** MCP → **`WebFetch`** → real-Chrome snapshot
     (`mcp__webbridge-mcp__navigate`+`snapshot` for sub-agents, or the `kimi-webbridge` skill in the
     main loop) — JS/anti-bot/login pages only. Record the full `fallback_chain` + `quota_status` in
     `raw_tool_status` every search. Full protocol + failure-signal matrix + capture shape:
     `control_plane/reasoning/methodology/web_search_provider_playbook.md`. (collector = the tier
     that produced the items, e.g. `multi-search-engine` / `web-reader` / `webbridge-mcp`)
   - **x** — the real-Chrome bridge on `https://x.com/search?q=<query>` (user's real login;
     virtual-scroll to accumulate tweet ids): `mcp__webbridge-mcp__*` (sub-agent reachable) or the
     `kimi-webbridge` skill (main loop). (collector `webbridge-mcp` or `kimi-webbridge`)
   - **douyin** — same real-Chrome bridge on `https://www.douyin.com/search/<query>`; capture
     the media URL and transcribe (`ros media transcribe`) before capture. (collector `webbridge-mcp`
     or `kimi-webbridge`; explicit request only)
   > ✅ **`webbridge-mcp` (:18061) is an MCP → it DOES propagate to spawned sub-agents**, so workflow
   > sub-agents can drive X/抖音 + login-gated web directly (`mcp__webbridge-mcp__navigate`+`snapshot`,
   > one task-named `session` reused across calls). `kimi-webbridge` stays a **skill (main-loop only)**
   > as the equivalent/fallback — both hit the same real Chrome (:10086). The "main-loop fetch → capture
   > → sub-agent condense" split is still the recommended discipline (replayable intake), just no longer
   > forced. `xiaohongshu-mcp` + zhipu MCPs also propagate. Rulings: `methodology/social_access_playbook.md`.
   - **xiaohongshu** — **multi-path**: prefer the real main Chrome (`mcp__webbridge-mcp__*`,
     sub-agent reachable, or the `kimi-webbridge` skill in the main loop); fall back to the
     **`xiaohongshu-mcp`** MCP (`search_feeds`) / **`researchos-xhs`** skill / `ros xhs` on
     anti-bot/EOF. Record the collector actually used (the gate hard-rejects only an explicit
     forbidden list; XHS has none). See
     `control_plane/reasoning/methodology/xiaohongshu_search_playbook.md`.
   - **风控是渐进式的**（空结果→内部错误→扫码墙）：首次成功后克制、详情配额只给 1–3 条最高价值条目、
     遇任何 EOF/扫码字样立即 STOP 不重试、被墙后列表卡片仍可降级 capture。详见
     `source_health_and_degradation.md`。

4. **Media → text** (Phase 2): transcribe video, OCR/caption images BEFORE capture, so cached text
   is always text.

5. **Capture.** Build a payload and run `ros capture <file.json> --topic <slug> --auto-promote`.
   Each item needs `platform`, `source_kind`, `content`, and a real `url` (or a `restricted_reason`
   if behind a wall — those stay raw-only). Declare the `collector` so the policy gate passes.

   ```json
   {"query":"...", "source":"xiaohongshu", "collector":"xiaohongshu-mcp", "capture_kind":"search",
    "items":[{"platform":"xiaohongshu","source_kind":"note","url":"https://www.xiaohongshu.com/...",
              "title":"...","author":"...","content":"<note text; images already OCR'd>"}]}
   ```

6. **Condense + report.** `ros condense <slug>` (source → L3 → L2 → L1 → L0), then
   `ros report <slug>` to regenerate `world_model.md`. `ros gaps`/`review` (Phase 2) surface what to
   search next — feed that back into step 1.

## Discipline

- Same-platform serial; 2–5s between actions; ≤10 page visits / 48h lookback per task.
- 风控是渐进式的（空结果→内部错误→扫码墙）：**墙出现前就克制**，首次成功后不立刻重搜、详情配额只给
  最高价值条目。遇任何 EOF/扫码字样 → STOP，不重试（重试作废登录会话）。完整协议见
  `source_health_and_degradation.md`。
- Never invent sources or ids. A url-less item must carry `restricted_reason`.
