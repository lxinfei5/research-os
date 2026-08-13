# Pillars · product innovations

Each subdirectory is **one innovation** — single owner, no cross-copy of method bodies.

| # | Folder | Innovation | Entry |
|---|---|---|---|
| 1 | [`half-life/`](./half-life/) | **Knowledge half-life (L0–L3)** — stable in KB, fast live | [`THESIS.md`](./half-life/THESIS.md) |
| 2 | [`corroboration/`](./corroboration/) | **Multi-source corroboration** — 2-of-N classes to *act* | [`THESIS.md`](./corroboration/THESIS.md) |
| 3 | [`discovery/`](./discovery/) | **Active discovery** on user-trusted channels (source-agnostic fetch matrix) | [`THESIS.md`](./discovery/THESIS.md) |
| 4 | [`thinking/`](./thinking/) | **Logical space + first principles** | [`THESIS.md`](./thinking/THESIS.md) |
| 5 | [`output/`](./output/) | **Problem-shaped output** — user surface first; audit behind | [`THESIS.md`](./output/THESIS.md) |

**North star (not a sixth pillar):** lowest cognitive load to *act* — [`../AGENTS.md`](../AGENTS.md) §0 · [`output/THESIS.md`](./output/THESIS.md) · plan [`../docs/LOW_BURDEN.md`](../docs/LOW_BURDEN.md).

Examples (not a sixth pillar): [`examples/`](./examples/) — travel, incident, [before/after](./examples/before-after.md).

## Constraint (keep the tree clean)

- **New method content** → only under the matching `pillars/<name>/`.  
- **Do not** grow a parallel copy under `rules/` (stubs only).  
- **Skills** (`.agents/skills/`) execute pillars; they do not redefine them.  
- **Topics** store *instance* knowledge, not method theses.  
- **Tools** are adapters (browser bridge), not innovations.

## Runtime loop (how pillars compose)

```
Prime (half-life L0/L1)
  → Discover (user-trusted multi-source + fetch-matrix)
  → Capture
  → Condense (half-life climb L3→L0 + multi-angle corroboration)
  → Think (thinking)
  → Emit (output)
```

**Not browser-first:** any trusted channel is valid; corroboration is the product claim.

Skill orchestration: `researchos-grow` · `researchos-condense` · `researchos-search`.
