# ResearchOS — Constitution

> Single authority. Runtime entrypoints (`CLAUDE.md` / `GROK.md` / …) symlink here.  
> **Innovations live under [`pillars/`](./pillars/)** — one folder per thesis; do not fork method bodies into `rules/` or skills.

---

## §0 What this is

**ResearchOS is a research *capability* for coding agents.**

It ships **five product innovations** (plus a thin browser adapter):

| # | Innovation | Folder |
|---|---|---|
| 1 | **Half-life knowledge (L0–L3)** — stable in KB, fast live | `pillars/half-life/` |
| 2 | **Multi-source corroboration** — 2-of-N classes enough to *act* | `pillars/corroboration/` |
| 3 | **Active discovery** + browser-first fetch | `pillars/discovery/` |
| 4 | **Logical space + first principles** | `pillars/thinking/` |
| 5 | **Problem-shaped structured output** | `pillars/output/` |

Form: markdown + skills + optional browser tools.  
**No analysis DB, no judgment engine, no self-scoring loop, no scrape-kit product surface.**

---

## §1 Directory discipline

| Path | Holds | Must not hold |
|---|---|---|
| `pillars/<innovation>/` | **Only** that innovation’s thesis + protocols | Other pillars’ copies; live topic facts |
| `rules/` | Thin redirects + shared ops stubs | New innovation theses |
| `.agents/skills/` | How to *run* the loop | Redefining pillar claims |
| `topics/` | Per-topic L0–L3 **instances** | Method ownership |
| `tools/` | Optional adapters (webbridge-mcp) | Research methodology |
| `docs/assets/` | Diagrams for README | Secrets |

Index of innovations: **`pillars/README.md`**.

---

## §2 Half-life (innovation 1) — memory design

Full: `pillars/half-life/THESIS.md`

| Band | Layers | Practice |
|---|---|---|
| Stable | L0 · L1 | Maintain in `topics/*/knowledge.md` |
| Fast | L2 · L3 | Prefer live fetch; external cache only |

**Condense** climbs L3→L2→L1→L0; **promotion is guilty by default**.

---

## §3 Behavior pillars (innovations 2–5)

| Pillar | One-liner | Entry |
|---|---|---|
| Corroboration | Independent classes; 2-of-N to act | `pillars/corroboration/THESIS.md` |
| Discovery | Hunt multi-source; loud UNKNOWN | `pillars/discovery/THESIS.md` |
| Thinking | First principles + full logical space | `pillars/thinking/THESIS.md` |
| Output | Main knife first; residuals loud | `pillars/output/THESIS.md` |

Fetch degradation: `pillars/discovery/fetch-matrix.md`  
(Codex browser · else kimi-webbridge / webbridge-mcp).

Standing stance: whole > parts · main question > flat list · delete > add · floors are DATA not gates.

---

## §4 Grow loop

`researchos-grow`:

1. Prime from L0/L1 + open questions  
2. Discover (browser-first)  
3. Capture if useful  
4. Condense by half-life + corroboration  
5. Think (logical space)  
6. Emit (problem-shaped)  

---

## §5 Example domain

Travel: `pillars/examples/travel.md` · skill `researchos-travel`.

---

## §6 Refuse

Analysis DB · self-scoring loops · personal corpora / live cookies in tree · weather-class L0.
