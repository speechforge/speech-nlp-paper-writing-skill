# Speech Lab Style Guide
**Learned from**: *Model-A* (IEEE Conference A), *Model-B Vocoder* (IEEE Conference B), and *Benchmark-D* (ICASSP 2027).

---

## 1. Capitalization & Typography Conventions

### Title & Headings
- **Paper Title**:
  - In IEEE conference templates: Title Case with uppercase acronyms:
    *Example*: `Model-A: Learning Linear-Time Sequence Modeling with Selective State Spaces for Voice Conversion`
    *Example*: `Model-B: A Longformer-Based GAN Vocoder for Gujarati Language`
  - In LaTeX IEEEtran, titles often compile in all-caps or title case; retain hyphenated architecture naming (`Model-A`, `HiFi-GAN`, `BigVGAN`, `Fast Conformer`).
- **Major Section Headings**:
  - Roman Numerals in Small Caps / Uppercase:
    - `I. INTRODUCTION`
    - `II. RELATED WORK`
    - `III. PROPOSED ARCHITECTURE` (or `III. Model-A: PROPOSED APPROACH`)
    - `IV. EXPERIMENTAL SETUP` (or `IV. EXPERIMENTS`)
    - `V. RESULTS AND DISCUSSION`
    - `VI. FUTURE DIRECTIONS` (or `VI. CONCLUSION`)
    - `VII. CLOSING REMARKS`
    - `ACKNOWLEDGMENT`
    - `REFERENCES`
- **Subsection Headings**:
  - Capital letters with Title Case:
    - `A. Voice Conversion` / `A. Why Gujarati Language?` / `B. GANs Vocoders` / `C. Attention Mechanism`
    - `A. Dataset Used` / `B. Model Parameter Configuration` / `C. Setup`
    - `A. Subjective Measures` / `B. Objective Measures`
- **Sub-subsection / Metric Run-in Headings**:
  - Arabic numbers with right parenthesis followed by colon and bold title:
    - `1) PCC: It measures...`
    - `2) PESQ: It measures speech quality...`
    - `3) STOI: It is widely used to evaluate speech intelligibility...`
    - `4) MSD: It calculates the likeness or disparity...`
    - `5) MCD: It is used to quantify the variation...`
    - `6) F0-RMSE: It measures pitch contour deviation...`
- **Table Captions**:
  - Roman numerals in table label, caption in FULL UPPERCASE:
    - `TABLE I: COMPARATIVE ANALYSIS OF PHONEME, CONSONANT, AND VOWEL COUNTS ACROSS LANGUAGES. AFTER [19].`
    - `TABLE II: COMPARISON OF OBJECTIVE AND SUBJECTIVE MEASURES (REPORTED WITH 95% CI), ON SYNTHETIC AND GT FOR INDICVOICES-R DATASET`
  - Columns must display metric orientation arrows: `(↑)` for higher is better, `(↓)` for lower is better.
- **Figure Captions**:
  - Abbreviated as `Fig. 1.` followed by sentence case:
    - `Fig. 1. Comparison of raw speech waveform generation between (a) The proposed Model-B, and (b) the traditional GAN architecture.`

---

## 2. Author Affiliation & Metadata Formatting
- First authors with equal contribution marked with asterisk:
  ```latex
  \author{First Author$^{*,1}$, Second Author$^{*,1}$, and Third Author$^{1}$ \\
  $^{1}$Speech Research Lab, University, City, Country \\
  \texttt{\{id1, id2, id3\}@university.edu}}
  ```
- **Index Terms (Keywords)**:
  - Formatted with em-dash:
    `Index Terms—Voice Conversion (VC), Diffusion, Speaker Representation, Selective State-Space Models, Adversarial Speaker Regularization.`

---

## 3. Abstract Blueprint (The 7-Sentence Lab Formula)
The abstract follows an em-dash (`Abstract—`) and contains 150–220 words covering exactly seven logical moves:
1. **Task Definition & Broad Impact**: What is the core problem and why does it matter?
   - *"Voice Conversion (VC) modifies the speaker identity of speech while preserving its linguistic content. It has transformed the domains of voice dubbing, voice cloning, and assistive technologies..."*
2. **Current SOTA Bottleneck**: What is the architectural or mathematical limitation?
   - *"Recent advances in generative models, particularly diffusion-based frameworks, have significantly improved perceptual quality but come at a high computational cost and face challenges, including degraded prosody and reduced speech intelligibility. These primarily arise from attention-based sequence modeling, which scales quadratically $\mathcal{O}(n^2 d)$."*
3. **The Proposed Solution**: What is the proposed system name and core mechanism?
   - *"In this work, we propose Model-A, a selective state space (SS)-based hierarchical framework that replaces the attention mechanism with linear-time $\mathcal{O}(nd)$ sequence modeling."*
