# Changelog

## Enhancement (2026-11-12)

All existing content (SKILL.md, README.md, references 01 to 09, skills/, chatgpt/, scripts/, Authors/, parsed_md/, analysis_cache/) is preserved. Changes are additions, plus one extended line (the SKILL.md front-matter description now begins with the original text and adds the new triggers).

### Added
- `references/10` to `22`: voice and flow with the no-coding-terms rule; journeys, artifacts, and token budget; citation integrity; ACL and IEEE templates; figures and visuals; interactive demo website; experiments on demand; credits and license; dashboard; novelty and story; reviewer mode and revision; submission readiness; craft from ML paper-writing guides.
- `scripts/`: `paper_init.py`, `context_digest.py`, `citations.py`, `fetch_template.py`, `prose_lint.py`, `paper_check.py`, `make_plots.py`, `make_diagram.py`, `make_audio_figs.py`, `make_latex_table.py`, `credits_license.py`, `experiments.py`, `build_demo_site.py`, `dashboard.py`, `package_skill.py`, plus shared `_common.py`, `_plot.py`, `_serve.py`.
- `templates/`: ACL, IEEE, and generic wrappers; shared venue-independent section bodies; artifact templates; demo site; dashboard; template manifest with pinned hashes.
- `compat/`, `AGENTS.md`, `GEMINI.md`, `.cursor/rules/`, `.github/copilot-instructions.md`, `agents/openai.yaml` for cross-platform use.
- `SKILL.md`: persona, journeys, integrity gates, tools, venue templates, experiments, multimedia, credits, token budget, platform notes, rules 6 to 13, file-based output contract.
- `README.md`: enhancement overview, journeys, why-this-skill tables, quick start, platform compatibility, attribution; repository tree extended.
- `skills/SKILL_ROUTER.md`: journey routing and integrity-floor composition rules.
- `chatgpt/`: integrity, human-English, journey, venue, credit/license, multimedia, and tooling additions.
- `NOTICE.md`, `tests/`.

### Verified during the enhancement
Live citation verification (ACL Anthology, arXiv, Crossref/DataCite, OpenAlex, Semantic Scholar); template fetching with SHA-256 pins and tamper refusal; plots, diagram, spectrogram, and table output inspected visually; demo site and dashboard rendered in headless Chrome in dark, light, and mobile layouts; dashboard security guards; experiment loop including refusal paths and failure handling. No LaTeX installation was available, so PDF compilation was not exercised here.

## Enhancement, second pass (2026-11-12)

### Added
- **All conferences:** wrappers for NeurIPS, ICML, ICLR, AAAI, COLM (`templates/<venue>/main.tex`) over the same section bodies; `templates/venues.json` (pages, required sections, official pages, universal and per-venue checklist items with automatic checks); `scripts/venue_check.py` (writes `submission_checklist.md`, part of the readiness gate); `scripts/fetch_template.py` extended to icml, iclr, colm (official, pinned), neurips, aaai (local import with SHA-256, `--from`) and an opt-in `--vendor`; `paper_init.py` venues and aliases from `venues.json`; `statements/ai_disclosure.tex`.
- `references/23_conference_checklists_and_requirements.md` (the supplied checklist set), `references/25_rebuttal_and_author_response.md` (venue reviewing, response template), additions to `references/22` and `13`, from the new `claude-code-templates/.../ml-paper-writing` folder.
- **Switchable sources:** `skills/registry.json`, `skills/profiles/` (full, ieee-lab, clinical, flow-tts, vocoder, ieee-lab+clinical, neutral), `skills/ACTIVE_PROFILE.json`, generated `skills/ACTIVE.md`, merge sheets in `skills/merged/`, `scripts/skill_profile.py` (use, enable, disable, only, merge, save, register, unregister, provenance, prune, export, doctor), `references/24_skill_profiles_and_sources.md`; SKILL.md, router, README, AGENTS.md, and the universal prompt now point agents to `ACTIVE.md`.

### Verified
Official ICML and ICLR archives were confirmed byte-identical to the supplied copies; COLM's repository now holds the 2026 template and is pinned at a commit. All seven wrapper families were initialised and checked statically (inputs resolve, placeholders replaced, braces balanced, AAAI forbidden-package scan). The venue checklist fails an empty skeleton and passes items once the text provides the evidence. Profile switching, merge sheet, dependency cascade, export, prune dry run and apply, provenance, and register/unregister (including a bug where deletion confirmation was checked after the change) were exercised on a scratch copy. No LaTeX installation was available, so wrappers were not compiled.
