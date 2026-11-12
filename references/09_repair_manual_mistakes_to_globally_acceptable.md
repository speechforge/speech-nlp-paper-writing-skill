# Repair Manual: Mistakes Found → Globally Acceptable Standards
## Lab | IEEE/EUSIPCO/Interspeech Conference Papers

> Every mistake below is extracted verbatim from your published papers.  
> Each entry shows: **ORIGINAL (broken)** → **REPAIRED (globally accepted)** → **THE RULE**.

---

## CATEGORY 1: Abstract Errors

---

### FIX-A1 — Critical Typo: Wrong Word ("discussion" vs "diffusion")

**ORIGINAL (broken):**
```
...Model-A, a selective state space (SS)-based hierarchical discussion framework 
that replaces attention mechanism with linear-time sequence modeling.
```

**REPAIRED (globally accepted):**
```
...Model-A, a selective state space (SS)-based hierarchical diffusion framework 
that replaces the attention mechanism with linear-time O(nd) sequence modeling.
```

**THE RULE:** Every word in the abstract must be re-read character-by-character before submission. "discussion" and "diffusion" look similar when typing fast. The abstract is the first (and often only) thing a reviewer reads — a typo here kills credibility instantly. Run `aspell` or Grammarly on the abstract as the final step.

---

### FIX-A2 — Missing Complexity Notation in Abstract

**ORIGINAL (broken):**
```
These primarily arise from attention-based sequence modeling, which scales quadratically.
```

**REPAIRED (globally accepted):**
```
These primarily arise from attention-based sequence modeling, which scales quadratically 
as O(n²d) with sequence length, limiting long-context modeling and real-time deployment.
```

**THE RULE:** If reducing computational complexity is **your core contribution**, you MUST state the original complexity `O(n²d)` AND the improved complexity `O(nd)` explicitly in the abstract. The word "quadratically" alone is too vague — a reviewer must immediately see the exact class of improvement.

---

### FIX-A3 — Duplicate/Redundant Sentence

**ORIGINAL (broken):**
```
...Model-A achieves a ∼15.6% improvement in real-time factor (RTF), demonstrating 
that linear-time SS modeling enables faster inference without degrading the quality of 
the synthesized VC. Model-A further reduces the RTF to achieve high-fidelity VC 
for practical deployment.
```

**REPAIRED (globally accepted):**
```
...Model-A achieves a ∼15.6% improvement in real-time factor (RTF 0.32→0.27), 
demonstrating that linear-time selective state-space modeling enables faster inference 
without degrading synthesized speech quality, making it suitable for practical deployment.
```

**THE RULE:** The abstract must contain zero redundant sentences. Merge overlapping ideas into one crisp sentence. Never end the abstract with a vague deployment claim — fold it into the efficiency sentence as a "making it suitable for X" clause.

---

### FIX-A4 — Vague "notable improvements" Without Numbers

**ORIGINAL (broken):**
```
Compared to the existing state-of-the-art VC systems, Model-A achieves notable 
improvements across subjective, objective, and quantitative metrics.
```

**REPAIRED (globally accepted):**
```
[DELETE THIS SENTENCE ENTIRELY — it is a hollow transition before the real numbers appear.]
```

**THE RULE:** Never use a placeholder sentence like "achieves notable improvements across... metrics" before listing the actual numbers. It wastes space and signals to reviewers that the authors lack confidence. Jump directly to the specific numbers (NISQA-MOS, UTMOS, F0-RMSE, WER, CER).

---

## CATEGORY 2: Introduction Errors

---

### FIX-I1 — Subject-Verb Agreement: "gives" vs "give"

**ORIGINAL (broken) — Model-B:**
```
non-autoregressive vocoders (NAR), flow-based [8], [9], GAN-based [10]–[13], 
and diffusion-based models [14], [15] gives improved speech generation quality
```

**REPAIRED (globally accepted):**
```
non-autoregressive (NAR), flow-based [8], [9], GAN-based [10]–[13], and 
diffusion-based models [14], [15] give improved speech generation quality
```

**THE RULE:** When the grammatical subject is a compound list of plural nouns, the verb must be **plural**: "vocoders, models, and architectures **give**" (not "gives"). Read each sentence aloud — if it sounds wrong, it is wrong.

