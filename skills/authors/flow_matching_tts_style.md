# SKILL_ID: AUTHOR::FLOW_MATCHING_TTS_STYLE
META_VERSION: 1.0
AUTHOR_NAME: Flow-matching TTS and audio-reasoning style (generalised from published papers)
SCOPE: Modern speech synthesis, Conditional Flow Matching (CFM), non-autoregressive acoustic modeling, audio foundation models, audio reasoning with sound tokens, and rigorous evaluation methodology
DEFAULT_FALLBACK: skills/default_speech_ai.md
INTERLOCKS_WITH: [DEFAULT_SPEECH_AI, DOMAIN::TTS_AND_VOCODERS, DOMAIN::NLP_AND_AAC, DOMAIN::REASONING_AND_EVALUATION]
LAYER_POLICY: DELTA_AND_STRICT_OVERLAY
FORMAT_STYLE: KEY_VALUE_DENSE

## 1. IDENTITY_AND_RESEARCH_ETHOS
PRIMARY_RESEARCH_PILLARS:
  FLOW_MATCHING_AND_DIFFUSION: Pioneering Conditional Flow Matching (CFM) with Optimal Transport (OT) paths for high-speed, non-autoregressive speech synthesis (Matcha-TTS)
  PARETO_OPTIMALITY: Quality vs latency trade-off mastery; models must be both perceptually superior AND significantly faster in Real-Time Factor (RTF)
  AUDIO_REASONING_AND_LLMS: Discrete sound tokens, generative reward models (SpeechJudge-GRM), audio-visual alignment (Model-H)
  CRITICAL_MOS_SKEPTICISM: Methodological rigor in TTS evaluation; challenging uncalibrated MOS tests, advocating MUSHRA, CCR, and anchored comparisons
  OPEN_SOURCE_DEPLOYABILITY: Ready-to-deploy offline robotics pipelines, PyTorch/ONNX releases, pip-installable toolkits

## 2. INTERLOCKING_WRITING_RULES
RULE_FLOWTTS_01_PUNCHY_SOLUTION_HOOK:
  STYLE: Direct, confident, immediate presentation of the named system in the Abstract
  PATTERNS:
  INTERLOCK: RULE_FLOWTTS_01_PUNCHY_SOLUTION_HOOK <-> DEFAULT::RULE_SEC_02_ABS
  FEEDBACK_TRIGGER: IF Introduction takes >2 paragraphs to name the system -> FLAG_FLOWTTS_HOOK_DELAYED

RULE_FLOWTTS_02_PARETO_FRONTIER_REPORTING:
  METRIC_PAIRING: Never report acoustic quality in isolation; always pair perceptual scores (MOS/PESQ) with inference speed (RTF on CPU and GPU)
  REPORTING_FORMAT: Tabulate Real-Time Factor (RTF) at different ODE step counts (e.g., 2, 4, 10, 50 steps)
  CANONICAL_TARGET: Achieve RTF < 0.1 on consumer CPU and < 0.02 on modern GPU
  INTERLOCK: RULE_FLOWTTS_02_PARETO_FRONTIER_REPORTING <-> DOMAIN::TTS_AND_VOCODERS
  FEEDBACK_TRIGGER: IF Generative TTS paper lacks RTF or latency benchmark -> FLAG_FLOWTTS_RTF_MISSING

RULE_FLOWTTS_03_CRITICAL_EVALUATION_CALIBRATION:
  METHODOLOGY_STANDARD:
    - In subjective listening tests, avoid naive absolute MOS when subtle artifacts are under test; use MUSHRA (MUlti Stimulus test with Hidden Reference and Anchor) or Comparison Mean Opinion Score (CMOS)
    - Always include explicit high-anchor (ground truth natural recording) and low-anchor (3.5 kHz low-pass filtered audio or corrupted baseline)
    - Perform statistical significance tests (Wilcoxon signed-rank test or paired t-test with Holm-Bonferroni correction)
  INTERLOCK: RULE_FLOWTTS_03_CRITICAL_EVALUATION_CALIBRATION <-> DOMAIN::REASONING_AND_EVALUATION
  FEEDBACK_TRIGGER: IF Subjective evaluation lacks statistical significance testing -> FLAG_FLOWTTS_SIGNIFICANCE_UNVERIFIED

