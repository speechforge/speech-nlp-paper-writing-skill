#!/usr/bin/env python3
"""Generate the credit (CRediT) statement, license statement, and acknowledgments from project_meta.json.

    credits_license.py PROJECT          write paper/statements/*.tex, CREDITS.md, demo/site_credits.json
    credits_license.py PROJECT --check  validate only

One source of truth feeds the paper, the demo website, and the README, so they never disagree.
Roles must come from the 14 CRediT roles. Licenses should be SPDX identifiers. Non-commercial or
no-derivative inputs are flagged because models and samples derived from them inherit the restriction.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import CREDIT_ROLES, load_json, save_json  # noqa: E402

KNOWN_LICENSES = {"CC-BY-4.0", "CC-BY-SA-4.0", "CC-BY-NC-4.0", "CC-BY-NC-SA-4.0", "CC-BY-ND-4.0", "CC0-1.0", "MIT", "Apache-2.0",
                  "BSD-3-Clause", "BSD-2-Clause", "GPL-3.0", "AGPL-3.0", "LGPL-3.0", "MPL-2.0", "OpenRAIL-M", "Public Domain", "Proprietary", "Custom"}
LICENSE_NAMES = {"CC-BY-4.0": "the Creative Commons Attribution 4.0 International license (CC BY 4.0)",
                 "CC-BY-SA-4.0": "the Creative Commons Attribution-ShareAlike 4.0 license (CC BY-SA 4.0)",
                 "CC-BY-NC-4.0": "the Creative Commons Attribution-NonCommercial 4.0 license (CC BY-NC 4.0)",
                 "CC-BY-NC-SA-4.0": "the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 license (CC BY-NC-SA 4.0)",
                 "CC-BY-ND-4.0": "the Creative Commons Attribution-NoDerivatives 4.0 license (CC BY-ND 4.0)",
                 "CC0-1.0": "the CC0 1.0 public domain dedication", "MIT": "the MIT License", "Apache-2.0": "the Apache License 2.0",
                 "BSD-3-Clause": "the BSD 3-Clause License", "BSD-2-Clause": "the BSD 2-Clause License", "GPL-3.0": "the GNU GPL v3",
                 "AGPL-3.0": "the GNU AGPL v3", "LGPL-3.0": "the GNU LGPL v3", "MPL-2.0": "the Mozilla Public License 2.0",
                 "OpenRAIL-M": "the OpenRAIL-M license"}
TEX_ESC = {"&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
PLACEHOLDER_NAMES = {"first author", "second author"}


def tex(s: str) -> str:
    return "".join(TEX_ESC.get(c, c) for c in (s or ""))


def lic(name: str) -> str:
    return LICENSE_NAMES.get(name, name or "[INSERT: license]")


def initials(name: str) -> str:
    parts = [p for p in re.split(r"[\s.]+", name) if p]
    return "".join(p[0].upper() + "." for p in parts)


def validate(meta: dict) -> tuple[list[str], list[str]]:
    errors, warns = [], []
    if not meta.get("authors"):
        errors.append("no authors in project_meta.json")
    for a in meta.get("authors", []):
        if a["name"].strip().lower() in PLACEHOLDER_NAMES:
            warns.append(f"placeholder author '{a['name']}' must be replaced")
        if not a.get("roles"):
            errors.append(f"author '{a['name']}' has no CRediT roles")
        for r in a.get("roles", []):
            if r not in CREDIT_ROLES:
                errors.append(f"unknown CRediT role '{r}' for {a['name']} (valid: {', '.join(CREDIT_ROLES)})")
    covered = {r for a in meta.get("authors", []) for r in a.get("roles", [])}
    for must in ("Conceptualization", "Writing - original draft"):
        if must not in covered:
            warns.append(f"no author is credited with '{must}'")
    for k, v in meta.get("licenses", {}).items():
        if v not in KNOWN_LICENSES:
            warns.append(f"license for {k} ('{v}') is not a recognised SPDX-style identifier")
    for t in meta.get("third_party", []):
        if not t.get("license") or not t.get("url"):
            warns.append(f"third-party asset '{t.get('name', '?')}' needs a license and url")
    if meta.get("human_subjects", {}).get("involved") and not (meta["human_subjects"].get("approval") and meta["human_subjects"].get("consent")):
        errors.append("human_subjects.involved is true but approval or consent is missing")
    return errors, warns


def restrictions(meta: dict) -> list[str]:
    notes = []
    nc = [t["name"] for t in meta.get("third_party", []) if re.search(r"\bNC\b|non-?commercial", t.get("license", ""), re.I)]
    nd = [t["name"] for t in meta.get("third_party", []) if re.search(r"\bND\b|no-?deriv", t.get("license", ""), re.I)]
    gpl = [t["name"] for t in meta.get("third_party", []) if re.search(r"GPL", t.get("license", ""))]
    if nc:
        notes.append(f"{', '.join(nc)} {'is' if len(nc) == 1 else 'are'} licensed for non-commercial use only, so models trained on {'it' if len(nc) == 1 else 'them'} and samples derived from {'it' if len(nc) == 1 else 'them'} carry the same restriction")
    if nd:
        notes.append(f"{', '.join(nd)} cannot be redistributed in modified form, so derived material is not released")
    if gpl:
        notes.append(f"{', '.join(gpl)} {'is' if len(gpl) == 1 else 'are'} copyleft; code that incorporates {'it' if len(gpl) == 1 else 'them'} must be released under compatible terms")
    return notes


def credit_tex(meta: dict) -> str:
    lines = ["% Generated by scripts/credits_license.py from project_meta.json. Edit the metadata, not this file."]
    if any(a["name"].strip().lower() in PLACEHOLDER_NAMES for a in meta["authors"]):
        lines.append("[INSERT: replace the placeholder authors in the project metadata]")
    lines.append("Author contributions follow the CRediT taxonomy.")
    for a in meta["authors"]:
        lines.append(f"{tex(initials(a['name']))}: {tex(', '.join(r.replace(' - ', ' -- ') for r in a['roles']))}.")
    eq = [initials(a["name"]) for a in meta["authors"] if a.get("equal_contribution")]
    if eq:
        lines.append(f"{tex(' and '.join(eq))} contributed equally.")
    co = [a for a in meta["authors"] if a.get("corresponding") and a.get("email")]
    if co:
        lines.append(f"Correspondence: {tex(co[0]['name'])} ({tex(co[0]['email'])}).")
    return "\n".join(lines) + "\n"


def license_tex(meta: dict) -> str:
    L, anon = meta.get("licenses", {}), meta.get("anonymous", True)
    parts = ["% Generated by scripts/credits_license.py from project_meta.json. Edit the metadata, not this file."]
    parts.append(f"The text and figures of this paper are released under {tex(lic(L.get('paper', '')))}.")
    repo = meta.get("repository_url", "")
    if L.get("code"):
        where = ("an anonymised repository supplied with the submission" if anon else (f"\\url{{{repo}}}" if repo else "[INSERT: repository URL]"))
        parts.append(f"The code is released under {tex(lic(L['code']))} at {where}.")
    if L.get("data"):
        parts.append(f"Data created for this work is released under {tex(lic(L['data']))}.")
    if L.get("models"):
        parts.append(f"Model weights are released under {tex(lic(L['models']))}.")
    if L.get("demo_media"):
        site = "" if anon or not meta.get("demo_url") else f" at \\url{{{meta['demo_url']}}}"
        consent = " Speakers and participants consented to public release of their recordings." if meta.get("human_subjects", {}).get("involved") else ""
        parts.append(f"Audio, image, and video samples on the project website{site} are released under {tex(lic(L['demo_media']))}.{consent}")
    tp = meta.get("third_party", [])
    if tp:
        items = "; ".join(f"{tex(t['name'])} ({tex(t.get('kind', 'asset'))}, {tex(t.get('license', '?'))})" for t in tp)
        parts.append(f"Third-party assets are used under their own terms: {items}.")
    for n in restrictions(meta):
        parts.append(tex(n[0].upper() + n[1:]) + ".")
    return "\n".join(parts) + "\n"


def ack_tex(meta: dict) -> str:
    lines = ["% Generated by scripts/credits_license.py from project_meta.json. Edit the metadata, not this file."]
    fund = meta.get("funding", [])
    if not fund:
        lines.append("[INSERT: funding statement, or 'This research received no external funding.']")
    for f in fund:
        agency, grant = f.get("agency", ""), f.get("grant", "")
        if re.search(r"meity|electronics and information technology", agency, re.I):
            lines.append("This work is supported by the Ministry of Electronics and Information Technology (MeitY), Government of India" + (f", under Project Grant ID: {tex(grant)}." if grant else "."))
        else:
            lines.append(f"This work was supported by {tex(agency)}" + (f" under grant {tex(grant)}." if grant else "."))
    for t in meta.get("thanks", []):
        lines.append(tex(t))
    ai = meta.get("ai_assistance", {})
    if ai.get("used") and ai.get("statement"):
        lines.append(tex(ai["statement"]))
    return "\n".join(lines) + "\n"


def ai_disclosure_tex(meta: dict) -> str:
    ai = meta.get("ai_assistance", {})
    lines = ["% Generated by scripts/credits_license.py from project_meta.json. Edit the metadata, not this file."]
    if ai.get("used") and ai.get("statement"):
        lines.append(tex(ai["statement"]))
        lines.append("Describe here the precise role of the assistant in ideation, writing, or code, and what the authors verified yourselves.")
    else:
        lines.append("No large language model played a significant role in the ideation, methodology, or writing of this work; none could be regarded as a contributor.")
    return "\n".join(lines) + "\n"


def credits_md(meta: dict) -> str:
    out = [f"# Credits and Licenses: {meta['project_name']}", "", "## Contributions (CRediT)", "", "| Author | Affiliation | Roles |", "|---|---|---|"]
    out += [f"| {a['name']} | {a.get('affiliation', '')} | {', '.join(a['roles'])} |" for a in meta["authors"]]
    out += ["", "## Licenses", ""] + [f"- **{k}**: {v}" for k, v in meta.get("licenses", {}).items()]
    if meta.get("third_party"):
        out += ["", "## Third-party assets", "", "| Asset | Kind | License | Source |", "|---|---|---|---|"]
        out += [f"| {t['name']} | {t.get('kind', '')} | {t.get('license', '')} | {t.get('url', '')} |" for t in meta["third_party"]]
    notes = restrictions(meta)
    if notes:
        out += ["", "## Inherited restrictions", ""] + [f"- {n}." for n in notes]
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    root = Path(args.project).resolve()
    meta = load_json(root / "project_meta.json")
    errors, warns = validate(meta)
    for w in warns:
        print("warning:", w)
    for e in errors:
        print("ERROR:", e)
    for n in restrictions(meta):
        print("note:", n)
    if errors or args.check:
        print("FAIL" if errors else "OK")
        return 1 if errors else 0
    sdir = root / "paper" / "statements"
    sdir.mkdir(parents=True, exist_ok=True)
    (sdir / "credit_statement.tex").write_text(credit_tex(meta), encoding="utf-8")
    (sdir / "license_statement.tex").write_text(license_tex(meta), encoding="utf-8")
    (sdir / "acknowledgments.tex").write_text(ack_tex(meta), encoding="utf-8")
    (sdir / "ai_disclosure.tex").write_text(ai_disclosure_tex(meta), encoding="utf-8")
    (root / "CREDITS.md").write_text(credits_md(meta), encoding="utf-8")
    anon = meta.get("anonymous", True)
    save_json(root / "demo" / "site_credits.json", {
        "authors": [{"name": a["name"], "affiliation": a.get("affiliation", ""), "roles": a["roles"]} for a in meta["authors"]] if not anon or True else [],
        "licenses": meta.get("licenses", {}), "third_party": meta.get("third_party", []), "restrictions": [n + "." for n in restrictions(meta)],
        "repository_url": meta.get("repository_url", ""), "human_subjects_consent": bool(meta.get("human_subjects", {}).get("involved")),
        "funding": meta.get("funding", [])})
    print(f"wrote {sdir}/credit_statement.tex, license_statement.tex, acknowledgments.tex, ai_disclosure.tex, CREDITS.md, demo/site_credits.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
