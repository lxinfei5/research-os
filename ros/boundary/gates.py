"""Boundary gates (see anti_corruption.md). Each gate returns (name, ok, problems[]). Pure checks —
no writes. run_all() aggregates; `ros lint` prints + exits nonzero on any failure."""
from __future__ import annotations

import ast
import json
import sqlite3
import sys
from pathlib import Path

from .. import paths, topics
from ..search import capabilities
from ..storage import intake, knowledge as K

Gate = tuple[str, bool, list[str]]


def _result(name: str, problems: list[str]) -> Gate:
    return (name, not problems, problems)


# ---------------------------------------------------------------------------
def lint_schema_drift() -> Gate:
    cur = K.current_schema_version()
    problems = []
    for t in topics.list_topics():
        slug = t["slug"]
        db = paths.knowledge_db(slug)
        if not db.is_file():
            # A missing live db is NOT drift: live .db files are gitignored and lazily
            # auto-materialized on first real access (ensure_knowledge_db). Every sibling gate
            # (collector_policy / snapshot_provenance / l0_version_integrity) skips the same way.
            # Reporting it made `ros lint` (the Stop hook) exit 1 every turn in every worktree,
            # crying wolf — which trains users to disable the hook, burying a REAL version mismatch.
            continue
        conn = K.get_conn(db)
        try:
            v = K.db_user_version(conn)
        finally:
            conn.close()
        if v != cur:
            problems.append(f"{slug}: schema v{v} != current v{cur} (run a migration)")
    return _result("schema_drift", problems)


# ---------------------------------------------------------------------------
def lint_collector_policy() -> Gate:
    problems = []
    for t in topics.list_topics():
        slug = t["slug"]
        sdb = paths.sources_db(slug)
        if not sdb.is_file():
            continue
        conn = intake.get_conn(sdb)
        try:
            # Skip a HOLLOW sources.db — a file that exists but was never schema-initialized (e.g.
            # promote_item opened a path that didn't exist, which sqlite3.connect creates as an empty
            # file). Without this guard the SELECT below raises OperationalError (no such table),
            # which is NOT in main()'s caught tuple → the Stop hook exits 2 with a traceback every
            # turn until the hollow file is hand-deleted. Mirrors _db_materialized for knowledge.db.
            tabs = {r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='source_session'").fetchall()}
            if "source_session" not in tabs:
                continue
            sessions = {r["id"]: dict(r) for r in conn.execute(
                "SELECT id, source, collector, capture_kind FROM source_session").fetchall()}
            items = conn.execute(
                "SELECT session_id, platform FROM source_item").fetchall()
        finally:
            conn.close()
        for sid, s in sessions.items():
            try:
                capabilities.validate_collector(s["source"], s["collector"],
                                                capture_kind=s["capture_kind"])
            except capabilities.CollectorPolicyError as e:
                problems.append(f"{slug}/{sid}: {e}")
        by_session = {sid: s for sid, s in sessions.items()}
        for it in items:
            s = by_session.get(it["session_id"])
            if not s or not it["platform"]:
                continue
            try:
                capabilities.validate_collector(it["platform"], s["collector"],
                                                capture_kind=s["capture_kind"])
            except capabilities.CollectorPolicyError as e:
                problems.append(f"{slug}/{it['session_id']} item platform={it['platform']}: {e}")
    return _result("collector_policy", problems)


# ---------------------------------------------------------------------------
_L_TABLES = ("l3_claim", "l2_finding", "l1_viewpoint", "l0_worldview")


def _db_materialized(conn) -> bool:
    """True only if the knowledge.db carries the L schema. A *hollow* db — a file that exists but was
    never schema-initialized (e.g. an aborted command that merely opened a sqlite connection, which
    creates the file) — is not a real world knowledge. schema_drift already reports it, so the
    provenance/version gates SKIP it instead of crashing on a `no such table` OperationalError."""
    names = {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name IN "
        "('l3_claim','l2_finding','l1_viewpoint','l0_worldview')").fetchall()}
    return len(names) == len(_L_TABLES)