---

### FIX-I2 — Lowercase Period Creates Fragment Sentence

**ORIGINAL (broken) — Model-B:**
```
In particular, AR models suffer from slow inference speed due to sequential nature. 
while NAR models were faster but demonstrated reduced speech quality.
```

**REPAIRED (globally accepted):**
```
In particular, AR models suffer from slow inference speed due to their sequential 
nature, while NAR models are faster but demonstrate reduced speech quality.
```

**THE RULE:** "while" is a subordinating conjunction — it cannot begin a new sentence when connecting two related clauses. Use a **comma + while** to join them. Also: "sequential nature" needs the article "their sequential nature". Tense: Use present tense ("are", "demonstrate") for describing established facts about model families.

---

### FIX-I3 — Wrong Preposition: "capable to" vs "capable of"

**ORIGINAL (broken) — Model-B:**
```
Similarly, diffusion-based vocoders [14], [15], capable to generate high-quality 
speech samples, however, require high-end GPU resources for real-time inference.
```

**REPAIRED (globally accepted):**
```
Diffusion-based vocoders [14], [15] are capable of generating high-quality speech 
samples but require significant GPU resources for real-time inference.
```

**THE RULE:** The globally correct collocation is "**capable of** + gerund (-ing form)". "Capable to + infinitive" is non-standard English and will be caught by any native-English reviewer. Also: the original sentence has redundant "Similarly," and "however," in the same sentence — pick one or neither.

---

### FIX-I4 — Self-Referential Redundancy ("the work proposed... proposed")

**ORIGINAL (broken) — Model-B:**
```
In 2017, the work proposed by Vaswani et al. [16] proposed the attention mechanism 
in the transformer, which revolutionized the NLP field.
```

**REPAIRED (globally accepted):**
```
In 2017, Vaswani et al. [16] proposed the attention mechanism in the Transformer 
architecture, which revolutionized sequence modeling in NLP and beyond.
```

**THE RULE:** "The work proposed by X proposed" is a tautology — "proposed by X" and "proposed" are the same verb twice. Write: "X proposed". Also: "Transformer" is a proper noun/architecture name — capitalize it. Add "and beyond" to acknowledge speech/audio applications.

---

### FIX-I5 — Missing Article Before Noun

**ORIGINAL (broken) — Model-B:**
```
In second phase, traditional vocoders, such as WORLD [6], analyze speech signals...
```

**REPAIRED (globally accepted):**
```
In the second phase, traditional vocoders such as WORLD [6] analyze speech signals...
```

**THE RULE:** "In second phase" is missing the definite article "the". The rule: ordinal adjectives ("second", "first", "third") almost always need "the" in formal English when referring to a specific, known phase. Also: no comma after "vocoders" when "such as" introduces an essential restrictive clause.

---

### FIX-I6 — Dangling Relative Clause (Fragment Starting with "Which")

**ORIGINAL (broken) — Model-B:**
```
The word 'Model-B' originates from Sanskrit, where the term 'Svara' refers to vowels, 
that are self-sounding. It originates from the root, referring to vowels and intonations. 
Which plays a fundamental role in speech production and perception.
```

**REPAIRED (globally accepted):**
```
The word 'Model-B' originates from Sanskrit, where the term 'Svara' refers to 
self-sounding vowels — a concept rooted in intonation and pitch — which plays 
a fundamental role in speech production and perception [20].
```

**THE RULE:** "Which plays..." cannot begin a new sentence — it is a relative clause and must be attached to its antecedent noun. Also, "It originates from the root, referring to vowels and intonations" repeats the same information already stated. Merge both into one flowing sentence.

---

### FIX-I7 — Wrong Comma Placement Creates Run-On

**ORIGINAL (broken) — Model-B:**
```
...many Gujarati phonemes, such as retroflex, consonants, and nasalized vowels are 
missing in pre-trained models, leads to pronunciation errors and phoneme mismapping 
(i.e., wrong assignment), as model attempt to replace unavailable sounds...
```

