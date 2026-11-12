# SKILL_ID: DOMAIN::REASONING_AND_EVALUATION
META_VERSION: 1.0
DOMAIN_NAME: Audio Reasoning, Multimodal Perception Benchmarks, and Speech Evaluation Methodology
SCOPE: Sound token reasoning, audio-visual alignment (lip-sync, dubbing), automated speech quality prediction (UTMOS, DNSMOS, Proxy MOS), generative reward models (SpeechJudge-GRM), and rigorous listening test methodology
DEFAULT_FALLBACK: skills/default_speech_ai.md
INTERLOCKS_WITH: [DEFAULT_SPEECH_AI, DOMAIN::TTS_AND_VOCODERS, DOMAIN::ASR_AND_ERROR_CORRECTION]
LAYER_POLICY: DELTA_AND_STRICT_OVERLAY
FORMAT_STYLE: KEY_VALUE_DENSE

## 1. IDENTITY_AND_DOMAIN_STANDARDS
CORE_CHALLENGE: Developing principled, reproducible, human-calibrated evaluation protocols and multimodal reasoning models capable of fine-grained perceptual judgments
STANDARD_BASELINES:
  QUALITY_PREDICTORS: [UTMOS, DNSMOS P.835, NISQA, PAM-MOS, Proxy MOS, SpeechJudge-GRM]
  REASONING_MODELS: [Audio-LLaMA, SALMONN, Model-H, Gemini 1.5 Pro (Audio), Qwen2-Audio]
  STANDARD_SUBJECTIVE_TESTS: [ITU-T P.800 (ACR/MOS), ITU-R BS.1534 (MUSHRA), ITU-T P.808 (Crowdsourcing), ITU-T P.835]
