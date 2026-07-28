# Anti-Corruption — boundary gate rules (single source)

`ros lint` runs every gate below (the `ALL_GATES` tuple in `gates.py` — **13 gates**); nonzero exit
means a rule was violated. The Stop hook (`.claude/settings.json` + `.grok/hooks/boundary.json`) runs
`tools/hooks/run-boundary-lint.sh` → `ros lint` each turn, so regressions surface immediately. Gates
are pure checks (no writes); they VALIDATE the iron rule, never reason. If you add a gate to
`ALL_GATES`, document it here in the same change (keep this list == the tuple).

1. **schema_drift** — every `topics/<slug>/knowledge.db` must be at the current migration version
   (`PRAGMA user_version == current_schema_version()`). A topic left behind a migration is a bug.

2. **collector_policy** — every retained capture must have used an ALLOWED collector for its source
   AND for each item's platform. This re-audits `sources.db` (defense-in-depth behind the
   capture-time gate): it hard-fails only on a source's explicit `forbidden_search_collectors`
   list (off-list/unknown collectors are accepted with an advisory). Xiaohongshu has **no**
   forbidden list — it is multi-path (real-Chrome `webbridge-mcp`/`kimi-webbridge` preferred,
   `xiaohongshu-mcp` fallback; see `source_capabilities.yaml` + `xiaohongshu_search_playbook.md`).
   A companion gate, **webbridge_mcp_registry**, positively FAILS lint if XHS ever forbids
   `webbridge-mcp`/`kimi-webbridge` (guarding the multi-path invariant against regression).

3. **snapshot_provenance** — no evidence row may carry a `context_snapshot_id` that is absent from
   `context_snapshot_log` (forged provenance). The DB trigger blocks this on insert; the lint
   re-checks existing rows.

4. **import_acl** — layering ACL:
   - `ros/cli.py` imports the high-level engine (`ros.api`, runners, assembly, media, search) — it
     must NOT reach into `ros.storage.*` internals directly (go through `ros.api`).
   - `ros/storage/*` must NOT import upward (`ros.run`, `ros.assembly`, `ros.cli`). Storage is a
     leaf the higher layers depend on, never the reverse. (storage→search.capabilities is the one
     allowed peer edge: the capture gate.)

5. **db_git_safety** — `.gitignore` must exclude the live SQLite DBs (`topics/*/knowledge.db`,
   `topics/*/sources.db`). Committing a working DB risks `git checkout` clobbering it; durable
   knowledge is committed as `topics/<slug>/snapshots/<date>.sql` instead.

6. **l0_version_integrity** — the L0 version-chain invariant: exactly ONE active world model per
   topic, and any non-empty version chain must be well-formed (no self-supersession / dangling
   supersede edges). Protects the worldview layer from forking against itself.

7. **search_provider_registry** — the quota-free Tier-3 web fallback (`multi-search-engine` skill)
   referenced by the `web` collector policy must exist and parse (SKILL.md + config.json). Static
   guard so the 3-tier web chain (zhipu → runtime WebSearch → multi-search-engine) can't silently
   lose its last-resort tier; see `web_search_provider_playbook.md`.

8. **webbridge_mcp_registry** — `webbridge-mcp` (the :18061 MCP proxy fronting the Kimi WebBridge
   real-Chrome daemon :10086) must be registered in `.mcp.json` and its source tree present, so
   workflow sub-agents can reach X / 抖音 / 小红书 / login-gated web. Positively FAILS if XHS forbids
   `webbridge-mcp`/`kimi-webbridge`, or if x/douyin/xiaohongshu drop it from their allow-list — i.e.
   it guards the multi-path invariant, the inverse of a ban.

9. **source_ref_host_platform** — platform-label honesty at the RETENTION layer
   (`knowledge.db.source_ref`), XHS-scoped and one-directional: any retained row whose `source_ref`
   URL host is a Xiaohongshu origin MUST declare `platform=xiaohongshu` (not `web`). Browser
   collection of XHS is allowed; relabeling an XHS scrape as `web` is what this catches (it corrupts
   facet coverage + cross-platform corroboration counts). It does not check the reverse direction or
   non-XHS hosts.

10. **web_search_evidence** — public-WEB search/detail/fetch captures must carry
    `raw_tool_status.fallback_chain` (W-08/#29) so the 3-tier path + quota state is auditable.
    Legacy rows with NULL `raw_tool_status` are ADVISORY (non-blocking); new captures must record it.

11. **snapshot_freshness** — ADVISORY (NON-blocking): warn when a live `knowledge.db` holds research
    newer than its latest committed snapshot, prompting `ros snapshot <slug>` before the work is lost.

12. **credibility_orphans** — flag `credibility_assessment` rows whose subject L-row no longer exists
    (W-21/#36), so credibility judgments don't dangle against deleted knowledge.

13. **no_llm_sdk** — the iron rule ("Python never reasons or calls an LLM") enforced as an SDK-import
    guard: NO module under `ros/` may `import anthropic` / `import openai`. The only sanctioned LLM
    call is the condense AGENT step shelling out to `claude -p` via `ros/run/claude_cmd.sh`;
    `ros/media` perception (whisper/OCR) is subprocess/MCP, not an SDK import. A stray
    `subprocess`→`claude` outside `ros/run` is left to the prose `break_condition` in AGENTS.md
    (subprocess args are too fuzzy to gate without false-positiving on `ros/media` perception).
