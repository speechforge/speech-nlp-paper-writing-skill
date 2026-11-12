# Skill Sources and Profiles (enable, disable, merge, add, delete)

The skill is built from **sources** you can switch on and off, so it can be exactly one lab style, exactly another, a merge of several, or your own. Everything is driven by one tool:

```bash
python3 scripts/skill_profile.py init        # once: registry, preset profiles, activates `full`
python3 scripts/skill_profile.py list        # every source, ON/off, and the profiles
python3 scripts/skill_profile.py show        # the generated ACTIVE.md the agent reads
```

The tool writes `skills/ACTIVE_PROFILE.json` (machine state) and `skills/ACTIVE.md` (what the agent must load and what it must ignore). **Agents read `skills/ACTIVE.md` first.** If it is absent, every source applies (the original behaviour).

---

## 1. What is a source

| Kind | Sources (ids) | What it contributes |
|---|---|---|
| **core** (always on, not listed) | engine | workflow, integrity (citations, no coding terms), venue data and checklists, figures, demo site, experiments, credits and license, dashboard, novelty, reviewer mode, readiness, rebuttal, and the writing method (`02` to `05`) |
| **base** | `speech_base` | universal speech-AI base skill (causal chains, 7-sentence abstract, 1600 DPI figures) |
| **author** | `author_ieee_lab`, `author_clinical`, `author_flow_tts`, `author_vocoder` | a lab's style and rules, distilled from published papers |
| **domain** | `domain_tts`, `domain_asr`, `domain_dataset`, `domain_nlp`, `domain_eval` | subject-matter metrics, baselines, and section architectures |
| **craft** | `ml_craft` | external ML writing craft (Nanda, Farquhar, Gopen and Swan, Perez, Lipton, Steinhardt) |
| **venue** | `venue_acl`, `venue_ieee`, `venue_neurips`, `venue_icml`, `venue_iclr`, `venue_aaai`, `venue_colm` | the wrapper template for each conference family |

`author_ieee_lab` bundles the lab rules (`references/01`, `06` to `09`) with the author overlay (`skills/authors/ieee_lab_style.md`), so switching it off removes everything attributed to that style. Hard dependencies are enforced: authors require `speech_base`, so disabling the base also switches them off (the tool says so).

Groups for bulk operations: `@authors`, `@domains`, `@venues`, `@craft`.

---

## 2. Everyday recipes

| I want | Command |
|---|---|
| **Only the IEEE-lab style** (all other authors off) | `skill_profile.py use ieee-lab`  or  `skill_profile.py only author_ieee_lab` |
| **Only the clinical/multimodal style** | `skill_profile.py use clinical`  or  `skill_profile.py only author_clinical` |
| **Only the flow-matching TTS style / only the vocoder style** | `use flow-tts` / `use vocoder` |
| **Merge IEEE-lab + clinical** (IEEE-lab wins on conflicts) | `skill_profile.py use ieee-lab+clinical`  or  `skill_profile.py merge author_ieee_lab author_clinical` |
| **Merge three, my order** | `skill_profile.py merge author_clinical author_ieee_lab author_flow_tts --name mix` |
| **No author overlay at all** | `skill_profile.py use neutral` |
| **Strictly one author, no domain skills derived from the others** | `skill_profile.py only author_ieee_lab --kinds author,domain` (then `enable domain_tts` to add back what you want) |
| Turn one thing off or on | `skill_profile.py disable author_flow_tts` / `enable @domains` |
| Only the venues I use | `skill_profile.py only venue_neurips venue_acl --kinds venue` |
| Save my current choice | `skill_profile.py save my-profile`  (later: `use my-profile`) |
| Add my own lab's source | write `skills/authors/my_lab.md` (see §4), then `skill_profile.py register my_lab --kind author --file skills/authors/my_lab.md --requires speech_base` |
| Delete a source and its files | `skill_profile.py unregister my_lab --delete-files --yes` (without `--yes` nothing changes) |
| Check consistency | `skill_profile.py doctor` |

Switching is instant and reversible: nothing is deleted unless you run `prune --apply` or `unregister --delete-files --yes`.

---

## 3. Merging sources

