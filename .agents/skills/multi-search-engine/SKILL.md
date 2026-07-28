---
name: multi-search-engine
description: |
  ResearchOS Tier-3 web-search fallback — quota-free public-web search by scraping search-engine
  result pages directly with the runtime's built-in fetch tool. 17 engines (CN + Global), no API key,
  no quota, no login. Use when zhipu web-search-prime + runtime WebSearch are both exhausted/unavailable,
  or when a high-value query needs cross-engine diversity. Results normalize into a `ros capture` payload
  with a full fallback_chain audit. Topic-agnostic (works for any ResearchOS topic).
metadata:
  researchos_role: "search_fallback"
  provider_tier: 3
  quota_free: true
  source: "ported from AStockOS .agents/skills/multi-search-engine (adapted for ResearchOS)"
---

# Multi Search Engine — ResearchOS Tier-3 quota-free fallback

Quota-free public-web search by scraping search-engine result pages directly via the runtime's
built-in fetch tool (`WebFetch` in Claude Code). **No API key, no quota, no login, no paid service** —
this is what makes it the ultimate fallback when metered providers run dry.

**Iron rule (ResearchOS):** Python never fetches. *You* (the agent) `WebFetch` these URLs, read the
HTML, and hand normalized items back through `ros capture`. Python only gates the collector + records.

## Where this sits — the web search fallback chain

Full chain + failure-signal matrix + capture shape:
`control_plane/reasoning/methodology/web_search_provider_playbook.md`. In short:

| Tier | Search provider | Tool | Quota |
|------|-----------------|------|-------|
| 1 | zhipu MCP | `mcp__web-search-prime__web_search_prime` | API-key gated |
| 2 | Runtime built-in | `WebSearch` | Runtime quota |
| **3** | **this skill** | `WebFetch` → engine result URLs | **quota-free** |

You land here when Tier 1 (zhipu 429/402/5xx or no `ZHIPU_API_KEY`) **and** Tier 2 (`WebSearch`
unavailable / 0 results) both failed — or when the caller explicitly wants multi-engine cross-checking.
Before executing, read `quota_status` from earlier attempts this session:
- `quota_status.zhipu_search == "exhausted"` → skip the Tier-1 retry, start here.
- `quota_status.zhipu_reader == "exhausted"` → read result URLs with `WebFetch`, not zhipu `web-reader`.

## Workflow

1. **Prepare.** Start an empty in-memory cookie store. Cookies are acquired dynamically **only** when
   a request is denied (403/429) — never preloaded.
2. **Language routing.** Chinese query → domestic engines (Baidu, Bing CN, 360, Sogou, WeChat,
   Toutiao). Non-Chinese → international (Google, Google HK, DuckDuckGo, Yahoo, Startpage, Brave,
   Ecosia, Qwant). Mixed/geopolitics → one of each side for cross-check.
3. **Pick 3–4 engines** best matched to the query (see table below).
4. **Controlled fetch.** `WebFetch` each engine's result URL (query in the `{keyword}` slot,
   standard URL-encoded), **1–2 s between requests**, batches of 3–4, honour robots.txt. On 403/429:
   fetch that engine's **homepage** for a fresh session cookie, **retry once**, then give up on it.
5. **Aggregate.** Deduplicate across engines **by URL first**, then extract title + URL + snippet into
   `ros capture` items.

## Engine selection (topic-agnostic)

| Query kind | Engines | Notes |
|------------|---------|-------|
| Chinese news / current affairs | Baidu + Toutiao + Sogou | Toutiao for breaking/real-time |
| Policy / macro / official | Baidu + Sogou + WeChat + Bing INT | WeChat = 公众号 深度分析 (unique — no other engine) |
| Tech / industry deep-dive | Baidu + Bing CN + Bing INT + Google HK | bilingual coverage |
| International / geopolitics | Google + Google HK + DuckDuckGo + Bing INT | English-language sources |
| Niche communities | Jisilu (低风险投资) etc. | community content absent elsewhere |
| Privacy-sensitive | DuckDuckGo + Startpage | no tracking |
| Facts / units / conversion | WolframAlpha | computed answers |

**Engine registry:** `config.json` (17 engines) is the machine-readable audit source for
`engines_attempted`. Bing CN vs INT share the host `cn.bing.com` (`ensearch=0` Chinese / `ensearch=1`
English).

## Operators & filters

