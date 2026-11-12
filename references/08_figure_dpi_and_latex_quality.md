# Figure Quality, DPI Standards & LaTeX PDF Compilation Rules
## Lab — IEEE Conference Submission Standards

---

## PART 1: Figure DPI and Image Quality Requirements

### Rule 1: Minimum DPI for Raster Images
- **Minimum**: **1600 DPI** for all raster figures (PNG, TIFF, BMP) embedded in the PDF.
- **Preferred**: **300–600 DPI** for grayscale halftone figures. **1200 DPI** for lineart (diagrams, block diagrams). **1600+ DPI** for mixed/color images.
- IEEE Xplore PDF standards: at least 300 DPI for color/grayscale, 600–1200 DPI for black & white lineart, but **Lab standard = 1600 DPI minimum** to ensure no pixelation under print zoom.

> [!CAUTION]
> Never export figures from PowerPoint or screenshot-capture at screen resolution (72–96 DPI). These will appear blurry in the printed PDF and will fail IEEE PDF compliance checks.

### Rule 2: Vector vs. Raster — When to Use Which

| Figure Type | Format | Reason |
|---|---|---|
| Block diagrams, architecture charts | **PDF / SVG / EPS (vector)** | Infinitely scalable; zero pixelation at any zoom |
| Loss/training curves, spectrograms | **PDF / EPS (vector via matplotlib)** | Axes, tick marks, and text render crisply |
| Listening test screenshots | **PNG at ≥1600 DPI** | Only use raster when vector is not possible |
| Waveform comparisons | **PDF / SVG (vector)** | Waveform edges must be sharp |
| Photos of hardware/equipment | **TIFF or PNG at ≥600 DPI** | Raster-only content |

✅ **CORRECT**: Export matplotlib/seaborn plots as `.pdf` or `.eps`:
```python
plt.savefig('figure1.pdf', format='pdf', bbox_inches='tight', dpi=300)
# Or for PNG fallback:
plt.savefig('figure1.png', format='png', dpi=1600, bbox_inches='tight')
```

❌ **WRONG**: `plt.savefig('figure1.png', dpi=100)` — Will produce a blurry, pixelated figure.

---

### Rule 3: LaTeX Figure Embedding

Always embed figures using `\includegraphics` with explicit width control:

```latex
\begin{figure}[t]
  \centering
  \includegraphics[width=\columnwidth]{figures/figure1.pdf}
  \caption{Comparison of (a) the proposed Model-A architecture, 
           and (b) the conventional attention-based VC baseline.}
  \label{fig:architecture}
\end{figure}
```

For two-column spanning figures:
```latex
\begin{figure*}[t]
  \centering
  \includegraphics[width=\textwidth]{figures/main_results.pdf}
  \caption{Benchmark-D evaluation results across five dimensions...}
  \label{fig:prism_results}
\end{figure*}
```

> [!IMPORTANT]
> Use `[t]` (top-of-page placement) for Figure 1 in IEEE 2-column format. Never use `[h]` (here) for important figures — it causes them to float unpredictably and may push the figure away from its citation location.

---

### Rule 4: Subfigure Labeling

✅ **CORRECT format** (from Model-B paper):
```
Fig. 1. Comparison of raw speech waveform generation between (a) The
proposed Model-B, and (b) the traditional GAN architecture.
```

In LaTeX using `subcaption` package:
```latex
\usepackage{subcaption}

\begin{figure}[t]
  \centering
  \begin{subfigure}[b]{0.48\columnwidth}
    \includegraphics[width=\textwidth]{figures/proposed.pdf}
    \caption{Proposed Model-B}
  \end{subfigure}
  \hfill
  \begin{subfigure}[b]{0.48\columnwidth}
    \includegraphics[width=\textwidth]{figures/baseline.pdf}
    \caption{Traditional GAN}
  \end{subfigure}
  \caption{Comparison of (a) the proposed Model-B and (b) the traditional GAN architecture.}
  \label{fig:architecture}
\end{figure}
```

---

### Rule 5: Font Sizes in Figures

| Element | Minimum Font Size |
|---|---|
| Axis labels | 8pt |
| Tick labels | 7pt |
| Legend text | 7pt |
| Annotation text | 7pt |
| Figure caption | As per IEEE (8–9pt) |

