# Scientific & ML Paper Writing Skill (Lab & 15-Step Method)

> **Speech & NLP Paper Writing Skill** (skill id `speech-nlp-paper-writing`).

A production-grade, globally accessible writing and review skill designed for academic researchers in Speech, Audio, Machine Learning, and Signal Processing (targeting **ICASSP, Interspeech, NeurIPS, ICML, ICLR**, and **IEEE/ACM Transactions**).

This skill combines:
- **Speech Lab Standards**: Unbroken causal argument chains, three-contribution rule, strict claim-evidence alignment, bounded claims, and comparative adjective laws.
- **Drake & Han (PLOS Comput. Biol., 2025) 15-Step Method**: CARS model (Territory-Niche-Occupy), paired method-rationale ("to-clauses"), results-to-findings bipartite mapping, problem-item & response pairs, topic & concluding sentences, and bold purpose sentences.
- **Sebastian Farquhar & Neel Nanda ML Paper Architecture**: 4-sentence Abstract formula, 1-page CARS Introduction, Figure 1 teaser rule, minimal-ink tables, and compress-then-expand drafting.

---

## Repository Structure

```text
speech-nlp-paper-writing/
├── SKILL.md                                 # Master Claude Code skill definition (YAML + instructions)
├── README.md                                # Skill documentation and installation guide
├── chatgpt/
│   ├── ChatGPT_Custom_Instructions.md       # Copy-paste for ChatGPT Personalization (Box 1 & Box 2)
│   └── ChatGPT_Project_or_GPT_Prompt.md     # Full Master Prompt for ChatGPT Projects & Custom GPTs
├── references/
│   ├── 01_ieee_lab_rules.md                # Causal chains, 3 contributions, construct naming, adjective law
│   ├── 02_15_step_writing_method.md         # Drake & Han 15-step scientific writing methodology
│   ├── 03_ml_speech_paper_architecture.md   # 4-sentence abstract, 1-page intro, Fig. 1, minimal-ink tables
│   ├── 04_section_blueprints.md             # Section-by-section drafting templates (Abstract -> Conclusion)
│   ├── 05_adversarial_review_checklist.md   # 5-dimension reviewer scorecard & Claim-Evidence Audit Matrix
│   ├── 06_conference_paper_style_guide.md # Style guide learned from published IEEE Conference A & IEEE Conference B papers
│   ├── 07_section_by_section_corrections_and_rules.md # ~700-line correction manual (Abstract to References)
│   ├── 08_figure_dpi_and_latex_quality.md   # Figure >=1600 DPI, vector rules, booktabs table standards
│   └── 09_repair_manual_mistakes_to_globally_acceptable.md # 25+ real error repairs into global standards
├── skills/
│   ├── SKILL_ROUTER.md                      # Dynamic router and composition rules for Speech AI skills
│   ├── default_speech_ai.md                 # Universal foundational Speech AI writing skill (dense KV)
│   ├── authors/                             # Author-specific writing style skills
│   │   ├── ieee_lab_style.md                # IEEE-conference lab style (acoustics, Teager, 3 contributions, ITU-T P.800)
│   │   ├── clinical_multimodal_style.md     # Clinical and accented speech, multimodal perception, ablation-first
│   │   └── flow_matching_tts_style.md       # Flow-matching TTS, sound tokens, Pareto speed-quality reporting
│   └── domains/                             # Domain-specific writing skills
│       ├── tts_and_vocoders.md              # TTS, vocoders, diffusion/flow matching, ODE solvers, MCD
│       ├── dataset_and_corpus.md            # Clinical & multi-speaker corpus design, IRB, annotator agreement
│       ├── asr_and_error_correction.md      # Conformer/Whisper, generative post-ASR correction, WER/CER
│       ├── nlp_and_aac.md                   # LLMs with sound tokens, AAC assistive communication, KSR
│       └── reasoning_and_evaluation.md      # Audio reasoning, Proxy MOS, critical MOS evaluation standards
├── scripts/
│   ├── pdf_to_md_preserve_style.py          # PDF to Markdown converter preserving italics, bold, math, provenance
│   ├── analyze_papers.py                    # Line-by-line deterministic rhetorical analyzer (18k+ lines)
│   └── update_skills_incremental.py         # Incremental hash-verified ingest and skill evidence updater
```

