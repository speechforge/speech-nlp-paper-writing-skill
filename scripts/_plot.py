"""Shared plotting style: venue column widths, colour-blind-safe palette, and triple export."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

# Okabe-Ito palette (colour-blind safe). The proposed method always gets VERMILLION.
OKABE = ["#0072B2", "#E69F00", "#009E73", "#56B4E9", "#CC79A7", "#F0E442", "#999999"]
VERMILLION = "#D55E00"
HATCHES = ["", "//", "..", "xx", "\\\\", "++", "--"]
WIDTHS = {"ieee-col": 3.5, "ieee-wide": 7.16, "acl-col": 3.03, "acl-wide": 6.3, "single": 6.0}


def style(font_size: float = 8) -> None:
    plt.rcParams.update({
        "font.family": "serif", "font.serif": ["STIXGeneral", "Times New Roman", "DejaVu Serif"], "mathtext.fontset": "stix",
        "font.size": font_size, "axes.labelsize": font_size, "axes.titlesize": font_size, "legend.fontsize": font_size - 1,
        "xtick.labelsize": font_size - 1, "ytick.labelsize": font_size - 1, "axes.linewidth": 0.6,
        "axes.spines.top": False, "axes.spines.right": False, "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none",
        "savefig.bbox": "tight", "savefig.pad_inches": 0.02, "figure.dpi": 150,
    })


def width_of(name: str) -> float:
    try:
        return float(name)
    except ValueError:
        if name not in WIDTHS:
            raise SystemExit(f"error: unknown width '{name}'. Use one of {', '.join(WIDTHS)} or a number in inches")
        return WIDTHS[name]


def color_for(label: str, i: int, highlight: str | None) -> str:
    if highlight and label.lower() == highlight.lower():
        return VERMILLION
    return OKABE[i % len(OKABE)]


def export(fig, out: str, dpi: int, source: dict | None = None) -> list[str]:
    """Write vector PDF + print PNG (dpi, default 1600) + 200 dpi web PNG + a source record."""
    out_p = Path(out)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    written = []
    for suffix, kw in ((".pdf", {}), (".png", {"dpi": dpi}), ("_web.png", {"dpi": 200})):
        path = str(out_p) + suffix
        fig.savefig(path, **kw)
        written.append(path)
    if source is not None:
        rec = Path(str(out_p) + ".source.json")
        rec.write_text(json.dumps(source, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        written.append(str(rec))
    plt.close(fig)
    return written


def sha256_of(path: str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
