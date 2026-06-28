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
ros condense <slug> [--stage distill|aggregate|synthesize] # source → L3 → L2 → L1 → L0
ros report  <slug>                           # regenerate reports/world_model.md (live doc)
ros report  <slug> --session --facet f --query "q"         # append an immutable session report
ros gaps <slug> / ros review <slug>          # what's still thin / contested → next round
ros snapshot <slug>                          # export snapshots/<date>.sql (git-durable)
```

Method lane (Phase 4): `ros method add|ls|export|import` — durable "how to research this" M0/M1
invariants (pure logic, no source). `ros topic merge <src> <dst>` if two topics are one thread.
`ros lint` runs the boundary gates (also the `.claude/settings.json` Stop hook).

## Sources — which collector, which skill (HARD constraints)

| source | collector | skill / tool |
|--------|-----------|--------------|
| web | `web_search` (any tier) | `WebSearch`/`WebFetch`, or zhipu `web-search-prime` + `web-reader` MCP |
| X | `kimi-webbridge` | **kimi-webbridge** skill (user's real login) |
| 抖音 douyin | `kimi-webbridge` | **kimi-webbridge** skill → transcribe video |
| 小红书 xiaohongshu | `xiaohongshu-mcp` ONLY | **xiaohongshu-mcp** MCP / `researchos-xhs` / `ros xhs` |

> ✱ **Xiaohongshu must use `xiaohongshu-mcp`. kimi-webbridge / browser are forbidden for XHS search**
> — the capture gate rejects it and `ros lint` re-audits. Never navigate bare `/explore/{noteId}`
> (QR wall). MCP servers: `.mcp.json` (`ZHIPU_API_KEY` for zhipu; xiaohongshu-mcp on :18060).

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

## Tests

`python3 -m pytest tests/ -q` (30 tests; deterministic via the stub agent). `ros lint` must be clean.