❌ **WRONG**: Tiny axis labels that become unreadable when the figure is resized to fit the column width. Always design figures at their intended print size (single column = ~8.5cm, double column = ~17.5cm).

```python
# matplotlib settings for publication-quality figures
import matplotlib as mpl
mpl.rcParams.update({
    'font.size': 8,
    'axes.labelsize': 8,
    'xtick.labelsize': 7,
    'ytick.labelsize': 7,
    'legend.fontsize': 7,
    'figure.figsize': (3.5, 2.5),  # Single-column width in inches
    'savefig.dpi': 1600,
    'savefig.format': 'pdf',
    'font.family': 'serif',
    'font.serif': ['Times New Roman'],  # Matches IEEEtran
})
```

---

### Rule 6: Color Usage in IEEE Figures

- Use colors **only when they will be visible in both color and grayscale** (the PDF may be printed in black and white).
- Preferred color-safe pairs: Blue/Orange, Blue/Red, avoid Red/Green (colorblind unfriendly).
- Always add a distinguishing **line style** (`-`, `--`, `-.`, `:`) in addition to color in plots.

✅ **CORRECT**:
```python
plt.plot(epochs, train_loss, 'b-', linewidth=1.5, label='Train Loss')
plt.plot(epochs, val_loss, 'r--', linewidth=1.5, label='Validation Loss')
```

❌ **WRONG**: Using only color differentiation with no line style variation (fails grayscale print).

---

### Rule 7: Figure Caption Format

✅ **CORRECT** (IEEE IEEEtran style):
```
Fig. 1. Comparison of raw speech waveform generation between (a) The proposed Model-B, and (b) the traditional GAN architecture.
```

Rules:
- Abbreviated: **`Fig. 1.`** (not `Figure 1.`, not `FIG. 1`)
- One space after period.
- Caption text begins with a capital letter.
- Caption ends with a period.
- When referencing subfigures in the caption body: lowercase `(a)`, `(b)`.
- In text, refer to figures as: `Fig. 1`, `Figs. 1 and 2`.

❌ **WRONG**:
- `Figure 1: Comparison...` (wrong — should be `Fig. 1.`, not `Figure 1:`)
- `FIG. 1 — Comparison...` (wrong capitalization and dash format)

---

### Rule 8: Table Formatting Rules

✅ **CORRECT format** (from Model-B paper, Table II):
```latex
\begin{table}[t]
\renewcommand{\arraystretch}{1.2}
\caption{COMPARISON OF OBJECTIVE AND SUBJECTIVE MEASURES (REPORTED
WITH 95\% CI), ON SYNTHETIC AND GT FOR INDICVOICES-R DATASET}
\label{tab:results}
\centering
\begin{tabular}{lccccc}
\toprule
\textbf{Method} & \textbf{PCC} $(\uparrow)$ & \textbf{PESQ} $(\uparrow)$ & \textbf{STOI} $(\uparrow)$ & \textbf{MSD} $(\downarrow)$ & \textbf{SMOS} $(\uparrow)$ \\
\midrule
GT             & --   & --   & --   & --    & 4.62 \\
MelGAN [4]     & 0.18 & 0.59 & 0.12 & 76.82 & 1.86 \\
HiFi-GAN [11]  & --0.00 & 2.22 & 0.84 & 37.09 & 3.09 \\
\textbf{Model-B (Proposed)} & \textbf{0.01} & \textbf{2.64} & \textbf{0.93} & \textbf{25.20} & \textbf{4.51$_{\pm 0.12}$} \\
\bottomrule
\end{tabular}
\end{table}
```

**Table Caption Rules**:
- In IEEEtran, `\caption{}` appears **ABOVE** the table (unlike figures where it appears below).
- Table caption in **FULL UPPERCASE**: `COMPARISON OF OBJECTIVE AND SUBJECTIVE MEASURES...`
- Table label: `TABLE I`, `TABLE II` (Roman numerals in uppercase).
- Use `\toprule`, `\midrule`, `\bottomrule` from the `booktabs` package. **Zero vertical lines**.
- Bold the proposed method row: `\textbf{Model-B (Proposed)}`.
- Bold the best numbers per column.
- Report uncertainty inline: `4.51$_{\pm 0.12}$`.
- Metric columns must include directional arrows: `$(\uparrow)$` or `$(\downarrow)$`.
- Include a **GT (Ground Truth)** row as the top anchor reference.

