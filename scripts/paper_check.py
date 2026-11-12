#!/usr/bin/env python3
"""Project-level checks for a manuscript workspace created by paper_init.py.

    paper_check.py PROJECT todos        unresolved markers (TODO, TBD, [CITATION NEEDED], lorem ipsum ...)
    paper_check.py PROJECT assets       missing figure files, undefined or duplicate labels and references
    paper_check.py PROJECT log          summarise the LaTeX log (errors, undefined refs, overfull boxes)
    paper_check.py PROJECT thread       is the novelty carried through every section?
    paper_check.py PROJECT claims       draft claim_evidence_map rows from Abstract + Introduction sentences
    paper_check.py PROJECT build        compile with latexmk/pdflatex when installed, record the result
    paper_check.py PROJECT ready        run everything, print a gate table, write .paper/checks.json

Standard library only. A missing TeX installation is reported, never faked.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import load_json, now_iso, save_json, strip_tex_noise, tex_files, venue_words  # noqa: E402

HERE = Path(__file__).resolve().parent
MARKERS = re.compile(r"\bTODO\b|\bFIXME\b|\bXXX\b|\bTBD\b|\[CITATION NEEDED|PLACEHOLDER|\\todo\b|lorem ipsum|\?\?|\[INSERT|<fill", re.I)
SECTION_KEYS = {
    "abstract": r"abstract",
    "introduction": r"introduction",
    "method": r"method|approach|model|system|framework|proposed",
    "experiments": r"experiment|result|evaluation|analysis|ablation",
    "conclusion": r"conclusion|discussion|closing|summary",
}
CLAIM_CUE = re.compile(r"\b(we (?:propose|introduce|present|show|demonstrate|find|achieve|develop|formulate|release)|outperform|improv|reduc|achiev|first|novel|new|enable|robust|efficient|faster|better|state-of-the-art)", re.I)


def paper_dir(root: Path) -> Path:
    return root / "paper" if (root / "paper").is_dir() else root


def read_tex(root: Path) -> dict[Path, str]:
    return {p: p.read_text(encoding="utf-8", errors="replace") for p in tex_files(paper_dir(root))}


def split_sections(root: Path) -> dict[str, str]:
    """Map canonical section keys to their text by heading; falls back to file names."""
    out = {k: "" for k in SECTION_KEYS}
    for p, text in read_tex(root).items():
        text = strip_tex_noise(text)
        pieces = re.split(r"(\\section\*?\{[^}]*\}|\\begin\{abstract\}|\\end\{abstract\})", text)
        current = None
        if re.search(r"abstract", p.stem, re.I):
            current = "abstract"
        elif any(re.search(v, p.stem, re.I) for v in SECTION_KEYS.values()):
            current = next(k for k, v in SECTION_KEYS.items() if re.search(v, p.stem, re.I))
        for piece in pieces:
            if piece.startswith("\\begin{abstract}"):
                current = "abstract"
                continue
            if piece.startswith("\\end{abstract}"):
                current = None
                continue
            m = re.match(r"\\section\*?\{([^}]*)\}", piece)
            if m:
                title = m.group(1)
                current = next((k for k, v in SECTION_KEYS.items() if re.search(v, title, re.I)), None)
                continue
            if current:
                out[current] += "\n" + piece
    return out


def cmd_todos(root: Path, quiet=False) -> list[str]:
    hits = []
    targets = list(tex_files(paper_dir(root))) + [p for p in paper_dir(root).rglob("*.bib")]
    targets += [root / n for n in ("paper_story.md", "claim_evidence_map.md") if (root / n).exists()]
    for p in targets:
        for i, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if MARKERS.search(line):
                hits.append(f"{p.relative_to(root)}:{i}: {line.strip()[:100]}")
    if not quiet:
        print("\n".join(hits) or "no unresolved markers")
    return hits


def cmd_assets(root: Path, quiet=False) -> list[str]:
    problems, labels, refs = [], {}, {}
    pdir = paper_dir(root)
    for p, text in read_tex(root).items():
        clean = re.sub(r"(?<!\\)%.*", "", text)
        for m in re.finditer(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", clean):
            name = m.group(1)
            base = (p.parent / name) if (p.parent / name).parent.exists() else (pdir / name)
            cands = [base] + [Path(str(base) + e) for e in (".pdf", ".png", ".jpg", ".jpeg", ".eps", ".svg")]
            cands += [pdir / name, *(Path(str(pdir / name) + e) for e in (".pdf", ".png", ".jpg"))]
            if not any(c.exists() for c in cands):
                problems.append(f"{p.name}: figure file not found: {name}")
        for m in re.finditer(r"\\label\{([^}]+)\}", clean):
            if m.group(1) in labels:
                problems.append(f"duplicate label {m.group(1)}")
            labels[m.group(1)] = p.name
        for m in re.finditer(r"\\(?:ref|eqref|autoref|cref|Cref|pageref)\{([^}]+)\}", clean):
            for k in m.group(1).split(","):
                refs.setdefault(k.strip(), p.name)
        for m in re.finditer(r"\\input\{([^}]+)\}", clean):
            f = pdir / (m.group(1) if m.group(1).endswith(".tex") else m.group(1) + ".tex")
            if not f.exists() and not (p.parent / f.name).exists():
                problems.append(f"{p.name}: \\input target missing: {m.group(1)}")
    for k, f in refs.items():
        if k not in labels:
            problems.append(f"{f}: reference to undefined label '{k}'")
    if not quiet:
        print("\n".join(problems) or "all figure files and labels resolve")
    return problems


def cmd_log(root: Path, quiet=False) -> list[str]:
    logs = list(paper_dir(root).glob("*.log"))
    if not logs:
        if not quiet:
            print("no LaTeX log found (build has not run)")
        return ["no LaTeX log; run `paper_check.py PROJECT build`"]
    text = max(logs, key=lambda p: p.stat().st_mtime).read_text(encoding="utf-8", errors="replace")
    probs = [f"LaTeX error: {m.strip()[:100]}" for m in re.findall(r"^! (.+)$", text, re.M)]
    probs += [f"undefined: {m}" for m in sorted(set(re.findall(r"(?:Citation|Reference) `([^']+)' .*?undefined", text)))]
    over = [float(x) for x in re.findall(r"Overfull \\hbox \(([\d.]+)pt", text)]
    if over and max(over) > 10:
        probs.append(f"{sum(1 for o in over if o > 10)} overfull boxes wider than 10pt (worst {max(over):.0f}pt)")
    if not quiet:
        print("\n".join(probs) or "log is clean")
    return probs


def novelty_terms(root: Path, extra: list[str] | None) -> list[str]:
    if extra:
        return extra
    story = root / "paper_story.md"
    if story.exists():
        m = re.search(r"^\s*(?:[-*]\s*)?\**Novelty keywords\**\s*:\s*(.+)$", story.read_text(encoding="utf-8"), re.I | re.M)
        if m:
            return [t.strip().strip("`*") for t in re.split(r"[;,]", m.group(1)) if t.strip() and "<" not in t]
    return []


def cmd_thread(root: Path, terms: list[str] | None = None, quiet=False) -> list[str]:
    terms = novelty_terms(root, terms)
    if not terms:
        msg = "no novelty keywords: add a 'Novelty keywords: a, b, c' line to paper_story.md (or pass --terms)"
        if not quiet:
            print(msg)
        return [msg]
    secs = split_sections(root)
    rows, problems = [], []
    for k in SECTION_KEYS:
        text = secs[k].lower()
        present = [t for t in terms if t.lower() in text]
        rows.append((k, len(text.split()), present))
        if text.strip() and not present:
            problems.append(f"novelty thread broken: no novelty keyword appears in {k}")
        if not text.strip():
            problems.append(f"section not found or empty: {k}")
    if not quiet:
        print(f"novelty keywords: {', '.join(terms)}")
        for k, n, present in rows:
            print(f"  {k:13} {n:5} words  {'OK  ' + ', '.join(present) if present else 'MISSING'}")
    return problems


def cmd_claims(root: Path, quiet=False) -> str:
    secs = split_sections(root)
    sents = []
    for key in ("abstract", "introduction"):
        for s in re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", secs[key])):
            s = re.sub(r"\\[a-zA-Z]+\*?\{?|[{}]", "", s).strip()
            if len(s.split()) >= 6 and CLAIM_CUE.search(s):
                sents.append((key, s))
    rows = ["| # | Claim (from draft) | Where | Evidence (table / figure / number) | Scope limit | Status |", "|---|---|---|---|---|---|"]
    rows += [f"| {i} | {s[:160]} | {k} | _fill_ | _fill_ | Needs evidence |" for i, (k, s) in enumerate(sents, 1)]
    out = "\n".join(rows)
    if not quiet:
        print(out if sents else "no claim-like sentences found in Abstract/Introduction")
    return out


def claim_map_status(root: Path) -> tuple[dict, list[str]]:
    f = root / "claim_evidence_map.md"
    counts = {"supported": 0, "partial": 0, "open": 0}
    probs = []
    if not f.exists():
        return counts, ["claim_evidence_map.md is missing"]
    for line in f.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or re.match(r"^\|[\s:-]+\|", line):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        status = cells[-1].lower() if cells else ""
        if status in ("status", "") or "claim" in cells[0].lower() and "evidence" in line.lower() and status == "audit status":
            continue
        if status.startswith("supported"):
            counts["supported"] += 1
        elif status.startswith("partial") or "bound" in status:
            counts["partial"] += 1
        elif status.startswith(("needs", "unsupported", "open", "weak")):
            counts["open"] += 1
    if counts["open"]:
        probs.append(f"{counts['open']} claim(s) still need evidence, bounding, or removal")
    if counts["supported"] + counts["partial"] + counts["open"] == 0:
        probs.append("claim_evidence_map.md has no claim rows yet")
    return counts, probs


def cmd_build(root: Path, quiet=False) -> dict:
    pdir = paper_dir(root)
    main = next((p for p in (pdir / "main.tex", *pdir.glob("*.tex")) if p.exists() and r"\documentclass" in p.read_text(encoding="utf-8", errors="replace")), None)
    rec = {"checked_at": now_iso(), "main": str(main.relative_to(root)) if main else None}
    if not main:
        rec["status"] = "no-main-tex"
    elif shutil.which("latexmk"):
        cmd = ["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", main.name]
        t0 = time.time()
        r = subprocess.run(cmd, cwd=main.parent, capture_output=True, text=True)
        rec.update(command=" ".join(cmd), exit_code=r.returncode, seconds=round(time.time() - t0, 1),
                   status="ok" if r.returncode == 0 else "failed")
    elif shutil.which("pdflatex"):
        t0, code = time.time(), 0
        for step in (["pdflatex", "-interaction=nonstopmode", main.name], ["bibtex", main.stem],
                     ["pdflatex", "-interaction=nonstopmode", main.name], ["pdflatex", "-interaction=nonstopmode", main.name]):
            code = subprocess.run(step, cwd=main.parent, capture_output=True, text=True).returncode or code
        rec.update(command="pdflatex+bibtex", exit_code=code, seconds=round(time.time() - t0, 1), status="ok" if code == 0 else "failed")
    else:
        rec["status"] = "tex-unavailable"
        rec["note"] = "No LaTeX installation found. Compile on Overleaf or install TeX Live; static checks still run."
    pdf = main.with_suffix(".pdf") if main else None
    if pdf and pdf.exists() and rec.get("status") == "ok":
        rec["pdf_sha256"] = hashlib.sha256(pdf.read_bytes()).hexdigest()
    save_json(root / ".paper" / "build_record.json", rec)
    if not quiet:
        print(f"build: {rec['status']}" + (f" - {rec['note']}" if rec.get("note") else ""))
    return rec


def run_script(name: str, *args: str) -> tuple[int, str]:
    r = subprocess.run([sys.executable, str(HERE / name), *args], capture_output=True, text=True)
    return r.returncode, (r.stdout.strip().splitlines() or [""])[-1]


def cmd_ready(root: Path, terms: list[str] | None) -> int:
    gates = []

    def gate(name, ok, detail, kind="fail"):
        gates.append({"gate": name, "ok": ok, "detail": detail, "kind": kind})

    todos = cmd_todos(root, True)
    gate("No unresolved markers", not todos, f"{len(todos)} marker(s)" + (f"; first: {todos[0]}" if todos else ""))
    code, _ = run_script("citations.py", "check", str(root), "--strict")
    r = subprocess.run([sys.executable, str(HERE / "citations.py"), "check", str(root), "--strict"], capture_output=True, text=True)
    out_lines = [ln for ln in r.stdout.splitlines() if ln.startswith(("ERROR", "cited keys"))]
    gate("Citations verified (two sources + claim support)", code == 0, out_lines[0] if out_lines else "no citations")
    code, last = run_script("prose_lint.py", str(paper_dir(root)), "--fail-on", "high")
    gate("Prose: no coding terms or hollow openers", code == 0, last)
    assets = cmd_assets(root, True)
    gate("Figures, labels, and inputs resolve", not assets, f"{len(assets)} problem(s)" + (f"; first: {assets[0]}" if assets else ""))
    thread = cmd_thread(root, terms, True)
    gate("Novelty thread runs through every section", not thread, thread[0] if thread else "all sections carry the novelty", "warn")
    counts, cprobs = claim_map_status(root)
    gate("Every claim has evidence", not cprobs, cprobs[0] if cprobs else f"{counts['supported']} supported, {counts['partial']} bounded")
    ledger = load_json(root / "experiments" / "ledger.json", {"experiments": []})
    open_exp = [e["id"] for e in ledger.get("experiments", []) if e.get("status") not in ("ingested", "cancelled")]
    gate("No experiment left pending", not open_exp, ", ".join(open_exp) or "none pending", "warn")
    meta = load_json(root / "project_meta.json", {})
    pdir = paper_dir(root)
    alltex = "\n".join(read_tex(root).values())
    has_credit = bool(re.search(r"CRediT|Author Contributions?|Contributor", alltex, re.I))
    has_license = bool(re.search(r"Licen[cs]e", alltex, re.I))
    gate("Credit and license statements present", has_credit and has_license,
         ("credit " + ("ok" if has_credit else "MISSING") + ", license " + ("ok" if has_license else "MISSING")))
    gate("Project identity free of venue names", not venue_words(meta.get("project_name", "")), meta.get("project_name", "(not set)"))
    r = subprocess.run([sys.executable, str(HERE / "venue_check.py"), str(root), "--quiet"], capture_output=True, text=True)
    summ = next((ln for ln in r.stdout.splitlines() if ln.startswith("SUMMARY")), "")
    gate("Venue requirements and checklist", r.returncode == 0, (summ.replace("SUMMARY ", "") or r.stderr.strip()[:90]) + "  (see submission_checklist.md)")
    build = cmd_build(root, True)
    gate("LaTeX build", build.get("status") == "ok", build.get("status", "?") + (f" - {build['note']}" if build.get("note") else ""), "warn" if build.get("status") == "tex-unavailable" else "fail")
    save_json(root / ".paper" / "checks.json", {"checked_at": now_iso(), "gates": gates, "claims": counts})
    width = max(len(g["gate"]) for g in gates)
    for g in gates:
        mark = "PASS" if g["ok"] else ("WARN" if g["kind"] == "warn" else "FAIL")
        print(f"{mark}  {g['gate']:<{width}}  {g['detail']}")
    failed = [g for g in gates if not g["ok"] and g["kind"] == "fail"]
    print(f"\n{'READY' if not failed else 'NOT READY'}: {len(failed)} blocking gate(s), {sum(1 for g in gates if not g['ok'] and g['kind'] == 'warn')} warning(s)")
    return 1 if failed else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project")
    ap.add_argument("command", choices=["todos", "assets", "log", "thread", "claims", "build", "ready"])
    ap.add_argument("--terms", help="comma-separated novelty keywords for `thread`")
    args = ap.parse_args()
    root = Path(args.project).resolve()
    terms = [t.strip() for t in args.terms.split(",")] if args.terms else None
    if args.command == "ready":
        return cmd_ready(root, terms)
    result = {"todos": lambda: cmd_todos(root), "assets": lambda: cmd_assets(root), "log": lambda: cmd_log(root),
              "thread": lambda: cmd_thread(root, terms), "claims": lambda: cmd_claims(root), "build": lambda: cmd_build(root)}[args.command]()
    return 1 if args.command in ("todos", "assets", "thread") and result else 0


if __name__ == "__main__":
    raise SystemExit(main())
