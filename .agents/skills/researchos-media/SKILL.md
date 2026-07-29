---
name: researchos-media
description: Turn media into text for ResearchOS — transcribe video/audio to text (whisper) and OCR images to text (zai-mcp agent path / local fallback). This is PERCEPTION, not reasoning. Use before capturing any video/image source into a topic's knowledge.
---

# ResearchOS — Media → Text (perception, no engine)

Media → text is **感知 (perception)**, not semantic judgment — so it has no Python module. YOU the
agent run these tools directly and write the text to the topic's `transcripts/` or the source's
cached text. Do this **before** writing a source into `knowledge.md` (a video/image is not evidence
until its content is text).

## Video / audio → text (whisper)

Toolchain: convert to 16kHz mono WAV, then ASR with `whisper-cli` (whisper.cpp).

1. **Convert** (macOS uses `afconvert`; elsewhere `ffmpeg`):
   ```bash
   # macOS
   afconvert -f WAVE -d LEI16@16000 -c 1 in.mp4 out.wav
   # linux / fallback
   ffmpeg -y -i in.mp4 -ar 16000 -ac 1 -f wav out.wav
   ```
2. **Transcribe**:
   ```bash
   whisper-cli -m /path/to/ggml-<model>.bin -l <lang> -otxt -of transcript out.wav
   # optional domain bias for the topic (e.g. 大模型术语):  add  --prompt "<bias terms>"
   ```
   - `whisper-cli` may be named `main` in some whisper.cpp builds — resolve whichever is on PATH.
   - Model: a `ggml-*.bin` (set via your env, e.g. `ROS_WHISPER_MODEL`); pick size to taste.
   - `-l`: `zh` for 中文 content, `en` for English, `auto` to detect.
3. **Write** the resulting text to `topics/<slug>/transcripts/<item_id>.txt` (and reference it from
   the source's provenance in `knowledge.md` / `sources/<hash>.md`).

If `whisper-cli` / model / converter is missing, say so loudly (a degraded note on the source:
`media_transcript: UNKNOWN (whisper-cli not found)`) — never fake a transcript.

## Image → text (OCR)

Default path is **agent-driven zai-mcp** (you call the OCR MCP tools yourself), local fallback for
offline.

1. **zai-mcp (preferred)**: call the image tools — `extract_text_from_screenshot`, `analyze_image`,
   `analyze_data_visualization`, or `understand_technical_diagram` — on the image, and use the
   returned text/caption as the source's text.
2. **Local fallback (offline)**: `tesseract <image> stdout -l chi_sim+eng` (or `paddleocr`).
3. Write the text to the topic's `cache/<hash>.md` alongside the source, or into `transcripts/`.

## Discipline

- Media→text is a **pre-capture** step: transcribe/OCR first, then write the source + its text into
  `sources/` and reference it in `knowledge.md`.
- Transcripts/screenshots live in `topics/<slug>/transcripts/` and `screenshots/` (committed);
  heavy media (mp4/wav) is transient — delete after transcription.
- This skill replaced `ros/media/transcribe.py` + `ros/media/image_ocr.py` (deleted 2026-07-29).
  The commands above are exactly what those modules shelled out to.
