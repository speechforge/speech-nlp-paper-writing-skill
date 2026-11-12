# SKILL_ID: ROUTER::SPEECH_AI
META_VERSION: 1.0
ROLE: Dynamic Router and Composition Engine for Speech AI Academic Writing Skills
UPDATE_COMMAND: python3 scripts/update_skills_incremental.py
LOAD_ORDER_PROTOCOL: [SKILL_ROUTER, default_speech_ai, AUTHOR::<target_author>, DOMAIN::<primary_domain>, DOMAIN::<secondary_domain>]

## 1. ROUTER_INVENTORY
AUTO_INVENTORY_BEGIN: TRUE
AUTHORS: [clinical_multimodal_style, ieee_lab_style, vocoder_benchmark_style, flow_matching_tts_style]
DOMAINS: [asr_and_error_correction, dataset_and_corpus, nlp_and_aac, reasoning_and_evaluation, tts_and_vocoders]
AUTO_INVENTORY_END: TRUE

## 2. TOPIC_ROUTING_DECISION_MATRIX
ROUTING_TABLE:
  - INTENT: "Writing a TTS, vocoder, or voice conversion paper"
    PRIMARY_DOMAIN: DOMAIN::TTS_AND_VOCODERS
    RECOMMENDED_AUTHORS: [AUTHOR::FLOW_MATCHING_TTS_STYLE, AUTHOR::IEEE_LAB_STYLE, AUTHOR::CLINICAL_MULTIMODAL_STYLE]
    ACTIVE_SKILLS: [default_speech_ai, domains/tts_and_vocoders.md]

  - INTENT: "Writing a paper using Flow Matching, Optimal Transport, or Matcha-TTS style architecture"
    PRIMARY_DOMAIN: DOMAIN::TTS_AND_VOCODERS
    AUTHOR_OVERLAY: AUTHOR::FLOW_MATCHING_TTS_STYLE
    ACTIVE_SKILLS: [default_speech_ai, authors/flow_matching_tts_style.md, domains/tts_and_vocoders.md]

  - INTENT: "Writing a paper for Speech Research Lab (University) or following Lab rules"
    AUTHOR_OVERLAY: AUTHOR::IEEE_LAB_STYLE
    ACTIVE_SKILLS: [default_speech_ai, authors/ieee_lab_style.md]
    MANDATORY_OVERLAYS: [3_CONTRIBUTION_LAW, COMPARATIVE_ADJECTIVE_LAW, ITU_T_P800_WITH_95_CI, MEITY_GRANT, 1600_DPI_FIGURES]

  - INTENT: "Writing a clinical speech, dysarthria, or assistive speech paper"
    PRIMARY_DOMAIN: DOMAIN::DATASET_AND_CORPUS
    SECONDARY_DOMAIN: DOMAIN::ASR_AND_ERROR_CORRECTION
    AUTHOR_OVERLAY: AUTHOR::CLINICAL_MULTIMODAL_STYLE
    ACTIVE_SKILLS: [default_speech_ai, authors/clinical_multimodal_style.md, domains/dataset_and_corpus.md, domains/asr_and_error_correction.md]

  - INTENT: "Writing an ASR, Whisper adaptation, or LLM post-ASR error correction paper"
    PRIMARY_DOMAIN: DOMAIN::ASR_AND_ERROR_CORRECTION
    SECONDARY_DOMAIN: DOMAIN::NLP_AND_AAC
    ACTIVE_SKILLS: [default_speech_ai, domains/asr_and_error_correction.md, domains/nlp_and_aac.md]

  - INTENT: "Writing an audio reasoning, sound token, or LLM speech paper"
    PRIMARY_DOMAIN: DOMAIN::NLP_AND_AAC
    SECONDARY_DOMAIN: DOMAIN::REASONING_AND_EVALUATION
    AUTHOR_OVERLAY: AUTHOR::FLOW_MATCHING_TTS_STYLE
    ACTIVE_SKILLS: [default_speech_ai, authors/flow_matching_tts_style.md, domains/nlp_and_aac.md, domains/reasoning_and_evaluation.md]

  - INTENT: "Writing an evaluation methodology, MOS test critique, or perception prediction paper"
    PRIMARY_DOMAIN: DOMAIN::REASONING_AND_EVALUATION
    ACTIVE_SKILLS: [default_speech_ai, domains/reasoning_and_evaluation.md]

## 3. MULTI_SKILL_COMPOSITION_RULES
RULE_COMPOSITION_01_PRECEDENCE:
  HIERARCHY:
    1. USER_EXPLICIT_CONSTRAINTS (Highest Priority)
    2. AUTHOR_SPECIFIC_SKILL (Overrides defaults on stylistic conventions and lab formatting)
    3. DOMAIN_SPECIFIC_SKILL (Adds domain metrics, baselines, and specialized section architectures)
    4. DEFAULT_SPEECH_AI (Foundational rigor, 7-sentence abstract, causal grounding, 1600 DPI)
  INTERLOCK: RULE_COMPOSITION_01_PRECEDENCE <-> DEFAULT::RULE_SEC_01_TITLE

