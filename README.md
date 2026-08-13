# ResearchOS

Agents dump a pile of evidence and a maybe. They almost never name the **key problem** or hand you a conclusion you can act on — whether you are reading production logs or a Xiaohongshu / Reddit / X recap. You still do the thinking. That load is why this exists.

> A research capability for coding agents.  
> **First principle:** the user-facing conclusion has the **lowest cognitive load to *act*** — what to do, under what conditions, what would flip it. No second “say it in human” pass.  
> Five means: half-life knowledge · multi-angle corroboration · active discovery · logical-space thinking · user-surface output.  
> **Source-agnostic** evidence (whatever the user trusts). Markdown topics. Git as audit log.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![Release](https://img.shields.io/badge/release-v0.4.0-green.svg)](./CHANGELOG.md)

---

## Five innovations

<!-- Hero: accurate labels (SVG). Generated raster alternative: docs/assets/pillars-hero.jpg (pending visual review). -->
<p align="center">
  <img src="docs/assets/pillars.svg" alt="ResearchOS five innovations diagram" width="100%"/>
</p>

| # | Innovation | What it changes | Owner folder |
|---|---|---|---|
| **1** | **Half-life knowledge (L0–L3)** | Split memory by *how fast facts change* — not by “importance” | [`pillars/half-life/`](./pillars/half-life/) |
| **2** | **Multi-source corroboration** | Independent evidence *classes*; **2-of-N** is enough to *act* | [`pillars/corroboration/`](./pillars/corroboration/) |
| **3** | **Active discovery** | Agent must hunt multi-source evidence on **user-trusted** channels; empty slots are loud | [`pillars/discovery/`](./pillars/discovery/) |
| **4** | **Logical space + first principles** | Cover the problem axes; name the main contradiction | [`pillars/thinking/`](./pillars/thinking/) |
| **5** | **Structured output** | **User surface** first (act / hold / flip); audit behind — not an encyclopedia | [`pillars/output/`](./pillars/output/) |

Full index: [`pillars/README.md`](./pillars/README.md).

### Half-life in one table

| | **L0 · L1 (stable)** | **L2 · L3 (fast)** |
|---|---|---|
| Tempo | Years / structure | Weeks–months or faster |
| Practice | **Maintain in** topic KB | **Live fetch**; cache *outside* durable KB |
| Example | Long-run regional structure | Visa-free *this quarter*; **today’s** weather |

**Condense** = climb L3→L2→L1→L0 only when half-life allows (promotion guilty by default).

---

## Why not “more search”?

Search volume is commoditized. Long reports are not a product.  
ResearchOS packages **how an agent should remember, verify, think, and hand over a decision** — so a C-end reader never has to digest the labor.

Intellectual cousins: **ReAct** (reason↔act) + logical-space planning + **half-life memory design**.  
**Not** a social-media scrape toolkit. **Not** a dossier generator.

---

## 60-second start

```bash
git clone https://github.com/lxinfei5/research-os.git
cd research-os
```

1. Point your agent at **`AGENTS.md`** + `.agents/skills/`.  
2. `cp -R topics/_templates/topic topics/my_question`  
3. *“Run researchos-grow — multi-source on channels I trust; condense by half-life; emit a one-glance act, not a dossier.”*  
4. Plug in **whatever sources you trust** (APIs, browser, files, briefings). Optional browser adapter: [`webbridge-mcp`](./tools/social_mcp/) when the runtime has no native browser.

Demo: `topics/demo_hello_research/` (user-surface card: `user_surface.md`).  
Same-evidence contrast: [`pillars/examples/before-after.md`](./pillars/examples/before-after.md).

---

## Evidence stance (important)

**Not browser-first.**  
ResearchOS does **triangulation / multi-angle corroboration** on sources **the user trusts**. Browser, search, vendor APIs, local files, and user briefings are all valid **channels** — interchangeable adapters under a stable evidence matrix (`pillars/discovery/fetch-matrix.md`). The product claim is **how you argue with evidence**, not which pipe you use.

---

## Repository layout

```
pillars/                 # ★ one folder per innovation (canonical method)
  half-life/             # L0–L3 thesis + condense protocols + corpus
  corroboration/         # multi-angle / 2-of-N
  discovery/             # active hunt + source-agnostic fetch-matrix
  thinking/
  output/
  examples/              # travel · incident · before/after (not a sixth pillar)
rules/                   # thin redirects + shared ops only
.agents/skills/          # grow · condense · search · travel · …
topics/                  # per-topic knowledge instances (L0–L3 headings)
tools/social_mcp/        # optional browser adapter (not required)
docs/assets/             # diagrams
AGENTS.md                # constitution
```

**Constraint:** new method text goes under the matching `pillars/<name>/` only — never a second copy in skills or a growing `rules/` pile.

---

## Grow loop

```
Prime (L0/L1) → Discover (user-trusted multi-source) → Capture
  → Condense (half-life + multi-angle corroboration) → Think
  → Emit (user surface first; audit behind)
```

---

## Examples

| File | What to feel |
|---|---|
| [`pillars/examples/before-after.md`](./pillars/examples/before-after.md) | Same facts; dossier vs one-glance act |
| [`pillars/examples/incident.md`](./pillars/examples/incident.md) | Name the key problem; one lever |
| [`pillars/examples/travel.md`](./pillars/examples/travel.md) | Weekend plan; rotting hours |
| [`pillars/output/embed.md`](./pillars/output/embed.md) | How a C-end card should open |

---

## License

MIT — see [LICENSE](./LICENSE).
