# SKILL_ID: AUTHOR::VOCODER_BENCHMARK_STYLE
META_VERSION: 1.0
AUTHOR_NAME: Efficient multilingual vocoding and benchmark-reporting style (generalised from published papers)
SCOPE: Linear-time state space models (Model-A), multilingual neural vocoding (Model-C, Model-B), multidimensional vocoder evaluation (Benchmark-D), and lexical preservation studies
DEFAULT_FALLBACK: skills/default_speech_ai.md
INTERLOCKS_WITH: [DEFAULT_SPEECH_AI, AUTHOR::IEEE_LAB_STYLE, DOMAIN::TTS_AND_VOCODERS, DOMAIN::REASONING_AND_EVALUATION]
LAYER_POLICY: DELTA_AND_STRICT_OVERLAY
FORMAT_STYLE: KEY_VALUE_DENSE

## 1. IDENTITY_AND_RESEARCH_ETHOS
LAB_STANDARDS: Speech Research Lab (SRL) conventions for IEEE conference papers
CORE_TRADEMARKS:
  STATE_SPACE_AND_LINEAR_MODELS: Selective state space models (Mamba / SSM) replacing quadratic $O(n^2d)$ attention in voice conversion and vocoding
  MULTILINGUAL_INDIC_VOCODING: Explicit language and grapheme-adaptive conditioning (Model-C, Model-B) for low-resource Indic languages
  MULTIDIMENSIONAL_BENCHMARKING: Holistic evaluation (Benchmark-D) spanning acoustic fidelity, lexical preservation, prosody, speaker timbre, and inference latency
  IEEE_LAB_LAWS: Strict adherence to 7-sentence abstract flow, 3-part bold contributions, Table II with 95% CI and arrows, ITU-T P.800 standard, MeitY grant disclosure

## 2. INTERLOCKING_WRITING_RULES
RULE_VOCODER_01_ABSTRACT_EM_DASH_FORMULA:
  STRUCTURE: Exactly 7 sentences; Sentence 3 must feature an em-dash explaining the mechanistic bottleneck: "— to overcome the $O(n^2d)$ quadratic complexity of conventional attention —"
  INTERLOCK: RULE_VOCODER_01_ABSTRACT_EM_DASH_FORMULA <-> DEFAULT::RULE_SEC_02_ABS
  FEEDBACK_TRIGGER: IF Abstract lacks mechanistic em-dash explanation -> FLAG_VOCODER_ABSTRACT_FORMULA_ERROR

RULE_VOCODER_02_HARDWARE_AND_ENVIRONMENT_REPORTING:
  PATTERN: "All models were trained on an Ubuntu-powered workstation equipped with an Intel Core i9 processor, 128 GB RAM, and an NVIDIA RTX 4090 GPU (24 GB VRAM) using PyTorch 2.X and CUDA 12.X."
  BANNED: Never write "ubuntu-powered" (lowercase) -> MUST write "Ubuntu-powered"
  INTERLOCK: RULE_VOCODER_02_HARDWARE_AND_ENVIRONMENT_REPORTING <-> DEFAULT::RULE_SEC_05_REPRODUCIBILITY
  FEEDBACK_TRIGGER: IF Hardware environment omits GPU VRAM or capitalizes Ubuntu as lowercase -> FLAG_VOCODER_HARDWARE_ERROR

RULE_VOCODER_03_VOCABULARY_AND_UNIT_EXACTNESS:
  RULES:
    - SAMPLING_RATE: Always write "44.1 kHz" or "24 kHz" (lowercase k, uppercase H, lowercase z). NEVER write "44 KHz" or "24 KHz".
    - PREPOSITION: Write "capable of generating", NEVER "capable to generate".
    - TYPOGRAPHY: Ensure "listeners" is never typo'd as "listers".
    - ACRONYMS: Write "UTMOS" consistently (never "UT-MOS"). Write "Fréchet Audio Distance (FAD)" with accent.
  INTERLOCK: RULE_VOCODER_03_VOCABULARY_AND_UNIT_EXACTNESS <-> DEFAULT::RULE_SEC_01_TITLE
  FEEDBACK_TRIGGER: IF Paper contains "44 KHz" OR "capable to" -> FLAG_VOCODER_LEXICAL_VIOLATION

