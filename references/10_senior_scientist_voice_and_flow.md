# Senior Scientist Voice, Human English, and Flow

Read this before drafting any prose. It defines who is writing, what the paper may and may not contain, and how paragraphs must connect.

---

## 1. The writer: a senior research scientist in NLP and speech

Write as someone who has shipped recognisers, synthesisers, and language models, has reviewed hundreds of submissions, and has been wrong in public. That person:

- **States the finding, then the boundary.** "Pitch error falls from [a] to [b] Hz on [corpus]; we did not test [condition]."
- **Names the linguistic or acoustic reason** behind a number. A gain without a mechanism is a benchmark entry, not a result (Causal Chain, `01_ieee_lab_rules.md`).
- **Respects the reader's time.** One message per paragraph, claims before details, no throat-clearing.
- **Distrusts their own best sample.** Reports where the method fails, which languages, speakers, or domains were not covered, and what the metric cannot see.
- **Knows the field's evaluation conventions** (see §6) and never invents a protocol to make a number look better.
- **Never claims more than the evidence.** Weak evidence changes the verb ("suggests", "is consistent with"), not the confidence of the tone.

If a sentence could appear unchanged in a paper on any other topic, it does not belong in this one.

---

## 2. No coding terms in the paper (hard rule)

The paper describes **ideas, data, and measurements**. It never describes the software that produced them. Code vocabulary leaks into drafts when an agent writes straight from a repository. Translate it.

| Never write (code-speak) | Write (paper-speak) |
|---|---|
| `train_vocoder.py` runs `main()` with `--lr <value>` | The vocoder is trained with a learning rate of [value, in scientific notation]. |
| the `DataLoader` batches [n] samples | Training uses mini-batches of [n] utterances. |
| `config.yaml` sets `sample_rate: <value>` | Audio is sampled at [rate] kHz. |
| we call `loss.backward()` / `optimizer.step()` | Parameters are updated with Adam. |
| the repo's `eval/` scripts compute MCD | Mel-cepstral distortion is computed with [toolkit, version, frame settings]. |
| run `pip install -r requirements.txt` | (Appendix or availability statement only: "Code and exact environment are released at [URL].") |
| `results.csv`, `ckpt_best.pt` | the evaluation results; the final checkpoint selected on validation loss |
| a TODO in the notebook; a hotfix in a branch | (omit; process notes belong in `plan/`, not in the manuscript) |

Rules:

1. **Describe by function, name by concept.** "The boundary detector" not `BoundaryNet.forward`. Use the project's scientific name for each component and keep it identical everywhere.
2. **Library and toolkit names are allowed only as scientific objects** (a named toolkit with its version when it defines a metric or preprocessing step, for example "Montreal Forced Aligner v2.2"). Function, class, flag, file, and branch names are never allowed.
3. **Implementation detail goes in prose, in the appendix or availability statement,** and only as much as reproduction needs: hyperparameters as values with meaning, hardware, total compute, seeds, release URL.
4. **No backticks, no typewriter font, no code blocks, no file paths, no shell commands** in main text. Algorithms are written as numbered steps in plain language or as a short algorithm environment with mathematical notation.
5. **Run the linter before every handoff:** `python3 scripts/prose_lint.py paper/`. High-severity findings (code spans, file names, flags, identifiers) are blockers.
6. The digest made by `context_digest.py` has an "Implementation vocabulary" section so you can understand the method. That section is a translation source, not a vocabulary source.

---

## 3. Human, specific English

Machine-sounding prose is detected by reviewers within a paragraph. Remove the causes.

**Replace stock phrases with the fact they gesture at.**

| Hollow | Specific |
|---|---|
| "plays a crucial role in speech synthesis" | "boundary errors are the most frequent cause of audible buzz in our listening tests ([n] of [N] flagged items)" |
| "it is worth noting that" | (delete; if it is worth noting, note it) |
| "comprehensive evaluation" | "evaluation on [k] corpora, [m] baselines, and [n] listeners" |
| "leverages recent advances" | name the advance and the citation |
| "seamlessly integrates" | say what interface joins the parts and what it costs |
| "significantly outperforms" | give the difference, the test, and the interval |

**Vary rhythm on purpose.** Mix a long explanatory sentence with a short one that lands the point. Three equal-length sentences in a row read as generated.

**Prefer concrete nouns and active verbs.** "We trained the detector on [n] hours of aligned speech" over "Training was performed using a dataset".

