# Section-by-Section Writing Corrections, Rules & Lab Quality Standards
## Learned Line-by-Line from Model-A (IEEE Conference A) & Model-B (IEEE Conference B)

> [!NOTE]
> Every rule below is extracted directly from the actual published papers and the lab writing standards documented in Benchmark-D. Each rule includes the exact line from the paper, what is correct/wrong, and why.

---

## A. Title Page & Metadata Rules

### Rule A1: Title Capitalization
✅ **CORRECT**: Title Case with every major word capitalized. Acronyms stay uppercase. Hyphenated models preserve their case.
```
Model-A: Learning Linear-Time Sequence Modeling with Selective State Spaces for Voice Conversion
Model-B: A Longformer-Based GAN Vocoder for Gujarati Language
```
❌ **WRONG**: Sentence case in the title:
```
Model-A: learning linear-time sequence modeling with selective state spaces for voice conversion
```
**Why**: IEEE conference template renders title in UPPERCASE in the PDF, but the LaTeX source must still be in Title Case for proper compiled output with mixed-case model names (Model-A renders correctly; ALL-CAPS would break it).

### Rule A2: Author Line Format
✅ **CORRECT**:
```
First Author*, Second Author*, Third Author
```
- Middle initial with period: `M.`, `S.`, `A.`
- Equal-contribution asterisk `*` immediately after each name, no space
- Senior author (supervisor) listed **last**, no asterisk
- No "and" between authors — comma separated only

❌ **WRONG**:
```
First M Author, Second S Author, Third A Author  % Missing periods on initials
```

### Rule A3: Affiliation Format
✅ **CORRECT**:
```
Speech Research Lab, University, City, Country
```
- Full institution name first, followed by parenthetical former name
- City, Country (not State, Country for well-known cities)
- Email on next line in curly-brace format: `{student1id, student2id, supervisoremail}@domain.ac.in`

### Rule A4: Equal Contribution Footnote
✅ **CORRECT**: The asterisk footnote appears at the **bottom of column 1 on page 1**:
```
*Authors contributed equally to this work.
```
In LaTeX (IEEEtran):
```latex
\author{
  \IEEEauthorblockN{First Author\IEEEauthorrefmark{1}, 
                    Second Author\IEEEauthorrefmark{1}, 
                    Third Author}
  \IEEEauthorblockA{Speech Research Lab, University\\
                    City, Country\\
                    \{id1, id2, id3\}@university.edu}
  \thanks{\IEEEauthorrefmark{1}Authors contributed equally to this work.}
}
```

---

## B. Abstract — Exact Rules (Line by Line)

### Rule B1: em-dash Format (CRITICAL)
✅ **CORRECT**: `Abstract—` (em-dash, no spaces on either side)
❌ **WRONG**: `Abstract:`, `Abstract -`, `Abstract –` (en-dash)

In LaTeX: `\begin{abstract}` auto-generates this in IEEEtran. Do NOT manually type `Abstract—`.

### Rule B2: Sentence 1 — Task Definition
✅ **CORRECT** (Model-A):
```
Voice Conversion (VC) modifies the speaker identity of speech while preserving its linguistic content.
```
- Define the task with its full name first, then abbreviation in parentheses
- Active verb: "modifies", "converts", "generates" — not passive
- **One sentence only** — do not include applications in sentence 1

❌ **WRONG**: Opening with the application before the definition:
```
Voice conversion is used in dubbing and cloning applications to modify speaker identity.
```

### Rule B3: Sentence 2 — Application Impact (Optional Bridge)
✅ **CORRECT**:
```
It has transformed the domains of voice dubbing, voice cloning, and assistive technologies 
by improving the naturalness of the synthesized speech.
```
- Use "It has transformed" (present perfect) — not "It is used in"
- List 2–3 application domains separated by commas with Oxford comma
- End with the specific quality dimension being addressed (naturalness, intelligibility, efficiency)

### Rule B4: Sentence 3 — Current SOTA Bottleneck
✅ **CORRECT** (Model-A):
```
Recent advances in generative models, particularly diffusion-based frameworks, have significantly 
improved perceptual quality but come at a high computational cost and face challenges, including 
degraded prosody and reduced speech intelligibility.
```
- Use "Recent advances in..." as the opening (not "In recent years...")
- State the specific framework family (diffusion, GAN, Transformer)
- Use "but" to introduce the limitation
- List specific failure symptoms (degraded prosody, reduced intelligibility — NOT generic "poor quality")

> [!WARNING]
> **Missing from Model-A abstract**: The sentence says "which scales quadratically" but does NOT write the explicit complexity `O(n²d)`. **the lab standard**: Always write the mathematical complexity in the abstract if it is a core contribution.
> ✅ SHOULD BE: "which scales quadratically as $\mathcal{O}(n^2 d)$"

### Rule B5: Sentence 4 — The Proposal
✅ **CORRECT**:
```
In this work, we propose Model-A, a selective state space (SS)-based hierarchical diffusion 
framework that replaces the attention mechanism with linear-time O(nd) sequence modeling.
```
- Always open with "In this work, we propose..."
- Include the model name (capitalized exactly as it appears in the title)
- One-sentence description of the core mechanism
- Include the complexity improvement: "linear-time `O(nd)`"

> [!CAUTION]
> **BUG IN PAPER**: Model-A abstract says "hierarchical **discussion** framework" — this is a **typo**. It should be "hierarchical **diffusion** framework". This is a critical error that must be caught before submission.