---

## PART 2: LaTeX Compilation and PDF Quality Rules

### Rule 9: Document Class

Always use the official IEEEtran class for IEEE conferences:
```latex
\documentclass[10pt,conference]{IEEEtran}
```
For INTERSPEECH (Springer LNCS) or other venues, use the appropriate class.

---

### Rule 10: Required Package List

```latex
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{amsmath, amssymb}     % Math
\usepackage{graphicx}              % Figures
\usepackage{booktabs}              % Professional tables: \toprule \midrule \bottomrule
\usepackage{subcaption}            % (a) (b) subfigures
\usepackage{url}                   % URL formatting in references
\usepackage{hyperref}              % Clickable links (use cautiously in IEEE — some require removal)
\usepackage{cite}                  % Sorted [1,2,3] citation format
\usepackage{microtype}             % Improved typography and hyphenation
```

---

### Rule 11: Compilation Command

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

Or for clean builds:
```bash
latexmk -C && latexmk -pdf -interaction=nonstopmode main.tex
```

---

### Rule 12: Pre-Submission PDF Checklist

Before submitting to IEEE Xplore / EDAS / CMT:

```bash
# Check for placeholder text that must be removed before submission:
grep -n "PENDING\|TBD\|TODO\|placeholder\|XX\|??" main.tex
grep -n "\\\\pending\|\\\\tbd\|\\\\draftnote" main.tex

# Check for overfull hboxes (text overflowing columns):
grep "Overfull" main.log

# Check PDF file size (IEEE: often max 10 MB):
du -sh main.pdf

# Check page count:
pdfinfo main.pdf | grep "Pages:"

# Verify all figures are embedded (not linked):
pdffonts main.pdf
```

---

### Rule 13: IEEE PDF Compliance (IEEE PDF eXpress)

Before submitting to any IEEE venue, run the PDF through **IEEE PDF eXpress** at `https://www.pdf-express.org/`:
1. Create an account with the conference ID.
2. Upload the PDF.
3. The system verifies: fonts embedded, margins correct, resolution compliant.
4. Download the certified PDF for submission.

> [!IMPORTANT]
> IEEE PDF eXpress will reject PDFs with non-embedded fonts or raster figures below 300 DPI. Use `\usepackage{microtype}` and embed all fonts by compiling with `pdflatex` or `lualatex`.

---

### Rule 14: Embedding Fonts

Ensure all fonts are embedded. Run after compilation:
```bash
pdffonts main.pdf
# Look for 'emb' column = 'yes' for all fonts
```

If fonts are not embedded, force embedding:
```bash
gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite -dEmbedAllFonts=true \
   -dSubsetFonts=true -sOutputFile=main_embedded.pdf main.pdf
```

---

### Rule 15: Margins (IEEEtran Default)

IEEEtran handles margins automatically. **Never override margins with geometry package** in IEEE submissions. If using a different class, verify:
- Top: 0.75 in, Bottom: 1.0 in, Left/Right: 0.625 in (letter paper)

---

### Rule 16: Supplementary Website URL Format

✅ **CORRECT** (from Model-A):
```latex
The demo utterances are publicly available at supplementary website:
\url{https://example.github.io/demo/}
```

✅ **CORRECT** (from Model-B):
```latex
at website\footnote{\url{https://example.github.io/demo/}}
```

Rules:
- Use `\url{}` for all URLs in the text body and footnotes.
- Footnote URLs: use the `\footnote{\url{...}}` format.
- Use HTTPS, not HTTP.
- Use proper GitHub Pages format: `username.github.io/project-name/`

---

## PART 3: Figure Design Standards (Matplotlib Recipes)

### Recipe 1: Block Diagram / Architecture Figure (For Figure 1)

```python
# Use matplotlib patches and arrows for architecture block diagrams
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch

fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.5))

# (a) Proposed architecture
# Draw blocks using mpatches.FancyBboxPatch
# (b) Baseline architecture
# Draw blocks using simple Rectangle

# Save at 1600 DPI as PDF:
plt.tight_layout()
plt.savefig('fig1_architecture.pdf', format='pdf', bbox_inches='tight')
plt.savefig('fig1_architecture.png', format='png', dpi=1600, bbox_inches='tight')
```

