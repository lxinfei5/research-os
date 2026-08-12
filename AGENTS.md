# ResearchOS — Constitution

> Single authority for this workspace. Runtime entrypoints (`CLAUDE.md` / `GROK.md` / …) symlink here.

---

## §0 What this is

**ResearchOS is a research *capability* for coding agents** — a reusable way to:

1. **Actively discover** multi-source evidence  
2. **Corroborate** enough of it to trust for action (not “one eternal truth”)  
3. **Traverse logical space** with first principles (coverage + main contradiction)  
4. **Emit structured outputs** that solve the user’s problem  

Form: markdown knowledge + agent skills + optional browser tools.  
**No analysis database, no judgment pipeline engine, no self-scoring loop.**

Closest public metaphor: **ReAct-style reason↔act loops**, with **surveyor-style logical-space discipline** so the agent does not collapse into local polish.

**Not the product:** platform scrape runbooks, anti-bot playbooks, or personal corpora.

---

## §1 Four pillars

| Pillar | One-liner | Detail |
|---|---|---|
| **1 · Corroboration** | Prefer **2 independent classes** of evidence before treating a claim as work-true | `rules/floor-corroboration.md` |
| **2 · Discovery** | The agent must **go get** evidence; empty slots are loud | `rules/floor-discovery.md` |
| **3 · Thinking shape** | First principles + full logical space + counterexamples before local depth | `rules/floor-thinking.md` |
| **4 · Output** | Lead with the main knife; templates serve it; confidence + residuals explicit | `rules/floor-output.md` |

Standing stance:

- **Whole > parts** · **Main question > flat lists** · **Delete > add**  
- **Constraint shape ≠ orchestrated thinking** (floors are DATA, not gates)  
- **Honest confidence > polite refusal** — intervals + chain beat “cannot judge” as default  

---

## §2 Knowledge form

- **N topics = N `topics/<slug>/knowledge.md`** (physically isolated world models).  
- Layers **L0–L3** are markdown headings by half-life (not schemas).  
- Write triad: **proposition + provenance + valid_until** (`rules/floor-corpus.md`).  
- Directional “so do X” schemes are **read-time** — optional in reports, not stored as eternal fact.  
- Git is the audit log.

**Progressive load:** never bulk-read all topics. Index → one `knowledge.md` → open only needed sources.

---

## §3 Fetch (browser-first, deliberately thin)

Evidence needs **channels**, not a particular vendor.

| Priority | Channel | When |
|---|---|---|
| **1** | **Browser use** (read real pages / apps in a browser) | Default for deep research |
| **2** | Runtime native web search / fetch | Quick clues, then open sources in browser |
| **3** | Optional APIs/MCP (X search, etc.) | If installed; never required to clone |

**Browser routing:**

| Runtime | How |
|---|---|
| **Codex / agents with native browser** | Use the runtime browser tools |
| **Claude Code / others without native browser** | `kimi-webbridge` skill and/or local `webbridge-mcp` (loopback → user Chrome) |

Degradation matrix (semantics stable under fallback): `rules/fetch-matrix.md`.  
Missing channel → `UNKNOWN + degraded_reason`, continue with remaining channels.

---

## §4 Research loop (grow)

One cycle (`researchos-grow` skill):

1. **Prime** — L0/L1 + open questions + thin facets (don’t re-search settled ground).  
2. **Discover** — browser-first multi-source hunt (`floor-discovery`).  
3. **Capture** — raw intake in `captures/` when useful.  
4. **Corroborate + distill** — L3 claims; upgrade only under corroboration rules.  
5. **Think** — logical space + first principles on the user’s problem (`floor-thinking`).  
6. **Emit** — structured card / plan (`floor-output`); refresh coverage.  

Condense contracts (L3→L2→L1→L0): `rules/l3_distill_protocol.md` etc. — servants of the pillars, not a second product.

---

## §5 Example domain: travel

Travel planning is a **canonical research-capability** use case: multi-source live evidence, user problem first, not “the one true ranking of all restaurants.”

→ `rules/examples/travel.md` + skill `researchos-travel`.

Other domains (incident review, vendor selection, market scan, paper triage) reuse the **same four pillars**.

---

## §6 What we still refuse

- Analysis DB / forced multi-step judgment engines  
- Self-endorsing win-rate loops  
- Shipping personal corpora or live cookies/tokens  
- Pretending a channel was covered when it was not  

---

## §7 Known costs

- Concurrent edits to one `knowledge.md` need re-read-before-write.  
- Freshness is conscious (stale tags), not a cron.  
- `_index.yaml` coverage is a snapshot — body is truth.  

---

## Pointers

| Need | Open |
|---|---|
| Corroboration (2-of-N) | `rules/floor-corroboration.md` |
| Active discovery | `rules/floor-discovery.md` |
| Thinking shape | `rules/floor-thinking.md` |
| Output shape | `rules/floor-output.md` |
| Write discipline | `rules/floor-corpus.md` |
| Fetch degrade | `rules/fetch-matrix.md` |
| Skills | `.agents/skills/*/SKILL.md` |
