---
name: knowledge-layering
display_name: Knowledge half-life (L0–L3)
status: canonical
as_of: 2026-08-12
role: product-thesis
---

# Knowledge half-life · L0–L3

> **Product thesis (core innovation):** Knowledge should be split by **how fast it changes** (sustainability / half-life) — **not** by “how true,” “how important,” or bull/bear direction.  
> That split decides **what belongs in an AI knowledge base** vs **what must be re-fetched outside**.

This is the worldview behind **Condense** (L3→L2→L1→L0) and topic files.  
L0–L3 are **markdown headings only** — not schemas, IDs, or engines.

---

## The claim

| Band | Layers | Change tempo (rule of thumb) | Where it should live |
|---|---|---|---|
| **Stable** | **L0 · L1** | Decade / multi-year · year-scale (or slower) | **Maintain inside** the topic knowledge base |
| **Fast** | **L2 · L3** | Week / month (or faster) | **Prefer live external gather** each session; if you must cache, cache **outside** the durable KB (session capture, CDN, vendor API) — **not** as fake-stable L0/L1 |

**Experimental stance we stand by:** treating “stable vs fast” as the primary axis produced better agent research systems than stuffing everything into one undifferentiated memory or one giant RAG blob.

---

## Layer definitions

| Layer | Half-life intent | What it is | Maintain in KB? |
|---|---|---|---|
| **L0** | Near-constant / multi-year | Topic **world model** — identity of the subject world, almost never rewritten | **Yes** — rare, careful updates |
| **L1** | Slow (year-scale, structural) | **Viewpoints / structure** — slow maps, stable relationships, slow-moving macro shape | **Yes** — human-reviewed when possible |
| **L2** | Medium-fast (weeks–months), **multi-source** | **Corroborated** time-bound facts (independence required) | **Selective** — only if still useful as dated memory with `valid_until`; never pretend timeless |
| **L3** | Fast / single-shot | **One source → one claim** (distilled proposition, not a text clip) | **Ephemeral bias** — intake / trail; promote or let expire; don’t promote to L0/L1 without half-life check |

### Concrete intuition (examples)

| Example | Likely layer | Why |
|---|---|---|
| How many countries exist; long-run geopolitical *structure* of a region | L0 / L1 | Changes rarely or slowly |
| Political *relationship pattern* between two regions (bloc logic) | L1 | Year-scale; structure over headlines |
| A country’s GDP *order of magnitude* or policy regime class | L1 (maybe L2 if mid-cycle) | More durable than tomorrow’s print; not eternal |
| Visa-free status this quarter | L2 (or live L3→check) | Can flip with policy notices |
| Today’s weather / today’s spot price | **Do not park as L0/L1** | Session-live; external fetch |

---

## What L0123 is *not*

| Wrong axis | Don’t use L for… |
|---|---|
| Truth / accuracy | S/A/B/C confidence lives in corroboration + output — orthogonal to L |
| Bullish / bearish | Directional schemes are read-time (`floor-output`), not a layer |
| “Importance” | An urgent fact can still be L3 (single source, fast) |
| Schema / enum / promote engine | Headings + human/agent judgment only |

---

## Operating rules (condense + store)

1. **Classify by half-life first** before writing into `knowledge.md`.  
2. **L0/L1 are expensive** — only write what you are willing to maintain; wrong L0 is long-lived poison.  
3. **L3 = one claim from one source** — proposition, not a truncated paste (`l3_distill_protocol.md`).  
4. **L2 requires multi-source corroboration** — independence rules in `floor-corroboration.md`. Count ≠ quality (echo chambers inflate counts).  
5. **Conflicts stay visible** — don’t silent-average; note tension in L2/L1.  
6. **L0 open questions** drive the *next* discovery cycle (prime).  
7. **Fast facts:** default path is **external gather** (`floor-discovery` + `fetch-matrix`). Internal store only with explicit `as-of` / `valid_until`, never as world-model filler.  
8. **If cost forces cache:** put cache in **captures / external store / vendor**, not by promoting weather into L0.
9. **Invalidate, don't delete** — a superseded/corrected entry is closed (`status: superseded` + `superseded_by` + `as_of`), never erased; newer wins by default, point-in-time survives. Demotion is the pair of promotion. Volatility classes + convention: `corpus.md`.

---

## Condense direction (abstraction up, half-life up)

```
external page / capture
        ↓ distill
      L3  (single-source claim, fast)
        ↓ corroborate
      L2  (multi-source, still time-bound)
        ↓ synthesize (slow structure only)
      L1  (stable viewpoint / structure)
        ↓ rare crystallization
      L0  (world model)
```

**Promotion is guilty by default:** only move L2→L1/L0 when the claim’s half-life truly matches.  
Protocols: `l3_distill_protocol.md` · `l2_aggregate_protocol.md` · `l1l0_synthesize_protocol.md`.

---

## break_condition

- Fast-changing operational numbers stored as L0 “forever true”  
- L3 used as a dump of raw article text  
- L2 labeled “corroborated” from a single repost graph  
- Building a promote engine / L-enum schema “to be safe”  
- Hard-deleting a superseded/corrected entry instead of closing its validity window  

---

## Pointers

| Topic | File |
|---|---|
| Write triad / merge / stale | `corpus.md` |
| Independence / 2-of-N | `../corroboration/THESIS.md` |
| Live gather | `../discovery/THESIS.md` · `../discovery/fetch-matrix.md` |
| Skill | `.agents/skills/researchos-condense/SKILL.md` |
