"""Image/screenshot → text (OCR / vision captioning).

Image-heavy posts (common on Xiaohongshu) must become text before retention. The PRIMARY path is
agent-driven: the search agent calls the `zai-mcp` tools (extract_text_from_screenshot /
analyze_image / analyze_data_visualization / understand_technical_diagram) and passes the resulting
text into the capture `content` — Python can't call an MCP server itself. This module provides:
  * a clear 'zai-mcp' default that returns status:'agent_required' (telling the agent to do it),
  * a local fallback (tesseract / paddleocr) for offline use, with the same resolution ladder,
  * a 'stub' backend for tests.
Backend override: ROS_OCR_BACKEND.
"""
from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
from pathlib import Path


def _sha(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def _ok(text: str, engine: str) -> dict:
    return {"status": "recognized", "engine": engine, "text": text,
            "text_hash": _sha(text), "char_count": len(text)}


def ocr(image: str, *, backend: str | None = None) -> dict:
    backend = backend or os.environ.get("ROS_OCR_BACKEND") or "zai-mcp"
    name = Path(image).name

    if backend == "stub":
        return _ok(f"[stub ocr for {name}]", "stub")

    if backend == "zai-mcp":
        return {"status": "agent_required", "engine": "zai-mcp", "text": None,
                "note": "Call zai-mcp (extract_text_from_screenshot / analyze_image) via the "
                        "researchos-search skill and pass the text into the capture content. "
                        "For an offline local OCR, set ROS_OCR_BACKEND=tesseract or paddleocr."}

    if not Path(image).is_file():
        return {"status": "failed", "engine": backend, "text": None,
                "reason": f"not a file: {image}"}

    if backend == "tesseract":
        exe = shutil.which(os.environ.get("ROS_TESSERACT", "tesseract"))
        if not exe:
            return {"status": "failed", "engine": "tesseract", "text": None,
                    "reason": "tesseract not found"}
        try:
            out = subprocess.run([exe, image, "stdout"], check=True, capture_output=True,
                                 text=True, timeout=120).stdout.strip()
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as e:
            return {"status": "failed", "engine": "tesseract", "text": None, "reason": str(e)}
        return _ok(out, "tesseract") if out else {"status": "failed", "engine": "tesseract",
                                                  "text": None, "reason": "empty OCR"}

    if backend == "paddleocr":
        try:
            from paddleocr import PaddleOCR  # type: ignore
        except ImportError:
            return {"status": "failed", "engine": "paddleocr", "text": None,
                    "reason": "paddleocr not installed"}
        try:
            res = PaddleOCR(use_angle_cls=True, lang="ch").ocr(image, cls=True)  # pragma: no cover
            lines = [ln[1][0] for page in (res or []) for ln in (page or [])]
            text = "\n".join(lines)
        except Exception as e:  # noqa: BLE001  # pragma: no cover
            return {"status": "failed", "engine": "paddleocr", "text": None, "reason": str(e)}
        return _ok(text, "paddleocr")

    return {"status": "failed", "engine": backend, "text": None,
            "reason": f"unknown backend '{backend}'"}
