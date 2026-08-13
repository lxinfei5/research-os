---
name: output-embed
display_name: Host progressive disclosure
status: canonical
as_of: 2026-08-14
---

# C-end / host embed

How a chat bubble, app card, or feed item **shows** a ResearchOS conclusion.  
Not a hosted ResearchOS app. Not a new pillar. Slots come from [`THESIS.md`](./THESIS.md).

---

## Slots

| Slot | Screen 1? | Rule |
|---|---|---|
| `act` | **Required** | One sentence. What to do, with conditions. |
| `why_not_that` | If the act is ambiguous | The key problem / main contradiction. One line. |
| `hold` | Optional, ≤3 | Only reasons the user needs in order to trust the act. |
| `flip` | Only if it changes the act | One residual. Omit if nothing material is unknown. |
| `confidence` | Once, on the act | S/A/B/C or equivalent. No per-line badges. |
| `audit` | **Never** on screen 1 | Table, sources, branches. Closed until the user opens it. |

---

## Screens

**Screen 1** — render `act`, then `why_not_that` / `hold` / `flip` if present, then a single control:

`Why / sources` → opens **screen 2** (`audit` only).

Do not auto-expand audit. Do not put the corroboration table above the fold.  
Irreversible acts (pay, deploy, delete, send) stay a **human** confirm — the card does not click them.

```
┌─ card ─────────────────────────────────┐
│  Rollback payment-svc 1.14.2 now.      │
│  Key problem: retry storm, not the DB. │
│  Flip: still climbing → page inventory.│
│  B                          [Why ▾]    │
└────────────────────────────────────────┘
```

Pasteable first screens: [`fixtures/incident.ship.md`](./fixtures/incident.ship.md), [`fixtures/social.ship.md`](./fixtures/social.ship.md).

---

## Failure

- Screen 1 is the 8-section memo.  
- Audit opens by default.  
- The control is labeled “full report” and dumps labor.  
- The host clicks rollback / pay without a human.
