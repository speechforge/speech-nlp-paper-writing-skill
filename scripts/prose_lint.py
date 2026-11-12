#!/usr/bin/env python3
"""Prose linter for research manuscripts (LaTeX or Markdown).

Enforces three rules from the skill:
  1. No coding terms in the paper: no code spans, file names, flags, identifiers.
  2. Human, specific English: no stock AI phrases, hollow openers, or filler.
  3. Comparative Adjective Law: no unbacked "best / superior / state-of-the-art".

    prose_lint.py PATH [PATH ...] [--fail-on high|medium|low|never] [--json] [--allow words.txt]

PATH may be files or folders (*.tex, *.md). Math, comments, tables, and verbatim blocks are
ignored. Sections named availability / reproducibility / appendix / artifact may mention
implementation vocabulary (never code spans or file names).
Exit code 1 when a finding at or above --fail-on exists (default: high).
"""
from __future__ import annotations

import argparse
import bisect
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import strip_tex_noise  # noqa: E402

SEV = {"high": 3, "medium": 2, "low": 1}
EXEMPT_SECTION = re.compile(r"availab|reproduc|appendix|artifact|supplement", re.I)
SECTION_RE = re.compile(r"\\(?:section|subsection|subsubsection|paragraph)\*?\{([^}]*)\}|^#{1,4}\s+(.+)$", re.M)

CODE_PATTERNS = [
    ("code-span", "high", re.compile(r"`[^`\n]+`"), "backtick code span; describe the idea in plain scientific language"),
    ("code-span", "high", re.compile(r"\\(?:texttt|verb|lstinline|code)\b"), "typewriter/code markup in prose"),
    ("file-name", "high", re.compile(r"\b[\w./-]+\.(?:py|ipynb|json|ya?ml|sh|toml|cfg|ini|pt|pth|ckpt|npz|npy|pkl|csv|tsv|log|cpp|js|ts)\b"), "file name in prose; name the artifact by what it is"),
    ("cli-flag", "high", re.compile(r"(?<![\w-])--[a-z][a-z0-9-]{2,}"), "command-line flag in prose; state the setting as a value with its meaning"),
    ("shell-command", "high", re.compile(r"\b(?:pip|conda|apt|npm)\s+install\b|\bgit\s+(?:clone|commit|push|pull|checkout)\b|\bpython3?\s+\S+\.py\b|\bdocker\s+(?:run|build)\b"), "shell command in prose"),
    ("function-call", "high", re.compile(r"\b[A-Za-z_][\w.]*\(\)|\b[a-z_]\w*\([a-z_]\w*\s*=[^)]*\)"), "function call in prose; describe the operation instead"),
    ("identifier", "high", re.compile(r"\b[a-z]+(?:_[a-z0-9]+){1,}\b"), "snake_case identifier; use the concept name (for example 'learning rate')"),
    ("identifier", "medium", re.compile(r"\b[a-z]{2,}[A-Z][a-zA-Z]*\b"), "camelCase identifier; use the concept name"),
]
CAMEL_ALLOW = {"dB", "kHz", "mHz", "mAP", "nDCG", "fMRI", "mBART", "iPhone", "eBay", "mRNA", "dBFS", "mT5", "xRT", "eGeMAPS", "wav2vec", "mHuBERT", "tSNE", "pH", "iOS", "macOS", "gRPC", "iVector", "xVector", "iPad", "eSpeak"}
IMPL_WORDS = re.compile(r"\b(?:codebase|repo|repository|script|scripts|config(?:uration)? file|yaml|dataloader|data loader|notebook|commit|branch|pull request|stdout|stderr|traceback|wrapper|boilerplate|hard-?coded|monkey[- ]?patch|kwargs|argparse|cli|api key|environment variable|requirements\.txt|makefile)\b", re.I)

