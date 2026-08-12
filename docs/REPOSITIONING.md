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

Owner: `rules/knowledge_layering.md` · skill `researchos-condense`.

### B. Four behavioral pillars (non-negotiable)

| # | Pillar | Owner file |
|---|---|---|
| 1 | **Multi-source corroboration** — e.g. ternary “2 of 3” (artifact / interface / live observation) | `rules/floor-corroboration.md` |
| 2 | **Active discovery** — agent must hunt evidence; silence is failure | `rules/floor-discovery.md` |
| 3 | **Logical space + first principles** — cover axes, name main contradiction, anti-corruption | `rules/floor-thinking.md` |
| 4 | **Structured output** — first-principle answer first; templates serve the main knife | `rules/floor-output.md` |

## Fetch philosophy (deliberately thin)

- **Primary:** browser use (read real pages, multi-site).
  - Codex / agents with native browser → use that.
  - Others → Kimi WebBridge skill and/or `webbridge-mcp` (loopback).
- **Optional:** dedicated search APIs / MCP (X search, etc.) when present.
- **Degradation:** `rules/fetch-matrix.md` — same evidence semantics under fallback; loud `UNKNOWN`.

We do **not** ship platform-specific anti-bot runbooks as core product.

## Example domain

**Travel planning** — classic research that is *not* solved by stockpile encyclopedias: multi-source user complaints vs ratings, first-principle “what weekend problem are we solving?”, structured plan output. See `rules/examples/travel.md` + `researchos-travel` skill.

## Delete / demote

| Was | Now |
|---|---|
| Heavy XHS/social pacing playbooks | Removed from core; optional local notes only |
| Zhipu / multi-engine as default | Browser-first; multi-engine optional residual |
| Personal corpora | Already stripped |

## Success for a fresh clone

1. Open `AGENTS.md` + `README.md` in any coding agent.  
2. Copy `topics/_templates/topic` → new slug.  
3. Run grow with browser-capable runtime.  
4. Get a card with corroboration table + first-principle answer + residuals.
