#!/usr/bin/env python3
"""Package the skill as a lean zip for upload to Claude.ai, ChatGPT (Code Interpreter or knowledge), or sharing.

    package_skill.py [--out dist/paper-writing-skill-lite.zip] [--with-corpus] [--name paper-writing]

The lean zip leaves out the PDF corpus (Authors/, parsed_md/, analysis_cache/, manifest.json, about 76 MB)
that is only needed for the incremental corpus updater. The zip's top folder is the skill name, with SKILL.md
directly inside it, which is the layout skill uploaders expect. Caches and compiled files are never included.
"""
from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
CORPUS = {"Authors", "parsed_md", "analysis_cache", "manifest.json"}
ALWAYS_SKIP = {"__pycache__", ".git", "dist", ".paper", ".DS_Store", "node_modules", ".pytest_cache"}
SKIP_SUFFIX = {".pyc", ".pyo", ".log"}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=None, help="default: dist/<skill id>-lite.zip")
    ap.add_argument("--with-corpus", action="store_true")
    ap.add_argument("--name", default=None, help="top folder inside the zip; defaults to the `name` in SKILL.md (they must match)")
    args = ap.parse_args()
    head = (SKILL / "SKILL.md").read_text(encoding="utf-8").split("---")[1]
    declared = re.search(r"^name:\s*(\S+)", head, re.M)
    args.name = args.name or (declared.group(1) if declared else SKILL.name)
    if declared and declared.group(1) != args.name:
        raise SystemExit(f"error: SKILL.md declares name '{declared.group(1)}' but --name is '{args.name}'")
    out = Path(args.out) if args.out else SKILL / "dist" / f"{args.name}-lite.zip"
    out.parent.mkdir(parents=True, exist_ok=True)
    count = size = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in sorted(SKILL.rglob("*")):
            rel = p.relative_to(SKILL)
            parts = set(rel.parts)
            if not p.is_file() or parts & ALWAYS_SKIP or p.suffix in SKIP_SUFFIX:
                continue
            if not args.with_corpus and rel.parts[0] in CORPUS:
                continue
            z.write(p, f"{args.name}/{rel.as_posix()}")
            count += 1
            size += p.stat().st_size
    print(f"wrote {out}  ({count} files, {size / 1e6:.1f} MB raw, {out.stat().st_size / 1e6:.2f} MB zipped)"
          + ("" if args.with_corpus else "; corpus excluded"))
    if out.stat().st_size > 28e6:
        print("warning: larger than 28 MB; many uploaders cap skills around 30 MB. Omit --with-corpus.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
