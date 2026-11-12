# Venue Templates: ACL and IEEE (plus others)

The skill ships **wrapper skeletons** for the two families this lab uses most, and fetches the **official style files** on demand. Always read the current call for papers: page limits, anonymity, and required sections change every year.

---

## 1. How the pieces fit

```
paper/main.tex          venue wrapper: documentclass, style, title/author block, section headings, bibliography style
paper/sections/*.tex    venue-independent bodies (shared)
paper/statements/*.tex  generated credit, license, acknowledgments
```

| Step | Command |
|---|---|
| Create a workspace in a family | `python3 scripts/paper_init.py init PROJECT --name "Project" --venue acl` (or `emnlp`, `naacl`, `eacl`, `ieee`, `icassp`, `interspeech`, ...) |
| Fetch the official style files (hash-pinned) | `python3 scripts/fetch_template.py acl --dest PROJECT/paper` or `... ieee ...` |
| Switch venue family later | `python3 scripts/paper_init.py convert PROJECT --to ieee` (the previous wrapper moves to `.paper/wrappers/`) |
| List families and manual venues | `python3 scripts/fetch_template.py --list` |

Style files are never edited and never redistributed by this skill. `templates/template_manifest.json` pins the ACL commit and file hashes and the IEEEtran archive hash; a changed upstream stops the fetch until reviewed.

---

## 2. ACL family (ACL, EMNLP, NAACL, EACL, AACL, ARR submissions)

- **Class and style:** `\documentclass[11pt]{article}` with `\usepackage[review]{acl}`. Modes: `review` (anonymous, line numbers), `final` (camera-ready), `preprint` (public, non-anonymous).
- **Citations:** natbib author-year. `\citet{key}` for "Author (year)", `\citep{key}` for "(Author, year)". Bibliography style `acl_natbib`.
- **Required or expected sections:** a **Limitations** section (unnumbered, after the conclusion; the ARR policy requires it and exempts it from the page limit, but confirm in the current call), **Ethical Considerations** when relevant, and the **Responsible NLP checklist** (answered in the submission system, not in the PDF). Check the current policy on disclosing AI writing assistance.
- **Length (official formatting guide, pinned commit):** review versions of long papers have up to 8 pages of content and short papers up to 4, with unlimited pages for references; camera-ready gets one more page (9 and 5) with unlimited pages for acknowledgments and references. All figures and tables of the main text must fit inside the content limit. Appendices and supplementary material are encouraged, need not fit, but must follow the same anonymity rules and reviewers need not read them.
- **Anonymity:** no author names, no acknowledgments, no identifying links in review mode. Our wrapper prints contributions, funding, and thanks only when `\camerareadytrue`. Use an anonymised repository link in review.
- **Tables and figures:** captions go **below** both figures and tables, in 10 pt roman; one-line captions centred, longer ones left-aligned. Two columns of 7.7 cm with a 0.6 cm gap (16 cm text width; `--width acl-col|acl-wide` in the plot scripts). Grayscale readability is strongly encouraged: never rely on colour alone (our plots add hatching and markers).
- **Style of presentation:** NLP reviewers expect precise definitions of datasets, annotation, human evaluation, and licences; careful scope for languages and domains; prompts and decoding settings where reproducibility needs them.
- **Fonts:** the template already uses Times and Inconsolata.

## 3. IEEE family (IEEEtran, ICASSP, Interspeech, SLT, ASRU, EUSIPCO, IJCNN, TASLP)

- **Class and style:** `\documentclass[conference]{IEEEtran}`, `\usepackage{cite}`, bibliography style `IEEEtran`. Numeric citations with `\cite{a,b}` rendering `[1], [2]`. Our section bodies use `\citet/\citep`; the wrapper maps both to `\cite`.
- **Annual kits:** ICASSP and Interspeech publish a new author kit every year (often `spconf.sty` with `IEEEbib.bst`, or the ISCA class). Take that preamble from the kit and keep the section inputs.
- **Length:** ICASSP-style papers are typically 4 pages of content plus a fifth page for references only; Interspeech is typically 4 pages plus references. Verify in the call.
- **Sections:** Roman-numeral headings, `ACKNOWLEDGMENT` (singular, uppercase) for the thanks section, index terms after the abstract. No separate mandatory Limitations section, so the wrapper places it as a subsection of the conclusion; keep it.
- **Tables and figures:** table captions **above** and set in small caps by the class; figures at `[t]`; zero vertical table rules; metric directions with $\uparrow/\downarrow$ in headers. Full rules: `06`, `07` (Rules G to I), `08` (>=1600 DPI raster or vector PDF, embedded fonts, PDF eXpress compliance).
- **Column width:** 3.5 in, page text width 7.16 in (`--width ieee-col|ieee-wide`).
- **Lab conventions** (`06`, `07`, `09`) apply to this family: Title Case and Roman numerals, 7-sentence abstract with em-dash, ITU-T P.800 listener demographics, 95% confidence intervals, MeitY funding sentence, IEEE reference format.

## 4. What differs between the families (check on conversion)

