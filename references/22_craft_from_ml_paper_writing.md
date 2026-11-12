# Craft from Leading ML Paper-Writing Guides

Consolidated from the *ml-paper-writing* guide supplied with this task (Orchestra Research, MIT; see `NOTICE.md`) and the researchers it synthesises. These rules **add to** the lab standards in `01` to `09`; where they differ, the notes below say how to reconcile them.

---

## 1. Sources

| Source | Key contribution |
|---|---|
| Neel Nanda (Google DeepMind) | the Narrative Principle; What / Why / So What; time allocation |
| Sebastian Farquhar (DeepMind) | five-sentence abstract formula |
| Gopen and Swan | seven principles of reader expectations |
| Zachary Lipton | word choice, eliminating hedging and intensifiers |
| Jacob Steinhardt (UC Berkeley) | precision, consistent terminology, assumptions stated |
| Ethan Perez (Anthropic) | micro-level clarity tips |
| Andrej Karpathy | single-contribution focus |

External pages (verify availability before citing them in a paper; they are guides, not citations): Nanda, "Highly opinionated advice on how to write ML papers" (Alignment Forum); Farquhar, "How to write ML papers"; Gopen and Swan, "The Science of Scientific Writing"; Lipton, "Heuristics for technical scientific writing"; Perez, "Easy paper writing tips".

---

## 2. Abstract: how the five-sentence formula fits the lab formulas

Farquhar: (1) what you achieved ("We introduce / prove / demonstrate ..."); (2) why this is hard and important; (3) how you do it, with specialist keywords for discoverability; (4) what evidence you have; (5) your most remarkable number or result. Delete any opening sentence that could be prepended to any ML paper.

Reconciliation: the lab's **4-sentence** formula (`03`) merges Farquhar's (4) and (5) into one evidence sentence; the **7-sentence IEEE** formula with the em-dash (`06`, Rules B1 to B8) splits task, application, bottleneck, proposal, results, efficiency, and demo. Use the form the target venue and lab convention require; all three keep the same order: achievement, difficulty, mechanism, evidence with the most remarkable number last.

---

## 3. Sentence-level clarity (Gopen and Swan)

| Principle | Rule | Example |
|---|---|---|
| Subject-verb proximity | keep subject and verb close | "The model, which was trained on ..., achieves" becomes "The model achieves ... after training on ..." |
| Stress position | emphasis goes at the sentence end | "When using attention, accuracy improves by 15%" |
| Topic position | context first, news after | "Given these constraints, we propose ..." |
| Old before new | familiar information, then unfamiliar | link backward, then introduce |
| One unit, one function | one point per paragraph | split multi-point paragraphs |
| Action in the verb | verbs, not nominalisations | "We analysed", not "We performed an analysis" |
| Context before new | set the stage first | explain, then show the equation |

## 4. Micro-level tips (Perez)

- Minimise bare pronouns: "This result shows", not "This shows".
- Put verbs early in the sentence.
- Unfold awkward possessives: "the Y of X" instead of "X's Y".
- Delete filler: actually, a bit, very, really, basically, quite, essentially.

## 5. Word choice (Lipton)

- Be specific: "accuracy" or "latency", not "performance".
- Eliminate hedging: drop "may" and "can" unless the uncertainty is real.
- Avoid incremental vocabulary ("combine", "modify", "expand") for the central idea; say what you "develop", "propose", or "introduce", and what it enables.
- Delete intensifiers: "provides tight approximation", not "very tight".

## 6. Precision over brevity (Steinhardt)

- One term per concept, for the whole paper; list assumptions before theorems; give intuition beside rigour.

---

## 7. What reviewers actually read

| Section | Share who read it | Implication |
|---|---|---|
| Abstract | all | must be perfect |
| Introduction | most, skimmed | front-load the contribution |
| Figures | before the method | Figure 1 is critical |
| Methods | only if interested | do not bury the lede |
| Appendix | rarely | supplementary only |

If the abstract and introduction do not hook the reviewer, the methods may never be read.

---

## 8. Conference requirements quick reference (as supplied; verify against the current call)

| Venue | Pages | Extra for camera-ready | Key requirement |
|---|---|---|---|
| NeurIPS | 9 | +0 | mandatory checklist; lay summary for accepted papers |
| ICML | 8 | +1 | broader-impact statement |
| ICLR | 9 | +1 | LLM disclosure; reciprocal reviewing |
| ACL | 8 long (official guide: 9 final) | +1 | Limitations section |
| AAAI | 7 | +1 | strict style-file adherence |
| COLM | 9 | +1 | focus on language models |