### Rule B6: Sentences 5–6 — Quantitative Results (Hard Numbers)
✅ **CORRECT**:
```
In particular, the proposed approach (DiffHier-VC + Ours) achieves the NISQA-MOS of 3.90 (+0.02) 
and a UTMOS of 2.92 (+0.16), outperforming existing diffusion baselines in perceptual stability.
The proposed approach reduces F0 RMSE to 42.44, improving prosodic accuracy, while also improving 
intelligibility, with WER reduced to 18.14 and CER to 8.73 compared to DiffHier-VC.
```
- Format for improvement: `NISQA-MOS of 3.90 (+0.02)` — absolute value with delta in parentheses
- Always name the baseline: "compared to DiffHier-VC"
- Cluster by dimension: perceptual, prosodic, intelligibility — not randomly mixed
- Use metric acronyms in full first time, abbreviation thereafter

### Rule B7: Sentence 7 — Efficiency Result with RTF Arrow
✅ **CORRECT**:
```
Furthermore, with 98% fewer computational resources, Model-A achieves a ∼15.6% improvement 
in real-time factor (RTF), demonstrating that linear-time SS modeling enables faster inference 
without degrading the quality of the synthesized VC.
```
- Exact RTF notation: use `→` arrow in the contributions (body), percentage improvement in abstract
- "∼15.6%" for approximate values (tilde for approximation)
- End the efficiency sentence with a causal explanation: "demonstrating that..."

> [!WARNING]
> **BUG IN PAPER**: The abstract contains a redundant dangling sentence: "Model-A further reduces the RTF to achieve high-fidelity VC for practical deployment." — This repeats what was already said and adds no new information. **DELETE this sentence before submission.**

### Rule B8: Final Sentence — Demo URL
✅ **CORRECT**:
```
The demo utterances are publicly available at supplementary website: 
https://example.github.io/demo/
```
- Always the **last sentence** of the abstract
- Use `\url{}` in LaTeX
- Format: `The demo utterances are publicly available at supplementary website: \url{...}`
- Do NOT use "GitHub Pages", "our website", "our supplementary material" — use "supplementary website"

---

## C. Index Terms / Keywords Rules

### Rule C1: Format
✅ **CORRECT**:
```
Index Terms—Voice Conversion (VC), Diffusion, Speaker Representation, Selective State-Space Models, 
Adversarial Speaker Regularization.
```
- Keyword: `Index Terms—` (em-dash, no space after)
- Title Case for all terms
- Parenthetical short-forms allowed: `Voice Conversion (VC)`
- Comma-separated list ending with period
- 4–6 terms (not more than 6 for IEEE)
- Order: most specific → most general

❌ **WRONG**:
```
Keywords: voice conversion, diffusion, speaker representation  % "Keywords" not "Index Terms"; lowercase; no period
```

---

## D. Section I: Introduction — Line-by-Line Rules

### Rule D1: Section Heading Format
✅ **CORRECT**: `I. INTRODUCTION`
- Roman numeral, period, space, FULL UPPERCASE
- In LaTeX: `\section{Introduction}` → IEEEtran renders this automatically

### Rule D2: First Sentence — Problem Entry (NO FILLER)
✅ **CORRECT** (Model-A):
```
Despite the increasing capabilities of diffusion-based state-of-the-art (SOTA) frameworks, 
Voice Conversion (VC) systems still face critical limitations...
```
- Opens with "Despite..." — immediately acknowledging progress then pivoting to limitation
- Defines the full term `Voice Conversion (VC)` on first use even if abstract used it
- Uses "still face" — indicating persistent unsolved nature

❌ **WRONG**: Generic opener — "In recent years, deep learning has revolutionized voice conversion..." → the lab will reject this. Skip it entirely.

### Rule D3: Failure Mode Enumeration
✅ **CORRECT**:
```
...results in generated utterances that exhibit robotic speech, incorrect intonation, 
or chopped words/sounds.
```
- List **specific, perceptible** failure modes — not abstract ones
- Use "or" for the final item (Oxford comma not required in enumeration lists)
- Technical vocabulary: "speaker leakage", "prosodic inconsistency", "temporal coherence"

### Rule D4: Mathematical Complexity Statement
✅ **CORRECT**:
```
The fundamental bottleneck of current SOTA architectures is their reliance on attention-based 
mechanism, which has quadratic complexity.
```
> [!WARNING]
> This should explicitly state `O(n²d)`:
> ✅ **SHOULD BE**: "which has quadratic complexity `O(n²d)`" — without the LaTeX expression, it is too vague. The Introduction MUST contain the explicit complexity notation if it is a core contribution claim.

### Rule D5: Transition to Contributions
✅ **CORRECT** (Model-A):
```
In order to improve the quality of VC and trade-off between computational efficiency and 
perceptual quality of voice, we identified and addressed these issues. The following are 
main contributions of this paper:
```
> [!TIP]
> A cleaner formulation:
> ✅ **PREFERRED**: "To address these limitations, we propose Model-A. The key contributions of this paper are:"
> - "The following are main contributions" is grammatically weak — prefer "The key contributions... are:"

### Rule D6: Contribution 1 — Architectural Proposal
✅ **CORRECT FORMAT**:
```
1) We proposed a Mamba-based sequential module for the source-filter and pitch encoder to reduce 
   the quadratic (O(n²d)) complexity of the attention to a lower-order (O(nd)) using the selective 
   scan mechanism.
```
- Numbered list: `1)` (number + right parenthesis)
- Past tense: "We proposed" — because it was done
- State **what** was proposed, **why** (reduce complexity), **how** (selective scan mechanism)
- Include **both** complexities: `O(n²d)` → `O(nd)`

> [!NOTE]
> Some reviewers prefer present tense: "We propose" instead of "We proposed". In IEEE conference papers, **past tense** ("We proposed", "We evaluated") is acceptable and commonly used in this lab's papers.

