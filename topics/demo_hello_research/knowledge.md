---
slug: demo_hello_research
title: "Demo: multi-source research loop (synthetic)"
status: open
stage: demo
coverage: L0=1 L1=1 L2=1 L3=1 src=1
last_grown_at: "2026-08-12"
---

# Demo: multi-source research loop (synthetic) — world knowledge

> **Synthetic demo only.** Numbers and sources below are illustrative so you can see the shape of a grown topic without personal or scraped corpora.

## L0 世界观 (near-constant)

### active · 2026-08-12

- **(world_model · confidence:A)** A durable research OS separates **intake** (captures), **claims** (L3), **corroboration** (L2), **viewpoint synthesis** (L1), and **world model** (L0). Collapsing them into one chat transcript loses auditability.
- **(world_model · confidence:A)** Empty evidence slots must be loud (`degraded_reason`); fluent reports that never searched a required channel are a primary failure mode.

## L1 视角 (slow)

- **(synthesis · confidence:A)** The minimal closed loop is Prime → Search → Capture → Distill → Condense → Coverage refresh. Priming from L0/L1 prevents re-searching settled ground.

## L2 印证事实 (multi-source)

- **(as-of 2026-08-12)** Multi-agent coding environments load project skills from a skills directory and a constitution file (e.g. `AGENTS.md`), enabling repeatable research handbooks without a custom orchestrator binary. — provenance: public agent tooling docs · valid_until: 2027-01-01

## L3 单源主张

- **[demo-src-001]** “Skills are advisory prose the agent executes; they are not a compile-time workflow engine.” — provenance: demo synthetic note · valid_until: 2027-01-01

## 未决问题

- [ ] How should facet coverage be auto-recomputed without reintroducing a DB gate?
- [ ] What’s the cleanest packaging for optional browser MCP on Windows vs macOS?

## facet 覆盖

| facet | status | notes |
|---|---|---|
| loop_shape | covered | L0/L1 describe the loop |
| tooling_surface | thin | only high-level claim |
| evaluation | thin | no benchmarks yet |

## 信源索引

| hash | platform | title | as_of |
|---|---|---|---|
| demo-src-001 | synthetic | Demo note on skills vs engines | 2026-08-12 |