**Use examples.** One concrete utterance, phoneme transition, or error string explains more than a paragraph of abstraction. Put it in Figure 1 or the introduction.

**Ban list (enforced by `prose_lint.py`):** delve, tapestry, realm, "it is worth noting", "plays a crucial/pivotal/vital role", game-changing, cutting-edge, groundbreaking, revolutionize, unprecedented, seamless, "a testament to", underscores, myriad, paramount, "in today's", "in recent years" openers, stock "not only ... but also", and unbacked superlatives. Sentence-initial *Moreover, Furthermore, Additionally* are allowed rarely and only when they carry meaning.

**Hedging.** Use "may" and "might" only where the evidence is genuinely uncertain, and say what would resolve it. Do not hedge established results; do not assert uncertain ones.

The classic craft rules (Gopen and Swan reader expectations, Perez micro-tips, Lipton word choice, Steinhardt precision) are consolidated in `22_craft_from_ml_paper_writing.md`. Apply them at sentence level.

---

## 4. Flow: how a paper reads as one argument

### 4.1 The spine
Fill the **reader promise table** in `paper_story.md` before drafting:

| Section | What the reader knows on entering | The question it answers | The hand-off question it leaves |
|---|---|---|---|

Every section starts by connecting to the previous hand-off question ("Having shown that boundary errors cause the buzz, we now ask what in the loss allows them") and ends by posing the next one. If a section's entry knowledge is not produced by the previous section, the flow is broken.

### 4.2 Paragraph clarity test (run on any paragraph that "does not flow")
1. Does the paragraph make **one** point, stated in its first sentence?
2. Are all key nouns understandable without hidden context? Is each new term defined before reuse?
3. Does each sentence connect to the previous one by a **named relation**: cause, contrast, consequence, refinement, example, or concession? If you cannot name it, the sentence is misplaced.
4. Does the last sentence close the idea and open the next paragraph?

### 4.3 Reverse outline (after every section)
Write the section's thesis. Under it, one line per paragraph topic sentence. Under each, the evidence or explanation points. Check: topic sentence maps to the thesis, evidence maps to its topic sentence. Move, merge, or delete any paragraph that cannot be mapped. If flow is still weak, add temporary headings and explicit transitions, then remove unneeded headings.

### 4.4 Connectives that carry meaning
Prefer: *because, so, however, even so, in contrast, for example, concretely, as a result, which is why, the exception is*. Avoid chains of additive connectives. A reader should be able to predict the logical shape of the next sentence from the connective.

### 4.5 Old before new
Begin sentences with what the reader already knows (the previous sentence's end, a defined term), and end with the new information, where stress falls. Put the number or the named result at the end of its sentence.

---

## 5. Novelty runs through every section

Flow is strongest when the contribution is the thread. Keep `Novelty keywords` in `paper_story.md` and apply the thread rule from `19_novelty_and_story.md`: the novelty must be recognisable in the title or first abstract sentence, the introduction's occupy move, the method (marked as new), each experiment's research question, the discussion, and the conclusion. `python3 scripts/paper_check.py PROJECT thread` verifies it mechanically.

---

## 6. Field conventions a senior NLP/speech author never skips

- **Speech synthesis and conversion:** MOS/SMOS with listener count, rating scale, anchors, and 95% confidence intervals (ITU-T P.800 conventions); MUSHRA for fine comparisons; objective metrics with toolkit and version; real-time factor with hardware and batch size; speaker-independent splits.
- **ASR and spoken-language understanding:** WER/CER with text normalisation declared; paired significance tests (bootstrap or matched-pairs); results broken down by speaker group, accent, or noise condition; contamination of pretraining data stated.
- **NLP:** state datasets, languages, and domains evaluated and refuse to generalise beyond them; report variance across seeds or prompts; for LLM-judged evaluation, name the judge, the prompt, agreement with humans, and known judge bias; for human evaluation, annotator count, qualification, compensation, agreement (Krippendorff's alpha or Fleiss' kappa).
- **Low-resource and multilingual:** report per-language numbers, not only averages; describe data provenance and licences; be explicit about dialect and script coverage.
- **Safety and ethics:** consent and licensing for voices and text; misuse of voice cloning; bias across languages and dialects.
Deeper domain rules live in `skills/domains/*.md`.

---

## 7. Time allocation (Neel Nanda)

Spend about equal effort on: (1) the abstract, (2) the introduction, (3) the figures, (4) everything else combined. Readers meet the paper as title, abstract, introduction, figures, and only then the body.
