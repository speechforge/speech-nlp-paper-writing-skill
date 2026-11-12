# Adversarial Review Checklist & Claim-Evidence Audit Matrix

Use this checklist to simulate a skeptical, top-tier conference reviewer (ICASSP, Interspeech, NeurIPS, ICML, ICLR) before submitting or finalizing any paper draft.

---

## Part 1: The 5-Dimension Adversarial Review Checklist

### 1. Contribution & Novelty
- [ ] Is the proposed contribution clearly distinguished from prior art, or does it feel like an incremental hyperparameter tweak?
- [ ] Are the listed contributions (2–4 items) each formally defined and verified in the results?
- [ ] Does the paper avoid ungrounded "first to..." or "revolutionary" claims?
- [ ] Is the core conceptual insight separable from increased model capacity or larger training datasets?

### 2. Writing Clarity & Narrative Flow
- [ ] Does the Abstract follow the 4-sentence structure and contain concrete numbers?
- [ ] Does the Introduction follow Swales's CARS model (Territory, Niche, Occupy) and fit within ~1 page?
- [ ] Does every paragraph have one central message with a strong topic sentence and forward-looking concluding sentence?
- [ ] Does Figure 1 immediately communicate the core problem and solution without needing main text lookup?
- [ ] Are all acronyms and symbols formally defined before their first usage?

### 3. Experimental Rigor & Fairness
- [ ] Are baselines tuned fairly, running with standard configurations or matched parameter budgets?
- [ ] Is the experimental unit explicitly declared (architecture, checkpoint, frontend, precision, backend, hardware)?
- [ ] Are statistical significance tests, standard deviations, or confidence intervals reported where claims of superiority are made?
- [ ] Are training, validation, and test splits strictly leak-free (no speaker or sentence overlap between train and test)?

### 4. Evaluation Completeness & Trade-Offs
- [ ] Does the evaluation cover multidimensional criteria (e.g., quality vs. computational efficiency vs. memory)?
- [ ] If the model trades off speed for quality (or vice-versa), is this trade-off explicitly stated and visualized on a Pareto frontier?
- [ ] If subjective listening tests (e.g., MUSHRA, MOS) are reported, are sample counts, listener counts, and listening environments stated?
- [ ] Are out-of-distribution (OOD) tests genuinely out-of-distribution (unseen speakers, noise, domains)?

### 5. Methodological Soundness & Reproducibility
- [ ] Are mathematical equations consistent in notation throughout the text?
- [ ] Do ablation studies isolate each individual novel component rather than turning everything on/off at once?
- [ ] Is every loss term weighted with justified hyperparameter choices?
- [ ] Are limitations and failure modes transparently acknowledged in the discussion?

---

## Part 2: Claim-Evidence Audit Matrix

Every major assertion in the Abstract, Introduction, and Results must pass this audit:

| Major Paper Claim | Supporting Table / Figure | Specific Numerical Evidence | Confidence / Scope Limit | Audit Status (`Supported` / `Partial` / `Unsupported`) |
|---|---|---|---|---|
| *Example: "Reduces aliasing distortion across high frequencies"* | Table 2 & Fig. 3 | Band 4 LSD reduced from 4.12 dB to 2.30 dB ($p < 0.01$) | Validated on LJSpeech and VCTK test splits | `Supported` |
| *Example: "Real-time synthesis on edge CPU devices"* | Table 4 | RTF = 0.082 on Raspberry Pi 4 (single thread) | Audio duration > 3s; 16 kHz sampling rate | `Supported` |
| *Example: "Outperforms all existing neural vocoders globally"* | Table 1 | Only tested against 3 baselines on 1 dataset | Overclaiming; must bound claim to tested set | `Needs Bounding / Revision` |

---

## Review Decision Rubric
- **Accept (Strong)**: All claims supported by traceable numbers, 3 clear contributions, fair baselines, honest limitations, and clean 1-page CARS introduction.
- **Weak Accept / Borderline**: Good empirical gains, but lacks statistical significance bounds or overstates generalization. Needs claim bounding.
- **Reject**: Unsubstantiated novelty claims ("better than all"), missing baseline ablations, data leakage, or confusing narrative structure.
