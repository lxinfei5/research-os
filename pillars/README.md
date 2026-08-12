# Pillars · product innovations

Each subdirectory is **one innovation** — single owner, no cross-copy of method bodies.

| # | Folder | Innovation | Entry |
|---|---|---|---|
| 1 | [`half-life/`](./half-life/) | **Knowledge half-life (L0–L3)** — stable in KB, fast live | [`THESIS.md`](./half-life/THESIS.md) |
| 2 | [`corroboration/`](./corroboration/) | **Multi-source corroboration** — 2-of-N classes to *act* | [`THESIS.md`](./corroboration/THESIS.md) |
| 3 | [`discovery/`](./discovery/) | **Active discovery** + browser-first fetch matrix | [`THESIS.md`](./discovery/THESIS.md) |
| 4 | [`thinking/`](./thinking/) | **Logical space + first principles** | [`THESIS.md`](./thinking/THESIS.md) |
| 5 | [`output/`](./output/) | **Problem-shaped structured output** | [`THESIS.md`](./output/THESIS.md) |

Example domain (not a sixth pillar): [`examples/travel.md`](./examples/travel.md).

## Constraint (keep the tree clean)

- **New method content** → only under the matching `pillars/<name>/`.  
- **Do not** grow a parallel copy under `rules/` (stubs only).  
- **Skills** (`.agents/skills/`) execute pillars; they do not redefine them.  
- **Topics** store *instance* knowledge, not method theses.  
- **Tools** are adapters (browser bridge), not innovations.

## Runtime loop (how pillars compose)

```
Prime (half-life L0/L1)
  → Discover (discovery + fetch-matrix)
  → Capture
  → Condense (half-life climb L3→L0 + corroboration)
  → Think (thinking)
  → Emit (output)
```

Skill orchestration: `researchos-grow` · `researchos-condense` · `researchos-search`.
