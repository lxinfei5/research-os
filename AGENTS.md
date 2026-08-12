# ResearchOS — Constitution

> Single authority for this workspace. Runtime entrypoints (`CLAUDE.md` / `GROK.md` / …) symlink here.

---

## §0 What this is

**ResearchOS is a research *capability* for coding agents** — a reusable way to:

1. **Actively discover** multi-source evidence  
2. **Corroborate** enough of it to trust for action (not “one eternal truth”)  
3. **Traverse logical space** with first principles (coverage + main contradiction)  
4. **Emit structured outputs** that solve the user’s problem  
5. **Store knowledge by half-life (L0–L3)** — stable in the KB, fast facts outside  

Form: markdown knowledge + agent skills + optional browser tools.  
**No analysis database, no judgment pipeline engine, no self-scoring loop.**

Closest public metaphors: **ReAct** (reason ↔ act) + **logical-space / first-principles** discipline + **half-life knowledge layering** (what memory should keep).

**Not the product:** platform scrape runbooks, anti-bot playbooks, or personal corpora.

---

## §1 Knowledge half-life (L0–L3) — core thesis

> Full write-up: **`rules/knowledge_layering.md`** (read this; don’t invent another axis).

**Claim:** split knowledge by **how fast it changes**, not by how “important” or “true” it feels.

| Band | Layers | Tempo | Practice |
|---|---|---|---|
| **Stable** | **L0 · L1** | Years / multi-year structure | **Maintain in** `topics/*/knowledge.md` |
| **Fast** | **L2 · L3** | Weeks–months or faster | **Prefer live external fetch**; cache outside the durable KB if needed |

Examples of intuition:

- L0/L1: country identity / long-run political *structure*; slow macro *shape*  
- L2/L3: visa-free *this quarter*; **today’s** weather or spot print  

**Condense** (L3→L2→L1→L0) is how raw finds **promote only when half-life allows** — promotion is guilty by default.

L0–L3 are **markdown headings only** — not schemas or promote engines.

---

## §2 Research behavior (four pillars)

| Pillar | One-liner | Detail |
|---|---|---|
| **1 · Corroboration** | Prefer **2 independent classes** of evidence before work-true | `rules/floor-corroboration.md` |
| **2 · Discovery** | The agent must **go get** evidence; empty slots are loud | `rules/floor-discovery.md` |
| **3 · Thinking shape** | First principles + full logical space before local depth | `rules/floor-thinking.md` |
| **4 · Output** | Lead with the main knife; confidence + residuals explicit | `rules/floor-output.md` |

Standing stance:

- **Whole > parts** · **Main question > flat lists** · **Delete > add**  
- **Constraint shape ≠ orchestrated thinking** (floors are DATA, not gates)  
- **Honest confidence > polite refusal**  

---

## §3 Knowledge form

- **N topics = N `topics/<slug>/knowledge.md`** (physically isolated).  
- Write triad: **proposition + provenance + valid_until** (`rules/floor-corpus.md`).  
- Directional “so do X” schemes are **read-time** — not eternal L0.  
- Git is the audit log.

**Progressive load:** never bulk-read all topics. Index → one `knowledge.md` → open only needed sources.

---

## §4 Fetch (browser-first, deliberately thin)

| Priority | Channel |
|---|---|
| **1** | **Browser use** (Codex native browser · else kimi-webbridge / webbridge-mcp) |
| **2** | Runtime WebSearch/WebFetch as *clues*, then open pages |
| **3** | Optional APIs/MCP if installed — never required to clone |

Degradation: `rules/fetch-matrix.md`. Fail → `UNKNOWN + degraded_reason`.

---

## §5 Research loop (grow + condense)

**Grow** (`researchos-grow`):

1. **Prime** — L0/L1 + open questions + thin facets  
2. **Discover** — browser-first multi-source (`floor-discovery`)  
3. **Capture** — raw intake when useful  
4. **Distill / corroborate** — L3 then L2 under half-life + corroboration rules  
5. **Think** — logical space + first principles (`floor-thinking`)  
6. **Emit** — problem-shaped output (`floor-output`); refresh coverage  

**Condense** (`researchos-condense`): climb L3→L2→L1→L0 **only** when half-life matches (`knowledge_layering.md` + stage protocols).

---

## §6 Example domain: travel

Live multi-source planning (reviews, hours, routes) — **fast facts stay live**; durable trip *logic* can sit in L1.  
→ `rules/examples/travel.md` · `researchos-travel`.

---

## §7 What we still refuse

- Analysis DB / forced judgment engines  
- Self-endorsing win-rate loops  
- Personal corpora or live cookies/tokens in public tree  
- Promoting weather-class facts into L0 “forever”  

---

## §8 Known costs

- Concurrent edits need re-read-before-write  
- Freshness is conscious (`valid_until` / stale), not a cron  
- `_index.yaml` is a snapshot — body is truth  

---

## Pointers

| Need | Open |
|---|---|
| **Half-life L0–L3** | `rules/knowledge_layering.md` |
| Corroboration | `rules/floor-corroboration.md` |
| Discovery | `rules/floor-discovery.md` |
| Thinking | `rules/floor-thinking.md` |
| Output | `rules/floor-output.md` |
| Write triad | `rules/floor-corpus.md` |
| Fetch | `rules/fetch-matrix.md` |
| Condense skill | `.agents/skills/researchos-condense/SKILL.md` |
