# Citation Integrity: Never Invented, Always Double-Verified

AI-generated references have a high error rate (commonly cited near 40%): papers that do not exist, wrong authors, wrong years, fabricated DOIs. A fabricated reference is academic misconduct and can cause desk rejection. **A citation is only as good as the record it was fetched from.**

---

## 1. The rules

1. **Never write a BibTeX entry, author list, year, venue, page range, or DOI from memory.** Every field comes from a fetched record.
2. **Never cite a paper you have not found in a search or identifier lookup in this session.** "I think there is a paper about X" is not a citation; search for it, or mark `[CITATION NEEDED]`.
3. **Double-verify.** A citation is `verified` only when (a) a **primary** record resolves the identifier and (b) an **independent second index** agrees on title, first author, and year, and (c) the **abstract or text was read** against the sentence that cites it.
4. **Fail closed.** If any step fails, the entry stays non-terminal and is reported. An empty search result from an unavailable API is not "no such paper" and never a licence to guess.
5. **Tell the user.** At the end of every drafting turn list placeholders and unverified entries: "I could not verify [N] citations; they are marked and listed below."
6. **Never use the user's email, name, or project in outgoing requests.** The scripts send a generic client name. `--mailto` is sent only if the user supplies it.

---

## 2. Three separate dimensions (never collapse them into one label)

| Dimension | Question | Tool |
|---|---|---|
| Existence and metadata | Is the work real, and are authors, title, year, venue correct? | `citations.py verify` (primary + second index) |
| BibTeX integrity | Does every `\cite` key resolve to exactly one well-formed entry? | `citations.py check` |
| Claim support | Does the source actually say what the sentence attributes to it? | you read the abstract or text, then set `supports[].relation` |

---

## 3. Procedure

```
1  Segment the manuscript into citable claims (one sentence, one source need).
2  Discover candidates:        python3 scripts/citations.py search "task method benchmark" --limit 5
   (or an agent search tool such as Exa MCP when installed; its results are candidates only)
3  Resolve an identifier:      DOI, arXiv ID, or ACL Anthology ID. Prefer the version that supports the claim.
4  Write citation_requests.json with the identifier and the exact supporting sentence.
5  Verify and build BibTeX:    python3 scripts/citations.py verify PROJECT --style acl|ieee
6  Read each abstract (stored in citation_lock.json) and set relation per sentence.
7  Re-run verify (it is cached and free), then:  python3 scripts/citations.py check PROJECT --strict
```

`citation_requests.json`:
```json
{"entries": [
  {"acl": "N19-1423",
   "supports": [{"sentence": "Pretrained bidirectional encoders transfer to many tasks.", "relation": "direct"}]},
  {"arxiv": "1706.03762", "key": "vaswani2017attention",
   "supports": [{"sentence": "Self-attention replaces recurrence.", "relation": "direct"}]}
]}
```

### Source routing

| Identifier | Primary record | Second index (must agree) |
|---|---|---|
| ACL Anthology ID | `aclanthology.org/<id>.bib` | OpenAlex, Semantic Scholar |
| DOI | Crossref, then DataCite (arXiv and Zenodo DOIs) | OpenAlex, Semantic Scholar, arXiv |
| arXiv ID | arXiv API | OpenAlex, Semantic Scholar |
| Dataset or software | Official repository, release, or dataset card | cite the associated paper if one exists |

DBLP is useful for finding NLP and speech venues but is rate limited; treat it as discovery only. OpenAlex and Semantic Scholar aggregate; use them as cross-checks, never as the only authority when a DOI, arXiv, or proceedings record exists.

Agreement test (`citations.py`): normalised title similarity at least 0.88, same first-author surname, years within one (preprint versus proceedings). A mismatch is a `conflict` and blocks citation until resolved against the publisher or proceedings page.

---

## 4. Claim relations (one per citation-sentence pair)

| Relation | Meaning | Allowed in a final paper? |
|---|---|---|
| `direct` | The source directly establishes the sentence | yes |
| `contrast` | The source accurately describes the setting you differ from | yes |
| `software` | Documents a tool, dataset, or model you use | yes |
| `background` | Motivates the area, not the specific claim | yes, only for background sentences |
| `partial` | Supports a narrower statement | no: narrow the sentence or add a source |
| `weak` | Does not support the sentence | no: remove or replace |
| `metadata-only` | Existence checked, content not read | no: cannot support a claim yet |

Strong technical or comparative claims need `direct`, `contrast`, or `software`. Related work must describe a paper only as far as its read text supports.

---

## 5. Statuses

`verified` (terminal) | `metadata-verified` (claim support pending) | `single-source` | `conflict` | `not-found` | `placeholder`. Only `verified` may remain in a final paper. `check --strict` fails otherwise.

When a citation cannot be verified, leave an explicit marker so nothing slips through:
```latex
\citep{PLACEHOLDER_author2024_verify}   % TODO: could not verify; author must confirm
... as shown in prior work [CITATION NEEDED: could not verify Smith et al. 2024].
```
The readiness gate fails while any marker remains.

---

## 6. BibTeX conventions

The generator follows the repository's reference rules (`07_...` Rules K1 to K15):
- `Lastname, Firstname` author format; `and others` (never `et al.`) when truncated (IEEE style truncates after six authors, ACL lists all).
- Titles in double braces to keep capitalisation; page ranges with `--`.
- Key format `firstauthoryearkeyword`; no duplicate keys (duplicates are an error in `check`).
- `@article` for arXiv preprints, `@misc` for datasets and software.
- Cite the **published** version when it exists and supports the claim; the generator surfaces a `version_hint` when the arXiv record points to a publication.
- Optional `--last-accessed "Month Dayth, Year"` adds the lab's "Last accessed" note.

Never type or "fix" entries by hand; re-run `verify` so the lock stays consistent.

---

## 7. Local corpus and access

Save close papers only where access and licensing permit. Record each important candidate with an official URL, version, and one of `available`, `metadata-only`, `needs-access`. Do not commit private or copyrighted PDFs to a public repository.

---

## 8. Final audit

- Every `\cite` key exists exactly once; every cited key is `verified`.
- Title, first author, year, venue, and identifier agree with the primary record.
- Each sentence relation is `direct`, `contrast`, `software`, or `background`.
- No `PLACEHOLDER_` key and no `[CITATION NEEDED]` remain.
- Concurrent work and secondary sources are described with scoped language.
- Self-citations that reveal identity are handled according to the venue's blind-review rules.

Run `python3 scripts/citations.py check PROJECT --strict`.
