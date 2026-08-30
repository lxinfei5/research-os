# Changelog

## [0.4.1] — 2026-08-30

### Consume the fenced webbridge runtime; retire the in-tree copy

- Deleted the unfenced Go under `tools/social_mcp/webbridge_mcp` (no JS/CDP/upload gates, no `<untrusted_content>` fence). Live server is user-level `~/.webbridge-mcp` on `127.0.0.1:18061`.
- `social_mcp_daemon.sh` / `.ps1` no longer compile, `nohup`, or `kill-9` `:18061` (that path could displace the fenced LaunchAgent).
- Skills / `fetch-matrix` / `SECURITY.md`: page bytes are inert data; sub-agents use `mcp__webbridge-mcp__*`; no `curl :10086`; xiaohongshu-mcp `:18060` labeled unfenced residual.
- `.mcp.json` uses `127.0.0.1` for 18060/18061 (matches the loopback listener).

## [0.4.0] — 2026-08-14

### First principle: lowest cognitive load to act

- README **first sentence** is the pain: agents dump evidence and a maybe; they do not name the key problem or hand over an act  
- Constitution (`AGENTS.md` §0): five innovations are **means**; the user-facing conclusion is the product  
- Output thesis: **user surface** (act / hold / flip) vs **audit surface**; 8-section memo is no longer the default  
- Thinking: adjudications must exist and stay available — not dumped on the first screen  
- `report_template.md` labeled audit / KB projection, not the answer  
- Grow + travel emit default to the user surface  

### P1–P3 (same release)

- P1: same-evidence before/after — `pillars/examples/before-after.md` + `pillars/output/fixtures/*.{ship,noship}.md`  
- P1: clone-and-run card — `topics/demo_hello_research/user_surface.md`  
- P2: fixture verdict table; new domain examples must justify every first-screen line (`pillars/examples/README.md`)  
- P2: incident domain — `pillars/examples/incident.md`  
- P3: host progressive disclosure — `pillars/output/embed.md`  
- Roadmap: `docs/LOW_BURDEN.md`

## [0.3.1] — 2026-08-12

### Evidence stance: not browser-first

- Clarify product claim: **multi-angle corroboration on user-trusted sources**  
- `fetch-matrix` and discovery thesis are **source-agnostic** (API, files, browser, briefing, library, …)  
- Browser / webbridge documented as **optional adapters**, not the core path  
- README / AGENTS / skills / diagram copy updated  

## [0.3.0] — 2026-08-12

### Pillar-first layout + five innovations

- Canonical method moved to **`pillars/`** — one folder per innovation  
  - `half-life` · `corroboration` · `discovery` · `thinking` · `output`  
- `rules/` reduced to redirects + shared ops stubs  
- README emphasizes five innovations; accurate SVG diagram in `docs/assets/pillars.svg`  
- Generated hero raster `docs/assets/pillars-hero.jpg` available for visual review  
- Skills / constitution paths updated  

## [0.2.1] — 2026-08-12

### Half-life knowledge (L0–L3) as first-class product thesis

- Canonical write-up: `pillars/half-life/THESIS.md`  
  - **Stable L0/L1** → maintain in the topic KB  
  - **Fast L2/L3** → prefer live external gather; cache outside if needed  
- Elevated in `AGENTS.md` / `README.md` / condense + grow skills  
- Condense framed as **half-life climb** (promotion guilty by default)  
- Travel example + demo topic show stable vs live facts  

## [0.2.0] — 2026-08-12

### Reposition: research *capability*, not scrape kit

- **Four pillars** as core product: corroboration · discovery · thinking · output  
- **Browser-first fetch** (`pillars/discovery/fetch-matrix.md`): Codex native browser; else kimi-webbridge / webbridge-mcp  
- Travel as **example domain** for commercial problem-solving research  
- Removed core social anti-bot / XHS / Zhipu playbooks from the public surface  
- History scrub: absolute local home paths replaced  
- Docs: `docs/REPOSITIONING.md`

## [0.1.0] — 2026-08-12

### Public framework release

- Soft-gate markdown topic OS; MIT; synthetic demo; OSS clean of personal corpora  
