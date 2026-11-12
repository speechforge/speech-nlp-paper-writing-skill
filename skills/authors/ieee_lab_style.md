# SKILL_ID: AUTHOR::IEEE_LAB_STYLE
META_VERSION: 1.0
AUTHOR_NAME: IEEE-conference speech-lab style (generalised from published IEEE conference papers)
SCOPE: Classical and deep speech processing, acoustic phonetics, Teager energy analysis, speech enhancement, voice conversion, vocoders, and clinical speech
DEFAULT_FALLBACK: skills/default_speech_ai.md
INTERLOCKS_WITH: [DEFAULT_SPEECH_AI, DOMAIN::TTS_AND_VOCODERS, DOMAIN::ASR_AND_ERROR_CORRECTION, DOMAIN::DATASET_AND_CORPUS]
LAYER_POLICY: DELTA_AND_STRICT_OVERLAY
FORMAT_STYLE: KEY_VALUE_DENSE

## 1. IDENTITY_AND_LAB_ETHOS
LAB_STANDARDS: Speech Research Lab (SRL) conventions for IEEE conference papers
CORE_TRADEMARKS:
  ACOUSTIC_GROUNDING: Every deep learning architectural modification must be explained through acoustic-phonetic or signal-processing mechanics
  THREE_CONTRIBUTION_LAW: Exactly three contributions; bullet 1 = Architecture/Theory, bullet 2 = Empirical Validation, bullet 3 = Artifact/Demo release
  COMPARATIVE_ADJECTIVE_LAW: Zero tolerance for bare adjectives ("better", "faster", "higher"); every comparative must specify baseline and numeric delta
  CONFIDENCE_INTERVAL_LAW: All MOS/SMOS subjective listening tests must report ITU-T P.800 compliance, listener count, age, gender, and 95% confidence intervals ($_{\pm 0.12}$)
  GRANT_MANDATE: Mandatory MeitY project acknowledgment formatting
  FIGURE_RESOLUTION: Minimum 1600 DPI raster or vector PDF; IEEE PDF eXpress certified

## 2. INTERLOCKING_WRITING_RULES
RULE_IEEELAB_01_HEADING_TYPOGRAPHY:
  SECTIONS: Primary sections Roman numerals in full uppercase (`I. INTRODUCTION`, `II. PROPOSED METHODOLOGY`)
  SUBSECTIONS: Uppercase letter with period and Title Case (`A. Feature Extraction Pipeline`, `B. Teager Energy Operator`)
  SUBSUBSECTIONS: Arabic numeral with right parenthesis and run-in italic title (`1) Acoustic Conditioning:`)
  INTERLOCK: RULE_IEEELAB_01_HEADING_TYPOGRAPHY <-> DEFAULT::RULE_SEC_01_TITLE
  FEEDBACK_TRIGGER: IF Section heading not Roman uppercase -> FLAG_IEEELAB_HEADING_VIOLATION

RULE_IEEELAB_02_ABSTRACT_7_SENTENCES:
  FLOW:
    S1: Domain context and technological challenge in speech
    S2: Failure mode of prior signal processing or neural baselines
    S3: Proposed model name with explicit architectural mechanism
    S4: Database, sampling rates, windowing specs, and phonetic/linguistic diversity
    S5: Quantitative gain on objective metrics over identified baselines
    S6: Subjective test gain (MOS/SMOS) with ITU-T P.800 standard and CI
    S7: Reproducibility statement with supplementary audio URL
  INTERLOCK: RULE_IEEELAB_02_ABSTRACT_7_SENTENCES <-> DEFAULT::RULE_SEC_02_ABS
  FEEDBACK_TRIGGER: IF Abstract lacks demo URL OR missing confidence interval -> FLAG_IEEELAB_ABSTRACT_DEFICIT

RULE_IEEELAB_03_CONTRIBUTION_FORMAT:
  STRUCTURE:
    - `\textbf{Architectural Novelty:}` We propose [Name] incorporating [Mechanistic Principle] to resolve [Acoustic Failure].
    - `\textbf{Empirical Superiority:}` Extensive evaluations on [Corpus] demonstrate superior performance over [Baselines], achieving [PESQ/WER Delta].
    - `\textbf{Open Resources:}` Audio samples and pre-trained weights are publicly available at [URL].
  INTERLOCK: RULE_IEEELAB_03_CONTRIBUTION_FORMAT <-> DEFAULT::RULE_SEC_03_CONTRIB
  FEEDBACK_TRIGGER: IF Contribution bullets != 3 OR lack bold category tags -> FLAG_IEEELAB_CONTRIB_DEFICIT

