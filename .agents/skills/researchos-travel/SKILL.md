---
name: researchos-travel
description: >
  Example domain skill: travel planning as research capability — multi-source
  corroboration, first-principle trip purpose, structured day plan. Not a scrape kit.
---

# ResearchOS · Travel (example domain)

Full rationale: `rules/examples/travel.md`.

## When

User wants a trip plan / weekend drive / “where to eat and stay” that needs **live multi-source** checks.

## Method

1. **Purpose** — one sentence (rest / kids / budget / photos).  
2. **Main contradiction** — e.g. drive time vs quiet.  
3. **Discover** — browser-open maps, booking pages, review apps (**≥2 platforms** for each key pick).  
4. **Corroborate** — 2 of {official listing, recent multi-app reviews, dated photo/menu}.  
5. **Emit** — day plan + picks + backups + UNKNOWN hours (`floor-output`).  

Optional HTML skin: `template.html` (map-friendly). Prefer substance over chrome.

## Do not

- Optimize anti-bot playbooks here  
- Rank “best city ever” without evidence classes  
- Invent opening hours  