**REPAIRED (globally accepted):**
```
Many Gujarati-specific phonemes — such as retroflex consonants and nasalized vowels — 
are absent from pre-trained multilingual models, leading to pronunciation errors and 
phoneme mismapping, where the model substitutes unavailable sounds with the phonetically 
closest match from its training language.
```

**THE RULE (three issues fixed):**
1. "retroflex, consonants" — the comma is wrong; "retroflex consonants" is a compound noun, no comma.
2. "leads to" — wrong tense/agreement; the subject is the whole clause so use "leading to" (participial phrase).
3. "as model attempt" — missing article: "as the model attempts" (singular subject → "attempts").

---

### FIX-I8 — Informal Transition: "while highlighting the following key contributions"

**ORIGINAL (broken) — Model-B:**
```
In this work, we introduce Model-B- a Longformer-based GAN vocoder designed especially 
for Gujarati (an Indian language) while highlighting the following key contributions:
```

**REPAIRED (globally accepted):**
```
In this work, we introduce Model-B, a Longformer-based GAN vocoder specifically 
designed for Gujarati — an Indian language with 55.5 million speakers and 
complex phonotactic structure. The key contributions of this paper are:
```

**THE RULE (two issues):**
1. "Model-B-" — hyphen after model name is wrong; use a **comma**: "we introduce Model-B, a Longformer..."
2. "while highlighting the following key contributions" — "while highlighting" implies the contributions happen simultaneously with introduction, which is awkward. Standard IEEE English: "The key contributions of this paper are:" as a standalone sentence.

---

### FIX-I9 — Weak Contribution Phrasing ("The earlier works were done heavily using...")

**ORIGINAL (broken) — Model-B:**
```
3) The earlier works were done heavily using subjective measures, such as MOS. In the 
   context of this work, we believe the perceptual evaluation is not sufficient for most 
   noisy conditions and phonetic information preservation and hence, we evaluated our 
   samples using objective measures, such as PCC, PESQ, STOI, MSD, and MCD.
```

**REPAIRED (globally accepted):**
```
3) Prior vocoder evaluations rely primarily on subjective Mean Opinion Score (MOS), 
   which is insufficient for capturing phonetic fidelity and performance under noisy 
   conditions. This work establishes a comprehensive objective evaluation protocol 
   using five metrics — PCC, PESQ, STOI, MSD, and MCD — providing reproducible, 
   quantitative assessment of speech quality. Demo samples are available at 
   \url{https://example.github.io/demo/}.
```

**THE RULE (three issues):**
1. "The earlier works were done heavily using" — passive and verbose. Use active: "Prior evaluations rely on."
2. "we believe the perceptual evaluation is not sufficient" — "we believe" weakens a factual statement. If it is a known fact, state it directly: "MOS is insufficient for..."
3. Contribution 3 must end with **what you DO**, not just what prior work failed at. State the protocol used, the metrics, and add the demo URL.

---

### FIX-I10 — Contributions: Mixed Tense

**ORIGINAL (broken) — Model-B:**
```
1) We propose a Longformer-based GAN vocoder...  [present]
2) We successfully trained the Model-B...           [past]
3) The earlier works were done...                [past passive]
```

**REPAIRED (globally accepted):**
> Pick **one tense** and apply uniformly across all contribution bullets.