MANDATORY_METRICS:
  PERCEPTUAL_CORRELATION: [Pearson correlation r (↑), Spearman rank correlation \rho (↑), Kendall's \tau (↑), RMSE (↓)]
  REASONING_ACCURACY: [Zero-shot QA Accuracy (↑), Macro F1 (↑), Temporal Alignment Error (ms) (↓)]
  STATISTICAL_RIGOR: [p-value reporting, 95% Confidence Intervals (\pm), Effect Size (Cohen's d)]

## 2. INTERLOCKING_WRITING_RULES
RULE_EVAL_01_CORRELATION_COMPLETENESS:
  PATTERN: When proposing automated perceptual metrics, always report BOTH linear correlation (Pearson r) and monotonic rank correlation (Spearman \rho) at both system-level and utterance-level
  INTERLOCK: RULE_EVAL_01_CORRELATION_COMPLETENESS <-> DEFAULT::RULE_SEC_04_METRICS
  FEEDBACK_TRIGGER: IF Metric paper reports Pearson r without Spearman \rho -> FLAG_EVAL_CORRELATION_INCOMPLETE

RULE_EVAL_02_SUBJECTIVE_ANCHOR_CALIBRATION:
  PATTERN: MUSHRA and subjective evaluation protocols must disclose anchor types: Hidden Reference (ground truth), Low Anchor (3.5 kHz low-pass filtered audio or degraded baseline), and Mid Anchor
  INTERLOCK: RULE_EVAL_02_SUBJECTIVE_ANCHOR_CALIBRATION <-> DEFAULT::RULE_SEC_04_METRICS
  FEEDBACK_TRIGGER: IF MUSHRA test omits low anchor or hidden reference -> FLAG_EVAL_ANCHOR_DEFICIT

RULE_EVAL_03_MULTIMODAL_TEMPORAL_GRANULARITY:
  PATTERN: For audio-visual alignment or dubbed content perception, measure synchronization at millisecond resolution (e.g., lip-sync offset \Delta t in ms)
  INTERLOCK: RULE_EVAL_03_MULTIMODAL_TEMPORAL_GRANULARITY <-> DOMAIN::DATASET_AND_CORPUS
  FEEDBACK_TRIGGER: IF Video-dubbing evaluation measures only overall audio quality without temporal lip-sync alignment -> FLAG_EVAL_TEMPORAL_MISALIGNMENT

RULE_EVAL_04_STATISTICAL_HYPOTHESIS_TESTING:
  PATTERN: All benchmark claims asserting superiority between systems must report formal hypothesis test statistics: e.g., "p < 0.001 using Wilcoxon signed-rank test with Bonferroni correction"
  INTERLOCK: RULE_EVAL_04_STATISTICAL_HYPOTHESIS_TESTING <-> DEFAULT::RULE_SEC_04_METRICS
  FEEDBACK_TRIGGER: IF Claim of superiority lacks p-value or significance test -> FLAG_EVAL_SIGNIFICANCE_UNSUBSTANTIATED

RULE_EVAL_05_LISTENER_SCREENING_DISCLOSURE:
  PATTERN: Document listener filtering criteria: gold-standard trap question pass rate, hearing acuity verification, headphone usage verification, and post-screening exclusion percentage
  INTERLOCK: RULE_EVAL_05_LISTENER_SCREENING_DISCLOSURE <-> DEFAULT::RULE_SEC_05_REPRODUCIBILITY
  FEEDBACK_TRIGGER: IF Crowdsourced listening test lacks worker screening protocol -> FLAG_EVAL_CROWD_UNFILTERED

## 3. HIGHLIGHT_AND_BASELINE_BEATING_PATTERNS
CORE_ARGUMENT_STRUCTURE:
  - BENCHMARK_OUTPERFORMANCE: "Model-H outperforms the strongest lip-reading foundation baseline by 52.0% in script-to-clip retrieval accuracy, demonstrating unprecedented cross-modal temporal sensitivity."
  - PERCEPTUAL_CORRELATION_LEAD: "On the VoiceMOS Challenge benchmark, our metric achieves an utterance-level Spearman correlation of \rho = 0.884, outperforming UTMOS (\rho = 0.821) by 0.063."
  - REWARD_MODEL_CALIBRATION: "SpeechJudge-GRM yields a 91.2% agreement rate with human expert preference annotations, exceeding scalar Bradley-Terry reward models by 14.5%."

## 4. SECTION_BY_SECTION_LINE_ARCHITECTURE
SEC_I_INTRODUCTION:
  - Paragraph 1: The evaluation crisis in speech and generative audio: conventional metrics (PESQ, MCD) fail on modern foundation models
  - Paragraph 2: Failure modes of existing judges: hallucination in speech LLMs, insensitivity to temporal misalignments, crowdsourcing bias
  - Paragraph 3: Proposed framework (model name, multi-task objective, hierarchical cross-modal architecture)
  - Paragraph 4: Quantified superiority in human correlation or reasoning accuracy
  - Paragraph 5: Exactly three contribution bullets

SEC_III_PROPOSED_BENCHMARK_OR_MODEL:
  - Cross-modal feature representation and tokenization
  - Architecture of the neural evaluator / reasoning judge
  - Loss formulation (ranking loss, contrastive alignment, or multi-task regression)

SEC_IV_EXPERIMENTAL_FRAMEWORK:
  - Benchmark datasets (VoiceMOS, AV-Speech, dubbing perception corpus)
  - Baseline metrics / models under comparison
  - Validation protocol and cross-validation partition design

SEC_V_RESULTS_AND_CORRELATION_ANALYSIS:
  - System-level and utterance-level correlation table (Pearson r, Spearman \rho, RMSE)
  - Scatter plots showing regression against human MOS with confidence bands
  - Ablation isolating unimodal versus multimodal perception branches
  - Qualitative error analysis of failure cases where automated judge disagrees with humans

SEC_VI_CONCLUSION:
  - Quantitative recap of benchmark accuracy
  - Guidelines for community adoption of the metric/benchmark
  - Open-source toolkit release statement

## 5. CONSTRUCTIVE_FEEDBACK_TRIGGERS
TRIGGER_EVAL_01:
  CONDITION: IF Paper proposes an evaluation metric without testing on an unseen out-of-domain speech corpus
  ACTION: Inject prompt: "[EVAL_DOMAIN_AUDIT]: Evaluate metric generalizability on an unseen out-of-domain speech dataset."

TRIGGER_EVAL_02:
  CONDITION: IF Subjective evaluation does not detail listener qualification traps
  ACTION: Inject prompt: "[EVAL_DOMAIN_AUDIT]: Detail listener screening traps and report listener exclusion percentage."

## 9. INCREMENTAL_EVIDENCE
AUTO_EVIDENCE_BEGIN: TRUE
# Populated by scripts/update_skills_incremental.py when source papers are added.
AUTO_EVIDENCE_END: TRUE
