---
name: floor-corpus
display_name: Knowledge write discipline
status: canonical
---

# Knowledge write discipline

## L0

`topics/*/knowledge.md` stores **falsifiable objective facts** for reuse.  
Plans and “do this now” schemes are **read-time** (`floor-output`), not eternal facts.

**What may live here long-term is governed by half-life** — sole thesis:  
→ **`THESIS.md`** (L0/L1 stable in KB · L2/L3 prefer live / external cache).

---

## Write triad

1. **proposition** — full falsifiable sentence  
2. **provenance** — URL/author/time (or capture id)  
3. **valid_until** — natural life; “forever” is not valid  

## Merge & stale

- Near-duplicate (same subject+predicate) → **merge**, don’t parallel stack  
- Past valid_until → `[stale since YYYY-MM-DD]`, keep for history  
- Untagged ≠ fresh  

### Invalidate, don’t delete (bi-temporal)

A superseded or corrected fact is **closed, not erased** — this is the demotion path
promotion ("guilty by default") never provided. Newer information **wins by default**,
but the old entry stays so point-in-time questions and the audit trail survive.

Annotate inline (or in frontmatter where the topic uses it); never hard-delete:

```
status: superseded        # active | stale | superseded
superseded_by: <the claim / entry that replaced it>
as_of: YYYY-MM-DD         # when it was true
valid_until: YYYY-MM-DD   # natural life (matches the write triad)
```

- **Contradiction closes the window** — the old claim keeps its `as_of`; the new claim
  opens its own. Don’t silently overwrite.
- **Volatility classes** (how fast a fact can flip): `eternal` (L0/L1) ·
  `time_based` (visa rules, season — stamp `valid_until`) · `volatile` (prices, queues,
  weather — live-fetch only, never parked as L0/L1). The §6 "weather-class L0" refusal
  is the `volatile` class.

## L0–L3 headings

Use layer headings only as **half-life labels** (see `THESIS.md`).  
No schema engines. Directory by subject, not by L.

## Owner

One fact → one subject file. Cross-file: path pointer, don’t restate numbers.
