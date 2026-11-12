#!/usr/bin/env python3
"""CSV -> publication-style booktabs table: no vertical rules, best value in bold, metric direction in the header.

    make_latex_table.py results.csv --caption "Main results on ..." --label tab:main [--family ieee|acl]
        [--aggregate method] [--decimals 2] [--columns "method,pitch_err_hz,mos"] [--names "Method,Pitch error (Hz),MOS"]
        [--direction "pitch_err_hz:down,mos:up"] [-o paper/tables/main.tex]

Rules applied (from the skill): zero vertical rules; direction arrows in headers; units in headers, not cells;
bold only the best value per column when a direction is given; caption ABOVE the table for IEEE family and
BELOW for ACL family; with --aggregate KEY, repeated rows (seeds) become "mean $\\pm$ sample std".
A column named X_ci or X_std next to X is merged as "X $\\pm$ value".
"""
from __future__ import annotations

import argparse
import csv
import re
import statistics
import sys
from collections import OrderedDict
from pathlib import Path

ESC = {"&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}"}
ARROW = {"up": r"$\uparrow$", "down": r"$\downarrow$"}


def esc(s: str) -> str:
    return "".join(ESC.get(c, c) for c in s)


def isnum(v: str) -> bool:
    try:
        float(v)
        return True
    except (TypeError, ValueError):
        return False


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv")
    ap.add_argument("--caption", default="")
    ap.add_argument("--label", default="tab:results")
    ap.add_argument("--family", choices=["ieee", "acl", "generic"], default="ieee")
    ap.add_argument("--aggregate", help="column(s) that identify a row; repeated rows are averaged", default=None)
    ap.add_argument("--decimals", type=int, default=2)
    ap.add_argument("--columns")
    ap.add_argument("--names")
    ap.add_argument("--direction", help="col:up|down,... (up = higher is better)", default="")
    ap.add_argument("--wide", action="store_true", help="use table* (spans both columns)")
    ap.add_argument("-o", "--output")
    args = ap.parse_args()
    with open(args.csv, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        raise SystemExit("error: empty CSV")
    allcols = list(rows[0])
    err_for = {}
    for c in allcols:
        m = re.fullmatch(r"(.+?)_(ci|std|sd|sem)", c)
        if m and m.group(1) in allcols:
            err_for[m.group(1)] = c
    cols = [c.strip() for c in args.columns.split(",")] if args.columns else [c for c in allcols if c not in err_for.values()]
    for c in cols:
        if c not in allcols:
            raise SystemExit(f"error: column '{c}' not in CSV ({', '.join(allcols)})")
    names = [n.strip() for n in args.names.split(",")] if args.names else cols
    if len(names) != len(cols):
        raise SystemExit("error: --names must match --columns")
    direction = dict(p.split(":") for p in args.direction.split(",") if ":" in p)
    for c, d in direction.items():
        if d not in ARROW:
            raise SystemExit(f"error: direction for {c} must be up or down")
    if args.aggregate:
        keys = [k.strip() for k in args.aggregate.split(",")]
        groups = OrderedDict()
        for r in rows:
            groups.setdefault(tuple(r[k] for k in keys), []).append(r)
        merged = []
        for k, rs in groups.items():
            out = {c: rs[0][c] for c in keys}
            for c in cols:
                if c in keys:
                    continue
                vals = [float(r[c]) for r in rs if isnum(r[c])]
                if vals:
                    out[c] = statistics.fmean(vals)
                    out[c + "_std"] = statistics.stdev(vals) if len(vals) > 1 else 0.0
                    err_for[c] = c + "_std"
                else:
                    out[c] = rs[0][c]
            merged.append(out)
        rows = merged
    best = {}
    for c, d in direction.items():
        vals = [float(r[c]) for r in rows if isnum(str(r.get(c, "")))]
        if vals:
            best[c] = max(vals) if d == "up" else min(vals)
    dec = args.decimals
    body = []
    for r in rows:
        cells = []
        for c in cols:
            v = r[c]
            if isnum(str(v)):
                txt = f"{float(v):.{dec}f}"
                if c in best and abs(float(v) - best[c]) < 10 ** (-dec) / 2:
                    txt = r"\textbf{" + txt + "}"
                if c in err_for and isnum(str(r.get(err_for[c], ""))) and round(float(r[err_for[c]]), dec) != 0:
                    txt += rf" {{\scriptsize$\pm${float(r[err_for[c]]):.{dec}f}}}"
            else:
                txt = esc(str(v))
            cells.append(txt)
        body.append(" & ".join(cells) + r" \\")
    heads = [esc(n) + (" " + ARROW[direction[c]] if c in direction else "") for n, c in zip(names, cols)]
    align = "l" + "c" * (len(cols) - 1)
    env = "table*" if args.wide else "table"
    cap = rf"\caption{{{esc(args.caption) if args.caption else '[INSERT: caption that states what is shown, the metric direction, and the takeaway]'}}}\label{{{args.label}}}"
    lines = [rf"\begin{{{env}}}[t]", r"\centering", r"\small"]
    if args.family == "ieee":
        lines.append(cap)
    lines += [rf"\begin{{tabular}}{{{align}}}", r"\toprule", " & ".join(heads) + r" \\", r"\midrule", *body, r"\bottomrule", r"\end{tabular}"]
    if args.family != "ieee":
        lines.append(cap)
    lines.append(rf"\end{{{env}}}")
    text = "\n".join(lines) + "\n"
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"wrote {args.output}")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
