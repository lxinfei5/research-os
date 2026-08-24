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

ResearchOS posture: **enough multi-source truth to act** + a **one-glance plan** — not “figure out the ultimate truth of Huizhou cuisine,” and not a city wiki the user must reread in human.

---

## Half-life (don’t mix)

| Travel fact | Layer practice |
|---|---|
| “This valley is a 2.5h drive corridor from the city” (structure) | L1-ish — slow; OK to maintain in topic KB |
| “Restaurant X open until 22:00 **today**” | **Live / L3** — re-check; never L0 |
| “Visa-free for passport P this year” | L2 or live — policy can flip |
| Trip *logic* (rest vs photos vs kids) | L1 purpose structure + read-time plan |

See `pillars/half-life/THESIS.md`.

## Map the pillars

| Pillar | Travel instantiation |
|---|---|
| Corroboration | Official listing (B) + recent user reviews on ≥2 apps (C) + photo/menu artifact (A) — 2 of 3 before “bookable pick” |
| Discovery | Browser-open maps, booking pages, review threads — not one blog listicle |
| Thinking | End purpose = restful weekend / family / budget; main contradiction e.g. *drive time vs. quiet*; cover axes: stay / eat / move / weather / backup |
| Output | **User surface:** go / don’t go + day skeleton + one flip. Audit: 2-of-3 tags, hours, sources |

---

## User-surface skeleton (default)

Each first-screen line must say why it *is* the act (or the one flip). See [`README.md`](./README.md).

1. **Act** — go or don’t; where to sleep (one line). *This is the act.*  
2. **Why this, not that** — e.g. drive vs quiet. *This is why that stay, not the other.*  
3. **Hold** — 1–3 reasons that change the booking. *Not a city tour.*  
4. **Flip** — e.g. hours not checked live → confirm before pay. *Only if it would change the act.*  
5. Day blocks only if they **are** the act (the weekend plan), not a guidebook.

Audit (on request): 2-of-3 tags per pick, full backups, source list.  

Skill handbook: `.agents/skills/researchos-travel/SKILL.md`.  
Host sketch (not the method): [`../../demo/travel/`](../../demo/travel/).

---

## What not to optimize

- Exhaustive city wikis  
- Scrape-anti-bot specialization as core OSS surface  
- Fake precision (“best restaurant #1 globally”) without classes of evidence  
