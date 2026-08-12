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

**break_condition:** main answer driven by a single unreplicated class with no residual called out.
