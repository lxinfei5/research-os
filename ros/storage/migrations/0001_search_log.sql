-- 0001_search_log.sql
--
-- Durable per-topic search log in the canonical knowledge.db. The raw-intake sidecar (sources.db)
-- is gitignored/replayable, so "what have I already searched for this topic" needs a home in the
-- durable DB to prime the next round (ros brief: don't re-run recent queries; drive thin facets).
-- This is the first forward-only migration — schema_knowledge.sql stays the frozen v0 baseline.

CREATE TABLE IF NOT EXISTS search_log (
    id           TEXT PRIMARY KEY,                 -- sl-<hash>
    query        TEXT NOT NULL,
    source       TEXT,                             -- web / x / douyin / xiaohongshu / ...
    facet        TEXT,                             -- facet this search targeted (nullable)
    run_id       TEXT,
    result_note  TEXT,                             -- optional: counts / outcome the agent recorded
    searched_at  TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_search_log_facet ON search_log(facet, searched_at);
CREATE INDEX IF NOT EXISTS idx_search_log_time ON search_log(searched_at);
