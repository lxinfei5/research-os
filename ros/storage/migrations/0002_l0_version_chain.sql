-- 0002_l0_version_chain.sql
--
-- The L0 world model is now a TRUE version chain: each synthesize run produces a new row (id derived
-- from slug + proposition + l1_ids content), the prior active row is archived, and supersedes_id
-- points to that real predecessor (not to itself, as the pre-0002 single-row model did).
--
-- All existing consumers already filter `WHERE status='active'`, so the schema change is transparent
-- to them; this migration only adds the indexes that make version-chain traversal + active filtering
-- efficient. schema_knowledge.sql stays the frozen v0 baseline; no columns are added or changed.

CREATE INDEX IF NOT EXISTS idx_l0_supersedes ON l0_worldview(supersedes_id);
CREATE INDEX IF NOT EXISTS idx_l0_status ON l0_worldview(status);