4. **Perceptual / Subjective Result**: Concrete score improvements with baselines.
   - *"In particular, the proposed approach achieves a NISQA-MOS of 3.90 (+0.02) and a UTMOS of 2.92 (+0.16), outperforming existing diffusion baselines in perceptual stability."*
5. **Objective & Acoustic Metrics**: Hard numbers on prosody, pitch, and intelligibility.
   - *"The proposed approach reduces F0 RMSE to 42.44, improving prosodic accuracy, while also improving intelligibility, with WER reduced to 18.14 and CER to 8.73 compared to DiffHier-VC."*
6. **Efficiency & Computational Reduction**: Real-Time Factor (RTF) and FLOPs reduction.
   - *"Furthermore, with 98% fewer computational resources, Model-A achieves a ~15.6% improvement in real-time factor (RTF 0.32 $\to$ 0.27), demonstrating that linear-time SS modeling enables faster inference without degrading speech quality."*
7. **Demo Utterances Link**: Publicly accessible GitHub Pages URL.
   - *"The demo utterances are publicly available at supplementary website: \url{https://example.github.io/demo/}."*

---

## 4. Section I: Introduction Architecture
1. **The Technical Tension (Paragraph 1)**:
   - Immediately frame the trade-off between perceptual speech quality and inference efficiency.
   - Point out specific audible degradation: robotic artifacts, chopped words/sounds, phase smearing, prosodic inconsistency, and speaker leakage during zero-shot transfer.
   - State the mathematical root cause: $\mathcal{O}(n^2 d)$ complexity of self-attention forcing models to use chunk-based processing, which breaks long-range prosodic dependencies.
2. **The Proposed Remedy (Paragraph 2)**:
   - Introduce the model name (*"In order to improve the quality of VC and trade-off between computational efficiency and perceptual quality of voice, we identified and addressed these issues..."*).
   - State the core mechanism (e.g., selective scan state-space models or Longformer sliding window + global attention).
3. **The Three Contribution Bullets**:
   Must follow this exact 3-part formula:
   - **Contribution 1 (Architectural / Algorithmic Proposal)**:
     - *"1) We proposed a Mamba-based sequential module for the source-filter and pitch encoder to reduce the quadratic ($\mathcal{O}(n^2 d)$) complexity of attention to lower-order ($\mathcal{O}(nd)$) using the selective scan mechanism."*
   - **Contribution 2 (Training Protocol & Evaluation Matrix)**:
     - *"2) Model-A was trained for only 0.2M steps with a batch size of 32 on an NVIDIA TITAN XP (12GB) with adversarial regularization... evaluated using more than 15 subjective, objective, quantitative measures (NISQA-MOS, UTMOS, PESQ, MCD, MSD, F0-RMSE, Fréchet Distance, CS, WER, CER) providing a detailed assessment against competitive baselines."*
   - **Contribution 3 (Quantitative Empirical Payoff)**:
     - *"3) Model-A reduces computations by 98%, improves real-time inference by 15.6% (RTF 0.32 $\to$ 0.27), lowers F0-RMSE to 42.44, and improves intelligibility with 18.15 WER and 8.73 CER while preserving speaker similarity (0.99)."*
4. **Roadmap Paragraph**:
   - *"The remaining part of the paper is organized as follows: Section II explores the related work in VC. Section III provides details on the proposed approach of Model-A, along with problem formulation. Section IV presents the experimental setup. Finally, Sections V and VI include the results, observations, and wrap up the paper with a conclusion, respectively."*

---

## 5. Section II: Related Work Architecture
Divide into 2–3 thematic subsections:
- **Subsection A (Core Domain & Phonetic Context)**:
  - If language-specific (e.g., Gujarati): Explain linguistic nuances (phoneme counts, consonants, vowels, retroflexes, G2P challenges, dialectal diversity across Kathiawar, North the region, Kutch, Central the region).
  - If speech conversion/synthesis: Contrast cycle-consistent GANs ($\mathcal{L}_{\text{cyc}}, \mathcal{L}_{\text{adv}}$) against diffusion models and explain where prosody breaks down.
- **Subsection B (Model Families)**:
  - Survey MelGAN, Parallel WaveGAN, HiFi-GAN, UnivNet, BigVGAN. Contrast implicit vs. explicit density models.
- **Subsection C (Sequence Modeling Mechanism)**:
  - Contrast standard Transformer self-attention ($\mathcal{O}(n^2 d)$) against linear alternatives (Mamba / Selective State Spaces, Longformer sliding window attention).

---

## 6. Section III: Proposed Architecture & Mathematical Formulation
- **Figure 1 Reference**:
  - Always contrast `(a) Proposed architecture` vs. `(b) Traditional baseline architecture`.
