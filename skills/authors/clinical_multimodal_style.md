# SKILL_ID: AUTHOR::CLINICAL_MULTIMODAL_STYLE
META_VERSION: 1.0
AUTHOR_NAME: Clinical, accented, and multimodal speech style (generalised from published papers)
SCOPE: Expressive TTS, cross-accent synthesis, disordered/dysarthric speech, non-parallel voice conversion, multimodal perception, and human dubbing benchmarks
DEFAULT_FALLBACK: skills/default_speech_ai.md
INTERLOCKS_WITH: [DEFAULT_SPEECH_AI, DOMAIN::TTS_AND_VOCODERS, DOMAIN::DATASET_AND_CORPUS, DOMAIN::REASONING_AND_EVALUATION]
LAYER_POLICY: DELTA_AND_STRICT_OVERLAY
FORMAT_STYLE: KEY_VALUE_DENSE

## 1. IDENTITY_AND_RESEARCH_ETHOS
PRIMARY_RESEARCH_PILLARS:
  CLINICAL_AND_ASSISTIVE_SPEECH: Disordered/dysarthric speech enhancement, speaker representation disentanglement, intelligibility vs timbre preservation
  EXPRESSIVE_AND_PROSODIC_TTS: Emotion regularization (Method-F), cross-accent speech synthesis (Model-E), adaptive oscillatory activations
  MULTIMODAL_PERCEPTION: Predicting human perception of AI-dubbed video/audio, Proxy MOS frameworks, audiovisual cross-modal fusion
  ABLATION_OBSESSION: Strict empirical isolation; every proposed loss term, module, and modal branch must undergo standalone ablation validation

## 2. INTERLOCKING_WRITING_RULES
RULE_CLINICAL_01_HYPOTHESIS_DRIVEN_PROPOSAL:
  STRUCTURE: Explicitly frame the architectural modification around a behavioral or perceptual hypothesis
  PATTERN: "We hypothesize that disentangling speaker identity from linguistic representations enables zero-shot accent transfer without timbre degradation."
  INTERLOCK: RULE_CLINICAL_01_HYPOTHESIS_DRIVEN_PROPOSAL <-> DEFAULT::RULE_SEC_03_CONTRIB
  FEEDBACK_TRIGGER: IF Architectural addition lacks an explicit hypothesis -> FLAG_CLINICAL_MISSING_HYPOTHESIS

RULE_CLINICAL_02_SYSTEMATIC_ABLATION_MANDATE:
  STRUCTURE: Must include dedicated subsection titled `Ablation Analysis` or `Ablation Experiments`
  COVERAGE:
    - Ablate each individual loss component (\mathcal{L}_{adv}, \mathcal{L}_{reg}, \mathcal{L}_{mel})
    - Ablate multimodal branches (Audio-only vs Visual-only vs Fused)
    - Tabulate degradation metrics with delta arrows
  INTERLOCK: RULE_CLINICAL_02_SYSTEMATIC_ABLATION_MANDATE <-> DEFAULT::RULE_SEC_04_RES
  FEEDBACK_TRIGGER: IF Multi-component system lacks ablation table -> FLAG_CLINICAL_ABLATION_ABSENT

RULE_CLINICAL_03_MULTIMODAL_PERCEPTION_SPECIFICATION:
  ALIGNMENT: Synchronize speech audio frame rates with video visual features (e.g., 25 fps video vs 50 fps mel-spectrogram)
  SUBJECTIVE_CALIBRATION: Report Pearson correlation coefficient (r) and Spearman rank correlation (\rho) against human subjective scores
  BENCHMARKING: Compare automated metrics (Proxy MOS) directly against ground-truth crowdsourced human annotations
  INTERLOCK: RULE_CLINICAL_03_MULTIMODAL_PERCEPTION_SPECIFICATION <-> DOMAIN::REASONING_AND_EVALUATION
  FEEDBACK_TRIGGER: IF Multimodal task lacks cross-modal temporal alignment description -> FLAG_CLINICAL_ALIGNMENT_UNSPECIFIED

