# ResearchOS — Agent / Operator Guide

Multi-topic research system: open a **topic**, search public web + X/抖音/小红书, condense findings
into that topic's own layered **L0–L3 world knowledge**, retain originals, and grow each topic over
time. Full design: `DESIGN.md`. Status: `README.md`. This file is how to OPERATE the system.

## The one iron rule

**Python never reasons or calls an LLM.** `ros/**` only orchestrates, counts, validates, persists.
Every semantic judgment — distillation, credibility, corroboration, synthesis, search relevance — is
done by an agent reading versioned methodology (`control_plane/reasoning/methodology/*.md`) and
written back through gated upserts. If you're tempted to put a heuristic that "decides meaning" in
Python, it belongs in a methodology doc + the condense AGENT step instead.

Corollaries: **N topics = N `topics/<slug>/` dirs = N `knowledge.db` = N world knowledges** (physical
isolation, no global topic_id; never auto-merge). Evidence rows never cross topics; only the global
`library/` (content-addressed originals) and pure-logic method rules are shared.

## Lifecycle (the loop)

```
ros topic new <slug> [--title T --alias A]   # scaffold dir + knowledge.db + sources.db
ros facet add "<question>" [--topic]         # seed a research sub-question
ros topic open <slug>                        # set active; print world model + facets + coverage

ros grow <slug>                              # PRIME: freeze a brief from current knowledge + plan
#   → agent runs the researchos-grow skill: search the thin facets, capture, condense, report
ros search "<q>" --source web,xiaohongshu --facet f_x   # plan + collector policy; logs the query
#   ↳ agent fetches via the READY skills, normalizes, then:
ros media transcribe <file> [--topic]        # video → text (whisper) BEFORE capture
ros media ocr <image>                        # image → text (zai-mcp agent path / local fallback)
ros capture <payload.json> --topic <slug> --auto-promote   # gate-checked intake → source_ref
#   first-party empirical (no public URL): platform=manual + source_kind=first_party_empirical[_table]
#   → mints researchos://first-party/<hash> (see methodology/first_party_empirical_playbook.md)
ros condense <slug> [--stage distill|aggregate|synthesize] # source → L3 → L2 → L1 → L0
ros report  <slug>                           # regenerate reports/world_model.md (live doc)
ros report  <slug> --session --facet f --query "q"         # append an immutable session report
ros gaps <slug> / ros review <slug>          # what's still thin / contested → next round
ros snapshot <slug>                          # export snapshots/<date>.sql (git-durable)
```

Method lane (Phase 4): `ros method add|ls|export|import` — durable "how to research this" M0/M1
invariants (pure logic, no source). `ros topic merge <src> <dst>` if two topics are one thread.
`ros lint` runs the boundary gates (also the Stop hook in `.claude/settings.json` and `.grok/hooks/boundary.json`, via `tools/hooks/run-boundary-lint.sh`).

## Sources — which collector, which skill (HARD constraints)

| source | collector | skill / tool |
|--------|-----------|--------------|
| web | 3-tier fallback | search: zhipu `web-search-prime` → `WebSearch` → **`multi-search-engine`** skill (quota-free URL scraping); fetch: zhipu `web-reader` → `WebFetch` → real-Chrome snapshot: `mcp__webbridge-mcp__*` (sub-agents) or `kimi-webbridge` skill (main loop) — JS/anti-bot/login only |
| X | `webbridge-mcp` or `kimi-webbridge` | **webbridge-mcp** MCP (:18061, sub-agent reachable) / **kimi-webbridge** skill (main loop) — same real login |
| 抖音 douyin | `webbridge-mcp` or `kimi-webbridge` | same real-Chrome bridge → transcribe video (explicit request only) |
| 小红书 xiaohongshu | `xiaohongshu-mcp` ONLY | **xiaohongshu-mcp** MCP / `researchos-xhs` / `ros xhs` |