`merge` makes a profile from two or more **author** sources, in precedence order (first listed wins), and writes a **merge sheet** (`skills/merged/<name>.md`):

- Each author file is written as `RULE_<AUTHOR>_NN_NAME:` blocks with `INTERLOCK: ... <-> DEFAULT::RULE_SEC_xx` lines. The sheet groups rules by the default rule or domain they refine.
- **Shared interlock points** are where two sources refine the same target and may disagree (for example the IEEE-lab style's three-part contribution format and the clinical style's hypothesis-driven proposal both refine the contribution rule). The agent applies the higher-precedence source and **tells you when a lower-precedence rule was overridden**.
- **Rules unique to each source** apply as written.
- No source, merged or not, may weaken the integrity floor (no invented citations or numbers, no coding terms, claims bounded by evidence, novelty carried through every section).

The merge is declarative, not a rewrite of the source files: the originals stay intact and `ACTIVE.md` records the order, so you can reorder with another `merge`.

---

## 4. Adding your own (user-based) source

1. **From papers:** put PDFs in `Authors/<new_author>/` and run `python3 scripts/update_skills_incremental.py` (the existing pipeline extracts and analyses them and writes an author skill with an evidence block per paper).
2. **By hand:** copy the structure of an existing author file: a header (`# SKILL_ID: AUTHOR::NAME`, `AUTHOR_NAME`, `SCOPE`, `LAYER_POLICY`), then `RULE_NAME_NN_TITLE:` blocks with indented keys (`STRUCTURE`, `PATTERN`, ...), an `INTERLOCK: RULE <-> DEFAULT::RULE_SEC_03_CONTRIB` line to say what it refines, and a `FEEDBACK_TRIGGER`.
3. `skill_profile.py register ID --kind author --file ... --requires speech_base`. The new source is enabled immediately and can be merged with any other.

---

## 5. Proof-based: where every rule comes from

Author and domain sources are distilled from named papers; each author file carries an evidence block (`PAPER::<slug>` with source file, parsed text, analysis) and rules carry line-level provenance tags (for example `[2505_20756v1::L512]`).

```bash
python3 scripts/skill_profile.py provenance --write      # skills/PROVENANCE.json
```
`PROVENANCE.json` records, for each author source, the papers (file name, SHA-256, domains) and the SHA-256 of the module files, **so the trail survives even after the PDFs are deleted**. Nothing at run time needs the PDFs.

---

## 6. Removing the PDFs and publishing a lean skill

The author PDFs, parsed text, and analysis caches (`Authors/`, `parsed_md/`, `analysis_cache/`, about 76 MB) are provenance, not runtime inputs. Two safe ways to drop them:

| Goal | Command |
|---|---|
| A **publishable copy** with only the enabled sources and no PDFs; your working folder stays intact | `skill_profile.py export ../my-skill-copy` (add `--corpus` to keep the PDFs) |
| Slim the working folder itself | `skill_profile.py prune --corpus` shows what would go; `--apply` deletes (provenance is written first) |
| An upload zip for Claude.ai or ChatGPT | `python3 scripts/package_skill.py` (lean by default) |

`export` copies the enabled sources, removes disabled files, filters `SKILL.md`, `README.md`, and the router so they do not list removed files, writes a consistent registry and `ACTIVE.md`, scopes `PROVENANCE.json` and the corpus manifest to the kept sources, and prints a list of documents that still mention removed sources in prose so you can review them before publishing.

---

## 7. Caveats (honest limits)

- **Domain skills were distilled from all four authors' papers.** A strictly single-author profile should switch domains off too (`only ... --kinds author,domain`), or keep them as shared subject knowledge.
- Reference docs outside a source sometimes cross-refer to files in a disabled source (for example `14` mentions `08`). Such references are ignored; `doctor` counts them.
- `export` filters list items and router entries by file name. Free prose that names a removed author (and the ChatGPT prompts, which list author overlays) is **not rewritten**; the export report names those files for review.
- A source with `requires` cannot stay on without its requirement; the tool switches it off and says so.
- The registry lists sources; core is never removable. Venue wrappers can be removed (`paper_init.py` then tells you the wrapper is missing); `venues.json` data stays.
