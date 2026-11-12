#!/usr/bin/env python3
"""Draw a method / pipeline / teaser block diagram from a small JSON spec. Deterministic, works on any agent.

    make_diagram.py spec.json --out figures/fig_method [--width ieee-wide] [--dpi 1600]

spec.json:
{
  "direction": "LR",                       # layout is left to right
  "blocks": [
    {"id": "wav",  "label": "Speech\\nwaveform", "kind": "io"},
    {"id": "enc",  "label": "Boundary\\ndetector", "kind": "module", "new": true, "group": "Generator"},
    {"id": "loss", "label": "Phase loss", "kind": "loss", "new": true}
  ],
  "edges": [ {"from": "wav", "to": "enc"}, {"from": "enc", "to": "loss", "label": "boundaries"},
             {"from": "loss", "to": "enc", "style": "dashed", "label": "gradient"} ],
  "legend": true
}
Blocks marked "new": true get the accent outline, so the figure shows the novelty at a glance.
Use short labels (two lines at most). Exact numbers never belong in a diagram; use make_plots.py for results.
For a polished illustration an image generator may be used when the agent has one; this tool is the always-available fallback.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _plot  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402
from matplotlib.path import Path as MplPath  # noqa: E402

FILL = {"io": "#F2F2F2", "module": "#DCEBF7", "loss": "#FCE9D6", "data": "#E4F3E8", "other": "#FFFFFF"}


def layers(blocks, edges):
    """Longest-path layering; back edges (cycles) are ignored for layout."""
    ids = [b["id"] for b in blocks]
    succ = {i: [] for i in ids}
    for e in edges:
        if e["from"] in succ and e["to"] in succ and not e.get("style") == "dashed":
            succ[e["from"]].append(e["to"])
    depth = {i: 0 for i in ids}
    for _ in range(len(ids)):
        changed = False
        for a in ids:
            for b in succ[a]:
                if depth[b] < depth[a] + 1 and depth[a] + 1 < len(ids):
                    depth[b] = depth[a] + 1
                    changed = True
        if not changed:
            break
    return depth


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("--out", required=True)
    ap.add_argument("--width", default="ieee-wide")
    ap.add_argument("--dpi", type=int, default=1600)
    ap.add_argument("--font", type=float, default=8)
    args = ap.parse_args()
    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    blocks, edges = spec["blocks"], spec.get("edges", [])
    ids = {b["id"] for b in blocks}
    for e in edges:
        if e["from"] not in ids or e["to"] not in ids:
            raise SystemExit(f"error: edge {e['from']} -> {e['to']} refers to an unknown block id")
    depth = layers(blocks, edges)
    columns: dict[int, list[dict]] = {}
    for b in blocks:
        columns.setdefault(depth[b["id"]], []).append(b)
    longest = max(len(line) for b in blocks for line in b["label"].replace("\\n", "\n").split("\n"))
    bw, bh, gap_main, gap_cross = max(1.3, 0.12 * longest), 0.62, 0.9, 0.55
    pos = {}
    for d, col in columns.items():
        for k, b in enumerate(col):
            pos[b["id"]] = (d * (bw + gap_main), -(k - (len(col) - 1) / 2) * (bh + gap_cross))
    groups: dict[str, list[str]] = {}
    for b in blocks:
        if b.get("group"):
            groups.setdefault(b["group"], []).append(b["id"])
    frames = {}
    for name, members in groups.items():
        gx = [pos[m][0] for m in members]
        gy = [pos[m][1] for m in members]
        frames[name] = (min(gx) - bw / 2 - 0.12, max(gx) + bw / 2 + 0.12, min(gy) - bh / 2 - 0.14, max(gy) + bh / 2 + 0.28)
    ys_all = [p[1] for p in pos.values()]
    top_base = max([max(ys_all) + bh / 2] + [f[3] for f in frames.values()]) + 0.22
    bot_base = min([min(ys_all) - bh / 2] + [f[2] for f in frames.values()]) - 0.22
    # Edges: neighbours get a gentle curve; longer forward edges ride a lane above the blocks and
    # back edges a lane below, so no connector ever crosses an unrelated block.
    routes, n_top, n_bot = [], 0, 0
    for e in edges:
        (x0, y0), (x1, y1) = pos[e["from"]], pos[e["to"]]
        span = depth[e["to"]] - depth[e["from"]]
        if e.get("style") == "dashed" and span <= 0 or span < 0:
            n_bot += 1
            lane = bot_base - 0.2 * (n_bot - 1)
            pts = [(x0, y0 - bh / 2), (x0, lane), (x1, lane), (x1, y1 - bh / 2)]
        elif span > 1:
            n_top += 1
            lane = top_base + 0.2 * (n_top - 1)
            pts = [(x0, y0 + bh / 2), (x0, lane), (x1, lane), (x1, y1 + bh / 2)]
        else:
            pts = [(x0 + bw / 2, y0), (x1 - bw / 2, y1)]
        routes.append((e, pts))
    lanes_y = [pt[1] for _, pts in routes for pt in pts]
    all_y0 = min([min(ys_all) - bh / 2] + lanes_y) - 0.35
    all_y1 = max([max(ys_all) + bh / 2] + lanes_y) + 0.15
    all_x0 = min(p[0] for p in pos.values()) - bw / 2 - 0.2
    all_x1 = max(p[0] for p in pos.values()) + bw / 2 + 0.2
    _plot.style(args.font)
    W = _plot.width_of(args.width)
    fig, ax = plt.subplots(figsize=(W, max(1.3, W * (all_y1 - all_y0) / (all_x1 - all_x0))))
    ax.set_xlim(all_x0, all_x1)
    ax.set_ylim(all_y0, all_y1)
    ax.set_aspect("equal")
    ax.axis("off")
    for name, (x0, x1, y0, y1) in frames.items():
        ax.add_patch(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0, boxstyle="round,pad=0.02,rounding_size=0.08", fc="none", ec="#888888", lw=0.7, ls=(0, (4, 3)), zorder=0))
        ax.text((x0 + x1) / 2, y1 - 0.1, name, ha="center", va="center", fontsize=args.font - 1, color="#555555", style="italic")
    for b in blocks:
        x, y = pos[b["id"]]
        new = b.get("new")
        ax.add_patch(FancyBboxPatch((x - bw / 2, y - bh / 2), bw, bh, boxstyle="round,pad=0.02,rounding_size=0.09", fc=FILL.get(b.get("kind", "other"), "#FFFFFF"),
                                    ec=_plot.VERMILLION if new else "#333333", lw=1.8 if new else 0.8, zorder=2))
        ax.text(x, y, b["label"].replace("\\n", "\n"), ha="center", va="center", fontsize=args.font - 0.5, zorder=3, linespacing=1.1)
    for e, pts in routes:
        dashed = e.get("style") == "dashed"
        if len(pts) == 2:
            a, b2 = pts
            rad = 0.0 if abs(a[1] - b2[1]) < 1e-6 else 0.12
            patch = FancyArrowPatch(a, b2, arrowstyle="-|>", mutation_scale=8, lw=0.9, color="#333333", ls=(0, (3, 2)) if dashed else "-",
                                    connectionstyle=f"arc3,rad={rad}", zorder=1, shrinkA=0, shrinkB=0)
            lx, ly = (a[0] + b2[0]) / 2, (a[1] + b2[1]) / 2 + 0.17
        else:
            path = MplPath(pts, [MplPath.MOVETO] + [MplPath.LINETO] * (len(pts) - 1))
            patch = FancyArrowPatch(path=path, arrowstyle="-|>", mutation_scale=8, lw=0.9, color="#333333", ls=(0, (3, 2)) if dashed else "-", zorder=1, shrinkA=0, shrinkB=0)
            lx, ly = (pts[1][0] + pts[2][0]) / 2, pts[1][1] + (0.13 if pts[1][1] > 0 or pts[1][1] >= max(ys_all) else -0.13)
        ax.add_patch(patch)
        if e.get("label"):
            ax.text(lx, ly, e["label"], ha="center", va="center", fontsize=args.font - 2, color="#444444", zorder=4, bbox=dict(fc="white", ec="none", pad=0.4))
    if spec.get("legend", True) and any(b.get("new") for b in blocks):
        ax.text(all_x0, all_y0 + 0.02, "orange outline: new in this work", fontsize=args.font - 1.5, color=_plot.VERMILLION, va="bottom")
    written = _plot.export(fig, args.out, args.dpi, {"kind": "diagram", "spec": spec})
    print("wrote " + ", ".join(Path(w).name for w in written))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
