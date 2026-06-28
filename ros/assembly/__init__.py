"""Priming / context-assembly: turn a topic's accumulated knowledge into the next search's brief.

Deterministic only — Python loads, counts, and freezes context; the search agent does the reasoning
about what to pursue. gap.py (coverage metrics) → stage.py (research stage) → context.py (assemble +
freeze the brief)."""
