"""Draw the F-01 before/after NVDA waveforms (RMS envelope of the NVDA-only audio) as SVGs for the report.
usage: python report/make_waveforms.py   (needs numpy)"""
import wave
from pathlib import Path
import numpy as np

HERE = Path(__file__).parent
EV = HERE.parent / "evidence" / "F-01"


def waveform_svg(wav, marks, label, w=1500, h=170, secs=5.0, color="#5eead4", t0=0.8):
    with wave.open(str(wav)) as r:
        sr, n, ch = r.getframerate(), r.getnframes(), r.getnchannels()
        a = np.frombuffer(r.readframes(n), dtype=np.int16).astype(np.float32)
    if ch > 1:
        a = a.reshape(-1, ch).mean(axis=1)
    a = a[int(t0 * sr): int(secs * sr)]  # skip NVDA's start-up speech
    bins = 300
    step = max(1, len(a) // bins)
    env = np.array([np.sqrt(np.mean(a[i:i + step] ** 2)) for i in range(0, step * bins, step)])
    env = env / (env.max() or 1)
    mid, bw = h / 2, w / bins
    bars = "".join(
        f'<rect x="{i*bw:.1f}" y="{mid - max(1.5, v*mid*0.92):.1f}" width="{bw*0.7:.1f}" height="{max(3, v*h*0.92):.1f}" rx="1" fill="{color}"/>'
        for i, v in enumerate(env))
    ann = ""
    for t, text, kind in marks:
        x = (t - t0) / (secs - t0) * w
        col = "#fbbf24" if kind == "key" else "#e5e7eb"
        y = 22 if kind == "key" else h - 10
        ann += f'<line x1="{x:.0f}" y1="0" x2="{x:.0f}" y2="{h}" stroke="{col}" stroke-width="2" stroke-dasharray="{"6 5" if kind == "key" else "0"}"/>'
        ann += (f'<text x="{x+8:.0f}" y="{y}" fill="{col}" font-size="22" font-family="Segoe UI, Arial" paint-order="stroke" '
                f'stroke="#0f172a" stroke-width="7" font-weight="{600 if kind == "key" else 400}">{text}</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{label}">'
            f'<rect width="{w}" height="{h}" fill="#0f172a"/>{bars}{ann}</svg>')


(HERE / "f01_before.svg").write_text(waveform_svg(
    EV / "before_bob_listen.wav",
    [(1.01, "Enter", "key"), (1.3, "(silence)", "say"), (3.00, "Tab", "key"), (3.2, "“Moon, link, heading, level 3”", "say")],
    "Before the fix: after Enter, NVDA says nothing; after Tab it reads Moon, link, heading, level 3 from the page behind the dialog",
    color="#f87171"), encoding="utf8")
(HERE / "f01_after.svg").write_text(waveform_svg(
    EV / "after_bob_listen.wav",
    [(1.01, "Enter", "key"), (1.2, "“Sign In, dialog”", "say"), (3.01, "Tab", "key"), (3.2, "“Close modal, button”", "say")],
    "After the fix: after Enter, NVDA says Sign In, dialog; after Tab it says Close modal, button"), encoding="utf8")
print("wrote f01_before.svg, f01_after.svg")
