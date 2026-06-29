#!/usr/bin/env python3
"""Deterministic stub agent for offline condense tests.

condense.py invokes the agent as `<ROS_AGENT_CMD> -- "<prompt>"` with env ROS_AGENT_IN (path to the
unit .in.json) and ROS_AGENT_STAGE. This stub ignores the prompt, reads the payload from
ROS_AGENT_IN, and prints canned-but-valid JSON matching the stage protocol — so the full
source→L3→L2→L1→L0 chain runs without a real LLM.
"""
import json
import os
import sys


def main() -> int:
    stage = os.environ.get("ROS_AGENT_STAGE", "")
    in_path = os.environ.get("ROS_AGENT_IN", "")
    payload = json.loads(open(in_path, encoding="utf-8").read()) if in_path else {}

    if stage == "distill":
        title = payload.get("title") or (payload.get("cached_text", "")[:24]) or "source"
        out = {
            "proposition": f"要点：{title}",
            "claim_kind": "analysis",
            "facet": "f_main",
            "analysis_note": "stub distill",
            "verbatim_excerpt": (payload.get("cached_text") or "")[:40],
            "credibility": {
                "level": "medium",
                "rationale": "stub: single named source",
                "filter_trace": {"independence": "single", "quality_density": "ok"},
                "echo_chamber_flag": False,
            },
        }
    elif stage == "aggregate":
        l3_ids = [c["l3_id"] for c in payload.get("claims", [])]
        out = {"findings": [{
            "statement": f"综合发现（{payload.get('facet')}，{len(l3_ids)} 源）",
            "finding_type": "claim",
            "l3_ids": l3_ids,
            "credibility": {"level": "medium", "rationale": "stub aggregate",
                            "filter_trace": {"independence": "multi"}},
        }]} if l3_ids else {"findings": []}
    elif stage == "synthesize":
        facets = payload.get("facets", [])
        viewpoints = []
        all_l2 = []
        for fb in facets:
            l2_ids = [f["l2_id"] for f in fb.get("findings", [])]
            all_l2.extend(l2_ids)
            viewpoints.append({
                "facet": fb.get("facet"),
                "synthesis_kind": "theme",
                "narrative": f"关于 {fb.get('facet')} 的综合视角（stub）。",
                "stance": "emerging",
                "l2_ids": l2_ids,
                "confidence": "medium",
                "open_questions": [f"{fb.get('facet')} 仍需深挖什么？"],
                "credibility": {"level": "medium", "rationale": "stub synth",
                                "filter_trace": {"logic_fit": "ok"}},
            })
        # proposition reflects the underlying findings, so changing a source's content between
        # condense runs yields a genuinely new worldview version (drives the version-chain test).
        first_stmt = ""
        for fb in facets:
            if fb.get("findings"):
                first_stmt = fb["findings"][0].get("statement", "")
                break
        prop = f"本主题当前理解状态（stub 世界模型）：{first_stmt}"
        # simulate a real agent that closes the first still-open question this round answers
        open_qs = payload.get("open_questions", []) or []
        answered = [q["oq_id"] for q in open_qs[:1] if q.get("oq_id")]
        out = {
            "viewpoints": viewpoints,
            "worldview": {
                "summary_kind": "state_of_understanding",
                "proposition": prop,
                "confidence": "medium",
                "key_findings": all_l2,
                "open_questions": ["下一轮应检索什么？", "哪些 facet 仍稀薄？"],
                "credibility": {"level": "medium", "rationale": "stub worldview",
                                "filter_trace": {"recency": "fresh"}},
            },
            "answered_oq_ids": answered,
        }
    else:
        out = {}

    sys.stdout.write(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
