# Workflow Journeys, Artifacts, and Token Budget

Six journeys cover almost every request. Pick the smallest one that fits, run its steps, and produce its artifacts. Do not load more references than the journey lists.

---

## 1. The six journeys

| Journey | You have | Ask the agent to do | Load first | Durable output |
|---|---|---|---|---|
| **Brainstorm and plan** | A topic, rough idea, or possible method | Clarify the thesis, research gap, contribution boundary, evidence needed, and the next experiment and writing plan | `19_novelty_and_story.md` | `paper_story.md` (thesis, novelty, gap), plan with experiments needed |
| **Repo to full paper** | Ideas, method design, code, notes, experiment logs, partial results, or a venue template | Build `paper_story.md`, `claim_evidence_map.md`, literature positioning, figures, tables, BibTeX, LaTeX draft, build checks, demo site | this file, then `19`, `12`, `13`, `14` | full workspace (see §3) |
| **Draft review** | A complete or partial draft | Act as a skeptical reviewer: reviewer-style comments, rejection risks, major issues turned into concrete edits | `20_reviewer_mode_and_revision.md`, `05_adversarial_review_checklist.md` | `reviewer_analysis.md`, edit plan |
| **Targeted revision** | A draft plus known weaknesses, reviewer feedback, or a section to improve | Revise the section or whole paper, preserving claim-evidence boundaries and adding no stronger claim | `20`, `10`, the section's blueprint in `04` | revised section files, updated claim map |
| **Figures and tables** | Results, logs, CSVs, method notes, or a rough figure idea | Figure and table plans, generated overview or method figures, deterministic result plots and tables, captions, LaTeX wiring | `14_figures_plots_and_visuals.md`, `08` | `figure_plan.md`, files in `paper/figures`, `paper/tables` |
| **Submission readiness** | A near-final package | Run citation, marker, prose, build, venue, reviewer-risk, checklist, and packaging checks | `21_submission_readiness.md`, `12`, `17` | gate report, `submission_readiness.md` |

Whatever the journey, the invariants hold: **claims map to evidence, citations are verified, the prose is human English with no code terms, and unsupported claims are weakened or removed.**

---

## 2. Repo to full paper: the state machine

Do not skip a failed gate. Weaken the claim or record a blocker.

1. **Scaffold and digest (one command each, a few hundred tokens of output).**
   `python3 scripts/paper_init.py init PROJECT --name "Project Name" --venue acl|ieee|... --context PATH`
   Read `context_digest.md` only. Open individual source files only to answer a specific question.
2. **Story first.** Fill `paper_story.md`: thesis, gap, challenge, insight, **novelty type and delta table**, contributions, claims to make or avoid, reader-promise table. Confirm the framing with the user **after** the first draft, flagged at the top, unless a blocking condition applies (§5).
3. **Evidence map.** One row per claim in `claim_evidence_map.md`. Mark gaps `Needs experiment`.
4. **Close evidence gaps** with `16_experiments_on_demand.md` if any claim needs an experiment. Do not draft results prose for numbers you do not have.
5. **Literature position.** Search with `citations.py search`, read the closest works, fill `literature_positioning.md`, then verify (`12_citation_integrity.md`). Related Work is written from this matrix.
6. **First draft pass, evidence-bearing core:** Method, Experimental Setup, Results and Analysis, Limitations. Write a provisional abstract only to bound scope.
7. **Second draft pass, framing:** Related Work, Introduction, Conclusion, then the final Abstract and title last.
8. **Figures and tables** (`14`) wired into the section files, with takeaway captions.
9. **Credits and license** (`17`): `credits_license.py`.
10. **Demo website** (`15`): `build_demo_site.py` from `demo/samples.json`.
11. **Review pass** (`20`): skeptical review, convert high risks into edits, experiments, limitations, or removed claims.
12. **Gates** (`21`): `python3 scripts/paper_check.py PROJECT ready`. A paper is "complete" only when all blocking gates pass or blockers are reported.

Show progress at any time with `python3 scripts/dashboard.py PROJECT` (zero tokens).

---

## 3. Workspace layout (created by `paper_init.py`)

