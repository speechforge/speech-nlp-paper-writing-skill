# Progress Dashboard (localhost, zero tokens)

```bash
python3 scripts/dashboard.py PROJECT --open        # http://127.0.0.1:8765/
```

The dashboard shows the whole path from first notes to submission-ready in a browser tab, refreshing every few seconds. It reads project files only; it does not call any model, so watching progress costs no tokens. Tell the user to open it instead of narrating status.

---

## 1. What it shows

- **Pipeline strip:** ten stages, each with a fill, a state word (Done, In progress, Not started), and a one-line detail. Shape and text carry the state, not colour alone.
- **What blocks submission:** the latest gate results from `paper_check.py ready`, tagged Pass, Warning, or Fail with detail. **Run checks** re-runs them from the page.
- **Do next:** the first three unfinished stages with plain-language actions.
- **Sections:** words and remaining `[INSERT]` placeholders per section file.
- **Claims and evidence:** supported, bounded, and open claims as one bar.
- **Citations:** verified over cited, and the statuses present.
- **Experiments:** each experiment and its status from the ledger.
- **Figures:** thumbnails of what exists in `paper/figures`.
- **Links:** the built demo website (`/demo/`) and the compiled PDF.

## 2. How each stage is derived (never self-reported)

| Stage | Done when |
|---|---|
| Context | `context_digest.md` exists |
| Story | thesis, novelty keywords, and contributions in `paper_story.md` are filled |
| Evidence | share of claim rows that are Supported (Partial counts half) |
| Experiments | every `Needs experiment` claim has an ingested experiment and nothing is pending |
| Draft | share of section files with no `[INSERT]` markers and real text |
| Figures | figures and tables exist in `paper/` (four items counts as complete; heuristic) |
| Citations | verified over cited keys in `citation_lock.json` |
| Review | at least three risks analysed in `reviewer_analysis.md` |
| Build | `.paper/build_record.json` says `ok` (without TeX it says so and stays open) |
| Website | `demo/site` built with sections |

The percentage in the header is the mean of the ten stage fractions. It is a progress signal, not a quality score: the readiness gate (`21`) decides submission readiness.

## 3. Security

- Binds to `127.0.0.1` only; a foreign `Host` header gets 403 (DNS-rebinding defence); a cross-origin POST gets 403.
- Serves only files under `paper/figures`, `paper/tables`, `paper/*.pdf`, and `demo/`, only image, PDF, and audio types, and rejects path traversal.
- The only action it can run is `paper_check.py PROJECT ready`.
- Nothing leaves the machine; the page makes no external requests.

## 4. Practical notes

- Use `--port` if 8765 is taken. Stop with Ctrl+C.
- If a file is mid-edit and unreadable, the page shows the message and recovers on the next refresh.
- The dashboard serves the demo site with HTTP Range support, so audio seeking and the blind test work from `/demo/`.
- It is read-only for your manuscript; run the checks, builds, and experiments through the scripts or the agent.
