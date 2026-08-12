---
name: researchos-search
description: >
  Browser-first evidence gathering for ResearchOS. Prefer real page reads via
  Codex browser or kimi-webbridge/webbridge-mcp. Search APIs are optional clues only.
---

# ResearchOS · Search / fetch (browser-first)

## Goal

Get **multi-source page-level evidence**, not a stack of SERP titles.

## Routing

| Runtime | Do this |
|---|---|
| **Codex** (or any agent with native browser) | Use native browser tools to open and read pages |
| **Claude Code / Grok / others** | `kimi-webbridge` skill; optional local `webbridge-mcp` on loopback |
| Native WebSearch / WebFetch available | Use for **clues**, then **open** top sources in browser |
| Optional X/API MCP installed | Use as extra channel; never block clone path |

Full matrix: `pillars/discovery/fetch-matrix.md`.

## Procedure

1. From prime brief, list 3–7 **queries / URLs** tied to the thin facet.  
2. Gather **clues** (search) if useful.  
3. **Open** ≥2 independent primary pages (browser).  
4. Extract claims with URL + as-of; note evidence **class** (artifact / interface / live).  
5. On failure: `UNKNOWN + degraded_reason`; do not invent.

## Anti-patterns

- Snippet-only conclusions  
- Single-site confirmation bias  
- Shipping cookies/tokens into the repo  
- Treating optional APIs as hard dependencies  

## Output to grow

Pass structured notes into capture/distill: urls, claims, class labels, residuals.