def lint_snapshot_provenance() -> Gate:
    problems = []
    for t in topics.list_topics():
        slug = t["slug"]
        db = paths.knowledge_db(slug)
        if not db.is_file():
            continue
        conn = K.get_conn(db)
        try:
            if not _db_materialized(conn):
                continue
            for tbl in _L_TABLES:
                bad = conn.execute(
                    f"SELECT count(*) FROM {tbl} WHERE context_snapshot_id IS NOT NULL "
                    f"AND trim(context_snapshot_id) <> '' AND context_snapshot_id NOT IN "
                    f"(SELECT snapshot_id FROM context_snapshot_log)").fetchone()[0]
                if bad:
                    problems.append(f"{slug}/{tbl}: {bad} row(s) cite a missing context_snapshot")
        finally:
            conn.close()
    return _result("snapshot_provenance", problems)


# ---------------------------------------------------------------------------
def _resolved_imports(src: str, own_parts: list[str]):
    """Yield resolved absolute module names for every Import / ImportFrom in `src`.

    Relative imports resolve against `own_parts` (the file's dotted package, e.g. ['ros','storage']
    for ros/storage/foo.py). AST-based so it catches every import form the old line-regexes missed
    (``from ros.run import x``, ``from ros import run``, ``from . import storage``, depth-variant
    relatives). Used by lint_import_acl — the sole automated guard for the cli→api→storage layering
    that backs the iron rule ('Python never reasons / calls an LLM').
    """
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name:
                    yield alias.name
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0:
                base = node.module or ""
            else:
                # relative: drop (level-1) trailing parts from own_parts, then append the module
                keep = len(own_parts) - (node.level - 1)
                if keep < 0:
                    continue  # escapes the package root — can't resolve reliably, skip
                parts = list(own_parts[:keep])
                if node.module:
                    parts.append(node.module)
                base = ".".join(parts)
            if not base:
                continue
            for alias in node.names:
                yield f"{base}.{alias.name}"


def _hits(imports, target: str) -> bool:
    return any(imp == target or imp.startswith(target + ".") for imp in imports)


def lint_import_acl() -> Gate:
    problems = []
    pkg = paths.PKG_DIR
    root_name = pkg.name  # 'ros'

    # cli.py must not import ros.storage directly — the layering is cli → ros.api → storage.
    storage_target = f"{root_name}.storage"
    cli_imports = list(_resolved_imports((pkg / "cli.py").read_text(encoding="utf-8"), [root_name]))
    if _hits(cli_imports, storage_target):
        problems.append("ros/cli.py imports ros.storage.* directly (use ros.api)")

    # storage/* must not import upward into run / assembly / cli — those shell out to the agent /
    # reason, so an upward import would let Python trigger LLM reasoning, breaking the iron rule.
    forbidden = {f"{root_name}.{n}" for n in ("run", "assembly", "cli")}
    for fp in sorted((pkg / "storage").glob("*.py")):
        src = fp.read_text(encoding="utf-8")
        hit = None
        for imp in _resolved_imports(src, [root_name, "storage"]):
            for tgt in forbidden:
                if imp == tgt or imp.startswith(tgt + "."):
                    hit = imp
                    break
            if hit:
                break
        if hit:
            problems.append(f"ros/storage/{fp.name} imports upward ({hit})")
    return _result("import_acl", problems)


# ---------------------------------------------------------------------------
def lint_db_git_safety() -> Gate:
    problems = []
    gi = paths.root() / ".gitignore"
    if not gi.is_file():
        return _result("db_git_safety", ["no .gitignore at repo root"])
    text = gi.read_text(encoding="utf-8")
    for pat in ("topics/*/knowledge.db", "topics/*/sources.db"):
        if pat not in text:
            problems.append(f".gitignore missing live-DB pattern: {pat}")
    return _result("db_git_safety", problems)


