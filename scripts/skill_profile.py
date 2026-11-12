#!/usr/bin/env python3
"""Choose which skill SOURCES apply: enable, disable, merge, add, delete, export, and prove where rules came from.

A source (module) is an author overlay (IEEE-lab, clinical, flow-matching TTS, vocoder benchmarking), a domain skill, a venue
pack, the speech base, or an external craft source. The engine (workflow, integrity, tools) is core and always on.
The active selection is written to skills/ACTIVE_PROFILE.json and skills/ACTIVE.md; agents read ACTIVE.md first and
must ignore disabled sources.

    skill_profile.py init                          create registry-based presets (idempotent) and activate `full`
    skill_profile.py list | show | doctor
    skill_profile.py use PROFILE                   activate a saved profile (full, ieee-lab, clinical, ieee-lab+clinical, neutral, ...)
    skill_profile.py enable  ID|@group ...         @authors @domains @venues @craft are groups
    skill_profile.py disable ID|@group ...
    skill_profile.py only ID ... [--kinds author,domain,venue,craft|all]   keep ONLY these within the given kinds (default: author)
    skill_profile.py merge ID ID ... [--name N]    merge author sources; first listed has precedence; writes a merge sheet
    skill_profile.py save NAME                     save the current selection as a profile
    skill_profile.py register ID --kind author --file skills/authors/x.md [--title T] [--requires a,b]
    skill_profile.py unregister ID [--delete-files --yes]
    skill_profile.py provenance [--write]          papers behind each author source (hashes), kept after PDFs are removed
    skill_profile.py prune [--corpus] [--apply]    delete files of disabled sources (dry run unless --apply)
    skill_profile.py export OUTDIR [--corpus]      standalone copy with only the enabled sources (original untouched)

PDFs and parsed corpora are never needed at run time. Remove them with `prune --corpus --apply` or leave them out of
a published copy with `export` (the default). Provenance is recorded first so the evidence trail survives.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import load_json, now_iso, save_json  # noqa: E402

SKILL = Path(__file__).resolve().parent.parent
SK = SKILL / "skills"
REGISTRY, PROFILES, ACTIVE_JSON, ACTIVE_MD, MERGED = SK / "registry.json", SK / "profiles", SK / "ACTIVE_PROFILE.json", SK / "ACTIVE.md", SK / "merged"
CORPUS = ["Authors", "parsed_md", "analysis_cache"]
GROUPS = {"@authors": "author", "@domains": "domain", "@venues": "venue", "@craft": "craft"}

DEFAULT_MODULES = {
    "speech_base": {"kind": "base", "title": "Universal speech-AI base skill (causal chains, 7-sentence abstract, 1600 DPI)", "files": ["skills/default_speech_ai.md"], "requires": [], "token": "DEFAULT_SPEECH_AI"},
    "author_ieee_lab": {"kind": "author", "title": "IEEE-conference speech-lab standards and style overlay", "requires": ["speech_base"], "token": "AUTHOR::IEEE_LAB_STYLE", "evidence_slug": "ieee_lab_style",
              "files": ["references/01_ieee_lab_rules.md", "references/06_conference_paper_style_guide.md", "references/07_section_by_section_corrections_and_rules.md", "references/08_figure_dpi_and_latex_quality.md", "references/09_repair_manual_mistakes_to_globally_acceptable.md", "skills/authors/ieee_lab_style.md"]},
    "author_clinical": {"kind": "author", "title": "Clinical and accented speech, multimodal perception, ablation-first style", "requires": ["speech_base"], "token": "AUTHOR::CLINICAL_MULTIMODAL_STYLE", "evidence_slug": "clinical_multimodal_style", "files": ["skills/authors/clinical_multimodal_style.md"]},
    "author_flow_tts": {"kind": "author", "title": "Flow-matching TTS, sound tokens, and Pareto-style reporting", "requires": ["speech_base"], "token": "AUTHOR::FLOW_MATCHING_TTS_STYLE", "evidence_slug": "flow_matching_tts_style", "files": ["skills/authors/flow_matching_tts_style.md"]},
    "author_vocoder": {"kind": "author", "title": "Efficient multilingual vocoding and benchmark reporting (related to the IEEE-lab style)", "requires": ["speech_base"], "suggests": ["author_ieee_lab"], "token": "AUTHOR::VOCODER_BENCHMARK_STYLE", "evidence_slug": "vocoder_benchmark_style", "files": ["skills/authors/vocoder_benchmark_style.md"]},
    "domain_tts": {"kind": "domain", "title": "TTS and vocoders", "files": ["skills/domains/tts_and_vocoders.md"], "requires": [], "suggests": ["speech_base"], "token": "DOMAIN::TTS_AND_VOCODERS"},
    "domain_asr": {"kind": "domain", "title": "ASR and error correction", "files": ["skills/domains/asr_and_error_correction.md"], "requires": [], "suggests": ["speech_base"], "token": "DOMAIN::ASR_AND_ERROR_CORRECTION"},
    "domain_dataset": {"kind": "domain", "title": "Datasets and corpora", "files": ["skills/domains/dataset_and_corpus.md"], "requires": [], "suggests": ["speech_base"], "token": "DOMAIN::DATASET_AND_CORPUS"},
    "domain_nlp": {"kind": "domain", "title": "NLP, sound tokens, AAC", "files": ["skills/domains/nlp_and_aac.md"], "requires": [], "suggests": ["speech_base"], "token": "DOMAIN::NLP_AND_AAC"},
    "domain_eval": {"kind": "domain", "title": "Reasoning and evaluation", "files": ["skills/domains/reasoning_and_evaluation.md"], "requires": [], "suggests": ["speech_base"], "token": "DOMAIN::REASONING_AND_EVALUATION"},
    "ml_craft": {"kind": "craft", "title": "ML paper-writing craft (Nanda, Farquhar, Gopen and Swan, Perez, Lipton, Steinhardt)", "files": ["references/22_craft_from_ml_paper_writing.md"], "requires": [], "source": "ml-paper-writing guide (Orchestra Research, MIT)"},
    "venue_acl": {"kind": "venue", "title": "ACL family wrapper", "files": ["templates/acl"], "requires": []},
    "venue_ieee": {"kind": "venue", "title": "IEEE family wrapper", "files": ["templates/ieee"], "requires": []},
    "venue_neurips": {"kind": "venue", "title": "NeurIPS wrapper", "files": ["templates/neurips"], "requires": []},
    "venue_icml": {"kind": "venue", "title": "ICML wrapper", "files": ["templates/icml"], "requires": []},
    "venue_iclr": {"kind": "venue", "title": "ICLR wrapper", "files": ["templates/iclr"], "requires": []},
    "venue_aaai": {"kind": "venue", "title": "AAAI wrapper", "files": ["templates/aaai"], "requires": []},
    "venue_colm": {"kind": "venue", "title": "COLM wrapper", "files": ["templates/colm"], "requires": []},
}


# ------------------------------------------------------------------ registry and state
def registry() -> dict:
    return load_json(REGISTRY)["modules"]


def save_registry(mods: dict) -> None:
    save_json(REGISTRY, {"schema": "paper-skill/registry-v1", "note": "Core (engine, integrity, workflow, tools, writing method, venue data) is always on and not listed. Edit with skill_profile.py register/unregister.", "modules": mods})


def expand(ids: list[str], mods: dict) -> list[str]:
    out = []
    for i in ids:
        if i in GROUPS:
            out += [m for m, e in mods.items() if e["kind"] == GROUPS[i]]
        elif i in mods:
            out.append(i)
        else:
            raise SystemExit(f"error: unknown source '{i}'. Known: {', '.join(mods)} and groups {', '.join(GROUPS)}")
    return list(dict.fromkeys(out))


def close_requires(enabled: list[str], mods: dict) -> list[str]:
    seen, stack = [], list(enabled)
    while stack:
        i = stack.pop(0)
        if i in seen:
            continue
        seen.append(i)
        stack += [r for r in mods[i].get("requires", []) if r in mods]
    return [m for m in mods if m in seen]  # registry order


def state() -> dict:
    return load_json(ACTIVE_JSON, {"profile": "full", "enabled": list(registry()), "precedence": [], "merge_sheet": None})


def profile_files() -> list[str]:
    return sorted(p.stem for p in PROFILES.glob("*.json")) if PROFILES.is_dir() else []


def write_active(st: dict, mods: dict) -> None:
    st["enabled"] = close_requires(st["enabled"], mods)
    st["updated"] = now_iso()
    save_json(ACTIVE_JSON, st)
    en = st["enabled"]
    dis = [m for m in mods if m not in en]
    lines = [f"# Active skill profile: {st['profile']}", "",
             "_Generated by scripts/skill_profile.py. Do not edit; change it with `skill_profile.py use|enable|disable|only|merge`._", "",
             "## Apply these sources, in this load order",
             "1. `skills/SKILL_ROUTER.md` (composition rules; its routing table is limited to the sources below)"]
    n = 2
    for kind, label in (("base", "base"), ("author", "author overlay"), ("domain", "domain"), ("craft", "craft"), ("venue", "venue pack")):
        ids = [m for m in en if mods[m]["kind"] == kind]
        if kind == "author" and st.get("precedence"):
            ids = [m for m in st["precedence"] if m in ids] + [m for m in ids if m not in st["precedence"]]
        for m in ids:
            tag = f" (precedence {st['precedence'].index(m) + 1})" if kind == "author" and m in st.get("precedence", []) else ""
            lines.append(f"{n}. **{m}** ({label}{tag}): {mods[m]['title']}  -> " + ", ".join(f"`{f}`" for f in mods[m]["files"]))
            n += 1
    lines += ["", "## Disabled (do not load, even if SKILL.md, the router, or a reference mentions them)"]
    lines += [f"- **{m}** ({mods[m]['kind']}): {mods[m]['title']}" for m in dis] or ["- none"]
    if st.get("precedence") and len(st["precedence"]) > 1:
        lines += ["", "## Merge policy", f"Precedence: {' > '.join(st['precedence'])}.",
                  f"On a shared interlock point (see `{st.get('merge_sheet') or 'the merge sheet'}`) apply the higher-precedence rule and tell the user when a lower-precedence rule was overridden. Rules that exist in only one source apply as written."]
    lines += ["", "## Always on (core)", "Workflow and artifacts (`references/11`), human English and no coding terms (`10`), citation integrity (`12`), venue templates and checklists (`13`, `23`), figures (`14`), demo site (`15`), experiments (`16`), credits and license (`17`), dashboard (`18`), novelty and story (`19`), reviewer mode (`20`), submission readiness (`21`), rebuttal (`25`), and the writing method (`02` to `05`).",
              "No source, merged or not, may weaken the integrity floor: never invent a citation or number; no coding terms in the paper; claims bounded by evidence; novelty carried through every section."]
    ACTIVE_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ------------------------------------------------------------------ merge sheet
SKIP_KEYS = {"INTERLOCK", "FEEDBACK_TRIGGER", "CANONICAL_PROVENANCE", "PROVENANCE", "PATTERN_PROVENANCE"}


def parse_rules(path: Path) -> list[dict]:
    """Rule blocks `RULE_X_NN_NAME:` with their INTERLOCK targets and a one-line summary."""
    blocks, cur = [], None
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"^(RULE_[A-Z0-9_]+):\s*$", line)
        if m:
            cur = {"id": m.group(1), "lines": []}
            blocks.append(cur)
        elif cur is not None:
            if line and not line.startswith((" ", "\t")):
                cur = None
            else:
                cur["lines"].append(line)
    rules = []
    for b in blocks:
        targets, summary = [], ""
        for i, line in enumerate(b["lines"]):
            t = re.match(r"^\s+INTERLOCK:\s*(.+)$", line)
            if t:
                targets += re.findall(r"[A-Z]+::[A-Z0-9_]+", t.group(1))
                continue
            k = re.match(r"^\s{2}([A-Z][A-Z0-9_]*):\s*(.*)$", line)
            if k and k.group(1) not in SKIP_KEYS and not summary:
                val = k.group(2).strip()
                if not val:  # value on the next nested bullet
                    nxt = next((x.strip(" -") for x in b["lines"][i + 1:] if x.strip()), "")
                    val = nxt
                if val:
                    summary = f"{k.group(1).title().replace('_', ' ')}: {val}"[:150]
        rules.append({"id": b["id"], "targets": targets, "summary": summary})
    return rules


def merge_sheet(ids: list[str], mods: dict, name: str) -> Path:
    per = {}
    for i in ids:
        f = next((SKILL / f for f in mods[i]["files"] if f.startswith("skills/authors/")), None)
        per[i] = parse_rules(f) if f and f.is_file() else []
    by_target: dict[str, dict[str, list[dict]]] = {}
    for i, rules in per.items():
        for r in rules:
            for t in r["targets"]:
                by_target.setdefault(t, {}).setdefault(i, []).append(r)
    shared = {t: d for t, d in by_target.items() if len(d) > 1}
    out = [f"# Merge sheet: {name}", "", f"Precedence: {' > '.join(ids)}. Generated {now_iso()} by `skill_profile.py merge`.", "",
           "Rules are grouped by the default rule or domain they refine (the `INTERLOCK` target). Where two sources refine the same target they may disagree: apply the higher-precedence source and tell the user when the other is overridden.", "",
           f"## Shared interlock points ({len(shared)})", ""]
    if shared:
        out += ["| Target | " + " | ".join(ids) + " |", "|---|" + "---|" * len(ids)]
        for t, d in sorted(shared.items()):
            out.append(f"| `{t}` | " + " | ".join("; ".join(f"`{r['id']}`: {r['summary'] or '(see rule)'}" for r in d.get(i, [])) or "-" for i in ids) + " |")
    else:
        out.append("None: the sources refine different targets, so every rule applies as written.")
    out += ["", "## Rules unique to each source", ""]
    for i in ids:
        uniq = [r for r in per[i] if not any(t in shared for t in r["targets"])]
        out.append(f"### {i} ({len(uniq)})")
        out += [f"- `{r['id']}`" + (f": {r['summary']}" if r["summary"] else "") for r in uniq] or ["- none"]
        out.append("")
    MERGED.mkdir(parents=True, exist_ok=True)
    p = MERGED / f"{name}.md"
    p.write_text("\n".join(out) + "\n", encoding="utf-8")
    return p


# ------------------------------------------------------------------ provenance
def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def provenance(mods: dict) -> dict:
    man = load_json(SKILL / "manifest.json", {})
    files = man.get("files", {})
    out = {"generated": now_iso(), "note": "Papers each author source was derived from, with SHA-256. Survives removal of the PDFs.", "sources": {}}
    for mid, e in mods.items():
        slug = e.get("evidence_slug")
        if not slug:
            continue
        papers = [{"pdf": k, "sha256": v["sha256"], "domains": v.get("domains", []), "parsed_md": v.get("parsed_md"), "analysis": v.get("analysis_jsonl")}
                  for k, v in sorted(files.items()) if v.get("author_slug") == slug]
        out["sources"][mid] = {"title": e["title"], "papers": papers,
                               "module_files": {f: sha(SKILL / f) for f in e["files"] if (SKILL / f).is_file()}}
    return out


# ------------------------------------------------------------------ markdown filtering for export
def removal_tokens(removed: list[str], mods: dict) -> set[str]:
    toks = set()
    for m in removed:
        e = mods[m]
        for f in e["files"]:
            toks |= {f, Path(f).name, Path(f).stem}
            if e["kind"] in ("author", "domain"):
                toks.add(Path(f).stem.upper())
        if e.get("token"):
            toks.add(e["token"])
    return {t for t in toks if len(t) > 3}


def filter_list_lines(text: str, toks: set[str]) -> str:
    lines, out, i = text.split("\n"), [], 0
    while i < len(lines):
        ln = lines[i]
        if re.match(r"^\s*[-*]\s", ln) and any(t in ln for t in toks):
            indent = len(ln) - len(ln.lstrip())
            i += 1
            while i < len(lines) and lines[i].strip() and (len(lines[i]) - len(lines[i].lstrip())) > indent:
                i += 1
            continue
        out.append(ln)
        i += 1
    return "\n".join(out)


def filter_router(text: str, toks: set[str]) -> str:
    def prune_list(m):
        items = [x.strip() for x in m.group(2).split(",") if x.strip()]
        keep = [x for x in items if not any(t in x for t in toks)]
        return m.group(1) + "[" + ", ".join(keep) + "]"
    text = re.sub(r"^(\s*[A-Z_]+:\s*)\[(.*?)\]\s*$", prune_list, text, flags=re.M)
    kept = [ln for ln in text.split("\n") if not (re.match(r"^\s*(AUTHOR_OVERLAY|PRIMARY_DOMAIN|SECONDARY_DOMAIN):", ln) and any(t in ln for t in toks))]
    return "\n".join(kept)


def mentions(root: Path, toks: set[str]) -> dict[str, int]:
    hits = {}
    for p in root.rglob("*"):
        rel = p.relative_to(root)
        if p.is_file() and p.suffix in (".md", ".mdc") and rel.parts[0] not in ("scripts", "tests", "parsed_md", "analysis_cache", "Authors") and p.name not in ("PROVENANCE.json",):
            try:
                t = p.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            n = sum(t.count(x) for x in toks if len(x) > 5)
            if n:
                hits[str(p.relative_to(root))] = n
    return hits


# ------------------------------------------------------------------ commands
def cmd_init(a) -> int:
    if not REGISTRY.exists() or a.reset:
        mods = {k: dict(v) for k, v in DEFAULT_MODULES.items()}
        save_registry(mods)
    mods = registry()
    PROFILES.mkdir(exist_ok=True)
    allids = list(mods)
    non_author = [m for m in allids if mods[m]["kind"] != "author"]
    def prof(name, desc, authors, prec=None):
        save_json(PROFILES / f"{name}.json", {"name": name, "description": desc, "enable": non_author + authors, "precedence": prec or authors})
    prof("full", "Everything on (default; the skill as originally delivered plus all additions)", [m for m in allids if mods[m]["kind"] == "author"], ["author_ieee_lab", "author_vocoder", "author_clinical", "author_flow_tts"])
    prof("ieee-lab", "IEEE-lab style only (lab standards + overlay); other author sources off", ["author_ieee_lab"])
    prof("clinical", "Clinical and multimodal style only; other author sources off", ["author_clinical"])
    prof("flow-tts", "Flow-matching TTS style only; other author sources off", ["author_flow_tts"])
    prof("vocoder", "Vocoder-benchmark style only; other author sources off", ["author_vocoder"])
    prof("ieee-lab+clinical", "Merge of the IEEE-lab and clinical styles; the IEEE-lab style has precedence", ["author_ieee_lab", "author_clinical"], ["author_ieee_lab", "author_clinical"])
    save_json(PROFILES / "neutral.json", {"name": "neutral", "description": "No author overlay: engine, base, domains, craft, and venues only", "enable": non_author, "precedence": []})
    if not ACTIVE_JSON.exists() or a.reset:
        write_active({"profile": "full", "enabled": allids, "precedence": ["author_ieee_lab", "author_vocoder", "author_clinical", "author_flow_tts"], "merge_sheet": None}, mods)
    print(f"registry: {len(mods)} sources; profiles: {', '.join(profile_files())}; active: {state()['profile']}")
    return 0


def cmd_list(a) -> int:
    mods, st = registry(), state()
    print(f"Active profile: {st['profile']}\n")
    for m, e in mods.items():
        on = "ON " if m in st["enabled"] else "off"
        missing = [f for f in e["files"] if not (SKILL / f).exists()]
        print(f"[{on}] {m:16} {e['kind']:7} {e['title'][:70]}" + (f"   (files missing: {len(missing)})" if missing else ""))
    print("\nProfiles: " + ", ".join(profile_files()) + "\nGroups: " + ", ".join(GROUPS))
    return 0


def cmd_show(a) -> int:
    print(ACTIVE_MD.read_text(encoding="utf-8") if ACTIVE_MD.exists() else "no active profile; run `skill_profile.py init`")
    return 0


def set_enabled(ids: list[str], on: bool) -> int:
    mods, st = registry(), state()
    ids = expand(ids, mods)
    cur = set(st["enabled"])
    cur = cur | set(ids) if on else cur - set(ids)
    st["enabled"] = [m for m in mods if m in cur]
    if on:
        st["enabled"] = close_requires(st["enabled"], mods)
    else:  # a source that still needs a disabled one stays disabled
        changed = True
        while changed:
            changed = False
            for m in list(st["enabled"]):
                if any(r not in st["enabled"] for r in mods[m].get("requires", []) if r in mods):
                    st["enabled"].remove(m)
                    print(f"note: {m} was switched off too because it requires a disabled source")
                    changed = True
    st["profile"] = "custom"
    st["precedence"] = [m for m in st.get("precedence", []) if m in st["enabled"]]
    write_active(st, mods)
    print(("enabled " if on else "disabled ") + ", ".join(ids) + f"; active sources: {len(st['enabled'])} of {len(mods)}; see skills/ACTIVE.md")
    return 0


def cmd_only(a) -> int:
    mods, st = registry(), state()
    keep = expand(a.ids, mods)
    kinds = {"author"} if not a.kinds else (set(e["kind"] for e in mods.values()) if a.kinds == "all" else set(a.kinds.split(",")))
    new = [m for m in st["enabled"] if mods[m]["kind"] not in kinds] + keep
    st.update(enabled=[m for m in mods if m in set(new)], profile="custom", precedence=keep if all(mods[k]["kind"] == "author" for k in keep) else st.get("precedence", []))
    write_active(st, mods)
    off = [m for m in mods if m not in st["enabled"]]
    print(f"only {', '.join(keep)} within kinds {', '.join(sorted(kinds))}. Off: {', '.join(off) or 'none'}. See skills/ACTIVE.md")
    return 0


def cmd_use(a) -> int:
    mods = registry()
    f = PROFILES / f"{a.profile}.json"
    if not f.exists():
        raise SystemExit(f"error: no profile '{a.profile}'. Available: {', '.join(profile_files())}")
    p = load_json(f)
    sheet = None
    if len(p.get("precedence", [])) > 1 and all(mods[x]["kind"] == "author" for x in p["precedence"]):
        sheet = str(merge_sheet(p["precedence"], mods, a.profile).relative_to(SKILL))
    st = {"profile": p["name"], "enabled": expand(p["enable"], mods), "precedence": p.get("precedence", []), "merge_sheet": sheet}
    write_active(st, mods)
    print(f"activated profile '{p['name']}': {p.get('description', '')}\nsources on: {', '.join(state()['enabled'])}")
    return 0


def cmd_merge(a) -> int:
    mods, st = registry(), state()
    ids = expand(a.ids, mods)
    if len(ids) < 2 or any(mods[i]["kind"] != "author" for i in ids):
        raise SystemExit("error: merge needs two or more AUTHOR sources, for example: merge author_ieee_lab author_clinical")
    name = a.name or "+".join(i.replace("author_", "") for i in ids)
    sheet = merge_sheet(ids, mods, name)
    keep_other = [m for m in st["enabled"] if mods[m]["kind"] != "author"]
    new = {"profile": name, "enabled": keep_other + ids, "precedence": ids, "merge_sheet": str(sheet.relative_to(SKILL))}
    write_active(new, mods)
    save_json(PROFILES / f"{name}.json", {"name": name, "description": f"Merge of {', '.join(ids)}; precedence in that order", "enable": new["enabled"], "precedence": ids})
    print(f"merged {' > '.join(ids)} as profile '{name}'. Merge sheet: {sheet.relative_to(SKILL)}. Active.")
    return 0


def cmd_save(a) -> int:
    st = state()
    save_json(PROFILES / f"{a.name}.json", {"name": a.name, "description": "Saved from the active selection", "enable": st["enabled"], "precedence": st.get("precedence", [])})
    st["profile"] = a.name
    write_active(st, registry())
    print(f"saved profile '{a.name}'")
    return 0


def cmd_register(a) -> int:
    mods = registry()
    if a.id in mods:
        raise SystemExit(f"error: '{a.id}' already registered; unregister it first")
    files = [f.strip() for f in a.file.split(",")]
    for f in files:
        if not (SKILL / f).exists():
            raise SystemExit(f"error: {f} does not exist under the skill folder")
    token = None
    first = SKILL / files[0]
    if first.is_file():
        m = re.search(r"^#\s*SKILL_ID:\s*(\S+)", first.read_text(encoding="utf-8", errors="replace"), re.M)
        token = m.group(1) if m else None
    mods[a.id] = {"kind": a.kind, "title": a.title or a.id, "files": files, "requires": [r for r in (a.requires or "").split(",") if r],
                  **({"token": token} if token else {}), **({"evidence_slug": a.evidence_slug} if a.evidence_slug else {})}
    for r in mods[a.id]["requires"]:
        if r not in mods:
            raise SystemExit(f"error: required source '{r}' is not registered")
    save_registry(mods)
    st = state()
    st["enabled"].append(a.id)
    write_active(st, mods)
    print(f"registered and enabled '{a.id}' ({a.kind}). New author sources can be created from PDFs with scripts/update_skills_incremental.py, then registered here.")
    return 0


def cmd_unregister(a) -> int:
    mods = registry()
    if a.id not in mods:
        raise SystemExit(f"error: unknown source '{a.id}'")
    if a.delete_files and not a.yes:  # validate BEFORE changing anything
        raise SystemExit("error: --delete-files needs --yes (this deletes files); nothing was changed")
    dependants = [m for m, e in mods.items() if a.id in e.get("requires", [])]
    if dependants:
        raise SystemExit(f"error: {', '.join(dependants)} require '{a.id}'; unregister them first")
    files = mods.pop(a.id)["files"]
    save_registry(mods)
    st = state()
    st["enabled"] = [m for m in st["enabled"] if m != a.id]
    st["precedence"] = [m for m in st.get("precedence", []) if m != a.id]
    write_active(st, mods)
    if a.delete_files:
        for f in files:
            p = SKILL / f
            shutil.rmtree(p) if p.is_dir() else p.unlink(missing_ok=True)
        print(f"unregistered '{a.id}' and deleted {len(files)} file(s)/folder(s)")
    else:
        print(f"unregistered '{a.id}' (files kept: {', '.join(files)})")
    return 0


def cmd_provenance(a) -> int:
    prov = provenance(registry())
    for m, d in prov["sources"].items():
        print(f"{m}: {len(d['papers'])} source papers; {len(d['module_files'])} module files hashed")
    if a.write:
        save_json(SK / "PROVENANCE.json", prov)
        print("wrote skills/PROVENANCE.json (keep it when you delete the PDFs)")
    return 0


def disabled_paths(mods, st) -> list[Path]:
    return [SKILL / f for m, e in mods.items() if m not in st["enabled"] for f in e["files"] if (SKILL / f).exists()]


def cmd_prune(a) -> int:
    mods, st = registry(), state()
    targets = disabled_paths(mods, st)
    corpus = [SKILL / c for c in CORPUS if (SKILL / c).exists()] if a.corpus else []
    size = lambda p: sum(f.stat().st_size for f in p.rglob("*") if f.is_file()) if p.is_dir() else p.stat().st_size  # noqa: E731
    print(f"{'WILL DELETE' if a.apply else 'dry run: would delete'}:")
    for p in targets + corpus:
        print(f"  {p.relative_to(SKILL)}  ({size(p) / 1e6:.2f} MB)")
    if not targets and not corpus:
        print("  nothing")
        return 0
    if not a.apply:
        print("\nNothing was deleted. Add --apply to delete. For a clean publishable copy use `export` instead and keep this folder intact.")
        return 0
    if corpus and not (SK / "PROVENANCE.json").exists():
        save_json(SK / "PROVENANCE.json", provenance(mods))
        print("wrote skills/PROVENANCE.json before deleting the corpus")
    for p in targets + corpus:
        shutil.rmtree(p) if p.is_dir() else p.unlink()
    write_active(st, mods)
    print("deleted. SKILL.md and the router may still mention removed files; agents are told to ignore disabled sources in ACTIVE.md. Use `export` for a fully filtered copy.")
    return 0


def cmd_export(a) -> int:
    mods, st = registry(), state()
    out = Path(a.outdir).resolve()
    if out.exists() and any(out.iterdir()):
        raise SystemExit(f"error: {out} exists and is not empty")
    removed = [m for m in mods if m not in st["enabled"]]
    skip_paths = {str(p.relative_to(SKILL)) for p in disabled_paths(mods, st)}
    skip_dirs = {"__pycache__", ".git", "dist", ".paper"} | (set() if a.corpus else set(CORPUS))
    n = 0
    for p in sorted(SKILL.rglob("*")):
        rel = p.relative_to(SKILL)
        if not p.is_file() or set(rel.parts) & skip_dirs or any(str(rel) == s or str(rel).startswith(s + "/") for s in skip_paths) or p.suffix == ".pyc":
            continue
        dst = out / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(p, dst)
        n += 1
    toks = removal_tokens(removed, mods)
    note = f"> **Profile `{st['profile']}`.** This copy contains only these sources: {', '.join(st['enabled'])}. Ignore any mention of removed sources.\n\n"
    if toks:
        for rel, fn in (("SKILL.md", filter_list_lines), ("README.md", filter_list_lines), ("skills/SKILL_ROUTER.md", filter_router)):
            f = out / rel
            if f.exists():
                text = fn(f.read_text(encoding="utf-8"), toks)
                if rel == "README.md":
                    text = note + text
                if rel == "SKILL.md" and text.startswith("---"):
                    head, _, body = text[3:].partition("\n---\n")
                    text = "---" + head + "\n---\n\n" + note + body.lstrip("\n")
                f.write_text(text, encoding="utf-8")
    kept = {m: dict(e) for m, e in mods.items() if m in st["enabled"]}
    save_json(out / "skills" / "registry.json", {"schema": "paper-skill/registry-v1", "modules": kept})
    for prof in (out / "skills" / "profiles").glob("*.json"):
        d = load_json(prof)
        d["enable"] = [m for m in d["enable"] if m in kept]
        d["precedence"] = [m for m in d.get("precedence", []) if m in kept]
        save_json(prof, d)
    new_st = {"profile": st["profile"], "enabled": list(kept), "precedence": [m for m in st.get("precedence", []) if m in kept], "merge_sheet": st.get("merge_sheet")}
    save_json(out / "skills" / "ACTIVE_PROFILE.json", new_st)
    (out / "skills" / "ACTIVE.md").write_text(ACTIVE_MD.read_text(encoding="utf-8"), encoding="utf-8") if ACTIVE_MD.exists() else None
    if (SK / "PROVENANCE.json").exists() or not a.corpus:
        prov = provenance(kept)
        save_json(out / "skills" / "PROVENANCE.json", prov)
        kept_slugs = {e.get("evidence_slug") for e in kept.values()}
        man = out / "manifest.json"
        if man.exists():  # the corpus manifest of removed sources is not part of this copy
            d = load_json(man)
            d["files"] = {k: v for k, v in d.get("files", {}).items() if v.get("author_slug") in kept_slugs}
            d["pdf_count"] = len(d["files"])
            save_json(man, d)
    print(f"exported {n} files to {out}; sources kept: {', '.join(kept)}; removed: {', '.join(removed) or 'none'}")
    res = mentions(out, {t for t in toks if len(t) > 6})
    if res:
        print("files that still mention removed sources in prose (review before publishing):")
        for k, v in sorted(res.items(), key=lambda kv: -kv[1])[:8]:
            print(f"  {k}: {v}")
    return 0


def cmd_doctor(a) -> int:
    mods, st = registry(), state()
    errors, warns = [], []
    for m, e in mods.items():
        miss = [f for f in e["files"] if not (SKILL / f).exists()]
        if miss and m in st["enabled"]:
            errors.append(f"enabled source '{m}' has missing files: {', '.join(miss)}")
        for r in e.get("requires", []):
            if r not in mods:
                errors.append(f"'{m}' requires unknown source '{r}'")
            elif m in st["enabled"] and r not in st["enabled"]:
                errors.append(f"'{m}' is enabled but its required source '{r}' is not")
        for s in e.get("suggests", []):
            if m in st["enabled"] and s in mods and s not in st["enabled"]:
                warns.append(f"'{m}' works best with '{s}' (suggested, currently off)")
    for m in st["enabled"]:
        if m not in mods:
            errors.append(f"active profile lists unknown source '{m}'")
    present = {str(p.relative_to(SKILL)) for p in (SKILL / "references").glob("*.md")} if (SKILL / "references").is_dir() else set()
    dangling = 0
    for p in list((SKILL / "references").glob("*.md")) + [SKILL / "SKILL.md"]:
        if p.exists():
            for ref in set(re.findall(r"references/(\d\d_[A-Za-z0-9_]+\.md)", p.read_text(encoding="utf-8"))):
                if f"references/{ref}" not in present:
                    dangling += 1
    if dangling:
        warns.append(f"{dangling} cross-reference(s) point to removed reference files; they are ignored (see ACTIVE.md)")
    head = (SKILL / "SKILL.md").read_text(encoding="utf-8").split("---")[1] if (SKILL / "SKILL.md").exists() else ""
    nm = re.search(r"^name:\s*(\S+)\s*$", head, re.M)
    ds = re.search(r"^description:\s*(.+)$", head, re.M)
    if not nm or not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", nm.group(1)) or len(nm.group(1)) > 64:
        errors.append("SKILL.md front matter: `name` must be 1-64 chars, lowercase letters, digits, and hyphens (Agent Skills spec)")
    if not ds or not 1 <= len(ds.group(1)) <= 1024:
        errors.append(f"SKILL.md front matter: `description` must be 1-1024 characters (found {len(ds.group(1)) if ds else 0}); Codex can skip a skill that exceeds it")
    for w in warns:
        print("warning:", w)
    for e in errors:
        print("ERROR:", e)
    print("OK" if not errors else f"FAIL ({len(errors)})")
    return 1 if errors else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("init")
    i.add_argument("--reset", action="store_true", help="recreate the registry and presets from the built-in defaults")
    for n in ("list", "show", "doctor"):
        sub.add_parser(n)
    u = sub.add_parser("use")
    u.add_argument("profile")
    for n in ("enable", "disable"):
        sub.add_parser(n).add_argument("ids", nargs="+")
    o = sub.add_parser("only")
    o.add_argument("ids", nargs="+")
    o.add_argument("--kinds", help="comma list of kinds to restrict (author, domain, venue, craft) or all; default author")
    m = sub.add_parser("merge")
    m.add_argument("ids", nargs="+")
    m.add_argument("--name")
    sub.add_parser("save").add_argument("name")
    r = sub.add_parser("register")
    r.add_argument("id"), r.add_argument("--kind", required=True, choices=["author", "domain", "venue", "craft", "base"])
    r.add_argument("--file", required=True, help="comma-separated paths relative to the skill folder")
    r.add_argument("--title"), r.add_argument("--requires"), r.add_argument("--evidence-slug")
    ur = sub.add_parser("unregister")
    ur.add_argument("id"), ur.add_argument("--delete-files", action="store_true"), ur.add_argument("--yes", action="store_true")
    pv = sub.add_parser("provenance")
    pv.add_argument("--write", action="store_true")
    pr = sub.add_parser("prune")
    pr.add_argument("--corpus", action="store_true"), pr.add_argument("--apply", action="store_true")
    ex = sub.add_parser("export")
    ex.add_argument("outdir"), ex.add_argument("--corpus", action="store_true")
    a = ap.parse_args()
    if a.cmd != "init" and not REGISTRY.exists():
        raise SystemExit("error: no registry yet; run `skill_profile.py init` first")
    return {"init": cmd_init, "list": cmd_list, "show": cmd_show, "doctor": cmd_doctor, "use": cmd_use,
            "enable": lambda a: set_enabled(a.ids, True), "disable": lambda a: set_enabled(a.ids, False), "only": cmd_only, "merge": cmd_merge, "save": cmd_save,
            "register": cmd_register, "unregister": cmd_unregister, "provenance": cmd_provenance, "prune": cmd_prune, "export": cmd_export}[a.cmd](a)


if __name__ == "__main__":
    raise SystemExit(main())
