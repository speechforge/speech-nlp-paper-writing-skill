# ML & Speech Research Paper Architecture (Farquhar & Nanda Principles)

Based on *Sebastian Farquhar (Oxford/DeepMind)*: "How to Write ML Papers" and *Neel Nanda*: "Highly Opinionated Advice on How to Write ML Papers".

---

## 1. The Four-Sentence Abstract Formula
A high-impact abstract has exactly 4–5 sentences:
1. **Sentence 1 (Achievement / Thesis)**: What did you achieve?
   - *"We introduce Benchmark-D, a multidimensional evaluation methodology that assesses pretrained neural vocoders across five perceptual and operational dimensions."*
2. **Sentence 2 (Difficulty / Importance)**: Why is this problem hard and important?
   - *"Existing benchmarks often collapse synthesis quality into isolated subjective scores or overall spectral averages, obscuring localized acoustic degradations and deployment feasibility."*
3. **Sentence 3 (The 'How' / Mechanism)**: How do you solve it?
   - *"Benchmark-D combines hierarchical utility normalization with reference-anchored phonetic transition diagnostics to isolate phoneme-level distortions."*
4. **Sentence 4–5 (Evidence / Hard Numbers)**: What is your strongest empirical evidence?
   - *"Evaluated across 14 vocoders and 3 benchmark corpora, Benchmark-D identifies high-frequency aliasing artifacts in 4 widely used models and correlates strongly with blinded listener judgments ($r=0.91$)."*

---

## 2. The One-Page Introduction Rule
For a standard conference paper (4-page ICASSP or 8-page Interspeech/NeurIPS/ICLR), the Introduction should be tightly budgeted:
- **Paragraph 1: Core Problem & Stakes (2–3 sentences)**:
  - Skip boilerplate generic claims (e.g., *"Deep learning has revolutionized speech processing in recent years"*—delete this; reviewers skip it). Start directly with the technical dilemma.
- **Paragraph 2: Current Bottleneck & Our Approach (3–4 sentences)**:
  - What prior models fail to do, what your mechanism does, and why it works differently.
- **Paragraph 3: Empirical Flavor of Evidence (2–3 sentences)**:
  - Scope of validation (datasets, model families, baselines, hardware setups).
- **Contributions (Bulleted list of 2–4 items)**:
  - Each bullet must be 1 line in single-column or 2 lines in two-column format.
  - Link each contribution to a specific result or ablation in the paper.

---

## 3. The Sacred Role of Figure 1 (The Teaser Pipeline)
- Reviewers and readers look at Figure 1 *first*.
- **Placement**:
  - In a two-column conference layout (IEEE ICASSP / Interspeech), Figure 1 should be placed at the **top of column 2 on Page 1**.
  - In single-column format, place it at the **top of Page 2**.
- **Content**:
  - Figure 1 must be self-contained. It should visually contrast the failure mode of prior art (e.g., smeared boundary, aliased harmonics) against the proposed method's remedy.
  - A reviewer should understand the paper's core hypothesis from Figure 1 and its caption alone.

---

## 4. Background vs. Related Work
Never confuse Background with Related Work:
- **Background**:
  - *Must meet three tests*: (a) Essential concept required to understand your math/architecture; (b) Not novel to your paper; (c) Not assumed common knowledge among typical reviewers.
  - Keep it short; omit textbook definitions.
- **Related Work**:
  - The goal is **not** an exhaustive literature survey, but **differentiating your work from the closest competitors**.
  - Always group related work thematically:
    $$\text{Method Family} \longrightarrow \text{What they achieved} \longrightarrow \text{What critical limitation remains} \longrightarrow \text{How our work directly addresses it}$$

---

## 5. Minimal-Ink Tables & Visual Clarity
- Follow Edward Tufte's principles of data presentation:
  - Use `booktabs` in LaTeX (`\toprule`, `\midrule`, `\bottomrule`). **Zero vertical lines**.
  - Bold only the statistically significant best number (or top-tier within confidence interval). If difference is negligible, do not arbitrarily bold one over another.
  - Always define metric orientation: indicate with $(\uparrow)$ or $(\downarrow)$ in each table header column.
  - State the unit (dB, %, ms, xRT) in the header, never repeated in table cells.

---

## 6. The Writing Process: Compress, Then Iteratively Expand
1. **Compress**: First write down the entire paper as a 10-line skeleton (Thesis, 3 Contributions, Figure 1 concept, 4 core numbers).
2. **Iteratively Expand**:
   - Flesh out table schemas and figure mockups before writing text.
   - Write bold purpose sentences for every paragraph.
   - Fill in methods ("to-clauses") and results.
   - Refine transitions and sentence-level polish.
