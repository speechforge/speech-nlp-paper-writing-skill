# SKILL_ID: DOMAIN::NLP_AND_AAC
META_VERSION: 1.0
DOMAIN_NAME: Natural Language Processing (NLP) for Speech and Assistive Communication (AAC)
SCOPE: Large language models for audio reasoning, discrete sound tokens, Augmentative and Alternative Communication (AAC), low-resource Indic language processing, and intent extraction from disordered speech
DEFAULT_FALLBACK: skills/default_speech_ai.md
INTERLOCKS_WITH: [DEFAULT_SPEECH_AI, DOMAIN::ASR_AND_ERROR_CORRECTION, DOMAIN::REASONING_AND_EVALUATION]
LAYER_POLICY: DELTA_AND_STRICT_OVERLAY
FORMAT_STYLE: KEY_VALUE_DENSE

## 1. IDENTITY_AND_DOMAIN_STANDARDS
CORE_CHALLENGE: Bridging linguistic representation models with acoustic signals to empower assistive communication, multilingual synthesis, and audio-text reasoning
STANDARD_BASELINES:
  FOUNDATION_LLMS: [LLaMA 3, Gemma 2, Mistral-7B, ByT5, Qwen2-Audio]
  SPEECH_LLMS: [AudioPaLM, SALMONN, SpeechGPT, Gemini Audio, Qwen-Audio]
  AAC_SYSTEMS: [Pictographic AAC, Scanning-based virtual keyboards, LLM predictive intent systems]
MANDATORY_METRICS:
  LANGUAGE_GENERATION: [BLEU (↑), ROUGE-L (↑), METEOR (↑), Perplexity (↓)]
  ASSISTIVE_USABILITY: [Keystroke Savings Rate (KSR %) (↑), Communication Rate (words/min) (↑), System Usability Scale (SUS) (↑)]
  SEMANTIC_FIDELITY: [Intent Classification Accuracy (↑), Semantic Cosine Similarity (↑)]

## 2. INTERLOCKING_WRITING_RULES
RULE_NLP_01_SOUND_TOKEN_DISCRETIZATION:
  PATTERN: When feeding audio into LLMs, formally specify the discrete token vocabulary size (e.g., 1024 or 4096 codebook vectors), frame rate (e.g., 50 Hz), and quantization method (RVQ / VQ-VAE)
  INTERLOCK: RULE_NLP_01_SOUND_TOKEN_DISCRETIZATION <-> DEFAULT::RULE_SEC_03_CONTRIB
  FEEDBACK_TRIGGER: IF Audio-LLM paper mentions sound tokens without codebook size and bitrate -> FLAG_NLP_TOKENIZER_VAGUE

RULE_NLP_02_AAC_CLINICAL_USABILITY_METRICS:
  PATTERN: AAC papers must evaluate practical user burden: report Keystroke Savings Rate (KSR) or Word Error Rate on intent prediction, not merely standard BLEU
  INTERLOCK: RULE_NLP_02_AAC_CLINICAL_USABILITY_METRICS <-> DOMAIN::DATASET_AND_CORPUS
  FEEDBACK_TRIGGER: IF AAC system evaluated solely on academic BLEU without clinical interaction metrics -> FLAG_NLP_AAC_METRIC_DEFICIT

RULE_NLP_03_LOW_RESOURCE_INDIC_TOKENIZATION:
  PATTERN: For Indic or morphologically rich low-resource languages, address subword fragmentation; evaluate byte-level (ByT5) vs script-specific BPE tokenizers
  INTERLOCK: RULE_NLP_03_LOW_RESOURCE_INDIC_TOKENIZATION <-> DEFAULT::RULE_SEC_05_REPRODUCIBILITY
  FEEDBACK_TRIGGER: IF Multilingual Indic model exhibits out-of-vocabulary UNK tokens -> FLAG_NLP_TOKENIZER_COLLAPSE

RULE_NLP_04_HALLUCINATION_AND_FACTUALITY_AUDIT:
  PATTERN: Measure generative hallucination rate when transforming telegraphic or dysarthric keyword inputs into full natural sentences
  INTERLOCK: RULE_NLP_04_HALLUCINATION_AND_FACTUALITY_AUDIT <-> DOMAIN::ASR_AND_ERROR_CORRECTION
  FEEDBACK_TRIGGER: IF Generative AAC model produces semantic drift from user intention -> FLAG_NLP_SEMANTIC_DRIFT

## 3. HIGHLIGHT_AND_BASELINE_BEATING_PATTERNS
VALUE_PROPOSITION_PATTERNS:
  - AAC_EFFICIENCY_GAIN: "Compared to traditional frequency-based predictive AAC systems, our LLM contextual assistant increases Keystroke Savings Rate (KSR) from 41.2% to 68.7%, reducing communication fatigue for users with motor impairments."
  - MULTIMODAL_AUDIO_REASONING: "Our sound-token tokenizer integrates seamlessly into LLaMA-3 without degrading text reasoning capabilities, achieving a 78.4% accuracy on sound-event QA benchmarks."
  - LOW_RESOURCE_GENERALIZATION: "By employing byte-level representations, the proposed model transfers phonetic knowledge across 12 Indic languages, reducing character error rate by 18.2% on unwritten dialects."

## 4. SECTION_BY_SECTION_LINE_ARCHITECTURE
SEC_I_INTRODUCTION:
  - Paragraph 1: Communication accessibility as a fundamental human right; challenges faced by individuals with speech/motor impairments
  - Paragraph 2: Conventional AAC limitations (slow typing rate, rigid vocabulary) or LLM audio hallucination
  - Paragraph 3: Proposed framework coupling LLM contextual understanding with multimodal speech/sound tokens
  - Paragraph 4: Quantified superiority in communication rate and semantic preservation
  - Paragraph 5: Exactly three contribution bullets

SEC_III_PROPOSED_FRAMEWORK:
  - Speech tokenizer / feature extractor architecture
  - LLM backbone conditioning and prompt formulation
  - Constrained decoding or semantic verification module

SEC_IV_EVALUATION_SETUP:
  - Clinical participant profiles (if evaluated with end-users) or benchmark corpora
  - Baseline communication interfaces and state-of-the-art NLP models
  - Usability metrics (KSR, SUS, communication speed in WPM)

SEC_V_RESULTS_AND_USER_STUDY:
  - Objective accuracy and text generation quality table
  - Human participant usability feedback and task completion times
  - Qualitative comparison of user intent versus expanded output sentences

SEC_VI_CONCLUSION:
  - Summary of communication speed and naturalness improvements
  - Ethical considerations regarding user agency and intent preservation

## 5. CONSTRUCTIVE_FEEDBACK_TRIGGERS
TRIGGER_NLP_01:
  CONDITION: IF Generative expansion model assumes user intent without verification step
  ACTION: Inject prompt: "[NLP_DOMAIN_AUDIT]: Implement user confirmation or intent verification mechanism in AAC dialogue flow."

TRIGGER_NLP_02:
  CONDITION: IF Indic speech NLP paper lacks dialectal or regional phonetic diversity analysis
  ACTION: Inject prompt: "[NLP_DOMAIN_AUDIT]: Report performance breakdown across regional accent variations."

## 9. INCREMENTAL_EVIDENCE
AUTO_EVIDENCE_BEGIN: TRUE
# Populated by scripts/update_skills_incremental.py when source papers are added.
AUTO_EVIDENCE_END: TRUE
