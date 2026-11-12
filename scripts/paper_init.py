#!/usr/bin/env python3
"""Create a manuscript workspace from a context file or folder, or convert it between venues.

    paper_init.py init PROJECT --name "Project Name" [--title "Paper title"] [--venue acl|ieee|icassp|interspeech|neurips|...]
                  [--context PATH] [--fetch-template]
    paper_init.py convert PROJECT --to acl|ieee|generic

`init` lays out the workspace, copies the venue wrapper and the venue-independent section bodies,
writes project_meta.json, paper_state.json and the working artifacts, digests the context (if given),
and generates the credit and license statements. `convert` swaps only paper/main.tex, so the prose
never changes when the target venue does.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import load_json, now_iso, save_json, slugify, venue_words  # noqa: E402

SKILL = Path(__file__).resolve().parent.parent
TPL = SKILL / "templates"
def _families() -> dict[str, str]:
    """Venue id or alias -> wrapper family, from templates/venues.json (single source of truth)."""
    fam = {"other": "generic"}
    for vid, e in load_json(TPL / "venues.json")["venues"].items():
        fam[vid] = e["family"]
        for alias in e.get("aliases", []):
            fam[alias] = e["family"]
    return fam


FAMILY = _families()
DIRS = ["paper/sections", "paper/statements", "paper/figures", "paper/tables", "figures_src", "results", "literature",
        "experiments/briefs", "experiments/results", "experiments/logs", "demo/assets", "plan/task-packets", ".paper"]


def fill(text: str, **kv) -> str:
    for k, v in kv.items():
        text = text.replace(f"@@{k}@@", v)
    return text


def init(args) -> int:
    root = Path(args.project).resolve()
    name = args.name.strip()
    bad = venue_words(name)
    if bad:
        raise SystemExit(f"error: the project name must not contain venue or publisher names ({', '.join(bad)}). Use a name that describes the work.")
    family = FAMILY.get(args.venue.lower())
    if not family:
        raise SystemExit(f"error: unknown venue '{args.venue}'. Known: {', '.join(sorted(FAMILY))}")
    if (root / "project_meta.json").exists() and not args.force:
        raise SystemExit(f"error: {root} already holds a project (use --force to re-scaffold missing files only)")
    for d in DIRS:
        (root / d).mkdir(parents=True, exist_ok=True)
    kv = dict(PROJECT_NAME=name, SLUG=slugify(name), TITLE=args.title or name, FAMILY=family, DATE=now_iso()[:10])
    if not (TPL / family / "main.tex").is_file():
        raise SystemExit(f"error: the wrapper for '{family}' is not installed (templates/{family}/ was removed or disabled). Re-enable it with scripts/skill_profile.py or choose another venue.")
    shutil.copyfile(TPL / family / "main.tex", root / "paper" / "main.tex") if not (root / "paper" / "main.tex").exists() else None
    main_tex = root / "paper" / "main.tex"
    main_tex.write_text(fill(main_tex.read_text(encoding="utf-8"), **kv), encoding="utf-8")
    for f in (TPL / "sections").glob("*.tex"):
        if not (root / "paper" / "sections" / f.name).exists():
            shutil.copyfile(f, root / "paper" / "sections" / f.name)
    for f in (TPL / "artifacts").iterdir():
        target = root / ("citation_requests.json" if f.name == "citation_requests.json" else f.name)
        if not target.exists():
            target.write_text(fill(f.read_text(encoding="utf-8"), **kv), encoding="utf-8")
    (root / "paper" / "references.bib").touch()
    state = {"schema": "paper-skill/state-v1", "mode": "full-paper", "stage": "story", "venue_family": family,
             "target_venue": args.venue.lower(), "created": now_iso(), "main_tex": "paper/main.tex", "bibliography": "paper/references.bib",
             "blockers": [], "journey": "repo-to-full-paper"}
    if not (root / "paper_state.json").exists():
        save_json(root / "paper_state.json", state)
    (root / "plan" / "progress.md").write_text(f"# Progress\n\n- Stage: story\n- Inputs consumed: {args.context or 'none yet'}\n- Artifacts produced: workspace scaffold\n- Verification run: none\n- Remaining scientific risk: unknown until the claim map is filled\n", encoding="utf-8")
    (root / "plan" / "task-packets" / "initial.md").write_text("# Task\n- Scope:\n- Target venue and template mode:\n- Inputs and evidence:\n- Files allowed to edit:\n- Required artifacts: paper_story.md, claim_evidence_map.md, references.bib, figures, demo site\n- Validation commands: python3 scripts/paper_check.py . ready\n- Acceptance criteria: all blocking gates pass, or blockers are reported\n", encoding="utf-8")
    here = Path(__file__).resolve().parent
    if args.context:
        subprocess.run([sys.executable, str(here / "context_digest.py"), args.context, "-o", str(root / "context_digest.md")], check=False)
    subprocess.run([sys.executable, str(here / "credits_license.py"), str(root)], check=False)
    if args.fetch_template and family != "generic":
        subprocess.run([sys.executable, str(here / "fetch_template.py"), family, "--dest", str(root / "paper")], check=False)
    print(f"\nWorkspace ready: {root}\n  venue family: {family}  |  project name: {name}  |  slug: {slugify(name)}")
    print("Next: read context_digest.md, then fill paper_story.md (thesis, novelty, claims) before writing prose.")
    if not args.fetch_template and family != "generic":
        print(f"      Official style files: python3 {here / 'fetch_template.py'} {family} --dest {root / 'paper'}" + ("   (add --from <folder with the official files>)" if family in ("neurips", "aaai") else ""))
    print(f"      Venue requirements and checklist: python3 {here / 'venue_check.py'} {root}")
    return 0


def convert(args) -> int:
    root = Path(args.project).resolve()
    target = args.to.lower()
    family = FAMILY.get(target)
    if not family or not (root / "paper" / "main.tex").exists():
        raise SystemExit(f"error: need an initialised project and a known target ({', '.join(sorted(set(FAMILY.values())))}, or a venue name)")
    meta = load_json(root / "project_meta.json")
    cur = meta.get("venue_family")
    if cur == family:
        print(f"already using the {family} wrapper; nothing to do")
        return 0
    main_tex = root / "paper" / "main.tex"
    backup = root / ".paper" / "wrappers" / f"main.{cur or 'old'}.tex"   # outside paper/, so checks never see it
    backup.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(main_tex, backup)
    kv = dict(PROJECT_NAME=meta["project_name"], SLUG=meta["slug"], TITLE=meta.get("title", meta["project_name"]), FAMILY=family, DATE=meta.get("created", "")[:10])
    new = fill((TPL / family / "main.tex").read_text(encoding="utf-8"), **kv)
    old = backup.read_text(encoding="utf-8")
    import re
    m = re.search(r"\\title\{(.*?)\}\s*\n", old, re.S)
    if m:
        new = re.sub(r"\\title\{.*?\}\s*\n", lambda _: "\\title{" + m.group(1) + "}\n", new, count=1, flags=re.S)
    main_tex.write_text(new, encoding="utf-8")
    meta["venue_family"] = family
    save_json(root / "project_meta.json", meta)
    state = load_json(root / "paper_state.json", {})
    state.update(venue_family=family, target_venue=target.lower())
    save_json(root / "paper_state.json", state)
    print(f"swapped wrapper {cur} -> {family}; previous wrapper kept at {backup.relative_to(root)}")
    print("Now: (1) fetch the official style files, (2) re-enter author blocks in main.tex, (3) re-check page budget and the venue's required sections.")
    print("Citations: bodies use \\citet/\\citep, so no text edit is needed. Re-run `citations.py verify --style " + ("acl" if family == "acl" else "ieee") + "` if you want the new author-list convention.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("init")
    i.add_argument("project")
    i.add_argument("--name", required=True)
    i.add_argument("--title")
    i.add_argument("--venue", default="acl")
    i.add_argument("--context")
    i.add_argument("--fetch-template", action="store_true")
    i.add_argument("--force", action="store_true")
    c = sub.add_parser("convert")
    c.add_argument("project")
    c.add_argument("--to", required=True)
    args = ap.parse_args()
    return init(args) if args.cmd == "init" else convert(args)


if __name__ == "__main__":
    raise SystemExit(main())
