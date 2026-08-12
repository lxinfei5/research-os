---
name: researchos-grow
description: >
  Run one ResearchOS growth cycle: prime → discover (browser-first) → capture →
  corroborate/distill → think (logical space) → structured emit → coverage refresh.
  Use when the user wants to grow/deepen/research a topic.
---

# ResearchOS · Grow (one cycle)

Heartbeat of the system. **You** (the agent) execute against `topics/<slug>/knowledge.md`.
No orchestration binary.

## Loop

1. **Prime** — Read L0 + L1 + open questions + facet coverage. Pick *one* thin facet or open question.  
   Don’t re-search settled L0.

2. **Discover (browser-first)** — Follow `rules/floor-discovery.md` + `rules/fetch-matrix.md`:
   - Codex → native browser  
   - Else → kimi-webbridge / webbridge-mcp  
   - Open ≥2 independent sources for claims that will drive the answer  

3. **Capture** — Optional `captures/<session>.json` for replay; always keep provenance.

4. **Corroborate + distill** — `rules/floor-corroboration.md` (2-of-N classes).  
   Write L3 claims with proposition + provenance + valid_until (`floor-corpus`).  
   Condense upward as needed (`researchos-condense`).

5. **Think** — `rules/floor-thinking.md`: end purpose, main contradiction, logical space, counterexamples.

6. **Emit** — User-facing structure per `rules/floor-output.md` (and domain example if any).  
   Refresh `## facet 覆盖` + `topics/_index.yaml`.

## Pillar checklist (before closing)

- [ ] Corroboration table present for main claims  
- [ ] No silent empty channel  
- [ ] Main contradiction named  
- [ ] Residuals loud  
- [ ] Reader can act on the answer  

## Floors

| Pillar | File |
|---|---|
| Corroboration | `rules/floor-corroboration.md` |
| Discovery | `rules/floor-discovery.md` |
| Thinking | `rules/floor-thinking.md` |
| Output | `rules/floor-output.md` |
| Fetch | `rules/fetch-matrix.md` |
