"""Per-frame music gain (ducking) derived from the original voice track.

Music file is normalised to -20 dBFS RMS. During speech it sits SPEECH_DB below
the voice; in pauses it rises to PAUSE_DB below the voice. Attack is fast so the
music ducks before the first syllable, release is slow so it never pumps.
"""
import json, subprocess, sys
import numpy as np

src, out = sys.argv[1], sys.argv[2]
FPS, SR = 30, 16000
SPEECH_DB, PAUSE_DB = -28.0, -22.0
MUSIC_RMS_DB = -20.0

pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-vn", "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                     capture_output=True, check=True).stdout
x = np.frombuffer(pcm, np.int16).astype(np.float64) / 32768
# voice band only, so ambience/bass does not count as speech
X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
X[(f < 120) | (f > 4000)] = 0
v = np.fft.irfft(X, len(x))
hop = SR // FPS
n = len(v) // hop + 1
db = np.array([10 * np.log10(np.mean(v[i*hop:(i+1)*hop] ** 2) + 1e-10) for i in range(n)])
speech_level = np.percentile(db, 75)
active = db > speech_level - 14
# look-ahead 3 frames (duck before the voice) and hold 6 frames
act = active.copy()
for i in range(n):
    if active[i:i+4].any() or active[max(0, i-6):i+1].any():
        act[i] = True
target = np.where(act, speech_level + SPEECH_DB, speech_level + PAUSE_DB) - MUSIC_RMS_DB
g = np.empty(n); g[0] = target[0]
for i in range(1, n):
    k = 0.55 if target[i] < g[i-1] else 0.08   # fast attack, slow release
    g[i] = g[i-1] + k * (target[i] - g[i-1])
gain = (10 ** (g / 20)).round(4).tolist()
json.dump({"fps": FPS, "speechLevelDb": round(float(speech_level), 1), "gain": gain}, open(out, "w"))
print(f"speech level {speech_level:.1f} dBFS, active {act.mean()*100:.0f}% of frames, gain range {min(gain)}..{max(gain)}")
