# Platform Compatibility

The skill is plain Markdown plus standard-library Python. The Markdown works everywhere; the scripts need an agent that can run a shell (or a person who runs them). The integrity rules (no invented citations or numbers, no coding terms, bounded claims) travel in text, so they apply on every platform.

## Matrix

| Platform | Reads | Can run scripts? | Setup |
|---|---|---|---|
| **Claude Code** | `SKILL.md` as a skill | yes | link or copy this folder to `~/.claude/skills/speech-nlp-paper-writing` |
| **Claude.ai / Claude Desktop** | skill zip | in the code sandbox (no network in some plans) | `python3 scripts/package_skill.py`, then upload `dist/paper-writing-skill-lite.zip` as a skill |
| **ChatGPT, Custom Instructions** | the two boxes in `chatgpt/ChatGPT_Custom_Instructions.md` (+ the Box 2 addendum) | no | paste |
| **ChatGPT Project / Custom GPT** | `chatgpt/ChatGPT_Project_or_GPT_Prompt.md` | with Code Interpreter if you upload the lean zip | paste the prompt; upload the lean zip as knowledge |
| **Codex CLI / agents that read `AGENTS.md`** | `AGENTS.md` then `SKILL.md` | yes | open the project with this folder reachable, or copy `AGENTS.md` into the repo |
| **Gemini CLI** | `GEMINI.md` (imports `AGENTS.md`) | yes | place in the project or `~/.gemini/` |
| **Cursor** | `.cursor/rules/paper-writing.mdc` | yes | copy `.cursor/` into the workspace |
| **GitHub Copilot** | `.github/copilot-instructions.md` | agent mode | copy `.github/` into the repo |
| **Any chat model** | `compat/UNIVERSAL_PROMPT.md` | no | paste the block |

## Claude Code
```bash
ln -s /path/to/this/skill ~/.claude/skills/speech-nlp-paper-writing
```
Invoke with `/speech-nlp-paper-writing`, or just ask for paper work; the description triggers it. Scripts run directly.

## Claude.ai and ChatGPT uploads: use the lean zip
The folder includes a large PDF corpus (`Authors/`, `parsed_md/`, `analysis_cache/`, about 76 MB). Uploads and token budgets do not need it.
```bash
python3 scripts/package_skill.py            # -> dist/paper-writing-skill-lite.zip (no corpus)
python3 scripts/package_skill.py --with-corpus   # everything, for local or Git use
```
The lean zip keeps `SKILL.md`, all references, author and domain skills, templates, scripts, and the compat files. The incremental corpus updater (`update_skills_incremental.py`) needs the corpus; run it locally.

## Limits to know (honest notes)
- **No network, no verification.** Citation verification needs live access to Crossref, arXiv, ACL Anthology, OpenAlex, or Semantic Scholar. Some sandboxes block outbound requests. Then: use the browsing tool, or give the model verified identifiers, and keep anything unverified marked `[CITATION NEEDED]`. Never let a model fill gaps from memory.
- **No TeX.** Many sandboxes have no LaTeX. `paper_check.py` reports `tex-unavailable` instead of faking a build; compile on Overleaf and record the result.
- **Instruction length.** If a field limits characters (Custom GPT instructions have been limited to roughly 8,000 characters; check the current limit), paste `compat/UNIVERSAL_PROMPT.md` (about 4,500 characters) instead of the full Project prompt and upload the references as knowledge files.
- **Plain chat cannot run the scripts.** Follow the same procedure by hand: you supply identifiers and results, the model drafts and marks what it cannot verify.
- **Figures.** `make_plots.py`, `make_diagram.py`, `make_audio_figs.py` need `matplotlib` and `numpy`. Image generators, where available, may illustrate concepts but never produce evidence.
- **Browsers.** The dashboard and demo site are served locally; open them in any modern browser. Both bind to `127.0.0.1`.

## Adding another platform
Point its rules file at `AGENTS.md`. Keep the hard rules in one place: `AGENTS.md` for agents, `UNIVERSAL_PROMPT.md` for chat.
