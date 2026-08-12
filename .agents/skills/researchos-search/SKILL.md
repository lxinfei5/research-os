---
name: researchos-search
description: >
  Source-agnostic evidence gathering for ResearchOS. Use whatever channels the
  user trusts (APIs, browser, files, briefings, library). Multi-angle coverage
  matters more than any single transport.
---

# ResearchOS · Search / fetch (source-agnostic)

## Goal

Get **multi-source evidence the user trusts**, then feed **corroboration** — not maximize one tool (browser, SERP, or API).

## Principle

| Do | Don’t |
|---|---|
| Ask / infer which sources the user trusts for this task | Assume “must use browser” |
| Prefer **independent classes** (artifact / interface / live) | Stack three reposts of one article |
| Mark failed channels `UNKNOWN + degraded_reason` | Invent data from a dead channel |

Full matrix: `pillars/discovery/fetch-matrix.md`.  
Corroboration: `pillars/corroboration/THESIS.md`.

## Optional adapters (examples)

| If available and user-trusted | Use for |
|---|---|
| Domain APIs / MCP | Structured primary data |
| Native WebSearch / WebFetch | Clues → then open or call primary |
| Codex / other browser tools | Interactive pages when needed |
| kimi-webbridge / webbridge-mcp | Browser when runtime has no native browser |
| User paste / local files | First-class sources |

None of these is required to clone or to run a research loop.

## Procedure

1. From prime brief, list claims to support and **trusted channels** for each.  
2. Gather evidence on those channels (multi-source).  
3. Extract claims with provenance + as-of; label evidence **class**.  
4. On failure: `UNKNOWN + degraded_reason`; continue.  
5. Hand off to corroboration / condense.

## Anti-patterns

- Snippet-only conclusions when body matters  
- Single-source confirmation bias  
- Shipping cookies/tokens into the repo  
- Treating optional tools as hard dependencies  
