# SKILL_ID: DOMAIN::TTS_AND_VOCODERS
META_VERSION: 1.0
DOMAIN_NAME: Text-to-Speech (TTS), Neural Vocoders, and Voice Conversion
SCOPE: Acoustic modeling, flow matching, diffusion probabilistic models, neural vocoding (HiFi-GAN, BigVGAN, Model-B), zero-shot voice cloning, non-autoregressive synthesis, and speech prosody
DEFAULT_FALLBACK: skills/default_speech_ai.md
INTERLOCKS_WITH: [DEFAULT_SPEECH_AI, DOMAIN::REASONING_AND_EVALUATION]
LAYER_POLICY: DELTA_AND_STRICT_OVERLAY
FORMAT_STYLE: KEY_VALUE_DENSE

## 1. IDENTITY_AND_DOMAIN_STANDARDS
CORE_CHALLENGE: Generating natural, expressive, speaker-consistent waveforms from text or source audio with low latency and high phonetic fidelity
STANDARD_BASELINES:
  AUTOREGRESSIVE: [VITS, FastSpeech 2, Tacotron 2, NaturalSpeech 2]
  DIFFUSION_AND_FLOW: [Grad-TTS, Matcha-TTS, Diff-TTS, VoiceBox, StyleTTS 2]
  VOCODERS: [HiFi-GAN (V1/V2), BigVGAN, MelGAN, WaveGlow, Model-B]
STANDARD_BENCHMARKS: [LJSpeech, VCTK, LibriTTS, Hi-Fi Multi-Speaker, IndicTTS]
MANDATORY_METRICS:
  OBJECTIVE: [MCD (dB) (↓), F0 RMSE (Hz) (↓), FAD (↓), PESQ (↑), UTMOS (↑), RTF (↓)]
  SUBJECTIVE: [Naturalness MOS (↑), Speaker Similarity MOS (SMOS) (↑), MUSHRA (↑)]

## 2. INTERLOCKING_WRITING_RULES
RULE_TTS_01_SAMPLING_RATE_EXPLICITNESS:
  PATTERN: Sampling rate must be explicitly noted in Abstract, Architecture diagram, and Experiments (e.g., 22.05 kHz or 24 kHz or 44.1 kHz)
  NOTE: Write "44.1 kHz" (never "44 KHz")
  INTERLOCK: RULE_TTS_01_SAMPLING_RATE_EXPLICITNESS <-> DEFAULT::RULE_SEC_05_REPRODUCIBILITY
  FEEDBACK_TRIGGER: IF Sampling rate missing or written as "44 KHz" -> FLAG_TTS_SAMPLING_RATE_ERROR

RULE_TTS_02_ODE_SOLVER_AND_STEP_SPECIFICATION:
  PATTERN: For flow matching or diffusion models, specify ODE solver (Euler, Midpoint, RK4), step count (N=2, 4, 10, 50), and temperature hyperparameter
  INTERLOCK: RULE_TTS_02_ODE_SOLVER_AND_STEP_SPECIFICATION <-> DEFAULT::RULE_SEC_03_CONTRIB
  FEEDBACK_TRIGGER: IF Flow/diffusion model evaluated without specifying step count -> FLAG_TTS_SOLVER_UNSPECIFIED

RULE_TTS_03_PARETO_FRONTIER_REPORTING:
  PATTERN: Tabulate both perceptual speech quality (MOS/PESQ/UTMOS) and computational efficiency (RTF, GPU VRAM, parameter count)
  INTERLOCK: RULE_TTS_03_PARETO_FRONTIER_REPORTING <-> DEFAULT::RULE_SEC_04_METRICS
  FEEDBACK_TRIGGER: IF TTS paper claims "fast" without RTF on CPU and GPU -> FLAG_TTS_RTF_MISSING

RULE_TTS_04_VOCODER_INDEPENDENCE_AUDIT:
  PATTERN: When comparing acoustic models, freeze the vocoder across all baselines (e.g., standard pre-trained HiFi-GAN) to isolate acoustic model contributions
  INTERLOCK: RULE_TTS_04_VOCODER_INDEPENDENCE_AUDIT <-> DEFAULT::RULE_SEC_06_EXP
  FEEDBACK_TRIGGER: IF Baselines use different neural vocoders without justification -> FLAG_TTS_VOCODER_CONFUNDED