- **Equation Presentation**:
  - Formulate Query, Key, Value projection matrices: $W_i^Q, W_i^K, W_i^V$.
  - State local sliding window equations:
    $$\text{Head}_i = \text{Attention}(S_t W_i^Q, S_{t-w:t+w} W_i^K, S_{t-w:t+w} W_i^V)$$
  - State global attention heads:
    $$\text{Head}_j^{\text{global}} = \text{Attention}(X W_j^Q, X W_j^K, X W_j^V)$$
  - State multi-head concatenation with residual connection:
    $$Y = \text{Concat}(\text{Head}_1, \dots, \text{Head}_h) W^O + S$$
- **Define Every Variable**:
  - Immediately following each equation, explicitly state what each variable represents ($d_k$ dimensionality, $w$ window size, $h$ head count).

---

## 7. Section IV: Experimental Setup Architecture
Must include three clear subsections:
- **A. Dataset Used**:
  - Name the corpus (e.g., *IndicVoices-R Gujarati*, *VCTK*, *LJSpeech*).
  - Explicit metrics: total hours (e.g., 8.94 hrs), speaker count (45 speakers), average duration (9.74 s), sampling rate (44.1 kHz downsampled to 22.05 kHz or 16 kHz), acoustic representation (128 Mel bins, 1024 window, 256 hop size).
  - Nature of speech: distinguish extempore conversational speech from read speech.
- **B. Model Parameter Configuration**:
  - State transposed convolution upsampling rates (`[8, 8, 2, 2]`), kernel sizes (`[16, 16, 4, 4]`), ResBlock dilations (`[1, 3, 5]`), batch size, learning rate ($2 \times 10^{-4}$ with 0.999 decay), Adam momentum parameters ($\beta_1 = 0.8, \beta_2 = 0.99$).
- **C. Setup / Hardware**:
  - Explicit workstation specs:
    *"All experiments were executed on an Ubuntu-powered workstation equipped with a 12th generation Intel Core i7 processor, 16GB of RAM, and an MSI GTX 1080 ARMOR 8GB / NVIDIA TITAN XP (12GB) graphics card with 2TB external SSD for storage."*

---

## 8. Section V: Results and Discussion Architecture
Divide into Subjective and Objective subsections:
- **A. Subjective Measures (ITU-T P.800 Standard)**:
  - Explicit listener demographic reporting: 10 naive listeners, native speakers of the target language, age range (19–28 years), gender breakdown (8 male, 2 female), no hearing impairment, TestVox web platform.
  - Scale definition: 1 (Bad), 2 (Poor), 3 (Fair), 4 (Good), 5 (Excellent).
  - Arithmetic mean formula and 95% Confidence Interval (CI):
    $$\text{SMOS} = \frac{1}{N} \sum_{i=1}^N S_i$$
- **B. Objective Measures (Itemized with Formulas)**:
  - `1) PCC:` Pearson Correlation Coefficient formula.
  - `2) PESQ:` Perceptual Evaluation of Speech Quality formula ($4.5 - 0.1 d_{\text{sym}} - 0.0309 d_{\text{asm}}$).
  - `3) STOI:` Short-Time Objective Intelligibility formula.
  - `4) MSD:` Modulation Spectra Distance formula.
  - `5) MCD:` Mel Cepstral Distortion formula.
  - `6) F0-RMSE:` Pitch contour root-mean-square error formula.
- **Table II Layout**:
  - Method | PCC (↑) | PESQ (↑) | STOI (↑) | MSD (↓) | MCD (↓) | SMOS (↑)
  - Include Ground Truth (GT) row for reference calibration.
  - Report SMOS with 95% CI (e.g., $4.51 \pm 0.12$).
- **Discrepancy & Perceptual Analysis**:
  - Explain cases where objective metrics diverge from human listening ratings (e.g., BigVGAN scoring higher on spectral distance but listeners preferring Model-B due to excessive smoothing in BigVGAN).

---

## 9. Section VI & VII: Future Directions, Conclusion & Acknowledgment
- **Future Directions**:
  - Focus on prosodic control, edge optimization, and expanding to multi-accented corpora.
- **Closing Remarks / Conclusion**:
  - Summarize the architectural novelty and the balance between subjective naturalness and objective metrics.
- **Acknowledgment Format (MeitY Grant Standard)**:
  - *"This work is supported by the Ministry of Electronics and Information Technology (MeitY), Government of India, under Project Grant ID: 11(1)/2022-HCC(TDIL)."*

---

## 10. References & Bibliography Formatting Rules
- **Conferences**:
  `author, “Title,” in Booktitle (ACRONYM), pp. XXX–XXX, YYYY, City, Country.`
- **arXiv Preprints**:
  `author, “Title,” arXiv preprint arXiv:XXXX.XXXXX, YYYY {Last Accessed: Month Day, Year}.`
- **Journals**:
  `author, “Title,” Journal Name, vol. XX, no. X, pp. XXX–XXX, YYYY.`
- **Websites / Online Resources**:
  `author, “Title,” YYYY, [Online]. Available: https://... {Last Accessed: Month Day, Year}.`