# ---------------------------------------------------------------------------
def lint_l0_version_integrity() -> Gate:
    """The L0 version chain invariant: exactly ONE active world model per topic, and any non-empty
    supersedes_id on an active row must point at a row that actually exists (a real predecessor,
    not a self-reference or a dangling pointer)."""
    problems = []
    for t in topics.list_topics():
        slug = t["slug"]
        db = paths.knowledge_db(slug)
        if not db.is_file():
            continue
        conn = K.get_conn(db)
        try:
            if not _db_materialized(conn):
                continue
            active = conn.execute(
                "SELECT id, supersedes_id FROM l0_worldview WHERE status='active'").fetchall()
            if len(active) > 1:
                problems.append(f"{slug}: {len(active)} active L0 rows (expected exactly 1)")
            for r in active:
                sup = r["supersedes_id"]
                if not sup:
                    continue
                if sup == r["id"]:
                    problems.append(f"{slug}: active L0 {r['id']} supersedes itself")
                elif conn.execute(
                        "SELECT 1 FROM l0_worldview WHERE id=?", (sup,)).fetchone() is None:
                    problems.append(f"{slug}: active L0 {r['id']} supersedes missing id {sup}")
        finally:
            conn.close()
    return _result("l0_version_integrity", problems)


# ---------------------------------------------------------------------------
def lint_search_provider_registry() -> Gate:
    """The quota-free Tier-3 web fallback (multi-search-engine) is referenced by the `web` collector
    policy AND by the researchos-search skill as prose. Per the boundary principle 'a constraint that
    lives only in bypassable prose is no constraint', verify the referenced skill actually exists and
    its engine registry parses — so the port can't silently rot into a dangling reference. Also assert
    the fetch-Tier-3 browser reader (kimi-webbridge) stays whitelisted for web, else the JS/anti-bot
    fallback would be rejected by the very gate meant to allow it."""
    problems: list[str] = []
    web_required = capabilities.required_collectors("web")
    if "multi-search-engine" not in web_required:
        problems.append("source_capabilities.yaml: 'web' no longer allows the multi-search-engine "
                        "Tier-3 collector (quota-free fallback would be gate-rejected)")
    if "kimi-webbridge" not in web_required:
        problems.append("source_capabilities.yaml: 'web' no longer allows kimi-webbridge (the "
                        "fetch-Tier-3 browser reader for JS/anti-bot pages would be gate-rejected)")

    # The skill is SOURCE code, co-located with the ros/ package — resolve from the code tree
    # (PKG_DIR.parent = repo root), NOT paths.root() which tests redirect via ROS_ROOT.
    skill_dir = paths.PKG_DIR.parent / ".agents" / "skills" / "multi-search-engine"
    cfg = skill_dir / "config.json"
    if not (skill_dir / "SKILL.md").is_file():
        problems.append("multi-search-engine collector is policy-allowed but its skill "
                        "(.agents/skills/multi-search-engine/SKILL.md) is missing")
    if not cfg.is_file():
        problems.append("multi-search-engine skill has no config.json engine registry "
                        "(engines_attempted audit source)")
    else:
        try:
            engines = (json.loads(cfg.read_text(encoding="utf-8")) or {}).get("engines")
        except (json.JSONDecodeError, OSError) as e:
            engines = None
            problems.append(f"multi-search-engine config.json does not parse: {e}")
        if isinstance(engines, list) and engines:
            bad = [i for i, e in enumerate(engines)
                   if not (isinstance(e, dict) and e.get("name") and "{keyword}" in str(e.get("url", "")))]
            if bad:
                problems.append(f"multi-search-engine config.json: {len(bad)} engine(s) miss "
                                f"name or a '{{keyword}}' slot in url (indices {bad[:5]})")
        elif engines is not None:
            problems.append("multi-search-engine config.json 'engines' must be a non-empty list")
    return _result("search_provider_registry", problems)


