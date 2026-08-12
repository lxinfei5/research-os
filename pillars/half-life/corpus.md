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

## L0–L3 headings

Use layer headings only as **half-life labels** (see `THESIS.md`).  
No schema engines. Directory by subject, not by L.

## Owner

One fact → one subject file. Cross-file: path pointer, don’t restate numbers.
