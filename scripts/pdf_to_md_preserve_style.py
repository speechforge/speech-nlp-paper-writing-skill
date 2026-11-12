#!/usr/bin/env python3
"""Convert PDFs to provenance-preserving Markdown with span-level typography.

Run this script with the project-local PDF environment:

    .venv_pdf/bin/python scripts/pdf_to_md_preserve_style.py
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import re
from pathlib import Path
import sys
import unicodedata
from typing import Any, Iterable, Sequence

try:
    import pdfplumber
    import pymupdf as fitz
    from pypdf import PdfReader
except ImportError as exc:  # pragma: no cover - exercised by the default env
    raise SystemExit(
        "Missing PDF dependencies. Run with `.venv_pdf/bin/python` or install "
        "pymupdf, pdfplumber, and pypdf."
    ) from exc


ITALIC_FLAG = 2
BOLD_FLAG = 16
SUPERSCRIPT_FLAG = 1
ITALIC_FONT_RE = re.compile(r"(?:italic|oblique|slanted|kursiv|cursiv)", re.I)
BOLD_FONT_RE = re.compile(r"(?:bold|black|heavy|semibold|semi-bold|demi)", re.I)
CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
SLUG_RE = re.compile(r"[^a-z0-9]+")


@dataclass(frozen=True)
class SpanStyle:
    italic: bool
    bold: bool
    superscript: bool


@dataclass
class ExtractedLine:
    block_index: int
    line_index: int
    bbox: tuple[float, float, float, float]
    plain: str
    markdown: str
    raw_span_text: str
    span_count: int
    italic_spans: int
    bold_spans: int
    bold_italic_spans: int
    superscript_spans: int
    replacement_chars: int


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii").lower()
    slug = SLUG_RE.sub("_", ascii_value).strip("_")
    return slug or "unnamed"


def style_for_span(span: dict[str, Any]) -> SpanStyle:
    flags = int(span.get("flags", 0))
    font = str(span.get("font", ""))
    return SpanStyle(
        italic=bool(flags & ITALIC_FLAG) or bool(ITALIC_FONT_RE.search(font)),
        bold=bool(flags & BOLD_FLAG) or bool(BOLD_FONT_RE.search(font)),
        superscript=bool(flags & SUPERSCRIPT_FLAG),
    )


def clean_span_text(value: Any) -> tuple[str, int]:
    text = "" if value is None else str(value)
    replacements = len(CONTROL_RE.findall(text))
    return CONTROL_RE.sub("\ufffd", text), replacements


def should_insert_gap(previous: dict[str, Any], current: dict[str, Any]) -> bool:
    previous_text = str(previous.get("text", ""))
    current_text = str(current.get("text", ""))
    if not previous_text or not current_text:
        return False
    if previous_text[-1].isspace() or current_text[0].isspace():
        return False
    previous_style = style_for_span(previous)
    current_style = style_for_span(current)
    if previous_style.superscript or current_style.superscript:
        return False
    previous_bbox = previous.get("bbox", (0, 0, 0, 0))
    current_bbox = current.get("bbox", (0, 0, 0, 0))
    gap = float(current_bbox[0]) - float(previous_bbox[2])
    font_size = min(float(previous.get("size", 0)), float(current.get("size", 0)))
    return gap > max(0.75, font_size * 0.16)


def wrap_markdown(text: str, style: SpanStyle) -> str:
    if not text:
        return text
    match = re.fullmatch(r"(\s*)(.*?)(\s*)", text, flags=re.S)
    if match is None:
        return text
    leading, core, trailing = match.groups()
    if not core:
        return text
    core = core.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "<br />")
    if style.superscript:
        core = f"<sup>{core}</sup>"
    if style.bold and style.italic:
        core = f"***{core}***"
    elif style.bold:
        core = f"**{core}**"
    elif style.italic:
        core = f"*{core}*"
    return f"{leading}{core}{trailing}"


def merge_styled_runs(
    spans: Sequence[dict[str, Any]],
) -> list[tuple[str, SpanStyle, int]]:
    runs: list[tuple[str, SpanStyle, int]] = []
    previous: dict[str, Any] | None = None
    for span in spans:
        text, replacements = clean_span_text(span.get("text", ""))
        if previous is not None and should_insert_gap(previous, span):
            if runs:
                prior_text, prior_style, prior_replacements = runs[-1]
                runs[-1] = (prior_text + " ", prior_style, prior_replacements)
            else:
                runs.append((" ", SpanStyle(False, False, False), 0))
        style = style_for_span(span)
        if runs and runs[-1][1] == style:
            prior_text, prior_style, prior_replacements = runs[-1]
            runs[-1] = (prior_text + text, prior_style, prior_replacements + replacements)
        else:
            runs.append((text, style, replacements))
        previous = span
    return runs


def extract_lines(page: fitz.Page) -> tuple[list[ExtractedLine], int]:
    page_dict = page.get_text("dict", sort=True)
    lines: list[ExtractedLine] = []
    image_blocks = 0
    page_line_index = 0
    for block_index, block in enumerate(page_dict.get("blocks", []), start=1):
        if int(block.get("type", 0)) != 0:
            if int(block.get("type", 0)) == 1:
                image_blocks += 1
            continue
        for source_line in block.get("lines", []):
            page_line_index += 1
            spans = list(source_line.get("spans", []))
            runs = merge_styled_runs(spans)
            plain = "".join(text for text, _, _ in runs)
            markdown = "".join(wrap_markdown(text, style) for text, style, _ in runs)
            raw_span_text = "".join(clean_span_text(span.get("text", ""))[0] for span in spans)
            styles = [style_for_span(span) for span in spans]
            bbox_values = source_line.get("bbox", (0.0, 0.0, 0.0, 0.0))
            lines.append(
                ExtractedLine(
                    block_index=block_index,
                    line_index=page_line_index,
                    bbox=tuple(float(value) for value in bbox_values),
                    plain=plain,
                    markdown=markdown,
                    raw_span_text=raw_span_text,
                    span_count=len(spans),
                    italic_spans=sum(style.italic for style in styles),
                    bold_spans=sum(style.bold for style in styles),
                    bold_italic_spans=sum(style.bold and style.italic for style in styles),
                    superscript_spans=sum(style.superscript for style in styles),
                    replacement_chars=sum(replacements for _, _, replacements in runs),
                )
            )
    return lines, image_blocks


def table_regions(plumber_page: Any) -> tuple[list[dict[str, Any]], list[str]]:
    tables: list[dict[str, Any]] = []
    warnings: list[str] = []
    try:
        found = plumber_page.find_tables()
    except Exception as exc:  # table inference is best-effort; text extraction still proceeds
        return [], [f"pdfplumber table detection failed: {type(exc).__name__}: {exc}"]
    for table_index, table in enumerate(found, start=1):
        try:
            rows = table.extract() or []
            populated_cells = sum(
                1 for row in rows for cell in (row or []) if cell not in (None, "")
            )
        except Exception as exc:
            rows = []
            populated_cells = 0
            warnings.append(
                f"table {table_index} extraction failed: {type(exc).__name__}: {exc}"
            )
        tables.append(
            {
                "id": table_index,
                "bbox": tuple(float(value) for value in table.bbox),
                "rows": len(rows),
                "columns": max((len(row or []) for row in rows), default=0),
                "populated_cells": populated_cells,
            }
        )
    return tables, warnings


def containing_table_id(
    line_bbox: tuple[float, float, float, float], tables: Sequence[dict[str, Any]]
) -> int | None:
    center_x = (line_bbox[0] + line_bbox[2]) / 2
    center_y = (line_bbox[1] + line_bbox[3]) / 2
    for table in tables:
        x0, top, x1, bottom = table["bbox"]
        if x0 <= center_x <= x1 and top <= center_y <= bottom:
            return int(table["id"])
    return None


def non_whitespace(text: str) -> str:
    return "".join(character for character in text if not character.isspace())


def counter_coverage(reference: str, candidate: str) -> float:
    reference_counter = Counter(non_whitespace(reference))
    if not reference_counter:
        return 1.0 if not non_whitespace(candidate) else 0.0
    candidate_counter = Counter(non_whitespace(candidate))
    overlap = sum((reference_counter & candidate_counter).values())
    return overlap / sum(reference_counter.values())


def json_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def markdown_header(
    source_pdf: str, source_sha256: str, pages: int, author_slug: str, paper_slug: str
) -> list[str]:
    return [
        "---",
        f"SOURCE_PDF: {json_string(source_pdf)}",
        f"SOURCE_SHA256: {source_sha256}",
        f"AUTHOR_SLUG: {author_slug}",
        f"PAPER_SLUG: {paper_slug}",
        f"PAGE_COUNT: {pages}",
        'EXTRACTOR: "PyMuPDF spans + pdfplumber table regions"',
        'PROVENANCE: "<!-- p<page>:l<line>:b<block> -->"',
        'STYLE_ENCODING: "italic=*text*; bold=**text**; bold_italic=***text***; superscript=<sup>text</sup>"',
        "---",
        "",
    ]


def output_path_for(pdf_path: Path, source_dir: Path, output_dir: Path) -> Path:
    relative = pdf_path.resolve().relative_to(source_dir.resolve())
    author_parts = relative.parent.parts or ("unknown_author",)
    author_slug = "__".join(slugify(part) for part in author_parts)
    return output_dir / author_slug / f"{slugify(pdf_path.stem)}.md"


def convert_pdf(
    pdf_path: Path,
    source_dir: Path,
    output_dir: Path,
    detect_tables: bool = True,
) -> dict[str, Any]:
    source_relative = pdf_path.resolve().relative_to(source_dir.resolve())
    output_path = output_path_for(pdf_path, source_dir, output_dir)
    author_slug = output_path.parent.name
    paper_slug = output_path.stem
    source_sha256 = sha256_file(pdf_path)
    warnings: list[str] = []

    document = fitz.open(pdf_path)
    plumber_document = pdfplumber.open(pdf_path)
    try:
        pypdf_pages = len(PdfReader(str(pdf_path), strict=False).pages)
    except Exception as exc:
        pypdf_pages = None
        warnings.append(f"pypdf page validation failed: {type(exc).__name__}: {exc}")

    page_count = len(document)
    markdown = markdown_header(
        source_pdf=source_relative.as_posix(),
        source_sha256=source_sha256,
        pages=page_count,
        author_slug=author_slug,
        paper_slug=paper_slug,
    )
    totals = Counter()
    page_reports: list[dict[str, Any]] = []
    fitz_span_stream_parts: list[str] = []
    emitted_stream_parts: list[str] = []
    pdfplumber_stream_parts: list[str] = []

    try:
        if len(plumber_document.pages) != page_count:
            warnings.append(
                f"page-count mismatch: PyMuPDF={page_count}, pdfplumber={len(plumber_document.pages)}"
            )
        for page_offset, page in enumerate(document):
            page_number = page_offset + 1
            lines, image_blocks = extract_lines(page)
            plumber_page = plumber_document.pages[page_offset]
            tables, table_warnings = table_regions(plumber_page) if detect_tables else ([], [])
            warnings.extend(f"page {page_number}: {warning}" for warning in table_warnings)
            independent_text = "".join(
                str(character.get("text", "")) for character in plumber_page.chars
            )
            raw_span_text = "".join(line.raw_span_text for line in lines)
            emitted_text = "".join(line.plain for line in lines)
            fitz_span_stream_parts.append(raw_span_text)
            emitted_stream_parts.append(emitted_text)
            pdfplumber_stream_parts.append(independent_text)

            if not non_whitespace(raw_span_text):
                warnings.append(f"page {page_number}: no extractable text spans")

            markdown.append(
                f"<!-- PAGE:{page_number} START width={page.rect.width:.2f} height={page.rect.height:.2f} -->"
            )
            active_table: int | None = None
            previous_block: int | None = None
            for line in lines:
                table_id = containing_table_id(line.bbox, tables)
                if table_id != active_table:
                    if active_table is not None:
                        markdown.append(f"<!-- TABLE:p{page_number}:t{active_table} END -->")
                    if table_id is not None:
                        markdown.append(f"<!-- TABLE:p{page_number}:t{table_id} START -->")
                    active_table = table_id
                if previous_block is not None and line.block_index != previous_block:
                    markdown.append("")
                provenance = f"<!-- p{page_number}:l{line.line_index}:b{line.block_index} -->"
                markdown.append(f"{provenance} {line.markdown}")
                previous_block = line.block_index
            if active_table is not None:
                markdown.append(f"<!-- TABLE:p{page_number}:t{active_table} END -->")
            markdown.extend([f"<!-- PAGE:{page_number} END -->", ""])

            page_metrics = {
                "page": page_number,
                "lines": len(lines),
                "spans": sum(line.span_count for line in lines),
                "source_span_chars": len(raw_span_text),
                "emitted_plain_chars": len(emitted_text),
                "span_text_recovery_ratio": counter_coverage(raw_span_text, emitted_text),
                "pdfplumber_reference_chars": len(independent_text),
                "pdfplumber_char_coverage_ratio": counter_coverage(independent_text, emitted_text),
                "italic_spans": sum(line.italic_spans for line in lines),
                "bold_spans": sum(line.bold_spans for line in lines),
                "bold_italic_spans": sum(line.bold_italic_spans for line in lines),
                "superscript_spans": sum(line.superscript_spans for line in lines),
                "replacement_characters": sum(line.replacement_chars for line in lines),
                "image_blocks": image_blocks,
                "tables": tables,
            }
            page_reports.append(page_metrics)
            for key in (
                "lines",
                "spans",
                "source_span_chars",
                "emitted_plain_chars",
                "pdfplumber_reference_chars",
                "italic_spans",
                "bold_spans",
                "bold_italic_spans",
                "superscript_spans",
                "replacement_characters",
                "image_blocks",
            ):
                totals[key] += int(page_metrics[key])
            totals["tables"] += len(tables)
    finally:
        plumber_document.close()
        document.close()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output_path.with_suffix(".md.tmp")
    temporary_path.write_text("\n".join(markdown), encoding="utf-8")
    temporary_path.replace(output_path)

    fitz_span_stream = "".join(fitz_span_stream_parts)
    emitted_stream = "".join(emitted_stream_parts)
    pdfplumber_stream = "".join(pdfplumber_stream_parts)
    page_count_match = pypdf_pages is None or pypdf_pages == page_count
    if not page_count_match:
        warnings.append(f"page-count mismatch: PyMuPDF={page_count}, pypdf={pypdf_pages}")

    return {
        "source_pdf": source_relative.as_posix(),
        "output_markdown": output_path.relative_to(output_dir.parent).as_posix(),
        "source_sha256": source_sha256,
        "output_sha256": sha256_file(output_path),
        "author_slug": author_slug,
        "paper_slug": paper_slug,
        "pages": page_count,
        "pypdf_pages": pypdf_pages,
        "page_count_match": page_count_match,
        **dict(totals),
        "pages_without_extractable_text": sum(
            not page_report["source_span_chars"] for page_report in page_reports
        ),
        "span_text_recovery_ratio": counter_coverage(fitz_span_stream, emitted_stream),
        "pdfplumber_char_coverage_ratio": counter_coverage(
            pdfplumber_stream, emitted_stream
        ),
        "fitz_span_text_sha256": hashlib.sha256(
            fitz_span_stream.encode("utf-8")
        ).hexdigest(),
        "emitted_plain_text_sha256": hashlib.sha256(
            emitted_stream.encode("utf-8")
        ).hexdigest(),
        "warnings": warnings,
        "page_metrics": page_reports,
    }


def discover_pdfs(source_dir: Path, supplied: Iterable[str]) -> list[Path]:
    supplied_paths = list(supplied)
    if supplied_paths:
        pdfs = [Path(path).resolve() for path in supplied_paths]
    else:
        pdfs = sorted(
            (path.resolve() for path in source_dir.rglob("*") if path.is_file() and path.suffix.lower() == ".pdf"),
            key=lambda path: path.as_posix().lower(),
        )
    missing = [path for path in pdfs if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing PDF(s): " + ", ".join(map(str, missing)))
    outside = []
    for path in pdfs:
        try:
            path.relative_to(source_dir.resolve())
        except ValueError:
            outside.append(path)
    if outside:
        raise ValueError("PDF(s) outside source directory: " + ", ".join(map(str, outside)))
    return pdfs


def aggregate_report(
    papers: Sequence[dict[str, Any]], source_dir: Path, output_dir: Path
) -> dict[str, Any]:
    totals = Counter()
    for paper in papers:
        for key in (
            "pages",
            "lines",
            "spans",
            "source_span_chars",
            "emitted_plain_chars",
            "pdfplumber_reference_chars",
            "italic_spans",
            "bold_spans",
            "bold_italic_spans",
            "superscript_spans",
            "replacement_characters",
            "image_blocks",
            "tables",
            "pages_without_extractable_text",
        ):
            totals[key] += int(paper.get(key, 0))
    weighted_source_chars = totals["source_span_chars"]
    weighted_reference_chars = totals["pdfplumber_reference_chars"]
    span_recovery = (
        sum(
            paper["span_text_recovery_ratio"] * paper["source_span_chars"]
            for paper in papers
        )
        / weighted_source_chars
        if weighted_source_chars
        else 1.0
    )
    independent_coverage = (
        sum(
            paper["pdfplumber_char_coverage_ratio"]
            * paper["pdfplumber_reference_chars"]
            for paper in papers
        )
        / weighted_reference_chars
        if weighted_reference_chars
        else 1.0
    )
    return {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "generator": "scripts/pdf_to_md_preserve_style.py",
        "libraries": {
            "pymupdf": getattr(fitz, "VersionBind", "unknown"),
            "pdfplumber": getattr(pdfplumber, "__version__", "unknown"),
        },
        "source_dir": source_dir.as_posix(),
        "output_dir": output_dir.as_posix(),
        "pdf_count": len(papers),
        "totals": {
            **dict(totals),
            "page_count_matches": sum(bool(paper["page_count_match"]) for paper in papers),
            "span_text_recovery_ratio": span_recovery,
            "pdfplumber_char_coverage_ratio": independent_coverage,
            "papers_with_warnings": sum(bool(paper["warnings"]) for paper in papers),
        },
        "papers": list(papers),
        "limitations": [
            "Only text encoded in the PDF text layer is extractable; text embedded solely in raster images requires OCR.",
            "PDF reading order is inferred from coordinates and may differ from intended order in complex multi-column or floating layouts.",
            "pdfplumber table regions are annotated without duplicating table text; table-cell geometry is summarized in this report.",
            "Font flags and font-name heuristics preserve encoded emphasis, but malformed/subset font metadata can obscure typography.",
        ],
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdfs", nargs="*", help="Optional PDFs under --source; default: all recursively")
    parser.add_argument("--source", type=Path, default=Path("Authors"))
    parser.add_argument("--output", type=Path, default=Path("parsed_md"))
    parser.add_argument(
        "--report", type=Path, default=Path("analysis_cache/pdf_extraction_report.json")
    )
    parser.add_argument("--no-table-detection", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    source_dir = args.source.resolve()
    output_dir = args.output.resolve()
    report_path = args.report.resolve()
    if not source_dir.is_dir():
        print(f"Source directory not found: {source_dir}", file=sys.stderr)
        return 2
    try:
        pdfs = discover_pdfs(source_dir, args.pdfs)
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if not pdfs:
        print(f"No PDF files found under {source_dir}", file=sys.stderr)
        return 2

    output_targets = [output_path_for(path, source_dir, output_dir) for path in pdfs]
    duplicates = [path for path, count in Counter(output_targets).items() if count > 1]
    if duplicates:
        print("Output slug collision(s): " + ", ".join(map(str, duplicates)), file=sys.stderr)
        return 2

    papers: list[dict[str, Any]] = []
    for index, pdf_path in enumerate(pdfs, start=1):
        if not args.quiet:
            print(f"[{index}/{len(pdfs)}] {pdf_path.relative_to(source_dir)}", flush=True)
        try:
            papers.append(
                convert_pdf(
                    pdf_path=pdf_path,
                    source_dir=source_dir,
                    output_dir=output_dir,
                    detect_tables=not args.no_table_detection,
                )
            )
        except Exception as exc:
            print(f"Failed to convert {pdf_path}: {type(exc).__name__}: {exc}", file=sys.stderr)
            return 1

    report = aggregate_report(papers, source_dir, output_dir)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if not args.quiet:
        totals = report["totals"]
        print(
            "Converted "
            f"{report['pdf_count']} PDFs / {totals['pages']} pages / {totals['lines']} lines; "
            f"span recovery={totals['span_text_recovery_ratio']:.6f}; "
            f"independent coverage={totals['pdfplumber_char_coverage_ratio']:.6f}"
        )
        print(f"Report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