# ---------------------------------------------------------------------------
def lint_webbridge_mcp_registry() -> Gate:
    """webbridge-mcp is the MCP proxy fronting the Kimi WebBridge real-Chrome daemon (:10086) so
    workflow SUB-AGENTS can reach X / 抖音 / login-gated web — a skill (kimi-webbridge) is advisory
    prose that does NOT propagate to spawned sub-agents. This gate keeps that port honest and, most
    importantly, asserts the crown-jewel XHS constraint survives it:
      1. webbridge-mcp is registered in .mcp.json  (else sub-agents never get mcp__webbridge-mcp__*),
      2. its Go source tree exists                 (the registration isn't a dangling reference),
      3. xiaohongshu STILL forbids webbridge-mcp   (a general browser bridge — MCP or skill — must
         never touch XHS search/detail; only xiaohongshu-mcp),
      4. x AND douyin allow webbridge-mcp          (the sub-agent-reachable transport the port added;
         without it X/抖音 would stay main-loop-only and the capability matrix is not complete).
    Static/pure — reads the committed .mcp.json + source tree from the CODE tree (PKG_DIR.parent),
    not paths.root() (tests redirect that via ROS_ROOT)."""
    problems: list[str] = []
    repo = paths.PKG_DIR.parent

    # 1. registered in .mcp.json → :18061
    mcp_cfg = repo / ".mcp.json"
    if not mcp_cfg.is_file():
        problems.append(".mcp.json missing at repo root (webbridge-mcp cannot be registered)")
    else:
        try:
            servers = (json.loads(mcp_cfg.read_text(encoding="utf-8")) or {}).get("mcpServers", {})
        except (json.JSONDecodeError, OSError) as e:
            servers = {}
            problems.append(f".mcp.json does not parse: {e}")
        wb = servers.get("webbridge-mcp")
        if not wb:
            problems.append(".mcp.json has no 'webbridge-mcp' server — workflow sub-agents would lose "
                            "mcp__webbridge-mcp__*, leaving X/抖音 unreachable from sub-agents")
        elif "18061" not in str(wb.get("url", "")):
            problems.append(f"webbridge-mcp url should target the webbridge proxy port :18061; "
                            f"got {wb.get('url')!r}")

    # 2. the Go source tree the registration points at actually exists (not dangling prose)
    src = repo / "tools" / "social_mcp" / "webbridge_mcp"
    for f in ("main.go", "server.go", "proxy.go", "tools.go", "go.mod"):
        if not (src / f).is_file():
            problems.append(f"webbridge-mcp is registered but its source is missing: "
                            f"tools/social_mcp/webbridge_mcp/{f}")

    # 3. crown jewel survives: XHS forbids EVERY general browser bridge (skill AND MCP)
    xhs_forbidden = set(capabilities.forbidden_collectors("xiaohongshu"))
    for must in ("kimi-webbridge", "browser", "webbridge-mcp"):
        if must not in xhs_forbidden:
            problems.append(f"xiaohongshu no longer forbids '{must}': a general browser bridge could "
                            f"scrape XHS, bypassing xiaohongshu-mcp (the crown-jewel constraint)")

    # 4. the matrix is actually completed: x + douyin allow the sub-agent-reachable transport
    for name in ("x", "douyin"):
        if "webbridge-mcp" not in capabilities.required_collectors(name):
            problems.append(f"source '{name}' does not allow 'webbridge-mcp' — X/抖音 would stay "
                            f"main-loop-only (the sub-agent reachability the MCP was built for is lost)")

    return _result("webbridge_mcp_registry", problems)


# ---------------------------------------------------------------------------
def lint_source_ref_host_platform() -> Gate:
    """Crown-jewel defense-in-depth at the RETENTION layer (knowledge.db.source_ref).

    The capture gate (capabilities.enforce_capture) inspects only DECLARED source/platform/collector
    — a sub-agent that scrapes XHS via webbridge-mcp then declares source='web' passes it. This gate
    cross-checks the one thing the agent cannot relabel: the URL HOST. A retained source_ref whose
    URL host is a Xiaohongshu origin (capabilities.host_is_xhs) MUST declare platform=xiaohongshu.
    A xiaohongshu.com URL with platform='web' is the fingerprint of a relabeled XHS scrape, caught
    here even though it slipped the declared-value capture gate. (W-01; transport denylist in
    webbridge-mcp is the primary control; this is the retention backstop.)
    """
    problems: list[str] = []
    for t in topics.list_topics():
        slug = t["slug"]
        db = paths.knowledge_db(slug)
        if not db.is_file():
            continue
        conn = K.get_conn(db)
        try:
            if not _db_materialized(conn):
                continue
            rows = conn.execute(
                "SELECT id, platform, url FROM source_ref WHERE url IS NOT NULL AND trim(url) <> ''"
            ).fetchall()
            for r in rows:
                if capabilities.host_is_xhs(r["url"]) and \
                        capabilities.canonical(r["platform"]) != "xiaohongshu":
                    problems.append(
                        f"{slug}/{r['id']}: url host is Xiaohongshu but platform='{r['platform']}' "
                        f"(relabeled XHS scrape that passed the declared-value capture gate?)")
        finally:
            conn.close()
    return _result("source_ref_host_platform", problems)


