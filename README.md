# ResearchOS

<p align="center">
  <strong>Decision-grade research capability for AI agents.</strong><br>
  Built for minimal cognitive load to act — zero fluff, anti-poisoning memory, multi-source verified.
</p>

<p align="center">
  <a href="./LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT"></a>
  <a href="./CHANGELOG.md"><img src="https://img.shields.io/badge/Release-v0.4.0-3ecf8e.svg" alt="Release"></a>
  <a href="./AGENTS.md"><img src="https://img.shields.io/badge/Constitution-AGENTS.md-94a3b8.svg" alt="Constitution"></a>
  <a href="https://lxinfei5.win/travel/"><img src="https://img.shields.io/badge/Live_Demo-Production_Ready-10b981.svg" alt="Production Ready Demo"></a>
</p>

---

## 🎯 The Core Thesis

Most AI research tools generate a 2,000-word dossier of links, summaries, and uncommitted "maybes." The cognitive burden of synthesizing facts into decisions is left entirely to the human reader.

**ResearchOS flips this paradigm.**

> **First Principle:** The deliverable is not research labor — it is a **one-glance decision** with the **lowest cognitive load to act**.
>
> 1. **Act:** What to do, bounded by concrete conditions.
> 2. **Hold:** 1–3 load-bearing reasons to trust the choice (no link dump).
> 3. **Flip:** Explicit conditions that would overturn the decision.
>
> *Audit tables, sources, and full logical spaces are progressively disclosed behind the card — never dumped on the first screen.*

---

## 🛡️ Production-Grade Dialectical Engine (类生产级核心辨证能力)

ResearchOS is engineered as an embeddable, **production-grade dialectical reasoning backbone** for autonomous agents, executive copilots, and high-stakes decision systems. It solves the fundamental reliability gap in modern LLM agent architectures:

* **Dialectical Triangulation (2-of-N):** Enforces cross-examination across independent evidence classes (Artifact, Interface, Live Observation). Agents refuse to act on uncorroborated single-source claims and explicitly surface `UNKNOWN` gaps.
* **Anti-Poisoning Memory Hierarchy:** Strict half-life separation prevents volatile, fast-decaying operational facts (L2/L3) from corrupting the agent's core world model (L0/L1).
* **Progressive Disclosure Architecture:** Delivers high-conviction **Act / Hold / Flip** cards to end-users on the first screen while maintaining full, auditable reasoning trails in the background.
* **Zero-Persistence Security & Sandboxing:** Proven in live hardened deployments with client-side credential isolation, strict SSRF-proof loopback proxies, and zero disk key logging.

---

## 🏛️ Five Architectural Innovations

<p align="center">
  <img src="docs/assets/pillars.svg" alt="ResearchOS five innovations diagram" width="100%"/>
</p>

| # | Pillar | Core Innovation | Canonical Thesis |
|---|---|---|---|
| **1** | **Half-Life Knowledge (L0–L3)** | Classifies knowledge strictly by **how fast facts change**, not by "importance". Volatile facts are kept ephemeral to prevent long-term memory poisoning. | [`pillars/half-life/`](./pillars/half-life/) |
| **2** | **Multi-Source Corroboration** | Enforces **2-of-N cross-class verification** (Artifacts, Interfaces, Live Observation) before any claim is accepted as work-true. | [`pillars/corroboration/`](./pillars/corroboration/) |
| **3** | **Active Discovery** | Source-agnostic evidence hunting across user-trusted channels; missing evidence is loudly surfaced as `UNKNOWN`. | [`pillars/discovery/`](./pillars/discovery/) |
| **4** | **Logical Space & Thinking** | Maps complete solution spaces and isolates the upstream core contradiction before local details are evaluated. | [`pillars/thinking/`](./pillars/thinking/) |
| **5** | **Problem-Shaped Output** | Prioritizes the user decision surface first; keeps verification tables, captures, and raw trails strictly on the audit surface. | [`pillars/output/`](./pillars/output/) |

*Full methodology details:* [`pillars/README.md`](./pillars/README.md)

---

## ⚡ Memory Architecture: Half-Life in Practice

| Layer | Half-Life Tempo | Storage Practice | Real-World Example |
|---|---|---|---|
| **L0 / L1 (Stable)** | Years to multi-year | **Maintain inside** durable KB | Regional macro structure, system design boundaries |
| **L2 / L3 (Fast)** | Days, weeks, or months | **Live fetch & ephemeral cache**; never promote to core KB | Spot prices, seasonal visa rules, current queue times |

> **Promotion is guilty by default:** Fast facts expire naturally; only structural invariants ever climb the abstraction ladder.

---

## 🌐 Applicability & Industry Use Cases

* **High-Stakes Consumer & Travel Decisions:** Cutting through sponsored noise and holiday surges to deliver definitive go/no-go itineraries. *(See [`pillars/examples/travel.md`](./pillars/examples/travel.md))*
* **Technical Due Diligence & Architecture:** Evaluating codebases and APIs against actual runtime evidence rather than marketing claims.
* **Incident Forensics & Operations:** Pinpointing the single root contradiction rather than drowning in log metrics. *(See [`pillars/examples/incident.md`](./pillars/examples/incident.md))*

---

## 🚀 Live Experiences & Demos

Explore ready-to-run decision surfaces and reference topics:

* **Interactive Travel Decision Studio:** [Launch Live Experience (https://lxinfei5.win/travel/)](https://lxinfei5.win/travel/)  
  *(For local setup, BYOK LLM proxy, and developer instructions, see [`demo/travel/`](./demo/travel/))*
* **Reference Output Card (Synthetic):** [`topics/demo_hello_research/user_surface.md`](./topics/demo_hello_research/user_surface.md)
* **Dossier vs. Actionable Card Contrast:** [`pillars/examples/before-after.md`](./pillars/examples/before-after.md)

---

## 📂 Repository Structure

```
pillars/                 # Canonical innovation theses and verification protocols
.agents/skills/          # Runtime agent skills (grow, condense, search, media)
topics/                  # Domain knowledge instances and active research topics
demo/                    # Interactive host sketches and visual surfaces
rules/                   # Protocol redirects and lightweight constraints
tools/                   # Optional adapters (e.g. MCP browser / search bridges)
AGENTS.md                # System constitution and execution discipline
```

---

## 📜 License

MIT License — see [LICENSE](./LICENSE).