### Rule D7: Contribution 2 — Training + Evaluation Matrix
✅ **CORRECT FORMAT**:
```
2) Model-A was trained for only 0.2M steps with a batch size of 32 on an NVIDIA TITAN XP (12GB), 
   with adversarial regularization... we thoroughly evaluated using more than 15 subjective, 
   objective, quantitative or performance measures, such as NISQA-MOS, UT-MOS, PESQ, MCD, MSD, 
   F0-RMSE, Frechet Distance, CS, WER, CER, and others.
```
> [!WARNING]
> **Issue in paper**: Contribution 2 mixes training details AND evaluation matrix in one bullet. These should be separated into:
> - **Contribution 2a**: Training + adversarial regularization (architecture/training novelty)
> - **Contribution 2b**: Evaluation matrix (evaluation novelty with 15+ metrics)
> OR keep together but restructure: state training first (1 sentence), then evaluation matrix (1 sentence).

> [!WARNING]
> **Consistency issue**: "UT-MOS" in contribution 2 vs "UTMOS" in the abstract. Pick one and use consistently throughout. The correct current name is **UTMOS** (not UT-MOS).

### Rule D8: Contribution 3 — Quantitative Payoff with RTF Arrow
✅ **CORRECT FORMAT**:
```
3) Model-A reduces the computations by 98%, and improves the real-time inference by 15.6% 
   (RTF 0.32→0.27), lowers the F0-RMSE to 42.44, and improves intelligibility with 18.15 WER 
   and 8.73 CER, by preserving the speaker similarity (0.99) in the synthesized utterance.
```
- RTF arrow notation: `RTF 0.32→0.27` (from value → to value)
- Specific numbers, NOT "improved significantly"
- Order: efficiency → prosody → intelligibility → speaker similarity (each dimension on separate clause)

### Rule D9: Roadmap Paragraph
✅ **CORRECT**:
```
The remaining part of the paper is organized as follows: Section II explores the related work in VC. 
Section III provides details on the proposed approach of Model-A, along with problem formulation. 
Section IV presents the experimental setup. Finally, Sections V and VI include the results, 
observations, and wrap up the paper with a conclusion, respectively.
```
- Opening: "The remaining part of the paper is organized as follows:"
- One sentence per section
- Use "explores" for Related Work, "provides" for Method, "presents" for Setup, "include the results... and wrap up" for Results+Conclusion
- "Finally," for the last one or two sections
- End with "respectively" if listing two things together

---

## E. Section II: Related Work — Line-by-Line Rules

### Rule E1: Subsection Heading Format
✅ **CORRECT**:
```
A. Voice Conversion
B. GANs Vocoders
C. Attention Mechanism
```
- Letter + period + space + Title Case
- **NOT** `A. VOICE CONVERSION` (not full caps for subsections)
- **NOT** `A) Voice Conversion` (no parenthesis for subsections)

### Rule E2: Opening the Subsection
✅ **CORRECT** (Model-A, Subsection A):
```
Earlier efforts in non-parallel VC used Generative Adversarial Networks (GANs) to mitigate 
the spectral oversmoothing caused by Mean Squared Error [1], [2].
```
- Open with "Earlier efforts..." or "Earlier work..." or "Prior work..."
- Define the category (non-parallel VC, GAN-based vocoders)
- Cite immediately after the claim: `[1], [2]`
- Comma-separated citations: `[1], [2]` (NOT `[1,2]` or `[1-2]` in IEEEtran — use `\cite{ref1, ref2}`)

### Rule E3: Loss Function Equation Format
When a loss function is introduced:
```
L_cyc = E_{x~P_X} [||G_{Y→X}(G_{X→Y}(x)) - x||_1],  (1)
to minimize the L1 distance between the original input x and its reconstruction through 
the target domain generator, G_{X→Y}, and source recovery generator, G_{Y→X}.
```
- Equation number on the **right**: `(1)`
- Explanation sentence immediately follows: "to minimize..."
- Define every symbol: "where x is..., G_{X→Y} is..."
- Use `\mathbb{E}_{x \sim P_X}` for expectation notation

### Rule E4: Citation Format
✅ **CORRECT**: `[1], [2]` for IEEE (sorted, comma-separated)
❌ **WRONG**: `(Wang et al., 2020)` — That is APA/author-date style, not IEEE

In LaTeX: Use `\cite{wang2020, kong2020}` → Renders as `[1], [2]` with IEEEtran

---

## F. Section III: Method — Line-by-Line Rules

### Rule F1: Subsection Naming Conventions
✅ **CORRECT** (Model-B):
```
III. Model-B: PROPOSED ARCHITECTURE
A. Sliding Windows
```
When the method has an acronym, include it in the section title: `III. Model-B: PROPOSED ARCHITECTURE`

### Rule F2: Mathematical Variable Definition Format
✅ **CORRECT** (Model-B):
```
For an input sequence S = {S_1, S_2, ..., S_n} (where S_t represents a speech frame or 
phoneme embedding at time step t), then attention mechanism is modified...
```
- Define variables inline in parentheses: `(where S_t represents...)`
- Use consistent subscript style throughout

After every equation, use "where," followed by variable definitions:
```
where W^Q_i, W^K_i, W^V_i are the learnable projection matrices for Query, Key, and Value.
```
- Italicize "where" is optional; lowercase is standard
- Semicolon between multiple variable definitions; period at end

