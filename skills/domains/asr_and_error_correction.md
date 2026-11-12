# SKILL_ID: DOMAIN::ASR_AND_ERROR_CORRECTION
META_VERSION: 1.0
DOMAIN_NAME: Automatic Speech Recognition (ASR) and Generative Error Correction
SCOPE: End-to-end ASR (Conformer, Whisper, Wav2Vec 2.0), LLM-based generative error correction, disordered/dysarthric speech recognition, low-resource speech, and acoustic model adaptation
DEFAULT_FALLBACK: skills/default_speech_ai.md
INTERLOCKS_WITH: [DEFAULT_SPEECH_AI, DOMAIN::NLP_AND_AAC, DOMAIN::DATASET_AND_CORPUS]
LAYER_POLICY: DELTA_AND_STRICT_OVERLAY
FORMAT_STYLE: KEY_VALUE_DENSE

## 1. IDENTITY_AND_DOMAIN_STANDARDS
CORE_CHALLENGE: Transcribing speech accurately across acoustic distortions, disordered articulations, and rare vocabulary, followed by phonetic-contextual error correction
STANDARD_BASELINES:
  ASR_FOUNDATION: [Whisper (base/large-v3), Conformer-CTC, Wav2Vec 2.0, MMS, Canary]
  ERROR_CORRECTION: [ByT5, BART-base, LLaMA-3-8B-Instruct, T5-ASR, Phonetic-BART]
STANDARD_BENCHMARKS: [LibriSpeech (test-clean / test-other), CHiME-6/7, TORGO, UASpeech, IndicSpeech]
MANDATORY_METRICS:
  ACCURACY: [Word Error Rate (WER %) (↓), Character Error Rate (CER %) (↓), Match Error Rate (MER %) (↓)]
  CORRECTION_INTEGRITY: [Correction Rate (CR %) (↑), Degradation Rate (DR %) (↓), Net Improvement (WIP %) (↑)]
  EFFICIENCY: [Latency (ms), Real-Time Factor (RTF) (↓), Model Parameter Count]

## 2. INTERLOCKING_WRITING_RULES
RULE_ASR_01_WER_METRIC_REPORTING:
  PATTERN: All WER/CER numbers must be reported with percentage signs and decimal precision: e.g., "WER of 14.2% on test-other"
  DIRECTION: Always append `(\downarrow)` in table headers: `\textbf{WER (\% prob)}$(\downarrow)$`
  INTERLOCK: RULE_ASR_01_WER_METRIC_REPORTING <-> DEFAULT::RULE_SEC_04_METRICS
  FEEDBACK_TRIGGER: IF Table reports WER without percentage symbol or direction arrow -> FLAG_ASR_WER_FORMAT_ERROR

RULE_ASR_02_CORRECTION_INTEGRITY_SAFEGUARD:
  PATTERN: Generative error correction models must report both positive corrections and catastrophic hallucinations (over-correction / degradation rate)
  FORMULA: Net WER Improvement = WER_{raw} - WER_{corrected}; Degradation Rate = (Number of correct tokens corrupted) / (Total correct tokens)
  INTERLOCK: RULE_ASR_02_CORRECTION_INTEGRITY_SAFEGUARD <-> DEFAULT::RULE_SEC_04_METRICS
  FEEDBACK_TRIGGER: IF Error correction paper claims WER reduction without reporting degradation rate -> FLAG_ASR_OVERCORRECTION_UNCHECKED

RULE_ASR_03_NORMALIZATION_AND_TEXT_PROCESSING:
  PATTERN: Explicitly define text normalization pipeline (e.g., lowercase conversion, punctuation removal, number expansion via Whisper-normalizer)
  REQUIREMENT: Same text normalizer must be applied identically to both hypothesis and reference text
  INTERLOCK: RULE_ASR_03_NORMALIZATION_AND_TEXT_PROCESSING <-> DEFAULT::RULE_SEC_05_REPRODUCIBILITY
  FEEDBACK_TRIGGER: IF ASR paper does not disclose text normalization rules -> FLAG_ASR_NORMALIZATION_VAGUE