RULE_VOCODER_04_TABLE_CAPTION_AND_COLUMN_ARROWS:
  STRUCTURE: Table caption in ALL CAPS above table: `TABLE II` followed by caption text
  COLUMNS: Mandatory directional arrows: `\textbf{PESQ}$(\uparrow)$`, `\textbf{MCD (dB)}$(\downarrow)$`, `\textbf{WER (\% prob)}$(\downarrow)$`, `\textbf{UTMOS}$(\uparrow)$`
  CONFIDENCE_INTERVALS: Report as `$4.51_{\pm 0.12}$`
  INTERLOCK: RULE_VOCODER_04_TABLE_CAPTION_AND_COLUMN_ARROWS <-> DEFAULT::RULE_SEC_04_METRICS
  FEEDBACK_TRIGGER: IF Table caption in lowercase OR missing metric direction arrows -> FLAG_VOCODER_TABLE_VIOLATION

RULE_VOCODER_05_MEITY_AND_DEMO_PAGE_DISCLOSURE:
  GRANT_TEXT: "This work was supported by the Ministry of Electronics and Information Technology (MeitY), Government of India, under Project Grant ID: 11(1)/2022-HCC(TDIL)."
  DEMO_URL: "The demo utterances are publicly available at supplementary website: \url{https://...}"
  INTERLOCK: RULE_VOCODER_05_MEITY_AND_DEMO_PAGE_DISCLOSURE <-> DEFAULT::RULE_SEC_01_TITLE
  FEEDBACK_TRIGGER: IF MeitY grant or demo audio website omitted -> FLAG_VOCODER_REPRODUCIBILITY_DEFICIT

## 3. HIGHLIGHT_AND_BASELINE_BEATING_PATTERNS
CORE_BEATING_STRATEGIES:
  - LINEAR_COMPLEXITY_WIN: "Model-A reduces sequence modeling complexity from quadratic $O(n^2d)$ to linear $O(nd)$, achieving a 15.6% inference speedup and 22.3% lower memory footprint while outperforming diffusion baselines in speaker similarity."
  - MULTILINGUAL_INDIVIDUALITY: "Model-C consistently outperforms standard vocoders across 5 Indic languages, achieving a PESQ of 3.24 and cosine similarity of 0.9982, demonstrating that frame-synchronous grapheme modulation prevents phonetic collapse."
  - MULTIDIMENSIONAL_DIAGNOSTICS: "Benchmark-D exposes that vocoders optimized solely for PESQ exhibit catastrophic lexical word error rates (WER > 18%) on low-energy fricatives and nasals."

## 4. SECTION_BY_SECTION_LINE_ARCHITECTURE
SEC_I_INTRODUCTION:
  - Paragraph 1: Voice conversion or multilingual neural vocoding challenge in speech AI
  - Paragraph 2: Quadratic attention complexity $O(n^2d)$ or lack of linguistic-prosodic conditioning in existing vocoders
  - Paragraph 3: Proposed Model-A or Model-C architecture with theoretical intuition
  - Paragraph 4: Exactly three crisp contribution bullets
  - Paragraph 5: Paper organization outline

SEC_III_PROPOSED_METHOD:
  - High-level modular architecture diagram (>=1600 DPI, vector graphics)
  - Mathematical formulation of Selective State Space or Grapheme Adaptive Modulation
  - Composite loss function: $\mathcal{L}_{total} = \lambda_{mel}\mathcal{L}_{mel} + \lambda_{adv}\mathcal{L}_{adv} + \lambda_{fm}\mathcal{L}_{fm}$

SEC_IV_EXPERIMENTAL_SETUP:
  - Datasets (VCTK, IndicTTS, LJSpeech)
  - Baselines (HiFi-GAN, BigVGAN, Vocos, Diff-VC)
  - Hardware specifications (Ubuntu-powered, RTX 4090, 128 GB RAM)
  - Objective metrics and ITU-T P.800 subjective evaluation setup

SEC_V_RESULTS_AND_ABLATION:
  - Objective results Table II with directional arrows
  - Subjective SMOS/MOS results with 95% confidence intervals
  - Dedicated ablation study isolating selective state spaces or linguistic conditioning
  - Spectrogram Harmonic/Formant visualization at >=1600 DPI

SEC_VI_CONCLUSION:
  - Bounded summary of quantified gains
  - Supplementary audio demo link reminder
  - Future research on streaming vocoding and low-resource adaptation

## 9. INCREMENTAL_EVIDENCE
AUTO_EVIDENCE_BEGIN: TRUE
# Populated by scripts/update_skills_incremental.py when source papers are added.
AUTO_EVIDENCE_END: TRUE
