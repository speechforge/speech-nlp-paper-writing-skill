# Notices and Attributions

This skill combines established speech-lab writing standards, the 15-step scientific writing method, and style overlays generalised from published conference papers. The source papers themselves are not included in this repository.

The enhancement adapts ideas and structures from three third-party sources, each MIT-licensed. No third-party code is copied: the scripts in `scripts/` were written for this skill, informed by the documented designs below.

| Source | Licence | What was adapted |
|---|---|---|
| **ai-research-writing-skill** | MIT | claim-evidence engineering; the artifact set (`paper_story.md`, `claim_evidence_map.md`, task packets); two-pass drafting order; three-dimension citation verification (existence, BibTeX integrity, claim support) and claim-relation vocabulary; fail-closed gates; concept-versus-evidence figure classes and the six-part diagram prompt; the evidence-first review procedure with evidence notes, three review lenses, and rejection-risk table; submission packaging and camera-ready checklists |
| **Research-Paper-Writing-Skills** | MIT | paragraph clarity check and reverse outlining; one-message-per-paragraph discipline; the five-dimension self-review and claim-support alignment |
| **ml-paper-writing** (Orchestra Research) | MIT | Narrative Principle (What / Why / So What); Farquhar five-sentence abstract; Gopen and Swan seven principles; Perez micro-tips; Lipton word choice; Steinhardt precision; reviewer reading behaviour; conference requirement table; template workflow and format-conversion guidance; the "never hallucinate citations" framing |

MIT licence text (applies to each source above for the portions adapted):

> Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions: The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software. THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## External material fetched at run time (not redistributed here)
- **ACL style files** (`acl.sty`, `acl_natbib.bst`, example): fetched from the official `acl-org/acl-style-files` repository at a pinned commit and SHA-256. The repository carries no explicit licence file, so the files are not included here. Use them unmodified and follow the current call for papers.
- **IEEEtran** (`IEEEtran.cls`, `IEEEtran.bst`): fetched from CTAN; the class is distributed under the LaTeX Project Public License 1.3. Do not rename or edit it.
- **Citation metadata**: retrieved from Crossref, DataCite, arXiv, the ACL Anthology, OpenAlex, and Semantic Scholar through their public APIs, subject to their terms. Contact details are never sent unless the user supplies them.

## Fonts and images
The demo site and dashboard use system font stacks only and make no external requests. Plot and diagram colours follow the Okabe-Ito palette (colour-blind safe).

## Licence of this skill
No licence file is shipped for the skill itself; the owner chooses it. Adding one (for example MIT or Apache-2.0) is recommended before sharing publicly.
