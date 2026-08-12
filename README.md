# ResearchOS

> **Multi-agent research loop for coding agents.**  
> Open a topic → prime from what you already know → search multiple sources → capture raw intake → distill into layered world knowledge (L0–L3) → grow again.  
> No analysis database. No judgment pipeline. Markdown is the knowledge store; git is the audit log.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![Release](https://img.shields.io/badge/release-v0.1.0-green.svg)](./CHANGELOG.md)

---

## What you get

| Piece | Role |
|---|---|
| **Agent loop** (`researchos-grow`) | One closed growth cycle: Prime → Search → Capture → Distill → Condense → Coverage |
| **Floor rules** (`rules/`) | Evidence ladder, write triad, confidence layers, loud empty slots |
| **Topic isolation** | `N topics = N knowledge.md` — geopolitics and API research never bleed |
| **CAS library** | Optional content-addressed originals under `library/sources/` |
| **Skills** | grow / search / condense / media / xhs / travel + multi-search-engine |
| **webbridge-mcp** (Go) | Optional local MCP proxy so *sub-agents* can drive a real Chrome session |

This is an **auto-research workspace for LLM coding agents** (Claude Code, Codex, Grok, …), not a hosted SaaS and not an auto-trading bot.

---

## The multi-agent loop

```
┌─────────────┐
│ 1. PRIME    │  Read L0+L1+open questions+facet coverage
└──────┬──────┘
       ▼
┌─────────────┐
│ 2. SEARCH   │  Web / platform search / optional authenticated browser
└──────┬──────┘
       ▼
┌─────────────┐
│ 3. CAPTURE  │  Raw session JSON (replayable intake)
└──────┬──────┘
       ▼
┌─────────────┐
│ 4. DISTILL  │  L3 claims with proposition+provenance+valid_until
└──────┬──────┘
       ▼
┌─────────────┐
│ 5. CONDENSE │  L3→L2 corroboration → L1 synthesis → L0 worldview
└──────┬──────┘
       ▼
┌─────────────┐
│ 6. GROW     │  Refresh coverage; next thin facet
└─────────────┘
```

Orchestration is **agent-native**: skills are handbooks the model follows. There is no Python “judgment engine.”

---

## Quick start

### 1. Clone

```bash
git clone https://github.com/<you>/research-os.git
cd research-os
```

### 2. Point your coding agent at the constitution

- Claude Code / similar: `CLAUDE.md` → `AGENTS.md`
- Codex / Agents: load `AGENTS.md` + `.agents/skills/*`

### 3. Create a topic

```bash
cp -R topics/_templates/topic topics/my_first_topic
# edit topics/my_first_topic/topic.yaml + knowledge.md
# register in topics/_index.yaml
```

Or start from the demo:

```bash
cp -R examples/demo_topic topics/demo_hello_research
```

### 4. Run one growth cycle

In your agent chat:

> Use `researchos-grow` on `topics/demo_hello_research` — prime, search one thin facet, capture, distill, update coverage.

### 5. (Optional) Browser / social MCP

```bash
# See tools/social_mcp/README.md
cp tools/social_mcp/runtime-config.example.env tools/social_mcp/runtime-config.env
# edit paths; never commit secrets
./tools/social_mcp/social_mcp_daemon.sh status
```

Loopback-only webbridge-mcp re-exposes **your** Chrome — keep it on `127.0.0.1`.

---

## Repository layout

```
AGENTS.md                 # Constitution (single entry)
rules/                    # Epistemic floors + protocols
topics/
  _index.yaml             # Topic registry (derived snapshot)
  _templates/topic/       # Empty topic scaffold
  _shared/methods/        # Cross-topic pure methods (optional)
  <slug>/                 # Your topics (knowledge.md + sources + captures)
examples/demo_topic/      # Tiny synthetic demo
library/sources/          # Optional CAS originals (you fill)
.agents/skills/           # Agent handbooks
tools/social_mcp/         # webbridge-mcp + daemon scripts
docs/                     # Architecture, private-vault guide, release notes
```

---

## Design principles (short)

1. **Must produce** graded-confidence knowledge — not “cannot judge” as default.
2. **Honest empty slots** — `UNKNOWN` / `degraded_reason`, never silent skip.
3. **Constraint shape ≠ orchestration** — floors are markdown DATA, not a gate engine.
4. **Delete > add** — no schema, no analysis DB, no self-scoring win-rate loop.
5. **Human owns risk** — especially browser login automation and third-party content retention.

Full constitution: [`AGENTS.md`](./AGENTS.md).

---

## Private research vs public skeleton

This public tree is a **framework + demo**. Keep personal corpora in a **private fork/vault**:

| Public (this repo) | Private vault |
|---|---|
| Rules, skills, tools, templates | Live `topics/*` research |
| Synthetic demo topic | Scraped originals, paywalled notes |
| Empty `library/sources/` | CAS dumps, media |

See [`docs/PRIVATE_VAULT.md`](./docs/PRIVATE_VAULT.md).

---

## Release

See [`CHANGELOG.md`](./CHANGELOG.md) and [`docs/RELEASE.md`](./docs/RELEASE.md).

```bash
# sanity (no secrets patterns in tracked files)
./scripts/check-public.sh
```

---

## Disclaimer

- Research methodology and agent workspace pattern only.
- Not investment advice; not a brokerage; not unattended social scraping-as-a-service.
- You are responsible for platform ToS, copyright of retained sources, and browser-session security.

## License

MIT — see [LICENSE](./LICENSE).
