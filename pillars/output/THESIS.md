---
name: floor-output
display_name: Structured output
status: canonical
---

# Pillar 5 · Structured output

## L0

**End purpose of the whole project:** the user can *act* with the **lowest cognitive load**.

Output exists to **hand over a decision**, not to display research labor.  
A conclusion that needs “say it in human again” has already failed — including on C-end products, where nobody will read a dossier.

This is **not** a sixth innovation. Half-life, corroboration, discovery, and thinking exist **to make this sentence true**.

Lowest burden ≠ shortest text.  
Burden = work to know the act + work to know it is safe enough + work to know what would flip it.  
Hide a flip-condition and the user pays later. Dump twenty sources and they pay now.

---

## Two surfaces (one owner)

| Surface | Who reads it | What it may contain | Default? |
|---|---|---|---|
| **User** | Impatient human (C-end, exec, on-call) | Decision + conditions + at most one flip-residual | **Yes — this is the deliverable** |
| **Audit** | Agent, reviewer, later self | Corroboration table, logical space, sources, L0–L3, captures | On demand; never the first screen |

Thinking requires adjudications to *exist*.  
Output requires them to be *available* on the audit surface — **not dumped** on the user surface.

`report_template.md` is an **audit / KB projection**, not the user surface.

---

## User-surface budget (default)

Fit **one glance / one phone screen**. Allowed, in this order:

1. **Act** — what to do (one sentence, with conditions).  
2. **Why this, not that** — the main contradiction in one line (optional if the act is already unambiguous).  
3. **Hold** — 1–3 work-true reasons the user needs in order to trust the act. No source parade.  
4. **Flip** — only residuals that would **change the act**. Silence is allowed when nothing material is unknown.  
5. **Open audit** — one pointer (“sources / table on request”), not the table itself.

Forbidden on the user surface:

- Equal-weight facet tours (“stay / eat / move / history / ratings / …”)  
- Confidence badges on every line  
- Replaying the search  
- Asking the user to synthesize the decision from a memo

Confidence: **once**, on the act (S/A/B/C or equivalent).

### Shape sample (user surface)

> **订那家海边亲子房。** 车程 2.5h 可接受；两家平台近两周都抱怨隔音，但你要的是孩子白天玩水、不是睡午觉。  
> **先付前再看一眼今夜房价**（时效事实，未写入长期记忆）。  
> 置信度 B。来源表可展开。

That is the whole first screen. The 2-of-3 table is audit.

---

## Audit-surface shape (behind the pointer)

When someone expands:

1. Problem restatement  
2. Main contradiction + why it won  
3. Working premises + corroboration table  
4. Full answer / plan branches  
5. Residuals / UNKNOWN (including non-flipping ones)  
6. What would change the answer  
7. Sources (short)

Domain templates may add sections **only here**. A new first-screen section is allowed only when that line *is* the act (rule: `../examples/README.md`).

---

## How the other pillars buy lower burden

| Pillar | User should not have to… |
|---|---|
| Half-life | Babysit which facts expired |
| Corroboration | Weigh twenty links to decide if they may act |
| Discovery | Go hunt; notice a silent empty slot |
| Thinking | Extract the real tradeoff from a pile |

If a pillar’s work does not reduce one of those jobs, it is display, not research.

---

## break_condition

- Reader remembers links, not the act.  
- Reader asks for a human-language recap.  
- User surface is the 8-section memo.  
- A flip-condition was buried to look “clean.”  
- Confidence theater with no actionability.

Pointers: grow emit → this file · fixtures `fixtures/` · embed `embed.md` · before/after `../examples/before-after.md` · plan `../../docs/LOW_BURDEN.md`.
