# ResearchOS

A personal, multi-topic research system. You open a research **topic**, search many sources
(public web + X / 抖音 / 小红书), and the findings are condensed into that topic's own layered
**L0–L3 world knowledge**. Each topic is physically isolated — **N topics = N knowledge bases** —
so today's geopolitics thread and tomorrow's trading-methodology thread never bleed into each
other. Originals are retained (link + cached text; video/image transcribed to text first), and each
new search is primed by what the topic already knows, then feeds back to grow it.

Full design: **[DESIGN.md](DESIGN.md)**.

Engine principle (from AStockOS): **Python never reasons or calls an LLM.** It only orchestrates,
counts, validates, and persists. Semantic work is done by agents reading versioned methodology,
handed back through gated writers.

---

## Status — Phase 0 (foundation) ✅

Built so far:

- **`ros/storage/schema_knowledge.sql`** — frozen v0 baseline for the per-topic `knowledge.db`:
  evidence lane `l3_claim → l2_finding → l1_viewpoint → l0_worldview`, the method lane
  (`method_rule`, dormant until Phase 4), `source_ref` (URL gate), `credibility_assessment`,
  `knowledge_change_log` (audit), `facet`/`open_question`, `context_snapshot_log`, `controlled_vocab`.
- **`ros/storage/knowledge.py`** — connection + forward-only migration runner (`PRAGMA user_version`),
  whole-blob upserts with append-only audit, credibility (5-axis + echo-chamber circuit breaker),
  `add_source_ref`, corroboration counting, coverage/snapshot reads.
- **`ros/storage/intake.py`** — the `sources.db` raw-intake sidecar: `record_capture` + URL-gated
  `promote_item`/`bulk_promote`.
- **`ros/library.py`** — global content-addressed original store (`library/sources/<sha256>.json`)
  with `referenced_by_topics[]`; per-topic cache snapshots.
- **`ros/topics.py`** — topic registry (`topics/_index.yaml`) with alias resolution, scaffolding,
  lifecycle.
- **`ros/cli.py`** — `ros topic|facet|capture|promote|db|lint`.

## Status — Phase 1 (MVP: search policy + condense + report) ✅

- **`ros/search/`** — `source_capabilities.yaml` + `capabilities.py`: the collector POLICY GATE,
  enforced inside `record_capture` as a **soft gate** (off-list/missing → warn, still write;
  only explicit forbids hard-reject). **Xiaohongshu is multi-path:** real Chrome
  (`webbridge-mcp` / `kimi-webbridge`) preferred; `xiaohongshu-mcp` is soft fallback.
- **`ros/lib/xiaohongshu_mcp_bridge.py`** + `ros xhs status|tools|call` — the XHS
  anti-bot fallback path (local JSON-RPC, loopback-only, destructive-tool blocked);
  real-Chrome `webbridge-mcp` / `kimi-webbridge` is preferred, this MCP path is the fallback.
- **`ros/run/condense.py`** — the 3-stage map-reduce: `distill` (source→L3), `aggregate`
  (L3→corroborated L2), `synthesize` (L2→L1 viewpoints + L0 worldview + open questions).
  MAP→AGENT→REDUCE; the AGENT step is `claude -p` (`ros/run/claude_cmd.sh`) or `ROS_AGENT_CMD`
  for offline runs. Resumable via `.out.json`; L3-staleness guard re-derives L2/L1/L0.
- **`ros/run/report.py`** + `ros report` — deterministic `world_model.md` render (worldview,
  open questions, themes, corroborated findings, source index w/ links + cache paths, facets).
- **`control_plane/reasoning/methodology/*.md`** — the versioned agent protocols (layering,
  credibility, distill/aggregate/synthesize, XHS playbook, report template).
- **`.agents/skills/researchos-{search,condense,xhs}/`** — operator skills.
- CLI added: `ros search` (plan+policy), `ros condense`, `ros report`, `ros xhs`.

## Status — Phase 2 (priming loop + media→text) ✅

- **`ros/storage/migrations/0001_search_log.sql`** — first forward-only migration (knowledge.db now
  at schema **v1**); `record_search`/`recent_searches`.
