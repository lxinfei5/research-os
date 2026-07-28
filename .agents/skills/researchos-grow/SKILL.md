---
name: researchos-grow
description: Run one full ResearchOS growth cycle for a topic — prime from existing knowledge, search the thin facets across sources, capture, condense, and report. Use when the user wants to "grow"/"deepen"/"continue researching" a topic, or for a scheduled slow-grow.
---

# ResearchOS — Grow (one closed-loop cycle)

This is the engine's heartbeat: **prior knowledge primes the next search; new results feed back to
grow the world model.** One cycle:

```
ros grow <slug>            # prints the primed brief (frozen context_snapshot) + the plan
```

Then YOU (the agent) execute the loop the brief lays out:

1. **Prime.** Read the brief `ros grow <slug>` prints (or `ros brief <slug>`): the established
   worldview (don't re-search it), the open questions + thin/contested facets to pursue, and the
   recent queries NOT to repeat. (Prime-stage invariants + decay modes + break_condition:
   `control_plane/reasoning/methodology/prime_brief_protocol.md`.)

2. **Search the gaps.** For each thin facet / open question, pick a source and fetch with the ready
   skills (see `researchos-search`): web (`web-search-prime`/`web-reader`), X & Douyin
   (`webbridge-mcp` MCP, sub-agent reachable, or `kimi-webbridge` skill in the main loop),
   Xiaohongshu (multi-path: real Chrome `webbridge-mcp`/`kimi-webbridge` preferred, `xiaohongshu-mcp` fallback). Transcribe video / OCR images to text
   first (`ros media transcribe|ocr`). Respect: same-platform serial, 2–5s waits, STOP on
   captcha/QR/logout.

3. **Capture + condense.**
   ```
   ros capture <payload.json> --topic <slug> --auto-promote   # collector declared; gate enforced
   ros condense <slug>                                          # source → L3 → L2 → L1 → L0
   ros report  <slug>                                           # regenerate world_model.md
   ros report  <slug> --session --facet <f> --query "<q>"       # append the session report
   ```

4. **Reassess + repeat.** `ros gaps <slug>` / `ros review <slug>` show what's still thin or
   contested. Loop back to step 1 until coverage is good or the budget is spent.

5. **Persist durably.** `ros snapshot <slug>` writes `snapshots/<date>.sql` to commit to git.

## Scheduling a slow-grow

To grow a topic automatically on a cadence, use the `/schedule` (cloud routine) or `/loop` features
with a prompt like: *"Run the researchos-grow skill for topic `<slug>`: prime, search the two
thinnest facets, capture, condense, report."* Keep each run small (≤10 fetches/facet) and STOP on
any login wall — unattended runs must never invalidate the user's sessions.