RULE_ASR_04_ACOUSTIC_CONFIDENCE_CONDITIONING:
  PATTERN: When using LLMs for ASR correction, incorporate acoustic confidence scores (token logits or N-best lattices) to prevent hallucinations
  INTERLOCK: RULE_ASR_04_ACOUSTIC_CONFIDENCE_CONDITIONING <-> DOMAIN::NLP_AND_AAC
  FEEDBACK_TRIGGER: IF LLM corrects ASR transcripts without acoustic grounding -> FLAG_ASR_HALLUCINATION_RISK

RULE_ASR_05_CLINICAL_SPEECH_STRATIFICATION:
  PATTERN: For dysarthric speech (e.g., TORGO / UASpeech), report WER broken down by dysarthria severity: Very Low, Low, Medium, and High
  INTERLOCK: RULE_ASR_05_CLINICAL_SPEECH_STRATIFICATION <-> DOMAIN::DATASET_AND_CORPUS
  FEEDBACK_TRIGGER: IF Dysarthric ASR averages all speakers into a single WER -> FLAG_ASR_SEVERITY_CONFLATION

## 3. HIGHLIGHT_AND_BASELINE_BEATING_PATTERNS
CORE_ARGUMENT_STRUCTURE:
  - QUANTIFIED_WER_REDUCTION: "On the challenging TORGO dysarthric benchmark, [Proposed] reduces the average WER from 42.8% (Whisper-large-v3 baseline) to 28.4%, representing a 33.6% relative improvement."
  - ROBUSTNESS_TO_NOISE: "Under 0 dB babble noise, [System] maintains a WER of 11.2%, whereas the competitive Conformer baseline degrades to 24.6%."
  - RARE_WORD_CORRECTION: "By incorporating phonetic context into ByT5, our correction module recovers 68.4% of out-of-vocabulary medical terms corrupted by the first-pass ASR."

## 4. SECTION_BY_SECTION_LINE_ARCHITECTURE
SEC_I_INTRODUCTION:
  - Paragraph 1: ASR deployment in noisy, clinical, or accented real-world conditions
  - Paragraph 2: Limitations of first-pass decoders: acoustic ambiguity, rare word hallucination, phonetic collapse
  - Paragraph 3: Proposed system introducing phonetic conditioning, LLM error correction, or adaptive acoustic representations
  - Paragraph 4: Highlight of quantitative gains over Whisper/Conformer baselines
  - Paragraph 5: Exactly three contribution bullets

SEC_III_PROPOSED_SYSTEM:
  - First-pass acoustic model formulation (encoder-decoder or CTC/AED hybrid)
  - Error correction / adaptation pipeline architecture
  - Multi-task or confidence-weighted objective function

SEC_IV_EXPERIMENTAL_SETUP:
  - Speech corpus description and speaker-independent partitions
  - Language model and tokenizer details
  - Baseline model citations and evaluation protocols

SEC_V_RESULTS_AND_ANALYSIS:
  - Primary WER/CER results table with standard baselines
  - Severity-level breakdown table for clinical datasets
  - Error breakdown analysis (Substitutions, Deletions, Insertions)
  - Qualitative transcript examples illustrating successful phonetic recovery

SEC_VI_CONCLUSION:
  - Quantitative recap of WER gains
  - Latency and compute trade-off discussion
  - Future work on streaming or zero-shot multilingual adaptation

## 5. CONSTRUCTIVE_FEEDBACK_TRIGGERS
TRIGGER_ASR_01:
  CONDITION: IF Paper asserts ASR superiority without reporting statistical significance test (e.g., MAPSSWE test)
  ACTION: Inject prompt: "[ASR_DOMAIN_AUDIT]: Conduct NIST MAPSSWE or matched-pairs t-test to confirm statistical significance of WER reduction."

TRIGGER_ASR_02:
  CONDITION: IF Generative LLM error corrector replaces correct proper nouns
  ACTION: Inject prompt: "[ASR_DOMAIN_AUDIT]: Provide Named Entity Recognition (NER) accuracy and degradation rate analysis."

## 9. INCREMENTAL_EVIDENCE
AUTO_EVIDENCE_BEGIN: TRUE
# Populated by scripts/update_skills_incremental.py when source papers are added.
AUTO_EVIDENCE_END: TRUE
