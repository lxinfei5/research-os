"""Media → text. Video is transcribed (whisper) and images OCR'd BEFORE retention, so every cached
source is text. transcribe.py runs a local tool ladder; image_ocr.py prefers the agent's zai-mcp
path with a local fallback. Both degrade to a status:'failed' record rather than crashing."""