- **`ros/assembly/`** — `gap.py` (per-facet coverage metrics: L3/L2 counts, corroboration depth,
  recency), `stage.py` (research-stage resolver scoping→…→mature), `context.py` (`assemble_brief`:
  load-all L0+L1+open-questions+facet-gaps+recent-queries → **freeze a context_snapshot** → a brief
  that says what's established / what to pursue / what not to re-search).
- **`ros/media/`** — `transcribe.py` (video→text: whisper-cli + afconvert tool-resolution ladder,
  graceful `status:failed`, `stub` backend) and `image_ocr.py` (agent-driven zai-mcp path +
  tesseract/paddleocr local fallback).
- **`ros/run/report.py`** — `write_session_report` (append-only `reports/sessions/<date>_<facet>.md`).
- CLI added: `ros brief` / `ros gaps` / `ros review` / `ros media transcribe|ocr` /
  `ros report --session`; `ros search --facet` now logs to the durable search log.

## Status — Phase 3 (multi-topic scaling + governance) ✅

- **Cross-topic `library` sharing** — the same URL captured under two topics is stored ONCE
  (`library/sources/<sha256>.json`, `referenced_by_topics[]`); each topic keeps its OWN `source_ref`
  + cache + L0–L3 (no contamination). `ros library ls|show|link` (`link` reuses a retained source
  into another topic without re-fetching); `shares_source` edges auto-written to `_index.yaml`.
- **Boundary gates** (`ros/boundary/gates.py` `ALL_GATES` — **13 gates**; documented one-per-line in
  `ros/boundary/anti_corruption.md`, the single source — keep the two in sync) run by `ros lint`.
  Spotlights: `collector_policy` (re-runs `validate_collector`; hard-fails ONLY on an explicit
  forbidden list — XHS has none, browser is a preferred path), `webbridge_mcp_registry` (the :18061
  proxy is registered + FAILS if XHS forbids webbridge-mcp/kimi-webbridge, guarding multi-path), and
  `no_llm_sdk` (iron rule: no `anthropic`/`openai` SDK import anywhere in `ros/`). Stop hook
  (`.claude/settings.json` + `.grok/hooks/boundary.json`) runs `tools/hooks/run-boundary-lint.sh` →
  `ros lint` each turn.
- **`ros snapshot`** — export durable knowledge → `snapshots/<date>.sql` (git-committed; live `.db`
  stays gitignored). **`ros resediment [--force]`** — drift re-condense (re-derive from current
  sources after a source was enriched / edited).

## Status — Phase 4 + real wiring (COMPLETE) ✅

- **Real search/condense wired** — `.mcp.json` (xiaohongshu-mcp + zhipu `web-search-prime`/`web-reader`),
  `.env.example`; the condense AGENT step runs real `claude -p` (verified producing quality L3).
  Skills name the ready tools: **webbridge-mcp** (:18061, X/抖音 + login-gated web, sub-agent
  reachable) or **kimi-webbridge** skill (same real Chrome, main-loop only), **xiaohongshu-mcp** (XHS),
  zhipu (web). Process mgmt: `tools/social_mcp/social_mcp_daemon.sh`.
  `ros grow` + `researchos-grow` skill drive one closed-loop cycle (prime → search → condense →
  report → reassess); schedulable via `/loop` or `/schedule`.
- **Method lane (M0/M1)** — `ros method add|ls|export|import`; durable "how to research this"
  invariants (pure logic, NO source/credibility, physically isolated from evidence). Cross-topic
  reuse via `topics/_shared/method.db` with a **fresh-condense gate** (imports land as `draft`).
- **`ros topic merge`** — escape hatch when two topics are one thread: links src's sources into dst
  (dst re-distills; no evidence-row copy) and archives src.
- **Operator guide** — `AGENTS.md` (+ `CLAUDE.md` symlink).

**All phases complete.** 30 tests green; `ros lint` clean. To run for real: set `ZHIPU_API_KEY`,
start the local `xiaohongshu-mcp` server (:18060), and use the `researchos-grow` / `researchos-search`
skills. See `AGENTS.md`.

---

## Quickstart

```bash
pip install -r requirements.txt

# A file named `ros` can't sit next to the ros/ package dir, so the wrapper is ros.sh.
# Either alias it, or just call the module form.
alias ros='./ros.sh'              # optional
python3 -m ros --help             # equivalent to `ros --help`

# 1. open a research topic (scaffolds topics/<slug>/ + knowledge.db + sources.db)
ros topic new geopolitics --title "2026 地缘政治格局" --alias 地缘政治
ros facet add "台海军事/外交动向"

# 2. see the per-source search plan + collector policy (the fetch is agent-driven via a skill)
ros search "台海 半导体 出口管制" --source web,xiaohongshu

# 3. record what an agent gathered (a capture payload), then URL-gate it into retained sources
ros capture my_capture.json --auto-promote

# 4. condense source → L3 → L2 → L1 → L0, then render the living world model
ros condense geopolitics          # set ROS_AGENT_CMD to a stub for offline runs (see tests/)
ros report  geopolitics           # → topics/<slug>/reports/world_model.md
ros topic open geopolitics        # world-model summary + coverage

# 5. verify / snapshot
ros db verify
ros db dump                       # → topics/<slug>/snapshots/<date>.sql  (git-durable)

# Xiaohongshu (anti-bot fallback path): needs a local xiaohongshu-mcp server on :18060
ros xhs status
ros xhs call --tool search_feeds --args-json '{"keyword":"地缘政治"}'
```

### Capture payload shape

```json
{
  "query": "台海 半导体 出口管制",
  "source": "web",
  "collector": "web_search",
  "items": [
    {"platform": "web", "source_kind": "article", "url": "https://example.com/a",
     "title": "…", "author": "…", "content": "全文（视频/图片已转写为文本）…"},
    {"platform": "xiaohongshu", "source_kind": "note", "restricted_reason": "detail behind login",
     "content": "列表卡片元数据…"}
  ]
}
```

The URL gate: items with a real `http(s)` URL promote into `source_ref` (+ cache snapshot + library
entry). Url-less items normally need a `restricted_reason`, stay raw-only, and are skipped on
promote — **except** no-public-URL intentional retention:

- **first-party empirical** (`source_kind=first_party_empirical*`) — field tests / quota tables
- **user briefing** (`source_kind=user_briefing`) — conversation knowledge the user told the agent

Both require `platform=manual` and mint `researchos://first-party/<content_hash>`. See
`methodology/first_party_empirical_playbook.md`.

Degraded search (all providers failed): `items: []` + `degraded_reason` is a valid loud empty slot
(no fake placeholder required).

## Tests

```bash
python3 -m pytest tests/ -q
```
