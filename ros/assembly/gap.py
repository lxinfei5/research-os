"""Deterministic per-facet coverage / gap metrics — drives `ros gaps` and brief priming.

Python only MEASURES (counts, corroboration depth, recency). Whether a facet is "done" is a judgment
the agent makes from these numbers; we just surface them and label coverage with mechanical
thresholds. No reasoning here.
"""
from __future__ import annotations

import sqlite3

from ..storage import knowledge as K

# coverage thresholds (mechanical; tune later)
_THIN_L3 = 3            # fewer than this many L3 claims → thin
_CORROBORATED_XPLAT = 2  # cross_platform_count >= this → corroborated


def facet_gaps(conn: sqlite3.Connection) -> list[dict]:
    """One row per facet (declared in the facet table) PLUS any '_unfileted' L3 bucket.

    Each row: l3/l2 counts, corroboration depth, latest source recency (days), last_searched_at,
    and a mechanical coverage label (thin | developing | corroborated).
    """
    facets = K._rows(conn, "SELECT id, question, status, last_searched_at FROM facet ORDER BY created_at")
    # include facets that exist only as a value on L3/L2 rows (e.g. condense assigned 'f_main')
    used = {r["facet"] for r in K._rows(conn,
            "SELECT DISTINCT facet FROM l3_claim WHERE facet IS NOT NULL "
            "UNION SELECT DISTINCT facet FROM l2_finding WHERE facet IS NOT NULL")}
    known = {f["id"] for f in facets}
    for fid in sorted(used - known):
        facets.append({"id": fid, "question": "(auto, from condense)", "status": "open",
                       "last_searched_at": None})

    out = []
    for f in facets:
        out.append(_facet_metrics(conn, f))
    return out


def _facet_metrics(conn: sqlite3.Connection, f: dict) -> dict:
    fid = f["id"]
    l3 = _scalar(conn, "SELECT count(*) FROM l3_claim WHERE facet=? AND status='active'", (fid,))
    l2 = _scalar(conn, "SELECT count(*) FROM l2_finding WHERE facet=? AND status='active'", (fid,))
    corroborated = _scalar(conn,
        "SELECT count(*) FROM l2_finding WHERE facet=? AND status='active' AND cross_platform_count>=?",
        (fid, _CORROBORATED_XPLAT))
    max_xplat = _scalar(conn,
        "SELECT COALESCE(MAX(cross_platform_count),0) FROM l2_finding WHERE facet=? AND status='active'", (fid,))
    # recency: days since the newest source cited by this facet's L3
    recency = conn.execute(
        "SELECT MIN(julianday('now') - julianday(COALESCE(sr.captured_at, sr.created_at))) "
        "FROM l3_claim c JOIN source_ref sr ON sr.id = c.single_source_ref_id "
        "WHERE c.facet=? AND c.status='active'", (fid,)).fetchone()[0]
    recency_days = round(recency, 1) if recency is not None else None

    if l3 < _THIN_L3:
        label = "thin"
    elif corroborated == 0:
        label = "developing"
    else:
        label = "corroborated"
    return {
        "facet": fid, "question": f.get("question"), "status": f.get("status"),
        "l3": l3, "l2": l2, "corroborated_l2": corroborated, "max_cross_platform": max_xplat,
        "recency_days": recency_days, "last_searched_at": f.get("last_searched_at"),
        "coverage": label,
    }


def thin_facets(conn: sqlite3.Connection) -> list[dict]:
    """Facets that most need more search (thin or developing), worst first."""
    rank = {"thin": 0, "developing": 1, "corroborated": 2}
    gaps = [g for g in facet_gaps(conn) if g["coverage"] != "corroborated"]
    return sorted(gaps, key=lambda g: (rank[g["coverage"]], g["l3"]))


def _scalar(conn, sql, params=()):
    return int(conn.execute(sql, params).fetchone()[0])
