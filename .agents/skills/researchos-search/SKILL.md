---
name: researchos-search
description: Drive a multi-source research search for a ResearchOS topic and capture what you gather. Use when the user wants to search/research a topic across public web + X + Douyin + Xiaohongshu and grow its world knowledge.
---

# ResearchOS — Search (fetch layer, no engine)

You are the FETCH layer. You drive search via the right path per source, transcribe media to text,
and write the raw capture to the topic's `captures/`. There is no `ros capture` gate — you record
what you gathered and the collector you actually used, then condense it into `knowledge.md` per
`rules/`.

## Loop

1. **Resolve topic + prime.** Read `topics/<slug>/knowledge.md` (L0 + L1 + 未决问题 + facet 覆盖)
   to see what the open questions / thin facets ask for. Query those, not the already-established.

2. **Verify each source is ALIVE — the right way — before fetching.** Social sources ride the
   **user's real login**; misjudging liveness wastes the budget. Never judge liveness by a bare
   `curl` status code. Full protocol: `rules/source_health_and_degradation.md`.
   - **XHS MCP** (:18060) → an MCP handshake (a `405` on bare curl means it's *up*; only
     connection-refused/timeout means down). See `researchos-xhs`.
   - **real-Chrome bridge** → `mcp__webbridge-mcp__status` (health-checks :10086;
     `extension_connected=false` means commands fail even if the daemon is up). Main loop may also
     use the `kimi-webbridge` skill: `list_tabs` → `navigate` + `snapshot` to confirm login state.
   - **zhipu** MCP → needs `ZHIPU_API_KEY`; if absent, degrade to runtime `WebSearch`/`WebFetch`.

3. **Fetch per source (respect the path policy):**
   - **web** — a **3-tier fallback chain** (never a single provider). Search: zhipu
     **`web-search-prime`** → runtime **`WebSearch`** → **`multi-search-engine`** (quota-free URL
     scraping, last resort). Fetch full text: zhipu **`web-reader`** → **`WebFetch`** → real-Chrome
     snapshot (`mcp__webbridge-mcp__navigate`+`snapshot` sub-agent, or `kimi-webbridge` main loop) —
     JS/anti-bot/login only. Record `fallback_chain` + `quota_status`. Protocol + failure matrix:
     `rules/web_search_provider_playbook.md`. (collector = the tier that produced items)
   - **x** — real-Chrome bridge on `https://x.com/search?q=<query>` (user's real login;
     virtual-scroll to accumulate tweet ids): `mcp__webbridge-mcp__*` (sub-agent) or `kimi-webbridge`
     (main loop).
   - **douyin** — same bridge on `https://www.douyin.com/search/<query>`; capture the media URL and
     transcribe (`researchos-media`) before capture. (explicit request only)
   > ✅ **`webbridge-mcp` (:18061) is an MCP → it propagates to spawned sub-agents**, so sub-agents
   > drive X/抖音 + login-gated web directly. `kimi-webbridge` is a skill (main-loop only) as the
   > equivalent/fallback — both hit the same real Chrome (:10086). Rulings:
   > `rules/social_access_playbook.md`.
   - **xiaohongshu** — **multi-path**: prefer the real main Chrome (`mcp__webbridge-mcp__*` /
     `kimi-webbridge`); fall back to **`xiaohongshu-mcp`** (`search_feeds`) / `researchos-xhs` on
     anti-bot/EOF. Record the collector actually used. See `rules/xiaohongshu_search_playbook.md`.
   - **风控是渐进式的**（空结果→内部错误→扫码墙）：首次成功后克制、详情配额只给 1–3 条最高价值条目、
     遇任何 EOF/扫码字样立即 STOP 不重试、被墙后列表卡片仍可降级 capture。详见
     `rules/source_health_and_degradation.md`。

4. **Media → text.** Transcribe video, OCR/caption images BEFORE capture (`researchos-media`), so
   cached text is always text.

5. **Capture.** Write the payload to `topics/<slug>/captures/<session>.json`. Each item needs
   `platform`, `source_kind`, `content`, and a real `url` (or a `restricted_reason` if behind a
   wall — those stay raw-only). Record the `collector` actually used. A source that returned nothing
   goes in as `items: []` + `degraded_reason` (a loud empty slot, never a silent one).

   ```json
   {"query":"...", "source":"xiaohongshu", "collector":"xiaohongshu-mcp", "capture_kind":"search",
    "items":[{"platform":"xiaohongshu","source_kind":"note","url":"https://www.xiaohongshu.com/...",
              "title":"...","author":"...","content":"<note text; images already OCR'd>"}]}
   ```

   **First-party / user briefing (no public URL)**: `platform: manual` +
   `source_kind: first_party_empirical* | user_briefing`; reference it as
   `researchos://first-party/<hash>` (protocol `rules/first_party_empirical_playbook.md`).

6. **Condense.** Distill + corroborate the capture into `knowledge.md` per `researchos-condense` and
   `rules/floor-corpus.md` — write the source to `sources/<hash>.md` + one `## 信源索引` line, then
   L3 → L2 → L1 → L0. Refresh `## facet 覆盖` and `topics/_index.yaml`.

## Discipline

- Same-platform serial; 2–5s between actions; ≤10 page visits / 48h lookback per task.
- 风控是渐进式的：**墙出现前就克制**，首次成功后不立刻重搜、详情配额只给最高价值条目。遇任何
  EOF/扫码字样 → STOP，不重试（重试作废登录会话）。完整协议见 `rules/source_health_and_degradation.md`。
- Never invent sources or ids. A url-less item must carry `restricted_reason`.
