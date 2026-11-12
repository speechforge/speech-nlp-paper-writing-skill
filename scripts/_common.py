"""Shared helpers for the paper-writing skill scripts (standard library only)."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path

# Venue / publisher names must never appear in a project's public identity
# (project name, demo-website title, demo-website headings).
VENUE_TOKENS = [
    "ACL", "EMNLP", "NAACL", "EACL", "AACL", "COLING", "ARR", "TACL", "COLM",
    "ICASSP", "Interspeech", "ISCA", "IEEE", "IJCNN", "EUSIPCO", "SLT", "ASRU", "TASLP",
    "NeurIPS", "NIPS", "ICML", "ICLR", "AAAI", "CVPR", "ICCV", "ECCV", "ACM",
]
_VENUE_RE = re.compile(r"(?<![A-Za-z0-9])(" + "|".join(map(re.escape, VENUE_TOKENS)) + r")(?![a-z0-9])", re.I)

CREDIT_ROLES = [
    "Conceptualization", "Data curation", "Formal analysis", "Funding acquisition",
    "Investigation", "Methodology", "Project administration", "Resources", "Software",
    "Supervision", "Validation", "Visualization", "Writing - original draft",
    "Writing - review & editing",
]


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-").lower()
    return text or "project"


def venue_words(text: str) -> list[str]:
    """Return venue/publisher tokens found in `text` (case-insensitive, whole word)."""
    found = []
    for m in _VENUE_RE.finditer(text or ""):
        # Short all-caps tokens such as ACL/ARR/SLT must be written in caps to count;
        # this avoids flagging ordinary words that happen to match.
        tok = m.group(1)
        if tok.upper() in {"ACL", "ARR", "SLT", "ACM", "NIPS"} and tok != tok.upper():
            continue
        found.append(tok)
    return sorted(set(found), key=str.lower)


def read_text(path: Path, limit: int | None = None) -> str:
    data = Path(path).read_bytes()
    if limit is not None:
        data = data[:limit]
    return data.decode("utf-8", errors="replace")


def load_json(path: Path, default=None):
    path = Path(path)
    if not path.exists():
        if default is not None:
            return default
        raise FileNotFoundError(f"Missing required file: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"error: {path} is not valid JSON ({exc})")


def save_json(path: Path, obj) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=False) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            chunk = fh.read(1 << 20)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def find_project_root(start: Path) -> Path:
    """Walk upward from `start` until a project_meta.json or paper_state.json is found."""
    start = Path(start).resolve()
    for cand in [start, *start.parents]:
        if (cand / "project_meta.json").exists() or (cand / "paper_state.json").exists():
            return cand
    return start


def eprint(*a) -> None:
    print(*a, file=sys.stderr)


def tex_files(root: Path) -> list[Path]:
    root = Path(root)
    if root.is_file():
        return [root]
    skip = {".git", ".paper", "node_modules", "__pycache__"}
    return sorted(p for p in root.rglob("*.tex") if not (set(p.parts) & skip))


def strip_tex_noise(text: str) -> str:
    """Remove comments, math, verbatim, and table bodies so prose checks see sentences only.

    Line structure is preserved (removed regions are replaced by blanks/newlines)
    so reported line numbers stay accurate.
    """
    def blank(m):  # keep newlines so line numbers survive
        return re.sub(r"[^\n]", " ", m.group(0))

    text = re.sub(r"(?<!\\)%.*", lambda m: " " * len(m.group(0)), text)
    env_pat = r"\\begin\{(verbatim\*?|lstlisting|minted|equation\*?|align\*?|eqnarray\*?|gather\*?|multline\*?|tabular\*?|tikzpicture|algorithm\*?|algorithmic|thebibliography)\}.*?\\end\{\1\}"
    text = re.sub(env_pat, blank, text, flags=re.S)
    text = re.sub(r"\$\$.*?\$\$", blank, text, flags=re.S)
    text = re.sub(r"\\\[.*?\\\]", blank, text, flags=re.S)
    text = re.sub(r"(?<!\\)\$[^$\n]*?(?<!\\)\$", lambda m: " " * len(m.group(0)), text)
    text = re.sub(r"\\(cite[a-zA-Z]*|ref|eqref|autoref|cref|Cref|label|url|href|includegraphics|input|include|bibliography|bibliographystyle|usepackage|documentclass)(\[[^\]]*\])*\{[^}]*\}", lambda m: " " * len(m.group(0)), text)
    return text
