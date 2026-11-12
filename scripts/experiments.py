#!/usr/bin/env python3
"""Experiment-on-demand loop: find evidence gaps, write the experiment prompt, run it quietly, ingest a summary.

    experiments.py gaps    PROJECT                          claims whose status needs an experiment or evidence
    experiments.py brief   PROJECT --title T --claims 1,3 --hypothesis H [--gpu-hours 2] [--timeout-hours 4]
    experiments.py approve PROJECT EXP-001                  record the user's go-ahead (cost and compute)
    experiments.py run     PROJECT EXP-001 -- <command ...> start detached; logs go to a file, not to the agent
    experiments.py status  PROJECT [EXP-001]                one line per experiment (refreshes running -> done/failed)
    experiments.py tail    PROJECT EXP-001 [-n 20]          last log lines; use only when status says failed
    experiments.py ingest  PROJECT EXP-001 results.csv      copy results, write a compact summary, update the claim map

Token discipline: the agent reads the brief once, then only `status` lines and the ingested summary.
It never reads raw logs unless an experiment failed. Running needs approval unless
project_meta.json has experiments.auto_run = true (a durable, user-set authorisation).
Numbers in the paper must come from the ingested results file, never from the log text.
"""
from __future__ import annotations

import argparse
import csv
import os
import re
import shutil
import statistics
import subprocess
import sys
from collections import OrderedDict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import load_json, now_iso, save_json  # noqa: E402

BRIEF = """# Experiment brief {id}: {title}

_Self-contained prompt. Give this file to the agent or lab member that will run the experiment. Created {created}._

## Goal
{hypothesis}

## Why this experiment
It supports claim(s) {claims} in `claim_evidence_map.md`. Without it the claim is **{status}** and must be weakened or removed.

## Protocol (fill every line; do not leave a default silently)
- Data and splits: [INSERT: corpus, split, speaker/sentence disjointness]
- Systems compared: the proposed method and [INSERT: baselines with exact versions and matched budgets]
- Metrics (name, direction, toolkit and version): [INSERT]
- Seeds: at least 3 independent runs; report mean and sample standard deviation
- Human evaluation, if any: [INSERT: listener count, instructions, agreement statistic] (otherwise state "none")
- Budget: {gpu_hours} GPU-hours; wall-clock limit {timeout_hours} h. Stop early and report if the limit is reached.

## Deliverable
One CSV, one row per (system, condition, seed), with columns:
`system, condition, seed, <one column per metric>, notes`
Save it as `results.csv` in the working folder and do not post-process the numbers by hand.

## Rules
- Do not change the evaluation code between systems.
- Write all progress to the log file; print at most 8 lines of final summary: what ran, how many rows, any anomaly.
- Never print or paste identifiers, file names, or commands into the paper text. The paper describes the method in scientific language only.
- If a run fails, report the last 20 log lines and stop. Do not retry more than once.

## Done when
`results.csv` exists, has every (system, condition, seed) row, and the summary lists any missing cell.
"""


def paths(root: Path):
    return root / "experiments" / "ledger.json", root / "experiments"


def load_ledger(root: Path) -> dict:
    return load_json(paths(root)[0], {"experiments": []})


def get(ledger: dict, exp_id: str) -> dict:
    for e in ledger["experiments"]:
        if e["id"] == exp_id:
            return e
    raise SystemExit(f"error: unknown experiment {exp_id}")


def claim_rows(root: Path) -> list[dict]:
    f = root / "claim_evidence_map.md"
    if not f.exists():
        return []
    rows, header = [], None
    for line in f.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or re.match(r"^\|[\s:-]+\|", line):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if header is None:
            header = [c.lower() for c in cells]
            continue
        rows.append(dict(zip(header, cells)))
    return rows


def refresh(root: Path, ledger: dict) -> None:
    changed = False
    for e in ledger["experiments"]:
        if e["status"] != "running":
            continue
        exit_file = root / "experiments" / "logs" / f"{e['id']}.exit"
        alive = False
        try:
            os.kill(e["pid"], 0)
            alive = True
        except (OSError, TypeError):
            pass
        if exit_file.exists():
            code = int(exit_file.read_text().strip() or 1)
            e.update(status="done" if code == 0 else "failed", exit_code=code, finished=now_iso())
            changed = True
        elif not alive:
            e.update(status="failed", exit_code=-1, finished=now_iso(), note="process ended without an exit record")
            changed = True
    if changed:
        save_json(paths(root)[0], ledger)


