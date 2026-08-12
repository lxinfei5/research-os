# ResearchOS

> **A research capability for coding agents.**  
> Multi-source corroboration · active discovery · logical-space thinking · structured problem-solving output.  
> Browser-first evidence. Markdown knowledge. Git as audit log.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![Release](https://img.shields.io/badge/release-v0.2.0-green.svg)](./CHANGELOG.md)

---

## Why it exists

Most “AI research” stacks optimize **search volume**.  
ResearchOS optimizes **how an agent thinks with evidence**:

1. **Corroborate** — don’t treat a single post or single metric as truth; use independent evidence *classes* (e.g. artifact + interface + live observation — **2 of 3** is enough to *act*).  
2. **Discover actively** — the agent must open pages and hunt; empty slots are loud.  
3. **Traverse logical space** — cover the problem axes, name the main contradiction, watch long-term corrosion (surveyor-shaped discipline).  
4. **Output for the user’s problem** — first-principle answer + structure; not an encyclopedic dump of “the ultimate truth.”

Intellectual cousins: **ReAct** (reason ↔ act with tools) + **logical-space / first-principles** planning.  
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
   # edit topic.yaml + knowledge.md; register in topics/_index.yaml
   ```
3. In chat: *“Run researchos-grow on topics/my_question — browser-first.”*  
4. Prefer a runtime that can **use a browser**:
   - **Codex** → native browser tools  
   - **Others** → `kimi-webbridge` skill and/or local [`webbridge-mcp`](./tools/social_mcp/) (loopback only)

Demo topic: `topics/demo_hello_research/`.

---

## Architecture

```
AGENTS.md                 # constitution — four pillars
rules/
  floor-corroboration.md  # multi-source / 2-of-N
  floor-discovery.md      # active hunt
  floor-thinking.md       # first principles + logical space
  floor-output.md         # delivery shape
  floor-corpus.md         # write triad / L0–L3
  fetch-matrix.md         # browser-first degradation
  examples/travel.md      # commercial-style research example
topics/<slug>/knowledge.md
.agents/skills/           # grow / search / condense / travel / media
tools/social_mcp/         # optional webbridge-mcp for non-Codex agents
```

---

## Fetch (thin by design)

| Priority | What |
|---|---|
| 1 | **Browser use** — open real pages, compare sites |
| 2 | Native web search/fetch if the runtime has it |
| 3 | Optional dedicated APIs (X search, etc.) — *not* required to start |

Same evidence label under fallback; failures → `UNKNOWN + degraded_reason`.  
See `rules/fetch-matrix.md`.

---

## Example: travel planning

Stock “best restaurants 2020” lists fail weekends.  
ResearchOS-style travel work: multi-source **live** complaints vs ratings, first-principle *what problem is this trip solving*, structured day plan — **enough truth to act**, not a global ranking of every venue.

→ `rules/examples/travel.md` · skill `researchos-travel`.

---

## What stays private

Your live topics, captures, and login cookies.  
Optional pattern: public framework + private vault (`docs/PRIVATE_VAULT.md`).

---

## License

MIT — see [LICENSE](./LICENSE).  
Not investment advice; you own browser-session and content-rights risk.
