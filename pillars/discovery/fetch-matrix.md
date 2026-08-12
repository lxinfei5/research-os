---
name: fetch-matrix
display_name: Fetch matrix (source-agnostic channels)
status: canonical
---

# Fetch matrix · trusted channels, stable semantics

## First principle

**End purpose:** obtain the evidence the task needs from **channels the user trusts**, with **stable evidence semantics** when tools change.  
Tool success ≠ research success.

**Main contradiction:** wrong *channel semantics* (e.g. treating a search snippet as live observation) make stronger tools more completely wrong.

**Not browser-first.** Browser is **one optional adapter** among many. The product claim is **multi-angle corroboration on user-trusted sources** — API, browser, local files, paid data, user briefing, library — whatever the human allows and trusts.

---

## Semantic channels (stable names)

| Channel | Means | Not |
|---|---|---|
| **Primary document / API** | Filings, official pages, structured APIs, SDK/IVK responses | Unverified repost of the same doc |
| **Browser / interactive surface** | Real page/app state when needed | Snippet-only SERP as proof of body |
| **Search clue** | Engine results / titles as *leads* | Proof of page content |
| **User-trusted private** | Briefings, exports, login-walled surfaces the user opens | Agent inventing private data |
| **Library** | Prior `knowledge/` / `library/` with as-of | “Live coverage” without dates |

Channels are **pluggable**. Enable what the user has; degrade loudly on the rest.

---

## How to choose (not a fixed ranking)

```
Need evidence?
│
├─ What sources does the user trust for this claim?
│     → Prefer those channels first (API, files, vendor, browser, …)
│
├─ Need independent *classes* for corroboration?
│     → Open a second class (artifact / interface / live), not a second repost
│
├─ Channel missing / failed?
│     → UNKNOWN + degraded_reason; continue with remaining trusted channels
│
└─ Never invent a source the user did not authorize
```

### Optional adapters (examples, not requirements)

| Runtime / tool | Role |
|---|---|
| Native WebSearch / WebFetch | Clues → then open or call primary if needed |
| Codex / other native browser | Interactive pages when the user wants browser use |
| kimi-webbridge / webbridge-mcp | Browser when the runtime has no native browser |
| Domain APIs / MCP (X, market data, …) | When installed and user-trusted |
| User paste / local files | First-class if the user supplies them |

**Security:** if using webbridge, bind **loopback only** — it can re-expose a real login session.

---

## Hard rails

1. Snippet ≠ body when the claim depends on full content.  
2. Fallback must not relabel evidence class (search clue ≠ live observation).  
3. Loud failure endpoints (`UNKNOWN + degraded_reason`).  
4. No secrets in repo (cookies, tokens).  
5. **User trust boundary** — do not expand into untrusted or unauthorized surfaces.

---

## Core clone path

**Agent + pillars + whatever sources the user trusts.**  
No particular browser, search vendor, or API is required to start.