RULE_COMPOSITION_02_ZERO_COLLISION:
  POLICY: Author rules specialize or tighten domain rules; they never weaken default rigor. If an Author skill requires 95% CI on MOS and the Domain skill mentions MOS, the 95% CI rule strictly applies.
  INTERLOCK: RULE_COMPOSITION_02_ZERO_COLLISION <-> AUTHOR::* <-> DOMAIN::*

RULE_COMPOSITION_03_INCREMENTAL_REFRESH:
  POLICY: When new papers are added to `Authors/<new_author>/<paper.pdf>`, run `python3 scripts/update_skills_incremental.py`. The router inventory and the relevant author/domain `INCREMENTAL_EVIDENCE` blocks update deterministically without re-analyzing unaffected papers.

## 4. JOURNEY_ROUTING (enhancement; additive to everything above)
META_VERSION_ADD: 1.1
PURPOSE: Select the smallest journey, then compose it with the author and domain overlays above. Load ONE reference at a time.
ROUTING_TABLE_JOURNEYS:
  - INTENT: "Brainstorm and plan (topic, rough idea, possible method)"
    LOAD: [references/19_novelty_and_story.md]
    OUTPUT: [paper_story.md, experiment plan]
  - INTENT: "Repo to full paper (code, notes, logs, partial results, venue template)"
    LOAD: [references/11_workflow_journeys_and_artifacts.md, references/19_novelty_and_story.md, references/12_citation_integrity.md, references/13_venue_templates_acl_ieee.md, references/14_figures_plots_and_visuals.md]
    FIRST_COMMAND: "python3 scripts/paper_init.py init PROJECT --name NAME --venue acl|ieee --context PATH"
    OUTPUT: [workspace, claim_evidence_map.md, references.bib + citation_lock.json, section files, figures, demo site]
  - INTENT: "Draft review (skeptical reviewer)"
    LOAD: [references/20_reviewer_mode_and_revision.md, references/05_adversarial_review_checklist.md]
    OUTPUT: [reviewer_analysis.md, edit plan]
  - INTENT: "Targeted revision (section, feedback, known weaknesses)"
    LOAD: [references/20_reviewer_mode_and_revision.md, references/10_senior_scientist_voice_and_flow.md, references/04_section_blueprints.md]
    OUTPUT: [revised section files, updated claim map]
  - INTENT: "Figures and tables"
    LOAD: [references/14_figures_plots_and_visuals.md, references/08_figure_dpi_and_latex_quality.md]
    OUTPUT: [figure_plan.md, paper/figures, paper/tables]
  - INTENT: "Submission readiness"
    LOAD: [references/21_submission_readiness.md, references/12_citation_integrity.md, references/17_credits_and_license.md]
    FIRST_COMMAND: "python3 scripts/paper_check.py PROJECT ready"
  - INTENT: "Evidence gap or missing experiment"
    LOAD: [references/16_experiments_on_demand.md]
  - INTENT: "Interactive samples, audio demo, multimedia website"
    LOAD: [references/15_interactive_demo_website.md]
  - INTENT: "Credit statement, license statement, acknowledgments, funding"
    LOAD: [references/17_credits_and_license.md]
  - INTENT: "ACL, EMNLP, NAACL, IEEE, ICASSP, Interspeech template or venue conversion"
    LOAD: [references/13_venue_templates_acl_ieee.md]
  - INTENT: "Show progress of the writing on localhost"
    LOAD: [references/18_progress_dashboard.md]
    COMMAND: "python3 scripts/dashboard.py PROJECT --open"

RULE_COMPOSITION_04_JOURNEY_WITH_OVERLAYS:
  POLICY: A journey chooses WHAT to do; author and domain overlays choose HOW the paper reads. Compose them; never let an overlay weaken the integrity rules below.
RULE_COMPOSITION_05_INTEGRITY_FLOOR:
  POLICY: In every journey and with every overlay: no invented citations or numbers, no coding terms in the paper, claims bounded by evidence, novelty carried through every section, credit and license statements present.
  ENFORCED_BY: [scripts/citations.py, scripts/prose_lint.py, scripts/paper_check.py]
RULE_COMPOSITION_06_FORMAT_FAMILY:
  POLICY: IEEE-family venues use the IEEE-specific rules in references/06 to 09 (Roman numerals, ALL-CAPS table captions above, numeric citations, ACKNOWLEDGMENT). ACL-family venues use references/13 (natbib author-year, captions below, Limitations section, Acknowledgments). Author and domain content rules apply to both.

RULE_COMPOSITION_07_ACTIVE_PROFILE:
  POLICY: skills/ACTIVE.md (generated by scripts/skill_profile.py) overrides every routing entry above. A source listed as disabled there is never loaded and none of its rules apply, even when an INTENT block or an AUTHORS/DOMAINS list names it. If ACTIVE.md is absent, all sources apply.
  MERGE: When several author sources are active, the first listed in ACTIVE.md has precedence; on a shared interlock point (see skills/merged/<profile>.md) apply the higher-precedence rule and tell the user when a lower-precedence rule was overridden.
  COMMANDS: [use <profile>, only <id>, merge <id> <id>, enable|disable <id|@group>, register, unregister, export, prune, provenance, doctor]
