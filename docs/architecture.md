# Architecture (v0.2)

## Product

Research **capability** for coding agents:

1. **Half-life knowledge (L0–L3)** — what the KB should hold vs re-fetch  
2. **Four behavioral pillars** — corroborate · discover · think · emit  
3. Browser-first evidence + topic markdown  

## Core loop

Prime (L0/L1) → Discover (browser) → Capture → Distill/Condense (half-life climb) → Think → Emit

## Planes

| Path | Role |
|---|---|
| `rules/knowledge_layering.md` | ★ Half-life thesis |
| `rules/floor-*.md` | Behavior pillars + corpus + fetch |
| `rules/l*_*.md` | Condense stage detail |
| `rules/examples/` | Domain instantiations |
| `topics/` | Isolated world knowledge (L0–L3 headings) |
| `.agents/skills/` | grow · condense · search · … |
| `tools/social_mcp/` | Optional non-Codex browser adapter |

## Non-goals

Scrape specialization, analysis DB, personal corpora, “ultimate truth” engines.
