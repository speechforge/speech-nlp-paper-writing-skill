# Interactive Demo Website and Multimedia Experience

A project-named website lets reviewers and readers **hear, see, and compare** the work. It is built from the same data as the paper, with the same credits and licences, and it never replaces the paper's evidence.

---

## 1. Naming rule (hard)

The site, its folder, title, headings, and text are named after **the project**, for example `BoundaryVoc`. They **never** contain a conference, journal, or publisher name (no ACL, EMNLP, ICASSP, Interspeech, IEEE, NeurIPS, ...). The builder refuses venue words in the project name and in site text. Pass `--allow-venue-words` only if the authors explicitly ask.

Why: the site outlives a submission, the venue may change, and a venue name in a public page can compromise blind review.

---

## 2. Build and run

```bash
# 1. put media under PROJECT/demo/assets/ and describe it in PROJECT/demo/samples.json
python3 scripts/build_demo_site.py PROJECT            # builds PROJECT/demo/site
python3 scripts/build_demo_site.py PROJECT --serve    # build and serve on http://127.0.0.1:8000/
python3 scripts/dashboard.py PROJECT                  # serves the site at http://127.0.0.1:8765/demo/ too
```
Static output: `index.html`, `style.css`, `app.js`, copied `assets/`, `site_manifest.json`. No external requests, no tracking, works offline. Serve over HTTP (the commands above do); opening `index.html` directly cannot decode audio for live spectrograms, and the page says so rather than failing silently.

Each project gets its **own accent colour** (a hue derived from the project slug), used for the interface and the spectrogram colour ramp. Light and dark themes follow the system and can be switched.

---

## 3. What the site offers (sections appear only when their data exists)

| Section | Experience |
|---|---|
| Hero | project name, tagline, a two to three sentence plain-language summary, and the first sample's live spectrogram |
| How it works | stepper over the method: short text plus an optional figure per step |
| Listen and compare | per sample: a segmented switch between systems; **switching keeps the playhead**, so you hear the same moment in each; spectrogram with a shared colour scale per sample; click to seek; download |
| Blind listening test | randomised pairs, A/B hidden, "A is better / B is better / No preference", tally revealed at the end; stored only in the visitor's browser |
| Compare outputs | text samples with word-level differences against the reference, with a toggle |
| Figures | gallery with captions and a lightbox |
| Videos | native video with optional captions |
| Results | ranked bars with confidence whiskers, metric direction, and a stated axis start |
| Credits | contributions (CRediT), licences, third-party assets and inherited restrictions, citation, repository link |

---

## 4. `demo/samples.json`

```json
{
  "tagline": "One plain sentence about what the work does.",
  "summary": "Two or three sentences a non-specialist can follow.",
  "pipeline": [{"title": "Find the boundary", "text": "...", "image": "images/step1.png"}],
  "audio_samples": [{"title": "Sentence 1", "transcript": "...",
     "systems": [{"name": "Reference", "file": "audio/s1_ref.wav", "reference": true},
                 {"name": "Baseline", "file": "audio/s1_base.wav"},
                 {"name": "ProjectName", "file": "audio/s1_ours.wav", "highlight": true}]}],
  "blind_test": {"enabled": true, "question": "Which sample sounds more natural?"},
  "text_samples": [{"title": "...", "reference": "...", "outputs": [{"name": "ProjectName", "text": "...", "highlight": true}]}],
  "gallery": [{"title": "...", "file": "images/fig_mos_web.png", "caption": "...", "alt": "..."}],
  "results": {"title": "Listening test", "metric": "MOS", "direction": "up", "axis_min": 3.0,
              "rows": [{"name": "Baseline", "value": 0, "ci": 0}]}
}
```
Media paths are relative to `demo/assets/`. Missing files stop the build with a list. The full schema is documented at the top of `scripts/build_demo_site.py`.

**Numbers in `results` must come from the results files** (for example the `.source.json` written by `make_plots.py`), never typed from memory or from the paper text.

---

## 5. Choosing samples honestly (this is part of the science)

- Select by a **stated rule**: random draw with a fixed seed, or median plus worst case plus best case. Say which on the page.
- Include at least one **failure case** of the proposed method.
- Use the **same text, speaker, and loudness** across systems. Loudness-normalise all systems identically (for example to the same integrated loudness) so volume does not bias listeners.
- Keep transcripts for accessibility and for the reader who cannot listen.
- Compress for the web without changing the comparison: keep the same sampling rate and bit depth across systems; trim to 3 to 10 seconds; mono is fine for most speech.
- For NLP projects use the text-comparison and figure sections: show the input, the reference, and each system's output with differences marked, plus attention or attribution figures from `make_plots.py heat`.

---

## 6. Responsibility and review

- **Consent and licence:** voices and images only with recorded consent; the licence for demo media is stated in the footer from `project_meta.json`. Non-commercial or no-derivative inputs flow into a visible "inherited restrictions" note.
- **Misuse:** for voice cloning, voice conversion, and highly natural synthesis state the intended use and misuse risk (see `17_credits_and_license.md`); consider withholding the most identity-preserving samples.
- **Anonymity:** while `anonymous` is true in `project_meta.json`, author names, funding, and the repository link are hidden on the site. During blind review host the site anonymously and put only an anonymised link in the paper. Flip `anonymous` to false for camera-ready.
- **Accessibility:** keyboard-operable controls, visible focus, reduced-motion respected, transcripts, alt text for figures.
- **Do not overclaim:** the site shows examples and scores; the paper holds the evidence. A listening-test chart on the site must match the paper table exactly.

---

## 7. Linking from the paper

At camera-ready, add one sentence to the availability statement or the first page: "Audio samples and an interactive comparison are at [URL]." In review, use the anonymised link or omit it.
