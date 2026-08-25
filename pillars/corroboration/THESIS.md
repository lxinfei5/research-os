---
name: floor-corroboration
display_name: Multi-source corroboration
status: canonical
---

# Pillar 1 · Multi-source corroboration

## L0

A claim becomes **work-true** (safe enough to drive the main answer) when **independent evidence classes** agree — not when one loud source repeats itself.

You do **not** need a complete reconstruction of absolute truth. You need **enough independent support to act** on the user’s problem.

---

## Ternary pattern (portable “2 of 3”)

Industrial / product research often has three *classes* (rename per domain):

| Class | Meaning | Examples |
|---|---|---|
| **A · Artifact** | Frozen human-made artifact | Code, PR, design doc, menu photo, brochure PDF |
| **B · Interface / contract** | What a system *claims* via an API or formal surface | IVK/SDK response, OpenAPI, booking page price, official FAQ |
| **C · Live observation** | What happens in the wild now | Logs, prod DB sample, user reviews this week, on-site photo dated today |

**Rule of thumb:** **any 2 of {A, B, C}** aligned → treat as work-true for action, with confidence marked.  
**Only 1 class** → clue / hypothesis, not main-driver alone.  
**Conflict across classes** → explicit residual; do not silently average.

This is the same *shape* as “code + IVK + online observation” in engineering forensics — domain labels change; **independence of class** does not.

---

## Independence (what counts as a second source)

| Counts as independent | Does not |
|---|---|
| Different *class* (A vs B vs C) | Same post rewritten by three accounts |
| Different *platform mechanism* (filing vs street photo) | Screenshot of the same official page |
| Different *time* if regime may have changed | Pure repost graph |

### Independence test — trace the ancestry (isnad check)

Volume never counts. Before counting 2-of-N, trace each chain **to its upstream origin**. Two chains that bottom out in the same page, wire story, scraper, dataset, or search-rank cascade are **ONE class**, not two.

Ask of every claim:
1. **Who observed it first?** (the primary, not the loudest repeater)
2. **Do my sources share that upstream?** (same wire / same scraped page / same training-data origin)
3. **Could one contamination hit all of them at once?** If yes → correlated noise, one class.

Named failure: two "independent-looking" pages converging on identical content usually means a single shared origin, not corroboration.

### Minority protection

Never settle by bare majority — agreement measures typicality, not truth.

- Make first passes **fully independent** before any cross-exposure (don't let sources see each other first).
- An **unrefuted minority** argument outweighs a conforming majority; carry it as a residual until refuted.
- Anonymize positions when comparing, so frequency can't be weighted as authority.

---

## Street / soft sources

Soft multi-source may upgrade when:

1. Independent multi-source (not pure echo)  
2. Mechanism is retellable  
3. Partial hard anchor exists (money path, primary snippet, live observation)  
4. Falsifiable detail  

Otherwise stay **clue**. Never fake-official (“company confirmed”) on street-only.

---

## Material obligation

Depth cards include a **corroboration table**:

| Claim | Class A | Class B | Class C | Status | Residual |
|---|---|---|---|---|---|
| … | hit/miss | … | … | work-true / clue / conflict | … |

**break_condition:**
- main answer driven by a single unreplicated class with no residual called out.
- two sources counted as independent that share one upstream origin (same wire / scraper / page) — false corroboration.
- a conforming majority silently outvoting an unrefuted minority.