---

## 1. How to Use with Claude Code (Global Personal Skill)

The skill is installed in your personal skills directory:
```text
~/.claude/skills/speech-nlp-paper-writing -> ../../.agents/skills/speech-nlp-paper-writing -> <this skill folder>
```

Because it is located in `~/.claude/skills/`, Claude Code loads it automatically across **all projects and sessions** on this computer.

### Ways to invoke:
1. **Direct Command**:
   ```bash
   /speech-nlp-paper-writing
   ```
2. **Automatic Invocation**:
   Simply ask Claude questions or tasks that match academic writing, such as:
   - *"Help me draft the Introduction for my ICASSP vocoder paper."*
   - *"Audit my Abstract and check claim-evidence alignment."*
   - *"Review this Results section as an adversarial reviewer."*
   - *"Write the Related Work section contrasting our method against HiFi-GAN and BigVGAN."*

---

## 2. How to Use with ChatGPT

### Option A: ChatGPT Custom Instructions (Global across all chats)
1. Open ChatGPT, click on your profile (bottom left or top right) and select **Custom Instructions** (or **Settings > Personalization > Custom Instructions**).
speech-nlp-paper-writing/
3. Copy **Box 1** into *"What would you like ChatGPT to know about you to provide better responses?"*.
4. Copy **Box 2** into *"How would you like ChatGPT to respond?"*.
5. Click **Save**.

### Option B: ChatGPT Projects or Custom GPT (Dedicated research workspace)
1. In ChatGPT, create a new **Project** or **Custom GPT** named *Speech & NLP Paper Writing Assistant*.
speech-nlp-paper-writing/
3. Copy the entire markdown content into the **Instructions / System Prompt** field.
4. (Optional) Upload the markdown files in `references/` into the Project/GPT knowledge base.

---

## 3. Core Rules Enforced by the Skill

1. **Unbroken Causal Chain**:
   $$\text{Problem} \longrightarrow \text{Observed Failure} \longrightarrow \text{Proposed Response} \longrightarrow \text{Expected Effect} \longrightarrow \text{Empirical Experiment} \longrightarrow \text{Bounded Conclusion}$$
2. **The 3-Contribution Rule**: Limit conference contributions to 2–4 (ideally 3) tightly scoped, non-overlapping items, each matched to an empirical table or ablation.
3. **No Fluff Openings**: Ban generic openings (*"Deep learning has become popular in recent years..."*). Start directly with the core technical dilemma.
4. **Comparative Adjective Law**: Never write "better", "superior", or "state-of-the-art" without citing: (1) baseline, (2) dataset/split, (3) independent metric, (4) effect size, and (5) uncertainty.
5. **Bold Purpose Statements**: Every drafted paragraph is preceded by `**[Purpose: ...]**` during development to ensure singular messaging.
6. **Claim-Evidence Matrix**: Every revision produces a verifiable claim-evidence audit table.

---

## 4. What is new (enhancement overview)

Everything above is preserved. The enhancement adds, on top of it:

