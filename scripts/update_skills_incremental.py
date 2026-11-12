#!/usr/bin/env python3
"""Incrementally ingest changed papers and refresh evidence-linked skill deltas.

The manifest is the transaction boundary: hashes are committed only after PDF
conversion, exhaustive line analysis, and skill-evidence updates all succeed.
Use ``--bootstrap`` after a verified full build to register the current corpus
without repeating conversion and analysis.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import unicodedata
from typing import Any, Iterable, Sequence


SCHEMA_VERSION = "1.0"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = PROJECT_ROOT / "Authors"
PARSED_DIR = PROJECT_ROOT / "parsed_md"
ANALYSIS_DIR = PROJECT_ROOT / "analysis_cache"
SKILLS_DIR = PROJECT_ROOT / "skills"
MANIFEST_PATH = PROJECT_ROOT / "manifest.json"
CONVERTER = PROJECT_ROOT / "scripts" / "pdf_to_md_preserve_style.py"
ANALYZER = PROJECT_ROOT / "scripts" / "analyze_papers.py"
PDF_PYTHON = PROJECT_ROOT / ".venv_pdf" / "bin" / "python"

SLUG_RE = re.compile(r"[^a-z0-9]+")
PROVENANCE_RE = re.compile(r"^\s*<!--\s*p\d+:l\d+:b\d+\s*-->\s*")
AUTO_BEGIN = "AUTO_EVIDENCE_BEGIN: TRUE"
AUTO_END = "AUTO_EVIDENCE_END: TRUE"
ROUTER_BEGIN = "AUTO_INVENTORY_BEGIN: TRUE"
ROUTER_END = "AUTO_INVENTORY_END: TRUE"

DOMAIN_KEYWORDS: dict[str, tuple[str, ...]] = {
    "tts_and_vocoders": (
        "text-to-speech", "tts", "vocoder", "voice conversion", "acoustic model",
        "speech synthesis", "flow matching", "waveform generation", "nam2speech",
    ),
    "dataset_and_corpus": (
        "dataset", "corpus", "annotation", "annotator", "data collection",
        "clinical speech", "dysarthric", "deepfake corpus", "speaker corpus",
    ),
    "asr_and_error_correction": (
        "automatic speech recognition", "asr", "word error rate", "wer",
        "error correction", "speech recognition", "quantization", "quantisation",
    ),
    "nlp_and_aac": (
        "natural language processing", "nlp", "augmentative and alternative",
        "aac", "language model", "llm", "nlg", "text generation", "indic",
    ),
    "reasoning_and_evaluation": (
        "reasoning", "benchmark", "leaderboard", "evaluation", "human perception",
        "theoretical", "formulation", "metric", "multidimensional", "analysis",
    ),
}

RHETORIC_PRIORITY = (
    "DOMAIN_URGENCY", "BOTTLENECK_GAP", "SOLUTION_HOOK", "CONTRIBUTION_LEAD",
    "CONTRIBUTION_ITEM", "BASELINE_SUPERIORITY", "QUANTIFIED_GAIN", "TRADEOFF",
    "STATISTICAL_SUPPORT", "ABLATION", "MECHANISM_ATTRIBUTION",
    "LIMITATION_DISCLOSURE", "BOUND_CONCLUSION",
)


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii").lower()
    return SLUG_RE.sub("_", ascii_value).strip("_") or "unnamed"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def discover_pdfs() -> list[Path]:
    return sorted(
        (path for path in SOURCE_DIR.rglob("*") if path.is_file() and path.suffix.lower() == ".pdf"),
        key=lambda path: path.relative_to(SOURCE_DIR).as_posix().lower(),
    )


def relative_key(path: Path) -> str:
    return path.resolve().relative_to(SOURCE_DIR.resolve()).as_posix()


def author_slug(path: Path) -> str:
    relative = path.resolve().relative_to(SOURCE_DIR.resolve())
    parts = relative.parent.parts or ("unknown_author",)
    return "__".join(slugify(part) for part in parts)


def paper_slug(path: Path) -> str:
    return slugify(path.stem)


def markdown_path(path: Path) -> Path:
    return PARSED_DIR / author_slug(path) / f"{paper_slug(path)}.md"


def analysis_path(path: Path) -> Path:
    return ANALYSIS_DIR / author_slug(path) / f"{paper_slug(path)}.jsonl"


def read_manifest() -> dict[str, Any]:
    if not MANIFEST_PATH.exists():
        return {"schema_version": SCHEMA_VERSION, "files": {}}
    payload = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if not isinstance(payload.get("files"), dict):
        raise ValueError("manifest.json must contain an object-valued 'files' field")
    return payload


def run_checked(command: Sequence[str]) -> None:
    print("RUN:", " ".join(command), flush=True)
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def converter_python() -> str:
    return str(PDF_PYTHON if PDF_PYTHON.is_file() else Path(sys.executable))


def convert_changed(paths: Sequence[Path]) -> None:
    if not paths:
        return
    report = ANALYSIS_DIR / "incremental_pdf_extraction_report.json"
    run_checked(
        [converter_python(), str(CONVERTER), *map(str, paths), "--source", str(SOURCE_DIR),
         "--output", str(PARSED_DIR), "--report", str(report)]
    )


def analyze_changed(paths: Sequence[Path]) -> None:
    markdowns = [markdown_path(path) for path in paths]
    missing = [str(path) for path in markdowns if not path.is_file()]
    if missing:
        raise FileNotFoundError("conversion did not create: " + ", ".join(missing))
    if markdowns:
        run_checked(
            [sys.executable, str(ANALYZER), *map(str, markdowns),
             "--input-dir", str(PARSED_DIR), "--output-dir", str(ANALYSIS_DIR)]
        )


def strip_markup(text: str) -> str:
    text = PROVENANCE_RE.sub("", text)
    text = re.sub(r"<!--.*?-->", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def load_analysis_evidence(path: Path) -> dict[str, Any]:
    metadata: dict[str, Any] | None = None
    summary: dict[str, Any] | None = None
    examples: dict[str, dict[str, Any]] = {}
    with path.open(encoding="utf-8") as stream:
        for physical_line in stream:
            record = json.loads(physical_line)
            record_type = record.get("record_type")
            if record_type == "paper_metadata":
                metadata = record
            elif record_type == "paper_summary":
                summary = record.get("summary", {})
            elif record_type == "line" and record.get("section") != "SEC_REF":
                clean = strip_markup(str(record.get("text", "")))
                if not clean or len(clean) > 360:
                    continue
                for label in record.get("rhetorical_functions", []):
                    if label in RHETORIC_PRIORITY and label not in examples:
                        examples[label] = {
                            "line": record.get("line_number"),
                            "section": record.get("section"),
                            "text": clean,
                        }
    if metadata is None or summary is None:
        raise ValueError(f"incomplete analysis JSONL: {path}")
    coverage = summary.get("coverage", {})
    if coverage.get("coverage_ratio") != 1.0 or not coverage.get("byte_exact_reconstruction"):
        raise ValueError(f"analysis coverage contract failed: {path}")
    return {"metadata": metadata, "summary": summary, "examples": examples}


def sidecar_domains(pdf: Path) -> list[str]:
    sidecar = pdf.with_suffix(pdf.suffix + ".domains")
    if not sidecar.is_file():
        return []
    labels: list[str] = []
    for value in re.split(r"[,\n]", sidecar.read_text(encoding="utf-8")):
        if value.strip():
            labels.append(slugify(value))
    return list(dict.fromkeys(labels))


def classify_domains(pdf: Path, markdown: Path) -> list[str]:
    declared = sidecar_domains(pdf)
    if declared:
        return declared
    text = f"{pdf.stem}\n{markdown.read_text(encoding='utf-8', errors='replace')}".lower()
    scores = {
        domain: sum(text.count(keyword) for keyword in keywords)
        for domain, keywords in DOMAIN_KEYWORDS.items()
    }
    ranked = sorted(scores, key=lambda domain: (-scores[domain], domain))
    selected = [domain for domain in ranked if scores[domain] > 0]
    if not selected:
        return ["speech_ai_misc"]
    primary_score = scores[selected[0]]
    return [domain for domain in selected if scores[domain] >= max(2, primary_score * 0.25)][:3]


def yaml_list(values: Iterable[str]) -> str:
    return "[" + ", ".join(values) + "]"


def skill_stub(kind: str, slug: str) -> str:
    fallback = "skills/default_speech_ai.md"
    peer = f"{kind}::{slug.upper()}"
    return (
        f"# SKILL_ID: {peer}\n"
        "META_VERSION: 1.0\n"
        f"DEFAULT_FALLBACK: {fallback}\n"
        f"INTERLOCKS_WITH: [DEFAULT_SPEECH_AI, {peer}]\n"
        "LAYER_POLICY: DELTA_ONLY\n\n"
        "## 1. DELTA_RULES\n"
        "RULE_DELTA_00:\n"
        "  SCOPE: Pending_Evidence_Synthesis\n"
        "  PATTERN: Apply DEFAULT_SPEECH_AI until evidence-supported deltas are ingested.\n"
        "  INTERLOCK: DEFAULT::RULE_SEC_ALL <-> DEFAULT::RULE_AUDIT_ALL\n"
        "  FEEDBACK_TRIGGER: IF evidence is insufficient -> RETAIN default; do not invent style.\n"
    )


def evidence_entry(pdf: Path, evidence: dict[str, Any], domains: Sequence[str]) -> list[str]:
    summary = evidence["summary"]
    mechanics = summary.get("sentence_mechanics", {})
    rhetoric = summary.get("rhetorical_profile", {}).get("functions", {})
    lines = [
        f"PAPER::{paper_slug(pdf)}:",
        f"  SOURCE_PDF: {relative_key(pdf)}",
        f"  SOURCE_MD: parsed_md/{author_slug(pdf)}/{paper_slug(pdf)}.md",
        f"  SOURCE_JSONL: analysis_cache/{author_slug(pdf)}/{paper_slug(pdf)}.jsonl",
        f"  DOMAINS: {yaml_list(domains)}",
        f"  COVERAGE: {summary['coverage']['analyzed_line_record_count']}/{summary['coverage']['source_line_count']}|BYTE_EXACT={str(summary['coverage']['byte_exact_reconstruction']).upper()}",
        f"  VOICE: ACTIVE_OR_OTHER={mechanics.get('active_or_other_ratio', 0)}|PASSIVE={mechanics.get('passive_ratio', 0)}",
        f"  CADENCE: {mechanics.get('cadence', 'UNKNOWN')}|MEAN_WORDS={mechanics.get('sentence_length_words', {}).get('mean', 0)}",
        f"  RHETORIC_COUNTS: {json.dumps(rhetoric, ensure_ascii=False, sort_keys=True, separators=(',', ':'))}",
    ]
    for label in RHETORIC_PRIORITY:
        example = evidence["examples"].get(label)
        if example:
            escaped = str(example["text"]).replace('"', '\\"')
            lines.append(
                f"  EXAMPLE_{label}: \"{escaped}\" @ {example['section']}::L{example['line']}"
            )
    lines.append(
        "  INTERLOCK: SOURCE_MD::LINE <-> SOURCE_JSONL::LINE_RECORD <-> AUTHOR_DELTA <-> DOMAIN_DELTA"
    )
    lines.append(
        "  FEEDBACK_TRIGGER: IF generated claim lacks a bound source/result -> REQUEST evidence; do not fabricate."
    )
    return lines


def parse_auto_entries(text: str) -> dict[str, list[str]]:
    if AUTO_BEGIN not in text or AUTO_END not in text:
        return {}
    block = text.split(AUTO_BEGIN, 1)[1].split(AUTO_END, 1)[0]
    entries: dict[str, list[str]] = {}
    current: str | None = None
    for line in block.splitlines():
        if line.startswith("PAPER::") and line.endswith(":"):
            current = line[len("PAPER::") : -1]
            entries[current] = [line]
        elif current is not None and (line.startswith("  ") or not line.strip()):
            entries[current].append(line)
    return entries


def render_auto_entries(entries: dict[str, list[str]]) -> str:
    lines = ["## 9. INCREMENTAL_EVIDENCE", AUTO_BEGIN]
    for slug in sorted(entries):
        lines.extend(entries[slug])
    lines.extend([AUTO_END, ""])
    return "\n".join(lines)


def upsert_auto_block(path: Path, kind: str, slug: str, entries: dict[str, list[str]]) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else skill_stub(kind, slug)
    current = parse_auto_entries(text)
    current.update(entries)
    block = render_auto_entries(current)
    if AUTO_BEGIN in text and AUTO_END in text:
        start = text.rfind("## 9. INCREMENTAL_EVIDENCE", 0, text.index(AUTO_BEGIN))
        if start < 0:
            start = text.index(AUTO_BEGIN)
        end = text.index(AUTO_END) + len(AUTO_END)
        while end < len(text) and text[end] == "\n":
            end += 1
        text = text[:start].rstrip() + "\n\n" + block
    else:
        text = text.rstrip() + "\n\n" + block
    atomic_write(path, text)


def update_affected_skills(paths: Sequence[Path]) -> dict[str, list[str]]:
    affected_authors: dict[str, dict[str, list[str]]] = {}
    affected_domains: dict[str, dict[str, list[str]]] = {}
    paper_domains: dict[str, list[str]] = {}
    for pdf in paths:
        evidence = load_analysis_evidence(analysis_path(pdf))
        domains = classify_domains(pdf, markdown_path(pdf))
        paper_domains[relative_key(pdf)] = domains
        entry = evidence_entry(pdf, evidence, domains)
        affected_authors.setdefault(author_slug(pdf), {})[paper_slug(pdf)] = entry
        for domain in domains:
            affected_domains.setdefault(domain, {})[paper_slug(pdf)] = entry
    for slug, entries in affected_authors.items():
        upsert_auto_block(SKILLS_DIR / "authors" / f"{slug}.md", "AUTHOR", slug, entries)
    for slug, entries in affected_domains.items():
        upsert_auto_block(SKILLS_DIR / "domains" / f"{slug}.md", "DOMAIN", slug, entries)
    return paper_domains


def refresh_router_inventory() -> None:
    router = SKILLS_DIR / "SKILL_ROUTER.md"
    if router.exists():
        text = router.read_text(encoding="utf-8")
    else:
        text = (
            "# SKILL_ID: ROUTER::SPEECH_AI\nMETA_VERSION: 1.0\n"
            "LOAD_ORDER: [SKILL_ROUTER, default_speech_ai, AUTHOR::<target>, DOMAIN::<primary>, DOMAIN::<secondary>]\n"
            "UPDATE: python3 scripts/update_skills_incremental.py\n"
        )
    authors = sorted(path.stem for path in (SKILLS_DIR / "authors").glob("*.md"))
    domains = sorted(path.stem for path in (SKILLS_DIR / "domains").glob("*.md"))
    block = "\n".join(
        [ROUTER_BEGIN, f"AUTHORS: {yaml_list(authors)}", f"DOMAINS: {yaml_list(domains)}", ROUTER_END]
    )
    if ROUTER_BEGIN in text and ROUTER_END in text:
        start = text.index(ROUTER_BEGIN)
        end = text.index(ROUTER_END) + len(ROUTER_END)
        text = text[:start] + block + text[end:]
    else:
        text = text.rstrip() + "\n" + block + "\n"
    atomic_write(router, text)


def validate_existing_outputs(paths: Sequence[Path]) -> None:
    missing = [
        str(output)
        for pdf in paths
        for output in (markdown_path(pdf), analysis_path(pdf))
        if not output.is_file()
    ]
    if missing:
        raise FileNotFoundError("cannot bootstrap; missing outputs: " + ", ".join(missing))
    for pdf in paths:
        load_analysis_evidence(analysis_path(pdf))


def build_manifest(
    pdfs: Sequence[Path], prior: dict[str, Any], domains_by_paper: dict[str, list[str]], has_changes: bool = True
) -> dict[str, Any]:
    prior_files = prior.get("files", {})
    files: dict[str, Any] = {}
    for pdf in pdfs:
        key = relative_key(pdf)
        prior_entry = prior_files.get(key, {})
        files[key] = {
            "sha256": sha256_file(pdf),
            "author_slug": author_slug(pdf),
            "paper_slug": paper_slug(pdf),
            "parsed_md": markdown_path(pdf).relative_to(PROJECT_ROOT).as_posix(),
            "analysis_jsonl": analysis_path(pdf).relative_to(PROJECT_ROOT).as_posix(),
            "domains": domains_by_paper.get(
                key,
                prior_entry.get("domains") or classify_domains(pdf, markdown_path(pdf)),
            ),
        }
    timestamp = (
        prior.get("generated_at_utc")
        if (not has_changes and prior.get("generated_at_utc"))
        else datetime.now(timezone.utc).isoformat()
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at_utc": timestamp,
        "source_dir": SOURCE_DIR.relative_to(PROJECT_ROOT).as_posix(),
        "pdf_count": len(pdfs),
        "files": files,
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--bootstrap", action="store_true",
        help="Validate/register the already-built corpus without reconverting it.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Report changes without writing.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    pdfs = discover_pdfs()
    if not pdfs:
        print(f"No PDFs found under {SOURCE_DIR}", file=sys.stderr)
        return 2
    prior = read_manifest()
    prior_files = prior.get("files", {})
    current_hashes = {relative_key(path): sha256_file(path) for path in pdfs}
    changed = [path for path in pdfs if prior_files.get(relative_key(path), {}).get("sha256") != current_hashes[relative_key(path)]]
    removed = sorted(set(prior_files) - set(current_hashes))
    print(f"PDFS={len(pdfs)} CHANGED={len(changed)} REMOVED={len(removed)}")
    for path in changed:
        print(f"CHANGED: {relative_key(path)}")
    for key in removed:
        print(f"REMOVED_FROM_SOURCE: {key} (derived artifacts retained)")
    if args.dry_run:
        return 0

    domains_by_paper: dict[str, list[str]] = {}
    if args.bootstrap:
        validate_existing_outputs(pdfs)
        domains_by_paper = update_affected_skills(pdfs)
    elif changed:
        convert_changed(changed)
        analyze_changed(changed)
        domains_by_paper = update_affected_skills(changed)

    refresh_router_inventory()
    manifest = build_manifest(pdfs, prior, domains_by_paper, has_changes=bool(changed or args.bootstrap))
    atomic_write(MANIFEST_PATH, json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(f"MANIFEST: {MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