RULE_IEEELAB_04_LISTENING_TEST_DEMOGRAPHICS:
  REQUIREMENT:
    STANDARD: "ITU-T P.800 recommendation for speech subjective quality assessment"
    POPULATION: "Evaluated by N listeners (M males, F females, age range X-Y years) with normal hearing acuity"
    ENVIRONMENT: "Conducted in a quiet laboratory environment using professional studio headphones (Sennheiser HD 280 Pro)"
    SCORING: "Scores presented as Mean Opinion Score (MOS) or Similarity MOS (SMOS) with 95% confidence intervals"
  INTERLOCK: RULE_IEEELAB_04_LISTENING_TEST_DEMOGRAPHICS <-> RULE_IEEELAB_05_TABLE_STANDARDS
  FEEDBACK_TRIGGER: IF Listening test lacks listener count OR demographic breakdown -> FLAG_IEEELAB_ETHICAL_LISTENER_OMISSION

RULE_IEEELAB_05_TABLE_STANDARDS:
  CAPTION_CASE: `TABLE II` followed by ALL UPPERCASE title placed ABOVE the table
  METRIC_NOTATION: Direction arrows mandatory for all metrics: `\textbf{PESQ}$(\uparrow)$`, `\textbf{MCD (dB)}$(\downarrow)$`, `\textbf{WER (\% prob)}$(\downarrow)$`
  CONFIDENCE_INTERVALS: Formatted as `$4.51_{\pm 0.12}$`
  STYLE: Three horizontal lines (`\toprule`, `\midrule`, `\bottomrule`), no vertical rules
  INTERLOCK: RULE_IEEELAB_05_TABLE_STANDARDS <-> DEFAULT::RULE_SEC_05_REPRODUCIBILITY
  FEEDBACK_TRIGGER: IF Table caption in lowercase OR lacks directional arrows -> FLAG_IEEELAB_TABLE_STYLE_ERROR

RULE_IEEELAB_06_HARDWARE_AND_TRAINING_SPECIFICATION:
  PATTERN: "All experiments were performed on an Ubuntu-powered workstation equipped with an Intel Core i9 processor, 128 GB RAM, and an NVIDIA RTX 4090 GPU (24 GB VRAM) using PyTorch 2.X and CUDA 12.X."
  INTERLOCK: RULE_IEEELAB_06_HARDWARE_AND_TRAINING_SPECIFICATION <-> DEFAULT::RULE_SEC_05_REPRODUCIBILITY
  FEEDBACK_TRIGGER: IF Hardware environment vague ("trained on a GPU") -> FLAG_IEEELAB_HARDWARE_VAGUE

RULE_IEEELAB_07_MEITY_FUNDING_ACKNOWLEDGMENT:
  EXACT_TEXT: "This work was supported by the Ministry of Electronics and Information Technology (MeitY), Government of India, under Project Grant ID: 11(1)/2022-HCC(TDIL)."
  INTERLOCK: RULE_IEEELAB_07_MEITY_FUNDING_ACKNOWLEDGMENT <-> DEFAULT::RULE_SEC_01_TITLE
  FEEDBACK_TRIGGER: IF MeitY grant cited with incorrect project code -> FLAG_IEEELAB_GRANT_MISMATCH

## 3. HIGHLIGHT_AND_BASELINE_BEATING_PATTERNS
HIGHLIGHT_BEATING_FORMULA:
  SIGNAL_DOMAIN_PROOFS: Connect performance gains directly to frequency-domain or time-domain acoustic phenomena (e.g., formant tracking, pitch continuity, high-frequency spectral envelope reconstruction).
  PARAMETRIC_ISOLATION: Compare models across window lengths (15 ms, 20 ms, 25 ms, 30 ms), window shapes (Hamming, Hann, Blackman), or acoustic frame rates.
  NOISE_SNR_CURVES: Show robustness curves from clean speech down to -5 dB, 0 dB, 5 dB, 10 dB SNR across white, babble, factory, and street noise.