### Rule F3: Complexity Notation in Text
✅ **CORRECT**:
```
reduces the second-order complexity of the self-attention computation to the lower-order (O(nd))
```
- Use `O(·)` with capital O for Big-O complexity
- Write in math mode: `$\mathcal{O}(n^2 d)$` or `$O(n^2 d)$`
- Always state **both**: the original complexity AND the improved complexity

### Rule F4: Equation Referencing in Text
✅ **CORRECT** (Model-B):
```
achieves a PESQ of 2.64 (as per eq. 10), STOI of 0.93 (as per eq. 11)
```
- Format: "as per eq. X" (lowercase "eq.", number without parentheses in running text)
- OR: "as given in Eq. (X)" — either form is acceptable; be consistent

---

## G. Section IV: Experimental Setup — Line-by-Line Rules

### Rule G1: Subsection Structure (Mandatory)
Every experimental setup section must have exactly these subsections:
```
A. Dataset Used
B. Model Parameter Configuration  
C. Setup
```
Alternative acceptable headings:
- `A. Dataset Used` / `A. Datasets`
- `B. Baseline Models` (if comparing)
- `B. Model Configuration` / `B. Implementation Details`
- `C. Setup` / `C. Hardware and Training Setup`

### Rule G2: Dataset Reporting Exact Format
✅ **CORRECT** (Model-B):
```
we used the IndicVoices-R Gujarati dataset, which includes a total of 8.94 hours of speech data 
from 45 speakers with an average duration of 9.74 seconds per utterance. The dataset was collected 
from the various districts of the state, India.
```
Mandatory items to report:
1. Dataset name (exact capitalization: IndicVoices-R, LJSpeech, LibriTTS, VCTK)
2. Total duration in hours (X.XX hours)
3. Number of speakers (X speakers)
4. Average utterance duration (X.XX seconds per utterance)
5. Original sampling rate (XX kHz)
6. Geographic/demographic details (from which districts/region)
7. Nature of speech: extempore conversational vs. read speech

> [!IMPORTANT]
> **Sampling Rate Format**:
> ✅ **CORRECT**: `22.05 kHz`, `16 kHz`, `44.1 kHz` (lowercase k in kHz)
> ❌ **WRONG in paper**: `44 KHz` — Must be lowercase k: `44.1 kHz` (and 44.1, not 44)

### Rule G3: Hyperparameter Reporting Format
✅ **CORRECT** (Model-B):
```
upsample rates [8,8,2,2], and a corresponding kernel size of [16,16,4,4] progressively. 
The training was conducted with 128 Mel bands spectrograms with a hop size of 256 and a 
Windows size of 1024. The batch size is limited to 8 on GTX 1080 ARMOR, learning rate of 
0.0002 with a decay factor of 0.999, and momentum parameters β_1 and β_2 were 0.8 and 0.99, respectively.
```
Mandatory hyperparameters to report:
- Upsample rates and kernel sizes (as arrays: `[8, 8, 2, 2]`)
- Number of Mel bands (`128`)
- Window size, hop size (in samples: `1024`, `256`)
- Batch size
- Learning rate (as decimal: `0.0002` or as scientific: `2 × 10⁻⁴`)
- Decay factor
- Optimizer momentum parameters: `β₁` and `β₂` values

> [!WARNING]
> **Issue in Model-B paper**: "Windows size of 1024" → should be "window size of 1024" (lowercase w, singular "window")

### Rule G4: Hardware Specification Sentence
✅ **CORRECT** (Model-B):
```
All experiments were executed on an ubuntu-powered workstation equipped with a 12th generation 
Intel Core i7 processor, 16GB of RAM, and an MSI GTX 1080 ARMOR 8GB graphics card with 
2TB external SSD for storage.
```
> [!WARNING]
> **Issue**: "ubuntu-powered" should be "Ubuntu-powered" (proper noun; OS name capitalized)

Mandatory hardware details:
- OS: "Ubuntu-powered workstation" or "Linux-based workstation"  
- CPU: Generation + model ("12th generation Intel Core i7")
- RAM: "16GB of RAM"
- GPU: Full model name + VRAM ("NVIDIA TITAN XP (12GB)" or "MSI GTX 1080 ARMOR 8GB")
- Storage (optional): "2TB external SSD"

### Rule G5: Footnote URL Format (Training Tools)
✅ **CORRECT** (Model-B):
```
Wav2Mel\footnote{\url{https://github.com/rhasspy/wav2mel.git}}
PESQ\footnote{\url{https://pypi.org/project/pesq/}}
```
- Footnote immediately after the tool name on first use
- Full URL in `\url{}`
- For GitHub: include `.git` suffix
- For PyPI: use `https://pypi.org/project/<package-name>/`

---

## H. Section V: Results and Discussion — Line-by-Line Rules

### Rule H1: Subsection Structure
```
V. RESULTS AND DISCUSSION
A. Subjective Measures
B. Objective Measures
```
Then within B, use run-in headings:
```
1) PCC: ...
2) PESQ: ...
3) STOI: ...
```

### Rule H2: Subjective Evaluation Listener Demographics (MANDATORY)
✅ **CORRECT** (Model-B):
```
we conducted a SMOS evaluation, according to ITU-T P.800 standard, by ensuring sufficient 
test duration and phonetic balance in test material [27]. All 10 subjects were naïve listeners 
with no prior training in speech or audio processing (e.g., age group of 19-28 years, gender 
distribution: 8 male, 2 female). Notably, all were native speakers of Gujarati, ensuring they 
could reliably judge the naturalness and intelligibility of synthesised Gujarati speech. None 
of the participants reported any hearing impairments or known biases toward the speech samples.
```
Mandatory fields:
1. Standard cited: `ITU-T P.800` (always cite the ITU-T standard)
2. Number of listeners: `10 subjects`
3. Listener type: `naïve listeners with no prior training in speech or audio processing`
4. Age range: `age group of 19-28 years`
5. Gender distribution: `8 male, 2 female`
6. Language expertise: `native speakers of Gujarati`
7. Hearing: `None reported hearing impairments`
8. Tool used: `TestVox web app [28]`

