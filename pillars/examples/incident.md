---
name: example-incident
display_name: Example domain — name the key problem
status: canonical
---

# Example · On-call / online incident

Agents are good at listing logs, graphs, and hypotheses. They are bad at saying **which contradiction this page is**.  
This domain exists so the user surface is a lever, not a war room transcript.

Worked pair (synthetic): [`../output/fixtures/incident.ship.md`](../output/fixtures/incident.ship.md) vs [`incident.noship.md`](../output/fixtures/incident.noship.md).

---

## Half-life (don’t mix)

| Fact | Layer |
|---|---|
| This service talks to inventory over a short timeout | L1 structure |
| Tonight’s error rate / which version is live | **Live / L3** — never L0 |
| “We always scale the DB first” as folklore | Not a fact; do not store |

---

## Map the pillars

| Pillar | Instantiation |
|---|---|
| Corroboration | Diff (A) + timeout/config contract (B) + live logs (C) before blaming a dependency |
| Discovery | Open the deploy artifact and the live error class — not only a metric screenshot |
| Thinking | End purpose = restore checkout; main contradiction e.g. *retry storm vs. “DB looks busy”* |
| Output | **User surface:** one lever + why that lever + one flip. Dashboards stay audit. |

---

## User-surface skeleton (default)

Each first-screen line must *be* the act, the reason the other lever is wrong, or the one flip.

1. **Act** — rollback / feature-flag / page X (one sentence). *This is the act.*  
2. **Why this, not that** — the key problem in one line. *This is why the act is that lever.*  
3. **Hold** — 1–3 work-true supports the on-call needs to trust the click. *Not a metric tour.*  
4. **Flip** — the one residual that would change the lever. *If it would not change the act, omit.*

Do **not** add “timeline / eight hypotheses / dashboard gallery” to the first screen. Those are audit.

Human owns irreversible actions (rollback, data delete, public comms).