def cmd_gaps(root: Path, a) -> int:
    rows = claim_rows(root)
    open_rows = [r for r in rows if r.get("status", "").lower().startswith(("needs", "unsupported", "partial"))]
    if not open_rows:
        print("no open claims; every row is Supported")
        return 0
    for r in open_rows:
        print(f"claim {r.get('#', '?')}: [{r.get('status')}] {r.get('claim (as worded in the paper)', r.get('claim', ''))[:110]}")
    print(f"\n{len(open_rows)} open. Mark rows 'Needs experiment' and run `brief` for each group of related claims.")
    return 0


def cmd_brief(root: Path, a) -> int:
    ledger = load_ledger(root)
    n = len(ledger["experiments"]) + 1
    exp_id = f"EXP-{n:03d}"
    meta = load_json(root / "project_meta.json", {})
    cap = meta.get("experiments", {}).get("max_gpu_hours_per_experiment", 0)
    gpu = a.gpu_hours if a.gpu_hours is not None else cap
    claims = [c.strip() for c in (a.claims or "").split(",") if c.strip()]
    rows = {r.get("#"): r for r in claim_rows(root)}
    status = next((rows[c]["status"] for c in claims if c in rows), "Needs experiment")
    brief = root / "experiments" / "briefs" / f"{exp_id}.md"
    brief.parent.mkdir(parents=True, exist_ok=True)
    brief.write_text(BRIEF.format(id=exp_id, title=a.title, created=now_iso(), hypothesis=a.hypothesis, claims=", ".join(claims) or "(none linked yet)",
                                  status=status, gpu_hours=gpu or "[INSERT]", timeout_hours=a.timeout_hours), encoding="utf-8")
    ledger["experiments"].append({"id": exp_id, "title": a.title, "claims": claims, "status": "proposed", "created": now_iso(),
                                  "brief": str(brief.relative_to(root)), "gpu_hours": gpu, "timeout_hours": a.timeout_hours})
    save_json(paths(root)[0], ledger)
    print(f"wrote {brief.relative_to(root)}  (status: proposed)")
    print("Next: complete the [INSERT] protocol lines, show the user the budget, and get approval before `run`.")
    return 0


def cmd_approve(root: Path, a) -> int:
    ledger = load_ledger(root)
    e = get(ledger, a.exp)
    e.update(status="approved", approved=now_iso())
    save_json(paths(root)[0], ledger)
    print(f"{a.exp} approved")
    return 0


def cmd_run(root: Path, a) -> int:
    ledger = load_ledger(root)
    e = get(ledger, a.exp)
    meta = load_json(root / "project_meta.json", {})
    auto = meta.get("experiments", {}).get("auto_run", False)
    if e["status"] not in ("approved", "failed") and not (auto and e["status"] == "proposed"):
        raise SystemExit(f"error: {a.exp} is '{e['status']}'. Show the brief and budget to the user, then run `approve` (or set experiments.auto_run in project_meta.json).")
    brief_text = (root / e["brief"]).read_text(encoding="utf-8")
    if "[INSERT" in brief_text:
        raise SystemExit("error: the brief still has [INSERT] protocol lines; complete them so the run is reproducible")
    cmd = a.run_cmd[1:] if a.run_cmd and a.run_cmd[0] == "--" else a.run_cmd
    if not cmd:
        raise SystemExit("error: give the command after --")
    logs = root / "experiments" / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    log, exit_file = logs / f"{a.exp}.log", logs / f"{a.exp}.exit"
    exit_file.unlink(missing_ok=True)
    secs = int(float(e.get("timeout_hours", 4)) * 3600)
    prefix = ["timeout", "-k", "30", str(secs)] if shutil.which("timeout") else []
    wrapped = ["sh", "-c", '"$@"; echo $? > "$0"', str(exit_file), *prefix, *cmd]
    with open(log, "ab") as fh:
        proc = subprocess.Popen(wrapped, cwd=str(root), stdout=fh, stderr=subprocess.STDOUT, start_new_session=True)
    e.update(status="running", pid=proc.pid, started=now_iso(), command=" ".join(cmd), log=str(log.relative_to(root)))
    save_json(paths(root)[0], ledger)
    print(f"{a.exp} running (pid {proc.pid}); log: {log.relative_to(root)}. Check with `status`; do not read the log unless it fails.")
    return 0


def cmd_status(root: Path, a) -> int:
    ledger = load_ledger(root)
    refresh(root, ledger)
    for e in ledger["experiments"]:
        if a.exp and e["id"] != a.exp:
            continue
        extra = f" exit={e['exit_code']}" if "exit_code" in e else ""
        print(f"{e['id']}  {e['status']:9}{extra}  {e['title']}" + (f"  | {e['summary']}" if e.get("summary") else ""))
    if not ledger["experiments"]:
        print("no experiments yet")
    return 0