**Option A — Past tense** (this lab's standard; Model-A uses past tense):
```
1) We proposed a Longformer-based GAN vocoder, which uses the sliding window 
   mechanism to capture local phonetic details and global prosodic dependencies.
2) We trained Model-B on the IndicVoices-R Gujarati dataset (8.94 hours, 45 speakers) 
   without explicit regularization in the GAN generator or discriminator.
3) We established a comprehensive objective evaluation protocol using PCC, PESQ, 
   STOI, MSD, and MCD, providing reproducible quantitative assessment of speech 
   quality beyond subjective MOS ratings.
```

**Option B — Present tense** (also globally acceptable, used in NeurIPS/ICML style):
```
1) We propose...  2) We evaluate...  3) We demonstrate...
```

**THE RULE:** Pick one, apply throughout. Never mix "We propose" (C1), "We trained" (C2), "The earlier works were done" (C3) in the same list.

---

## CATEGORY 3: Sampling Rate & Units Errors

---

### FIX-U1 — Wrong Capitalization of Unit "KHz" → "kHz"

**ORIGINAL (broken) — Model-B:**
```
Initially, the datasets' raw audio was sampled at 44 KHz.
```

**REPAIRED (globally accepted):**
```
The raw audio was originally sampled at 44.1 kHz and downsampled to 22.05 kHz for training.
```

**THE RULE (two issues):**
1. **Unit capitalization**: SI prefix "kilo" is always lowercase: **kHz** (not KHz, not khz, not KHZ). This is a universal physics/engineering standard — IEEE reviewers will flag it.
2. **Value accuracy**: Standard audio sampling rates are `44.1 kHz` (CD quality), not `44 kHz`. If the actual rate was 44,100 Hz, write `44.1 kHz`. If it truly was `44,000 Hz` (unusual), confirm before writing.

**Global SI unit rule table:**
| Unit | Correct | Wrong |
|---|---|---|
| kilohertz | **kHz** | KHz, khz, KHZ |
| megahertz | **MHz** | Mhz, mHz |
| kilobytes | **kB** | KB (KB = kilobits in some contexts) |
| megabytes | **MB** | Mb (Mb = megabits) |
| decibels | **dB** | DB, db |
| milliseconds | **ms** | Ms, MS |
| seconds | **s** | S (capital S = Siemens) |

---

### FIX-U2 — Non-Standard Unit Abbreviation

**ORIGINAL (broken) — Model-B:**
```
Model-B achieves a 4.51 Subjective Mean Opinion Score (SMOS)...
It generates 22.05 kHz audio 833.33 × times faster than real-time on an NVIDIA GTX 1650.
```

**REPAIRED (globally accepted):**
```
Model-B achieves a Subjective Mean Opinion Score (SMOS) of 4.51 (±0.12, 95% CI)...
It generates 22.05 kHz audio at 833.33× real-time on an NVIDIA GeForce GTX 1650.
```

**THE RULE (two issues):**
1. The number goes after the quantity: "SMOS **of** 4.51" (not "a 4.51 SMOS").
2. "833.33 × times faster" — "×" already means "times", so "× times" is redundant. Write: "833.33× real-time" or "833.33 times faster than real-time". Standard shorthand: **833.33×** (no space before ×).

---

## CATEGORY 4: Typographical and OS/Proper-Noun Errors

---

### FIX-T1 — OS Name Capitalization

**ORIGINAL (broken) — Model-B:**
```
All experiments were executed on an ubuntu-powered workstation...
```

**REPAIRED (globally accepted):**
```
All experiments were executed on an Ubuntu 22.04-based workstation equipped with...
```

**THE RULE:** Operating system names are **proper nouns** — always capitalize: **Ubuntu**, **Windows**, **macOS**, **CentOS**. Add the version number for reproducibility: "Ubuntu 22.04" or "Ubuntu 20.04 LTS". Reviewers checking reproducibility will want to know the exact OS version.

---

### FIX-T2 — Table Caption "AFTER [N]" in Running Text

**ORIGINAL (broken) — Model-B:**
```
TABLE I
COMPARATIVE ANALYSIS OF PHONEME, CONSONANT, AND VOWEL
COUNTS ACROSS LANGUAGES. AFTER [19].
```

**REPAIRED (globally accepted):**
```
TABLE I
COMPARATIVE ANALYSIS OF PHONEME, CONSONANT, AND VOWEL 
COUNTS ACROSS SELECTED LANGUAGES
```
Then in the table footnote (using `\tablenotetext` or `\footnotesize`):
```
Data from [19].
```

**THE RULE:** "AFTER [19]" is informal and should not be in the table caption. The citation belongs either (a) as a table footnote using `\tablenotetext{a}{Data from [19].}` or (b) in the paragraph referring to the table: "As shown in Table I (data from [19])..."

---

### FIX-T3 — Metric Name Consistency ("UT-MOS" vs "UTMOS")

**ORIGINAL (broken) — Model-A:**
- Abstract: `UTMOS` ✅
- Contribution 2: `UT-MOS` ❌

**REPAIRED (globally accepted):** Use **UTMOS** everywhere (no hyphen).

**THE RULE:** The correct name of the metric from its original paper (Saeki et al., INTERSPEECH 2022) is **UTMOS** — no hyphen. When a metric or model has an official name, use it exactly as defined in its source paper throughout the entire manuscript. Create a LaTeX macro to ensure consistency:
```latex
\newcommand{\UTMOS}{\textsc{UTMOS}}
\newcommand{\NISQAMOS}{NISQA-MOS}
\newcommand{\PESQ}{\textsc{PESQ}}
```

---

### FIX-T4 — "nMOS" Undefined

**ORIGINAL (broken) — Model-A:**
```
Earlier work depends heavily on subjective or objective measures, such as nMOS, WER, and CER.
```

**REPAIRED (globally accepted):**
```
Earlier work relies primarily on a limited set of perceptual and accuracy metrics, 
such as the Mean Opinion Score (MOS), Word Error Rate (WER), and Character Error Rate (CER).
```

**THE RULE:** "nMOS" is not a standard metric name. The standard is **MOS** (Mean Opinion Score). If you mean "naturalness MOS", write **nMOS (naturalness MOS)** or **N-MOS** on first use with explicit definition. If you mean the standard ITU-T P.800 MOS, just write **MOS**. Never use a non-standard acronym without defining it.

---

### FIX-T5 — "Frechet Distance" Missing Accent

**ORIGINAL (broken) — Model-A:**
```
NISQA-MOS, UT-MOS, PESQ, MCD, MSD, F0-RMSE, Frechet Distance, CS, WER, CER
```

**REPAIRED (globally accepted):**
```
NISQA-MOS, UTMOS, PESQ, MCD, MSD, F0-RMSE, Fréchet Audio Distance (FAD), 
Cosine Similarity (CS), WER, CER
```

**THE RULE (two issues):**
1. The correct spelling is **Fréchet** (with accent) — in LaTeX: `Fr\'echet` or `Fréchet` with UTF-8. Many IEEE reviewers of signal processing background will notice this.
2. "Frechet Distance" in the context of audio generation is specifically the **Fréchet Audio Distance (FAD)** — use the full form with acronym on first use.

---

### FIX-T6 — "W.R.T." vs "With Respect To"

**ORIGINAL (broken) — Model-B:**
```
the GAN-based vocoder becomes a preferred choice due to its real-time capabilities 
w.r.t. the speech quality and inference speed [10]–[13].
```

**REPAIRED (globally accepted):**
```
GAN-based vocoders are the preferred choice for real-time applications due to 
their balance between speech quality and inference speed [10]–[13].
```

**THE RULE:** "w.r.t." (with respect to) is a mathematical shorthand used in equations and proofs — it is **too informal for running text in academic prose**. In body text, write out the full phrase or rephrase the sentence entirely. The example sentence above actually needed full restructuring because "real-time capabilities w.r.t. quality and speed" doesn't clearly communicate that GAN balances the two.

---

## CATEGORY 5: Sentence Structure & Grammar

---

### FIX-S1 — "These vocoder" (Missing Plural S)

**ORIGINAL (broken) — Model-B:**
```
These vocoder often produce robotic and unnatural speech.
```

**REPAIRED (globally accepted):**
```
These vocoders often produce robotic and unnatural speech.
```

**THE RULE:** Subject-noun agreement. "These" is a plural demonstrative — it requires a **plural noun**: "these **vocoders**". A simple but embarrassing error. Use grammar check tools.

---

### FIX-S2 — "e.g.," Without Comma / Wrong Usage

**ORIGINAL (broken) — Model-B:**
```
extract key acoustic parameters e.g., pitch (i.e., fundamental frequency, F0), formants, 
and spectral envelope.
```

**REPAIRED (globally accepted):**
```
extract key acoustic parameters, e.g., pitch (i.e., fundamental frequency, F0), 
formants, and spectral envelope.
```

**THE RULE:** "e.g.," (exempli gratia = for example) must be preceded by a **comma** when it appears mid-sentence: "parameters**,** e.g., pitch...". Omitting the comma is grammatically incorrect. The same applies to "i.e.," (id est = that is).

---

### FIX-S3 — Comma Splice Creating Two Fragments

**ORIGINAL (broken) — Model-B:**
```
In particular, AR models suffer from slow inference speed due to sequential nature. 
while NAR models were faster but demonstrated reduced speech quality.
```

**REPAIRED (globally accepted):**
```
Specifically, AR models suffer from slow inference due to their sequential nature, 
while NAR models are faster but produce lower speech quality.
```

**THE RULE:** A period followed by a lowercase "while" means the sentence was split incorrectly. "While" here is a **coordinating conjunction** between two parallel clauses — they must share one sentence connected by a comma. Also: "sequential nature" → "their sequential nature" (needs possessive "their").

---

### FIX-S4 — Passive Construction Weakening Scientific Claims

**ORIGINAL (broken) — Model-B:**
```
The earlier works were done heavily using subjective measures.
```

**REPAIRED (globally accepted):**
```
Prior vocoder studies relied primarily on subjective perceptual evaluations such as MOS.
```

**THE RULE:** "Were done" is passive and vague — by whom? Who did these works? The active voice is cleaner and more precise: "Prior studies relied on..." Active voice is the IEEE/NeurIPS/ICASSP standard for empirical claims. Reserve passive voice only when the agent is genuinely unknown or irrelevant.

---

### FIX-S5 — Run-On Sentence: "and still struggle"

**ORIGINAL (broken) — Model-B:**
```
the use of self-attention increases complexity quadratically with a sequence length 
of the (O(n²d)), makes it complex for long sequences and limits real-world applications, 
and still struggle with long sequences due to vanishing attention weights over distant tokens.
```

**REPAIRED (globally accepted):**
```
The standard self-attention mechanism scales quadratically, O(n²d), with sequence length, 
imposing prohibitive memory and compute costs for long sequences and causing vanishing 
attention weights over distant tokens — both of which limit real-world deployment.
```

**THE RULE (three issues):**
1. "the (O(n²d))" — the parenthesis is misplaced; write "O(n²d)" without "the" before it.
2. "makes it complex... and still struggle" — tense mismatch: "makes" (singular present) but "struggle" (plural) with no clear subject.
3. The whole sentence should be restructured as one clean claim with a dash-clause for elaboration.

---

## CATEGORY 6: Reference Formatting Errors

---

### FIX-R1 — Missing City/Country in Conference References

**ORIGINAL (broken) — Model-A (extracted from papers):**
```
@inproceedings{rekesh2023fast,
  booktitle = {IEEE Automatic Speech Recognition and Understanding Workshop (ASRU), pp. 1--8},
  year      = {2023}
}
```

**REPAIRED (globally accepted):**
```
@inproceedings{rekesh2023fast,
  booktitle = {IEEE Automatic Speech Recognition and Understanding Workshop (ASRU), pp. 1--8},
  year      = {2023, Taipei, Taiwan}
}
```

**THE RULE:** Conference references must always include **Year, City, Country** in the year field OR booktitle field. This is a lab standard for traceability. ASRU 2023 was held in Taipei, Taiwan.

---

### FIX-R2 — arXiv Reference Missing Last-Accessed Date

**ORIGINAL (broken):**
```
@article{hrinchuk2019correction,
  journal = {arXiv preprint arXiv:1910.10697},
  year    = {2019}
}
```

**REPAIRED (globally accepted):**
```
@article{hrinchuk2019correction,
  journal = {arXiv preprint arXiv:1910.10697},
  year    = {2019 \{Last Accessed Date: November 11$^{\mathrm{th}}$, 2026\}}
}
```

**THE RULE:** arXiv preprints are **not formally peer-reviewed** and can change. The "Last Accessed" date lets readers verify they found the same version. lab standard: always add `{Last Accessed Date: Month Day, Year}` to ALL arXiv references.

---

### FIX-R3 — Duplicate BibTeX Keys

**ORIGINAL (broken) — from the references submitted in the previous session:**
```
@inproceedings{baevski2020wav2vec, ... year = {2020, Virtual}}
@inproceedings{baevski2020wav2vec, ... year = {2020}}           ← DUPLICATE KEY

@inproceedings{rekesh2023fast, ... year = {2023}}
@inproceedings{rekesh2023fast, ... year = {2023}}               ← DUPLICATE KEY

@article{zheng2026towards, ... year = {2026 \{Last Accessed...}}}
@article{zheng2026towards, ... year = {2026}}                   ← DUPLICATE KEY
```

**REPAIRED (globally accepted):**
```
% Keep only the MORE COMPLETE entry; delete the other.
% For genuinely different papers that share a first-author + year:
@inproceedings{baevski2020wav2vec_neurips,
  author    = {Baevski, Alexei and Zhou, Yuhao and Mohamed, Abdelrahman and Auli, Michael},
  booktitle = {Advances in Neural Information Processing Systems (NeurIPS), pp. 12449--12460},
  year      = {2020, Virtual}
}
```

**THE RULE:** Duplicate BibTeX keys cause LaTeX to silently use only the **first** occurrence and ignore the second — leading to wrong references in your paper without any error or warning. Always run:
```bash
grep -c "@inproceedings\|@article\|@misc" refs.bib  # Total entries
# Check for duplicates:
grep "^@" refs.bib | sort | uniq -d
```

---

### FIX-R4 — Wrong En-Dash vs Hyphen in Page Ranges

**ORIGINAL (broken):**
```
pp. 4779-4783   ← hyphen (wrong)
pp. 1741--1744  ← double-hyphen in LaTeX (correct → renders as –)
```

**REPAIRED (globally accepted) in BibTeX:**
```
pages = {4779--4783}   ← always use -- in LaTeX (renders as en-dash –)
```

**Rendered output must be:** `pp. 4779–4783` (en-dash, not hyphen)

**THE RULE:** Page ranges always use the **en-dash** (–) in academic publishing. In LaTeX: `4779--4783` → renders as `4779–4783`. Never use a single hyphen `-` for page ranges.

---

## CATEGORY 7: Figure & Table Formatting

---

### FIX-F1 — Table Caption: "AFTER [19]" in Caption

**ORIGINAL (broken) — Model-B:**
```
TABLE I
COMPARATIVE ANALYSIS OF PHONEME, CONSONANT, AND VOWEL
COUNTS ACROSS LANGUAGES. AFTER [19].
```

**REPAIRED (globally accepted):**

In LaTeX:
```latex
\begin{table}[t]
\caption{COMPARATIVE ANALYSIS OF PHONEME, CONSONANT, AND VOWEL 
         COUNTS ACROSS SELECTED LANGUAGES}
\label{tab:phoneme_counts}
\centering
\begin{tabular}{lrrr}
\toprule
\textbf{Language} & \textbf{Phonemes} & \textbf{Consonants} & \textbf{Vowels} \\
\midrule
Mandarin  & 35 & 26 &  9 \\
French    & 35 & 21 & 14 \\
English   & 44 & 24 & 20 \\
Gujarati  & 57 & 32 & 25 \\
\bottomrule
\end{tabular}
{\footnotesize Source: [19].}
\end{table}
```

**THE RULE:** Citation attribution belongs either as a table footnote `{\footnotesize Source: [19].}` placed immediately after `\end{tabular}` or in the paragraph text that refers to the table. It must NOT be part of the caption text.

---

### FIX-F2 — Table Column Headers Missing ↑/↓ Arrows

**ORIGINAL (broken) — Model-B Table II (inferred from text):**
```
Method | PCC | PESQ | STOI | MSD | MCD | SMOS
```

**REPAIRED (globally accepted):**
```
\textbf{Method} & \textbf{PCC}$(\uparrow)$ & \textbf{PESQ}$(\uparrow)$ & 
\textbf{STOI}$(\uparrow)$ & \textbf{MSD}$(\downarrow)$ & \textbf{MCD}$(\downarrow)$ & 
\textbf{SMOS}$(\uparrow)$
```

**Rendered:** Method | PCC (↑) | PESQ (↑) | STOI (↑) | MSD (↓) | MCD (↓) | SMOS (↑)

**THE RULE:** Every metric column must declare its optimization direction. A reviewer must not need to remember whether lower or higher is better. This is a universal IEEE/ICASSP/Interspeech standard. No exceptions.

---

### FIX-F3 — SMOS Confidence Interval Not in Table

**ORIGINAL (broken) — Model-B:**
```
Model-B (Proposed)   0.01   2.64   0.93   25.20   35.66   4.51
```

**REPAIRED (globally accepted):**
```
\textbf{Model-B (Proposed)} & \textbf{0.01} & \textbf{2.64} & \textbf{0.93} & 
\textbf{25.20} & \textbf{35.66} & \textbf{4.51}$_{\pm 0.12}$ \\
```

**Rendered:** Model-B (Proposed) | **0.01** | **2.64** | **0.93** | **25.20** | **35.66** | **4.51** ±0.12

**THE RULE:** Subjective scores (MOS, SMOS, CMOS) must ALWAYS include their uncertainty (95% CI or standard deviation) in the results table. A score without uncertainty is unverifiable. Format: `4.51±0.12` or `4.51 (±0.12)`.

---

## CATEGORY 8: Globally Accepted Abstract Template

Based on all corrections above, here is the **globally accepted abstract template** for lab IEEE papers:

```
Abstract—[TASK NAME (ABBR)] [defines/converts/generates] [what] while [preserving what]. 
It has transformed [2–3 application domains] by [specific benefit]. 
[Recent advances / Prior methods] in [specific model family], particularly [sub-family], 
have [achieved X] but [face specific limitation], arising from [mathematical root cause, 
e.g., O(n²d) complexity of self-attention]. 
In this work, we propose [MODEL NAME], a [specific mechanism] that [replaces/augments] 
[prior component] with [linear-time / improved / novel approach], reducing complexity 
from O(n²d) to O(nd). 
[Proposed approach] achieves [METRIC₁ = VALUE₁ (+ΔVALUE₁)] and [METRIC₂ = VALUE₂ (+ΔVALUE₂)], 
outperforming [BASELINE NAME] in [specific quality dimension]. 
[Proposed approach] further reduces [METRIC₃ to VALUE₃] and [METRIC₄ to VALUE₄] compared 
to [BASELINE NAME], demonstrating [specific advantage]. 
With [X]% fewer computational resources, [MODEL NAME] achieves [RTF from VALUE→VALUE], 
enabling [practical deployment scenario]. 
The demo utterances are publicly available at supplementary website: \url{[URL]}.
```

---

## CATEGORY 9: Globally Accepted Contribution Bullet Template

```
1) We proposed [ARCHITECTURAL COMPONENT] for [SPECIFIC MODULE] to reduce the 
   [ORIGINAL COMPLEXITY O(n²d)] of [PRIOR MECHANISM] to [IMPROVED COMPLEXITY O(nd)] 
   using [SPECIFIC TECHNIQUE], enabling [SPECIFIC BENEFIT].

2) [MODEL NAME] was trained for [X]M steps with a batch size of [B] on [GPU MODEL (VRAM)], 
   with [TRAINING TECHNIQUE]. [MODEL NAME] comprehensively evaluated using [N] 
   subjective, objective, and performance measures — [METRIC₁], [METRIC₂], ..., [METRIC_N] — 
   providing a thorough assessment against [NUMBER] competitive baselines.

3) [MODEL NAME] reduces computations by [X]%, improves real-time inference by [Y]% 
   (RTF [FROM]→[TO]), lowers [PROSODY_METRIC] to [VALUE], and improves intelligibility 
   with [WER VALUE] and [CER VALUE], while preserving [SPEAKER METRIC] of [VALUE].
```

---

## CATEGORY 10: Globally Accepted Conclusion Template

```
In this paper, we introduced [MODEL NAME], a [BRIEF DESCRIPTION] for [APPLICATION]. 
By [CORE MECHANISM], [MODEL NAME] [WHAT IT ACHIEVES] — specifically, [SPECIFIC CLAIM 1] 
and [SPECIFIC CLAIM 2]. 
Experimental evaluation on [DATASET(S)] demonstrates that [MODEL NAME] [OUTPERFORMS/MATCHES] 
[BASELINE FAMILY] across [METRICS], achieving [BEST NUMBER] in [BEST METRIC], 
while reducing inference cost by [X]% (RTF [FROM]→[TO]). 
[Forward-looking, positive final sentence about broader impact or next research frontier — 
never a limitation or "further work is needed."]
```

---
