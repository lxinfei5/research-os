"""Boundary gates (see anti_corruption.md). Each gate returns (name, ok, problems[]). Pure checks —
no writes. run_all() aggregates; `ros lint` prints + exits nonzero on any failure."""
from __future__ import annotations

import json
import re
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
            problems.append(f"{slug}: missing knowledge.db")
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
_STORAGE_FORBIDDEN = re.compile(r"^\s*(from\s+\.\.|import\s+ros\.)(run|assembly|cli)\b", re.M)
_STORAGE_FORBIDDEN2 = re.compile(r"^\s*from\s+\.\.(run|assembly)\s+import", re.M)
_CLI_STORAGE = re.compile(r"^\s*(from\s+\.storage\s+import|from\s+ros\.storage\s+import|import\s+ros\.storage)", re.M)


def lint_import_acl() -> Gate:
    problems = []
    pkg = paths.PKG_DIR
    cli = (pkg / "cli.py").read_text(encoding="utf-8")
    if _CLI_STORAGE.search(cli):
        problems.append("ros/cli.py imports ros.storage.* directly (use ros.api)")
    for fp in (pkg / "storage").glob("*.py"):
        src = fp.read_text(encoding="utf-8")
        if _STORAGE_FORBIDDEN.search(src) or _STORAGE_FORBIDDEN2.search(src):
            problems.append(f"ros/storage/{fp.name} imports upward (run/assembly/cli)")
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
ALL_GATES = (lint_schema_drift, lint_collector_policy, lint_snapshot_provenance,
             lint_import_acl, lint_db_git_safety, lint_l0_version_integrity,
             lint_search_provider_registry, lint_webbridge_mcp_registry)


def run_all() -> list[Gate]:
    return [g() for g in ALL_GATES]
