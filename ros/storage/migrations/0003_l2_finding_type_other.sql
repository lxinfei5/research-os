-- 0003_l2_finding_type_other.sql
--
-- Add the NEUTRAL 'other' bucket to l2_finding.finding_type (W-13). The aggregate agent sometimes
-- emits a near-synonym ('data' / 'analysis' / 'observation') that isn't in the CHECK whitelist.
-- Without a neutral bucket, _reduce_aggregate silently REWROTE it to the meaning-bearing 'claim' —
-- a semantic classification Python is forbidden to make (the iron rule). L3's claim_kind already
-- carries 'other' for exactly this reason; L2 was the asymmetry. Now unrecognized types map to
-- 'other' (neutral) instead of 'claim'.
--
-- SQLite cannot ALTER a CHECK in place, so this is the standard controlled rebuild: create __new
-- with the widened CHECK, copy verbatim, drop, rename, reassert indexes. The migration runner
-- turns FK off and wraps us in one txn; credibility_id rows survive the copy. The snapshot-provenance
-- trigger drops with the old table and is reasserted by reapply_triggers() at end of apply_migrations.

CREATE TABLE l2_finding__new (
    id                    TEXT PRIMARY KEY,
    facet                 TEXT,
    finding_type          TEXT NOT NULL CHECK (finding_type IN
                            ('fact','event','figure','claim','trend','other')),
    statement             TEXT NOT NULL,
    value_text            TEXT,
    value_num             REAL,
    unit                  TEXT,
    valid_from            TEXT,
    valid_to              TEXT,
    corroboration_count   INTEGER NOT NULL DEFAULT 1,
    cross_platform_count  INTEGER NOT NULL DEFAULT 1,
    corroboration_sources TEXT,
    conflict_note         TEXT,
    source_ref_ids        TEXT NOT NULL,
    credibility_id        TEXT NOT NULL REFERENCES credibility_assessment(id),
    l3_ids                TEXT,
    parent_l1_id          TEXT,
    status                TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','archived')),
    run_id                TEXT,
    context_snapshot_id   TEXT,
    context_hash          TEXT,
    created_at            TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at            TEXT NOT NULL DEFAULT (datetime('now')),
    updated_by            TEXT NOT NULL DEFAULT 'analysis',
    audit_note            TEXT,
    CHECK (source_ref_ids NOT IN ('','[]','null','[ ]')),
    CHECK (corroboration_count >= 1),
    CHECK (cross_platform_count >= 1)
);

INSERT INTO l2_finding__new (id, facet, finding_type, statement, value_text, value_num, unit,
    valid_from, valid_to, corroboration_count, cross_platform_count, corroboration_sources,
    conflict_note, source_ref_ids, credibility_id, l3_ids, parent_l1_id, status, run_id,
    context_snapshot_id, context_hash, created_at, updated_at, updated_by, audit_note)
SELECT id, facet, finding_type, statement, value_text, value_num, unit,
    valid_from, valid_to, corroboration_count, cross_platform_count, corroboration_sources,
    conflict_note, source_ref_ids, credibility_id, l3_ids, parent_l1_id, status, run_id,
    context_snapshot_id, context_hash, created_at, updated_at, updated_by, audit_note
FROM l2_finding;

DROP TABLE l2_finding;
ALTER TABLE l2_finding__new RENAME TO l2_finding;

CREATE INDEX IF NOT EXISTS idx_l2_facet ON l2_finding(facet);
CREATE INDEX IF NOT EXISTS idx_l2_parent ON l2_finding(parent_l1_id);
