# Architecture (v0.2)

## Product

Research **capability** for coding agents: four pillars + browser-first evidence + topic markdown.

## Core loop

Prime → Discover (browser) → Capture → Corroborate/Distill → Think → Emit

## Planes

| Path | Role |
|---|---|
| `rules/floor-*.md` | Pillars + corpus + fetch |
| `rules/examples/` | Domain instantiations |
| `topics/` | Isolated world knowledge |
| `.agents/skills/` | Executable handbooks |
| `tools/social_mcp/` | Optional non-Codex browser adapter |

## Non-goals

Scrape specialization, analysis DB, personal corpora, “ultimate truth” engines.
