# Script Reference

All new scripts use the Python standard library, except the figure scripts, which also need `matplotlib` and `numpy`. They fail explicitly on missing inputs and never fake a result (for example, without TeX the build gate reports `tex-unavailable`). Run `python3 scripts/<name>.py --help` for options. Existing corpus scripts (`pdf_to_md_preserve_style.py`, `analyze_papers.py`, `update_skills_incremental.py`) are unchanged.

| Script | Purpose | Typical use |
|---|---|---|
| `paper_init.py` | Scaffold a workspace (venue wrapper, section bodies, artifacts, statements) or swap the venue wrapper | `paper_init.py init PROJECT --name "Name" --venue acl --context PATH --fetch-template`; `paper_init.py convert PROJECT --to ieee` |
| `context_digest.py` | One compact brief of a notes file or a project folder (layout, notes, result tables, setup values, citation candidates, media, evidence gaps) | `context_digest.py PATH -o context_digest.md` |
| `citations.py` | `search` candidates, `verify` with two sources and build BibTeX, `check` the manuscript against the lock | `citations.py search "title words"`; `citations.py verify PROJECT --style acl`; `citations.py check PROJECT --strict` |
| `fetch_template.py` | Install official style files (acl, ieee, icml, iclr, colm, neurips, aaai), hash-verified; `--from` for local copies; `--vendor` opt-in | `fetch_template.py icml --dest PROJECT/paper`; `neurips --from DIR`; `--list` |
| `prose_lint.py` | Flag coding terms, stock phrases, hollow openers, unbacked superlatives, long sentences | `prose_lint.py PROJECT/paper --fail-on high` |
| `paper_check.py` | `todos`, `assets`, `log`, `thread` (novelty), `claims`, `build`, and the aggregate `ready` gate (writes `.paper/checks.json`) | `paper_check.py PROJECT ready` |
| `make_plots.py` | Deterministic bar, line, Pareto, and heat plots; vector PDF, print PNG (1600 DPI default), web PNG, source record | `make_plots.py bar results.csv --x method --y mos --out paper/figures/fig_mos` |
| `make_diagram.py` | Block diagram from a JSON spec; new components outlined | `make_diagram.py spec.json --out paper/figures/fig_method` |
| `make_audio_figs.py` | Spectrograms on one shared dB scale, optional waveforms | `make_audio_figs.py spec ref.wav ours.wav --labels "Reference,Ours" --out paper/figures/fig_spec` |
| `make_latex_table.py` | CSV to booktabs table, direction arrows, best in bold, mean and std | `make_latex_table.py results.csv --direction mos:up --family ieee -o paper/tables/main.tex` |
| `credits_license.py` | CRediT, license, and acknowledgment statements, `CREDITS.md`, site credits | `credits_license.py PROJECT` |
| `experiments.py` | Gaps, brief (the experiment prompt), approve, quiet run, status, tail, ingest | `experiments.py brief PROJECT --title T --claims 1 --hypothesis H` |
| `build_demo_site.py` | Static project-named demo site; refuses venue names | `build_demo_site.py PROJECT --serve` |
| `dashboard.py` | Localhost progress dashboard (read-only, loopback) | `dashboard.py PROJECT --open` |
| `venue_check.py` | Venue requirements and checklist (NeurIPS 16 items, ICML, ICLR, ACL, AAAI, COLM, IEEE, universal) checked against the project; writes `submission_checklist.md` | `venue_check.py PROJECT`; `--list` |
| `skill_profile.py` | Enable, disable, only, merge, register, unregister, prune, export, provenance for skill sources | `skill_profile.py use ieee-lab`; `merge author_ieee_lab author_clinical`; `export OUTDIR` |
| `package_skill.py` | Lean zip for Claude.ai or ChatGPT upload | `package_skill.py` |
| `_common.py`, `_plot.py`, `_serve.py` | Shared helpers (not run directly) | |

## Conventions
- A project is a folder created by `paper_init.py`; most scripts take `PROJECT` as their first argument.
- Exit code 1 means a blocking problem was found; messages say what to fix.
- Network use: only `citations.py` and `fetch_template.py`. No contact details are sent unless you pass `--mailto`.
- Tests: `python3 -m unittest discover -s tests -v`.
