"""Narración con Piper (voz neuronal offline es_MX)."""
import os, re, wave, json
from piper import PiperVoice, SynthesisConfig
from content import PRONUNCIATION

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL = os.path.join(ROOT, "assets", "voice", "es_MX-ald-medium.onnx")
_voice = None


def speakable(text):
    t = text
    for a, b in PRONUNCIATION:
        t = re.sub(r"(?<![\w])" + re.escape(a) + r"(?![\w])", b, t)
    t = t.replace("→", " a ").replace("%", " por ciento").replace("~", "unos ")
    return t


def synth(text, path, speed=0.93):
    global _voice
    if _voice is None:
        _voice = PiperVoice.load(MODEL)
    cfg = SynthesisConfig(length_scale=speed, noise_scale=0.6, noise_w_scale=0.75)
    with wave.open(path, "wb") as wf:
        _voice.synthesize_wav(speakable(text), wf, syn_config=cfg)
    with wave.open(path, "rb") as wf:
        return wf.getnframes() / wf.getframerate()