> [!NOTE]
> "naïve" (with umlaut) is the preferred academic spelling for "not trained". In LaTeX: `na\"ive` or `na\"{i}ve`.

### Rule H3: Listening Scale Definition
✅ **CORRECT** (Model-B):
```
where 5 represents excellent (clear and natural), 4 is good (acceptable), 3 is fair 
(noticeable degradation), 2 is poor (notable distortion), and 1 is bad (unacceptable or unintelligible).
```
- Always define all 5 scale points with both the word and parenthetical descriptor
- Format: `N label (description)`
- Order: 5 → 1 (best to worst)

### Rule H4: SMOS Formula Placement
✅ **CORRECT**:
```
we calculated the arithmetic mean (average) score of all ratings the listeners gave as per eq. 8.

SMOS = (1/N) Σ Si.    (8)
```
- Equation number in parentheses on right: `(8)`
- Equation label directly above the data table that uses the score
- Reference in text: "as per eq. 8" (before the equation)

### Rule H5: 95% CI Reporting
✅ **CORRECT** (Model-B):
```
95% Confidence Interval (CI) means 'true SMOS score is expected to lie with 95% certainty.'
...
Model-B (Proposed)  0.01  2.64  0.93  25.20  35.66  4.51 (±0.12)
```
- Define CI in text before the table
- Report as `4.51 (±0.12)` in the table cell or as `4.51 ± 0.12`
- In LaTeX table: `$4.51_{\pm 0.12}$`

### Rule H6: Results Discussion with Metric Disagreement Analysis
✅ **CORRECT** (Model-B):
```
We noted that BigVGAN [22] achieves the best overall performance in objective evaluations, 
closely followed by Model-B... but as per the SMOS results, the listeners rated BigVGAN [22] 
samples lower regardless of its strong objective performance, this variation is possible due 
to perceived excessive smoothing, and unconditioned accents in BigVGAN [22], which leads 
listeners to choose the generated samples from the Model-B model...
```
The lab requires:
- Acknowledge when a **baseline beats the proposed model** on some metric (BigVGAN beats Model-B on PESQ/MCD)
- Explain WHY there is a discrepancy between objective and subjective results
- Use perceptual/linguistic justification: "perceived excessive smoothing", "unconditioned accents"
- Do NOT hide inconvenient results

### Rule H7: Table Caption Format
✅ **CORRECT**:
```
TABLE II
COMPARISON OF OBJECTIVE AND SUBJECTIVE MEASURES (REPORTED
WITH 95% CI), ON SYNTHETIC AND GT FOR INDICVOICES-R DATASET
```
- `TABLE` in full capitals (not `Table`)
- Roman numeral: `TABLE II`
- Caption in FULL UPPERCASE
- Caption appears ABOVE the table data
- In LaTeX: `\caption{COMPARISON OF...}` before `\begin{tabular}`

### Rule H8: Table Column Header Format
✅ **CORRECT**:
```
Method | PCC (↑) | PESQ (↑) | STOI (↑) | MSD (↓) | MCD (↓) | SMOS (↑)
```
- Metric name + space + direction arrow in parentheses
- `↑` for higher-is-better, `↓` for lower-is-better
- In LaTeX: `\textbf{PESQ} $(\uparrow)$`
- Bold column headers: yes

### Rule H9: Run-in Metric Headings
✅ **CORRECT** (Model-B):
```
1) PCC: It measures the linear association between two signals x and y, with values ranging 
         from 1 (perfect positive) to -1 (perfect negative) [29].
2) PESQ: It measures speech quality. Higher PESQ ratings indicate high speech quality.
```
- Format: `N) NAME: Description.`
- Number + right parenthesis (not period): `1)`
- NAME in uppercase: `PCC`, `PESQ`, `STOI`
- Colon after name
- Short 1–2 sentence description
- Cite the original metric paper: `[29]`, `[30]`
- If formula follows, write it immediately after the description

---

## I. Conclusion / Closing Remarks / Future Directions — Rules

### Rule I1: Section Naming
labs use **two separate sections** for large papers:
```
VI. FUTURE DIRECTIONS
VII. CLOSING REMARKS
```
OR for 4-page papers, combine:
```
V. CONCLUSION
```

### Rule I2: Future Directions Content
✅ **CORRECT** (Model-B):
```
Our future improvements will focus on enhancing prosody control, optimizing computational 
efficiency for real-time application, and integrating mode-diverse linguistic datasets, 
especially for Gujarati.
```
- Specific future directions, not generic "future work"
- 2–4 sentences maximum
- Each direction must be motivated by a limitation in the current work

> [!WARNING]
> **Issue in Model-B**: The future directions section is too repetitive and verbose:
> ```
> "This work provides the robust foundation for future advancements in Indic language vocoders, 
> which are low-resource and complex to synthesize from the existing non-Indic pre-trained models, 
> which miss the important phonemes and mispredict the Indic phonemes with need more naturalness..."
> ```
> This run-on sentence needs to be shortened. The lab would want: One clean, forward-looking sentence per future direction.

