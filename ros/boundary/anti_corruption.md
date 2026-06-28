# Anti-Corruption — boundary gate rules (single source)

`ros lint` runs every gate below; nonzero exit means a rule was violated. The Stop hook
(`.claude/settings.json`) runs `ros lint` so regressions surface immediately.

1. **schema_drift** — every `topics/<slug>/knowledge.db` must be at the current migration version
   (`PRAGMA user_version == current_schema_version()`). A topic left behind a migration is a bug.

2. **collector_policy** — every retained capture must have used an ALLOWED collector for its source
   AND for each item's platform. This re-audits `sources.db` (defense-in-depth behind the
   capture-time gate): in particular, **no Xiaohongshu capture via kimi-webbridge/browser**.

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
