---
name: example-before-after
display_name: Same evidence, two deliveries
status: canonical
---

# Example · dossier vs user surface

Not a sixth pillar. Same synthetic facts; only the **first screen** changes.  
Canonical cards: [`../output/fixtures/`](../output/fixtures/).

This is the P1 “feel it” pair: paste a `*.ship.md` user surface into a C-end mock and you do not need a recap. Paste a `*.noship.md` and you still have to think.

---

## Pair A — production incident

**Question:** checkout 5xx after 14:02. What is the lever?

Shared facts: payment-svc 1.14.2 shipped; inventory retries 1→5; timeout logs; Redis/DB not saturated.

| Delivery | First screen | Reader still must… |
|---|---|---|
| [`incident.noship.md`](../output/fixtures/incident.noship.md) | Eight equal sections, eight hypotheses | Name the key problem and the act |
| [`incident.ship.md`](../output/fixtures/incident.ship.md) | Rollback 1.14.2. Key problem = retry storm, not the DB. One flip. | Click rollback (human-owned) |

---

## Pair B — Xiaohongshu / Reddit / X recap

**Question:** take kids to Harbor Noodle this Saturday?

Shared notes: 90-minute weekend wait; weekday lunch fine; official “no reservations”; mixed stars.

| Delivery | First screen | Reader still must… |
|---|---|---|
| [`social.noship.md`](../output/fixtures/social.noship.md) | Sentiment “mixed-to-positive” + 14 links | Invent Saturday’s plan |
| [`social.ship.md`](../output/fixtures/social.ship.md) | Don’t do Saturday dinner; weekday lunch. Wait vs kid stamina. One flip. | Walk in, or not |

---

## What to copy

The **User surface** block of a `*.ship.md` file — not the audit table, not the noship memo.