- **Journeys.** Six request types route the agent to the smallest set of references (below).
- **A senior NLP/speech scientist voice** with a hard rule: **no coding terms in the paper**, human and specific English, novelty-centred flow.
- **Citation integrity.** References are searched, resolved, and **double-verified** (primary record plus an independent index, then sentence-level support). Nothing is generated from memory.
- **ACL and IEEE conference templates** wired to the workflow. Section bodies are venue-independent; switching venue swaps one wrapper file. Official style files are fetched and hash-verified.
- **Figures, plots, spectrograms, diagrams, and tables** generated deterministically from data, with the proposed method and the novelty visible.
- **An interactive demo website** named after the project (never a conference or journal): audio A/B with live spectrograms, blind listening test, text comparison, results, credits, licences.
- **Experiments on demand.** When evidence is missing, the skill writes the experiment prompt, asks for approval, runs it quietly, and ingests a compact summary. Tokens go to writing and thinking, not job logistics.
- **Credit and license statements** (CRediT, licences, third-party credit, inherited restrictions), generated from one metadata file.
- **A localhost dashboard** that shows the whole progress at zero token cost.
- **Portability.** Works in Claude, ChatGPT, Codex, Gemini, Cursor, Copilot, and plain chat (`compat/`).

### New files added by the enhancement (the tree above is the original and is unchanged)

| Path | Purpose |
|---|---|
| `references/10_senior_scientist_voice_and_flow.md` | persona, human English, no coding terms, paragraph flow |
| `references/11_workflow_journeys_and_artifacts.md` | six journeys, workspace layout, token budget |
| `references/12_citation_integrity.md` | never-invented, double-verified citations |
| `references/13_venue_templates_acl_ieee.md` | ACL and IEEE wrappers, page rules, venue conversion |
| `references/14_figures_plots_and_visuals.md` | plots, diagrams, spectrograms, tables |
| `references/15_interactive_demo_website.md` | project-named multimedia site |
| `references/16_experiments_on_demand.md` | experiment brief -> quiet run -> compact ingest |
| `references/17_credits_and_license.md` | CRediT, license statement, speech ethics |
| `references/18_progress_dashboard.md` | localhost progress view |
| `references/19_novelty_and_story.md` | novelty types, delta, novelty thread |
| `references/20_reviewer_mode_and_revision.md` | evidence-first review, targeted revision |
| `references/21_submission_readiness.md` | readiness gate and packaging |
| `references/22_craft_from_ml_paper_writing.md` | Nanda, Farquhar, Gopen & Swan, Perez, Lipton, Steinhardt |
| `references/23_conference_checklists_and_requirements.md` | NeurIPS 16 items, ICML, ICLR, ACL, AAAI, COLM, IEEE + universal |
| `references/24_skill_profiles_and_sources.md` | enable/disable/merge/add/delete sources; lean export without PDFs |
| `references/25_rebuttal_and_author_response.md` | how venues review; author response template |
| `scripts/paper_init.py / scripts/context_digest.py` | scaffold a workspace; compact brief of a file or folder |
| `scripts/citations.py / scripts/fetch_template.py` | search, double-verify, BibTeX, gate; official ACL/IEEE style files |
| `scripts/prose_lint.py / scripts/paper_check.py` | coding-term and stock-phrase linter; readiness gate |
| `scripts/make_plots.py / scripts/make_diagram.py / scripts/make_audio_figs.py / scripts/make_latex_table.py` | deterministic figures and tables |
| `scripts/credits_license.py / scripts/experiments.py` | CRediT + license statements; experiment loop |
| `scripts/build_demo_site.py / scripts/dashboard.py` | interactive demo site; localhost progress dashboard |
| `scripts/venue_check.py / scripts/skill_profile.py` | per-venue checklist; switch skill sources on/off, merge, export |
| `scripts/package_skill.py` | lean zip for Claude.ai / ChatGPT upload |
| `templates/` | acl/ ieee/ neurips/ icml/ iclr/ aaai/ colm/ generic/ wrappers, venues.json, sections/, artifacts/, demo_site/, dashboard/ |
| `compat/` | platform guide and self-contained UNIVERSAL_PROMPT.md |
| `tests/` | unit tests for the scripts |
| `AGENTS.md  GEMINI.md  .cursor/  .github/` | entry points for Codex, Gemini CLI, Cursor, Copilot |
| `NOTICE.md  CHANGELOG.md` | attributions and what changed |

## 5. The six journeys

