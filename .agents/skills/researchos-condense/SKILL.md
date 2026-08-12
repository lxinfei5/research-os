---
name: researchos-condense
description: >
  Distill and condense new sources into topic knowledge.md (L3→L2→L1→L0)
  under corroboration and corpus floors. Use after a discovery pass.
---

# ResearchOS · Condense

## Rules

1. **Corpus triad** — every stored fact: proposition + provenance + valid_until (`rules/floor-corpus.md`).  
2. **Corroboration** — multi-source upgrades only per `rules/floor-corroboration.md`.  
3. **Near-duplicate merge** in the same file; don’t parallel-stack the same claim.  
4. **L3** single-source claims → **L2** when independent classes agree → **L1** slow synthesis → **L0** durable world model.  
5. **Never** store directional “buy/book this now” as eternal fact; plans are read-time output (`floor-output`).

## Protocols (detail)

- `rules/l3_distill_protocol.md`  
- `rules/l2_aggregate_protocol.md`  
- `rules/l1l0_synthesize_protocol.md`  

These are **servants** of the four pillars — if they conflict with pillars, pillars win.
