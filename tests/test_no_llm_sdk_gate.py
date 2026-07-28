"""Locks in the iron-rule SDK-import guard (lint_no_llm_sdk): Python never calls an LLM via SDK.

Pure/static — no network, no built .db. The sanctioned LLM call is the condense AGENT step shelling
out to `claude -p` (ros/run), and ros/media perception (whisper/OCR) is subprocess/MCP — neither
imports an LLM SDK, so the real tree must pass clean.
"""
from __future__ import annotations

from ros.boundary import gates


def test_no_llm_sdk_gate_registered():
    assert gates.lint_no_llm_sdk in gates.ALL_GATES


def test_no_llm_sdk_real_tree_clean():
    name, ok, problems = gates.lint_no_llm_sdk()
    assert name == "no_llm_sdk"
    assert ok, f"iron rule violated — LLM SDK imported in ros/: {problems}"


def test_no_llm_sdk_detects_import_and_from(tmp_path):
    (tmp_path / "bad_import.py").write_text("import anthropic\n", encoding="utf-8")
    (tmp_path / "bad_from.py").write_text("from openai import OpenAI\n", encoding="utf-8")
    (tmp_path / "clean.py").write_text("import ast\nimport subprocess\n", encoding="utf-8")
    sub = tmp_path / "pkg"
    sub.mkdir()
    (sub / "bad_nested.py").write_text("import openai\n", encoding="utf-8")

    violations = gates._llm_sdk_violations(tmp_path)
    joined = "\n".join(violations)
    assert any("anthropic" in v for v in violations)
    assert any("openai" in v for v in violations)
    assert "bad_nested.py" in joined          # recursion into subpackages
    assert "clean.py" not in joined           # subprocess / ast are NOT flagged
    assert len(violations) == 3
