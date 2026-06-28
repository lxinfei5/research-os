-- ResearchOS — per-topic knowledge.db canonical schema (v0 BASELINE)
--
-- ⚠ This file is the FROZEN v0 BASELINE. The CURRENT schema is this file ∪
--   ros/storage/migrations/NNNN_*.sql applied in order (tracked by PRAGMA user_version).
--   Do NOT edit the CREATE TABLE DDL below to evolve the schema — add a numbered migration in
--   ros/storage/migrations/ instead. Comment edits are OK. (Pattern ported from AStockOS
--   data/schema.sql + its migration runner.)
--
-- ONE knowledge.db PER TOPIC. Physical isolation IS the "N copies of world knowledge"
--   requirement — there is no global topic_id column. The raw-intake side (sources.db) uses a
--   DIFFERENT, deliberately simpler evolution model (inline SCHEMA + check-then-ALTER in
--   ros/storage/intake.py, also stamped with PRAGMA user_version). Two models coexist by design.
--
-- Two physically-isolated knowledge lanes:
--   * EVIDENCE lane (information-abstraction axis) — every row REQUIRES source_ref + credibility:
--       l3_claim     L3 = a single-source proposition distilled from one original item
--       l2_finding   L2 = a multi-source CORROBORATED finding (corroboration is L2's defining trait)
--       l1_viewpoint L1 = a synthesized viewpoint per facet / sub-question / angle
--       l0_worldview L0 = the topic's macro world model + open questions (NEVER pruned)
--   * METHOD lane (logic-generality axis, Phase 4 — table present in baseline, unused until then):
--       method_rule  M0 = topic-general method invariants; M1 = stage/facet conditional heuristics
--                    (pure logic — NO source_ref, NO credibility). Lanes never merge: a high-density
--                    single-source claim can never masquerade as a verified method.
--
-- Iron rules at DB level: real FK, controlled vocab, source_ref URL required (kills placeholders),
--   append-only audit (knowledge_change_log), append-only context freeze (context_snapshot_log).
-- Idempotent: CREATE ... IF NOT EXISTS, safe to re-run. Write-gate TRIGGERS live in triggers.sql
--   (re-asserted after every migration run), NOT here.

PRAGMA foreign_keys = ON;

-- =====================================================================
-- CONTROLLED VOCABULARY — governed enums (platform, source_kind, ...).
-- =====================================================================
CREATE TABLE IF NOT EXISTS controlled_vocab (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    vocab_name       TEXT NOT NULL,
    canonical_value  TEXT NOT NULL,
    alias            TEXT,
    status           TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','retired')),
    UNIQUE (vocab_name, canonical_value, alias)
);
CREATE INDEX IF NOT EXISTS idx_vocab_lookup ON controlled_vocab(vocab_name);

-- =====================================================================
-- PROVENANCE — source_ref is the durable RETENTION record (link + cached
--   text + media transcript), independent of which L-row cites it. L rows
--   reference it through their source_ref_ids JSON arrays. URL required.
--   subject_type/subject_id are an OPTIONAL "primary subject" hint (a source
--   may be promoted/retained before any L-row distils from it → nullable).
-- =====================================================================
CREATE TABLE IF NOT EXISTS source_ref (
    id                    TEXT PRIMARY KEY,        -- src-<hash>
    subject_type          TEXT CHECK (subject_type IN
                            ('l3_claim','l2_finding','l1_viewpoint','l0_worldview','pending')),
    subject_id            TEXT,
    platform              TEXT NOT NULL,           -- controlled vocab (source_platform)
    source_kind           TEXT NOT NULL,           -- controlled vocab (source_kind)
    url                   TEXT NOT NULL,           -- real verifiable URL; empty/'dataset' REJECTED
    author                TEXT,
    title                 TEXT,
    content_hash          TEXT,                    -- → library/sources/<hash>.json
    cached_text_path      TEXT,                    -- per-topic cache/<hash>.md snapshot
    media_transcript_path TEXT,                    -- video ASR / image OCR text, if any
    intake_item_id        TEXT,                    -- sources.db source_item this was promoted from
    captured_at           TEXT,
    captured_by           TEXT,
    valid_to              TEXT,
    created_at            TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_source_subject ON source_ref(subject_type, subject_id);
CREATE INDEX IF NOT EXISTS idx_source_hash ON source_ref(content_hash);

-- =====================================================================
-- CREDIBILITY — agent-judged (5-axis). Every evidence-lane L row FK-points
--   here. rationale + filter_trace required (never silent). echo_chamber_flag
--   lets the credibility recorder mechanically cap level→low (circuit breaker).
-- =====================================================================
CREATE TABLE IF NOT EXISTS credibility_assessment (
    id                 TEXT PRIMARY KEY,           -- cred-<hash>
    subject_type       TEXT NOT NULL CHECK (subject_type IN
                         ('l3_claim','l2_finding','l1_viewpoint','l0_worldview')),
    subject_id         TEXT NOT NULL,
    level              TEXT NOT NULL CHECK (level IN ('low','medium','high')),
    rationale          TEXT NOT NULL,
    filter_trace       TEXT NOT NULL,              -- JSON: independence / hype / recency checks
    independence_note  TEXT,
    echo_chamber_flag  INTEGER NOT NULL DEFAULT 0,
    calibration_basis  TEXT,
    status             TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','archived')),
    run_id             TEXT,
    assessed_at        TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_cred_subject ON credibility_assessment(subject_type, subject_id);

-- =====================================================================
-- EVIDENCE LANE — L3 (single-source claim)
-- =====================================================================
CREATE TABLE IF NOT EXISTS l3_claim (
    id                    TEXT PRIMARY KEY,         -- sc-<hash>
    facet                 TEXT,
    proposition           TEXT NOT NULL,            -- the real point, not a verbatim truncation
    claim_kind            TEXT NOT NULL CHECK (claim_kind IN
                            ('fact','analysis','rumor','breaking','opinion','data','other')),
    source_kind           TEXT CHECK (source_kind IN
                            ('article','post','video','image','forum','paper','other')),
    single_source_ref_id  TEXT NOT NULL REFERENCES source_ref(id),
    source_ref_ids        TEXT NOT NULL,            -- JSON array; kept = [single_source_ref_id ∪ ...]
    verbatim_excerpt      TEXT,
    cached_text_hash      TEXT,                     -- → library/sources/<hash>.json
    analysis_note         TEXT,
    filter_trace          TEXT NOT NULL,            -- JSON: independence / hype / recency
    debate_trace          TEXT,                     -- JSON: pro / con / synthesis rounds
    credibility_id        TEXT NOT NULL REFERENCES credibility_assessment(id),
    parent_l2_id          TEXT,
    lifecycle             TEXT,
    status                TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','archived')),
    run_id                TEXT,
    context_snapshot_id   TEXT,
    context_hash          TEXT,
    created_at            TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at            TEXT NOT NULL DEFAULT (datetime('now')),
    updated_by            TEXT NOT NULL DEFAULT 'analysis',
    audit_note            TEXT,
    CHECK (source_ref_ids NOT IN ('','[]','null','[ ]'))
);
CREATE INDEX IF NOT EXISTS idx_l3_facet ON l3_claim(facet);
CREATE INDEX IF NOT EXISTS idx_l3_parent ON l3_claim(parent_l2_id);

-- =====================================================================
-- EVIDENCE LANE — L2 (multi-source corroborated finding)
-- =====================================================================
CREATE TABLE IF NOT EXISTS l2_finding (
    id                    TEXT PRIMARY KEY,         -- sf-<hash>
    facet                 TEXT,
    finding_type          TEXT NOT NULL CHECK (finding_type IN
                            ('fact','event','figure','claim','trend')),
    statement             TEXT NOT NULL,
    value_text            TEXT,
    value_num             REAL,
    unit                  TEXT,
    valid_from            TEXT,
    valid_to              TEXT,
    corroboration_count   INTEGER NOT NULL DEFAULT 1,   -- = #independent source_ref_ids (mechanical)
    cross_platform_count  INTEGER NOT NULL DEFAULT 1,   -- = #distinct platforms (mechanical)
    corroboration_sources TEXT,                         -- JSON list (written by _corroborate)
    conflict_note         TEXT,                         -- agent records contradictions
    source_ref_ids        TEXT NOT NULL,                -- JSON array
    credibility_id        TEXT NOT NULL REFERENCES credibility_assessment(id),
    l3_ids                TEXT,                         -- JSON array of l3_claim.id
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
CREATE INDEX IF NOT EXISTS idx_l2_facet ON l2_finding(facet);
CREATE INDEX IF NOT EXISTS idx_l2_parent ON l2_finding(parent_l1_id);

-- =====================================================================
-- EVIDENCE LANE — L1 (synthesized viewpoint)
-- =====================================================================
CREATE TABLE IF NOT EXISTS l1_viewpoint (
    id                  TEXT PRIMARY KEY,           -- vp-<hash>
    facet               TEXT,
    sub_question        TEXT,
    viewpoint_scope     TEXT,                       -- JSON {angle, role, stance}
    synthesis_kind      TEXT NOT NULL CHECK (synthesis_kind IN
                          ('theme','sub_question','viewpoint','contrarian')),
    narrative           TEXT NOT NULL,
    stance              TEXT CHECK (stance IN
                          ('established','contested','emerging','refuted','uncertain')),
    l2_ids              TEXT,                       -- JSON array of l2_finding.id
    open_questions      TEXT,                       -- JSON array
    confidence          TEXT CHECK (confidence IN ('low','medium','high')),
    source_ref_ids      TEXT NOT NULL,
    credibility_id      TEXT NOT NULL REFERENCES credibility_assessment(id),
    parent_l0_id        TEXT,
    rank                INTEGER,
    status              TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','archived')),
    run_id              TEXT,
    context_snapshot_id TEXT,
    context_hash        TEXT,
    created_at          TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at          TEXT NOT NULL DEFAULT (datetime('now')),
    updated_by          TEXT NOT NULL DEFAULT 'analysis',
    audit_note          TEXT,
    CHECK (source_ref_ids NOT IN ('','[]','null','[ ]'))
);
CREATE INDEX IF NOT EXISTS idx_l1_facet ON l1_viewpoint(facet);

-- =====================================================================
-- EVIDENCE LANE — L0 (topic world model; NEVER pruned)
-- =====================================================================
CREATE TABLE IF NOT EXISTS l0_worldview (
    id                  TEXT PRIMARY KEY,           -- wv-<hash>
    summary_kind        TEXT NOT NULL CHECK (summary_kind IN
                          ('state_of_understanding','consensus','tension','frontier','other')),
    proposition         TEXT NOT NULL,
    scope               TEXT,                       -- JSON
    key_findings        TEXT,                       -- JSON: array of l2_finding.id
    open_questions      TEXT,                       -- JSON: drives the feedback loop
    confidence          TEXT CHECK (confidence IN ('low','medium','high')),
    supersedes_id       TEXT,                       -- prior worldview (chain)
    l1_ids              TEXT,                       -- JSON array of l1_viewpoint.id
    source_ref_ids      TEXT NOT NULL,
    credibility_id      TEXT NOT NULL REFERENCES credibility_assessment(id),
    status              TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','archived')),
    run_id              TEXT,
    context_snapshot_id TEXT,
    context_hash        TEXT,
    created_at          TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at          TEXT NOT NULL DEFAULT (datetime('now')),
    updated_by          TEXT NOT NULL DEFAULT 'analysis',
    audit_note          TEXT,
    CHECK (source_ref_ids NOT IN ('','[]','null','[ ]'))
);

-- =====================================================================
-- METHOD LANE — M0/M1 (pure logic, NO source_ref/credibility). Phase 4.
-- =====================================================================
CREATE TABLE IF NOT EXISTS method_rule (
    id           TEXT PRIMARY KEY,                  -- mr-<hash>
    level        TEXT NOT NULL CHECK (level IN ('M0','M1')),
    proposition  TEXT NOT NULL,
    valid_if     TEXT,                              -- M1: JSON {stage, facet, condition}; M0: NULL
    wrong_if     TEXT,
    status       TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','retired','draft')),
    created_at   TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at   TEXT NOT NULL DEFAULT (datetime('now')),
    updated_by   TEXT NOT NULL DEFAULT 'analysis'
);

-- =====================================================================
-- FACETS / OPEN QUESTIONS — the gap map that drives priming + feedback.
-- =====================================================================
CREATE TABLE IF NOT EXISTS facet (
    id               TEXT PRIMARY KEY,              -- f_<slug>
    question         TEXT NOT NULL,
    status           TEXT NOT NULL DEFAULT 'open' CHECK (status IN
                       ('open','survey','deepening','saturating','closed')),
    last_searched_at TEXT,
    created_at       TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS open_question (
    id               TEXT PRIMARY KEY,              -- oq-<hash>
    question         TEXT NOT NULL,
    facet_id         TEXT,
    status           TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open','answered','stale')),
    spawned_from_l_id TEXT,
    answered_by_l_id  TEXT,
    created_at       TEXT NOT NULL DEFAULT (datetime('now'))
);

-- =====================================================================
-- AUDIT (append-only). Gated writers do whole-blob read-modify-write and log
--   here. The audit table itself is never audited (no trigger on it).
-- =====================================================================
CREATE TABLE IF NOT EXISTS knowledge_change_log (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name    TEXT NOT NULL,
    row_id        TEXT NOT NULL,
    column_name   TEXT NOT NULL,
    change_kind   TEXT NOT NULL CHECK (change_kind IN
                    ('insert','update','dedup_skip','archive','budget_warn','json_warn')),
    old_blob      TEXT,
    new_blob      TEXT,
    diff_summary  TEXT,
    changed_by    TEXT NOT NULL,
    changed_at    TEXT NOT NULL DEFAULT (datetime('now')),
    audit_note    TEXT
);

-- =====================================================================
-- CONTEXT FREEZE (append-only) — every knowledge write can carry the exact
--   primed context it saw (run_id / context_snapshot_id / context_hash).
-- =====================================================================
CREATE TABLE IF NOT EXISTS context_snapshot_log (
    snapshot_id   TEXT PRIMARY KEY,
    payload       TEXT,
    content_hash  TEXT,
    freeze_policy TEXT,
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);