> ✱ **Xiaohongshu must use `xiaohongshu-mcp`. kimi-webbridge / browser / `webbridge-mcp` are forbidden
> for XHS search** — the capture gate rejects it and `ros lint` re-audits (a general browser bridge,
> MCP or skill, must never touch XHS). Never navigate bare `/explore/{noteId}` (QR wall). MCP servers:
> `.mcp.json` (`ZHIPU_API_KEY` for zhipu; xiaohongshu-mcp on :18060; webbridge-mcp on :18061).
>
> ✱ **Web search is never a single provider** — walk the 3-tier chain and record
> `raw_tool_status.fallback_chain` + `quota_status` every search; all-fail → `degraded_reason`, never
> a silent empty. Full protocol: `methodology/web_search_provider_playbook.md`.
> ✱ **Control-plane isolation + anti-detection rulings** (why-MCP-not-skill / sub-agent reachability,
> isolated-profile换号陷阱, twscrape否决, account tiering, argv-scoped reaper):
> `methodology/social_access_playbook.md`. **`webbridge-mcp` (:18061) is the MCP proxy fronting the
> Kimi WebBridge real-Chrome daemon → it DOES propagate to spawned sub-agents**, so X/抖音 + browser
> web-reads are now sub-agent reachable (`xiaohongshu-mcp` + zhipu MCPs also propagate). `kimi-webbridge`
> stays a skill (main-loop only) as the equivalent/fallback. Process mgmt: `tools/social_mcp/`.

## Condense internals

`ros condense` is MAP → AGENT → REDUCE per stage. The AGENT step shells out to `claude -p`
(`ros/run/claude_cmd.sh`) with `methodology + one unit payload`; it emits strict JSON; REDUCE writes
through gated upserts. Resumable via `.out.json`; an L3-staleness guard re-derives L2/L1/L0 when L3
changes. Offline/tests: set `ROS_AGENT_CMD` to a stub (`tests/stub_agent.py`). Pin a model with
`ROS_MODEL`.

## Layout

`ros/` engine (storage, search, run, assembly, media, boundary, lib) · `control_plane/reasoning/methodology/`
agent protocols · `.agents/skills/researchos-*` operator skills · `topics/<slug>/` per-topic world
knowledge · `library/sources/<sha256>.json` shared originals. Live `.db` files are gitignored; durable
knowledge is committed as `topics/<slug>/snapshots/<date>.sql`.

## Travel guide generation

When the user asks for a travel plan / trip guide / weekend itinerary:

1. Follow `methodology/travel_guide_pattern.md` — the **social-media-first** evaluation protocol.
2. Use `.agents/skills/researchos-travel/SKILL.md` as the execution playbook.
3. HTML output goes to `topics/<slug>/plan.html`, styled per `methodology/travel_visual_style.md`
   (minimal single-column, green accent `#3d6b4f`, Leaflet map required).
4. Reusable skeleton: `.agents/skills/researchos-travel/template.html`.

Key rules (from methodology):
- **社媒活人评价 > 平台评分** (XHS/Douyin real-user reviews carry more weight than Dianping/Trip.com,
  which can be manipulated)
- **Every restaurant must have both good AND bad review excerpts** — only-positive = suspicious signal
- **Rank by review density − complaint severity**, not by star ratings
- **Three sections**: 行 (routes, concise table), 吃 (restaurants, detailed with review excerpts),
  住 (brief, 2–3 options)
- **Leaflet map required** in every output

For XHS search: `xiaohongshu-mcp` must run in headed mode (headless triggers XHS anti-bot).
If `xiaohongshu-mcp` is unavailable or repeatedly times out, fall back to `webbridge-mcp`
(which is inherently headed — it runs in the user's real Chrome with real login).
This is a narrow exception for travel research UX; core ResearchOS XHS capture still goes
through `xiaohongshu-mcp`.

## Tests

`python3 -m pytest tests/ -q` (30 tests; deterministic via the stub agent). `ros lint` must be clean.