AI_PHRASES = [
    r"\bdelv(?:e|es|ing)\b", r"\btapestry\b", r"\bin the realm of\b", r"\bit is (?:worth|important to) (?:noting|note|mention)\b",
    r"\bplays? an? (?:crucial|vital|pivotal|important|key|significant) role\b", r"\bgame[- ]chang", r"\bcutting[- ]edge\b",
    r"\bgroundbreaking\b", r"\brevolutioni[sz]", r"\bunprecedented\b", r"\bseamless(?:ly)?\b", r"\ba testament to\b",
    r"\bunderscores?\b", r"\bnavigat(?:e|ing) the complexit", r"\bever[- ](?:growing|evolving|changing)\b", r"\bin today'?s\b",
    r"\bin the (?:rapidly|ever) (?:evolving|changing)\b", r"\bharness(?:es|ing)? the power\b", r"\bmyriad\b", r"\bparamount\b",
    r"\bembark(?:s|ed|ing)?\b", r"\bunlock(?:s|ed|ing)? the (?:potential|power)\b", r"\bshed(?:s|ding)? light on\b", r"\bthe landscape of\b",
    r"\bholistic\b", r"\bmultifaceted\b", r"\bintricate\b", r"\bcomprehensive(?:ly)?\b", r"\bat the forefront\b", r"\bpave(?:s|d)? the way\b",
]
OPENERS = re.compile(r"\b(?:in recent years|deep learning has|has (?:gained|attracted|received) (?:immense|significant|considerable|increasing|growing) (?:attention|interest)|has revolutioni[sz]ed|remarkable (?:success|progress)|with the (?:rapid|recent) (?:development|advances?|rise))\b", re.I)
UNBACKED = [
    (r"\b(?:achieves?|achieving|new|sets?|establish(?:es)?) (?:a )?(?:new )?state[- ]of[- ]the[- ]art\b", "state-of-the-art claim needs named baselines, dataset, effect size, and uncertainty"),
    (r"\bstate[- ]of[- ]the[- ]art (?:performance|results?|accuracy|quality)\b", "state-of-the-art claim needs named baselines, dataset, effect size, and uncertainty"),
    (r"\boutperforms? (?:all|every|any) (?:existing|prior|previous|other)\b", "universal comparison; bound it to the tested baselines"),
    (r"\b(?:best|superior|unmatched|unrivall?ed)\b(?! (?:of|in) (?:both|the two))", "superlative; name baseline, dataset, number, and uncertainty or remove"),
    (r"\b(?:drastic(?:ally)?|dramatic(?:ally)?|massive(?:ly)?|vastly|tremendous(?:ly)?)\b", "intensifier without a number; give the effect size"),
    (r"\bfirst (?:to|work|study|paper|approach)\b", "priority claim; needs an exhaustive, recorded literature search"),
    (r"\b(?:significantly|substantially|considerably) (?:better|improv|outperform|higher|lower|faster|reduc)", "'significant' language needs a test and p-value or confidence interval"),
]
FILLER = re.compile(r"\b(?:very|really|quite|basically|essentially|actually|simply|just|rather|extremely|highly|fairly)\b", re.I)
HEDGE = re.compile(r"\b(?:may|might|could|perhaps|possibly|arguably)\b", re.I)
VAGUE_THIS = re.compile(r"(?:^|[.!?]\s+)This (?:is|was|shows?|means|suggests?|indicates?|demonstrates?|allows?|enables?|leads?|results?)\b")
TRANSITION = re.compile(r"(?:^|[.!?]\s+)(?:Moreover|Furthermore|Additionally|In addition),")


def load_allow(path: str | None) -> set[str]:
    if not path:
        return set()
    return {ln.strip() for ln in Path(path).read_text(encoding="utf-8").splitlines() if ln.strip() and not ln.startswith("#")}


def clean_markdown(text: str, findings: list, rel: str) -> str:
    def fence(m):
        line = text[: m.start()].count("\n") + 1
        findings.append((rel, line, "high", "code-block", "fenced code block inside the manuscript", m.group(0)[:60].replace("\n", " ")))
        return re.sub(r"[^\n]", " ", m.group(0))
    return re.sub(r"```.*?```", fence, text, flags=re.S)


def to_prose(text: str, is_tex: bool) -> str:
    if is_tex:
        text = strip_tex_noise(text)
        text = text.replace("\\_", "_")
        text = re.sub(r"\\(?:textbf|textit|emph|textsc|text|mbox)\{", " ", text)
        text = re.sub(r"\\(?:texttt|verb|lstinline|code)\b", lambda m: m.group(0), text)
        text = re.sub(r"\\(?!(?:texttt|verb|lstinline|code)\b)[a-zA-Z]+\*?", " ", text)
        text = text.replace("{", " ").replace("}", " ").replace("~", " ")
    return text


def section_at(sections: list[tuple[int, str]], offset: int) -> str:
    name = ""
    for pos, title in sections:
        if pos <= offset:
            name = title
        else:
            break
    return name


