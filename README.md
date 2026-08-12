# ResearchOS

> **A research capability for coding agents.**  
> **Half-life knowledge (L0–L3)** · multi-source corroboration · active discovery · logical-space thinking · structured output.  
> Browser-first evidence. Markdown topics. Git as audit log.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![Release](https://img.shields.io/badge/release-v0.2.1-green.svg)](./CHANGELOG.md)

---

## Why it exists

Most “AI research” stacks optimize **search volume** or **one big memory**.  
ResearchOS optimizes two things that actually transfer across domains:

### 1. Knowledge half-life (L0–L3) — what the KB should hold

**Split knowledge by how fast it changes** — not by “importance” or vibes.

| | **L0 · L1 (stable)** | **L2 · L3 (fast)** |
|---|---|---|
| Tempo | Years / multi-year structure | Weeks–months or faster |
| Examples | Country identity; long-run political *structure*; slow macro *shape* | Visa-free *this quarter*; **today’s** weather or spot price |
| Practice | **Maintain inside** the topic knowledge file | **Prefer live external fetch**; if you cache, cache **outside** the durable KB |

**Condense** (L3→L2→L1→L0) promotes claims **only when half-life allows**.  
Wrong L0 is long-lived poison; weather in L0 is a design bug.

→ Full thesis: [`rules/knowledge_layering.md`](./rules/knowledge_layering.md)

### 2. How the agent researches (four pillars)

1. **Corroborate** — independent evidence *classes* (e.g. artifact / interface / live observation — **2 of 3** to *act*).  
2. **Discover actively** — open real pages; loud empty slots.  
3. **Traverse logical space** — first principles + coverage before local polish.  
4. **Output for the user’s problem** — main knife first; not an encyclopedia of “ultimate truth.”

Intellectual cousins: **ReAct** + logical-space planning + **half-life memory design**.  
**Not** a social-media scrape toolkit.

---

## 60-second start

```bash
git clone https://github.com/lxinfei5/research-os.git
cd research-os
```

1. Point your coding agent at **`AGENTS.md`** (and `.agents/skills/`).  
2. Copy a topic:
   ```bash
   cp -R topics/_templates/topic topics/my_question
   ```
3. Chat: *“Run researchos-grow on topics/my_question — browser-first; condense by half-life.”*  
4. Browser:
   - **Codex** → native browser  
   - **Others** → `kimi-webbridge` and/or [`webbridge-mcp`](./tools/social_mcp/) (loopback)

Demo: `topics/demo_hello_research/`.

---

## Architecture

```
AGENTS.md
rules/
  knowledge_layering.md   # ★ half-life thesis (L0–L3)
  floor-corroboration.md
  floor-discovery.md
  floor-thinking.md
  floor-output.md
  floor-corpus.md
  fetch-matrix.md
  l3_distill_protocol.md / l2_aggregate_protocol.md / l1l0_synthesize_protocol.md
  examples/travel.md
topics/<slug>/knowledge.md   # L0–L3 headings in one file
.agents/skills/              # grow · search · condense · travel · media
tools/social_mcp/            # optional browser bridge for non-Codex agents
```

---

## Condense in one picture

```
live pages / captures
        ↓ distill
   L3  single-source claim     ← fast; don’t idolize
        ↓ corroborate
   L2  multi-source, still dated
        ↓ only if half-life is slow
   L1  stable structure / viewpoint
        ↓ rare
   L0  world model
```

Skill: `researchos-condense`.

---

## Fetch (thin)

1. Browser use (default)  
2. Native search/fetch as clues  
3. Optional APIs — not required to start  

→ `rules/fetch-matrix.md`

---

## Example domain: travel

Stock listicles fail weekends.  
ResearchOS-style travel: **live** multi-source checks for hours/crowds (fast) + durable trip *logic* in L1 (stable) + problem-shaped day plan.

→ `rules/examples/travel.md`

---

## License

MIT — see [LICENSE](./LICENSE).  
Not investment advice; you own browser-session and content-rights risk.
