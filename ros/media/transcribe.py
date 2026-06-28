"""Video/audio → text (ASR). Adapted from AStockOS lib/media_transcript.py.

Tool-resolution ladder (never crashes on the wrong machine): explicit arg → env → default name →
PATH probe (shutil.which) → status:'failed'. On macOS the converter is `afconvert` (16kHz mono WAV),
elsewhere `ffmpeg`; ASR is `whisper-cli` (whisper.cpp) with an optional per-topic domain-bias prompt.

Returns an auditable record dict; writes the transcript to topics/<slug>/transcripts/ when a slug is
given. Set ROS_MEDIA_BACKEND=stub for deterministic offline runs/tests.
"""
from __future__ import annotations

import hashlib
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

from .. import paths


def _resolve(explicit: str | None, env_var: str, *candidates: str) -> str | None:
    if explicit:
        return explicit if (os.path.isabs(explicit) or shutil.which(explicit)) else None
    env = os.environ.get(env_var)
    if env:
        return env if (os.path.isabs(env) or shutil.which(env)) else None
    for c in candidates:
        hit = shutil.which(c)
        if hit:
            return hit
    return None


def _sha(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def _fail(reason: str, **extra) -> dict:
    return {"status": "failed", "transcript_text": None, "reason": reason, **extra}


def transcribe(media: str, *, slug: str | None = None, prompt: str | None = None,
               backend: str | None = None, whisper_cli: str | None = None,
               model: str | None = None, language: str = "zh") -> dict:
    """Transcribe a LOCAL audio/video file → text. (URL fetch is the agent's job — download via the
    search skill, then pass the local path here.) Returns {status, transcript_text, transcript_hash,
    char_count, engine, ...}."""
    backend = backend or os.environ.get("ROS_MEDIA_BACKEND") or "whisper"
    name = Path(media).name

    if backend == "stub":
        text = f"[stub transcript for {name}]"
        rec = {"status": "transcribed", "engine": "stub", "transcript_text": text,
               "transcript_hash": _sha(text), "char_count": len(text)}
        return _maybe_write(slug, name, rec)

    if backend != "whisper":
        return _fail(f"unknown backend '{backend}'")

    src = Path(media)
    if not src.is_file():
        return _fail(f"not a local file: {media} (download it first, then transcribe)")

    cli = _resolve(whisper_cli, "ROS_WHISPER_CLI", "whisper-cli", "main")
    if not cli:
        return _fail("whisper-cli not found (set ROS_WHISPER_CLI or install whisper.cpp)",
                     engine="whisper")
    mdl = model or os.environ.get("ROS_WHISPER_MODEL")
    if not mdl or not Path(mdl).is_file():
        return _fail("whisper model not found (set ROS_WHISPER_MODEL to a ggml-*.bin path)",
                     engine="whisper")

    is_mac = platform.system() == "Darwin"
    converter = _resolve(None, "ROS_AUDIO_CONVERTER", "afconvert" if is_mac else "ffmpeg", "ffmpeg")
    if not converter:
        return _fail("audio converter not found (afconvert/ffmpeg)", engine="whisper")

    work = (paths.transcripts_dir(slug) if slug else src.parent)
    work.mkdir(parents=True, exist_ok=True)
    wav = work / (src.stem + ".16k.wav")
    try:
        if Path(converter).name == "afconvert":
            subprocess.run([converter, "-f", "WAVE", "-d", "LEI16@16000", "-c", "1",
                            str(src), str(wav)], check=True, capture_output=True, timeout=600)
        else:
            subprocess.run([converter, "-y", "-i", str(src), "-ar", "16000", "-ac", "1",
                            str(wav)], check=True, capture_output=True, timeout=600)
        out_base = work / src.stem
        cmd = [cli, "-m", mdl, "-l", language, "-otxt", "-of", str(out_base), str(wav)]
        if prompt:
            cmd += ["--prompt", prompt]
        subprocess.run(cmd, check=True, capture_output=True, timeout=1800)
        txt_path = Path(str(out_base) + ".txt")
        text = txt_path.read_text(encoding="utf-8").strip() if txt_path.is_file() else ""
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as e:
        return _fail(f"transcription failed: {e}", engine="whisper")
    finally:
        try:
            wav.unlink(missing_ok=True)
        except OSError:
            pass

    if not text:
        return _fail("empty transcript", engine="whisper")
    return {"status": "transcribed", "engine": "whisper", "transcript_text": text,
            "transcript_hash": _sha(text), "char_count": len(text),
            "transcript_path": str(work / (src.stem + ".txt"))}


def _maybe_write(slug: str | None, name: str, rec: dict) -> dict:
    if slug and rec.get("transcript_text"):
        d = paths.transcripts_dir(slug)
        d.mkdir(parents=True, exist_ok=True)
        fp = d / (Path(name).stem + ".txt")
        fp.write_text(rec["transcript_text"], encoding="utf-8")
        rec["transcript_path"] = str(fp)
    return rec
