---
name: researchos-condense
description: Condense a topic's new sources into its layered L0–L3 knowledge.md (distill → corroborate → synthesize) and refresh the world model. Use after capturing new sources, or when asked to "condense"/"grow" a topic's knowledge.
---

# ResearchOS — Condense (agent recompute, no map-reduce engine)

There is no `ros condense`. Condensing = YOU the agent reading the topic's new `captures/` +
`sources/` and its current `knowledge.md`, then writing the next state of the L0–L3 ladder directly.
It's one reasoning pass over the doc, not a Python pipeline. Honor the floor rules in
`rules/floor-corpus.md` and the three contracts below.

## The three moves (contracts in `rules/`)

| move | what you do | contract |
|------|-------------|----------|
| **distill** | one new source → one L3 claim. proposition is the POINT, not a truncation; attach a credibility tag (T0–T4 + `[echo]` if a repost-chain) | `rules/l3_distill_protocol.md` |
| **aggregate** | group a facet's L3 claims that say the same thing → corroborated L2 findings; record multi-source / cross-platform counts as a prefix; preserve contradictions as `⚠冲突` | `rules/l2_aggregate_protocol.md` |
| **synthesize** | the topic's L2 → L1 viewpoints + L0 worldview + open questions; close answered 未决问题 | `rules/l1l0_synthesize_protocol.md` |

You decide which items corroborate and what they mean — the counts (多源×N · 跨平台×M) are just
prefix labels you write; they never decide trust (`rules/floor-judgment.md`).

## How to run it (against the file)

1. Read `topics/<slug>/knowledge.md` and the new `captures/<session>.json` + the sources they point
   to (`sources/<hash>.md` → original in `library/sources/<hash>.json`).
2. **Distill** each un-distilled source into an L3 bullet under its facet heading. Write the
   source's provenance to `sources/<hash>.md` + one row in `## 信源索引`.
3. **Aggregate**: within each facet, merge L3s that say the same thing into L2 bullets
   (`**[<T-tag> · 多源×N · 跨平台×M]** …` + provenance line). Keep contradictions visible.
4. **Synthesize**: fold mature L2 into L1 viewpoints; refresh the active **L0** worldview (sink the
   old one to `### archived · [superseded]`); tick off answered 未决问题, add new ones.
5. Apply `rules/floor-corpus.md` discipline throughout: three elements per fact, single owner,
   `[stale since]` not delete, no directional state, platform tag matches url host.
6. Update `## facet 覆盖` and the topic row in `topics/_index.yaml`. Optionally re-render
   `reports/world_model.md` (the human view) and append `reports/sessions/`
   (`rules/report_template.md`).

## Floor reminders

- Proposition is a falsifiable claim, not a verbatim truncation.
- Credibility is your judgment (T0–T4); echo chambers get an `[echo]` note — you decide the level,
  nothing mechanically caps it.
- Directional/verdict state is read-time-only, never persisted.
