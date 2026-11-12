#!/usr/bin/env python3
"""Condense a context file or a project directory into one compact brief.

Purpose: let an agent (Claude, ChatGPT, Codex, Gemini, ...) understand a research
project by reading ONE small digest instead of crawling hundreds of files.
It is read-only, uses only the standard library, and caps its own output size.

    python3 scripts/context_digest.py PATH [-o context_digest.md] [--max-chars 24000]

PATH may be a single notes/markdown/text/LaTeX/notebook file or a directory.
The digest has a section called "Implementation vocabulary". Those identifiers
exist only to help the agent understand the method. They must be translated into
scientific language and must never be printed in the paper.
"""
from __future__ import annotations

import argparse
import ast
import csv
import json
import re
import statistics
import wave
from collections import Counter
from pathlib import Path

SKIP_DIRS = {".git", ".hg", ".svn", "node_modules", "__pycache__", ".venv", "venv", "env",
             ".idea", ".vscode", ".mypy_cache", ".pytest_cache", ".ipynb_checkpoints",
             "wandb", "mlruns", "lightning_logs", ".paper", "site-packages", "build", "dist"}
DOC_EXT = {".md", ".markdown", ".txt", ".rst", ".tex"}
TABLE_EXT = {".csv", ".tsv"}
MEDIA_EXT = {".png", ".jpg", ".jpeg", ".svg", ".pdf", ".wav", ".flac", ".mp3", ".ogg", ".mp4", ".webm", ".gif"}
CONFIG_KEYS = ["learning_rate", "lr", "batch_size", "epochs", "num_epochs", "max_steps", "optimizer",
               "weight_decay", "warmup", "dropout", "seed", "sample_rate", "sampling_rate", "n_fft",
               "hop_length", "n_mels", "num_layers", "hidden_dim", "d_model", "num_heads",
               "beam_size", "temperature", "max_length", "gpu", "precision", "fp16", "bf16"]
RESULT_HINT = re.compile(r"(result|metric|eval|score|output|experiment|benchmark|ablation|table|log)", re.I)
ID_PAT = re.compile(r"(?:arxiv[:/ ]*(\d{4}\.\d{4,5})(?:v\d+)?)|(?:\b(10\.\d{4,9}/[^\s\"'<>)\]]+))", re.I)
UNCERTAINTY = re.compile(r"(?:^|[_\- ])(?:std|stdev|sd|sem|se|ci|ci95|ci_?lo|ci_?hi|stderr|conf|confidence)(?:[_\- ]|$)|±")
HEADING = re.compile(r"^(#{1,4})\s+(.+?)\s*$")


def human(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f}{unit}" if unit == "B" else f"{n:.1f}{unit}"
        n /= 1024
    return f"{n}B"


def read_head(path: Path, nbytes: int = 60000) -> str:
    try:
        return path.read_bytes()[:nbytes].decode("utf-8", errors="replace")
    except OSError:
        return ""


def walk(root: Path):
    for p in sorted(root.rglob("*")):
        if any(part in SKIP_DIRS for part in p.relative_to(root).parts):
            continue
        if p.is_file():
            yield p


def section_tree(files: list[Path], root: Path) -> str:
    ext = Counter(p.suffix.lower() or "(none)" for p in files)
    top = Counter(p.relative_to(root).parts[0] if len(p.relative_to(root).parts) > 1 else "(root)" for p in files)
    lines = ["## 1. Layout", f"- files: {len(files)}; by type: " + ", ".join(f"{k} {v}" for k, v in ext.most_common(10)),
             "- top-level folders: " + ", ".join(f"{k}/ ({v})" for k, v in top.most_common(12))]
    return "\n".join(lines)


def summarize_doc(path: Path, root: Path, max_lines: int = 14) -> str:
    text = read_head(path, 20000)
    heads = [m.group(2) for line in text.splitlines() if (m := HEADING.match(line))][:10]
    if path.suffix == ".tex":
        heads = re.findall(r"\\(?:section|subsection)\*?\{([^}]*)\}", text)[:10] or heads
    body = [ln.strip() for ln in text.splitlines() if ln.strip() and not ln.startswith(("#", "\\", "```", "---"))][:max_lines]
    out = [f"### {path.relative_to(root)}"]
    if heads:
        out.append("headings: " + " | ".join(heads))
    out.append("\n".join("> " + b[:220] for b in body[:max_lines]))
    return "\n".join(out)


def summarize_notebook(path: Path, root: Path) -> str:
    try:
        nb = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError:
        return f"### {path.relative_to(root)} (unreadable notebook)"
    md = []
    for cell in nb.get("cells", []):
        if cell.get("cell_type") == "markdown":
            md.append("".join(cell.get("source", []))[:300].replace("\n", " "))
    return f"### {path.relative_to(root)} (notebook)\n" + "\n".join("> " + m for m in md[:8] if m)