| Item | ACL family | IEEE family |
|---|---|---|
| Citations | natbib author-year | numeric `[n]` |
| Heading numbers | Arabic | Roman |
| Table caption | below | above |
| Limitations | mandatory unnumbered section | subsection (still required by us) |
| Ethics | section when relevant | short paragraph, in the conclusion when relevant |
| Thanks heading | Acknowledgments | ACKNOWLEDGMENT |
| Anonymity | review mode hides names; hide thanks and contributions | usually single-blind unless the call says otherwise; follow the call |
| Appendix | allowed, outside the limit | normally not allowed in the page budget; use supplementary material or the project website |
| Reference style | `acl_natbib`; list all authors | `IEEEtran`; truncate after six authors |

---

## 5. The other bundled venues: NeurIPS, ICML, ICLR, AAAI, COLM

Each has a wrapper in `templates/<venue>/main.tex` over the same section bodies, so the whole workflow (claim map, citations, figures, statements, demo site) is identical. Requirements and checklists are in `23_conference_checklists_and_requirements.md`; `venue_check.py` verifies what can be verified.

| Venue | Wrapper highlights | Style files | Official page |
|---|---|---|---|
| NeurIPS | `\usepackage{neurips_2025}` (none = anonymous, `final`, `preprint`); Limitations and Broader Impacts sections; checklist block after the references | local copy via `--from` (installed as `neurips_2025.sty`; hash-pinned) | style-files page |
| ICML | `\usepackage{icml2026}`; `\icmltitle` and author list inside `\twocolumn[...]`; `\printAffiliationsAndNotice{}`; **Impact Statement** | official archive, fetched and verified | author instructions |
| ICLR | `\usepackage{iclr2026_conference,times}`; `\iclrfinalcopy` for camera-ready; **LLM-use appendix** section | official Master Template archive | author guide |
| AAAI | the mandatory "do not change" preamble, `[submission]` option, `\affiliations`, camera-ready `links` block; **no `\bibliographystyle`**; no hyperref or geometry | local copy via `--from` (hash-pinned) | author kit |
| COLM | `\usepackage[submission]{colm2026_conference}`; Ethics Statement, Author Contributions, Acknowledgments as in the official sample | official repository at a pinned commit | template repository |

```bash
python3 scripts/fetch_template.py icml --dest PROJECT/paper                       # official archive
python3 scripts/fetch_template.py colm --dest PROJECT/paper                       # official repository, pinned
python3 scripts/fetch_template.py neurips --dest PROJECT/paper --from <folder>    # local copy, verified by SHA-256
python3 scripts/fetch_template.py aaai --dest PROJECT/paper --from <folder>
```
Years: the pinned kits are NeurIPS 2025, ICML 2026, ICLR 2026, AAAI 2026, COLM 2026. For another year download its kit, read it, then re-pin (`--trust-new-hash`). **These wrappers were checked statically** (inputs resolve, placeholders replaced, braces balanced, forbidden-package scan for AAAI) but not compiled here because no LaTeX installation was available; compile once on Overleaf or locally before relying on one. A venue not listed: use `templates/generic/main.tex` or copy a kit's preamble into `paper/main.tex` and keep the `\input` lines.

Vendoring: none of these style files ships with this skill because their redistribution terms are not stated. If you decide the terms allow it, `fetch_template.py FAMILY --vendor` copies the verified files into `templates/FAMILY/vendor/`, and later runs use them offline.

## 6. Converting between venues (resubmission)

1. `paper_init.py convert PROJECT --to <family>` swaps only the wrapper. Do not copy preambles between templates.
2. Fetch the target's style files; re-enter the author block; check the page budget.
3. **Cutting pages:** move proofs and detailed tables to the appendix or website, cite surveys instead of listing papers, merge experiments into one table, use subfigures, tighten prose. **Expanding:** add reviewer-requested ablations, expand limitations, add baselines or qualitative examples.
4. **Venue-specific additions:** ACL: Limitations, Ethical Considerations, Responsible NLP checklist. IEEE: index terms, ACKNOWLEDGMENT wording, annual kit. NeurIPS: 16-item checklist after the references. ICML: Impact Statement. ICLR: LLM-use appendix. COLM: ethics statement. AAAI: no forbidden packages, no `\\bibliographystyle`. Then run `venue_check.py`.
5. Update self-citations for blind review; replace "under review" references with published versions.
6. When resubmitting after rejection: address the reviewers' concerns in the paper, but do **not** add a "changes from the previous submission" section and do not mention previous reviews in the manuscript.
7. Re-run `citations.py check`, `prose_lint.py`, `paper_check.py ready`.

### Template pitfalls

| Pitfall | Fix |
|---|---|
| Copy only `main.tex` | fetch the style files too |
| Edit `.sty` or `.cls` | never; edit the wrapper |
| Add random packages | only when necessary; they conflict with venue styles |
| Delete example content too early | keep as comments until the end |
| Compile rarely | compile after each section; no local TeX means Overleaf, and `paper_check.py` says so honestly |