## 4. SECTION_BY_SECTION_LINE_ARCHITECTURE
SEC_I_INTRODUCTION:
  - Paragraph 1: Speech communication importance, phonetic acoustic nature, speech signal properties
  - Paragraph 2: Historical context from source-filter theory and spectral analysis to modern neural vocoding/conversion
  - Paragraph 3: Specific bottleneck in baseline (e.g., quadratic attention complexity O(n^2d), phase distortion, poor prosodic control)
  - Paragraph 4: Introduction of the proposed system with physical intuition
  - Paragraph 5: Exactly three contribution bullets
  - Paragraph 6: Outline of remaining sections

SEC_II_RELATED_WORK:
  - Thematic organization into subsections A and B
  - Clear chronological progression showing why earlier acoustic features or models fall short

SEC_III_PROPOSED_METHOD:
  - Architectural overview diagram (vector graphic, min 1600 DPI, font-matched)
  - Mathematical formulation of each module with explicit symbol definitions
  - Loss formulation with balancing hyperparameters (\lambda)

SEC_IV_EXPERIMENTAL_SETUP:
  - Database details (sampling rate: 16 kHz or 22.05 kHz or 44.1 kHz, speaker count, duration, recording conditions)
  - Baseline architectures (exact citations and configuration)
  - Objective metrics (PESQ, STOI, MCD, UTMOS, FAD)
  - Subjective listening test (ITU-T P.800 with 95% CI)

SEC_V_RESULTS_AND_DISCUSSION:
  - Table of objective results with directional arrows
  - Table of subjective MOS/SMOS with 95% CI
  - Spectrogram visual analysis highlighting harmonic clarity and formant preservation
  - Discussion linking numbers to physical acoustics

SEC_VI_CONCLUSION:
  - Precise recap of quantitative superiority
  - Public demo link reminder
  - Future acoustic research avenues

## 5. SENTENCE_STRUCTURE_AND_VOCABULARY_BANK
CANONICAL_IEEELAB_SENTENCES:
  - "The effectiveness of speech recognition systems under degraded acoustic environments critically depends on the robustness of front-end feature representations."
  - "To mitigate spectral distortion in high-frequency regions, we introduce [Proposed], which leverages [Mechanistic_Feature]."
  - "The proposed framework yields a statistically significant improvement of [X.XX] dB in MCD and [Y.YY] in PESQ over the competitive baseline."
  - "Subjective evaluation conducted in accordance with ITU-T P.800 confirms that the proposed vocoder achieves an SMOS of 4.51_{\pm 0.12}, rivaling natural speech."

BANNED_LAB_PHRASES:
  - BANNED: "44 KHz" -> USE: "44.1 kHz"
  - BANNED: "ubuntu-powered" -> USE: "Ubuntu-powered"
  - BANNED: "listers" -> USE: "listeners"
  - BANNED: "capable to generate" -> USE: "capable of generating"
  - BANNED: "gives improved speech" -> USE: "gives improved speech quality" OR "yields higher quality speech"
  - BANNED: "UT-MOS" vs "UTMOS" -> USE: "UTMOS" consistently
  - BANNED: "discussion framework" -> USE: "diffusion framework"

## 6. CONSTRUCTIVE_FEEDBACK_TRIGGERS
TRIGGER_IEEELAB_01:
  CONDITION: IF MOS reported without ITU-T P.800 reference
  ACTION: Inject prompt: "[IEEELAB_LAB_AUDIT]: Cite ITU-T P.800 standard and report listener demographics (count, gender, normal hearing)."

TRIGGER_IEEELAB_02:
  CONDITION: IF Table caption placed below table OR in mixed case
  ACTION: Inject prompt: "[IEEELAB_LAB_AUDIT]: Place TABLE caption ABOVE table in ALL UPPERCASE letters."

TRIGGER_IEEELAB_03:
  CONDITION: IF Comparative adjective lacks explicit numerical delta
  ACTION: Inject prompt: "[IEEELAB_LAB_AUDIT]: Replace bare comparative with exact delta and baseline name."

## 9. INCREMENTAL_EVIDENCE
AUTO_EVIDENCE_BEGIN: TRUE
# Populated by scripts/update_skills_incremental.py when source papers are added.
AUTO_EVIDENCE_END: TRUE
