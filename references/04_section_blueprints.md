# Research Paper Section Blueprints & Drafting Templates

Use these section blueprints when drafting or restructuring each section of an academic research paper.

---

## Blueprint 1: Abstract
- **Length**: 150–220 words (typically one block paragraph).
- **Structure (The 4-Sentence Rule)**:
  1. *Context & Objective*: State the core technical challenge and the proposed method name.
  2. *Gap / Failure of Prior Art*: Specify precisely what existing models fail to model or evaluate.
  3. *Core Mechanism*: Detail the novel mathematical or architectural formulation in concrete terms.
  4. *Quantitative Validation*: State the exact benchmark, baselines, and 2–3 strongest metrics with numerical improvements.

---

## Blueprint 2: Introduction (Swales CARS Architecture)
- **Target Space**: 0.8–1.0 page.
- **Move 1: Establish Territory (Paragraph 1)**
  - Topic significance (speech synthesis quality, diffusion speed, representation fidelity).
  - High-level current landscape.
- **Move 2: Create a Niche (Paragraph 2)**
  - Highlight the exact failure mode (e.g., "However, standard time-domain losses fail to penalize phase discontinuity across unvoiced-to-voiced boundaries, leading to audible buzz...").
  - Point out why existing baselines cannot easily resolve this.
- **Move 3: Occupy the Niche (Paragraph 3 & Contributions)**
  - "To overcome this limitation, this paper proposes..."
  - Summarize the mechanism and foreshadow the empirical outcomes.
  - Bulleted Contributions:
    - *Contribution 1*: Operational definition of the primary architectural/methodological proposal.
    - *Contribution 2*: Formulation of novel diagnostic, loss, or evaluation metric.
    - *Contribution 3*: Comprehensive empirical validation on [X datasets, Y baselines], establishing [Z key finding] and public reproducibility.

---

## Blueprint 3: Related Work & Prior Baselines
- **Structure**: Organize by 2–3 distinct thematic paradigms (not chronological author laundry-lists).
- **Format for each paradigm paragraph**:
  1. *Category Definition*: Name the family of models/approaches.
  2. *Key Advances*: Cite 3–5 representative papers and their shared methodology.
  3. *Remaining Limitation*: Explicitly pinpoint the gap or assumption they rely upon.
  4. *Contrast with Proposed Work*: One sentence stating how the proposed method diverges conceptually or mathematically.

---

## Blueprint 4: Proposed Methodology / Mathematical Formulation
- **Structure**:
  1. *Overview / Problem Formulation*: Formal mathematical notation, inputs $x \in \mathcal{X}$, outputs $y \in \mathcal{Y}$, and objective function.
  2. *Core Component 1*: Detailed formulation, architecture diagram reference, equation derivations.
  3. *Core Component 2*: Loss functions, regularizers, or diagnostic transformations.
  4. *Algorithmic / Computational Complexity*: Parameter count, memory footprint, or sampling steps.
- **Guiding Rule**:
  - Always explain the *intuition* behind each mathematical term immediately after its equation.
  - Define every variable upon its first appearance.

---

## Blueprint 5: Experimental Setup
- **Essential Subsections**:
  1. *Datasets & Partitions*: Training, validation, and test splits (hours, speakers, sampling rate). Clear OOD definition if claimed.
  2. *Baseline Models*: Exact names, checkpoints, and parameter matching across comparisons.
  3. *Training & Implementation Details*: Optimizer, learning rate schedule, batch size, iterations, loss weights, hardware (GPU type, precision).
  4. *Evaluation Metrics*:
     - Group into clear dimensions (e.g., Perceptual Quality, Objective Reconstruction, Intelligibility, Efficiency).
     - State metric toolkits, versions, and sampling rates used.

---

## Blueprint 6: Results and Discussion
- **Structure in Claim Order**:
  1. *Primary Comparative Table*: Main benchmark results comparing proposed model against all baselines.
  2. *Analysis of Primary Results*:
     - Lead with the main takeaway.
     - Cite exact numbers from the table.
     - Provide physical or mathematical rationale for *why* the proposed method achieves this gain.
  3. *Ablation Studies*:
     - Isolate each proposed component one-by-one.
     - Show that the gain does not come merely from increased parameter capacity.
  4. *Diagnostic / Qualitative Analysis*:
     - Spectrogram comparisons, error distributions, or phonetic breakdown.
     - Point out localized artifacts or boundary transitions.

---

## Blueprint 7: Limitations, Discussion & Future Work
- **Structure**:
  - State 2–3 genuine limitations honestly (e.g., inference latency on edge devices, performance on severely noisy speech, reliance on accurate pitch extraction).
  - Provide a paired response or prospective solution for each limitation.
  - End on a strong, forward-looking note regarding broader applications.

---

## Blueprint 8: Conclusion
- **Length**: 1–2 compact paragraphs.
- **Structure**:
  1. Concise recap of the core problem addressed and the proposed solution.
  2. Summary of key empirical validation results.
  3. Final synthesis sentence emphasizing the broader impact on the research field.
