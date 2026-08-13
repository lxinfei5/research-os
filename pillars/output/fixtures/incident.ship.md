# Incident · user surface (may ship)

Synthetic. Same facts as `incident.noship.md`.

## User surface

**Rollback `payment-svc` 1.14.2 now.**  
The key problem is **retry amplification on inventory** (retries 1→5 against an 800ms budget), not a sick database.  
**Flip:** if 5xx still climb after rollback, page inventory — do not scale the DB first.  
Confidence A. [Why / sources]

## Audit (collapsed)

| Claim | A artifact | B interface | C live | Status |
|---|---|---|---|---|
| 1.14.2 changed inventory retries 1→5 | release diff | client config / 800ms timeout | timeout logs after 14:02 | work-true |
| DB / Redis are the bottleneck | — | connection gauges normal | Redis CPU ~40% | clue against |
| Inventory itself is down | — | — | only seen via client timeouts | UNKNOWN — check after rollback |

Main contradiction: *retry storm vs. “the database looks busy.”* Fixing the wrong lever (scale DB) would hide the storm.

Half-life: retry config and tonight’s error rate are live / L3. Do not write “inventory is always the problem” into L0.

Human owns the rollback click.
