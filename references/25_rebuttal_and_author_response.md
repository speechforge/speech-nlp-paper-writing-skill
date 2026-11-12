# Rebuttal, Author Response, and How Venues Review

Use after reviews arrive, and before submission to anticipate them. It complements `20_reviewer_mode_and_revision.md` (which simulates review) with venue-specific reviewing practice and a disciplined author response. Adapted from the reviewer guidelines of the *ml-paper-writing* guide (MIT; see `NOTICE.md`). Verify dates and forms against the current call.

---

## 1. How the major venues review

### NeurIPS
- Six-point score (see `23` §10). Reviewers are told to **evaluate the paper as written** (not what it could become), give constructive feedback (three to five actionable points), **not penalise honest limitations**, assess reproducibility, and consider ethical implications.
- They should avoid superficial reviews, unreasonable demands for extra experiments, penalising limitation acknowledgment, and rejecting for missing citations to their own work.
- Process: bidding, review period, author rebuttal window, discussion between reviewers, final notification (dates change yearly).

### ICML
- Review form: Summary, Strengths, Weaknesses, Questions, Limitations (assessment of the stated ones), Ethics, Overall score. Scale similar to NeurIPS with calibration: top quarter of accepted papers score 5 to 6, typical accepted 4 to 5, borderline 3 to 4, clear reject 1 to 2.
- Emphasis: reproducibility, experimental rigour (several seeds, proper baselines), writing quality, non-trivial novelty.

### ICLR
- OpenReview: public reviews after decisions, author responses visible to reviewers, discussion with area chairs. Scores: soundness, presentation, contribution (1 to 4 each), overall (1 to 10), confidence (1 to 5).
- Unique: LLM-disclosure compliance is assessed; emphasis on code availability; reciprocal reviewing.

### ACL family
- NLP-specific criteria: **linguistic soundness** (are linguistic claims accurate?), **resource documentation** (datasets and models documented), **multilingual consideration** (language diversity if relevant).
- Reviewers check the Limitations section: honest and comprehensive, whether it undermines core claims, whether negative impacts are addressed. A dedicated ethics review covers dual-use, privacy, and bias.

### Strong reviews follow Dennett's rules (useful when you review others or self-review)
Restate the position so fairly the author would say "thanks, I wish I had put it that way"; list points of agreement; mention what you learned; only then criticise.

---

## 2. Common concerns and the fix you should already have made

| Concern | Fix before submission |
|---|---|
| Technical: unclear method, missing assumptions, weak baselines | state assumptions formally, add the strongest fair baseline, show the ablation that isolates the idea |
| Novelty: "this has been done" | name the closest verified work and the experiment that isolates the delta (`19`) |
| Clarity: hard to follow | signposting, consistent terms, self-contained captions, one message per paragraph (`10`) |
| Significance: why care | tie the contribution to a recognised open problem in the introduction |
| Evidence: missing seeds or uncertainty | add runs and intervals (`16`) |

---

## 3. Writing the author response

**Do:** thank reviewers briefly; answer each concern specifically, quoting it; give evidence (new results from a briefed experiment, `16`); be concise; **accept valid criticism gracefully** ("The reviewer is correct that ...; we will revise to ...").
**Do not:** be defensive or dismissive; promise what you cannot deliver; ignore difficult points; write at excessive length; argue about subjective assessments; use the response to present a substantially different paper unless the venue allows it.

### Template
```markdown
We thank the reviewers for their careful reading.

## Reviewer 1
**R1-Q1: [quoted concern]**
[Direct answer with evidence: table, number, or the exact revised sentence.]
**R1-Q2: [quoted concern]**
[...]

## Reviewer 2
...

## Summary of changes
If accepted, we will:
1. [specific change, with the section it affects]
2. [...]
```

### Accept the criticism when it is
a valid technical error | missing important related work | an unclear explanation | missing experimental details.

### Push back (respectfully) when
the reviewer misunderstood the paper (point to the exact passage) | a requested experiment is out of scope (say why, and what the existing evidence already shows) | the criticism is factually incorrect (give the evidence). Frame it as: "We appreciate this perspective. However, [explanation]."

### Discipline
- Every claim in the response matches `claim_evidence_map.md`; weaken it there first if you cannot support it.
- Any new number comes from an ingested experiment file, not from memory.
- Any new citation goes through `12_citation_integrity.md`.
- Keep a change log mapping each reviewer point to the edit (section, sentence). For double-blind venues, never reveal identity in the response.
- Do not rely on the response for substantial new experiments unless the venue explicitly allows them.

---

## 4. Pre-submission reviewer simulation (ask yourself)

**Quality:** Would I trust these results if I saw them? Are all claims supported by evidence? Are baselines fair and recent?
**Clarity:** Can someone reproduce this from the paper? Is it clear to non-experts in the subfield? Are all terms and notation defined?
**Significance:** Why should the community care? What can people do with this work? Is the problem important?
**Originality:** What specifically is new? How does it differ from the closest related work? Is the contribution non-trivial?

Then run the evidence-first review in `20`, the checklist in `23`, and the gate in `21`.
