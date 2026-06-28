"""Research-stage resolver — maps deterministic coverage metrics to a topic stage label.

scoping → survey → deepening → corroborating → saturating → mature. Used to gate brief content and
to stamp topic.yaml. Mechanical; the agent doesn't decide the stage, the numbers do.
"""
from __future__ import annotations

import sqlite3

from . import gap

STAGES = ["scoping", "survey", "deepening", "corroborating", "saturating", "mature"]


def resolve_stage(conn: sqlite3.Connection) -> str:
    def n(sql, params=()):
        return int(conn.execute(sql, params).fetchone()[0])

    l3 = n("SELECT count(*) FROM l3_claim WHERE status='active'")
    l2 = n("SELECT count(*) FROM l2_finding WHERE status='active'")
    l0 = n("SELECT count(*) FROM l0_worldview WHERE status='active'")
    corroborated = n("SELECT count(*) FROM l2_finding WHERE status='active' AND cross_platform_count>=2")
    thin = [g for g in gap.facet_gaps(conn) if g["coverage"] == "thin"]

    # pick the highest stage whose precondition holds
    if l0 >= 1 and corroborated >= 3 and not thin:
        return "mature"
    if l0 >= 1 and corroborated >= 1:
        return "saturating"
    if corroborated >= 1:
        return "corroborating"
    if l2 >= 1:
        return "deepening"
    if l3 >= 1:
        return "survey"
    return "scoping"