RULE_CLINICAL_04_CLINICAL_AND_ACCENT_DISENTANGLEMENT:
  TERMINOLOGY: Clearly distinguish between `speaker timbre` (vocal tract identity), `prosody` (pitch, rhythm, duration), and `content` (phonemes/text)
  CLINICAL_METRICS: For dysarthric or disordered speech, report Word Error Rate (WER) alongside Phone Error Rate (PER) and Speaker Similarity MOS (SMOS)
  DATASET_SPLITS: Stratify test speakers strictly by severity level (Mild, Moderate, Severe) or regional accent dialect
  INTERLOCK: RULE_CLINICAL_04_CLINICAL_AND_ACCENT_DISENTANGLEMENT <-> DOMAIN::DATASET_AND_CORPUS
  FEEDBACK_TRIGGER: IF Dysarthric speech evaluated without severity stratification -> FLAG_CLINICAL_SEVERITY_UNSTRATIFIED

## 3. HIGHLIGHT_AND_BASELINE_BEATING_PATTERNS
BASELINE_SUPERIORITY_STRATEGY:
  MULTIDIMENSIONAL_WIN: Simultaneously demonstrate superior acoustic quality (PESQ/UTMOS), prosodic similarity (PCC/RMSE-F0), and speaker similarity (SMOS).
  EXEMPLAR_PATTERNS:

## 4. SECTION_BY_SECTION_LINE_ARCHITECTURE
SEC_I_INTRODUCTION:
  - Paragraph 1: Real-world communication stakes (assistive speech, dubbing, expressive conversational agents)
  - Paragraph 2: Entanglement or synchronization bottleneck in existing methods
  - Paragraph 3: Hypothesis-driven formulation of proposed framework
  - Paragraph 4: Exactly three crisp contribution bullets
  - Paragraph 5: Paper outline

SEC_II_RELATED_WORK:
  - Section A: Acoustic models and Voice Conversion
  - Section B: Disentangled representations / Multimodal perception models

SEC_III_PROPOSED_METHOD:
  - High-level modular architecture diagram (encoder, regularizer, adapter, decoder)
  - Formal loss functions with regularization weights
  - Disentanglement proof or objective alignment mechanics

SEC_IV_EXPERIMENTAL_SETUP:
  - Comprehensive dataset details (e.g., TORGO, IndicTTS, VCTK, proprietary dubbing corpus)
  - Acoustic feature parameters (mel filterbanks, hop length, window length)
  - Baseline model definitions and implementation parity assurance

SEC_V_RESULTS_AND_ABLATION:
  - Objective metrics table comparing proposed against baselines
  - Subjective listening tests with 95% confidence intervals
  - Formal `Ablation Analysis` isolating loss terms and modalities
  - Spectrogram or attention map visualization proving disentanglement

SEC_VI_CONCLUSION:
  - Quantitative recap of gains across intelligibility, similarity, and naturalness
  - Explicit discussion of current limitations and future clinical/multimodal directions

## 5. SENTENCE_STRUCTURE_AND_VOCABULARY_BANK
CANONICAL_CLINICAL_SENTENCES:
  - "In this paper, we propose regularizing emotion representations to prevent acoustic leakage across speaker identities."
  - "Entanglement in voice conversion is essential to accurately transfer prosodic nuance without corrupting linguistic intelligibility."
  - "We introduce Proxy MOS, a hierarchical cross-modal fusion architecture that predicts human perceptual dubbing quality."
  - "Ablation experiments reveal that removing the cross-attention layer degrades subjective naturalness by 0.28 MOS."

## 6. CONSTRUCTIVE_FEEDBACK_TRIGGERS
TRIGGER_CLINICAL_01:
  CONDITION: IF Clinical speech paper lacks severity-stratified results
  ACTION: Inject prompt: "[CLINICAL_AUDIT]: Partition test results across Mild, Moderate, and Severe dysarthria subgroups."

TRIGGER_CLINICAL_02:
  CONDITION: IF Proposed loss function has multiple terms (\mathcal{L}_1 + \mathcal{L}_2) without separate ablation
  ACTION: Inject prompt: "[CLINICAL_AUDIT]: Add ablation row demonstrating performance when \mathcal{L}_2 is disabled."

## 9. INCREMENTAL_EVIDENCE
AUTO_EVIDENCE_BEGIN: TRUE
# Populated by scripts/update_skills_incremental.py when source papers are added.
AUTO_EVIDENCE_END: TRUE