# ---------------------------------------------------------------------------
def lint_web_search_evidence() -> Gate:
    """Public-WEB search/detail/fetch captures must carry raw_tool_status.fallback_chain (W-08/#29).

    Enforced at the AUDIT layer (not capture-time — a hard capture gate broke legitimate minimal
    fetches and the collector-policy tests): a web search session whose raw_tool_status has no
    fallback_chain list leaves the rate-limit signal invisible — exactly what lets a 限流 precursor
    be misread as 'no results' and the facet get marked covered. Structural shape check only (the
    iron rule permits validating audit-trail shape, not meaning). Scoped to web; social playbooks
    use degraded_reason / restricted_reason, not fallback_chain."""
    problems: list[str] = []
    for t in topics.list_topics():
        slug = t["slug"]
        sdb = paths.sources_db(slug)
        if not sdb.is_file():
            continue
        conn = intake.get_conn(sdb)
        try:
            tabs = {r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='source_session'").fetchall()}
            if "source_session" not in tabs:
                continue
            rows = conn.execute(
                "SELECT id, capture_kind, raw_tool_status FROM source_session "
                "WHERE source IN ('web','web_search') "
                "AND capture_kind IN ('search','detail','fetch')").fetchall()
            legacy_null: list[str] = []
            for r in rows:
                raw = r["raw_tool_status"]
                if not raw:
                    # No status recorded AT ALL - almost always a pre-gate legacy capture: the
                    # raw_tool_status.fallback_chain recording convention postdates commit 6449199
                    # (2026-07-06), so older captures have NULL and can never be backfilled (the data
                    # was never captured) and the research they fed is already condensed. Collected
                    # and surfaced as ONE NON-blocking stderr advisory per topic (the snapshot_freshness
                    # pattern): failing every turn (the Stop hook) on unfixable legacy just trains
                    # operators to disable lint - the schema_drift / snapshot_freshness crying-wolf
                    # lesson. A POST-gate capture that regresses to NULL rts still appears here as a
                    # visible advisory; a non-NULL-but-malformed rts stays blocking below.
                    legacy_null.append(r["id"])
                    continue
                try:
                    rts = json.loads(raw)
                except json.JSONDecodeError:
                    rts = None
                # Status WAS recorded but lacks fallback_chain (or is malformed) - a real, recent
                # capture-time gap the gate is meant to block (unlike the NULL legacy case above).
                if not (isinstance(rts, dict) and isinstance(rts.get("fallback_chain"), list)):
                    problems.append(
                        f"{slug}/{r['id']}: web {r['capture_kind']} capture has no "
                        f"raw_tool_status.fallback_chain (rate-limit signal invisible)")
            if legacy_null:
                print(f"[lint] advisory: {slug}: {len(legacy_null)} web capture(s) recorded no "
                      f"raw_tool_status (legacy pre-gate, rate-limit signal invisible; non-blocking)",
                      file=sys.stderr)
        finally:
            conn.close()
    return _result("web_search_evidence", problems)


# ---------------------------------------------------------------------------
def lint_snapshot_freshness() -> Gate:
    """Advisory (NON-blocking): warn when a live knowledge.db holds research newer than its last
    committed snapshot (W-12/#12).

    The live .db is gitignored; the snapshot is the durable artifact. ensure_knowledge_db
    auto-restores the last snapshot when the live db is MISSING — so research written to the live
    db but never snapshotted is silently lost the moment the worktree is deleted (with no error and
    no lint signal). This gate surfaces 'you have unsnapshotted research' as a stderr advisory so it
    isn't silent. Deliberately non-blocking (ok=True): a condense/grow run legitimately leaves the
    live db fresher than the snapshot until the operator commits; failing every turn (the Stop hook)
    would cry wolf and train the user to disable lint — the schema_drift false-positive lesson."""
    for t in topics.list_topics():
        slug = t["slug"]
        db = paths.knowledge_db(slug)
        if not db.is_file():
            continue
        snap = paths.latest_snapshot_path(slug)
        if snap is None or not snap.is_file():
            # live db exists but NO snapshot at all → most acute silent-loss risk
            print(f"[lint] advisory: '{slug}' has a live knowledge.db but NO committed snapshot — "
                  f"run `ros snapshot {slug}` before deleting the worktree or this research is lost",
                  file=sys.stderr)
            continue
        if db.stat().st_mtime > snap.stat().st_mtime + 60:  # 60s grace for a snapshot just started
            print(f"[lint] advisory: '{slug}' live knowledge.db is newer than its latest snapshot "
                  f"({snap.name}) — run `ros snapshot {slug}` to durably commit the new research",
                  file=sys.stderr)
    return _result("snapshot_freshness", [])  # advisory only — never blocks


# ---------------------------------------------------------------------------
def lint_credibility_orphans() -> Gate:
    """Flag credibility_assessment rows whose subject L-row no longer exists (W-21/#36).

    credibility rows are written at L-upsert time (_require_credibility binds them); if an L-row is
    ever removed (a future DELETE path or a hand-edited snapshot committed to git), its credibility
    row orphans with no lint signal. Pure existence check (no semantic judgement). subject_type is
    CHECK-constrained to the 4 L-table names, so it is safe to use as the table name here."""
    problems: list[str] = []
    for t in topics.list_topics():
        slug = t["slug"]
        db = paths.knowledge_db(slug)
        if not db.is_file():
            continue
        conn = K.get_conn(db)
        try:
            if not _db_materialized(conn):
                continue
            for stype in ("l3_claim", "l2_finding", "l1_viewpoint", "l0_worldview"):
                rows = conn.execute(
                    f"SELECT c.id, c.subject_id FROM credibility_assessment c "
                    f"WHERE c.subject_type=? AND NOT EXISTS "
                    f"(SELECT 1 FROM {stype} x WHERE x.id = c.subject_id)", (stype,)).fetchall()
                for r in rows:
                    problems.append(f"{slug}: credibility {r['id']} references missing {stype} {r['subject_id']}")
        finally:
            conn.close()
    return _result("credibility_orphans", problems)


# ---------------------------------------------------------------------------
ALL_GATES = (lint_schema_drift, lint_collector_policy, lint_snapshot_provenance,
             lint_import_acl, lint_db_git_safety, lint_l0_version_integrity,
             lint_search_provider_registry, lint_webbridge_mcp_registry,
             lint_source_ref_host_platform, lint_web_search_evidence, lint_snapshot_freshness,
             lint_credibility_orphans)


def run_all() -> list[Gate]:
    """Run every gate, fail-soft on transient DB errors.

    A transient SQLITE_BUSY (a writer in another shell holds the lock past busy_timeout) or an
    unexpected OperationalError must NOT make `ros lint` (the Stop hook) exit 2 with a traceback
    every turn. The per-gate _db_materialized guards skip hollow DBs; this catches anything that
    still slips through, warns on stderr, and SKIPS the gate that turn (the Stop hook re-runs next
    turn, so a transient lock is observed again once free — failing on it would just cry wolf)."""
    gates: list[Gate] = []
    for g in ALL_GATES:
        try:
            gates.append(g())
        except sqlite3.OperationalError as e:
            print(f"[lint] {g.__name__}: transient DB error, skipped this turn — {e}",
                  file=sys.stderr)
    return gates