RULE_FLOWTTS_04_MATHEMATICAL_FLOW_FORMULATION:
  NOTATION_RIGOR:
    - Formal definition of probability path p_t(x) and vector field v_t(x)
    - Exact ODE formulation: dx_t = v_t(x_t) dt
    - Explicit Optimal Transport (OT) conditional vector field equation: u_t(x | x_1) = (x_1 - (1 - \sigma_{min}) x) / (1 - (1 - \sigma_{min}) t)
  INTERLOCK: RULE_FLOWTTS_04_MATHEMATICAL_FLOW_FORMULATION <-> DEFAULT::RULE_SEC_03_CONTRIB
  FEEDBACK_TRIGGER: IF Flow matching model describes training heuristically without vector field equations -> FLAG_FLOWTTS_MATH_INCOMPLETE

## 3. HIGHLIGHT_AND_BASELINE_BEATING_PATTERNS
BASELINE_SUPERIORITY_STRATEGY:
  SPEED_QUALITY_DUAL_VICTORY: Beat diffusion models in generation speed by an order of magnitude (e.g., 4 steps vs 100 steps) while simultaneously matching or exceeding their naturalness.
  QUANTIFIED_SUPERIORITY_EXAMPLES:

## 4. SECTION_BY_SECTION_LINE_ARCHITECTURE
SEC_I_INTRODUCTION:
  - Paragraph 1: Modern speech synthesis / foundation model paradigm and the tension between sampling speed and audio fidelity
  - Paragraph 2: Failure modes of autoregressive (slow, serial) and standard diffusion models (excessive sampling steps, high computational cost)
  - Paragraph 3: Introduction of the proposed system (named in bold/italics), highlighting continuous-time formulation or novel tokenization
  - Paragraph 4: Quantified headline gains over baselines
  - Paragraph 5: Three clear contribution bullets with open-source commitment

SEC_II_RELATED_WORK_AND_BACKGROUND:
  - Concise review of diffusion and flow matching paradigms
  - Clear delineation between existing discrete token approaches and proposed continuous formulation

SEC_III_METHOD:
  - Mathematical formulation of conditional probability paths
  - Architectural schematic showing 1D CNN / Transformer text encoder and U-Net / DiT flow backbone
  - Exact loss function and training algorithm pseudocode

SEC_IV_EXPERIMENTS_AND_SETUP:
  - Benchmark datasets (LJSpeech, VCTK, LibriTTS)
  - Sampling setup: Euler / Midpoint ODE solvers with varying step sizes (2, 4, 10, 50)
  - Objective suite: Mel-Cepstral Distortion (MCD), F0 RMSE, Character Error Rate (CER), Real-Time Factor (RTF)
  - Subjective suite: MUSHRA / CMOS with 95% confidence intervals

SEC_V_RESULTS_AND_ABLATION:
  - Pareto curve visualization (RTF vs MOS / MCD)
  - Tabulated comparisons against autoregressive, diffusion, and flow matching baselines
  - Step-count ablation demonstrating rapid ODE convergence

SEC_VI_CONCLUSION:
  - Concise summary of empirical and theoretical achievements
  - Practical deployment impact on offline edge devices and robotics

## 5. SENTENCE_STRUCTURE_AND_VOCABULARY_BANK
CANONICAL_FLOWTTS_SENTENCES:
  - "This paper introduces Matcha-TTS, a probabilistic and non-autoregressive acoustic model that pairs high naturalness with rapid ODE-based sampling."
  - "Unlike traditional diffusion models requiring dozens of denoising steps, our Optimal Transport flow path enables high-fidelity synthesis in as few as four steps."
  - "We demonstrate that discrete sound tokens can be seamlessly integrated into LLMs to enable interleaved text and audio reasoning without catastrophic forgetting."
  - "To address known biases in subjective speech evaluation, we conduct MUSHRA listening tests with hidden anchors and evaluate statistical significance via Wilcoxon signed-rank tests."

## 6. CONSTRUCTIVE_FEEDBACK_TRIGGERS
TRIGGER_FLOWTTS_01:
  CONDITION: IF Flow matching or diffusion model claims speed advantage without plotting RTF vs steps
  ACTION: Inject prompt: "[FLOWTTS_AUDIT]: Plot Pareto curve of RTF vs MCD/MOS across 2, 4, 10, 20, 50 ODE steps."

TRIGGER_FLOWTTS_02:
  CONDITION: IF Evaluation relies purely on uncalibrated crowdsourced MOS without hidden anchors
  ACTION: Inject prompt: "[FLOWTTS_AUDIT]: Implement MUSHRA test with low/high anchors or report paired statistical significance."

## 9. INCREMENTAL_EVIDENCE
AUTO_EVIDENCE_BEGIN: TRUE
# Populated by scripts/update_skills_incremental.py when source papers are added.
AUTO_EVIDENCE_END: TRUE
