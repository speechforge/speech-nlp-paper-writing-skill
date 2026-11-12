# Conference Checklists and Requirements (all supported venues)

Major venues now require checklists; a missing one can mean desk rejection. This file documents the requirements for **NeurIPS, ICML, ICLR, ACL (and ARR), AAAI, COLM, and IEEE conferences (ICASSP, Interspeech, ...)**, and shows how `scripts/venue_check.py` turns them into a checked list for your project. Source: the checklist reference of the *ml-paper-writing* guide (Orchestra Research, MIT; see `NOTICE.md`) plus the official venue pages recorded in `templates/venues.json`. Always read the current call for papers: years and rules change.

```bash
python3 scripts/paper_init.py init PROJECT --name "Project" --venue neurips    # neurips, icml, iclr, acl, ieee, aaai, colm, or an alias
python3 scripts/fetch_template.py neurips --dest PROJECT/paper --from <folder with the official style file>
python3 scripts/venue_check.py PROJECT                  # writes PROJECT/submission_checklist.md
python3 scripts/venue_check.py --list                   # all venues, pages, aliases
python3 scripts/paper_check.py PROJECT ready            # includes the venue gate
```

Item states: **OK** (verified from the project files), **FAIL** (checked and not met; blocking items stop the gate), **CONFIRM** (only the author can confirm; never silently ticked), **N/A** (declared not applicable in `project_meta.json`, for example no human subjects). Automatic checks look for evidence in the text; they are not proof.

---

## 1. Page limits (as supplied; verify against the current call)

| Venue | Main content | References | Appendix | Template in this skill |
|---|---|---|---|---|
| NeurIPS 2025 | 9 pages | unlimited | unlimited (checklist separate) | `templates/neurips` |
| ICML 2026 | 8 (+1 camera-ready) | unlimited | unlimited | `templates/icml` |
| ICLR 2026 | 9 (+1 camera-ready) | unlimited | unlimited | `templates/iclr` |
| ACL | long 8 / short 4 for review, +1 camera-ready (official guide) | unlimited | outside the limit | `templates/acl` |
| AAAI 2026 | 7 (+1 camera-ready) | unlimited | unlimited | `templates/aaai` |
| COLM | 9 (+1 camera-ready) | unlimited | unlimited | `templates/colm` |
| IEEE conferences (ICASSP, Interspeech, ...) | typically 4 (+1 for references) | see call | see call | `templates/ieee` |

The kits pinned here are NeurIPS 2025, ICML 2026, ICLR 2026, AAAI 2026, COLM 2026, ACL (pinned commit), IEEEtran. For another year download that year's kit, review it, and re-pin (`fetch_template.py --trust-new-hash`).

---

## 2. NeurIPS paper checklist (16 items, mandatory)

The checklist appears after the references and supplemental material, outside the page limit; a paper without it faces automatic desk rejection. Authors answer yes, no, or N/A per question, with an optional one or two sentence justification. **Reviewers are instructed not to penalise honest acknowledgment of limitations.**

| # | Item | What to check or include | Automatic evidence |
|---|---|---|---|
| 1 | Claims alignment | abstract and introduction claims match results; contributions, assumptions, limitations stated; contributions specific and falsifiable | claim map has no open row |
| 2 | Limitations | dedicated section: strong assumptions, robustness to violations, scope, factors that influence performance, conditions where it fails | `07_limitations` filled |
| 3 | Theory and proofs | all assumptions stated formally; complete proofs in the main text or appendix; proof sketch in the main text | author confirms |
| 4 | Reproducibility | steps that let others verify results: code release, instructions, model access, checkpoints | release statement plus setup details |
| 5 | Data and code access | instructions for the main results, exact commands, environment specification, data access | licence/availability statement |
| 6 | Experimental details | train/validation/test splits, all hyperparameters, selection method | text mentions splits and hyperparameters |
| 7 | Statistical significance | error bars, intervals, or tests; number of runs; whether standard deviation or standard error; assumptions | text mentions uncertainty |
| 8 | Compute resources | worker types (CPU/GPU), memory, storage, time per run, total project compute | text mentions hardware and hours |
| 9 | Code of Ethics | read and confirm compliance; note deviations with justification | author confirms |
| 10 | Broader impacts | negative applications, fairness, privacy, mitigation | `08_ethics` filled |
| 11 | Safeguards | controlled release and usage guidelines for high-risk models or scraped datasets | author confirms |
| 12 | License respect | creators cited; licence names, URLs, version numbers, terms of service | licence statement |
| 13 | Asset documentation | datasheet or model card for new releases: training data, limitations, consent, licensing | author confirms |
| 14 | Human subjects | task instructions, compensation, time estimates, minimum-wage compliance | applies if `human_subjects.involved` |
| 15 | IRB approvals | approval or equivalent, risks disclosed, anonymised at submission | `human_subjects.approval` recorded |
| 16 | LLM declaration | disclose LLMs used as a core methodology component (writing and editing assistance needs no declaration) | author confirms |

---

## 3. ICML

