---
name: researchos-grow
description: Run one full ResearchOS growth cycle for a topic — prime from existing knowledge, search the thin facets across sources, write them into the topic's knowledge.md, and refresh coverage. Use when the user wants to "grow"/"deepen"/"continue researching" a topic, or for a scheduled slow-grow.
---

# ResearchOS — Grow (one closed-loop cycle, no engine)

This is the system's heartbeat: **prior knowledge primes the next search; new results feed back to
grow the world model.** There is no `ros grow` — YOU the agent run the loop against the topic's
`knowledge.md`, guided by the floor rules in `rules/`.

## The loop

1. **Prime.** Read `topics/<slug>/knowledge.md`: the active **L0 worldview** (don't re-search it),
   the **L1 viewpoints**, the **未决问题**, and the **facet 覆盖** snapshot. Decide which thin facet
   or open question this cycle should pursue. (Prime invariants + decay modes + break_condition:
   `rules/prime_brief_protocol.md`.)

2. **Search the gaps.** For the chosen facet/question, pick a source and fetch via
   `researchos-search`: web (`WebSearch`/`WebFetch` + `multi-search-engine` fallback), X & Douyin
   (`webbridge-mcp` MCP / `kimi-webbridge` skill), Xiaohongshu (`researchos-xhs` multi-path).
   Transcribe video / OCR images to text FIRST (`researchos-media`). Respect pacing: same-platform
   serial, 2–5s waits, STOP on captcha/QR/logout (`rules/social_access_playbook.md`).

3. **Capture.** Save the raw payload to `topics/<slug>/captures/<session>.json` (query, source,
   collector used, items[], and `degraded_reason` if a source came back empty — a loud empty slot,
   never a silent one). A capture is replayable raw intake, not yet knowledge.

4. **Condense.** Distill + corroborate + synthesize the new sources into `knowledge.md` per
   `rules/floor-corpus.md` (three elements, single owner, stale-not-delete) and the condense
   contracts — see `researchos-condense`. Write provenance to `sources/<hash>.md` + one line in the
   `## 信源索引`.

5. **Refresh coverage.** Update `## facet 覆盖` in `knowledge.md` and the topic's row in
   `topics/_index.yaml` (coverage is a derived snapshot — recompute from the body). Optionally
   re-render `reports/world_model.md` (the human-readable view) and append `reports/sessions/`.

6. **Reassess + repeat.** What's still thin or contested? Loop back to step 1 until coverage is
   good or the budget is spent. Everything persists in git — commit when the cycle lands.

## Floor reminders (自觉, non-negotiable)

- Directional state (该买/退潮/目标价/conclusion-verdicts) is computed at read-time, **never**
  written into `knowledge.md` (`rules/floor-corpus.md`).
- Every fact carries proposition + provenance + valid_until; platform tag matches url host.
- `topics/_index.yaml` coverage and `## facet 覆盖` are derived snapshots — the body is truth.
