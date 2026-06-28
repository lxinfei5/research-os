"""ResearchOS — multi-topic research system with per-topic L0–L3 world knowledge.

Engine principle (inherited from AStockOS): Python NEVER reasons or calls an LLM. This package only
orchestrates deterministically, counts, validates, and persists. All semantic work (search,
distillation, credibility, synthesis) is done by agents reading versioned methodology, then handed
back here through gated writers.
"""
__version__ = "0.0.1"  # Phase 0 — foundation
