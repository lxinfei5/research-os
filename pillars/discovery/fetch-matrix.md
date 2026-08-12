---
name: fetch-matrix
display_name: Fetch matrix (browser-first)
status: canonical
---

# Fetch matrix · browser-first degradation

## First principle

**End purpose:** obtain the evidence the task needs, with **stable evidence semantics** when tools change.  
Tool success ≠ research success.

**Main contradiction:** wrong *channel semantics* make stronger tools more completely wrong.

---

## Semantic channels (stable names)

| Channel | Means | Not |
|---|---|---|
| **Browser** | Real page/app state via a browser tool | Snippet-only SERP |
| **Search clue** | Engine results / titles as *leads* | Proof of page content |
| **Optional API** | Platform search/API if installed | Required for clone |
| **Library** | Prior `knowledge/` / `library/` | “Live coverage” without as-of |

---

## Default priority (OSS quick path)

```
Need evidence?
│
├─ 1. Browser use
│     ├─ Codex / native browser runtime → use it
│     └─ Else → kimi-webbridge skill and/or webbridge-mcp (loopback)
│
├─ 2. Runtime WebSearch / WebFetch (clues → then browser open)
│
├─ 3. Optional dedicated APIs (X search, etc.) if present
│
└─ Fail → UNKNOWN + degraded_reason; continue other channels
```

### Runtime mapping (recommended)

| Runtime | Browser path |
|---|---|
| Codex | Built-in browser / computer-use as exposed |
| Claude Code / Grok / others | `kimi-webbridge` skill; optional `tools/social_mcp` webbridge-mcp on `127.0.0.1` |
| Headless CI | Expect degraded browser; mark residuals |

**Security:** webbridge re-exposes a real login browser — **loopback only**, never `0.0.0.0` in defaults.

---

## Hard rails

1. Snippet ≠ body — promote claims only after page open when material.  
2. Fallback must not relabel evidence class (search clue ≠ live observation).  
3. Loud failure endpoints.  
4. No secrets in repo (cookies, tokens).

---

## Optional advanced tools

Multi-engine search skills, platform MCPs, paid data — **adapters**, not core.  
Core clone path = **agent + browser + markdown floors**.
