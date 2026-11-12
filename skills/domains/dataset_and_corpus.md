# SKILL_ID: DOMAIN::DATASET_AND_CORPUS
META_VERSION: 1.0
DOMAIN_NAME: Speech Corpus Design, Annotation Protocols, and Benchmark Datasets
SCOPE: Clinical/dysarthric speech corpora, multilingual & low-resource speech, AI-dubbing evaluation datasets, expressive speech databases, and audio-visual corpora
DEFAULT_FALLBACK: skills/default_speech_ai.md
INTERLOCKS_WITH: [DEFAULT_SPEECH_AI, DOMAIN::REASONING_AND_EVALUATION]
LAYER_POLICY: DELTA_AND_STRICT_OVERLAY
FORMAT_STYLE: KEY_VALUE_DENSE

## 1. IDENTITY_AND_DOMAIN_STANDARDS
CORE_CHALLENGE: Constructing reproducible, ethically consented, acoustically rigorous speech datasets with high-fidelity annotations for clinical or specialized AI research
STANDARD_BENCHMARKS_AND_REFERENCES: [TORGO, UASpeech, LibriSpeech, IndicTTS, CommonVoice, VCTK]
MANDATORY_DOCUMENTATION:
  ETHICS_AND_IRB: Institutional Review Board (IRB) or Ethics Committee approval ID and informed consent statement
  RECORDING_SETUP: Microphone models, acoustic isolation/booth specs, sampling rate (Hz), bit depth (16/24-bit), channel count
  DEMOGRAPHIC_BREAKDOWN: Total speakers, gender balance (M/F), age range, linguistic background, clinical severity distribution
  SPEAKER_INDEPENDENT_SPLITS: Train, validation, and test partitions must have disjoint speaker sets (zero speaker leakage)
  ANNOTATOR_AGREEMENT: Inter-annotator reliability metrics (Cohen's kappa \kappa, Fleiss' kappa, or Krippendorff's \alpha)

## 2. INTERLOCKING_WRITING_RULES
RULE_DATA_01_ETHICAL_AND_IRB_MANDATE:
  PATTERN: State institutional review board approval: "The data collection protocol was reviewed and approved by the Institutional Ethics Committee (IEC) under Protocol ID [XXX]. Written informed consent was obtained from all participants prior to recording."
  INTERLOCK: RULE_DATA_01_ETHICAL_AND_IRB_MANDATE <-> DEFAULT::RULE_SEC_01_TITLE
  FEEDBACK_TRIGGER: IF Human recording paper lacks IRB/consent disclosure -> FLAG_DATA_ETHICS_MISSING

RULE_DATA_02_SPEAKER_INDEPENDENT_PARTITIONING:
  PATTERN: "To prevent identity leakage, data splits are strictly speaker-independent: N_{train} speakers for training, N_{val} for validation, and N_{test} for testing, ensuring no overlap."
  INTERLOCK: RULE_DATA_02_SPEAKER_INDEPENDENT_PARTITIONING <-> DEFAULT::RULE_SEC_06_EXP
  FEEDBACK_TRIGGER: IF Train and test sets share identical speaker IDs -> FLAG_DATA_SPEAKER_LEAKAGE

RULE_DATA_03_INTER_ANNOTATOR_AGREEMENT_METRICS:
  PATTERN: When human perceptual scores (MOS, emotion, dubbing alignment) are collected, report inter-rater agreement: Fleiss' \kappa = 0.72 or Pearson r = 0.81 across annotators
  INTERLOCK: RULE_DATA_03_INTER_ANNOTATOR_AGREEMENT_METRICS <-> DOMAIN::REASONING_AND_EVALUATION
  FEEDBACK_TRIGGER: IF Subjective labels presented without agreement statistics -> FLAG_DATA_UNVERIFIED_LABELS

RULE_DATA_04_ACOUSTIC_SPECIFICATIONS:
  PATTERN: Explicitly specify room reverberation time (RT60), signal-to-noise ratio (SNR), microphone polar pattern, and audio format (.wav, uncompressed PCM, 48 kHz / 24-bit)
  INTERLOCK: RULE_DATA_04_ACOUSTIC_SPECIFICATIONS <-> DEFAULT::RULE_SEC_05_REPRODUCIBILITY
  FEEDBACK_TRIGGER: IF Recording hardware or acoustic specifications omitted -> FLAG_DATA_ACOUSTIC_VAGUE

RULE_DATA_05_BENCHMARK_MODEL_VERIFICATION:
  PATTERN: Dataset papers must establish baseline performance using at least three standard public models (e.g., Whisper, Conformer, VITS) on the new corpus
  INTERLOCK: RULE_DATA_05_BENCHMARK_MODEL_VERIFICATION <-> DEFAULT::RULE_SEC_04_METRICS
  FEEDBACK_TRIGGER: IF Dataset introduced without benchmarking standard models -> FLAG_DATA_BENCHMARK_MISSING

## 3. HIGHLIGHT_AND_BASELINE_BEATING_PATTERNS
VALUE_PROPOSITION_PATTERNS:
  - NOVELTY_OF_SCALE_OR_DOMAIN: "While existing clinical corpora like TORGO are restricted to [N] speakers and English only, our proposed corpus provides [M] hours across [K] Indic languages with fine-grained phonetic alignments."
  - ANNOTATION_PRECISION: "Unlike crowdsourced annotations prone to high noise, our multi-tier expert annotation achieves a Fleiss' kappa of 0.84, ensuring reliable benchmark ground truth."
  - MULTIMODAL_ALIGNMENT: "Every audio utterance is precisely synchronized with 4K video facial cues and phonetic transcripts at millisecond precision."

## 4. SECTION_BY_SECTION_LINE_ARCHITECTURE
SEC_I_INTRODUCTION:
  - Paragraph 1: The critical role of specialized speech data in overcoming AI bottlenecks (clinical, multimodal, low-resource)
  - Paragraph 2: Deficiencies of existing corpora (limited diversity, lack of severity annotations, copyright ambiguity)
  - Paragraph 3: Introduction of the new corpus with key statistics (hours, speakers, annotations)
  - Paragraph 4: Three contribution bullets (Corpus design, Annotation protocol, Open benchmark release)

SEC_II_CORPUS_DESIGN_AND_COLLECTION:
  - Participant recruitment, screening, and demographic stratification
  - Studio hardware, microphone array, and acoustic calibration
  - Prompt selection protocol (phonetically balanced sentences, emotional vignettes)

SEC_III_ANNOTATION_AND_QUALITY_CONTROL:
  - Multi-stage annotation pipeline (automatic alignment followed by manual correction)
  - Inter-annotator agreement statistics and conflict resolution protocol
  - Filtering criteria for acoustic distortions or clipping

SEC_IV_CORPUS_STATISTICS_AND_ANALYSIS:
  - Distribution histograms: duration per speaker, phoneme coverage, clinical severity scores
  - Comparative table against existing corpora in the literature

SEC_V_BASELINE_BENCHMARK_EXPERIMENTS:
  - Training and evaluating established open-source models on the new dataset
  - Identifying failure modes and research challenges exposed by the benchmark

SEC_VI_DATA_ACCESS_AND_ETHICS:
  - Licensing terms (e.g., CC-BY-NC 4.0), anonymization procedures, and repository download instructions

## 5. CONSTRUCTIVE_FEEDBACK_TRIGGERS
TRIGGER_DATA_01:
  CONDITION: IF Clinical or patient speech corpus does not document speaker consent procedures
  ACTION: Inject prompt: "[DATA_DOMAIN_AUDIT]: Provide formal patient consent and ethics committee authorization protocol."

TRIGGER_DATA_02:
  CONDITION: IF Dataset paper omits demographic breakdown table
  ACTION: Inject prompt: "[DATA_DOMAIN_AUDIT]: Add demographic table listing speaker count, age, gender, dialect, and hours."

## 9. INCREMENTAL_EVIDENCE
AUTO_EVIDENCE_BEGIN: TRUE
# Populated by scripts/update_skills_incremental.py when source papers are added.
AUTO_EVIDENCE_END: TRUE
