"""Catalan transcription with word-level timestamps -> Remotion Caption[] JSON.

Usage: python scripts/transcribe.py public/source.mp4 public/captions.json [model]
Requires `pip install faster-whisper` and network access to huggingface.co
(the first run downloads the model, default large-v3).
"""
import json, sys
from faster_whisper import WhisperModel

src, out = sys.argv[1], sys.argv[2]
model_name = sys.argv[3] if len(sys.argv) > 3 else "large-v3"
model = WhisperModel(model_name, device="cpu", compute_type="int8")
segments, info = model.transcribe(
    src,
    language="ca",              # force Catalan, never translate
    task="transcribe",
    beam_size=10,
    best_of=5,
    temperature=0.0,
    word_timestamps=True,
    vad_filter=True,
    vad_parameters={"min_silence_duration_ms": 150},
    condition_on_previous_text=False,
    initial_prompt="Vídeo en català d'una discoteca. EZE. Que nos quiten lo bailao.",
)
caps = []
for seg in segments:
    for w in seg.words:
        caps.append({
            "text": w.word,  # keeps the leading space, as Remotion captions expect
            "startMs": round(w.start * 1000),
            "endMs": round(w.end * 1000),
            "timestampMs": round((w.start + w.end) / 2 * 1000),
            "confidence": round(w.probability, 3),
        })
        print(f"{w.start:6.2f}-{w.end:6.2f} {w.probability:.2f} {w.word}")
json.dump(caps, open(out, "w"), ensure_ascii=False, indent=1)
print(f"{len(caps)} words -> {out} (lang prob {info.language_probability:.2f})")