### Recipe 2: Results Comparison Plot

```python
import matplotlib.pyplot as plt
import numpy as np

mpl.rcParams.update({'font.size': 8, 'font.family': 'serif'})

methods = ['GT', 'MelGAN', 'P.WaveGAN', 'HiFi-GAN', 'BigVGAN', 'Model-B\n(Proposed)']
smos = [4.62, 1.86, 2.02, 3.09, 4.39, 4.51]
colors = ['gray', 'steelblue', 'steelblue', 'steelblue', 'steelblue', 'darkorange']

fig, ax = plt.subplots(figsize=(3.5, 2.5))
bars = ax.bar(methods, smos, color=colors, edgecolor='black', linewidth=0.5)
ax.set_ylabel('SMOS (↑)', fontsize=8)
ax.set_ylim(0, 5.2)
ax.axhline(y=4.62, color='gray', linestyle='--', linewidth=0.8, label='GT')
ax.legend(fontsize=7)
plt.xticks(rotation=15, ha='right', fontsize=7)
plt.tight_layout()
plt.savefig('smos_comparison.pdf', format='pdf', bbox_inches='tight')
plt.savefig('smos_comparison.png', format='png', dpi=1600, bbox_inches='tight')
```

### Recipe 3: Spectrogram Figure

```python
import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt

# Load generated and ground truth audio
y_gt, sr = librosa.load('ground_truth.wav', sr=22050)
y_gen, sr = librosa.load('generated.wav', sr=22050)

fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.5))

# GT spectrogram
D_gt = librosa.amplitude_to_db(np.abs(librosa.stft(y_gt, n_fft=1024, hop_length=256)), ref=np.max)
librosa.display.specshow(D_gt, sr=sr, hop_length=256, y_axis='mel', x_axis='time', ax=axes[0])
axes[0].set_title('(a) Ground Truth', fontsize=8)
axes[0].set_xlabel('Time (s)', fontsize=8)
axes[0].set_ylabel('Frequency (Hz)', fontsize=8)

# Generated spectrogram
D_gen = librosa.amplitude_to_db(np.abs(librosa.stft(y_gen, n_fft=1024, hop_length=256)), ref=np.max)
librosa.display.specshow(D_gen, sr=sr, hop_length=256, y_axis='mel', x_axis='time', ax=axes[1])
axes[1].set_title('(b) Proposed Model-B', fontsize=8)
axes[1].set_xlabel('Time (s)', fontsize=8)
axes[1].set_ylabel('', fontsize=8)

plt.tight_layout()
plt.savefig('spectrogram_comparison.pdf', format='pdf', bbox_inches='tight')
plt.savefig('spectrogram_comparison.png', format='png', dpi=1600, bbox_inches='tight')
```

---

## PART 4: Pre-Submission Figure Quality Checklist

Before generating the final PDF:

- [ ] All figures exported at **≥1600 DPI** (PNG) or as **vector PDF/EPS**
- [ ] All fonts in figures embedded (not linked)
- [ ] Figure text is readable at 100% zoom in the final PDF (minimum 7pt)
- [ ] Architecture block diagrams use clean, equal-spaced boxes and arrows
- [ ] No jagged edges or pixelation visible at 300% zoom in Acrobat Reader
- [ ] All subfigures labeled with `(a)`, `(b)` etc.
- [ ] Figure captions follow `Fig. X.` format with period
- [ ] Figure 1 placed at top-right of Page 1 in 2-column IEEE layout
- [ ] Spectrogram color maps are consistent across all figures (use `magma` or `viridis`)
- [ ] Tables use `booktabs` (`\toprule`, `\midrule`, `\bottomrule`), no vertical lines
- [ ] Table captions appear ABOVE the table in IEEEtran
- [ ] Table captions are in FULL UPPERCASE
- [ ] Metric direction arrows `(↑)` or `(↓)` in every column header
- [ ] Ground Truth (GT) row included in all results tables
- [ ] Best results bolded per column
- [ ] 95% CI reported for all subjective scores
- [ ] PDF compiled without overfull hboxes
- [ ] PDF checked in IEEE PDF eXpress before submission