- **Impact Statement** at the end of the paper, before the references, outside the page limit: positive impacts, negative impacts, mitigation, who may be affected. Our wrapper provides `\section*{Impact Statement}` from `08_ethics`.
- **Reproducibility:** data splits specified; hyperparameters listed; search ranges documented; selection method explained; compute resources specified; code availability stated.
- **Statistical reporting:** error bars on all figures; standard deviation versus standard error specified; number of runs stated; significance tests when comparing methods.
- **Anonymisation:** no author names, no acknowledgments, no grant numbers, prior work cited in the third person, no identifiable repository URLs (scanned automatically in review mode).

## 4. ICLR

- **LLM disclosure policy:** if LLMs played a significant role in research ideation and/or writing to the extent that they could be regarded as a contributor, describe their precise role in a **separate appendix section**. Required when the role is significant (significant ideation, substantial writing, contributor-level). Not required for grammar checking, minor editing, or code completion. Non-disclosure risks desk rejection. Our wrapper adds the appendix section from `statements/ai_disclosure.tex`, which `credits_license.py` generates from `project_meta.json`.
- **Reproducibility statement** (optional, recommended): supporting materials, code, data, model checkpoints.
- **Ethics statement** (optional): up to one page, outside the limit.
- **Reciprocal reviewing:** authors on 3 or more papers serve as reviewers for at least 6; each submission needs at least one author registered to review at least 3.
- Camera-ready uses `\iclrfinalcopy` (our wrapper issues it when `\camerareadytrue`).

## 5. ACL family (ACL, EMNLP, NAACL, EACL, AACL, ARR)

- **Limitations section (mandatory):** strong assumptions, scope limitations, when the method may fail, generalisation concerns; outside the page limit under ARR policy (confirm in the call). Reviewers check that limitations are honest, whether they undermine core claims, and whether negative impacts are addressed.
- **Responsible NLP:** bias considerations addressed; fairness evaluated if applicable; dual-use concerns discussed. The Responsible NLP checklist is answered in the submission system, not in the PDF.
- **Multilingual (if applicable):** language diversity addressed, non-English languages included, translation quality verified.
- **Human evaluation (if applicable):** annotator details, agreement metrics, compensation.
- Ethics review exists for dual-use, privacy, and bias concerns. Follow the current policy on disclosing AI writing assistance.

## 6. AAAI

Strict adherence to the author kit. The style file sets the bibliography style itself; **never add `\bibliographystyle`**. Forbidden: `hyperref`, `geometry`, `fullpage`, `balance`, `authblk`, `float`, `fontenc`, `multicol`; `\newpage`, `\clearpage`, `\pagestyle`, `\baselinestretch`, `\columnsep`, `\tiny`, negative `\vspace`. `venue_check.py` scans for all of these (blocking). Section numbering depth must be 0, 1, or 2. A camera-ready `links` block between the abstract and the body is the place for the project website.

## 7. COLM

Focus on language models; template similar to ICLR. The official sample ends with Author Contributions, Acknowledgments, and Ethics Statement sections, which our wrapper mirrors (contributions and acknowledgments in camera-ready only). Options: `submission` (line numbers), `preprint`, `final`.

## 8. IEEE conferences (ICASSP, Interspeech, SLT, ASRU, EUSIPCO, IJCNN)

Lab conventions apply (`06` to `09`): index terms (4 to 6, alphabetical), `ACKNOWLEDGMENT`, IEEEtran reference format, listening tests with 95% confidence intervals and listener demographics (ITU-T P.800 conventions), vector or at least 1600 DPI figures, MeitY funding sentence. Take the annual kit's preamble when the call provides one.

---

## 9. Universal pre-submission checklist (applied to every venue)

**Paper content:** abstract within the word limit (usually 250 to 300; the lab's IEEE blueprint is 150 to 220) | main content within the page limit | references complete and verified | Limitations section included | all figures and tables captioned | captions self-contained.
**Formatting:** correct template (venue and year) | margins unmodified | font sizes unmodified | double-blind requirements met | page numbers for review, none for camera-ready.
**Technical:** all claims supported by evidence | error bars included | baselines appropriate | hyperparameters documented | compute resources stated.
**Reproducibility:** code will be available (or justification) | data will be available (or justification) | environment documented | commands to reproduce provided (in the release or appendix, never in the narrative).
**Ethics:** broader impacts considered | limitations honestly stated | licences respected | IRB obtained if needed.
**Final checks:** PDF compiles without errors | all figures render | all citations resolve | supplementary material organised | the venue's checklist completed.

`venue_check.py` verifies the machine-checkable subset and lists the rest for the author. Anything it cannot verify stays `CONFIRM`; never tick a `CONFIRM` item without reading the call.

---

## 10. Reviewer scoring references (calibrate your self-review)

NeurIPS six-point scale: 6 strong accept (groundbreaking, flawless), 5 accept (technically solid, high impact), 4 borderline accept (solid, limited evaluation), 3 borderline reject (solid but weaknesses outweigh), 2 reject (technical flaws), 1 strong reject (known results or unaddressed ethics concerns). Venue-specific reviewing and rebuttal guidance: `25_rebuttal_and_author_response.md`.

## 11. Official pages (recorded in `templates/venues.json`)

NeurIPS: paper-checklist guide, reviewer guidelines, style files. ICML: author instructions, style archive. ICLR: author guide, Master Template. ACL: style files, formatting guide, ACL Rolling Review. AAAI: author kit. COLM: template repository. IEEE: conference template hub.
