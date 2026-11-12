# Reviewer Mode and Targeted Revision

Use for the **Draft review** and **Targeted revision** journeys. It extends the 5-dimension checklist and claim-evidence audit in `05_adversarial_review_checklist.md` with an evidence-first procedure and a revision discipline. Procedure adapted from the evidence-first review method of the *ai-research-writing-skill* project (MIT, see `NOTICE.md`).

---

## 1. Choose the context (and say which one)

- **Author-side simulation:** diagnose the draft and plan revisions. Label every verdict as simulated; never present it as a venue decision.
- **Assigned peer review:** assess the submitted version and supplements, write a concise review with evidence notes, leave final judgment to the human reviewer, and do not rewrite the manuscript unless asked. Keep confidential material inside the authorised workspace. Never fabricate a human reviewer's assessment, expertise, or reproduction work.

---

## 2. Evidence-first procedure

1. **Inventory coverage:** which version, which appendices, what code or data was available, what could not be read. An access failure is not evidence that authors supplied nothing. State partial-read limits.
2. **Restate the strongest supported contribution:** separate whole-system performance from the controlled contribution of a component. Value useful negative results, simple methods, careful measurement, and new tasks; do not demand leaderboard gains.
3. **Check before objecting:** read the appendices and captions before saying something is missing; verify consequential equations, table columns, and figures when text extraction is ambiguous; recompute decisive differences where feasible. If you cannot verify, keep the uncertainty rather than assert a contradiction.
4. **Write evidence notes** before verdicts (template below). Separate observation, interpretation, and question.
5. **Prioritise by decision impact:** merge duplicates; foreground the few concerns that could change the recommendation; omit peripheral requests.
6. **Calibrate:** weigh reliable contributions against unresolved risks to the central claims, not the number of complaints. Report your confidence separately from the recommendation.

### Three lenses (run before merging findings)

| Lens | Primary questions |
|---|---|
| Methodology | Is the method sound, motivated, and reproducible, and do the experiments support it? |
| Domain and positioning | Is the task important, is the closest work represented accurately, and is the contribution genuinely different? |
| Statistics and evidence | Do numbers trace to sources? Are uncertainty, seeds, tests, failures, and claim strength handled correctly? |

Do not ask one pass to rewrite the paper while reviewing it. First record findings with section and claim references.

### Evidence note (one per material concern)

```
ID / affected claim:
Location: section, page, equation, table row, appendix, or artifact path
Already supplied / checked:
Observation and evidence:
Fact / inference / needs clarification:
Impact on the central claim and severity (high, medium, low):
Question for the authors:
Minimum evidence that would resolve or narrow the concern:
```
Record strengths with locations too.

### Fairness
- Ask for what the claim needs; prefer an existing table or a small diagnostic over a new research project, and say why any extra experiment is necessary.
- Missing detail or an unclear split supports a clarification request, not an accusation of leakage or misconduct.
- For novelty objections, name the concrete technical overlap in verified close work.
- Do not penalise non-state-of-the-art results or cosmetic defects unless they undermine the stated contribution.

---

## 3. Review format

```
Review context: version read; simulated or AI-assisted status
Summary: problem, method, strongest supported contribution, scope
Strengths: specific, with evidence
Major concerns: IDs, locations, evidence, impact on claims
Questions: each mapped to a concern ID and bounded resolving evidence
Recommendation: stance and decisive reasons
Confidence and coverage: what was checked, not checked, uncertain
Ethics: an evidence-based concern if any (none found is not a clearance)
```

### Six dimensions (pass, needs revision, needs evidence, not assessed)

| Dimension | Reviewer question | Common failure |
|---|---|---|
| Contribution | What is new and why does it matter? | reads like an implementation report |
| Writing clarity | Can I restate the paper after the introduction? | narrative is a list of modules |
| Experimental strength | Do the experiments support the main claims? | claims rest on partial or cherry-picked numbers |
| Evaluation completeness | Are baselines, metrics, splits fair? | missing ablations, unclear settings, weak baselines |
| Method soundness | Are design choices justified and reproducible? | hidden manual steps, undocumented heuristics |
| Responsibility | Limitations, data use, ethics, release claims? | obvious risks unstated |

Reference scale used by several ML venues (six points): 6 strong accept (groundbreaking, flawless); 5 accept (technically solid, high impact); 4 borderline accept (solid, limited evaluation); 3 borderline reject (solid but weaknesses outweigh); 2 reject (technical flaws); 1 strong reject (known results or ethics issues). Calibrate against the target venue's own rubric.

### Speech and NLP specifics to check
Speaker-independent splits and leakage; listener counts, scale, anchors, confidence intervals; metric toolkit and version; text normalisation for WER; language and dialect scope; annotation protocol and agreement; LLM-judge validity; licence and consent of corpora; misuse of synthesis.

---

## 4. Rejection-risk diagnosis to concrete edits

Write `reviewer_analysis.md` (template provided). Convert every high or medium risk into exactly one action:

| Risk | Fix type | Concrete action |
|---|---|---|
| Unsupported claim | Edit | weaken or remove it in the abstract and introduction; update the claim map |
| Missing evidence | Experiment | write a brief (`16`), run, ingest, rewrite |
| Confusing method | Writing and figure | add the overview diagram, state the invariant, reorder |
| Weak citation | Citation | replace with a verified primary source (`12`) |
| Scope gap | Limitation | add a limitation paragraph with its consequence |
| Policy or ethics risk | Responsibility | add disclosure, anonymise an asset, or remove an unsupported release claim |
| "Done before" | Positioning | name the exact prior work and the experiment that isolates the delta |

High-severity unresolved items block a "submission-ready" claim; record any user-accepted risk explicitly rather than marking it resolved. They do not block delivering an honest review.

### Final self-review statement
```
The paper is currently strongest on ...
The highest remaining reviewer risk is ...
The main evidence for the central claim is ...
Claims intentionally weakened or removed: ...
Submission-blocking issues: ...
```

---

## 5. Targeted revision discipline

Use when the user gives a draft plus feedback, or a section to improve.

1. **Scope the change:** name the section files you will touch; do not regenerate the whole paper unless the story changed.
2. **Preserve claim-evidence boundaries:** never write a stronger claim than the evidence supports, never introduce a number that is not in a results file, never add a citation that is not verified.
3. **Load only the blueprint for that section** (`04`) and the voice rules (`10`).
4. **Revise paragraph by paragraph:** one message per paragraph, topic sentence first, connectives that carry meaning, terminology identical to the rest of the paper.
5. **Reverse-outline the section** after the edit (`10` §4.3).
6. **Update the claim map** for every claim whose wording changed; if a claim was weakened, weaken it everywhere (abstract, introduction, conclusion, website, figure captions).
7. **Re-run the checks that the edit can break:** `prose_lint.py`, `citations.py check`, `paper_check.py thread` and `assets`.
8. **Report the diff in claims, not just words:** which claims were weakened, removed, or newly supported.
9. **Do not silently hide trade-offs.** If the right fix needs an experiment, a different framing, or a weaker claim, tell the author.

### Rebuttal readiness
Before submission prepare short answers to: What is the closest prior work and the exact difference? Why are the baselines fair? Which result directly supports the central claim? What happens in failure cases? Which limitation is real but does not invalidate the claim? If an answer needs a large new experiment, do it before submission or weaken the claim: rebuttal cannot be relied on for substantial new experiments.
