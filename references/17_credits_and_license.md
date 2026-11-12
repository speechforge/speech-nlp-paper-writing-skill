# Credit Statement and License Statement

Every paper, its code and data release, and its website carry a **credit statement** (who did what, and what was built on) and a **license statement** (what others may do with what we release). One source, `project_meta.json`, feeds all of them so they never disagree:

```bash
python3 scripts/credits_license.py PROJECT          # writes paper/statements/*.tex, CREDITS.md, demo/site_credits.json
python3 scripts/credits_license.py PROJECT --check  # validate only
```

---

## 1. Author contributions with CRediT

Use the **CRediT** taxonomy (14 roles). Every author needs at least one role (the generator errors otherwise) and unknown role names are rejected. It warns when nobody is credited with *Conceptualization* or *Writing - original draft*.

| Role | Meaning |
|---|---|
| Conceptualization | ideas, research goals and aims |
| Data curation | annotation, cleaning, maintenance of research data |
| Formal analysis | statistical, mathematical, or computational analysis |
| Funding acquisition | obtaining financial support |
| Investigation | conducting experiments or data collection |
| Methodology | developing or designing the methods |
| Project administration | management and coordination |
| Resources | materials, compute, tools, corpora |
| Software | programming, implementation, code |
| Supervision | oversight and leadership |
| Validation | verification and replication of results |
| Visualization | figures, plots, demonstrations |
| Writing - original draft | preparing the first written draft |
| Writing - review & editing | critical review, commentary, revision |

Statement format (generated): "Author contributions follow the CRediT taxonomy. A.B.: Conceptualization, Methodology. C.D.: Software, Investigation, Writing -- original draft." Equal contribution and the corresponding author are added from the metadata.

**Anonymity:** contributions, funding, and thanks identify the authors, so the wrappers print them only in the camera-ready build (`\cameraready` switch). Never leave names in an anonymous review version.

---

## 2. Acknowledgments and funding

- Heading by family: **ACKNOWLEDGMENT** (singular, uppercase) for IEEE; **Acknowledgments** for ACL (Rule J1 in `07`).
- **MeitY format** (Rule J2), generated exactly: "This work is supported by the Ministry of Electronics and Information Technology (MeitY), Government of India, under Project Grant ID: X." One sentence. Other funders: "This work was supported by [agency] under grant [number]."
- Thank people and compute providers in plain language; never include credentials or private details.
- **AI assistance disclosure:** if a generative assistant helped draft or edit text, say so in the acknowledgments (and in the venue's form if required), stating that the authors verified claims, numbers, and citations and take responsibility. Venues differ; follow the current policy. The wording lives in `project_meta.json` under `ai_assistance`.

---

## 3. License statement

State, for each thing released:

| Asset | Common choices | Notes |
|---|---|---|
| Paper text and figures | CC BY 4.0 | follow the venue's copyright or licence form at camera-ready; arXiv offers its own choices |
| Code | Apache-2.0 or MIT | Apache-2.0 includes a patent grant |
| Data created for this work | CC BY 4.0 (or CC BY-NC when constrained) | include a datasheet or data statement; state consent |
| Model weights | Apache-2.0, or OpenRAIL-M when use restrictions are intended | weights inherit restrictions from training data |
| Demo media | CC BY 4.0 | only with recorded consent from speakers and participants |

Use SPDX identifiers in `project_meta.json` (`CC-BY-4.0`, `Apache-2.0`, `MIT`, `CC-BY-NC-4.0`, ...). Unrecognised identifiers raise a warning.

**Inherited restrictions are computed for you.** If a third-party asset is licensed non-commercial (NC), models trained on it and samples derived from it carry that restriction; no-derivatives (ND) inputs cannot be redistributed in modified form; GPL-family code requires compatible release terms. The statement states these explicitly. If the chosen release licence conflicts with an input licence, change the release licence or drop the asset; do not hide the conflict.

---

## 4. Third-party credit

Every dataset, pretrained model, toolkit, and code base used is listed in `third_party` with: name, kind (dataset, model, tool, code), licence, URL, and the verified citation key. The paper cites each one (`citations.py`, relation `software`) and the generator adds the licence sentence. Credit original annotators and corpus creators by citation, and respect any attribution wording the licence requires.

---

## 5. Speech and language specifics

- **Consent and privacy:** recorded consent for every voice and for public release of samples; no identifying content in transcripts; compensation stated; ethics approval or exemption identifier when humans are involved (`human_subjects`; the generator errors if involvement is declared without approval and consent).
- **Voice cloning and conversion:** state intended use, the misuse risk (impersonation, fraud), and any mitigations (watermarking, restricted release, consent policy). Consider releasing code and low-identity samples while withholding easy-to-misuse weights.
- **Bias and coverage:** state which languages, dialects, and populations are covered and which are not; do not imply universality.
- **Annotation and human evaluation:** annotators' qualifications, instructions, payment, and agreement.
- **Data statements and datasheets:** for new corpora provide provenance, collection method, demographics at an appropriate level of detail, and licence.

---

## 6. Where the statements appear

| Place | Content |
|---|---|
| Paper, before references | "Licenses and Availability" (always), Author Contributions and Acknowledgments (camera-ready only) |
| `CREDITS.md` in the project | full table of roles, licences, third-party assets, inherited restrictions |
| Demo website footer | credits (when not anonymous), licences, third-party material, how to cite, repository link |
| Repository | add the matching `LICENSE` file and a `CITATION.cff` when the repository is released |

Check consistency by regenerating after any change to `project_meta.json`.
