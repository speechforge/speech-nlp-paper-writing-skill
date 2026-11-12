#!/usr/bin/env python3
"""Citation integrity tool: discover, double-verify, build BibTeX, and gate the manuscript.

Nothing here is written from memory. Every record is fetched from a live index and a
citation is only called `verified` when TWO independent sources agree and the sentence
it supports has been read and classified.

    citations.py search "title words" [--limit 5]
    citations.py verify PROJECT [--requests citation_requests.json] [--style ieee|acl] [--mailto you@example.org]
    citations.py check  PROJECT [--strict]

citation_requests.json (written by the agent, never from memory of a paper):
{"entries": [{"key": "optional_key",
              "doi": "10.18653/v1/N19-1423",      # or "arxiv": "1810.04805" or "acl": "N19-1423"
              "supports": [{"sentence": "The exact sentence in the paper that cites this work.",
                            "relation": "direct|contrast|software|background|partial|weak"}]}]}

Statuses: verified | metadata-verified (claim support still pending) | single-source |
          conflict | not-found | placeholder. Only `verified` may stay in a final paper.
Contact details are never sent unless you pass --mailto yourself.
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import load_json, now_iso, save_json, tex_files  # noqa: E402

UA = "paper-writing-skill-citation-verifier/1.0"
GOOD_RELATIONS = {"direct", "contrast", "software", "background"}
WEAK_RELATIONS = {"partial", "weak", "metadata-only"}
STOP = {"a", "an", "the", "of", "on", "for", "to", "in", "and", "with", "via", "towards", "toward", "is", "are", "from", "by", "at"}
CITE_RE = re.compile(r"\\(?:cite|citep|citet|citealp|citealt|citeauthor|citeyear|parencite|textcite|autocite|footcite)\*?(?:\[[^\]]*\]){0,2}\{([^}]*)\}")
NOCITE_RE = re.compile(r"\\nocite\{([^}]*)\}")


# --------------------------------------------------------------------------- network
class Net:
    def __init__(self, cache_dir: Path | None, mailto: str | None = None, offline: bool = False):
        self.cache_dir, self.mailto, self.offline = cache_dir, mailto, offline
        if cache_dir:
            cache_dir.mkdir(parents=True, exist_ok=True)

    def get(self, url: str, accept: str = "application/json", retries: int = 2) -> tuple[int, str]:
        if self.mailto and "api.openalex.org" in url:
            url += ("&" if "?" in url else "?") + "mailto=" + urllib.parse.quote(self.mailto)
        key = hashlib.sha256((url + accept).encode()).hexdigest()
        cache = self.cache_dir / f"{key}.json" if self.cache_dir else None
        if cache and cache.exists():
            c = json.loads(cache.read_text(encoding="utf-8"))
            if c["status"] == 200:
                return c["status"], c["body"]
        if self.offline:
            return 0, ""
        ua = UA + (f" (mailto:{self.mailto})" if self.mailto else "")
        status, body = 0, ""
        for attempt in range(retries + 1):
            req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept": accept})
            try:
                with urllib.request.urlopen(req, timeout=25) as r:
                    status, body = r.status, r.read().decode("utf-8", errors="replace")
                break
            except urllib.error.HTTPError as e:
                status, body = e.code, ""
                if e.code in (429, 500, 502, 503, 504) and attempt < retries:
                    time.sleep(1.5 * (attempt + 1))
                    continue
                break
            except (urllib.error.URLError, TimeoutError, OSError):
                status = 0
                if attempt < retries:
                    time.sleep(1.0)
        if cache and status == 200:
            cache.write_text(json.dumps({"status": status, "body": body}), encoding="utf-8")
        return status, body


# --------------------------------------------------------------------------- normalisation
def fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    return "".join(c for c in s if not unicodedata.combining(c))


def norm_title(t: str) -> str:
    t = fold(t).lower()
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def surname(name: str) -> str:
    name = fold(name).strip()
    if "," in name:
        name = name.split(",")[0]
    else:
        parts = name.split()
        name = parts[-1] if parts else ""
    return re.sub(r"[^a-z]", "", name.lower())


def rec(source, url, title, authors, year, venue="", doi="", arxiv="", abstract="", typ="", extra=None) -> dict:
    return {"source": source, "url": url, "title": re.sub(r"\s+", " ", (title or "")).strip(),
            "authors": [a for a in authors if a], "year": int(year) if str(year or "").isdigit() else None,
            "venue": venue or "", "doi": (doi or "").replace("https://doi.org/", ""), "arxiv": arxiv or "",
            "abstract": re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", abstract or "")).strip()[:1500], "type": typ,
            "extra": extra or {}}


def authors_from_names(names: list[str]) -> list[str]:
    out = []
    for n in names:
        n = n.strip()
        if "," in n:
            out.append(n)
        else:
            p = n.split()
            out.append(f"{p[-1]}, {' '.join(p[:-1])}" if len(p) > 1 else n)
    return out


# --------------------------------------------------------------------------- fetchers
def f_crossref(net: Net, doi: str):
    st, body = net.get("https://api.crossref.org/works/" + urllib.parse.quote(doi))
    if st != 200:
        return None
    m = json.loads(body)["message"]
    auth = [f"{a.get('family', a.get('name', ''))}, {a.get('given', '')}".strip(", ") for a in m.get("author", [])]
    year = ((m.get("issued") or {}).get("date-parts") or [[None]])[0][0]
    return rec("crossref", f"https://doi.org/{doi}", (m.get("title") or [""])[0], auth, year,
               (m.get("container-title") or [""])[0], doi, "", m.get("abstract", ""), m.get("type", ""),
               {"pages": m.get("page", ""), "volume": m.get("volume", ""), "issue": m.get("issue", ""),
                "publisher": m.get("publisher", ""), "event": (m.get("event") or {}).get("name", "")})


def f_datacite(net: Net, doi: str):
    st, body = net.get("https://api.datacite.org/dois/" + urllib.parse.quote(doi))
    if st != 200:
        return None
    a = json.loads(body)["data"]["attributes"]
    auth = [f"{c.get('familyName', c.get('name', ''))}, {c.get('givenName', '')}".strip(", ") for c in a.get("creators", [])]
    desc = " ".join(d.get("description", "") for d in a.get("descriptions", [])[:1])
    ax = re.search(r"arxiv\.(\d{4}\.\d{4,5})", doi, re.I)
    return rec("datacite", f"https://doi.org/{doi}", (a.get("titles") or [{}])[0].get("title", ""), auth,
               a.get("publicationYear"), a.get("publisher", ""), doi, ax.group(1) if ax else "", desc, "preprint")


def f_arxiv(net: Net, aid: str):
    aid = re.sub(r"v\d+$", "", aid.replace("arXiv:", "").strip())
    st, body = net.get("https://export.arxiv.org/api/query?id_list=" + urllib.parse.quote(aid), "application/atom+xml")
    if st != 200:
        return None
    ns = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}
    root = ET.fromstring(body)
    e = root.find("a:entry", ns)
    if e is None or (e.findtext("a:title", "", ns) or "").strip().lower() == "error":
        return None
    title = e.findtext("a:title", "", ns)
    if not title or not e.findtext("a:published", "", ns):
        return None
    auth = authors_from_names([a.findtext("a:name", "", ns) for a in e.findall("a:author", ns)])
    year = (e.findtext("a:published", "", ns) or "")[:4]
    return rec("arxiv", f"https://arxiv.org/abs/{aid}", title, auth, year, "arXiv", e.findtext("x:doi", "", ns) or "", aid,
               e.findtext("a:summary", "", ns), "preprint",
               {"journal_ref": e.findtext("x:journal_ref", "", ns) or "", "published_doi": e.findtext("x:doi", "", ns) or ""})


def parse_bibtex_fields(text: str) -> dict:
    fields = {}
    for m in re.finditer(r"(\w+)\s*=\s*(\{(?:[^{}]|\{[^{}]*\})*\}|\"[^\"]*\"|\d+)", text):
        v = m.group(2).strip()
        fields[m.group(1).lower()] = v[1:-1] if v[0] in "{\"" else v
    return fields


def f_acl(net: Net, acl_id: str):
    st, body = net.get(f"https://aclanthology.org/{acl_id}.bib", "text/plain")
    if st != 200 or "@" not in body:
        return None
    f = parse_bibtex_fields(body)
    names = [n.strip() for n in re.split(r"\s+and\s+", f.get("author", "")) if n.strip()]
    return rec("acl-anthology", f"https://aclanthology.org/{acl_id}/", re.sub(r"[{}]", "", f.get("title", "")), authors_from_names(names),
               f.get("year"), re.sub(r"[{}]", "", f.get("booktitle", f.get("journal", ""))), f.get("doi", ""), "", f.get("abstract", ""),
               "inproceedings", {"pages": f.get("pages", ""), "publisher": f.get("publisher", ""), "address": f.get("address", "")})


def f_openalex(net: Net, doi: str = "", arxiv: str = "", title: str = ""):
    if doi:
        url = "https://api.openalex.org/works/doi:" + urllib.parse.quote(doi, safe="/")
    elif arxiv:
        url = "https://api.openalex.org/works/doi:10.48550/arxiv." + arxiv
    else:
        return None
    st, body = net.get(url)
    if st != 200:
        return None
    w = json.loads(body)
    inv = w.get("abstract_inverted_index") or {}
    abstract = ""
    if inv:
        pos = sorted((p, word) for word, ps in inv.items() for p in ps)
        abstract = " ".join(word for _, word in pos)
    auth = authors_from_names([a["author"]["display_name"] for a in w.get("authorships", []) if a.get("author")])
    src = ((w.get("primary_location") or {}).get("source") or {}).get("display_name", "")
    return rec("openalex", w.get("id", ""), w.get("title") or w.get("display_name", ""), auth, w.get("publication_year"), src,
               (w.get("doi") or "").replace("https://doi.org/", ""), "", abstract, w.get("type", ""))


def f_s2(net: Net, doi: str = "", arxiv: str = "", acl: str = ""):
    ident = f"DOI:{doi}" if doi else f"ARXIV:{arxiv}" if arxiv else f"ACL:{acl}" if acl else ""
    if not ident:
        return None
    st, body = net.get("https://api.semanticscholar.org/graph/v1/paper/" + urllib.parse.quote(ident, safe=":/")
                       + "?fields=title,year,authors,venue,abstract,externalIds")
    if st != 200:
        return None
    p = json.loads(body)
    ext = p.get("externalIds") or {}
    return rec("semantic-scholar", f"https://www.semanticscholar.org/paper/{p.get('paperId', '')}", p.get("title", ""),
               authors_from_names([a.get("name", "") for a in p.get("authors", [])]), p.get("year"), p.get("venue", ""),
               ext.get("DOI", ""), ext.get("ArXiv", ""), p.get("abstract") or "", "")


# --------------------------------------------------------------------------- verification
def agree(primary: dict, other: dict) -> tuple[bool, list[str]]:
    reasons = []
    sim = difflib.SequenceMatcher(None, norm_title(primary["title"]), norm_title(other["title"])).ratio()
    if sim < 0.88:
        reasons.append(f"title differs (similarity {sim:.2f}): '{other['title'][:70]}'")
    if primary["authors"] and other["authors"] and surname(primary["authors"][0]) != surname(other["authors"][0]):
        reasons.append(f"first author differs: {primary['authors'][0]} vs {other['authors'][0]}")
    if primary["year"] and other["year"] and abs(primary["year"] - other["year"]) > 1:
        reasons.append(f"year differs: {primary['year']} vs {other['year']}")
    return not reasons, reasons


def key_for(r: dict) -> str:
    first = surname(r["authors"][0]) if r["authors"] else "anon"
    words = [w for w in norm_title(r["title"]).split() if w not in STOP and len(w) > 2]
    return f"{first}{r['year'] or ''}{words[0] if words else 'paper'}"


def bib_escape_title(t: str) -> str:
    return "{{" + t.replace("{", "").replace("}", "") + "}}"


def build_bibtex(key: str, r: dict, style: str, last_accessed: str | None) -> str:
    max_auth = 6 if style == "ieee" else 25
    auths = r["authors"][:max_auth] + (["others"] if len(r["authors"]) > max_auth else [])
    ex = r.get("extra", {})
    typ = r.get("type", "")
    if r["source"] in ("arxiv",) or typ == "preprint" or (r["arxiv"] and not r["venue"].lower().startswith("proc")):
        kind = "article"
    elif typ in ("proceedings-article", "inproceedings") or "proc" in r["venue"].lower() or "conference" in r["venue"].lower():
        kind = "inproceedings"
    elif typ in ("journal-article", "article"):
        kind = "article"
    elif typ in ("book", "monograph"):
        kind = "book"
    else:
        kind = "misc"
    f = [("author", " and ".join(auths)), ("title", bib_escape_title(r["title"]))]
    if kind == "inproceedings":
        f.append(("booktitle", r["venue"]))
    elif kind == "article":
        f.append(("journal", f"arXiv preprint arXiv:{r['arxiv']}" if r["arxiv"] and r["source"] == "arxiv" else r["venue"]))
        for k in ("volume", "issue"):
            if ex.get(k):
                f.append(("number" if k == "issue" else k, ex[k]))
    elif kind == "book" and ex.get("publisher"):
        f.append(("publisher", ex["publisher"]))
    if ex.get("pages"):
        f.append(("pages", str(ex["pages"]).replace("–", "--").replace("-", "--").replace("----", "--")))
    f.append(("year", str(r["year"] or "")))
    if r["doi"] and not r["doi"].startswith("10.48550"):
        f.append(("doi", r["doi"]))
    if r["arxiv"]:
        f += [("eprint", r["arxiv"]), ("archivePrefix", "arXiv")]
    if last_accessed:
        f.append(("note", f"Last accessed: {last_accessed}"))
    body = ",\n".join(f"  {k:<13}= {{{v}}}" if k != "title" else f"  {k:<13}= {v}" for k, v in f if v)
    return f"@{kind}{{{key},\n{body}\n}}\n"


def verify_entry(net: Net, e: dict, style: str, last_accessed: str | None) -> dict:
    doi = (e.get("doi") or "").strip().replace("https://doi.org/", "")
    arxiv = (e.get("arxiv") or "").strip()
    acl = (e.get("acl") or "").strip()
    out = {"key": e.get("key", ""), "identifiers": {k: v for k, v in (("doi", doi), ("arxiv", arxiv), ("acl", acl)) if v},
           "checked_at": now_iso(), "supports": e.get("supports", []), "secondary": []}
    primary = None
    if acl:
        primary = f_acl(net, acl)
        doi = doi or (primary or {}).get("doi", "")
    if not primary and doi:
        primary = f_crossref(net, doi) or f_datacite(net, doi)
    if not primary and arxiv:
        primary = f_arxiv(net, arxiv)
    if not primary:
        out["key"] = out["key"] or "unresolved_" + re.sub(r"[^a-z0-9]+", "_", (doi or arxiv or acl or "entry").lower()).strip("_")
        out["status"] = "not-found"
        out["note"] = "No primary record resolved. Do not cite; search again or mark [CITATION NEEDED]."
        return out
    out["primary"] = {k: primary[k] for k in ("source", "url", "title", "authors", "year", "venue", "doi", "arxiv")}
    out["abstract"] = primary["abstract"]
    if "arxiv" in primary["source"] or primary["arxiv"] or doi.startswith("10.48550"):
        arxiv = arxiv or primary["arxiv"]
    others = [f_openalex(net, doi if not doi.startswith("10.48550") else "", arxiv), f_s2(net, doi if not doi.startswith("10.48550") else "", arxiv, acl)]
    if arxiv and not primary["source"] == "arxiv":
        others.append(f_arxiv(net, arxiv))
    agreed, disagreed = 0, 0
    for o in others:
        if not o:
            continue
        ok, why = agree(primary, o)
        out["secondary"].append({"source": o["source"], "url": o["url"], "agrees": ok, "reasons": why})
        agreed += ok
        disagreed += (not ok)
        if not out["abstract"] and o["abstract"]:
            out["abstract"] = o["abstract"]
    if agreed >= 1 and (disagreed == 0 or agreed >= 2):
        out["status"] = "metadata-verified"
    elif disagreed:
        out["status"] = "conflict"
        out["note"] = "A second source disagrees; resolve against the publisher/proceedings page before citing."
    else:
        out["status"] = "single-source"
        out["note"] = "Only one index resolved this work; retry later or add another identifier."
    ex = primary.get("extra", {})
    if ex.get("published_doi") or ex.get("journal_ref"):
        out["version_hint"] = f"arXiv record points to a published version (doi={ex.get('published_doi') or '-'}, ref={ex.get('journal_ref') or '-'}); cite the version that supports your sentence."
    out["key"] = out["key"] or key_for(primary)
    out["bibtex"] = build_bibtex(out["key"], primary, style, last_accessed)
    sup = out["supports"]
    rels = {s.get("relation", "") for s in sup}
    if out["status"] == "metadata-verified":
        if not sup or not rels <= (GOOD_RELATIONS | WEAK_RELATIONS):
            out["claim_status"] = "pending"
        elif rels & WEAK_RELATIONS:
            out["claim_status"] = "weak"
        else:
            out["claim_status"] = "ok"
        if out["claim_status"] == "ok":
            out["status"] = "verified"
    return out


# --------------------------------------------------------------------------- commands
def cmd_search(args) -> int:
    net = Net(None, args.mailto)
    q = urllib.parse.quote(args.query)
    print(f"Candidates for: {args.query}\n(Candidates are NOT citations. Resolve an identifier, then run `verify`.)\n")
    st, body = net.get(f"https://api.openalex.org/works?search={q}&per-page={args.limit}&select=id,title,publication_year,doi,authorships,primary_location")
    if st == 200:
        for w in json.loads(body).get("results", []):
            a = [x["author"]["display_name"] for x in w.get("authorships", [])[:3] if x.get("author")]
            src = ((w.get("primary_location") or {}).get("source") or {}).get("display_name", "")
            print(f"[openalex] {w.get('title')}\n    {', '.join(a)}{' et al.' if len(w.get('authorships', [])) > 3 else ''} | {w.get('publication_year')} | {src}\n    doi: {(w.get('doi') or '-').replace('https://doi.org/', '')}")
    else:
        print(f"[openalex] unavailable (http {st})")
    st, body = net.get(f"https://api.semanticscholar.org/graph/v1/paper/search?query={q}&limit={args.limit}&fields=title,year,authors,venue,externalIds")
    if st == 200:
        for p in json.loads(body).get("data", []):
            ext = p.get("externalIds") or {}
            a = [x["name"] for x in p.get("authors", [])[:3]]
            print(f"[s2] {p.get('title')}\n    {', '.join(a)} | {p.get('year')} | {p.get('venue', '')}\n    doi: {ext.get('DOI', '-')}  arxiv: {ext.get('ArXiv', '-')}  acl: {ext.get('ACL', '-')}")
    else:
        print(f"[semantic-scholar] unavailable (http {st}); this is a rate limit, not 'no results'")
    return 0


def cmd_verify(args) -> int:
    root = Path(args.project).resolve()
    req = load_json(args.requests or root / "citation_requests.json")
    net = Net(root / ".paper" / "cache" / "citations", args.mailto, args.offline)
    lock_path = root / "citation_lock.json"
    lock = load_json(lock_path, {"schema": "paper-skill/citation-lock-v1", "entries": {}})
    bib_path = root / "paper" / "references.bib"
    bib_path.parent.mkdir(parents=True, exist_ok=True)
    existing = bib_path.read_text(encoding="utf-8") if bib_path.exists() else ""
    rows, bib_new = [], []
    for e in req.get("entries", []):
        res = verify_entry(net, e, args.style, args.last_accessed)
        k = res["key"]
        lock["entries"][k] = {kk: vv for kk, vv in res.items() if kk != "bibtex"}
        if res.get("bibtex") and res["status"] in ("verified", "metadata-verified", "single-source"):
            lock["entries"][k]["bib_sha256"] = hashlib.sha256(res["bibtex"].encode()).hexdigest()
            if re.search(rf"@\w+\s*\{{\s*{re.escape(k)}\s*,", existing):
                existing = re.sub(rf"@\w+\s*\{{\s*{re.escape(k)}\s*,.*?\n\}}\n", res["bibtex"], existing, flags=re.S)
            else:
                bib_new.append(res["bibtex"])
        rows.append((k, res["status"], res.get("primary", {}).get("source", "-"),
                     ",".join(s["source"] for s in res["secondary"] if s["agrees"]) or "-", res.get("note", "")))
    header = "% Generated by scripts/citations.py from fetched metadata. Do not hand-edit; re-run verify.\n" if not existing else ""
    bib_path.write_text(header + existing.rstrip() + ("\n\n" if existing.strip() else "") + "\n".join(bib_new), encoding="utf-8")
    save_json(lock_path, lock)
    md = ["# Citation verification", "", f"_Checked {now_iso()}. `verified` requires primary + independent index agreement and a read sentence-level relation._", "",
          "| Key | Status | Primary | Agreeing index | Note |", "|---|---|---|---|---|"]
    md += [f"| {k} | {s} | {p} | {a} | {n} |" for k, s, p, a, n in rows]
    (root / "citation_verification.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    for k, s, p, a, n in rows:
        print(f"{s:18} {k}  [{p} + {a}] {n}")
    print(f"\nwrote {bib_path}, {lock_path}, citation_verification.md")
    pending = [r for r in rows if r[1] != "verified"]
    if pending:
        print(f"{len(pending)} entr{'y is' if len(pending) == 1 else 'ies are'} not final-ready. Read each abstract in citation_lock.json, set supports[].relation, and rerun.")
    return 0


def collect_keys(root: Path) -> tuple[dict[str, list[str]], bool, list[str]]:
    cited: dict[str, list[str]] = {}
    markers = []
    nocite_all = False
    for p in tex_files(root):
        text = p.read_text(encoding="utf-8", errors="replace")
        text = re.sub(r"(?<!\\)%.*", "", text)
        for i, line in enumerate(text.splitlines(), 1):
            if re.match(r"\s*\\(?:provide|new|renew)command", line):
                continue
            for m in CITE_RE.finditer(line):
                for k in (x.strip() for x in m.group(1).split(",")):
                    if k and not k.startswith("#"):
                        cited.setdefault(k, []).append(f"{p.name}:{i}")
            if NOCITE_RE.search(line) and "*" in NOCITE_RE.search(line).group(1):
                nocite_all = True
            if re.search(r"\[CITATION NEEDED|PLACEHOLDER_|\bTODO-CITE\b", line):
                markers.append(f"{p.name}:{i}")
    return cited, nocite_all, markers


def cmd_check(args) -> int:
    root = Path(args.project).resolve()
    cited, _, markers = collect_keys(root)
    bibs = [p for p in root.rglob("*.bib") if ".paper" not in p.parts]
    keys, dups = {}, []
    for b in bibs:
        for k in re.findall(r"@(?!comment|string|preamble)\w+\s*\{\s*([^,\s]+)\s*,", b.read_text(encoding="utf-8", errors="replace"), flags=re.I):
            if k in keys:
                dups.append(k)
            keys[k] = b.name
    lock = load_json(root / "citation_lock.json", {"entries": {}})["entries"]
    errors, warns = [], []
    for k, where in sorted(cited.items()):
        if k not in keys:
            errors.append(f"cited key '{k}' has no BibTeX entry ({where[0]})")
        elif k.startswith("PLACEHOLDER_"):
            errors.append(f"placeholder citation '{k}' still in text ({where[0]})")
        else:
            st = lock.get(k, {}).get("status")
            if st != "verified":
                (errors if args.strict else warns).append(f"'{k}' is not verified (status: {st or 'not in lock'}) ({where[0]})")
            elif lock[k].get("claim_status") == "weak":
                errors.append(f"'{k}' only partially supports its sentence; revise the sentence or replace the source")
    for d in sorted(set(dups)):
        errors.append(f"duplicate BibTeX key '{d}' (LaTeX silently uses one entry)")
    for m in markers:
        (errors if args.strict else warns).append(f"unresolved citation marker at {m}")
    unused = sorted(set(keys) - set(cited))
    if unused:
        warns.append(f"{len(unused)} bibliography entries are never cited: {', '.join(unused[:8])}{' ...' if len(unused) > 8 else ''}")
    print(f"cited keys: {len(cited)} | bib entries: {len(keys)} | verified in lock: {sum(1 for k in cited if lock.get(k, {}).get('status') == 'verified')}")
    for w in warns:
        print("warning:", w)
    for e in errors:
        print("ERROR:", e)
    print("PASS" if not errors else f"FAIL ({len(errors)} errors)")
    return 1 if errors else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search")
    s.add_argument("query")
    s.add_argument("--limit", type=int, default=5)
    s.add_argument("--mailto")
    v = sub.add_parser("verify")
    v.add_argument("project")
    v.add_argument("--requests")
    v.add_argument("--style", choices=["ieee", "acl"], default="ieee")
    v.add_argument("--mailto", help="optional contact for polite API pools; never sent unless provided")
    v.add_argument("--offline", action="store_true", help="use cached responses only")
    v.add_argument("--last-accessed", help="adds a 'Last accessed' note to every entry (IEEE-lab convention)")
    c = sub.add_parser("check")
    c.add_argument("project")
    c.add_argument("--strict", action="store_true", help="every cited key must be `verified`")
    args = ap.parse_args()
    return {"search": cmd_search, "verify": cmd_verify, "check": cmd_check}[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