### Rule I3: Closing Remarks / Conclusion Structure
✅ **CORRECT** (Model-B):
```
In this paper, we introduced Model-B, a longformer-based GAN vocoder for Gujarati speech synthesis. 
By integrating the sliding windows mechanism with a GANs-based vocoder, Model-B captures local 
phonetic details and long-range dependencies... The subjective and objective evaluation shows 
that the proposed work surpasses traditional vocoders...
```
- Opening: "In this paper, we introduced/proposed [Model Name], ..."
- 2–3 sentences summarizing the method and its core advantage
- 1–2 sentences summarizing the key quantitative results
- **Final sentence**: Forward-looking positive statement (never end with a limitation)

❌ **WRONG endings**:
- "Further research is needed to..."
- "We leave this as future work"
- "However, our method still has limitations in..."

---

## J. Acknowledgment — Exact Format

### Rule J1: Section Heading
✅ **CORRECT**: `ACKNOWLEDGMENT` (singular, no "S", FULL UPPERCASE)
❌ **WRONG**: `Acknowledgements`, `ACKNOWLEDGEMENTS`, `Acknowledgments` (with S)

> [!NOTE]
> IEEE uses "ACKNOWLEDGMENT" (American English, no S). Springer/LNCS uses "Acknowledgements" (British English, with S). Match the venue.

### Rule J2: MeitY Grant Format
✅ **CORRECT**:
```
This work is supported by the Ministry of Electronics and Information Technology (MeitY), 
Government of India, under Project Grant ID: 11(1)/2022-HCC(TDIL).
```
- Full ministry name first: "Ministry of Electronics and Information Technology"
- Abbreviation in parentheses: `(MeitY)`
- "Government of India" (not "GoI")
- "under Project Grant ID: X" (not "grant number" or "grant no.")
- One sentence only

---

## K. References — 25+ Specific Rules

### Rule K1: Conference Paper Format
✅ **CORRECT**:
```
[N] A. Author and B. Author, "Title of the Paper," in Proceedings of the Conference Name 
    (SHORT), pp. XXX–XXX, YYYY, City, Country.
```
Actual example (Model-B):
```
[3] A. Author et al., "Natural TTS synthesis by conditioning wavenet on Mel spectrogram 
    predictions," in IEEE International Conference on Acoustics, Speech and Signal Processing 
    (ICASSP), pp. 4779–4783, 2018, Calgary, Canada.
```

### Rule K2: arXiv Preprint Format
✅ **CORRECT**:
```
[N] A. Author, "Title of Paper," arXiv preprint arXiv:XXXX.XXXXX, YYYY {Last Accessed: Month Day, Year}.
```
Example (Model-B):
```
[7] A. Author, "Wavenet: A generative model for raw audio," arXiv preprint arXiv:1609.03499, 
    2016, {Last Accessed: March 16th, 2025}.
```
- Year as plain year, comma, then `{Last Accessed: Month Dayth, Year}` in curly braces
- Day uses ordinal superscript: `16th`, `1st`, `2nd`, `3rd`

### Rule K3: Journal Paper Format
✅ **CORRECT**:
```
[N] A. Author, "Title," Journal Name, vol. XX, no. X, pp. XXX–XXX, YYYY.
```
Example (Model-B):
```
[31] B. Author et al., "An algorithm for intelligibility prediction of time–frequency weighted 
     noisy speech," IEEE Transactions on Audio, Speech, and Language Processing, vol. 19, no. 7, 
     pp. 2125–2136, 2011.
```

### Rule K4: Title Capitalization in References
✅ **CORRECT**: Title Case for paper titles that are model names or proper nouns:
```
"MelGAN: Generative Adversarial Networks for Conditional Waveform Synthesis"
"HiFi-GAN: Generative Adversarial Networks for Efficient and High Fidelity Speech Synthesis"
```
> [!NOTE]
> In BibTeX: Use double braces `{{}}` around titles to preserve capitalization:
> `title = {{HiFi-GAN: Generative Adversarial Networks for Efficient and High Fidelity Speech Synthesis}}`

### Rule K5: Page Number Format
✅ **CORRECT**: En-dash between page numbers: `pp. 4779–4783`
❌ **WRONG**: Hyphen: `pp. 4779-4783` (use `--` in LaTeX which renders as en-dash)

### Rule K6: Conference Year + Location Format
✅ **CORRECT**: `YYYY, City, Country` after the pp.:
```
pp. 6199–6203, 2020, Barcelona, Spain.
pp. 3918–3926, 2018, Stockholm, Sweden.
pp. 28492–28518, 2023, Honolulu, Hawaii, USA.
```
- For US cities, include State abbreviation: `Honolulu, Hawaii, USA`
- For non-US cities, `City, Country` is sufficient: `Barcelona, Spain`

### Rule K7: "and others" vs "et al."
In BibTeX `author` fields:
- Use `and others` in BibTeX (NOT `et al.`):
  ```bibtex
  author = {Author, Anna and others}
  ```
- The LaTeX style file converts `and others` → `et al.` in the rendered output

### Rule K8: Author Name Format in BibTeX
✅ **CORRECT**: `Lastname, Firstname` format:
```bibtex
author = {Vaswani, Ashish and Shazeer, Noam and Parmar, Niki}
```
❌ **WRONG**: `Firstname Lastname` format (causes incorrect sorting):
```bibtex
author = {Ashish Vaswani and Noam Shazeer and Niki Parmar}
```

### Rule K9: BibTeX Key Format
Consistent key format: `firstauthorlastnameyearkeyword`
✅ **CORRECT**: `kong2020hifigan`, `yamamoto2020parallel`, `vaswani2017attention`
❌ **WRONG**: `HiFiGAN`, `parallel_wavegan`, `Vaswani2017`