```
PROJECT/
  project_meta.json         name, slug, authors + CRediT roles, licenses, funding, third-party assets, experiment policy
  paper_state.json          journey, stage, venue family, blockers
  context_digest.md         compact brief of the source material
  paper_story.md            thesis, novelty, contributions, reader-promise table
  claim_evidence_map.md     every claim, its evidence, scope limit, status
  literature_positioning.md closest work and lines of work
  citation_requests.json    identifiers + supports[] (written by the agent from searched, not remembered, papers)
  citation_lock.json        generated: verification record
  figure_plan.md            figure and table plan
  reviewer_analysis.md      skeptical review
  submission_readiness.md   final checklist
  paper/
    main.tex                venue wrapper (ACL / IEEE / generic); swap to change venue
    sections/*.tex          venue-independent bodies: abstract, 01..06, limitations, ethics, appendix
    statements/*.tex        generated credit, license, acknowledgments
    figures/  tables/  references.bib
  experiments/              ledger.json, briefs/, results/, logs/
  demo/                     samples.json, assets/, site/ (built), site_credits.json
  plan/                     progress.md, task-packets/
  .paper/                   caches, checks.json, build_record.json, wrappers/ (old main.tex backups)
```

**Why section files:** a targeted revision reads and rewrites one small file instead of a 10-page document, which saves tokens and prevents accidental edits elsewhere. It also makes venue conversion a wrapper swap.

---

## 4. Artifact rules

- Process notes, TODOs, and tool names live in `plan/` and `paper_story.md`, never in manuscript prose.
- Keep source data and the command that regenerated each figure (`*.source.json` is written automatically).
- Do not commit private or copyrighted PDFs. Record inaccessible papers as `metadata-only` or `needs-access`.
- A terminal stage (`submission-ready`) is invalid while markers, unverified citations, open claims, pending experiments, or a stale build remain.

---

## 5. Proactive, but honest: when to ask

**Default: draft first, ask with the draft.** Scientists are busy; give them something concrete. Put the assumptions you made in a short list at the top ("I framed X as the main contribution; I chose results A, B, C; Related Work covers [lines]; these citations remain unverified").

| Confidence | Action |
|---|---|
| High (clear repo, obvious contribution) | Write the full draft, deliver, iterate |
| Medium (some ambiguity) | Draft with flagged uncertainties, continue |
| Low (major unknowns) | Ask one or two targeted questions, then draft |

**Block for input only when:** the target venue or template is unclear and changes page limits or framing; two contradictory framings are equally valid; results look incomplete or inconsistent; running an experiment would incur real cost the user has not authorised; or the user asked for review before continuing.

**Do not block for:** word choice, section order, which results to show (choose, flag), or citation completeness (draft with what is verified, list the gaps).

This reconciles two instructions that look opposed ("never assume the narrative" and "be proactive"): the narrative is **proposed and flagged**, never silently assumed and never held hostage to a question.

---

## 6. Token budget (the skill must stay cheap to run)

1. **Route first, load one reference at a time.** Never load all references.
2. **Read digests, not directories.** `context_digest.md` (about 500 to 6000 tokens) replaces crawling a repository.
3. **Section files.** Edit the one file a change touches.
4. **Quiet tools.** Experiments log to files; read `experiments.py status` lines and the ingested summary, and read raw logs only on failure (`tail -n 20`).
5. **Scripts do the mechanical work** (verification, linting, plots, tables, statements, dashboard) so the model spends tokens on thinking and writing.
6. **Caches:** citation responses are cached in `.paper/cache`; re-verification is free offline (`--offline`).
7. **Do not paste results into chat.** Point to files; quote only the numbers a paragraph needs.
8. **Dashboard over narration.** Instead of describing progress, tell the user to open the dashboard.

---

## 7. Task packet and completion

For multi-file or submission work, keep `plan/task-packets/<task>.md` (scope, venue, inputs, files allowed to edit, required artifacts, validation commands, acceptance criteria) and `plan/progress.md` (stage, inputs consumed, artifacts produced, verification run, remaining scientific risk). Before saying "done": check scope against the packet, run the gates, inspect the output, fix failures or report blockers. No verification means "drafted", not "complete".
