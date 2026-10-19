"""Original royalty-free reggaeton/dembow underscore, synthesised from scratch.

Two sections that share key and tempo so the change feels like one soundtrack:
  A (intro, 0 -> 4 bars): filtered perreo groove, sparse, nocturnal pads.
  B (4 bars ->): fuller dembow groove with sub-bass and plucks.
The A->B crossfade lands on bar 4, which is placed exactly on the 9.267 s cut.
"""
import numpy as np
import sys
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 48000
CUT = 9.2667          # scene change in the source video
BAR = CUT / 4         # tempo derived so bar 4 lands on the cut (~103.6 BPM)
BEAT = BAR / 4
STEP = BEAT / 4       # 16th note
DUR = 18.3 + 1.0
N = int(DUR * SR)
rng = np.random.default_rng(7)


def t_(sec):
    return np.arange(int(sec * SR)) / SR


def place(buf, sig, at, gain=1.0):
    i = int(at * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i] * gain


def lp(x, fc, order=2):
    return sosfilt(butter(order, fc, "low", fs=SR, output="sos"), x)


def hp(x, fc, order=2):
    return sosfilt(butter(order, fc, "high", fs=SR, output="sos"), x)


def kick():
    t = t_(0.45)
    f = 48 + 110 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 7.5) + 0.25 * np.sin(ph * 2) * np.exp(-t * 30)


def snare():
    t = t_(0.22)
    noise = hp(rng.standard_normal(len(t)), 1800) * np.exp(-t * 22)
    body = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30)
    return 0.55 * noise + 0.45 * body


def hat(open_=False):
    t = t_(0.18 if open_ else 0.05)
    n = hp(rng.standard_normal(len(t)), 7000, 4)
    return n * np.exp(-t * (18 if open_ else 80))


def rim():
    t = t_(0.06)
    return hp(np.sin(2 * np.pi * 1700 * t) + 0.4 * rng.standard_normal(len(t)), 900) * np.exp(-t * 90)


def midi(n):
    return 440 * 2 ** ((n - 69) / 12)


def pad(notes, dur):
    t = t_(dur)
    s = np.zeros_like(t)
    for n in notes:
        for det in (-0.08, 0.0, 0.08):
            f = midi(n + det)
            s += np.sign(np.sin(2 * np.pi * f * t)) * 0.3 + np.sin(2 * np.pi * f * t)
    env = np.minimum(1, t / 0.35) * np.minimum(1, (dur - t) / 0.4).clip(0)
    return lp(s * env, 1400) / (len(notes) * 3)


def pluck(n, dur=0.35):
    t = t_(dur)
    f = midi(n)
    s = (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(4 * np.pi * f * t) + 0.2 * np.sin(6 * np.pi * f * t))
    return lp(s * np.exp(-t * 9), 3200)


def sub(n, dur):
    t = t_(dur)
    f = midi(n)
    s = np.sin(2 * np.pi * f * t) + 0.15 * np.sin(4 * np.pi * f * t)
    env = np.minimum(1, t / 0.01) * np.exp(-t * 2.2) * np.minimum(1, (dur - t) / 0.03).clip(0)
    return s * env


# F minor, nocturnal: Fm - Db - Ab - Eb
CHORDS = [(53, [65, 68, 72]), (49, [61, 65, 68]), (56, [63, 68, 72]), (51, [63, 67, 70])]
DEMBOW_SN = [3, 6, 11, 14]          # classic dembow snare placements (16ths)
PERREO_SN = [3, 6, 11, 14]
TRESILLO = [0, 3, 6]                # 3-3-2 bass hits per half bar (in 16ths)

drumsA = np.zeros(N); drumsB = np.zeros(N)
musA = np.zeros(N); musB = np.zeros(N)
n_bars = int(DUR / BAR) + 1

for b in range(n_bars):
    t0 = b * BAR
    root, notes = CHORDS[b % 4]
    # ---- section A: filtered, softer
    place(musA, pad(notes, BAR + 0.3), t0, 0.9)
    for s in range(16):
        ts = t0 + s * STEP
        if s % 4 == 0 and b >= 1:
            place(drumsA, kick(), ts, 0.75)
        if s in PERREO_SN and b >= 1:
            place(drumsA, rim(), ts, 0.35)
        if s % 2 == 0:
            place(drumsA, hat(), ts, 0.18 if s % 4 else 0.1)
    # ---- section B: full dembow
    place(musB, pad(notes, BAR + 0.3), t0, 0.7)
    for half in (0, 8):
        for k, s in enumerate(TRESILLO):
            ln = (3 if k < 2 else 2) * STEP
            place(musB, sub(root - 12, ln * 0.95), t0 + (half + s) * STEP, 0.9)
    for s in range(16):
        ts = t0 + s * STEP
        if s % 4 == 0:
            place(drumsB, kick(), ts, 0.95)
        if s in DEMBOW_SN:
            place(drumsB, snare(), ts, 0.55)
        place(drumsB, hat(open_=(s % 8 == 6)), ts, 0.16 if s % 2 else 0.24)
        if s in (2, 7, 10, 15):
            place(musB, pluck(notes[(s // 4) % 3] + 12), ts, 0.22)

A = lp(drumsA, 2500) + lp(musA, 1100)
B = drumsB + musB

# equal-power crossfade over one beat, centred on the cut
t = np.arange(N) / SR
x = np.clip((t - (CUT - BEAT / 2)) / BEAT, 0, 1)
gA, gB = np.cos(x * np.pi / 2), np.sin(x * np.pi / 2)
# short filtered riser into the switch
riser = np.zeros(N)
rl = t_(BAR)
place(riser, hp(rng.standard_normal(len(rl)), 3000) * (rl / BAR) ** 3, CUT - BAR, 0.12)
mix = A * gA + B * gB + riser

# fade in / out
mix *= np.clip(t / 0.6, 0, 1) * np.clip((18.3 - t) / 1.2, 0, 1)
mix = np.tanh(mix * 0.9)

# simple stereo width: Haas on the music bed only
L = mix
R = np.concatenate([np.zeros(int(0.004 * SR)), mix[: -int(0.004 * SR)]]) * 0.5 + mix * 0.5
st = np.stack([L, R], 1)
# normalise to -20 dBFS RMS so gain values in Remotion are relative to a known level
rms = np.sqrt(np.mean(st[: int(18.3 * SR)] ** 2))
st *= 10 ** (-20 / 20) / rms
st = np.clip(st, -0.99, 0.99)
wavfile.write(sys.argv[1], SR, (st * 32767).astype(np.int16))
print(f"BPM={60/BEAT:.2f} bar={BAR:.4f}s")
