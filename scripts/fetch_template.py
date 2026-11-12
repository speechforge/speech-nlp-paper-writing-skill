#!/usr/bin/env python3
"""Install official venue style files into a paper folder, hash-verified and never edited.

    fetch_template.py --list
    fetch_template.py FAMILY --dest PROJECT/paper [--from DIR] [--vendor] [--force] [--trust-new-hash]

FAMILY: acl, ieee, icml, iclr, colm, neurips, aaai (see --list).
Sources, tried in this order:
  1. templates/<family>/vendor/   (only if you previously ran --vendor; verified against VENDOR.json)
  2. --from DIR                   a local folder that already holds the official files (for example an unpacked kit);
                                  required for families without a stable official URL (neurips, aaai)
  3. the official archive or repository pinned in templates/template_manifest.json (acl, ieee, icml, iclr, colm)
Every file must match its pinned SHA-256. A mismatch stops the run (upstream changed: review it, then pass
--trust-new-hash or update the manifest). Downloads and local copies are treated as untrusted data: only
whitelisted file names are written, paths cannot escape the destination, and sizes are capped.
--vendor additionally copies the verified files into templates/<family>/vendor/. That is an explicit, opt-in
decision: do it only if the venue's terms allow you to redistribute the files with this skill.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
import urllib.request
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import load_json  # noqa: E402

SKILL = Path(__file__).resolve().parent.parent
MANIFEST = SKILL / "templates" / "template_manifest.json"
MAX_BYTES = 8_000_000


def download(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "paper-writing-skill-template-fetch/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise SystemExit(f"error: {url} is larger than {MAX_BYTES} bytes; refusing")
    return data


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check(data: bytes, expected: str, name: str, trust_new: bool) -> None:
    got = sha(data)
    if got == expected:
        return
    msg = f"hash mismatch for {name}: expected {expected[:16]}..., got {got[:16]}..."
    if trust_new:
        print("warning:", msg, "(accepted because of --trust-new-hash)")
        return
    raise SystemExit("error: " + msg + "\nThe upstream file changed. Review it, then rerun with --trust-new-hash or update templates/template_manifest.json.")


def write_safe(dest: Path, name: str, data: bytes, force: bool) -> None:
    target = (dest / name).resolve()
    if dest.resolve() not in target.parents:
        raise SystemExit(f"error: unsafe path {name}")
    if target.exists() and not force:
        print(f"kept existing {target.name} (use --force to replace)")
        return
    target.write_bytes(data)
    print(f"wrote {target}")


def from_vendor(fam_name: str) -> dict[str, bytes] | None:
    vdir = SKILL / "templates" / fam_name / "vendor"
    rec = vdir / "VENDOR.json"
    if not rec.is_file():
        return None
    hashes = json.loads(rec.read_text(encoding="utf-8"))["files"]
    out = {}
    for name, h in hashes.items():
        f = vdir / name
        if not f.is_file() or sha(f.read_bytes()) != h:
            raise SystemExit(f"error: vendored file {name} is missing or changed; delete templates/{fam_name}/vendor/ and fetch again")
        out[name] = f.read_bytes()
    print(f"using vendored copies in templates/{fam_name}/vendor/ (verified)")
    return out


def from_local(fam: dict, src: Path, trust_new: bool) -> dict[str, bytes]:
    out = {}
    for fname, expected in fam["files"].items():
        hits = [p for p in sorted(src.rglob(Path(fname).name)) if p.is_file() and p.stat().st_size <= MAX_BYTES]
        if not hits:
            raise SystemExit(f"error: {fname} not found under {src}. {fam.get('local_hint', '')}")
        data = hits[0].read_bytes()
        check(data, expected, str(hits[0]), trust_new)
        out[fam.get("install_as", {}).get(fname, fname)] = data
    return out


def from_remote(fam: dict, trust_new: bool) -> dict[str, bytes]:
    out = {}
    if fam["source"] == "github-raw":
        for fname, expected in fam["files"].items():
            data = download(f"https://raw.githubusercontent.com/{fam['repo']}/{fam['commit']}/{fname}")
            check(data, expected, fname, trust_new)
            out[fam.get("install_as", {}).get(fname, fname)] = data
    elif fam["source"] == "zip":
        blob = download(fam["url"])
        check(blob, fam["sha256"], fam["url"], trust_new)
        with zipfile.ZipFile(io.BytesIO(blob)) as z:
            names = set(z.namelist())
            for member, name in fam["extract"].items():
                if member not in names:
                    raise SystemExit(f"error: {member} not found in the archive")
                if z.getinfo(member).file_size > MAX_BYTES:
                    raise SystemExit(f"error: {member} too large")
                out[name] = z.read(member)
    else:
        raise SystemExit(f"error: this family has no downloadable source. {fam.get('local_hint', 'Use --from DIR.')}")
    return out


def main() -> int:
    man = load_json(MANIFEST)
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("family", nargs="?", choices=sorted(man["families"]))
    ap.add_argument("--dest", default="paper")
    ap.add_argument("--from", dest="src", help="local folder holding the official files")
    ap.add_argument("--vendor", action="store_true", help="also copy the verified files into templates/<family>/vendor/ (opt-in redistribution decision)")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--trust-new-hash", action="store_true")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()
    if args.list or not args.family:
        for k, v in man["families"].items():
            where = {"local": "needs --from DIR", "github-raw": "fetched from the official repository", "zip": "fetched from the official archive"}[v["source"]]
            print(f"{k}: {', '.join(v['venues'])}  [{where}]\n    citations: {v['citation_style']}\n    official: {v['official_page']}\n    {v['notes']}")
        print("\nOther venues (fetch manually, then keep the section inputs):")
        for k, v in man["manual"].items():
            print(f"  {k}: base family {v['family']}; {v['where']}")
        return 0
    fam = man["families"][args.family]
    dest = Path(args.dest)
    dest.mkdir(parents=True, exist_ok=True)
    files = from_vendor(args.family)
    if files is None:
        if args.src:
            if "files" not in fam:
                raise SystemExit("error: --from works for families that pin per-file hashes (neurips, aaai, acl, colm). For icml, iclr, ieee omit it to fetch the official archive.")
            files = from_local(fam, Path(args.src), args.trust_new_hash)
        else:
            files = from_remote(fam, args.trust_new_hash)
    for name, data in files.items():
        write_safe(dest, name, data, args.force)
    if args.vendor:
        vdir = SKILL / "templates" / args.family / "vendor"
        vdir.mkdir(parents=True, exist_ok=True)
        for name, data in files.items():
            (vdir / name).write_bytes(data)
        (vdir / "VENDOR.json").write_text(json.dumps({"family": args.family, "files": {n: sha(d) for n, d in files.items()}}, indent=2) + "\n", encoding="utf-8")
        print(f"vendored {len(files)} file(s) into templates/{args.family}/vendor/. Confirm the venue's terms allow redistribution before publishing this skill.")
    print(f"\n{args.family} style files ready in {dest}. Licence note: {fam.get('license', 'see the official page; files are used unmodified')}")
    print("Never edit the style files; adjust the wrapper (main.tex) instead. " + fam["notes"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