| Journey | You have | Ask the agent to do |
|---|---|---|
| Brainstorm and plan | A topic, rough idea, or possible method | Clarify the thesis, research gap, contribution boundary, evidence needed, and next experiment and writing plan |
| Repo to full paper | Ideas, method design, code, notes, experiment logs, partial results, or a venue template | Build `paper_story.md`, `claim_evidence_map.md`, literature positioning, figures, tables, BibTeX, LaTeX draft, and build checks |
| Draft review | A complete or partial paper draft | Act as a skeptical reviewer: write reviewer-style comments, identify rejection risks, and turn major issues into concrete edits |
| Targeted revision | A draft plus known weaknesses, reviewer feedback, or a section to improve | Revise the section or whole paper while preserving claim-evidence boundaries and avoiding unsupported stronger claims |
| Figures and tables | Results, logs, CSVs, method notes, or a rough figure idea | Produce figure and table plans, generated overview or method figures, deterministic result plots and tables, captions, and LaTeX wiring |
| Submission readiness | A near-final paper package | Run citation, marker, build, venue, reviewer-risk, checklist, and packaging checks before submission or Overleaf/Git handoff |

## 6. Why this skill

| Typical AI paper help | This skill |
|---|---|
| Fluent paragraphs from memory | Claims mapped to repository evidence |
| Citations guessed or invented | BibTeX fetched from Crossref, DataCite, arXiv, or ACL Anthology and cross-checked in a second index |
| Figure "plans" that never ship | Generated diagrams, spectrograms, and deterministic result plots and tables |
| Stops at an outline | Concrete artifacts: `paper_story.md`, `claim_evidence_map.md`, `references.bib`, section files, figures, demo site |
| Generic writing tips | Reviewer-style comments, rejection-risk diagnosis, venue checklists, build and packaging gates |
| Code vocabulary leaking into the paper | A linter that blocks file names, flags, identifiers, and code spans |

| Before using this skill | After using this skill |
|---|---|
| Scattered notes, logs, and half-written sections | `paper_story.md` and scoped task packets |
| Claims that sound plausible | `claim_evidence_map.md` with evidence status |
| Candidate citations from memory | BibTeX fetched or verified from authoritative metadata, double-checked |
| Figure ideas in prose | Generated concept figures and deterministic result plots |
| "Looks done" | Reviewer-style critique, build, marker, citation, and submission checks |

## 7. Quick start

```bash
SK=/path/to/this/skill   # adjust to where the skill lives

# 1. Workspace from a notes file or a project folder (reads it once, writes a compact digest)
python3 $SK/scripts/paper_init.py init ~/papers/boundaryvoc --name "BoundaryVoc" \
        --venue acl --context ~/code/my-vocoder-project --fetch-template

# 2. Watch progress in a browser (no tokens)
python3 $SK/scripts/dashboard.py ~/papers/boundaryvoc --open

# 3. Work through the journey with your agent, then run the gate
python3 $SK/scripts/paper_check.py ~/papers/boundaryvoc ready
```

Citations: `citations.py search`, then write `citation_requests.json`, then `citations.py verify`, then `citations.py check --strict`. Figures: `make_plots.py`, `make_diagram.py`, `make_audio_figs.py`, `make_latex_table.py`. Website: `build_demo_site.py PROJECT --serve`. Experiments: `experiments.py brief`, `approve`, `run`, `status`, `ingest`. Statements: `credits_license.py PROJECT`. Full options: `scripts/README.md`.

Requirements: Python 3 for the scripts (tested on 3.12 and 3.13); `matplotlib` and `numpy` for the figure scripts; network access for citation verification and style-file fetching; a LaTeX installation (or Overleaf) to compile. The scripts report honestly when something is unavailable.

## 8. Platform compatibility

