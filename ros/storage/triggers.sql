-- ResearchOS — write-gate TRIGGERS (single source of truth).
--
-- Re-asserted by reapply_triggers() at the end of every apply_migrations() run, so a table-rebuild
-- migration that dropped a trigger self-heals. CREATE TRIGGER IF NOT EXISTS = no-op when present,
-- heal when dropped. Add any NEW write-gate trigger HERE (not only in a migration). Ported from
-- AStockOS data/triggers.sql.

-- ---------------------------------------------------------------------
-- URL GATE — source_ref.platform/source_kind must be in controlled_vocab and
--   url must be a real verifiable URL (empty / 'dataset' placeholders REJECTED).
--   This is the unbypassable provenance gate for every retained source.
-- ---------------------------------------------------------------------
CREATE TRIGGER IF NOT EXISTS trg_source_ref_url_gate BEFORE INSERT ON source_ref
BEGIN
    SELECT CASE WHEN NEW.url IS NULL OR trim(NEW.url) = '' OR lower(NEW.url) = 'dataset'
        THEN RAISE(ABORT, 'source_ref.url must be a real verifiable URL (empty/dataset placeholders forbidden)') END;
    SELECT CASE WHEN NOT EXISTS (
        SELECT 1 FROM controlled_vocab v
        WHERE v.vocab_name='source_platform' AND v.status='active'
          AND (v.canonical_value=NEW.platform OR v.alias=NEW.platform)
    ) THEN RAISE(ABORT, 'source_ref.platform not in controlled_vocab(source_platform)') END;
    SELECT CASE WHEN NOT EXISTS (
        SELECT 1 FROM controlled_vocab v
        WHERE v.vocab_name='source_kind' AND v.status='active'
          AND (v.canonical_value=NEW.source_kind OR v.alias=NEW.source_kind)
    ) THEN RAISE(ABORT, 'source_ref.source_kind not in controlled_vocab(source_kind)') END;
END;

-- ---------------------------------------------------------------------
-- PROVENANCE FREEZE GATE — a non-empty context_snapshot_id on any evidence row
--   must reference a real frozen snapshot (forged provenance is a real hazard).
--   One trigger per table (SQLite has no multi-table trigger).
-- ---------------------------------------------------------------------
CREATE TRIGGER IF NOT EXISTS trg_l3_snapshot_provenance BEFORE INSERT ON l3_claim
WHEN NEW.context_snapshot_id IS NOT NULL AND trim(NEW.context_snapshot_id) <> ''
BEGIN
    SELECT CASE WHEN NOT EXISTS (
        SELECT 1 FROM context_snapshot_log s WHERE s.snapshot_id = NEW.context_snapshot_id
    ) THEN RAISE(ABORT, 'l3_claim.context_snapshot_id not found in context_snapshot_log (forged provenance)') END;
END;

CREATE TRIGGER IF NOT EXISTS trg_l2_snapshot_provenance BEFORE INSERT ON l2_finding
WHEN NEW.context_snapshot_id IS NOT NULL AND trim(NEW.context_snapshot_id) <> ''
BEGIN
    SELECT CASE WHEN NOT EXISTS (
        SELECT 1 FROM context_snapshot_log s WHERE s.snapshot_id = NEW.context_snapshot_id
    ) THEN RAISE(ABORT, 'l2_finding.context_snapshot_id not found in context_snapshot_log (forged provenance)') END;
END;

CREATE TRIGGER IF NOT EXISTS trg_l1_snapshot_provenance BEFORE INSERT ON l1_viewpoint
WHEN NEW.context_snapshot_id IS NOT NULL AND trim(NEW.context_snapshot_id) <> ''
BEGIN
    SELECT CASE WHEN NOT EXISTS (
        SELECT 1 FROM context_snapshot_log s WHERE s.snapshot_id = NEW.context_snapshot_id
    ) THEN RAISE(ABORT, 'l1_viewpoint.context_snapshot_id not found in context_snapshot_log (forged provenance)') END;
END;

CREATE TRIGGER IF NOT EXISTS trg_l0_snapshot_provenance BEFORE INSERT ON l0_worldview
WHEN NEW.context_snapshot_id IS NOT NULL AND trim(NEW.context_snapshot_id) <> ''
BEGIN
    SELECT CASE WHEN NOT EXISTS (
        SELECT 1 FROM context_snapshot_log s WHERE s.snapshot_id = NEW.context_snapshot_id
    ) THEN RAISE(ABORT, 'l0_worldview.context_snapshot_id not found in context_snapshot_log (forged provenance)') END;
END;