### Rule K10: Duplicate Key Handling
> [!CAUTION]
> **Never have two entries with the same BibTeX key** (e.g., two `@inproceedings{baevski2020wav2vec}` entries, two `@inproceedings{rekesh2023fast}` entries). LaTeX will silently use only one and produce wrong references. 
> **Fix**: Use `baevski2020wav2vec_full` and `baevski2020wav2vec_short`, or just delete the duplicate.

### Rule K11: Workshop Papers
✅ **CORRECT**:
```
in Workshop on Speech and Language Processing for Assistive Technologies (SLPAT), 
pp. 72–78, 2015, Dresden, Germany.
```
- Use `in` before workshop/conference name
- Full name + (Acronym)

### Rule K12: Book Format
✅ **CORRECT**:
```
[N] A. Author and B. Author, Title of Book, Publisher, City, Year.
```
Example:
```
C. Author and D. Author, Speech and Language Processing: An Introduction to Natural Language 
Processing, Computational Linguistics, and Speech Recognition with Language Models, 
Pearson / Online Draft (3rd ed.), 2026.
```

### Rule K13: Wikipedia/Online Resource Format
✅ **CORRECT** (Model-B):
```
[18] Wikipedia contributors, "Gujarati language — Wikipedia, the free encyclopedia," 2024, 
     [Online; {Last Accessed: March 16th, 2025}]. [Online]. Available: 
     https://en.wikipedia.org/wiki/Gujarati_language
```

### Rule K14: Misc/Dataset Format
✅ **CORRECT**:
```
@misc{zheng2024saphypo5,
  author       = {Zheng, Xiuwen and others},
  title        = {{SAP-Hypo5: A Benchmark Dataset for Dysarthric Speech Error Analysis}},
  howpublished = {Hugging Face Repository},
  year         = {2024 \{Last Accessed Date: November 11$^{\mathrm{th}}$, 2026\}}
}
```

### Rule K15: `@misc` vs `@article` for arXiv
- Use `@article` for arXiv preprints (more information available)
- Use `@misc` for datasets, software tools, and online resources

---

## L. Figure Quality & Image DPI Requirements

> See companion file `08_figure_dpi_and_latex_quality.md` for complete details.

### Quick Reference:
- **Minimum DPI**: 1600 DPI for all raster images (PNG, TIFF)
- **Preferred**: Vector PDF/EPS for all diagrams and plots
- **Figure placement**: `[t]` (top-of-page) in IEEEtran
- **Figure 1**: Top-right column of Page 1 in 2-column layout
- **Caption format**: `Fig. 1.` (abbreviated, with period, then sentence case)
- **Tables**: Caption ABOVE in FULL UPPERCASE with Roman numeral identifier

---

## M. Mathematical Notation Consistency Rules

### Rule M1: Equation Numbering
- Number ALL equations, even inline ones if referenced later
- In LaTeX: use `\begin{equation}...\end{equation}` for numbered equations
- For unnumbered: `\begin{equation*}...\end{equation*}`

### Rule M2: Equation Referencing in Text
✅ **CORRECT options** (use ONE consistently):
- "as per eq. 8" (lowercase, no parentheses)
- "as given in Eq. (8)" (capitalized, with parentheses)
- "(see Eq. (8))"

❌ **WRONG**: Mixing styles within the same paper

### Rule M3: Complexity Notation
✅ **CORRECT**: 
- In text: `O(n²d)` or `$\mathcal{O}(n^2 d)$`
- Preferred: `$\mathcal{O}(n^2 d)$` (calligraphic O, standard academic notation)

### Rule M4: Variable Fonts
- Scalars: italic `x`, `y`, `d`
- Vectors: bold lowercase `**x**`, `**y**` or `$\mathbf{x}$`
- Matrices: bold uppercase `$\mathbf{W}$`
- Sets: calligraphic `$\mathcal{X}$`, `$\mathcal{Y}$`

---

## N. 25 Specific Writing Issues to Correct (Found in These Papers)

