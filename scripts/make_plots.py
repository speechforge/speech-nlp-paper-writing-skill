#!/usr/bin/env python3
"""Deterministic result plots from a CSV: bar, line, pareto, heat. Numbers come from data, never from a model.

    make_plots.py bar    results.csv --x method --y mos [--group dataset] [--err mos_ci] [--highlight Ours] --out figures/fig_mos
    make_plots.py line   results.csv --x snr --y wer --series method [--err wer_std] --out figures/fig_noise
    make_plots.py pareto results.csv --x rtf --y mos --label method [--xlog] [--x-lower-better] --out figures/fig_pareto
    make_plots.py heat   results.csv --row language --col metric --value score --out figures/fig_heat

Common options: --ylabel "MOS (higher is better)" --width ieee-col|ieee-wide|acl-col|acl-wide|<inches> --dpi 1600
If several rows share an x (for example seeds) and no --err column is given, the script reports mean +/- sample std
and prints the sentence to paste into the caption. Outputs: .pdf (vector), .png (print dpi), _web.png (200 dpi),
and .source.json (command, input hash, plotted numbers) so every figure can be regenerated and audited.
"""
from __future__ import annotations

import argparse
import csv
import statistics
import sys
from collections import OrderedDict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _plot  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402


def read(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        raise SystemExit(f"error: non-numeric value '{v}' where a number is required")


def aggregate(rows, keys: list[str], y: str, err: str | None):
    """Group rows by `keys`; return {key: (mean, error, n)} with error from --err or sample std."""
    groups: "OrderedDict[tuple, list[dict]]" = OrderedDict()
    for r in rows:
        groups.setdefault(tuple(r[k] for k in keys), []).append(r)
    out = {}
    for k, rs in groups.items():
        vals = [num(r[y]) for r in rs]
        mean = statistics.fmean(vals)
        if err:
            e = num(rs[0][err]) if len(rs) == 1 else statistics.fmean(num(r[err]) for r in rs)
        else:
            e = statistics.stdev(vals) if len(vals) > 1 else 0.0
        out[k] = (mean, e, len(vals))
    return out


def caption_hint(agg, err: str | None) -> str:
    n = {v[2] for v in agg.values()}
    if err:
        return f"Error bars show the '{err}' column."
    if max(n) > 1:
        runs = f"{min(n)}" if min(n) == max(n) else f"{min(n)}-{max(n)}"
        return f"Bars show the mean and error bars the sample standard deviation over {runs} runs."
    return "Single run per condition; no uncertainty can be shown."


def finish(fig, args, source, hint=""):
    written = _plot.export(fig, args.out, args.dpi, source)
    print("wrote " + ", ".join(Path(w).name for w in written))
    if hint:
        print("caption hint:", hint)


def bar(args):
    rows = read(args.csv)
    keys = [args.x] + ([args.group] if args.group else [])
    agg = aggregate(rows, keys, args.y, args.err)
    xs = list(OrderedDict.fromkeys(k[0] for k in agg))
    groups = list(OrderedDict.fromkeys(k[1] for k in agg)) if args.group else [None]
    _plot.style(args.font)
    fig, ax = plt.subplots(figsize=(_plot.width_of(args.width), args.height))
    w = 0.8 / len(groups)
    for gi, g in enumerate(groups):
        pos, vals, errs = [], [], []
        for xi, x in enumerate(xs):
            key = (x, g) if args.group else (x,)
            if key in agg:
                pos.append(xi + (gi - (len(groups) - 1) / 2) * w)
                vals.append(agg[key][0])
                errs.append(agg[key][1])
        present = [x for x in xs if ((x, g) if args.group else (x,)) in agg]
        if args.group:   # colour encodes the group; the proposed method is marked by a heavy outline, not a new colour
            colors = [_plot.OKABE[gi % len(_plot.OKABE)]] * len(present)
            edges = [1.6 if args.highlight and x.lower() == args.highlight.lower() else 0.4 for x in present]
        else:
            colors = [_plot.color_for(x, xs.index(x), args.highlight) for x in present]
            edges = 0.4
        ax.bar(pos, vals, w * 0.92, yerr=errs if any(errs) else None, capsize=2, color=colors, edgecolor="black", linewidth=edges,
               hatch=_plot.HATCHES[gi % len(_plot.HATCHES)] if args.group else "", error_kw={"linewidth": 0.6},
               label=str(g) if args.group else None)
    ax.set_xticks(range(len(xs)))
    ax.set_xticklabels(xs, rotation=args.rotate, ha="right" if args.rotate else "center")
    if args.group and args.highlight:
        for t in ax.get_xticklabels():
            if t.get_text().lower() == args.highlight.lower():
                t.set_fontweight("bold")
    ax.set_ylabel(args.ylabel or args.y)
    if args.ymin is not None:
        ax.set_ylim(bottom=args.ymin)
    if args.group:
        ax.legend(frameon=False, ncol=min(len(groups), 3))
    finish(fig, args, {"kind": "bar", "input": args.csv, "input_sha256": _plot.sha256_of(args.csv), "y": args.y,
                       "values": {" / ".join(k): {"mean": v[0], "error": v[1], "n": v[2]} for k, v in agg.items()}}, caption_hint(agg, args.err))


def line(args):
    rows = read(args.csv)
    agg = aggregate(rows, [args.series, args.x], args.y, args.err)
    series = list(OrderedDict.fromkeys(k[0] for k in agg))
    _plot.style(args.font)
    fig, ax = plt.subplots(figsize=(_plot.width_of(args.width), args.height))
    markers = "osD^v<>"
    for i, s in enumerate(series):
        pts = sorted(((float(k[1]), v) for k, v in agg.items() if k[0] == s), key=lambda t: t[0])
        x = [p[0] for p in pts]
        y = [p[1][0] for p in pts]
        e = [p[1][1] for p in pts]
        c = _plot.color_for(s, i, args.highlight)
        ax.plot(x, y, marker=markers[i % len(markers)], ms=3.5, lw=1.2, color=c, label=s)
        if any(e):
            ax.fill_between(x, [a - b for a, b in zip(y, e)], [a + b for a, b in zip(y, e)], color=c, alpha=0.18, linewidth=0)
    ax.set_xlabel(args.xlabel or args.x)
    ax.set_ylabel(args.ylabel or args.y)
    ax.legend(frameon=False)
    finish(fig, args, {"kind": "line", "input": args.csv, "input_sha256": _plot.sha256_of(args.csv), "y": args.y,
                       "values": {" / ".join(k): {"mean": v[0], "error": v[1], "n": v[2]} for k, v in agg.items()}}, caption_hint(agg, args.err))


def pareto(args):
    rows = read(args.csv)
    agg_x = aggregate(rows, [args.label], args.x, None)
    agg_y = aggregate(rows, [args.label], args.y, args.err)
    labels = list(agg_x)
    pts = [(agg_x[k][0], agg_y[k][0], k[0]) for k in labels]
    _plot.style(args.font)
    fig, ax = plt.subplots(figsize=(_plot.width_of(args.width), args.height))
    for i, (x, y, lab) in enumerate(pts):
        c = _plot.color_for(lab, i, args.highlight)
        ax.errorbar([x], [y], yerr=[agg_y[(lab,)][1]] if agg_y[(lab,)][1] else None, fmt="o", ms=5, color=c, capsize=2, elinewidth=0.6, markeredgecolor="black", markeredgewidth=0.4)
        ax.annotate(lab, (x, y), textcoords="offset points", xytext=(4, 4), fontsize=args.font - 1)
    # Pareto frontier: higher y is better; for x, lower is better unless --x-higher-better.
    better_x = (lambda a, b: a >= b) if args.x_higher_better else (lambda a, b: a <= b)
    front = sorted([p for p in pts if not any(q is not p and better_x(q[0], p[0]) and q[1] >= p[1] and (q[0] != p[0] or q[1] != p[1]) for q in pts)], key=lambda p: p[0])
    if len(front) > 1:
        ax.plot([p[0] for p in front], [p[1] for p in front], "--", color="#555555", lw=0.8, zorder=0)
    if args.xlog:
        ax.set_xscale("log")
        ax.set_xticks(sorted({p[0] for p in pts}))
        ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
        ax.minorticks_off()
    ax.set_xlabel(args.xlabel or args.x)
    ax.set_ylabel(args.ylabel or args.y)
    finish(fig, args, {"kind": "pareto", "input": args.csv, "input_sha256": _plot.sha256_of(args.csv), "points": [{"label": p[2], "x": p[0], "y": p[1]} for p in pts], "frontier": [p[2] for p in front]},
           "Dashed line connects the non-dominated points (better x and higher y).")


def heat(args):
    rows = read(args.csv)
    rs = list(OrderedDict.fromkeys(r[args.row] for r in rows))
    cs = list(OrderedDict.fromkeys(r[args.col] for r in rows))
    grid = [[float("nan")] * len(cs) for _ in rs]
    for r in rows:
        grid[rs.index(r[args.row])][cs.index(r[args.col])] = num(r[args.value])
    _plot.style(args.font)
    fig, ax = plt.subplots(figsize=(_plot.width_of(args.width), max(args.height, 0.3 * len(rs) + 0.8)))
    im = ax.imshow(grid, cmap="viridis", aspect="auto")
    ax.set_xticks(range(len(cs)), cs, rotation=args.rotate, ha="right" if args.rotate else "center")
    ax.set_yticks(range(len(rs)), rs)
    for i in range(len(rs)):
        for j in range(len(cs)):
            v = grid[i][j]
            if v == v:
                ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=args.font - 1.5, color="white" if v < (min(map(min, grid)) + max(map(max, grid))) / 2 else "black")
    fig.colorbar(im, ax=ax, label=args.ylabel or args.value, fraction=0.04, pad=0.02)
    for s in ("top", "right"):
        ax.spines[s].set_visible(True)
    finish(fig, args, {"kind": "heat", "input": args.csv, "input_sha256": _plot.sha256_of(args.csv), "rows": rs, "cols": cs, "grid": grid})


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="kind", required=True)
    for name in ("bar", "line", "pareto", "heat"):
        p = sub.add_parser(name)
        p.add_argument("csv")
        p.add_argument("--out", required=True, help="output path without extension")
        p.add_argument("--width", default="ieee-col")
        p.add_argument("--height", type=float, default=2.2)
        p.add_argument("--dpi", type=int, default=1600, help="print PNG dpi (skill rule: at least 1600 for raster line art)")
        p.add_argument("--font", type=float, default=8)
        p.add_argument("--highlight", help="label of the proposed method (drawn in vermillion)")
        p.add_argument("--ylabel")
        p.add_argument("--xlabel")
        p.add_argument("--err", help="column holding an error (std, CI half-width); default: sample std over repeated rows")
        p.add_argument("--rotate", type=int, default=0)
        if name == "bar":
            p.add_argument("--x", required=True), p.add_argument("--y", required=True), p.add_argument("--group"), p.add_argument("--ymin", type=float)
        if name == "line":
            p.add_argument("--x", required=True), p.add_argument("--y", required=True), p.add_argument("--series", required=True)
        if name == "pareto":
            p.add_argument("--x", required=True), p.add_argument("--y", required=True), p.add_argument("--label", required=True)
            p.add_argument("--xlog", action="store_true"), p.add_argument("--x-higher-better", action="store_true")
        if name == "heat":
            p.add_argument("--row", required=True), p.add_argument("--col", required=True), p.add_argument("--value", required=True)
    args = ap.parse_args()
    {"bar": bar, "line": line, "pareto": pareto, "heat": heat}[args.kind](args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
