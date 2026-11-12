# Lab Rules: Scientific Paper Writing Principles

These rules are drawn from rigorous speech signal processing, audio, and ML research standards (ICASSP, Interspeech, IEEE/ACM Transactions on Audio, Speech, and Language Processing):

---

## 1. The Core Causal Argument Chain
Every scientific proposal and section must maintain an unbroken causal chain:
$$\text{Problem} \longrightarrow \text{Observed Failure} \longrightarrow \text{Proposed Response} \longrightarrow \text{Expected Effect} \longrightarrow \text{Empirically Designed Experiment} \longrightarrow \text{Bounded Conclusion}$$

- **Never report disconnected metrics**: A metric or observation without a causal hypothesis is mere benchmark reporting, not scientific contribution.
- **Observational results cannot establish architectural causality**: Showing that Model X scores higher on metric Y does not prove the architectural reason *why* without controlled ablation and isolation of variables.

---

## 2. The Three-Contribution Rule
Every conference paper (4–8 pages) must define **exactly two to four (ideally three) substantial, non-overlapping contributions**:
1. **Each contribution must have a formal operational definition**: What mathematical or conceptual construct is proposed?
2. **Each contribution must have a corresponding experiment or ablation**: A metric column or extra dataset is not automatically an additional contribution.
3. **No inflated contribution lists**: Bullet points in the introduction must be concise (at most 1–2 lines each), defensible, and directly verified in the Results section.

---

## 3. Strict Construct Definition and Naming
- **Name the measured construct first**: Always explain what a concept/metric measures (e.g., perceptual speech quality, temporal boundary distortion, acoustic invariance) *before* listing mathematical implementations or toolkits.
- **Separate established measurements from proposed methodology**:
  - Existing toolkits/metrics (e.g., UTMOS, NISQA, PESQ, STOI, MCD, MFA, ECAPA-TDNN) must be cited as external baselines or measurement tools.
  - Novel weights, transformations, aggregation rules, and boundary formulations must be clearly designated as the proposal.
  - An included predictor or score cannot independently validate its own composite.

---

## 4. Defensible Comparative Language (Comparative Adjective Law)
- **Forbidden unbacked adjectives**: Never use "better", "superior", "state-of-the-art", "drastic", "massive", or "unprecedented" without:
  1. A named, fair baseline;
  2. A declared dataset/profile and split;
  3. An independent evaluation criterion;
  4. An exact numerical effect size;
  5. Statistical uncertainty / confidence intervals or p-values.
- **Novelty claims ("First") require exhaustive verification**: Never claim "first to propose..." unless an exhaustive literature search explicitly proves it. Use defensible wording:
  - *Defensible current wording*: "We propose...", "We formulate...", "Under the tested protocol...", "Our results demonstrate that on Dataset X...".
  - *Wording requiring rigorous verification*: "universally optimal", "first to ever", "outperforms all existing methods".

---

## 5. Match Evidence Strictly to Scope
- **Domain specificity**: Multiple datasets establish breadth *only over those datasets*. Do not claim cross-domain generalization from clean in-domain datasets.
- **Out-of-Distribution (OOD)**: Requires clear proof of training-exposure isolation (unseen speakers, unseen acoustic environments, unseen languages).
- **Robustness**: Requires declared perturbation curves (SNR levels, reverberation times, clipping).
- **Efficiency & Latency**: Must declare the exact experimental unit: Architecture + checkpoint + frontend + sampler + precision + backend + hardware (e.g., PyTorch 2.4, CUDA 12.4, NVIDIA RTX 4090, batch size 1). Published speed numbers from different GPUs or batch sizes are background, not directly comparable benchmark results.

---

## 6. Structure Results in Claim Order
Organize experimental presentation strictly in claim order:
$$\text{Main Finding} \longrightarrow \text{Supporting Table / Figure} \longrightarrow \text{Interpretation} \longrightarrow \text{Targeted Ablation} \longrightarrow \text{Limitation}$$
- Installation, code adapters, directory hierarchies, and pipeline scripts belong in reproducibility appendices or repositories, never in the main four-page conference narrative.
- Keep disagreements transparent: If a baseline wins on one metric (e.g., PESQ) while the proposed method wins on another (e.g., MOS or latency), report and interpret the trade-off openly. Reviewers respect honest trade-off analysis far more than smoothed-over perfection.