| # | Issue Found | Location | Correction |
|---|---|---|---|
| 1 | "hierarchical **discussion** framework" | Model-A Abstract | Should be "hierarchical **diffusion** framework" (critical typo) |
| 2 | Duplicate sentence: "Model-A further reduces the RTF..." | Model-A Abstract, last 2 sentences | Delete the duplicate sentence entirely |
| 3 | "which scales quadratically" (no complexity notation) | Model-A Abstract | Add: "which scales quadratically as $\mathcal{O}(n^2 d)$" |
| 4 | "UT-MOS" in Contribution 2, "UTMOS" in Abstract | Model-A | Use "UTMOS" consistently throughout |
| 5 | Contribution 2 mixes training + evaluation matrix | Model-A | Separate into two focused contribution bullets |
| 6 | "The following are main contributions of this paper:" | Model-A | Prefer: "The key contributions of this paper are:" |
| 7 | "nMOS" (not defined) | Model-A Contribution 2 | Define: "nMOS (normalized MOS)" or use "MOS" |
| 8 | "ubuntu-powered" | Model-B Setup section | Should be "Ubuntu-powered" (capitalized proper noun) |
| 9 | "44 KHz" (incorrect capitalization and value) | Model-B Dataset section | Should be "44.1 kHz" (lowercase k, correct value 44.1) |
| 10 | "listers" (typo) | Model-B Results section | Should be "listeners" |
| 11 | "Synthesis quality of synthesized samples" (repetitive) | Model-B Results: "assess the synthesized quality of synthesized samples" | "assess the perceptual quality of synthesized samples" |
| 12 | "Windows size" | Model-B Model Config | "window size" (lowercase w, singular) |
| 13 | "GAN [18]" citing Wikipedia for GAN | Model-B Related Work | Should cite Goodfellow et al. (2014) NeurIPS paper |
| 14 | "attends to a fixed window size w around it instead" (line break issue in text) | Model-B Architecture section | Rewrite for clean sentence structure |
| 15 | "gives improved speech generation quality" (incorrect subject-verb agreement) | Model-B Introduction | "give improved speech generation quality" |
| 16 | "Author et al. [7] proposed the autoregressive... WaveNet, which model the waveform" | Model-B Introduction | "which models the waveform" (singular subject-verb) |
| 17 | "while NAR models were faster but demonstrated reduced speech quality" | Model-B Introduction | Tense inconsistency — use past tense consistently: "were" is correct here |
| 18 | "Similarly, diffusion-based vocoders [14], [15], capable to generate high-quality speech" | Model-B Introduction | "capable of generating" (not "capable to generate") |
| 19 | "In 2017, the work proposed by Vaswani et al. [16] proposed" | Model-B Related Work | "In 2017, Vaswani et al. [16] proposed" (redundant "work proposed by...proposed") |
| 20 | Missing: Frechet Distance definition in contribution 2 metrics list | Model-A | Either define FD or expand to "Fréchet Inception Distance (FID)" |
| 21 | "Authorized licensed use limited to: DA IICT..." running into text | Both papers (PDF extraction artifact) | This is a watermark from IEEE Xplore — not an error in the original LaTeX |
| 22 | F0-RMSE values: 42.44 in abstract vs 42.44 in Contribution 3 (consistent ✓) | Model-A | No issue — values are consistent |
| 23 | Missing explicit ablation study | Both papers | the lab requires ablation that isolates each component's contribution — add a table showing: "without Mamba module" vs "with Mamba module" |
| 24 | "mode-diverse linguistic datasets" | Model-B Future Directions | Unclear — should be "multi-dialectal linguistic datasets" |
| 25 | "To the best of our understanding and belief, no prior work integrates..." | Model-B | Acceptable hedge phrase but verbose — prefer "To the best of our knowledge, no prior work integrates..." |

---

## O. LaTeX Compilation & Submission Rules

### Pre-Submission Search Commands
```bash
# Check for placeholder text:
grep -n "TODO\|TBD\|PENDING\|XX\|??\|placeholder" paper.tex

# Check for pending macros:
grep -n "\\\\pending\|\\\\tbd\|\\\\draftnote\|\\\\todo" paper.tex

# Check for overfull/underfull boxes:
grep -c "Overfull\\|Underfull" paper.log

# Count pages:
pdfinfo paper.pdf | grep "Pages:"

# Check figure resolution (for PNG files):
identify -verbose figure.png | grep "Resolution\|Print size"

# Verify font embedding:
pdffonts paper.pdf | grep -v "yes" | grep -v "emb"
```

---

## P. The 35-Item Pre-Submission Checklist

### Title & Authors
- [ ] Title is Title Case with correct acronym capitalization (Model-A not Model-A)
- [ ] All author initials have periods (M. not M)
- [ ] Affiliation includes city and country
- [ ] Equal contribution asterisk footnote placed correctly

### Abstract
- [ ] Opens with `Abstract—` (em-dash, no space)
- [ ] No "In recent years, deep learning has..." opener
- [ ] Proposal identified with model name in sentence 3–4
- [ ] Explicit complexity notation: `O(n²d)` and `O(nd)`
- [ ] All numbers consistent with Introduction and Tables
- [ ] RTF arrow notation if applicable: `RTF 0.32→0.27`
- [ ] Final sentence is supplementary website URL
- [ ] No duplicate/redundant sentences

### Introduction
- [ ] "The key contributions of this paper are:" (not "following are main contributions")
- [ ] 3 contributions (not 2, not 4–6)
- [ ] Each contribution is 3–5 lines (not longer)
- [ ] Roadmap paragraph present
- [ ] No generic filler openers

### Related Work
- [ ] 2–3 thematic subsections
- [ ] Each subsection opens with "Earlier efforts..." or "Prior work..."
- [ ] Loss functions defined with equations for cited methods
- [ ] Citations in `[N]` format (not `(Author, Year)`)

### Method
- [ ] Figure 1 contrasts proposed vs. baseline
- [ ] Every equation numbered
- [ ] Every variable defined immediately after first use
- [ ] Complexity stated for both original and improved

### Experiments
- [ ] Dataset: hours, speakers, duration, Hz, Mel bands all reported
- [ ] Hardware: GPU model, VRAM, CPU generation all reported
- [ ] All hyperparameters reported
- [ ] "kHz" (lowercase k) used throughout

### Results
- [ ] ITU-T P.800 cited for listening studies
- [ ] 10 listeners, age range, gender, native speaker status all reported
- [ ] All 5 scale points defined (1-Bad to 5-Excellent)
- [ ] 95% CI reported for SMOS
- [ ] Table caption in FULL UPPERCASE above table
- [ ] ↑/↓ arrows in all column headers
- [ ] GT row included in table
- [ ] Best results bolded
- [ ] Metric disagreements discussed openly

### References
- [ ] No duplicate BibTeX keys
- [ ] All conference refs: venue + pp. + year + city + country
- [ ] All arXiv refs: `{Last Accessed: Month Dayth, Year}` format
- [ ] All URLs: `\url{}` command
- [ ] No `et al.` in BibTeX `author` field (use `and others`)

### Figures & PDF
- [ ] All raster figures ≥ 1600 DPI
- [ ] All diagrams exported as vector PDF
- [ ] No Overfull hboxes in log
- [ ] Page count within limit
- [ ] No TODO/TBD/PENDING text in PDF
- [ ] Fonts embedded (pdffonts shows "yes" for all)
