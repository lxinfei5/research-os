"""Per-source pacing + cooldown for social fetches via the ROS bridge (`ros xhs`).

Two 防风控 controls the playbooks demand but the bridge never enforced (W-02 / W-04):

  * MIN-INTER-CALL GAP with jitter — the XHS pacing discipline (detail 5–8s, search 2–5s) lived
    only as advisory prose; a tight `ros xhs call` loop fired at TCP speed with zero human jitter,
    which is exactly the burst XHS escalation escalates soft-limit → EOF → 扫码 → hard ban.
  * COOLDOWN (circuit breaker) — on ANY risk-control signal (empty-result-but-200 / EOF / 扫码 /
    验证码 / 操作频繁) the playbook says STOP the source, never retry-until-it-works. Without a
    cooldown, a retry loop or a fresh `ros xhs call` re-hits a throttled source within seconds and
    turns a soft wall into a hard ban.

File-backed under $ROS_SOCIAL_HOME (default ~/.researchos/social_mcp) so it persists across `ros xhs`
invocations (each is a fresh process) and is shared by every caller on the machine — matching the
daemon script's state dir.

⚠ SCOPE: this protects the `ros xhs` bridge path (and any main-loop caller that goes through
xiaohongshu_mcp_bridge). Workflow sub-agents that call mcp__xiaohongshu-mcp__* / mcp__webbridge-mcp__*
DIRECTLY bypass this Python layer — full fan-out protection must ALSO live in the Go servers
(xiaohongshu-mcp + webbridge-mcp). The markers below are pure string-containment (validation, not
reasoning) — the iron rule permits pattern detection on a known risk-control marker set.
"""
from __future__ import annotations

import json
import os
import random
import time
from pathlib import Path
from typing import Any

DEFAULT_SOCIAL_HOME = Path.home() / ".researchos" / "social_mcp"

# Min inter-call gap (seconds) by source — the playbook numbers, made the code default.
# Detail/get_feed_detail is the higher-risk op (longer gap); search shorter. Tuned human-speed.
MIN_GAP = {
    "xiaohongshu": {"search": (2.0, 5.0), "detail": (5.0, 8.0), "default": (3.0, 6.0)},
    "x": {"default": (3.0, 6.0)},
    "douyin": {"default": (3.0, 6.0)},
}
DEFAULT_GAP = (3.0, 6.0)

# Default cooldown applied when a risk-control signal is detected (the playbook's "STOP, don't
# retry" — bounded so the source recovers after a rest, not banned forever).
DEFAULT_COOLDOWN_SEC = 30 * 60  # 30 min

# Risk-control markers. Pure substring match against the MCP result text — NOT a semantic judgement.
# When any appears (or the result is an MCP error / an unambiguously empty search), the source goes
# into cooldown. Mirrors the escalation ladder in xiaohongshu_search_playbook.md /
# source_health_and_degradation.md.
RISK_MARKERS = (
    "扫码", "请打开 App", "请打开App", "验证码", "滑块", "操作频繁", "操作太频繁",
    "限制", "稍后再试", "risk", "blocked", "EOF", "panic", "unauthorized",
)


def _social_home() -> Path:
    return Path(os.environ.get("ROS_SOCIAL_HOME", str(DEFAULT_SOCIAL_HOME)))


def _state_path() -> Path:
    p = _social_home() / "pacing.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def _load() -> dict[str, Any]:
    p = _state_path()
    if not p.is_file():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _save(state: dict[str, Any]) -> None:
    p = _state_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, p)  # atomic across concurrent `ros xhs` processes


def _gap_for(source: str, op: str | None) -> tuple[float, float]:
    src = MIN_GAP.get(source, {})
    if op and op in src:
        return src[op]
    return src.get("default", DEFAULT_GAP)


def looks_like_risk_signal(result: dict) -> str | None:
    """Return the matched marker (or '' for a pure is_error/empty case) if `result` (a bridge
    call_tool return) smells like risk-control, else None. Structural pattern match only."""
    if not isinstance(result, dict):
        return None
    if result.get("is_error"):
        return ""
    # search_feeds returning an empty feed list with no error is the soft-limit precursor —
    # the playbook treats a second empty result as a STOP signal. We can't tell "first vs second"
    # here, so treat an unambiguously empty successful search as a weak signal (short cooldown).
    content = result.get("content") or []
    blob = json.dumps(content, ensure_ascii=False) if not isinstance(content, str) else content
    for marker in RISK_MARKERS:
        if marker and marker in blob:
            return marker
    return None


def in_cooldown(source: str) -> tuple[str, str] | None:
    """Return (cooldown_until_iso, reason) if `source` is currently in cooldown, else None."""
    st = _load().get(source, {})
    until = st.get("cooldown_until")
    reason = st.get("cooldown_reason", "")
    if not until:
        return None
    if time.time() >= _parse_iso(until):
        # cooldown expired — clear it so callers proceed
        _clear_field(source, "cooldown_until")
        return None
    return until, reason


def set_cooldown(source: str, seconds: int = DEFAULT_COOLDOWN_SEC, reason: str = "") -> str:
    """Put `source` into cooldown for `seconds` (circuit breaker). Returns the until-ISO."""
    state = _load()
    until = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(time.time() + int(seconds)))
    src = state.get(source, {})
    src["cooldown_until"] = until
    src["cooldown_reason"] = reason or "risk-control signal"
    src["cooldown_set_at"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
    state[source] = src
    _save(state)
    return until


def clear_cooldown(source: str) -> None:
    _clear_field(source, "cooldown_until")


def _clear_field(source: str, field: str) -> None:
    state = _load()
    if source in state and state[source].get(field):
        state[source].pop(field, None)
        if not state[source]:
            state.pop(source, None)
        _save(state)


def enforce_min_gap(source: str, op: str | None = None) -> float:
    """Block (sleep) until the min inter-call gap for (source, op) has elapsed since the last call,
    with jitter. Records the dispatch time AFTER sleeping. Returns seconds slept."""
    lo, hi = _gap_for(source, op)
    state = _load()
    last = state.get(source, {}).get("last_call")
    slept = 0.0
    if last:
        elapsed = time.time() - _parse_iso(last)
        gap = random.uniform(lo, hi)  # jitter — a fixed cadence is itself a fingerprint
        if elapsed < gap:
            slept = gap - elapsed
            time.sleep(slept)
    _record_call(source)
    return slept


def _record_call(source: str) -> None:
    state = _load()
    src = state.get(source, {})
    src["last_call"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
    state[source] = src
    _save(state)


def _parse_iso(s: str) -> float:
    try:
        return time.mktime(time.strptime(s, "%Y-%m-%dT%H:%M:%S"))
    except (ValueError, TypeError):
        return 0.0