def cmd_tail(root: Path, a) -> int:
    log = root / "experiments" / "logs" / f"{a.exp}.log"
    if not log.exists():
        raise SystemExit("error: no log yet")
    lines = log.read_text(encoding="utf-8", errors="replace").splitlines()[-a.n:]
    print("\n".join(l[:240] for l in lines))
    return 0


def cmd_ingest(root: Path, a) -> int:
    ledger = load_ledger(root)
    e = get(ledger, a.exp)
    src = Path(a.results)
    if not src.is_file():
        raise SystemExit(f"error: {src} not found")
    dst_dir = root / "experiments" / "results"
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / f"{a.exp}{src.suffix}"
    shutil.copyfile(src, dst)
    lines = [f"# Results summary {a.exp}: {e['title']}", ""]
    if src.suffix.lower() in (".csv", ".tsv"):
        with open(dst, newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh, delimiter="\t" if src.suffix.lower() == ".tsv" else ","))
        cols = list(rows[0]) if rows else []
        key = next((c for c in ("system", "method", "model") if c in cols), cols[0] if cols else None)
        seed = next((c for c in cols if "seed" in c.lower()), None)
        lines.append(f"- rows: {len(rows)}; columns: {', '.join(cols)}")
        if seed:
            lines.append(f"- seeds per system: {', '.join(sorted({r[seed] for r in rows}))}")
        else:
            lines.append("- WARNING: no seed column; uncertainty cannot be reported")
        if key:
            groups = OrderedDict()
            for r in rows:
                groups.setdefault(r[key], []).append(r)
            for c in cols:
                if c in (key, seed):
                    continue
                try:
                    stats = {g: [float(r[c]) for r in rs] for g, rs in groups.items()}
                except (ValueError, KeyError):
                    continue
                lines.append(f"- {c}: " + "; ".join(f"{g} {statistics.fmean(v):.4g}" + (f" (sd {statistics.stdev(v):.2g}, n={len(v)})" if len(v) > 1 else " (n=1)") for g, v in stats.items()))
    else:
        lines.append(f"- file: {dst.name} ({dst.stat().st_size} bytes); read it directly, it is not tabular")
    if a.summary:
        lines.append(f"- note: {a.summary}")
    (dst_dir / f"{a.exp}.summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    e.update(status="ingested", ingested=now_iso(), result_file=str(dst.relative_to(root)), summary=(a.summary or f"{len(lines) - 2} summary lines"))
    save_json(paths(root)[0], ledger)
    updated = 0
    cmap = root / "claim_evidence_map.md"
    if cmap.exists() and e.get("claims"):
        out, header = [], None
        for line in cmap.read_text(encoding="utf-8").splitlines():
            if line.startswith("|") and not re.match(r"^\|[\s:-]+\|", line):
                cells = [c.strip() for c in line.strip("|").split("|")]
                if header is None:
                    header = [c.lower() for c in cells]
                elif cells and cells[0] in e["claims"] and "experiment" in header:
                    cells[header.index("experiment")] = a.exp
                    if cells[-1].lower() == "needs experiment":
                        cells[-1] = "Needs evidence"
                    updated += 1
                    line = "| " + " | ".join(cells) + " |"
            out.append(line)
        cmap.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"ingested {dst.relative_to(root)}; summary: experiments/results/{a.exp}.summary.md; claim rows updated: {updated}")
    print("Next: read only the summary, copy the exact numbers into the paper, and set each linked claim to Supported or Partial.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("gaps", "brief", "approve", "run", "status", "tail", "ingest"):
        p = sub.add_parser(name)
        p.add_argument("project")
        if name == "brief":
            p.add_argument("--title", required=True), p.add_argument("--hypothesis", required=True), p.add_argument("--claims", default="")
            p.add_argument("--gpu-hours", type=float), p.add_argument("--timeout-hours", type=float, default=4)
        if name in ("approve", "run", "tail", "ingest"):
            p.add_argument("exp")
        if name == "status":
            p.add_argument("exp", nargs="?")
        if name == "run":
            p.add_argument("run_cmd", nargs=argparse.REMAINDER)
        if name == "tail":
            p.add_argument("-n", type=int, default=20)
        if name == "ingest":
            p.add_argument("results"), p.add_argument("--summary")
    a = ap.parse_args()
    root = Path(a.project).resolve()
    return {"gaps": cmd_gaps, "brief": cmd_brief, "approve": cmd_approve, "run": cmd_run, "status": cmd_status, "tail": cmd_tail, "ingest": cmd_ingest}[a.cmd](root, a)


if __name__ == "__main__":
    raise SystemExit(main())