RULE_TTS_05_SPECTROGRAM_FIGURE_STANDARDS:
  PATTERN: Mel-spectrogram comparisons must use matching frequency/time axes, identical colormaps (e.g., Viridis or Magma), and >= 1600 DPI resolution
  INTERLOCK: RULE_TTS_05_SPECTROGRAM_FIGURE_STANDARDS <-> DEFAULT::RULE_LATEX_AND_FIGURES
  FEEDBACK_TRIGGER: IF Spectrogram figures blurry or have mismatched dynamic range scales -> FLAG_TTS_SPECTROGRAM_LOW_RES

## 3. HIGHLIGHT_AND_BASELINE_BEATING_PATTERNS
CORE_ARGUMENT_STRUCTURE:
  - ARGUMENT_1_QUALITY: "Our proposed architecture achieves a Mel-Cepstral Distortion (MCD) of [X.XX] dB, outperforming [Baseline] ([Y.YY] dB) by [Delta] dB."
  - ARGUMENT_2_SPEED: "By using optimal transport conditional flow matching, [System] synthesizes 1 second of speech in [Z] ms (RTF = 0.015), representing a 5x speedup over diffusion baselines."
  - ARGUMENT_3_ZERO_SHOT_TIMBRE: "In zero-shot speaker adaptation, [System] achieves an SMOS of [X.XX_{\pm 0.08}], demonstrating robust speaker timbre retention without fine-tuning."

## 4. SECTION_BY_SECTION_LINE_ARCHITECTURE
SEC_I_INTRODUCTION:
  - Paragraph 1: Voice interfaces and demand for expressive, zero-shot, real-time speech generation
  - Paragraph 2: Dilemma: Autoregressive models are slow and prone to hallucination; diffusion models require excessive denoising steps
  - Paragraph 3: Proposed model introducing continuous-time flow matching, efficient vocoding, or disentangled prosody
  - Paragraph 4: Quantified superiority over top baselines in MCD, MOS, and RTF
  - Paragraph 5: Three contribution bullets with open-source code/audio demo link

SEC_III_PROPOSED_ARCHITECTURE:
  - Text/Phoneme encoder (conformer, transformer, or byte tokenizer)
  - Duration/Pitch predictor (explicit vs flow-based alignment)
  - Flow matching or diffusion decoder with exact vector field equations
  - Vocoder interface with loss functions (multi-resolution STFT loss, adversarial loss, mel-loss)

SEC_IV_EXPERIMENTS:
  - Dataset specifications (hours, speakers, acoustic quality)
  - Baseline model citations and exact pre-trained configurations
  - Audio demo website statement with uncompressed 24/48 kHz WAV files

SEC_V_RESULTS:
  - Comprehensive comparison table (MCD, F0-RMSE, CER, PESQ, UTMOS, RTF)
  - Listening test results (MOS/SMOS) with 95% confidence intervals and ITU-T P.800 compliance
  - Spectrogram analysis illustrating high-frequency harmonic restoration

## 5. CONSTRUCTIVE_FEEDBACK_TRIGGERS
TRIGGER_TTS_01:
  CONDITION: IF Paper claims human parity or rivaling natural speech without paired CMOS test
  ACTION: Inject prompt: "[TTS_DOMAIN_AUDIT]: Conduct comparison MOS (CMOS) against ground-truth natural speech."

TRIGGER_TTS_02:
  CONDITION: IF Voice conversion paper omits Source-Target speaker similarity metrics
  ACTION: Inject prompt: "[TTS_DOMAIN_AUDIT]: Include SMOS or cosine similarity of speaker embeddings (WavLM/ECAPA-TDNN)."

## 9. INCREMENTAL_EVIDENCE
AUTO_EVIDENCE_BEGIN: TRUE
# Populated by scripts/update_skills_incremental.py when source papers are added.
AUTO_EVIDENCE_END: TRUE
