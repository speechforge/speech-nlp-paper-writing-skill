# Submission Readiness and Packaging

A submission package must be buildable, auditable, and free of accidental placeholders. A polished PDF is not enough: the source tree must have no unresolved citations, broken figure paths, stale assets, or hidden markers.

---

## 1. The gate

```bash
python3 scripts/paper_check.py PROJECT ready      # prints a gate table, writes .paper/checks.json (shown on the dashboard)
```

| Gate | Blocking? | What it checks |
|---|---|---|
| No unresolved markers | yes | `TODO`, `FIXME`, `TBD`, `[INSERT`, `[CITATION NEEDED`, `PLACEHOLDER`, lorem ipsum in the manuscript and story/claim files |
| Citations verified | yes | `citations.py check --strict`: every cited key present, unique, `verified` in the lock, no weak support |
| Prose | yes | `prose_lint.py` high-severity findings: code spans, file names, flags, identifiers, shell commands |
| Figures, labels, inputs | yes | every `\includegraphics`, `\input`, and `\ref` resolves; no duplicate labels |
| Every claim has evidence | yes | `claim_evidence_map.md` has no open row and at least one claim |
| Novelty thread | warning | each section carries a novelty keyword |
| No experiment pending | warning | ledger has nothing proposed, approved, running, or failed |
| Credit and license statements | yes | both present in the manuscript |
| Project identity free of venue names | yes | project name has no conference or publisher word |
| LaTeX build | blocking if TeX exists; warning if not installed | latexmk or pdflatex+bibtex succeeded |

**Do not say "done" until blocking gates pass or blockers are reported.** If TeX is not installed the gate says so: compile on Overleaf, then record the result; the static checks still apply.

Other helpers: `paper_check.py PROJECT todos | assets | log | thread | claims | build`.

---

## 2. Manual review that tools cannot do

- **Citation fit:** each source supports the sentence (relation recorded), including in Related Work.
- **Number tracing:** every number in the abstract, introduction, tables, and website traces to a results file or `.source.json`.
- **Claim audit:** abstract and introduction claims versus the strongest experiments; "first", "general", "robust", "state-of-the-art" re-examined (`01`, `19`).
- **Venue checklist:** limitations and failure modes; datasets, splits, metrics, baselines, seeds, uncertainty, compute; code, data, and model availability and licences; ethics, privacy, human subjects, safety; AI-assistance disclosure; consent for released assets. An honest "No" with a concrete limitation beats an unsupported "Yes".
- **Anonymity (review versions):** author names, affiliations, acknowledgments, contribution statements, funding, repository and website links, file metadata, PDF properties, speaker names in samples, and self-citations.
- **Page budget:** what counts toward the limit under the current call (`13`).
- **Figures:** readable at final size, grayscale-safe, fonts embedded (`14`, `08`).
- **Website:** built, free of venue names, numbers match the paper (`15`).

---

## 3. Packaging hygiene

- Keep source for plots and diagrams (`*.source.json`, specs); prefer vector formats; remove `.DS_Store`, temporary TeX files, stale PDFs, failed generation attempts, and `.paper/cache` unless archiving.
- Never include credentials, local absolute paths, private datasets, or API keys.
- Check that figures match captions and text.
- Zip or upload only `paper/` (and supplementary material), not `.paper/`, experiment logs, or private notes.

### Build commands (when TeX is available)
```bash
latexmk -pdf -interaction=nonstopmode paper/main.tex
# or: pdflatex; bibtex; pdflatex; pdflatex
python3 scripts/paper_check.py PROJECT log
```
Check: undefined references and citations, overfull boxes, missing figures, placeholder author names, and acknowledgments in anonymous versions.

### Overleaf or Git handoff
1. `git status --short`; inspect modified files and generated assets.
2. Run the gate.
3. Stage only intended files; commit with a concise message.
4. **Push only when the user has asked or clearly authorised it**; confirm the remote and branch.
5. Never revert unrelated edits made by the user.

---

## 4. Camera-ready differences

Author names, affiliations, and acknowledgments appear (`\camerareadytrue`, class option `final`); licence and data or code links updated; website `anonymous` set to false; arXiv and supplementary references updated; reviewer-requested changes done; appendix cross-references; final page and file-size limits; venue copyright or licence form.

---

## 5. Submission readiness record

Fill `submission_readiness.md`: target venue and template mode, page budget, anonymity check, gate output, citation status, venue checklist status, credit and license consistency, figure status, website status, known reviewer risks left open (user-accepted), and next actions.

## 6. Final response contract

When reporting, state: files changed; checks run and their results; build status; remaining scientific risks and blockers; any commit or push performed. Say plainly what was not verified.
