---
name: researchos-condense
description: Run the ResearchOS condense pipeline (source → L3 → L2 → L1 → L0) for a topic and regenerate its world model. Use after capturing/promoting new sources, or when asked to "condense"/"grow" a topic's knowledge.
---

# ResearchOS — Condense

`ros condense <slug>` runs three map-reduce stages over the topic's `knowledge.db`. Each stage's
AGENT step is an isolated `claude -p` call that reads a versioned methodology protocol + ONE unit
payload and emits strict JSON; Python does the deterministic MAP (build units) and REDUCE (gated
write). Resumable via per-unit `.out.json`; a staleness guard re-derives L2/L1/L0 when L3 changed.

| stage | unit | protocol | produces |
|-------|------|----------|----------|
| distill | one un-distilled `source_ref` | `l3_distill_protocol.md` | L3 claim (+ credibility) |
| aggregate | one facet's L3 claims | `l2_aggregate_protocol.md` | corroborated L2 findings |
| synthesize | the whole topic's L2 | `l1l0_synthesize_protocol.md` | L1 viewpoints + L0 worldview + open questions |

## Run

```bash
ros condense <slug>                 # full chain (distill → aggregate → synthesize) + staleness guard
ros condense <slug> --stage distill # a single stage
ros report  <slug>                  # regenerate reports/world_model.md from the DB
```

## When you ARE the agent (a unit prompt)

You will receive a methodology protocol followed by `TASK PAYLOAD: {...}`. Output ONLY the strict
JSON object the protocol specifies — no prose, no code fences. Honor the iron rules in
`knowledge_layering.md`:
- one source → one L3; proposition is the POINT, not a truncation;
- you decide which items corroborate — Python counts; you never supply corroboration counts;
- every row carries a credibility verdict (`credibility_guide.md`); echo chamber → flag it;
- only cite ids present in the payload; preserve contradictions (`conflict_note` / contrarian L1).

## Offline / testing

Set `ROS_AGENT_CMD` to a command that reads the unit payload (path in `ROS_AGENT_IN`, stage in
`ROS_AGENT_STAGE`) and prints canned JSON — the pipeline runs deterministically without `claude`.