The ACL row is reconciled with the pinned official formatting guide in `13`. Universal: double-blind, references outside the count, unlimited appendices that reviewers need not read, LaTeX required.

## 9. Paper structure workflow (supplied guide, aligned with this skill)

1. Define the **one-sentence contribution** (`19`). 2. Draft **Figure 1** (readable in black and white; caption stands alone). 3. Abstract. 4. Introduction (1 to 1.5 pages; 2 to 4 contribution bullets; methods start by page 2 or 3). 5. Methods (reimplementable: outline or pseudocode, hyperparameters, architecture). 6. Experiments (each experiment states the claim it supports, how it connects to the contribution, the setting, and what to observe; error bars with their method; search ranges; compute; seeds). 7. Related Work organised **by method, not paper by paper** ("one line of work assumes X; we use Y because ..."), cited generously because reviewers likely wrote some of it. 8. **Limitations** (required; honesty is not penalised and pre-empts criticism). 9. Venue checklist. 10. Final review cycle.

## 10. Common issues and fixes

| Issue | Fix |
|---|---|
| Abstract too generic | delete the first sentence if it fits any ML paper; start with the contribution |
| Introduction over 1.5 pages | move background to Related Work; front-load the contribution bullets |
| Experiments lack explicit claims | add "This experiment tests whether [claim]" before each |
| Reviewers find it hard to follow | add signposting, keep terminology consistent, make captions stand alone |
| Missing statistical significance | error bars with their definition, number of runs, a test when comparing methods |

## 11. Tables and figures (additions)

Use `booktabs`; bold the best value per metric; direction symbols; right-align numbers (or centre consistently); constant decimal precision. Figures: vector, colour-blind-safe, grayscale-legible, no in-figure title, self-contained captions (see `14`).

---

## 12. Additions from the full writing guide

### Introduction template (one to one and a half pages; methods start by page 2 or 3)
1. **Opening hook** (2 to 3 sentences): the problem and why it matters now. 2. **Background and challenge** (one paragraph): what makes it hard, what others tried, why that is insufficient. 3. **Your approach** (one paragraph): what you do differently and the key insight. 4. **Contribution bullets** (2 to 4, one or two lines each, specific and falsifiable). 5. **Results preview** (2 to 3 sentences): the most impressive numbers and the scope of the evaluation. 6. **Organisation** (optional, one or two sentences). This maps onto the lab's CARS introduction (`04` Blueprint 2): hook and challenge are the Territory and Niche, the approach and bullets occupy the niche.

### Contribution bullets
- Good (specific, checkable): "We prove that X converges in O(n log n) time under assumption Y." "We introduce Z, which reduces memory by [p]%." "We show that A outperforms B by [d] on benchmark C." (Fill brackets from results files; never invent them.)
- Bad: "We study the problem of X" (not a contribution); "We provide extensive experiments" (vague); "We make several contributions to the field" (says nothing).

### Mathematical writing
State all assumptions formally before theorems; give intuition beside proofs; keep notation consistent and define each symbol at first use; unfold awkward possessives ("the accuracy of the model"). Conventions: scalars lowercase italic ($x,\alpha$); vectors lowercase bold ($\mathbf{x}$); matrices uppercase bold ($\mathbf{W}$); sets uppercase calligraphic ($\mathcal{X}$); named functions in roman ($\mathrm{softmax}$). Explain each equation in words immediately after it (lab rule, `04` Blueprint 4).

### Vocabulary signalling
Choose verbs that tell the reader how strongly the evidence supports a statement ("proves", "shows", "suggests", "is consistent with"), and use one term per concept.

### Common mistakes
| Area | Mistake | Fix |
|---|---|---|
| Structure | introduction over 1.5 pages | move background to Related Work |
| Structure | methods buried after page 3 | front-load the contribution, cut the introduction |
| Structure | no contribution bullets | add 2 to 4 specific, falsifiable claims |
| Writing | generic abstract opening | start with the specific contribution |
| Writing | passive voice everywhere | "We show", not "It is shown" |
| Writing | hedging everywhere | be confident unless genuinely uncertain |
| Figures | raster plots, red-green palettes, titles inside figures, captions that need the text | vector, colour-blind-safe, caption carries the title, self-contained captions |
| Citations | paper-by-paper Related Work; missing relevant work; AI-generated references | organise by method; cite generously; verify with `12` |

See also `25_rebuttal_and_author_response.md` for review and response practice.
