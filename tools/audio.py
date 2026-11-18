"""Música synthwave y efectos generados por código (100 % originales, sin copyright)."""
import numpy as np
import soundfile as sf

SR = 44100


def _note(n):  # MIDI -> Hz
    return 440.0 * 2 ** ((n - 69) / 12)


def _env(n, a, r):
    e = np.ones(n)
    a = min(int(a * SR), n); r = min(int(r * SR), n)
    if a: e[:a] = np.linspace(0, 1, a)
    if r: e[-r:] *= np.linspace(1, 0, r)
    return e


def _saw(f, n, detune=0.0):
    t = np.arange(n) / SR
    out = np.zeros(n)
    for d in (-detune, 0, detune):
        ph = (t * f * (1 + d)) % 1.0
        out += 2 * ph - 1
    return out / 3


def _lowpass(x, cutoff):
    # one-pole IIR, vectorised via cumulative trick is hard; use FFT brickwall-ish smooth filter
    X = np.fft.rfft(x)
    fr = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / (1 + (fr / cutoff) ** 4)
    return np.fft.irfft(X, len(x))


PROGS = {
    "sunset": ([57, 53, 48, 55], 100),   # Am F C G
    "mint":   ([50, 46, 53, 48], 96),    # Dm Bb F C
    "cyber":  ([52, 48, 55, 50], 108),   # Em C G D
    "fire":   ([45, 41, 48, 43], 104),
    "ocean":  ([55, 52, 48, 50], 92),    # G Em C D
    "retro":  ([53, 50, 46, 48], 100),
}


def music(duration, style="sunset", seed=0):
    rng = np.random.default_rng(seed)
    roots, bpm = PROGS.get(style, PROGS["sunset"])
    beat = 60 / bpm
    bar = beat * 4
    total = int(duration * SR) + SR
    out = np.zeros((total, 2))
    n_bar = int(bar * SR)
    # pre-render one cycle of 4 bars
    cyc = np.zeros((n_bar * 4, 2))
    minor = {0: [0, 3, 7], 1: [0, 4, 7], 2: [0, 4, 7], 3: [0, 4, 7]}
    for i, r in enumerate(roots):
        s = i * n_bar
        third = 3 if i == 0 or style in ("cyber", "ocean") and i in (0, 1) else 4
        chord = [r, r + third, r + 7, r + 12]
        pad = sum(_saw(_note(c), n_bar, 0.004) for c in chord) / 4
        pad = _lowpass(pad, 1400) * _env(n_bar, 0.4, 0.4) * 0.22
        cyc[s:s + n_bar, 0] += pad
        cyc[s:s + n_bar, 1] += np.roll(pad, 300)
        # bass 8ths
        step = int(beat / 2 * SR)
        for k in range(8):
            nb = _saw(_note(r - 12), step, 0.002)
            nb = _lowpass(nb, 500) * _env(step, 0.005, 0.08) * 0.42
            cyc[s + k * step:s + (k + 1) * step] += nb[:, None]
        # arp 16ths
        st = int(beat / 4 * SR)
        arp = [chord[j % 4] + 12 for j in (0, 1, 2, 3, 2, 1, 2, 3)]
        for k in range(16):
            f = _note(arp[k % 8])
            tt = np.arange(st) / SR
            a = (np.sign(np.sin(2 * np.pi * f * tt)) * 0.5 + np.sin(2 * np.pi * f * tt) * 0.5)
            a = _lowpass(a, 2500) * np.exp(-tt * 18) * 0.10
            pan = 0.5 + 0.35 * np.sin(k)
            cyc[s + k * st:s + (k + 1) * st, 0] += a * (1 - pan)
            cyc[s + k * st:s + (k + 1) * st, 1] += a * pan
    # drums
    nb = int(beat * SR)
    t = np.arange(nb) / SR
    kick = np.sin(2 * np.pi * (50 + 110 * np.exp(-t * 30)) * t) * np.exp(-t * 7) * 0.9
    noise = rng.uniform(-1, 1, nb)
    snare = (_lowpass(noise, 6000) * np.exp(-t * 16) * 0.35 + np.sin(2 * np.pi * 190 * t) * np.exp(-t * 25) * 0.2)
    hat_n = int(beat / 2 * SR)
    hat = (noise[:hat_n] - _lowpass(noise[:hat_n], 7000)) * np.exp(-np.arange(hat_n) / SR * 60) * 0.18
    for b in range(16):
        s = b * nb
        cyc[s:s + nb] += kick[:, None]
        if b % 2 == 1:
            cyc[s:s + nb] += snare[:, None]
        for h in range(2):
            hs = s + h * hat_n
            cyc[hs:hs + hat_n] += hat[:, None] * (0.6 if h == 0 else 1.0)
    # tile
    reps = total // len(cyc) + 1
    full = np.tile(cyc, (reps, 1))[:total]
    # fade in/out
    fi = int(1.5 * SR); fo = int(3 * SR)
    full[:fi] *= np.linspace(0, 1, fi)[:, None]
    full[-fo:] *= np.linspace(1, 0, fo)[:, None]
    full = np.tanh(full * 0.9)
    full /= np.max(np.abs(full)) + 1e-9
    return full * 0.8


def whoosh(seed=1):
    rng = np.random.default_rng(seed)
    n = int(0.6 * SR)
    t = np.arange(n) / SR
    x = rng.uniform(-1, 1, n)
    # sweep via chunks of lowpass
    out = np.zeros(n)
    chunks = 24
    for i in range(chunks):
        a, b = i * n // chunks, (i + 1) * n // chunks
        cut = 300 + 6000 * np.sin(np.pi * i / chunks)
        out[a:b] = _lowpass(x, cut)[a:b]
    env = np.sin(np.pi * t / t[-1]) ** 2
    out = out * env
    return np.stack([out, np.roll(out, 200)], 1) / (np.max(np.abs(out)) + 1e-9) * 0.5


def pop():
    n = int(0.15 * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * (900 - 2500 * t) * t) * np.exp(-t * 35)
    return np.stack([x, x], 1) * 0.35


def hit():
    n = int(1.2 * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(7)
    x = np.sin(2 * np.pi * (45 + 80 * np.exp(-t * 20)) * t) * np.exp(-t * 3.5)
    x += _lowpass(rng.uniform(-1, 1, n), 2500) * np.exp(-t * 9) * 0.5
    return np.stack([x, x], 1) * 0.7


def write(path, data):
    sf.write(path, data.astype(np.float32), SR)
