#!/usr/bin/env python3
"""ONE-SHOT migration exporter (use-and-delete): live knowledge.db -> knowledge.md.

ResearchOS 弱门控化 + 去 db 化 — Stage 1 exporter. Reads each topic's live
`knowledge.db` (authoritative) and emits the file-world layout:
  topics/<slug>/knowledge.md       L0/L1/L2/L3 as heading labels + open questions + source index + facet coverage
  topics/<slug>/sources/<hash>.md  one md per source_ref (provenance frontmatter)
  topics/<slug>/captures/<session>.json  raw intake payloads (replayable)
  topics/_shared/methods/*.md      M0/M1 method rules

credibility_assessment is FOLDED INLINE as a T/S/A/B/C prefix tag (+[echo] note);
it is not a separate table anymore. controlled_vocab / knowledge_change_log /
context_snapshot_log are dropped (platform/kind become inline tags; git = audit).

Deterministic, read-only against the db. Run: python3 export_one.py <topics_root> <out_root> [slug ...]
"""
from __future__ import annotations
import json
import os
import re
import sqlite3
import sys
from pathlib import Path

T_MAP = {"high": "T1", "medium": "T2", "low": "T3"}  # credibility level -> source-ladder tag
GRADE_MAP = {"high": "S", "medium": "A", "low": "B"}  # conclusion-confidence grade (L1/L0)


def conn(db: Path) -> sqlite3.Connection:
    c = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    c.row_factory = sqlite3.Row
    return c


def j(s, default=None):
    if s is None or s == "":
        return default
    try:
        return json.loads(s)
    except Exception:
        return default


def slugify(text: str, maxlen: int = 24) -> str:
    t = re.sub(r"\s+", "_", (text or "").strip())
    t = re.sub(r"[^\w一-鿿_-]", "", t)
    return t[:maxlen] or "misc"


def creds_by_subject(c: sqlite3.Connection) -> dict:
    out = {}
    for r in c.execute("SELECT * FROM credibility_assessment"):
        out[(r["subject_type"], r["subject_id"])] = dict(r)
    return out


def tag_for(cred: dict | None) -> str:
    if not cred:
        return "T2"
    t = T_MAP.get(cred.get("level") or "", "T2")
    if cred.get("echo_chamber_flag"):
        t += " · [echo]"
    return t


def src_provenance(c: sqlite3.Connection, ids: list) -> str:
    """Render a compact provenance string from source_ref ids (deduped by url)."""
    bits, seen = [], set()
    for sid in ids:
        r = c.execute("SELECT platform, url, author FROM source_ref WHERE id=?", (sid,)).fetchone()
        if r and r["url"] not in seen:
            seen.add(r["url"])
            a = f" {r['author']}" if r["author"] else ""
            bits.append(f"{r['platform']}{a} <{r['url']}>")
    return " + ".join(bits) if bits else "(源见信源索引)"


def facet_of(row) -> str:
    return (row["facet"] or "").strip() or "未分组"