| Operator | Example | Meaning |
|----------|---------|---------|
| `site:` | `site:reuters.com sanctions` | within a site |
| `filetype:` | `filetype:pdf 白皮书` | file type |
| `"…"` | `"固态电池"` | exact phrase (URL-encode `%22`) |
| `-` | `新能源 -汽车` | exclude term |
| `OR` | `降息 OR 降准` | either term |

Time filters are **not portable** across engines: Google `tbs=qdr:d/w/m/y`, Brave `tf=pw`, Startpage
`time=week`. Use each engine's own syntax; don't assume Google's works everywhere.

```
# Chinese news
WebFetch: https://www.baidu.com/s?wd=乌克兰 停火 谈判 2026
# 公众号 deep analysis (unique to WeChat/sogou)
WebFetch: https://wx.sogou.com/weixin?type=2&query=大模型 后训练 RLHF
# bilingual industry
WebFetch: https://cn.bing.com/search?q=HBM memory supply chain&ensearch=1
# international, past week
WebFetch: https://www.google.com/search?q=Russia Ukraine frontline&tbs=qdr:w
# site-scoped
WebFetch: https://www.baidu.com/s?wd=site:gov.cn 人工智能 备案
```

## Output contract — hand results to `ros capture`

Search-engine HTML is **unstructured snippets**, so every item is a **clue, not evidence**:
`source_kind: "search_result"` + `needs_review: true`. It becomes promotable only after you `WebFetch`
the target URL and confirm the content (then `source_kind` → `web_page`/`article`, `capture_kind: fetch`).

```json
{
  "query": "...",
  "source": "web",
  "collector": "multi-search-engine",
  "capture_kind": "search",
  "result_count": 6,
  "items": [
    {"platform": "web", "source_kind": "search_result", "needs_review": true,
     "url": "https://…", "title": "…", "content": "<agent-extracted snippet / key points>"}
  ],
  "raw_tool_status": {
    "provider_id": "multi_search_engine", "fetch_tool": "WebFetch", "actual_runtime": "claude_code",
    "fallback_chain": [
      {"tier": 1, "provider": "web-search-prime", "status": "quota_exhausted", "error": "429"},
      {"tier": 2, "provider": "WebSearch", "status": "failed", "error": "0 results"},
      {"tier": 3, "provider": "multi-search-engine", "status": "partial"}
    ],
    "quota_status": {"zhipu_search": "exhausted", "zhipu_reader": "available"},
    "engines_attempted": ["Baidu", "Bing CN", "Sogou"],
    "engines_succeeded": ["Baidu", "Bing CN"],
    "engines_failed": {"Sogou": "403 anti-bot"}
  }
}
```

**All engines fail → never drop silently.** The intake gate (`ros/storage/intake.py::record_capture`)
rejects only a SILENT empty capture — `items: []` **with** a `degraded_reason` is a legal "loud empty
slot". Record the fail-visibly in either legal shape: (a) `items: []` + `degraded_reason` on the
session, or (b) **one url-less placeholder item** carrying `restricted_reason`. Never an empty array
WITHOUT `degraded_reason` (that silent drop is exactly what this guards against). Keep `degraded_reason`
on the session and the full `fallback_chain` + `engines_attempted` + `engines_failed` in `raw_tool_status`.
A url-less item stays raw-only (the promote URL-gate never lifts it) — evidence of the failure, not a lead.

```json
{"query": "...", "source": "web", "collector": "multi-search-engine", "capture_kind": "search",
 "result_count": 0, "degraded_reason": "all_search_engines_failed",
 "items": [{"platform": "web", "source_kind": "search_result", "needs_review": true,
            "restricted_reason": "all_search_engines_failed",
            "content": "All Tier-3 engines failed; no candidates (see raw_tool_status.fallback_chain)."}],
 "raw_tool_status": {"engines_attempted": ["Baidu","Bing CN"], "engines_succeeded": [],
                     "engines_failed": {"Baidu": "403", "Bing CN": "captcha"}, "fallback_chain": [/*…*/]}}
```

## Ethics & cookie discipline

- **Cookies live in memory only** — fetched on-demand on 403/429, never written to disk / config / git,
  cleared when the session ends. Only session cookies from the engine's own domain.
- **Rate limit:** 1–2 s between requests, batches of 3–4, respect robots.txt. This is legitimate
  research retrieval, not mass scraping.
- **Results are leads.** Cross-engine ranking is noise — never trust an engine's order as importance.
  Confirm anything load-bearing by fetching the real page.