def lint(path: Path, allow: set[str]) -> list[tuple]:
    raw = path.read_text(encoding="utf-8", errors="replace")
    is_tex = path.suffix == ".tex"
    rel = str(path)
    findings: list[tuple] = []
    if not is_tex:
        raw = clean_markdown(raw, findings, rel)
    if is_tex and "\\begin{document}" in raw:  # the preamble and author block are not prose
        cut = raw.index("\\begin{document}")
        raw = re.sub(r"[^\n]", " ", raw[:cut]) + raw[cut:]
    sections = [(m.start(), m.group(1) or m.group(2) or "") for m in SECTION_RE.finditer(raw)]
    prose = to_prose(raw, is_tex)

    def add(off, sev, cat, msg, snip=""):
        line = prose.count("\n", 0, off) + 1
        findings.append((rel, line, sev, cat, msg, snip.strip()[:80]))

    bounds = [m.end() for m in re.finditer(r"(?<!\d)(?<!e\.g)(?<!i\.e)(?<!et al)(?<!Fig)[.!?](?=\s|$)|\n\s*\n", prose)]
    for cat, sev, pat, msg in CODE_PATTERNS:
        for m in pat.finditer(prose):
            tok = m.group(0)
            if tok in allow or tok in CAMEL_ALLOW:
                continue
            if cat == "identifier" and sev == "medium" and (tok in CAMEL_ALLOW or tok[0].isupper()):
                continue
            if cat == "identifier" and re.search(r"[A-Z]", tok) is None and "_" in tok and prose[max(0, m.start() - 1): m.start()] in ("@", "/", "-"):
                continue
            add(m.start(), sev, cat, msg, tok)
    for m in IMPL_WORDS.finditer(prose):
        if EXEMPT_SECTION.search(section_at(sections, m.start())) or m.group(0).lower() in allow or "statements" in path.parts or "appendix" in path.stem.lower():
            continue
        add(m.start(), "medium", "implementation-vocabulary", "implementation vocabulary in the scientific narrative; describe the method, not the software", m.group(0))
    for pat in AI_PHRASES:
        for m in re.finditer(pat, prose, re.I):
            add(m.start(), "medium", "stock-phrase", "stock phrase that reads as machine-written; say the specific thing", m.group(0))
    for m in OPENERS.finditer(prose):
        add(m.start(), "medium", "hollow-opener", "generic opener; start from the concrete technical problem", m.group(0))
    for pat, msg in UNBACKED:
        for m in re.finditer(pat, prose, re.I):
            i = bisect.bisect_right(bounds, m.start())
            sentence = prose[(bounds[i - 1] if i else 0): (bounds[i] if i < len(bounds) else len(prose))]
            backed = re.search(r"\d+(?:\.\d+)?\s*(?:%|dB|Hz|kHz|ms|points?|pp|x|WER|MOS)|Table~?\s*\S|Fig(?:ure|\.)~?\s*\S|\bp\s*[<=]|confidence interval", sentence)
            if backed and "first" not in pat:
                continue
            add(m.start(), "medium", "unbacked-claim", msg, m.group(0))
    for m in FILLER.finditer(prose):
        add(m.start(), "low", "filler", "filler word; delete or replace with a measured fact", m.group(0))
    for m in VAGUE_THIS.finditer(prose):
        add(m.start(), "low", "vague-pronoun", "'This <verb>' without a noun; write 'This result/effect/gap ...'", m.group(0).strip(". "))
    words = max(len(re.findall(r"\w+", prose)), 1)
    hedges = len(HEDGE.findall(prose))
    if words > 250 and hedges / words > 0.012:
        add(0, "low", "hedging", f"{hedges} hedges in {words} words; keep 'may/might' only where the evidence is genuinely uncertain")
    trans = len(TRANSITION.findall(prose))
    if words > 250 and trans / words > 0.004:
        add(0, "low", "transition-tic", f"{trans} sentence-initial Moreover/Furthermore/Additionally; use logical connectives that carry meaning")
    if len(re.findall(r"not only\b.{0,80}\bbut also\b", prose, re.I | re.S)) > 2:
        add(0, "low", "stock-phrase", "'not only ... but also' used more than twice")
    off = 0
    for para in re.split(r"\n\s*\n", prose):
        n = len(re.findall(r"\w+", para))
        if n > 230:
            add(off, "low", "long-paragraph", f"paragraph of {n} words; one message per paragraph", para[:40])
        for s in re.split(r"(?<=[.!?])\s+(?=[A-Z])", para):
            k = len(re.findall(r"\w+", s))
            if k > 55:
                add(off, "low", "long-sentence", f"sentence of {k} words; split it", s[:60])
        off += len(para) + 2
    findings.sort(key=lambda f: (f[0], f[1]))
    return findings


def collect(paths: list[str]) -> list[Path]:
    out = []
    skip = {".git", ".paper", "node_modules", "__pycache__", "statements_build"}
    for p in map(Path, paths):
        if p.is_file():
            out.append(p)
        elif p.is_dir():
            out += [q for q in sorted(p.rglob("*")) if q.suffix in (".tex", ".md") and not (set(q.parts) & skip)]
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--fail-on", choices=["high", "medium", "low", "never"], default="high")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--allow", help="file with terms to ignore, one per line")
    ap.add_argument("--min", choices=["high", "medium", "low"], default="low", help="hide findings below this severity")
    args = ap.parse_args()
    files = collect(args.paths)
    if not files:
        raise SystemExit("error: no .tex or .md files found")
    allow = load_allow(args.allow)
    all_f = [f for p in files for f in lint(p, allow)]
    shown = [f for f in all_f if SEV[f[2]] >= SEV[args.min]]
    if args.json:
        print(json.dumps([dict(zip(("file", "line", "severity", "category", "message", "snippet"), f)) for f in shown], indent=2))
    else:
        for f in shown:
            print(f"{f[0]}:{f[1]} [{f[2]}] {f[3]}: {f[4]}" + (f"  <<{f[5]}>>" if f[5] else ""))
        counts = {s: sum(1 for f in all_f if f[2] == s) for s in SEV}
        print(f"\n{len(files)} file(s): {counts['high']} high, {counts['medium']} medium, {counts['low']} low")
    if args.fail_on == "never":
        return 0
    return 1 if any(SEV[f[2]] >= SEV[args.fail_on] for f in all_f) else 0


if __name__ == "__main__":
    raise SystemExit(main())
