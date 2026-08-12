---
name: floor-corpus
display_name: Knowledge write discipline
status: canonical
---

# Knowledge write discipline

## L0

`knowledge/` stores **falsifiable objective facts** for reuse.  
Plans and “do this now” schemes are **read-time** (`floor-output`), not eternal facts.

---

## Write triad

1. **proposition** — full falsifiable sentence  
2. **provenance** — URL/author/time (or capture id)  
3. **valid_until** — natural life; “forever” is not valid  

## Merge & stale

- Near-duplicate (same subject+predicate) → **merge**, don’t parallel stack  
- Past valid_until → `[stale since YYYY-MM-DD]`, keep for history  
- Untagged ≠ fresh  

## L0–L3 (half-life headings only)

| Layer | Holds |
|---|---|
| L0 | Near-constant world model |
| L1 | Slow viewpoints / structure |
| L2 | Multi-source corroborated facts |
| L3 | Single-source claims |

No schema engines. Directory by subject, not by L.

## Owner

One fact → one subject file. Cross-file: path pointer, don’t restate numbers.