def export_topic(slug: str, db_path: Path, out: Path, shared_methods: dict) -> dict:
    c = conn(db_path)
    creds = creds_by_subject(c)
    counts = {"L0": 0, "L1": 0, "L2": 0, "L3": 0, "src": 0, "oq": 0}

    # topic.yaml for title/stage/aliases
    title = slug
    stage = "scoping"
    ty = out / "topic.yaml"
    if ty.exists():
        for line in ty.read_text(encoding="utf-8").splitlines():
            if line.startswith("title:"):
                title = line.split(":", 1)[1].strip()
            if line.startswith("stage:"):
                stage = line.split(":", 1)[1].strip()

    # ---- gather rows
    l0s = list(c.execute("SELECT * FROM l0_worldview ORDER BY (status='active') DESC, created_at DESC"))
    l1s = list(c.execute("SELECT * FROM l1_viewpoint ORDER BY facet, rank, created_at"))
    l2s = list(c.execute("SELECT * FROM l2_finding ORDER BY facet, created_at"))
    l3s = list(c.execute("SELECT * FROM l3_claim ORDER BY facet, created_at"))
    srcs = list(c.execute("SELECT * FROM source_ref ORDER BY created_at"))
    oqs = list(c.execute("SELECT * FROM open_question ORDER BY created_at"))
    facets = list(c.execute("SELECT * FROM facet ORDER BY created_at"))
    try:
        search_last = {r["facet"]: r["searched_at"] for r in c.execute(
            "SELECT facet, MAX(searched_at) searched_at FROM search_log GROUP BY facet")}
    except sqlite3.OperationalError:
        search_last = {}

    counts["L0"], counts["L1"], counts["L2"], counts["L3"] = len(l0s), len(l1s), len(l2s), len(l3s)
    counts["src"], counts["oq"] = len(srcs), len(oqs)

    # ---- per-source md (dedup by URL: the same article captured twice with
    # different content hashes should yield ONE canonical sources/<hash>.md and
    # ONE index row; every source_ref id still resolves to that canonical file)
    (out / "sources").mkdir(parents=True, exist_ok=True)
    src_hash_by_id = {}
    url_canonical = {}          # url -> canonical content_hash
    canonical_rows = {}         # canonical content_hash -> source_ref row (first seen)
    for s in srcs:
        url = (s["url"] or "").strip()
        if url and url in url_canonical:
            src_hash_by_id[s["id"]] = url_canonical[url]
            continue
        h = s["content_hash"] or s["id"].replace("src-", "")
        if url:
            url_canonical[url] = h
        canonical_rows[h] = s
        src_hash_by_id[s["id"]] = h
    for h, s in canonical_rows.items():
        fm = [
            "---",
            f"content_hash: {h}",
            f"platform: {s['platform']}",
            f"source_kind: {s['source_kind']}",
            f"url: {s['url']}",
        ]
        if s["author"]:
            fm.append(f"author: {s['author']}")
        if s["title"]:
            fm.append(f"title: {json.dumps(s['title'], ensure_ascii=False)}")
        if s["captured_at"]:
            fm.append(f"captured_at: {s['captured_at']}")
        if s["valid_to"]:
            fm.append(f"valid_to: {s['valid_to']}")
        fm.append("---\n")
        body = [f"# {s['title'] or s['url']}", ""]
        body.append(f"> 原文：`../../../library/sources/{h}.json`（内容寻址共享库）。本文件只承载 provenance。")
        if s["media_transcript_path"]:
            body.append(f"> 转写：`{s['media_transcript_path']}`")
        (out / "sources" / f"{h}.md").write_text("\n".join(fm) + "\n" + "\n".join(body) + "\n", encoding="utf-8")
    counts["src_files"] = len(canonical_rows)

    # ---- knowledge.md
    L = []
    L.append("---")
    L.append(f"slug: {slug}")
    L.append(f"title: {json.dumps(title, ensure_ascii=False)}")
    L.append("status: open")
    L.append(f"stage: {stage}")
    L.append(f"coverage: L0={counts['L0']} L1={counts['L1']} L2={counts['L2']} L3={counts['L3']} src={counts['src']}")
    L.append("last_grown_at: ")
    L.append("---\n")
    L.append(f"# {title} — 世界知识\n")
    L.append("> 本档只存带 provenance+valid_until 的客观知识。L0–L3 是 heading 标签(按半衰期),非 schema。"
             "发现=grep+读本档。方向性状态现算不落。可信度为 inline 前缀标签(T0–T4/S/A/B/C),不另立表。\n")

    # L0
    L.append("## L0 世界观(恒真,≈从不改;首段为 active,历史版本下沉,git 即版本链)\n")
    if not l0s:
        L.append("_(空 — 尚未综合出世界观)_\n")
    for i, r in enumerate(l0s):
        active = (r["status"] == "active")
        date = (r["created_at"] or "")[:10]
        head = f"### {'active' if active else 'archived'} · {date}"
        if not active and i > 0:
            head += " · [superseded]"
        L.append(head)
        cred = creds.get(("l0_worldview", r["id"]))
        grade = GRADE_MAP.get((cred or {}).get("level") or "", "A")
        prop = (r["proposition"] or "").strip()
        L.append(f"- **({r['summary_kind']} · confidence:{r['confidence'] or grade})** {prop}")
        oq = j(r["open_questions"], [])
        if oq:
            L.append(f"  *(open_questions: {'；'.join(str(x) for x in oq)})*")
        L.append("")

    # L1 grouped by facet
    L.append("## L1 视角(慢变,主题/子问题综合,人复审)\n")
    if not l1s:
        L.append("_(空)_\n")
    by_facet = {}
    for r in l1s:
        by_facet.setdefault(facet_of(r), []).append(r)
    for fac, rows in by_facet.items():
        L.append(f"### {fac}")
        for r in rows:
            cred = creds.get(("l1_viewpoint", r["id"]))
            grade = GRADE_MAP.get((cred or {}).get("level") or "", "A")
            stance = r["stance"] or "established"
            narr = (r["narrative"] or "").strip()
            L.append(f"- **({r['synthesis_kind']} · {stance} · confidence:{r['confidence'] or grade})** {narr}")
            oq = j(r["open_questions"], [])
            if oq:
                L.append(f"  *(open_questions: {'；'.join(str(x) for x in oq)})*")
        L.append("")

    # L2 grouped by facet
    L.append("## L2 印证事实(多源互证,带 corroboration + provenance + valid_until)\n")
    if not l2s:
        L.append("_(空)_\n")
    by_facet = {}
    for r in l2s:
        by_facet.setdefault(facet_of(r), []).append(r)
    for fac, rows in by_facet.items():
        L.append(f"### {fac}")
        for r in rows:
            cred = creds.get(("l2_finding", r["id"]))
            tag = tag_for(cred)
            ids = j(r["source_ref_ids"], [])
            prov = src_provenance(c, ids)
            cc = r["corroboration_count"] or 1
            xp = r["cross_platform_count"] or 1
            val = ""
            if r["value_text"]:
                val = f" = {r['value_text']}"
            elif r["value_num"] is not None:
                val = f" = {r['value_num']}{r['unit'] or ''}"
            vu = f"; valid_until: {r['valid_to']}" if r["valid_to"] else ""
            stale = "" if r["status"] == "active" else f"[{r['status']}] "
            stmt = (r["statement"] or "").strip()
            L.append(f"- {stale}**[{tag} · 多源×{cc} · 跨平台×{xp}]** {stmt}{val}")
            L.append(f"  *(provenance: {prov}{vu})*")
            if r["conflict_note"]:
                L.append(f"  *(⚠冲突: {r['conflict_note']})*")
        L.append("")

    # L3 grouped by facet
    L.append("## L3 单源主张(一条 source 一条,带可信度标签)\n")
    if not l3s:
        L.append("_(空)_\n")
    by_facet = {}
    for r in l3s:
        by_facet.setdefault(facet_of(r), []).append(r)
    for fac, rows in by_facet.items():
        L.append(f"### {fac}")
        for r in rows:
            cred = creds.get(("l3_claim", r["id"]))
            tag = tag_for(cred)
            h = src_hash_by_id.get(r["single_source_ref_id"], "")
            srclink = f"sources/{h}.md" if h else "(源见信源索引)"
            stale = "" if r["status"] == "active" else f"[{r['status']}] "
            prop = (r["proposition"] or "").strip()
            L.append(f"- {stale}**[{tag} · {r['claim_kind'] or 'claim'} · 单源]** {prop}")
            L.append(f"  *(source: `{srclink}`)*")
        L.append("")

    # open questions
    L.append("## 未决问题\n")
    if not oqs:
        L.append("_(无)_\n")
    for r in oqs:
        done = r["status"] in ("answered", "stale")
        box = "[x]" if r["status"] == "answered" else "[ ]"
        line = f"- {box} {(r['question'] or '').strip()}"
        if r["status"] == "answered" and r["answered_by_l_id"]:
            line += f" → 答于 {r['answered_by_l_id']}"
        elif done:
            line += f" · ({r['status']})"
        L.append(line)
    L.append("")

    # source index (one row per canonical, deduped source)
    L.append("## 信源索引\n")
    L.append("| content_hash | platform | kind | url | captured | valid_to |")
    L.append("|---|---|---|---|---|---|")
    for h, s in canonical_rows.items():
        L.append(f"| `{h}` | {s['platform']} | {s['source_kind']} | {s['url']} "
                 f"| {(s['captured_at'] or '')[:10]} | {s['valid_to'] or '—'} |")
    L.append("")

    # facet coverage (derived snapshot)
    # per-facet L counts: L rows store the facet *id* (f_*), so key counts by id.
    # Map id -> short question label for display. Some L rows may carry the question
    # string or a non-id bucket (e.g. "_unfileted") — count those under their raw value.
    n3_by_fid, n2_by_fid = {}, {}
    for r in l3s:
        f = (r["facet"] or "").strip()
        n3_by_fid[f] = n3_by_fid.get(f, 0) + 1
    for r in l2s:
        f = (r["facet"] or "").strip()
        n2_by_fid[f] = n2_by_fid.get(f, 0) + 1
    L.append("## facet 覆盖(派生快照,以正文为准)\n")
    if not facets and not n3_by_fid and not n2_by_fid:
        L.append("_(无 facet 记录)_\n")
    for f in facets:
        fid = f["id"]
        fq = f["question"] or fid
        n3 = n3_by_fid.get(fid, 0)
        n2 = n2_by_fid.get(fid, 0)
        last = (search_last.get(fid) or "")[:10]
        thin = "thin" if n2 < 3 else ("corroborated" if n2 >= 10 else "developing")
        L.append(f"- {fq} (`{fid}`): L3={n3} L2={n2} · {thin}" + (f" · last_search {last}" if last else ""))
    # surface any facet buckets present in L rows but not in the facet table
    known = {f["id"] for f in facets}
    extra = sorted((set(n3_by_fid) | set(n2_by_fid)) - known - {""})
    for f in extra:
        L.append(f"- {f}: L3={n3_by_fid.get(f,0)} L2={n2_by_fid.get(f,0)} · (未登记 facet)")
    L.append("")

    (out / "knowledge.md").write_text("\n".join(L) + "\n", encoding="utf-8")

    # ---- captures/ from sources.db
    caps = 0
    sdb = db_path.parent / "sources.db"
    if sdb.exists():
        sc = conn(sdb)
        (out / "captures").mkdir(exist_ok=True)
        for sess in sc.execute("SELECT * FROM source_session"):
            items = [dict(x) for x in sc.execute("SELECT * FROM source_item WHERE session_id=?", (sess["id"],))]
            payload = {"session": dict(sess), "items": items}
            (out / "captures" / f"{sess['id']}.json").write_text(
                json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            caps += 1

    # ---- method rules -> shared
    for r in c.execute("SELECT * FROM method_rule"):
        key = f"{slug}:{r['id']}"
        shared_methods[key] = dict(r)

    c.close()
    counts["captures"] = caps
    return counts


def main() -> int:
    topics_root = Path(sys.argv[1])
    out_root = Path(sys.argv[2])
    only = set(sys.argv[3:])
    shared_methods: dict = {}
    summary = []
    for d in sorted(topics_root.iterdir()):
        if not d.is_dir() or d.name.startswith("_"):
            continue
        slug = d.name
        if only and slug not in only:
            continue
        db = d / "knowledge.db"
        out = out_root / "topics" / slug
        out.mkdir(parents=True, exist_ok=True)
        # carry over topic.yaml
        ty = d / "topic.yaml"
        if ty.exists():
            (out / "topic.yaml").write_text(ty.read_text(encoding="utf-8"), encoding="utf-8")
        if not db.exists():
            # empty topic: scaffold
            (out / "knowledge.md").write_text(
                f"---\nslug: {slug}\nstatus: open\n---\n\n# {slug} — 世界知识\n\n"
                "> 空主题,尚无知识。\n\n## L0 世界观\n_(空)_\n\n## L1 视角\n_(空)_\n\n## L2 印证事实\n_(空)_\n\n"
                "## L3 单源主张\n_(空)_\n\n## 未决问题\n_(无)_\n\n## 信源索引\n\n## facet 覆盖\n_(无)_\n",
                encoding="utf-8")
            summary.append((slug, "scaffold(empty)"))
            continue
        counts = export_topic(slug, db, out, shared_methods)
        summary.append((slug, counts))

    # shared methods
    if shared_methods:
        md = out_root / "topics" / "_shared" / "methods"
        md.mkdir(parents=True, exist_ok=True)
        for key, r in shared_methods.items():
            body = [f"# ({r['level']}) {r['proposition']}", ""]
            if r["valid_if"]:
                body.append(f"- valid_if: `{r['valid_if']}`")
            if r["wrong_if"]:
                body.append(f"- wrong_if: `{r['wrong_if']}`")
            body.append(f"- origin: {key.split(':')[0]} · status: {r['status']}")
            (md / f"{r['id']}.md").write_text("\n".join(body) + "\n", encoding="utf-8")

    print("=== export summary ===")
    for slug, counts in summary:
        print(f"{slug}: {counts}")
    print(f"shared_methods: {len(shared_methods)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
