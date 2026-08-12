---
name: example-travel
display_name: Example domain — travel planning
status: canonical
---

# Example · Travel as research capability

## Why travel

Travel planning is a **commercial research problem** that **stockpile encyclopedias don’t solve**:

- Evidence rots weekly (closures, price, crowds).  
- Platform ratings are gameable; **recent multi-source complaints** matter.  
- The user has a **problem** (“relaxed weekend under 3h drive”), not a need for the global ranking of all restaurants.

ResearchOS posture: **enough multi-source truth to act** + first-principle plan — not “figure out the ultimate truth of Huizhou cuisine.”

---

## Half-life (don’t mix)

| Travel fact | Layer practice |
|---|---|
| “This valley is a 2.5h drive corridor from the city” (structure) | L1-ish — slow; OK to maintain in topic KB |
| “Restaurant X open until 22:00 **today**” | **Live / L3** — re-check; never L0 |
| “Visa-free for passport P this year” | L2 or live — policy can flip |
| Trip *logic* (rest vs photos vs kids) | L1 purpose structure + read-time plan |

See `pillars/half-life/THESIS.md`.

## Map the four pillars

| Pillar | Travel instantiation |
|---|---|
| Corroboration | Official listing (B) + recent user reviews on ≥2 apps (C) + photo/menu artifact (A) — 2 of 3 before “bookable pick” |
| Discovery | Browser-open maps, booking pages, review threads — not one blog listicle |
| Thinking | End purpose = restful weekend / family / budget; main contradiction e.g. *drive time vs. quiet*; cover axes: stay / eat / move / weather / backup |
| Output | Day-by-day plan + map + why these picks + residuals (unverified hours) |

---

## Minimal output skeleton

1. Trip purpose (one sentence)  
2. Main tradeoff  
3. Day plan (time blocks)  
4. Eat / stay / move picks with corroboration tags  
5. Backup branch if weather/crowd fails  
6. UNKNOWN (hours not checked live, etc.)  

Skill handbook: `.agents/skills/researchos-travel/SKILL.md`.

---

## What not to optimize

- Exhaustive city wikis  
- Scrape-anti-bot specialization as core OSS surface  
- Fake precision (“best restaurant #1 globally”) without classes of evidence  