def summarize_table(path: Path, root: Path) -> str:
    delim = "\t" if path.suffix == ".tsv" else ","
    try:
        with open(path, newline="", encoding="utf-8", errors="replace") as fh:
            rows = list(csv.reader(fh, delimiter=delim))
    except (OSError, csv.Error):
        return f"### {path.relative_to(root)} (unreadable table)"
    if not rows:
        return f"### {path.relative_to(root)} (empty)"
    head, data = rows[0], rows[1:]
    lines = [f"### {path.relative_to(root)}  ({len(data)} rows; columns: {', '.join(head[:14])}{' ...' if len(head) > 14 else ''})"]
    stats = []
    for j, name in enumerate(head[:14]):
        vals = []
        for r in data:
            if j < len(r):
                try:
                    vals.append(float(r[j]))
                except ValueError:
                    pass
        if len(vals) >= max(2, len(data) // 2):
            stats.append(f"{name}: min {min(vals):.4g}, mean {statistics.fmean(vals):.4g}, max {max(vals):.4g}")
    if stats:
        lines.append("numeric: " + "; ".join(stats[:8]))
    for j, name in enumerate(head[:6]):
        cats = Counter(r[j] for r in data if j < len(r) and r[j] and not re.fullmatch(r"-?[\d.eE+-]+", r[j]))
        if 1 < len(cats) <= 12:
            lines.append(f"levels of {name}: " + ", ".join(sorted(cats)[:12]))
    lowered = [h.lower() for h in head]
    lines.append(f"seed column: {'yes' if any('seed' in h for h in lowered) else 'NO'}; "
                 f"uncertainty column (std/ci/err): {'yes' if any(UNCERTAINTY.search(h) for h in lowered) else 'NO'}")
    return "\n".join(lines)


def summarize_json(path: Path, root: Path) -> str:
    try:
        obj = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except (json.JSONDecodeError, OSError):
        return ""
    if isinstance(obj, dict):
        keys = list(obj)[:16]
        nums = {k: obj[k] for k in keys if isinstance(obj[k], (int, float))}
        return f"### {path.relative_to(root)}  keys: {', '.join(keys)}" + (f"\nscalars: {json.dumps(nums)[:300]}" if nums else "")
    if isinstance(obj, list):
        return f"### {path.relative_to(root)}  list of {len(obj)} items" + (f"; first keys: {', '.join(list(obj[0])[:10])}" if obj and isinstance(obj[0], dict) else "")
    return ""


def summarize_python(path: Path, root: Path) -> str:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except (SyntaxError, ValueError):
        return ""
    doc = (ast.get_docstring(tree) or "").strip().splitlines()
    classes = [n.name for n in tree.body if isinstance(n, ast.ClassDef)]
    funcs = [n.name for n in tree.body if isinstance(n, ast.FunctionDef) and not n.name.startswith("_")]
    if not (doc or classes or funcs):
        return ""
    line = f"- {path.relative_to(root)}: {doc[0][:140] if doc else '(no docstring)'}"
    if classes:
        line += f" | classes: {', '.join(classes[:6])}"
    if funcs:
        line += f" | functions: {', '.join(funcs[:8])}"
    return line


def find_config_values(files: list[Path], root: Path) -> list[str]:
    hits: dict[str, set[str]] = {}
    cfg_files = [p for p in files if p.suffix.lower() in {".yaml", ".yml", ".json", ".toml", ".cfg", ".ini"} and p.stat().st_size < 200000]
    for p in cfg_files[:40]:
        text = read_head(p, 40000)
        for key in CONFIG_KEYS:
            for m in re.finditer(rf"[\"']?\b{key}\b[\"']?\s*[:=]\s*([^\s,#}}]+)", text, re.I):
                hits.setdefault(key, set()).add(m.group(1).strip("\"'")[:24])
    return [f"{k} = {', '.join(sorted(v)[:4])}" for k, v in sorted(hits.items())]


def find_identifiers(files: list[Path]) -> list[str]:
    found: dict[str, str] = {}
    for p in files:
        if p.suffix.lower() in DOC_EXT | {".py", ".ipynb", ".bib", ".json"} and p.stat().st_size < 400000:
            for m in ID_PAT.finditer(read_head(p, 100000)):
                if m.group(1):
                    found.setdefault("arXiv:" + m.group(1), str(p.name))
                elif m.group(2):
                    found.setdefault("doi:" + m.group(2).rstrip(".,;"), str(p.name))
    return [f"{k}  (in {v})" for k, v in sorted(found.items())][:40]


def summarize_bib(files: list[Path], root: Path) -> list[str]:
    out = []
    for p in files:
        if p.suffix.lower() == ".bib":
            keys = re.findall(r"@\w+\s*\{\s*([^,\s]+)\s*,", read_head(p, 400000))
            out.append(f"{p.relative_to(root)}: {len(keys)} entries (these are CANDIDATES; verify before citing)")
    return out


def describe_media(files: list[Path], root: Path) -> list[str]:
    out = []
    for p in files:
        if p.suffix.lower() not in MEDIA_EXT:
            continue
        info = human(p.stat().st_size)
        if p.suffix.lower() == ".wav":
            try:
                with wave.open(str(p), "rb") as w:
                    info += f", {w.getframerate()} Hz, {w.getnchannels()} ch, {w.getnframes() / max(w.getframerate(), 1):.1f}s"
            except (wave.Error, EOFError):
                pass
        out.append(f"{p.relative_to(root)} ({info})")
    return out


def digest_dir(root: Path, max_chars: int) -> str:
    files = list(walk(root))
    parts = [f"# Context digest: {root.name}", "",
             "_Auto-generated, read-only. Evidence = items from the results/tables sections; everything else is intent or context._", "",
             section_tree(files, root), ""]

    docs = [p for p in files if p.suffix.lower() in DOC_EXT and p.stat().st_size < 400000]
    docs.sort(key=lambda p: (0 if p.name.lower().startswith(("readme", "notes", "abstract", "paper", "story")) else 1, len(p.parts)))
    parts += ["## 2. Notes and documents (headings + first lines)"]
    parts += [summarize_doc(p, root) for p in docs[:10]]
    parts += [summarize_notebook(p, root) for p in files if p.suffix == ".ipynb"][:4]
    parts.append("")

    tables = [p for p in files if p.suffix.lower() in TABLE_EXT and p.stat().st_size < 5_000_000]
    tables.sort(key=lambda p: (0 if RESULT_HINT.search(str(p.relative_to(root))) else 1, str(p)))
    jsons = [p for p in files if p.suffix.lower() == ".json" and RESULT_HINT.search(str(p.relative_to(root)))
             and p.stat().st_size < 2_000_000 and "package" not in p.name and "tsconfig" not in p.name]
    parts += ["## 3. Result candidates (tables / metrics files) - the only source of numbers"]
    parts += [summarize_table(p, root) for p in tables[:10]]
    parts += [s for s in (summarize_json(p, root) for p in jsons[:8]) if s]
    if not tables and not jsons:
        parts.append("- none found: every quantitative claim needs an experiment (see references/16_experiments_on_demand.md)")
    parts.append("")

    cfg = find_config_values(files, root)
    parts += ["## 4. Setup values found in configuration files (for the Experimental Setup)"]
    parts += [f"- {c}" for c in cfg] or ["- none found"]
    parts.append("")

    py = [s for s in (summarize_python(p, root) for p in files if p.suffix == ".py" and p.stat().st_size < 300000) if s]
    parts += ["## 5. Implementation vocabulary - FOR UNDERSTANDING ONLY",
              "_Translate these into scientific descriptions. Never print identifiers, file names, or function names in the paper._"]
    parts += py[:40] or ["- no Python modules found"]
    parts.append("")

    parts += ["## 6. Citation candidates already present"]
    parts += summarize_bib(files, root)
    parts += [f"- {i}" for i in find_identifiers(files)] or ["- no identifiers found"]
    parts.append("")

    media = describe_media(files, root)
    parts += ["## 7. Media and figures available for the paper / demo site"]
    parts += [f"- {m}" for m in media[:60]] or ["- none"]
    if len(media) > 60:
        parts.append(f"- ... and {len(media) - 60} more")
    parts.append("")

    parts += ["## 8. Evidence gaps spotted automatically",
              "- Treat each 'NO' above (seeds, uncertainty), a missing baseline row, or an empty results section as a candidate experiment.",
              "- Next step: fill paper_story.md and claim_evidence_map.md, then mark gaps 'Needs experiment'."]
    text = "\n".join(parts)
    return text if len(text) <= max_chars else text[:max_chars] + "\n\n_[digest truncated; rerun with a larger --max-chars or point at a sub-folder]_\n"


def digest_file(path: Path, max_chars: int) -> str:
    root = path.parent
    if path.suffix == ".ipynb":
        body = summarize_notebook(path, root)
    elif path.suffix.lower() in TABLE_EXT:
        body = summarize_table(path, root)
    else:
        text = read_head(path, max_chars * 2)
        body = text
    ids = find_identifiers([path])
    out = [f"# Context digest: {path.name}", "", "_Single-file context. Read fully; verify any numbers against a results file before use._", "", body]
    if ids:
        out += ["", "## Citation candidates present", *[f"- {i}" for i in ids]]
    text = "\n".join(out)
    return text if len(text) <= max_chars else text[:max_chars] + "\n\n_[truncated]_\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", type=Path)
    ap.add_argument("-o", "--output", type=Path, help="write digest here (default: print)")
    ap.add_argument("--max-chars", type=int, default=24000, help="size cap, about 4 chars per token")
    args = ap.parse_args()
    if not args.path.exists():
        raise SystemExit(f"error: {args.path} does not exist")
    text = digest_dir(args.path.resolve(), args.max_chars) if args.path.is_dir() else digest_file(args.path.resolve(), args.max_chars)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
        print(f"wrote {args.output} ({len(text)} chars, ~{len(text) // 4} tokens)")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
