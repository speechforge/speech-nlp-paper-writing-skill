# Paper Writing Skill: agent entry point

This folder is **Speech & NLP Paper Writing Skill** (skill id `speech-nlp-paper-writing`; lab standards, extended). Any agent that reads `AGENTS.md` (Codex, Cursor, Copilot, Gemini CLI via `GEMINI.md`, and others) should follow it.

**Start here:** read `skills/ACTIVE.md` (which author, domain, venue, and craft sources are on; disabled ones must be ignored; absent means all on), then `SKILL.md`. It routes the request to one of six journeys and names the single reference file to load next. Do not load every reference.

## Hard rules (always, in every journey)
1. **Never invent a citation or a number.** Fetch and double-verify references with `scripts/citations.py` (primary record plus an independent index, then read the abstract against the sentence). Unverified items stay marked `[CITATION NEEDED]` and are reported to the user. Numbers must trace to a results file.
2. **The paper contains no coding terms**: no file names, functions, flags, identifiers, code spans, or shell commands. Describe ideas, data, and measurements in human, specific English. Check with `scripts/prose_lint.py`.
3. **Claims are bounded by evidence.** Keep `claim_evidence_map.md`. Weaken, remove, or mark `Needs experiment`; never write a stronger claim than the evidence.
4. **The novelty runs through every section** (title to conclusion). Name the novelty type and the delta against the closest verified work.
5. **Credit (CRediT) and license statements** are part of every paper (`scripts/credits_license.py`), anonymised in review builds.
6. **The demo website is named after the project**, never a conference, journal, or publisher.
7. **Do not say "done"** until `python3 scripts/paper_check.py PROJECT ready` passes its blocking gates or blockers are reported.
8. **Ask before costly or outward-facing actions**: running experiments (unless `experiments.auto_run` is set), pushing to a remote, publishing a site.

## Quick map
| Need | Where |
|---|---|
| Journeys and workspace | `references/11_workflow_journeys_and_artifacts.md` |
| Workspace from a file or folder | `python3 scripts/paper_init.py init PROJECT --name NAME --venue acl (or ieee) --context PATH` |
| Voice, flow, no coding terms | `references/10_senior_scientist_voice_and_flow.md` |
| Citations | `references/12_citation_integrity.md` |
| ACL / IEEE templates | `references/13_venue_templates_acl_ieee.md` |
| Figures, plots, spectrograms | `references/14_figures_plots_and_visuals.md` |
| Demo website | `references/15_interactive_demo_website.md` |
| Missing evidence | `references/16_experiments_on_demand.md` |
| Progress on localhost | `python3 scripts/dashboard.py PROJECT --open` |
| Switch sources on or off, merge, export | `python3 scripts/skill_profile.py use ieee-lab` (or `clinical`, `ieee-lab+clinical`, `neutral`); `references/24_skill_profiles_and_sources.md` |
| Conference checklist (NeurIPS, ICML, ICLR, ACL, AAAI, COLM, IEEE) | `python3 scripts/venue_check.py PROJECT`; `references/23_conference_checklists_and_requirements.md` |

No script access? Follow the same rules by hand and see `compat/README.md`. All scripts are standard-library Python (figures also need matplotlib and numpy).
