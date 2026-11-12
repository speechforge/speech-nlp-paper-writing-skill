# Figures, Plots, Tables, and Visuals

Visual quality is content. Readers go title, abstract, introduction, **figures**, and only then the body. This file adds tooling and a workflow to the existing rules in `03` (Figure 1 as teaser, minimal-ink tables) and `08` (>=1600 DPI raster, vector PDF/EPS preferred, font embedding, booktabs).

---

## 1. Two classes of visual (classify before choosing a tool)

| Class | Use for | Allowed backends | Never |
|---|---|---|---|
| **Evidence** | numbers: results, ablations, trends, Pareto, heatmaps, spectrogram comparisons, tables | deterministic scripts only (`make_plots.py`, `make_latex_table.py`, `make_audio_figs.py`) | image generators, hand-drawn numbers |
| **Concept** | teaser, pipeline, architecture, mechanism, failure-mode illustration | `make_diagram.py` (always available) or an image generator when the agent has one | exact values, axes, metrics, tables, anything a reader could mistake for data |

Generated or drawn concept figures explain an idea. They are never experimental evidence.

---

## 2. Plan first: `figure_plan.md`

One row per figure or table: class, role (teaser, method overview, result, ablation, failure analysis, qualitative), the single message, the source data file or spec, the tool, caption status, and whether it also goes on the website. A figure that cannot state one message does not earn its space.

Required set for a typical paper: Figure 1 teaser (problem and remedy, understandable from the caption alone), a method overview, one main-result table, one ablation figure or table, one qualitative figure (spectrograms, example outputs, or attention), and one failure-case or trade-off figure (Pareto of quality against cost).

---

## 3. Tools

### Result plots: `make_plots.py`
```bash
python3 scripts/make_plots.py bar    results.csv --x method --y mos --group dataset --highlight Ours \
        --ylabel "MOS (higher is better)" --width ieee-col --out paper/figures/fig_mos
python3 scripts/make_plots.py line   results.csv --x snr --y wer --series method --out paper/figures/fig_noise
python3 scripts/make_plots.py pareto results.csv --x rtf --y mos --label method --xlog --highlight Ours --out paper/figures/fig_pareto
python3 scripts/make_plots.py heat   results.csv --row language --col metric --value score --out paper/figures/fig_langs
```
- Repeated rows (seeds) become mean and sample standard deviation automatically; the script prints the **caption hint** stating exactly what the bars and bars' whiskers mean. Paste it. A `--err` column (CI half-width) overrides.
- Outputs: `.pdf` (vector, fonts embedded as TrueType 42), `.png` (print DPI, default **1600**, the lab rule for raster line art), `_web.png` (200 DPI for the website and dashboard), and `.source.json` (command, input hash, plotted numbers).
- Widths: `ieee-col` 3.5 in, `ieee-wide` 7.16 in, `acl-col` 3.03 in, `acl-wide` 6.3 in, `single` 6 in, or a number.
- The proposed method is vermillion; other series use the Okabe-Ito palette. In grouped bars, colour encodes the group and the proposed method is marked by a heavy outline and bold label, so the legend is never contradicted. Hatching and markers keep figures readable in grayscale.

### Concept diagrams: `make_diagram.py`
```bash
python3 scripts/make_diagram.py diagrams/method.json --out paper/figures/fig_method --width ieee-wide
```
A JSON spec of blocks and edges; blocks marked `"new": true` get the accent outline so the figure shows **what is new in this work**. Long forward edges ride a lane above the blocks and feedback edges a lane below, so no connector crosses an unrelated block. Use two-line labels at most.

When the agent has an image generator, it may produce a polished illustration of the same idea. Use a six-part prompt (framing and takeaway, visual style, exact hex palette, layout regions, every arrow and label, constraints: no logos, no fake numbers, no tiny text). Inspect the result; regenerate if labels are wrong; keep the prompt next to the asset. Keep exact labels as a deterministic overlay when needed.

### Speech and audio visuals: `make_audio_figs.py`
```bash
python3 scripts/make_audio_figs.py spec ref.wav baseline.wav ours.wav --labels "Reference,Baseline,Ours" \
        --fmax 8000 --wave --out paper/figures/fig_spec
```
All panels share one dB scale relative to the loudest clip, so visible differences are real rather than an artefact of per-panel normalisation. State this in the caption (the script prints it). Pick examples by a stated rule (random, or worst-case and median), not only the best.

### Tables: `make_latex_table.py`
```bash
python3 scripts/make_latex_table.py results.csv --aggregate method --columns method,mos,rtf \
        --names "Method,MOS,RTF" --direction mos:up,rtf:down --family ieee --caption "..." --label tab:main -o paper/tables/main.tex
```
Zero vertical rules; direction arrows in headers; units in headers, not cells; bold only the best value per column when a direction is given; `X_ci`/`X_std` columns merge into "value $\pm$ interval"; caption **above** for the IEEE family and **below** for ACL. Bold the best only when it is outside the confidence interval of the next, otherwise bold none or both.

---

## 4. Rules that apply to every figure

1. One message per figure; Figure 1 is placed at the top of the first page (IEEE: top of column 2 on page 1).
2. Vector for plots and diagrams; raster at >=1600 DPI only for line art that must be raster, 600 DPI floor for photographs.
3. Colour-blind-safe palette (Okabe-Ito or Paul Tol), grayscale-legible, no information carried by colour alone.
4. No title inside the figure; the caption carries it. Captions are miniature arguments: what is shown, the encoding and metric direction, the takeaway, and a caveat only if needed. Each caption stands alone.
5. Text readable at final print size (8 pt minimum); check at final width.
6. Label every axis with a quantity and unit; include metric direction.
7. Do not use 3D bars, pie charts for model comparison, heavy gridlines, or unexplained dual axes.
8. Every figure is referenced in the text before or near where it appears, with its takeaway stated.
9. Every number in a figure matches the source data; keep `.source.json`.
10. Do not publish identifying details in anonymous submissions (file metadata, watermark, speaker names).

## 5. QA before submission

View each figure at final width; check grayscale; confirm labels match paper terminology; confirm numbers against the source; confirm file sizes are reasonable (web copies are small); confirm every `\includegraphics` resolves (`paper_check.py PROJECT assets`).