| Platform | How |
|---|---|
| Claude Code | install as a skill (section 1 above); scripts run directly |
| Claude.ai / Claude Desktop | upload the lean zip from `python3 scripts/package_skill.py` as a skill |
| ChatGPT | Custom Instructions, Project / Custom GPT prompt (section 2), or Code Interpreter with the lean zip |
| Codex, Cursor, Copilot, Gemini CLI, other agents | `AGENTS.md`, `GEMINI.md`, `.cursor/rules/`, `.github/copilot-instructions.md` all point to `SKILL.md` |
| Any chat model without file access | paste `compat/UNIVERSAL_PROMPT.md`; the same integrity rules apply by hand |

Details and limits: `compat/README.md`.

## 9. Venue templates, multimedia, credits

- **ACL and IEEE** wrappers with shared section bodies; official style files fetched on demand with pinned hashes (`references/13_venue_templates_acl_ieee.md`).
- **Demo website** and **dashboard** (`references/15_interactive_demo_website.md`, `references/18_progress_dashboard.md`).
- **Credit and license statements** (`references/17_credits_and_license.md`).

## 10. Attribution

Parts of the enhancement adapt ideas from three MIT-licensed projects: *ai-research-writing-skill*, *Research-Paper-Writing-Skills*, and the *ml-paper-writing* guide. Their notices and what was adapted are in `NOTICE.md`; changes are listed in `CHANGELOG.md`.

## 11. Conference support (ACL, IEEE, NeurIPS, ICML, ICLR, AAAI, COLM)

Every venue has a wrapper over the same venue-independent section bodies, a pinned way to obtain its official style files (fetched from the official archive or repository, or imported from a local copy and verified by SHA-256), and a checklist taken from the venue's requirements and your checklist document:

```bash
python3 scripts/paper_init.py init PROJECT --name "Project" --venue neurips      # neurips icml iclr acl ieee aaai colm (+ emnlp, icassp, interspeech, ...)
python3 scripts/fetch_template.py icml --dest PROJECT/paper                      # official archive; neurips and aaai use --from <folder>
python3 scripts/venue_check.py PROJECT                                           # NeurIPS 16 items, ICML impact statement, ICLR LLM disclosure, ACL Limitations, AAAI forbidden packages, ...
python3 scripts/paper_init.py convert PROJECT --to iclr                          # swap venue; the prose never changes
```
`venue_check.py` verifies what can be verified from the project files (limitations present, compute stated, forbidden packages absent, anonymity, citations verified, ...) and lists the rest for the author to confirm; it writes `submission_checklist.md`, and the readiness gate includes it. Details: `references/13_venue_templates_acl_ieee.md`, `references/23_conference_checklists_and_requirements.md`. Style files are not redistributed (their terms are not stated); `fetch_template.py --vendor` is an explicit opt-in if you decide they may be bundled. The wrappers were checked statically but not compiled here (no LaTeX installation): compile once on Overleaf.

## 12. Choose your sources (one style only, merged, or your own)

```bash
python3 scripts/skill_profile.py init                         # once
python3 scripts/skill_profile.py use ieee-lab                 # only the IEEE-lab style (other authors off)
python3 scripts/skill_profile.py use clinical                 # only the clinical/multimodal style
python3 scripts/skill_profile.py use ieee-lab+clinical        # merge; the IEEE-lab style wins on conflicts (merge sheet in skills/merged/)
python3 scripts/skill_profile.py only author_ieee_lab --kinds author,domain   # strictly one style, domain skills off too
python3 scripts/skill_profile.py register my_lab --kind author --file skills/authors/my_lab.md   # add your own
python3 scripts/skill_profile.py unregister my_lab --delete-files --yes                          # delete a source
python3 scripts/skill_profile.py export ../my-skill-copy       # publishable copy: enabled sources only, no author PDFs
```
Agents read `skills/ACTIVE.md` first and ignore disabled sources. The author PDFs are provenance, not runtime inputs: `skill_profile.py provenance --write` records the papers behind each source (with hashes) so they can be deleted later without losing the evidence trail. Full guide: `references/24_skill_profiles_and_sources.md`.
