#!/usr/bin/env python3
"""Speech figures from WAV files: stacked spectrograms on one shared dB scale (and optional waveforms).

    make_audio_figs.py spec ref.wav base.wav ours.wav --labels "Reference,Baseline,Ours" --out figures/fig_spec \
                       [--fmax 8000] [--start 0 --dur 3] [--wave] [--width ieee-col] [--dpi 1600]

All clips share one color scale (relative to the loudest clip), so differences you see are real, not an
artefact of per-panel normalisation. Reads PCM WAV (8/16/24/32-bit) with the standard library; needs numpy.
The same call is used for the demo website's spectrogram images (the *_web.png output).
"""
from __future__ import annotations

import argparse
import sys
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _plot  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402


def read_wav(path: str) -> tuple[np.ndarray, int]:
    with wave.open(path, "rb") as w:
        sr, ch, sw, n = w.getframerate(), w.getnchannels(), w.getsampwidth(), w.getnframes()
        raw = w.readframes(n)
    if sw == 1:
        x = (np.frombuffer(raw, dtype=np.uint8).astype(np.float32) - 128) / 128
    elif sw == 2:
        x = np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768
    elif sw == 3:
        b = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
        x = ((b[:, 0].astype(np.int32) | (b[:, 1].astype(np.int32) << 8) | (b[:, 2].astype(np.int32) << 16)) << 8 >> 8).astype(np.float32) / 8388608
    elif sw == 4:
        x = np.frombuffer(raw, dtype="<i4").astype(np.float32) / 2147483648
    else:
        raise SystemExit(f"error: unsupported sample width {sw} in {path}")
    return x.reshape(-1, ch).mean(axis=1), sr


def stft_db(x: np.ndarray, n_fft: int = 1024, hop: int = 256) -> np.ndarray:
    if len(x) < n_fft:
        x = np.pad(x, (0, n_fft - len(x)))
    win = np.hanning(n_fft).astype(np.float32)
    frames = np.lib.stride_tricks.sliding_window_view(x, n_fft)[::hop]
    mag = np.abs(np.fft.rfft(frames * win, axis=1)).T
    return 20 * np.log10(np.maximum(mag, 1e-8))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", choices=["spec"])
    ap.add_argument("wavs", nargs="+")
    ap.add_argument("--labels", help="comma-separated panel labels (default: file names)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--fmax", type=float, default=None, help="top of the frequency axis in Hz (default: Nyquist)")
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--dur", type=float, default=None)
    ap.add_argument("--top-db", type=float, default=80.0)
    ap.add_argument("--wave", action="store_true", help="add a waveform strip above each spectrogram")
    ap.add_argument("--width", default="ieee-col")
    ap.add_argument("--dpi", type=int, default=1600)
    ap.add_argument("--font", type=float, default=8)
    args = ap.parse_args()
    labels = [s.strip() for s in args.labels.split(",")] if args.labels else [Path(p).stem for p in args.wavs]
    if len(labels) != len(args.wavs):
        raise SystemExit("error: --labels must match the number of WAV files")
    clips = []
    for p in args.wavs:
        x, sr = read_wav(p)
        a = int(args.start * sr)
        b = len(x) if args.dur is None else a + int(args.dur * sr)
        clips.append((x[a:b], sr))
    specs = [stft_db(x) for x, _ in clips]
    ref = max(float(s.max()) for s in specs)
    _plot.style(args.font)
    n = len(clips)
    rows = n * (2 if args.wave else 1)
    ratios = [1, 3] * n if args.wave else [1] * n
    fig, axes = plt.subplots(rows, 1, figsize=(_plot.width_of(args.width), (0.75 if args.wave else 1.15) * n + 0.35), gridspec_kw={"height_ratios": ratios, "hspace": 0.55 if args.wave else 0.25}, squeeze=False)
    axes = axes[:, 0]
    im = None
    for i, ((x, sr), S, lab) in enumerate(zip(clips, specs, labels)):
        t_end = len(x) / sr
        if args.wave:
            wax = axes[2 * i]
            wax.plot(np.arange(len(x)) / sr, x, lw=0.3, color="#333333")
            wax.set_xlim(0, t_end)
            wax.axis("off")
            wax.set_title(lab, fontsize=args.font, loc="left", pad=1)
        ax = axes[2 * i + 1] if args.wave else axes[i]
        fmax = args.fmax or sr / 2
        im = ax.imshow(np.clip(S - ref, -args.top_db, 0), origin="lower", aspect="auto", cmap="magma", vmin=-args.top_db, vmax=0,
                       extent=[0, t_end, 0, sr / 2 / 1000])
        ax.set_ylim(0, fmax / 1000)
        ax.set_ylabel("kHz")
        if not args.wave:
            ax.text(0.01, 0.92, lab, transform=ax.transAxes, color="white", va="top", fontsize=args.font, fontweight="bold")
        if i < n - 1:
            ax.set_xticklabels([])
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    axes[-1].set_xlabel("Time (s)")
    cb = fig.colorbar(im, ax=list(axes), pad=0.02, fraction=0.04)
    cb.set_label("dB re. loudest clip")
    written = _plot.export(fig, args.out, args.dpi, {"kind": "spectrogram", "inputs": [{"file": p, "sha256": _plot.sha256_of(p)} for p in args.wavs],
                                                      "labels": labels, "top_db": args.top_db, "shared_scale_db_ref": ref})
    print("wrote " + ", ".join(Path(w).name for w in written))
    print("caption hint: All panels share one color scale (dB relative to the loudest clip).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
