# Repositioning plan (v0.2)

## Product first principle

ResearchOS is **not** a scraper kit and **not** a “find the one true answer” engine.

It is a **portable research *capability*** for coding agents:

> Actively discover multi-source evidence → corroborate enough to act → traverse logical space with first principles → emit a structured solution to the user’s problem.

Closest intellectual shape: **ReAct-style agent loops** (reason ↔ act with tools) plus **surveyor-style logical-space discipline** (coverage before local polish). Information channels are interchangeable; **thinking shape is the product**.

## Two product cores

### A. Half-life knowledge (L0–L3) — memory design

| Band | Layers | Practice |
|---|---|---|
| Stable | L0 · L1 | Maintain in topic KB |
| Fast | L2 · L3 | Live fetch; external cache only |

Owner: `pillars/half-life/THESIS.md` · skill `researchos-condense`.

### B. Four behavioral pillars (non-negotiable)

| # | Pillar | Owner file |
|---|---|---|
| 1 | **Multi-source corroboration** — e.g. ternary “2 of 3” (artifact / interface / live observation) | `pillars/corroboration/THESIS.md` |
| 2 | **Active discovery** — agent must hunt evidence; silence is failure | `pillars/discovery/THESIS.md` |
| 3 | **Logical space + first principles** — cover axes, name main contradiction, anti-corruption | `pillars/thinking/THESIS.md` |
| 4 | **Structured output** — first-principle answer first; templates serve the main knife | `pillars/output/THESIS.md` |

## Fetch philosophy (deliberately thin)

- **Primary:** browser use (read real pages, multi-site).
  - Codex / agents with native browser → use that.
  - Others → fenced `mcp__webbridge-mcp__*` on `127.0.0.1:18061` (not the kimi-webbridge skill / not `:10086`).
- **Optional:** dedicated search APIs / MCP (X search, etc.) when present.
- **Degradation:** `pillars/discovery/fetch-matrix.md` — same evidence semantics under fallback; loud `UNKNOWN`.

We do **not** ship platform-specific anti-bot runbooks as core product.

## Example domain

**Travel planning** — classic research that is *not* solved by stockpile encyclopedias: multi-source user complaints vs ratings, first-principle “what weekend problem are we solving?”, structured plan output. See `pillars/examples/travel.md` + `researchos-travel` skill.

## Delete / demote

| Was | Now |
|---|---|
| Heavy XHS/social pacing playbooks | Removed from core; optional local notes only |
| Browser / multi-engine as the product | **Source-agnostic** channels the user trusts; multi-angle corroboration is the product; browser/API are optional adapters |
| Personal corpora | Already stripped |

## Success for a fresh clone

1. Open `AGENTS.md` + `README.md` in any coding agent.  
2. Copy `topics/_templates/topic` → new slug.  
3. Run grow with browser-capable runtime.  
4. Get a card with corroboration table + first-principle answer + residuals.
