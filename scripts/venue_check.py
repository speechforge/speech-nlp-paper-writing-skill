#!/usr/bin/env python3
"""Venue requirements and checklist, checked against the project files.

    venue_check.py PROJECT [--venue neurips|icml|iclr|acl|ieee|aaai|colm|generic|<alias>] [--list] [--quiet]

Loads templates/venues.json (universal items + the venue's own items, including the NeurIPS 16-item paper
checklist, ICML broader-impact and reproducibility items, the ICLR LLM-use disclosure, ACL Limitations and
Responsible-NLP items, AAAI forbidden-package scan, COLM, IEEE). Each item is one of:
  OK       verified automatically from the project files
  FAIL     automatically checked and not satisfied (blocking items fail the readiness gate)
  CONFIRM  only the author can confirm (listed, never silently ticked)
  N/A      declared not applicable (for example no human subjects)
Writes PROJECT/submission_checklist.md. Exit code 1 when a blocking item FAILs.
Automatic checks are evidence, not proof: always read the venue's current call for papers.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import load_json  # noqa: E402
import paper_check  # noqa: E402

HERE = Path(__file__).resolve().parent
VENUES = HERE.parent / "templates" / "venues.json"


def strip_comments(t: str) -> str:
    return re.sub(r"(?<!\\)%.*", "", t)


def gather(root: Path, paths: list[str]) -> str:
    out = []
    for rel in paths:
        p = root / rel
        files = sorted(p.rglob("*.tex")) if p.is_dir() else ([p] if p.is_file() else [])
        out += [strip_comments(f.read_text(encoding="utf-8", errors="replace")) for f in files]
    # [INSERT: ...] placeholder text is a to-do, never evidence that a topic was written about
    return re.sub(r"\[INSERT[^\]]*\]", " ", "\n".join(out))


def words(t: str) -> int:
    t = re.sub(r"\[INSERT[^\]]*\]", " ", t)
    return len(re.findall(r"[A-Za-z]{2,}", re.sub(r"\\[a-zA-Z]+", " ", t)))


def dotted(d: dict, path: str):
    for k in path.split("."):
        d = d.get(k, {}) if isinstance(d, dict) else {}
    return d


def resolve(data: dict, venue: str) -> tuple[str, dict]:
    v = venue.lower()
    for vid, e in data["venues"].items():
        if v == vid or v in e.get("aliases", []):
            return vid, e
    raise SystemExit(f"error: unknown venue '{venue}'. Known: {', '.join(sorted(data['venues']))} (aliases: "
                     + ", ".join(a for e in data["venues"].values() for a in e.get("aliases", [])) + ")")


def run_item(root: Path, meta: dict, item: dict) -> tuple[str, str]:
    """Return (status, detail)."""
    cond = item.get("applies_if")
    if cond and not dotted(meta, cond):
        return "N/A", f"declared not applicable ({cond} is false in project_meta.json)"
    a = item["auto"]
    k = a["kind"]
    if k == "manual":
        return "CONFIRM", "author must confirm"
    if k == "file_ready":
        p = root / a["path"]
        if not p.is_file():
            return "FAIL", f"{a['path']} missing"
        t = strip_comments(p.read_text(encoding="utf-8", errors="replace"))
        if "[INSERT" in t:
            return "FAIL", "still has [INSERT] placeholders"
        n = words(t)
        return ("OK", f"{n} words") if n >= a.get("min_words", 8) else ("FAIL", f"only {n} words (need {a.get('min_words', 8)}+)")
    if k in ("regex", "regex_all"):
        text = gather(root, a["paths"])
        if not text.strip():
            return "FAIL", "the files to check are missing or empty"
        pats = a["patterns"] if k == "regex_all" else [a["pattern"]]
        miss = [p for p in pats if not re.search(p, text, re.I)]
        return ("OK", "evidence found in the text") if not miss else ("FAIL", f"no mention of: {miss[0][:60]}")
    if k == "forbidden":
        if a.get("only_if_anonymous") and not meta.get("anonymous", True):
            return "OK", "not anonymous mode; not applicable"
        text = gather(root, a["paths"])
        hits = [p for p in a["patterns"] if re.search(p, text, re.M)]
        return ("OK", "none found") if not hits else ("FAIL", f"found: {hits[0][:70]}")
    if k == "claims":
        _, probs = paper_check.claim_map_status(root)
        return ("OK", "no open claim rows") if not probs else ("FAIL", probs[0])
    if k == "citations":
        r = subprocess.run([sys.executable, str(HERE / "citations.py"), "check", str(root), "--strict"], capture_output=True, text=True)
        return ("OK", "all cited works verified") if r.returncode == 0 else ("FAIL", next((l for l in r.stdout.splitlines() if l.startswith("ERROR")), "citation check failed")[:110])
    if k == "statement":
        p = root / "paper" / "statements" / f"{a['name']}.tex"
        if not p.is_file():
            return "FAIL", f"{a['name']}.tex missing; run credits_license.py"
        t = strip_comments(p.read_text(encoding="utf-8"))
        return ("FAIL", "has [INSERT] placeholders") if "[INSERT" in t or not t.strip() else ("OK", "statement present")
    if k == "captions":
        text = gather(root, ["paper"])
        envs = len(re.findall(r"\\begin\{(figure|table)\*?\}", text))
        caps = len(re.findall(r"\\caption\b", text))
        return ("OK", f"{caps} captions for {envs} floats") if caps >= envs else ("FAIL", f"{envs - caps} float(s) without a caption")
    if k == "build":
        b = load_json(root / ".paper" / "build_record.json", {}).get("status")
        return {"ok": ("OK", "compiled"), "tex-unavailable": ("CONFIRM", "no TeX here; compile on Overleaf and confirm"), None: ("CONFIRM", "not built yet; run paper_check.py build")}.get(b, ("FAIL", f"build {b}"))
    if k == "anon":
        main = gather(root, ["paper/main.tex"])
        ready = bool(re.search(r"\\camerareadytrue", main))
        anon = meta.get("anonymous", True)
        if anon and not ready:
            return "OK", "anonymous mode and review build"
        if not anon and ready:
            return "OK", "camera-ready build with identity shown"
        return "FAIL", "project_meta.json anonymous and the \\camerareadytrue switch disagree"
    if k == "abstract_words":
        p = root / "paper" / "sections" / "abstract.tex"
        if not p.is_file():
            return "FAIL", "abstract.tex missing"
        t = strip_comments(p.read_text(encoding="utf-8"))
        if "[INSERT" in t:
            return "FAIL", "abstract still has placeholders"
        n = words(t)
        return ("OK", f"{n} words") if n <= a["max"] else ("FAIL", f"{n} words exceeds {a['max']}")
    if k == "meta":
        return ("OK", "recorded in project_meta.json") if dotted(meta, a["path"]) else ("FAIL", f"{a['path']} is empty in project_meta.json")
    if k == "no_marker":
        m = re.search(rf"\\begin\{{{a['pattern']}\}}(.*?)\\end\{{{a['pattern']}\}}", gather(root, [a["path"]]), re.S)
        if not m:
            return "FAIL", f"{a['pattern']} block not found"
        return ("FAIL", "still a placeholder") if "[INSERT" in m.group(1) or not m.group(1).strip() else ("OK", "filled")
    return "CONFIRM", f"unknown check kind {k}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project", nargs="?")
    ap.add_argument("--venue")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--quiet", action="store_true", help="print only the summary line")
    args = ap.parse_args()
    data = load_json(VENUES)
    if args.list or not args.project:
        for vid, e in data["venues"].items():
            print(f"{vid:8} {e['name']}  | pages: {e['pages'].get('content')} | aliases: {', '.join(e.get('aliases', [])) or '-'}")
        return 0
    root = Path(args.project).resolve()
    meta = load_json(root / "project_meta.json", {})
    state = load_json(root / "paper_state.json", {})
    vname = args.venue or state.get("target_venue") or meta.get("venue_family") or "generic"
    vid, v = resolve(data, vname)
    items = data["universal"] + [i for i in v["items"] if i["id"] not in {u["id"] for u in data["universal"]}]
    rows = [(i, *run_item(root, meta, i)) for i in items]
    counts = {s: sum(1 for r in rows if r[1] == s) for s in ("OK", "FAIL", "CONFIRM", "N/A")}
    blocking_fail = [r for r in rows if r[1] == "FAIL" and r[0].get("blocking")]
    if not args.quiet:
        print(f"Venue: {v['name']}  (kit: {v['version']})")
        print(f"Pages: {v['pages']}")
        print(f"Required: {', '.join(v['required_sections'])}")
        for k, url in v.get("official", {}).items():
            print(f"  {k}: {url}")
        print()
        for i, st, detail in rows:
            print(f"{st:8} {'*' if i.get('blocking') else ' '} {i['text'][:92]}" + (f"\n{'':11}{detail}" if st in ("FAIL", "CONFIRM") else ""))
        print("\n(* = blocking)")
    md = [f"# Submission checklist: {v['name']}", "", f"_Kit: {v['version']}. Pages: {v['pages']}. Automatic checks are evidence, not proof; confirm against the current call._", "",
          f"Required: {', '.join(v['required_sections'])}", ""]
    for i, st, detail in rows:
        box = "x" if st == "OK" else " "
        tag = {"OK": "verified", "FAIL": "NOT MET", "CONFIRM": "author to confirm", "N/A": "not applicable"}[st]
        md.append(f"- [{box}] **{tag}**{' (blocking)' if i.get('blocking') else ''}: {i['text']}" + (f" _({detail})_" if detail else ""))
    (root / "submission_checklist.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"SUMMARY venue={vid} ok={counts['OK']} fail={counts['FAIL']} blocking_fail={len(blocking_fail)} confirm={counts['CONFIRM']} na={counts['N/A']}")
    return 1 if blocking_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
