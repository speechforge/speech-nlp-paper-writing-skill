#!/usr/bin/env python3
"""Exhaustive, deterministic rhetorical analysis for converted paper Markdown.

The analyzer emits one JSON object for every physical source line, including blank
lines, followed by a document summary. It deliberately uses only the Python
standard library so it can run in the incremental ingestion pipeline without a
model download or an external NLP service.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence


SCHEMA_VERSION = "1.1"
ANALYZER_VERSION = "1.1.0"

WORD_RE = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*|\d+(?:\.\d+)?")
MARKDOWN_HEADING_RE = re.compile(r"^\s*(#{1,6})\s+(.+?)\s*#*\s*$")
LIST_ITEM_RE = re.compile(r"^\s*(?:[-+*]|\d+[.)]|[A-Za-z][.)])\s+")
TABLE_ROW_RE = re.compile(r"^\s*\|.*\|\s*$")
CAPTION_RE = re.compile(
    r"^\s*(?:\*{0,2})?(fig(?:ure)?|table|algorithm|equation|eq\.?|scheme)\s*[.:]?\s*\d+",
    re.IGNORECASE,
)
PAGE_MARKER_RE = re.compile(r"^\s*(?:<!--\s*)?(?:page|pdf_page)\s*[:=#-]?\s*\d+", re.I)
PROVENANCE_PREFIX_RE = re.compile(
    r"^(?P<leading>\s*)<!--\s*"
    r"p(?P<page>\d+):l(?P<pdf_line>\d+):b(?P<block>\d+)\s*-->"
    r"(?P<separator>[ \t]*)(?P<content>.*)$",
    re.I,
)
MARKER_COMMENT_RE = re.compile(r"^\s*<!--\s*(?P<marker>.*?)\s*-->\s*$")
TABLE_MARKER_RE = re.compile(r"^TABLE:p\d+:t\d+\s+(?:START|END)$", re.I)
FOOTNOTE_RE = re.compile(r"^\s*(?:\[\^[^]]+\]:|\^\d+\s+|[*†‡§¶]\s+)")
FRONT_MATTER_FIELD_RE = re.compile(r"^[A-Z][A-Z0-9_]*:\s*")
ITALIC_ASTERISK_RE = re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)")
ITALIC_BOLD_RE = re.compile(r"(?<!\*)\*\*\*(.+?)\*\*\*(?!\*)|(?<!_)___(.+?)___(?!_)")
ITALIC_UNDERSCORE_RE = re.compile(r"(?<!\w)_(?!_)(.+?)(?<!_)_(?!\w)")
BOLD_RE = re.compile(r"(?<!\*)\*\*(?!\*)(.+?)(?<!\*)\*\*(?!\*)|(?<!_)__(?!_)(.+?)(?<!_)__(?!_)")
INLINE_MATH_PATTERNS = (
    re.compile(r"(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)"),
    re.compile(r"\\\((.+?)\\\)"),
)
DISPLAY_MATH_RE = re.compile(r"\$\$|\\\[|\\begin\{(?:equation|align|gather|multline)\*?\}")
ACRONYM_RE = re.compile(r"\b[A-Z][A-Z0-9-]{1,11}s?\b")
EXPANDED_ACRONYM_RE = re.compile(
    r"\b((?:[A-Z]?[a-z][A-Za-z-]*|[A-Z][a-zA-Z-]*)(?:\s+(?:of|for|and|the|to|in|with|[A-Z]?[a-z][A-Za-z-]*|[A-Z][a-zA-Z-]*)){1,11})\s*"
    r"\(([A-Z][A-Z0-9-]{1,11}s?)\)"
)
NUMBER_RE = re.compile(r"(?<!\w)[+−-]?\d+(?:\.\d+)?(?:\s?%|\s?[×x])?")

KNOWN_SHORT_FORMS = {
    "AI",
    "ASR",
    "AUC",
    "CNN",
    "CPU",
    "CTC",
    "DNN",
    "F0",
    "GAN",
    "GPU",
    "LLM",
    "LSTM",
    "MCD",
    "MOS",
    "NLP",
    "PESQ",
    "RNN",
    "RTF",
    "SNR",
    "STFT",
    "TTS",
    "WER",
}

SECTION_ALIASES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("SEC_ABS", ("abstract", "summary")),
    ("SEC_INT", ("introduction", "motivation")),
    (
        "SEC_REL",
        (
            "related work",
            "prior work",
            "previous work",
            "literature review",
            "background",
            "preliminaries",
        ),
    ),
    (
        "SEC_PROP",
        (
            "proposed method",
            "proposed framework",
            "proposed approach",
            "methodology",
            "methods",
            "method",
            "model architecture",
            "mathematical formulation",
            "system overview",
        ),
    ),
    (
        "SEC_EXP",
        (
            "experimental setup",
            "experiment setup",
            "experiments",
            "dataset",
            "datasets",
            "corpus",
            "implementation details",
            "evaluation metrics",
            "metrics",
            "baselines",
        ),
    ),
    (
        "SEC_RES",
        (
            "results and discussion",
            "results & discussion",
            "experimental results",
            "results",
            "evaluation",
            "analysis",
            "ablation study",
            "ablation studies",
            "discussion",
        ),
    ),
    (
        "SEC_CON",
        (
            "limitations and conclusion",
            "conclusion and future work",
            "conclusions and future work",
            "conclusion",
            "conclusions",
            "limitations",
            "future work",
            "broader impact",
        ),
    ),
    ("SEC_REF", ("references", "bibliography")),
    ("SEC_APP", ("appendix", "appendices", "supplementary material", "supplement")),
    ("SEC_ACK", ("acknowledgment", "acknowledgments", "acknowledgement", "acknowledgements")),
)

TRANSITION_GROUPS: dict[str, tuple[str, ...]] = {
    "contrast": (
        "however",
        "nevertheless",
        "nonetheless",
        "in contrast",
        "conversely",
        "on the other hand",
        "whereas",
        "while",
        "despite",
        "although",
        "yet",
    ),
    "addition": (
        "furthermore",
        "moreover",
        "additionally",
        "in addition",
        "also",
        "similarly",
        "notably",
    ),
    "cause": ("because", "since", "owing to", "due to", "given that"),
    "result": ("therefore", "thus", "hence", "consequently", "as a result", "accordingly"),
    "exemplification": ("for example", "for instance", "specifically", "in particular", "namely"),
    "sequence": ("first", "second", "third", "finally", "subsequently", "then", "next"),
    "reformulation": ("in other words", "that is", "i.e.", "to this end"),
    "limitation": ("a limitation", "one limitation", "we acknowledge", "remains challenging", "future work"),
}

SUBORDINATORS = (
    "although",
    "because",
    "before",
    "despite",
    "even if",
    "even though",
    "given that",
    "if",
    "once",
    "provided that",
    "since",
    "so that",
    "though",
    "unless",
    "until",
    "when",
    "whereas",
    "whether",
    "while",
    "which",
    "who",
    "whose",
    "that",
)

PASSIVE_RE = re.compile(
    r"\b(?:am|are|is|was|were|be|been|being|become|becomes|became|remain|remains|remained)\b"
    r"(?:\s+\w+){0,3}\s+"
    r"(?:\w+(?:ed|en)|built|done|found|given|known|made|shown|seen|set|taken|used)\b",
    re.IGNORECASE,
)
AGENTIVE_RE = re.compile(r"\bby\s+(?:the|a|an|our|this|these|that|those)\b", re.I)
ACTIVE_CUE_RE = re.compile(
    r"\b(?:we|our (?:method|model|framework|system|approach|results?|experiments?))\s+"
    r"(?:propose|present|introduce|develop|design|evaluate|compare|show|demonstrate|find|observe|achieve|outperform|use|employ|conduct|analyze|investigate)s?\b",
    re.I,
)
NOMINALIZATION_RE = re.compile(
    r"\b[A-Za-z]{4,}(?:tion|sion|ment|ness|ance|ence|ity|ization|isation|al)\b",
    re.I,
)

LATINISMS: tuple[tuple[str, str], ...] = (
    ("et al.", r"\bet\s+al\."),
    ("i.e.", r"\bi\.e\."),
    ("e.g.", r"\be\.g\."),
    ("bona fide", r"\bbona\s+fide\b"),
    ("a priori", r"\ba\s+priori\b"),
    ("a posteriori", r"\ba\s+posteriori\b"),
    ("in situ", r"\bin\s+situ\b"),
    ("vis-à-vis", r"\bvis[-‐‑‒–—]à[-‐‑‒–—]vis\b"),
    ("ad hoc", r"\bad\s+hoc\b"),
    ("per se", r"\bper\s+se\b"),
    ("de facto", r"\bde\s+facto\b"),
    ("vice versa", r"\bvice\s+versa\b"),
)

RHETORICAL_PATTERNS: dict[str, tuple[str, ...]] = {
    "DOMAIN_URGENCY": (
        r"\b(?:critical|crucial|essential|important|growing need|increasing demand|urgent|challenging)\b",
        r"\b(?:plays?|has) (?:an? )?(?:important|critical|key|central) (?:role|impact)\b",
    ),
    "PRIOR_WORK": (
        r"\b(?:prior|previous|existing|recent) (?:work|studies|approaches|methods|systems)\b",
        r"\bstate[- ]of[- ]the[- ]art\b",
    ),
    "BOTTLENECK_GAP": (
        r"\bhowever\b.*\b(?:lack|fail|limited|overlook|remain|challenge|degrad|cannot|unable)\w*\b",
        r"\bdespite (?:these|such|recent) (?:advances|efforts|developments|improvements)\b",
        r"\b(?:existing|prior|current) (?:approaches|methods|systems|work)\b.*\b(?:fail|lack|limit|overlook|neglect|struggle|cannot)\w*\b",
        r"\b(?:little|limited|no) (?:attention|work|research|evidence)\b",
        r"\b(?:remains?|poses?) (?:an? )?(?:open|major|key|significant|fundamental) (?:challenge|problem|question)\b",
    ),
    "SOLUTION_HOOK": (
        r"\b(?:to (?:address|bridge|overcome|mitigate|tackle) (?:this|the) (?:gap|challenge|limitation|problem)|to this end)\b",
        r"\bwe (?:propose|present|introduce|develop|design)\b",
        r"\bthis (?:paper|work|study) (?:proposes|presents|introduces|develops)\b",
    ),
    "MECHANISM_HOW": (
        r"\b(?:by|through|via) (?:integrating|combining|leveraging|using|employing|modeling|incorporating)\b",
        r"\bconsists? of\b|\bcomprises?\b|\bis composed of\b",
    ),
    "CONTRIBUTION_LEAD": (
        r"\b(?:main|primary|key) contributions? (?:of this (?:work|paper)|are)\b",
        r"\bcontributions? (?:are|can be) summarized as follows\b",
        r"\bwe make the following contributions?\b",
    ),
    "CONTRIBUTION_ITEM": (
        r"^\s*(?:[-+*]|\d+[.)]|[ivx]+[.)])\s+.*\b(?:propose|introduce|develop|design|demonstrate|show|establish|release|construct|provide)\b",
    ),
    "BASELINE_SUPERIORITY": (
        r"\b(?:outperform|surpass|exceed)s?\b",
        r"\b(?:better|superior|higher|lower)\b.*\b(?:than|compared (?:with|to))\b",
        r"\bstate[- ]of[- ]the[- ]art (?:performance|results?)\b",
    ),
    "QUANTIFIED_GAIN": (
        r"\b(?:relative|absolute) (?:improvement|reduction|gain|increase|decrease)\b",
        r"\b(?:improv|reduc|increas|decreas)\w*\b.*(?:%|percent|points?|×|x)\b",
        r"\bby\s+[+−-]?\d+(?:\.\d+)?\s*(?:%|points?|×|x)\b",
    ),
    "TRADEOFF": (
        r"\b(?:although|while|despite)\b.*\b(?:fewer|lower|higher|marginal|cost|latency|parameters?|memory|quality|accuracy|error)\b",
        r"\btrade[- ]off\b",
        r"\bat the (?:cost|expense) of\b",
    ),
    "STATISTICAL_SUPPORT": (
        r"\b(?:statistically significant|significance|confidence interval|standard deviation|standard error|p\s*[<=>])\b",
        r"\b(?:95%|99%)\s*(?:CI|confidence interval)\b",
    ),
    "ABLATION": (
        r"\bablation\b",
        r"\b(?:removing|without|w/o|variant|component analysis)\b.*\b(?:module|component|loss|mechanism|block|layer)\b",
    ),
    "MECHANISM_ATTRIBUTION": (
        r"\b(?:attributed to|due to|owing to|because of|stems? from|results? from)\b.*\b(?:proposed|our|module|component|mechanism|architecture|loss)\b",
    ),
    "QUALITATIVE_EVIDENCE": (
        r"\b(?:qualitative|visualization|spectrogram|attention map|case study|listening test|subjective evaluation)\b",
    ),
    "LIMITATION_DISCLOSURE": (
        r"\b(?:limitation|limited to|we acknowledge|does not|cannot|future work|remains challenging)\b",
    ),
    "BOUND_CONCLUSION": (
        r"\b(?:these results|our findings|the results) (?:suggest|indicate|demonstrate|show)\b",
        r"\bunder (?:the|our|these) (?:evaluated|experimental|considered) (?:conditions|settings|datasets)\b",
    ),
}

SECTION_MOVE_HINTS: dict[str, dict[str, tuple[str, ...]]] = {
    "SEC_ABS": {
        "L1_DOMAIN_ANCHOR": ("DOMAIN_URGENCY", "PRIOR_WORK"),
        "L2_BOTTLENECK_GAP": ("BOTTLENECK_GAP",),
        "L3_PROPOSED_PARADIGM": ("SOLUTION_HOOK",),
        "L4_METRIC_CLAIM": ("BASELINE_SUPERIORITY", "QUANTIFIED_GAIN", "STATISTICAL_SUPPORT"),
        "L5_IMPLICATION": ("BOUND_CONCLUSION",),
    },
    "SEC_INT": {
        "L1_DOMAIN_ANCHOR": ("DOMAIN_URGENCY", "PRIOR_WORK"),
        "L2_BOTTLENECK_GAP": ("BOTTLENECK_GAP",),
        "L3_PROPOSED_PARADIGM": ("SOLUTION_HOOK",),
        "L4_MECHANISM_HOW": ("MECHANISM_HOW",),
        "L5_CONTRIBUTION_LOCK": ("CONTRIBUTION_LEAD", "CONTRIBUTION_ITEM"),
    },
    "SEC_REL": {
        "P1_PRIOR_CAPABILITY": ("PRIOR_WORK",),
        "P2_LIMITATION_CONTRAST": ("BOTTLENECK_GAP",),
        "P3_POSITIONING": ("SOLUTION_HOOK",),
    },
    "SEC_PROP": {
        "P1_MOTIVATION": ("BOTTLENECK_GAP",),
        "P2_ARCHITECTURE": ("SOLUTION_HOOK", "MECHANISM_HOW"),
        "P3_COMPONENT_RATIONALE": ("MECHANISM_ATTRIBUTION",),
    },
    "SEC_EXP": {
        "P1_DATA_PROTOCOL": ("QUALITATIVE_EVIDENCE",),
        "P2_BASELINE_PROTOCOL": ("PRIOR_WORK",),
        "P3_METRIC_PROTOCOL": ("STATISTICAL_SUPPORT",),
    },
    "SEC_RES": {
        "P1_MAIN_COMPARISON": ("BASELINE_SUPERIORITY", "QUANTIFIED_GAIN"),
        "P2_TRADEOFF_ANALYSIS": ("TRADEOFF",),
        "P3_ABLATION": ("ABLATION", "MECHANISM_ATTRIBUTION"),
        "P4_QUALITATIVE": ("QUALITATIVE_EVIDENCE",),
    },
    "SEC_CON": {
        "P1_FINDING_RECAP": ("BOUND_CONCLUSION", "BASELINE_SUPERIORITY"),
        "P2_LIMITATION": ("LIMITATION_DISCLOSURE",),
        "P3_FUTURE_SCOPE": ("LIMITATION_DISCLOSURE",),
    },
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def markdown_plain_text(text: str) -> str:
    """Remove structural Markdown without changing the source record itself."""
    text = re.sub(r"<!--.*?-->", " ", text)
    text = re.sub(r"!\[([^]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[*_`~#>|]", "", text)
    return normalize_space(text)


def percentile(values: Sequence[int], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return float(ordered[lower])
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def sentence_length_band(word_count: int) -> str:
    if word_count == 0:
        return "EMPTY"
    if word_count <= 10:
        return "SHORT"
    if word_count <= 24:
        return "MEDIUM"
    if word_count <= 39:
        return "LONG"
    return "VERY_LONG"


def split_sentences(text: str) -> list[tuple[str, int, int]]:
    """Return conservative sentence spans while avoiding common abbreviations."""
    if not text.strip():
        return []
    abbreviation_re = re.compile(
        r"(?:\b(?:e\.g|i\.e|et al|Fig|Eq|Sec|Dr|Prof|Mr|Ms|vs|cf|al)\.|\b[A-Z]\.)$",
        re.I,
    )
    spans: list[tuple[str, int, int]] = []
    start = 0
    for match in re.finditer(r"[.!?][\]\)}'\"”’]*\s+", text):
        candidate = text[start : match.end()].rstrip()
        if abbreviation_re.search(candidate):
            continue
        next_index = match.end()
        while next_index < len(text) and text[next_index].isspace():
            next_index += 1
        if next_index >= len(text):
            break
        next_char = text[next_index]
        if not (next_char.isupper() or next_char.isdigit() or next_char in "*_$`[(\\"):
            continue
        sentence_end = match.end() - len(match.group(0)) + len(match.group(0).rstrip())
        sentence = text[start:sentence_end].strip()
        if sentence:
            actual_start = start + len(text[start:sentence_end]) - len(text[start:sentence_end].lstrip())
            spans.append((sentence, actual_start, sentence_end))
        start = match.end()
    tail = text[start:].strip()
    if tail:
        actual_start = start + len(text[start:]) - len(text[start:].lstrip())
        spans.append((tail, actual_start, len(text.rstrip())))
    return spans


def canonical_section(heading: str) -> str | None:
    normalized = normalize_space(re.sub(r"^[\dIVXivx.()\s-]+", "", markdown_plain_text(heading))).lower()
    normalized = normalized.rstrip(".:—–-")
    for section_id, aliases in SECTION_ALIASES:
        if any(normalized == alias or normalized.startswith(alias + ":") for alias in aliases):
            return section_id
    return None


def detect_heading(text: str) -> tuple[int, str] | None:
    match = MARKDOWN_HEADING_RE.match(text)
    if match:
        return len(match.group(1)), normalize_space(match.group(2))
    plain = markdown_plain_text(text)
    if not plain or len(WORD_RE.findall(plain)) > 12:
        return None
    if canonical_section(plain):
        return 2, plain
    return None


def classify_line_kind(text: str, section: str) -> str:
    if text == "":
        return "blank"
    if not text.strip():
        return "whitespace_only"
    if PAGE_MARKER_RE.match(text):
        return "page_marker"
    if detect_heading(text):
        return "heading"
    if text.strip().startswith("```") or text.strip().startswith("~~~"):
        return "code_fence"
    if TABLE_ROW_RE.match(text):
        return "table_row"
    if DISPLAY_MATH_RE.search(text) or (text.strip().startswith("$") and text.strip().endswith("$")):
        return "equation"
    if CAPTION_RE.match(text):
        return "caption"
    if LIST_ITEM_RE.match(text):
        return "list_item"
    if section == "SEC_REF":
        return "reference_entry"
    if text.lstrip().startswith("<!--"):
        return "html_comment"
    return "prose"


def extract_italic_spans(text: str) -> list[dict[str, Any]]:
    spans: list[dict[str, Any]] = []
    for match in ITALIC_BOLD_RE.finditer(text):
        spans.append(
            {
                "text": match.group(1) or match.group(2),
                "syntax": "bold_italic",
                "start": match.start(),
                "end": match.end(),
            }
        )
    for syntax, pattern in (("asterisk", ITALIC_ASTERISK_RE), ("underscore", ITALIC_UNDERSCORE_RE)):
        for match in pattern.finditer(text):
            spans.append(
                {
                    "text": match.group(1),
                    "syntax": syntax,
                    "start": match.start(),
                    "end": match.end(),
                }
            )
    return sorted(spans, key=lambda item: (item["start"], item["end"]))


def extract_bold_spans(text: str) -> list[dict[str, Any]]:
    spans = [
        {"text": match.group(1) or match.group(2), "start": match.start(), "end": match.end()}
        for match in BOLD_RE.finditer(text)
    ]
    spans.extend(
        {"text": match.group(1) or match.group(2), "start": match.start(), "end": match.end()}
        for match in ITALIC_BOLD_RE.finditer(text)
    )
    return sorted(spans, key=lambda item: (item["start"], item["end"]))


def extract_math_spans(text: str) -> list[dict[str, Any]]:
    spans: list[dict[str, Any]] = []
    for pattern in INLINE_MATH_PATTERNS:
        for match in pattern.finditer(text):
            spans.append({"text": match.group(1), "start": match.start(), "end": match.end(), "display": False})
    if DISPLAY_MATH_RE.search(text):
        spans.append({"text": text.strip(), "start": 0, "end": len(text), "display": True})
    return sorted(spans, key=lambda item: (item["start"], item["end"]))


def latinism_statuses(text: str, italic_spans: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    italic_ranges = [(int(span["start"]), int(span["end"])) for span in italic_spans]
    statuses: list[dict[str, Any]] = []
    for label, expression in LATINISMS:
        for match in re.finditer(expression, text, re.I):
            italicized = any(start <= match.start() and match.end() <= end for start, end in italic_ranges)
            statuses.append(
                {
                    "term": label,
                    "surface": match.group(0),
                    "italicized": italicized,
                    "start": match.start(),
                    "end": match.end(),
                }
            )
    return sorted(statuses, key=lambda item: item["start"])


def transition_hits(text: str) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    lowered = text.lower()
    for category, phrases in TRANSITION_GROUPS.items():
        for phrase in phrases:
            match = re.search(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", lowered)
            if match:
                hits.append(
                    {
                        "category": category,
                        "phrase": text[match.start() : match.end()],
                        "position": "initial" if not text[: match.start()].strip(" *#-–—,;:()") else "medial",
                    }
                )
    return hits


def rhetorical_hits(text: str) -> list[str]:
    hits: list[str] = []
    for label, expressions in RHETORICAL_PATTERNS.items():
        if any(re.search(expression, text, re.I) for expression in expressions):
            hits.append(label)
    return hits


def section_moves(section: str, rhetoric: Sequence[str]) -> list[str]:
    rhetoric_set = set(rhetoric)
    moves: list[str] = []
    for move, evidence_labels in SECTION_MOVE_HINTS.get(section, {}).items():
        if rhetoric_set.intersection(evidence_labels):
            moves.append(move)
    return moves


def punctuation_profile(text: str) -> dict[str, int]:
    return {
        "comma": text.count(","),
        "semicolon": text.count(";"),
        "colon": text.count(":"),
        "parenthesis_pair": min(text.count("("), text.count(")")),
        "square_bracket_pair": min(text.count("["), text.count("]")),
        "hyphen": text.count("-"),
        "en_dash": text.count("–"),
        "em_dash": text.count("—"),
        "question_mark": text.count("?"),
        "exclamation_mark": text.count("!"),
    }


def analyze_sentence(sentence: str, start: int, end: int, ordinal: int) -> dict[str, Any]:
    plain = markdown_plain_text(sentence)
    words = WORD_RE.findall(plain)
    passive_hits = [match.group(0) for match in PASSIVE_RE.finditer(plain)]
    agentive_hits = [match.group(0) for match in AGENTIVE_RE.finditer(plain)]
    active_hits = [match.group(0) for match in ACTIVE_CUE_RE.finditer(plain)]
    if passive_hits:
        voice = "passive"
    elif active_hits:
        voice = "active_explicit"
    elif words:
        voice = "active_or_other"
    else:
        voice = "not_applicable"
    subordination = [
        phrase
        for phrase in SUBORDINATORS
        if re.search(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", plain, re.I)
    ]
    nominalizations = [match.group(0) for match in NOMINALIZATION_RE.finditer(plain)]
    clauses = 1 + plain.count(",") + plain.count(";") + len(subordination)
    return {
        "ordinal": ordinal,
        "text": sentence,
        "start": start,
        "end": end,
        "word_count": len(words),
        "length_band": sentence_length_band(len(words)),
        "voice": voice,
        "passive_indicators": passive_hits,
        "agentive_by_phrases": agentive_hits,
        "active_indicators": active_hits,
        "subordinators": subordination,
        "subordination_count": len(subordination),
        "estimated_clause_count": clauses,
        "nominalizations": nominalizations,
        "nominalization_count": len(nominalizations),
        "punctuation": punctuation_profile(sentence),
        "transitions": transition_hits(plain),
    }


def extract_acronyms(text: str, seen: set[str]) -> list[dict[str, Any]]:
    expansions: dict[str, str] = {}
    for match in EXPANDED_ACRONYM_RE.finditer(text):
        expansions[match.group(2).rstrip("s")] = normalize_space(match.group(1))
    acronyms: list[dict[str, Any]] = []
    for match in ACRONYM_RE.finditer(text):
        surface = match.group(0)
        normalized = surface.rstrip("s")
        first_use = normalized not in seen
        expansion = expansions.get(normalized)
        if first_use and expansion:
            status = "expanded_on_first_use"
        elif first_use and normalized in KNOWN_SHORT_FORMS:
            status = "unexpanded_first_use_common"
        elif first_use:
            status = "unexpanded_first_use"
        else:
            status = "reuse"
        acronyms.append(
            {
                "surface": surface,
                "normalized": normalized,
                "first_use": first_use,
                "expansion": expansion,
                "status": status,
                "start": match.start(),
                "end": match.end(),
            }
        )
        seen.add(normalized)
    return acronyms


def extract_variables(italic_spans: Sequence[dict[str, Any]], math_spans: Sequence[dict[str, Any]]) -> list[str]:
    variables: set[str] = set()
    for span in italic_spans:
        candidate = normalize_space(str(span["text"]))
        if re.fullmatch(r"[A-Za-z](?:[_^][A-Za-z0-9{}]+)?|[A-Za-z]_[0-9]+", candidate):
            variables.add(candidate)
    for span in math_spans:
        value = str(span["text"])
        variables.update(re.findall(r"(?<![A-Za-z\\])(?:\\?[A-Za-z]|[A-Za-z])(?:_[{]?[A-Za-z0-9]+[}]?)?", value))
    return sorted(variables)


def comparison_features(text: str) -> dict[str, Any]:
    comparative_terms = re.findall(
        r"\b(?:outperform\w*|surpass\w*|exceed\w*|better|best|superior|higher|lower|faster|slower|fewer|more|less|state[- ]of[- ]the[- ]art)\b",
        text,
        re.I,
    )
    metric_terms = re.findall(
        r"\b(?:WER|CER|MOS|MCD|PESQ|STOI|UTMOS|SNR|accuracy|precision|recall|F1|latency|throughput|parameters?|real[- ]time factor|RTF)\b",
        text,
        re.I,
    )
    return {
        "comparative_terms": comparative_terms,
        "metric_terms": metric_terms,
        "numbers": NUMBER_RE.findall(text),
        "has_baseline_anchor": bool(re.search(r"\b(?:baseline|compared (?:with|to)|than|versus|vs\.)\b", text, re.I)),
        "has_mechanism_attribution": bool(
            re.search(r"\b(?:attributed to|due to|owing to|because of|stems? from|results? from)\b", text, re.I)
        ),
    }


def detect_heading_section(heading_text: str, current_section: str) -> str:
    mapped = canonical_section(heading_text)
    if mapped:
        return mapped
    if current_section == "SEC_TITLE":
        return "SEC_META"
    return current_section


class PaperAccumulator:
    def __init__(self) -> None:
        self.line_kinds: Counter[str] = Counter()
        self.sections: Counter[str] = Counter()
        self.section_content_lines: Counter[str] = Counter()
        self.rhetoric: Counter[str] = Counter()
        self.moves: Counter[str] = Counter()
        self.transitions: Counter[str] = Counter()
        self.voice: Counter[str] = Counter()
        self.voice_by_section: dict[str, Counter[str]] = defaultdict(Counter)
        self.punctuation: Counter[str] = Counter()
        self.italic_terms: Counter[str] = Counter()
        self.bold_terms: Counter[str] = Counter()
        self.latinism_styles: Counter[str] = Counter()
        self.acronym_statuses: Counter[str] = Counter()
        self.acronym_first_use_issues: list[dict[str, Any]] = []
        self.variables: Counter[str] = Counter()
        self.nominalizations: Counter[str] = Counter()
        self.sentence_lengths: list[int] = []
        self.subordination_counts: list[int] = []
        self.word_count = 0
        self.content_char_count = 0
        self.blank_line_count = 0
        self.nonblank_line_count = 0

    def add(self, record: dict[str, Any]) -> None:
        line_kind = record["line_kind"]
        section = record["section"]
        self.line_kinds[line_kind] += 1
        self.sections[section] += 1
        if line_kind in {"blank", "whitespace_only"}:
            self.blank_line_count += 1
        else:
            self.nonblank_line_count += 1
            self.section_content_lines[section] += 1
        self.content_char_count += record["char_count"]
        self.rhetoric.update(record["rhetorical_functions"])
        self.moves.update(record["section_moves"])
        for hit in record["transitions"]:
            self.transitions[hit["category"] + "::" + hit["phrase"].lower()] += 1
        self.punctuation.update(record["punctuation"])
        for span in record["italics"]:
            self.italic_terms[normalize_space(span["text"]).lower()] += 1
        for span in record["bold"]:
            self.bold_terms[normalize_space(span["text"]).lower()] += 1
        for item in record["latinisms"]:
            style = "italic" if item["italicized"] else "plain"
            self.latinism_styles[item["term"] + "::" + style] += 1
        for item in record["acronyms"]:
            self.acronym_statuses[item["status"]] += 1
            if item["status"] == "unexpanded_first_use":
                self.acronym_first_use_issues.append(
                    {"line_number": record["line_number"], "acronym": item["surface"]}
                )
        self.variables.update(record["variables"])
        for sentence in record["sentences"]:
            length = sentence["word_count"]
            self.word_count += length
            self.sentence_lengths.append(length)
            self.subordination_counts.append(sentence["subordination_count"])
            self.voice[sentence["voice"]] += 1
            self.voice_by_section[section][sentence["voice"]] += 1
            self.nominalizations.update(word.lower() for word in sentence["nominalizations"])

    def summary(self, total_lines: int) -> dict[str, Any]:
        lexical_voice_total = sum(
            count for voice, count in self.voice.items() if voice != "not_applicable"
        )
        passive_count = self.voice["passive"]
        active_count = self.voice["active_explicit"] + self.voice["active_or_other"]
        lengths = self.sentence_lengths
        successive_differences = [abs(right - left) for left, right in zip(lengths, lengths[1:])]
        if not lengths:
            cadence = "NO_SENTENCES"
        elif statistics.mean(lengths) <= 10:
            cadence = "PREDOMINANTLY_SHORT"
        elif statistics.mean(lengths) >= 30:
            cadence = "PREDOMINANTLY_LONG"
        elif successive_differences and statistics.mean(successive_differences) >= 10:
            cadence = "HIGH_VARIATION"
        else:
            cadence = "MODERATE_VARIATION"
        section_voice: dict[str, Any] = {}
        for section, counts in sorted(self.voice_by_section.items()):
            denominator = sum(value for key, value in counts.items() if key != "not_applicable")
            section_voice[section] = {
                "counts": dict(sorted(counts.items())),
                "passive_ratio": round(counts["passive"] / denominator, 4) if denominator else 0.0,
                "active_or_other_ratio": round(
                    (counts["active_explicit"] + counts["active_or_other"]) / denominator, 4
                )
                if denominator
                else 0.0,
            }
        return {
            "coverage": {
                "source_line_count": total_lines,
                "analyzed_line_record_count": sum(self.line_kinds.values()),
                "coverage_ratio": round(sum(self.line_kinds.values()) / total_lines, 6) if total_lines else 1.0,
                "blank_or_whitespace_lines": self.blank_line_count,
                "nonblank_lines": self.nonblank_line_count,
                "content_character_count_excluding_line_endings": self.content_char_count,
            },
            "structure": {
                "line_kinds": dict(sorted(self.line_kinds.items())),
                "section_line_counts": dict(sorted(self.sections.items())),
                "section_content_line_counts": dict(sorted(self.section_content_lines.items())),
            },
            "sentence_mechanics": {
                "sentence_count": len(lengths),
                "word_count": self.word_count,
                "sentence_length_words": {
                    "min": min(lengths) if lengths else 0,
                    "mean": round(statistics.mean(lengths), 3) if lengths else 0.0,
                    "median": round(statistics.median(lengths), 3) if lengths else 0.0,
                    "p90": round(percentile(lengths, 0.9), 3),
                    "max": max(lengths) if lengths else 0,
                    "population_stdev": round(statistics.pstdev(lengths), 3) if len(lengths) > 1 else 0.0,
                },
                "cadence": cadence,
                "mean_successive_length_difference": round(statistics.mean(successive_differences), 3)
                if successive_differences
                else 0.0,
                "voice_counts": dict(sorted(self.voice.items())),
                "passive_ratio": round(passive_count / lexical_voice_total, 4) if lexical_voice_total else 0.0,
                "active_or_other_ratio": round(active_count / lexical_voice_total, 4) if lexical_voice_total else 0.0,
                "voice_by_section": section_voice,
                "mean_subordinators_per_sentence": round(statistics.mean(self.subordination_counts), 4)
                if self.subordination_counts
                else 0.0,
                "nominalizations": dict(self.nominalizations.most_common()),
                "punctuation": dict(sorted(self.punctuation.items())),
            },
            "rhetorical_profile": {
                "functions": dict(sorted(self.rhetoric.items())),
                "section_moves": dict(sorted(self.moves.items())),
                "transitions": dict(self.transitions.most_common()),
            },
            "typography_and_lexicon": {
                "italic_terms": dict(self.italic_terms.most_common()),
                "bold_terms": dict(self.bold_terms.most_common()),
                "latinism_style_counts": dict(sorted(self.latinism_styles.items())),
                "acronym_status_counts": dict(sorted(self.acronym_statuses.items())),
                "unexpanded_first_use_acronyms": self.acronym_first_use_issues,
                "math_and_italic_variables": dict(self.variables.most_common()),
            },
        }


def line_ending(raw_line: str) -> tuple[str, str]:
    if raw_line.endswith("\r\n"):
        return raw_line[:-2], "CRLF"
    if raw_line.endswith("\n"):
        return raw_line[:-1], "LF"
    if raw_line.endswith("\r"):
        return raw_line[:-1], "CR"
    return raw_line, "NONE"


def analyze_line(
    raw_line: str,
    line_number: int,
    section: str,
    heading_path: Sequence[dict[str, Any]],
    seen_acronyms: set[str],
) -> dict[str, Any]:
    text, ending = line_ending(raw_line)
    kind = classify_line_kind(text, section)
    plain = markdown_plain_text(text)
    italics = extract_italic_spans(text)
    bold = extract_bold_spans(text)
    math_spans = extract_math_spans(text)
    rhetoric = rhetorical_hits(text)
    sentence_records = [
        analyze_sentence(sentence, start, end, ordinal)
        for ordinal, (sentence, start, end) in enumerate(split_sentences(text), start=1)
    ]
    transitions = transition_hits(plain)
    return {
        "record_type": "line",
        "line_number": line_number,
        "source_fragment_sha256": sha256_bytes(raw_line.encode("utf-8")),
        "text": text,
        "line_ending": ending,
        "char_count": len(text),
        "byte_count_with_line_ending": len(raw_line.encode("utf-8")),
        "line_kind": kind,
        "section": section,
        "heading_path": list(heading_path),
        "sentences": sentence_records,
        "sentence_count": len(sentence_records),
        "word_count": sum(sentence["word_count"] for sentence in sentence_records),
        "punctuation": punctuation_profile(text),
        "transitions": transitions,
        "italics": italics,
        "bold": bold,
        "math_spans": math_spans,
        "variables": extract_variables(italics, math_spans),
        "latinisms": latinism_statuses(text, italics),
        "acronyms": extract_acronyms(text, seen_acronyms),
        "rhetorical_functions": rhetoric,
        "section_moves": section_moves(section, rhetoric),
        "comparison": comparison_features(text),
    }


def update_heading_path(
    path: list[dict[str, Any]], level: int, heading: str, section: str, line_number: int
) -> list[dict[str, Any]]:
    updated = [item for item in path if int(item["level"]) < level]
    updated.append(
        {"level": level, "text": heading, "section": section, "line_number": line_number}
    )
    return updated


def json_line(record: dict[str, Any]) -> str:
    return json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def source_identity(source: Path, input_root: Path) -> tuple[str, str, Path]:
    relative = source.relative_to(input_root)
    author = relative.parts[0] if len(relative.parts) > 1 else "unassigned"
    paper = source.stem
    output_relative = relative.with_suffix(".jsonl")
    return author, paper, output_relative


def analyze_paper(source: Path, input_root: Path, output_root: Path) -> dict[str, Any]:
    source_bytes = source.read_bytes()
    source_text = source_bytes.decode("utf-8")
    raw_lines = source_text.splitlines(keepends=True)
    author, paper, output_relative = source_identity(source, input_root)
    output_path = output_root / output_relative
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = output_path.with_suffix(output_path.suffix + ".tmp")

    metadata = {
        "record_type": "paper_metadata",
        "schema_version": SCHEMA_VERSION,
        "analyzer_version": ANALYZER_VERSION,
        "source_path": source.as_posix(),
        "source_relative_path": source.relative_to(input_root).as_posix(),
        "source_sha256": sha256_bytes(source_bytes),
        "source_byte_count": len(source_bytes),
        "source_character_count": len(source_text),
        "source_line_count": len(raw_lines),
        "source_ends_with_line_ending": source_text.endswith(("\n", "\r")),
        "author_slug": author,
        "paper_slug": paper,
        "coverage_contract": "one line record per physical Markdown line, including blank lines",
    }

    accumulator = PaperAccumulator()
    seen_acronyms: set[str] = set()
    section = "SEC_TITLE"
    heading_path: list[dict[str, Any]] = []
    reconstructed_parts: list[str] = []

    with temp_path.open("w", encoding="utf-8", newline="") as stream:
        stream.write(json_line(metadata))
        for line_number, raw_line in enumerate(raw_lines, start=1):
            text, _ = line_ending(raw_line)
            heading = detect_heading(text)
            if heading:
                level, heading_text = heading
                section = detect_heading_section(heading_text, section)
                heading_path = update_heading_path(heading_path, level, heading_text, section, line_number)
            record = analyze_line(raw_line, line_number, section, heading_path, seen_acronyms)
            accumulator.add(record)
            reconstructed_parts.append(record["text"])
            ending = record["line_ending"]
            reconstructed_parts.append({"LF": "\n", "CRLF": "\r\n", "CR": "\r", "NONE": ""}[ending])
            stream.write(json_line(record))

        summary = accumulator.summary(len(raw_lines))
        reconstructed = "".join(reconstructed_parts).encode("utf-8")
        summary["coverage"]["reconstructed_sha256"] = sha256_bytes(reconstructed)
        summary["coverage"]["source_sha256"] = metadata["source_sha256"]
        summary["coverage"]["byte_exact_reconstruction"] = reconstructed == source_bytes
        summary_record = {
            "record_type": "paper_summary",
            "schema_version": SCHEMA_VERSION,
            "analyzer_version": ANALYZER_VERSION,
            "source_relative_path": metadata["source_relative_path"],
            "summary": summary,
        }
        stream.write(json_line(summary_record))

    if summary["coverage"]["analyzed_line_record_count"] != len(raw_lines):
        temp_path.unlink(missing_ok=True)
        raise RuntimeError(f"line coverage failure for {source}")
    if not summary["coverage"]["byte_exact_reconstruction"]:
        temp_path.unlink(missing_ok=True)
        raise RuntimeError(f"byte reconstruction failure for {source}")
    temp_path.replace(output_path)
    output_bytes = output_path.read_bytes()
    return {
        "author_slug": author,
        "paper_slug": paper,
        "source_relative_path": metadata["source_relative_path"],
        "source_sha256": metadata["source_sha256"],
        "analysis_relative_path": output_path.relative_to(output_root).as_posix(),
        "analysis_sha256": sha256_bytes(output_bytes),
        "analysis_byte_count": len(output_bytes),
        "coverage": summary["coverage"],
        "sentence_count": summary["sentence_mechanics"]["sentence_count"],
        "word_count": summary["sentence_mechanics"]["word_count"],
        "sections_present": sorted(
            section_name
            for section_name, count in summary["structure"]["section_content_line_counts"].items()
            if count
        ),
        "limitations": [
            "voice, clause, transition, and rhetorical-move labels are deterministic regex heuristics",
            "line preservation is byte-verified against Markdown, not independently against PDF rendering",
        ],
    }


def discover_inputs(input_root: Path, explicit_inputs: Sequence[str]) -> list[Path]:
    if explicit_inputs:
        discovered: list[Path] = []
        for raw in explicit_inputs:
            path = Path(raw).resolve()
            if path.is_dir():
                discovered.extend(path.rglob("*.md"))
            elif path.suffix.lower() == ".md" and path.is_file():
                discovered.append(path)
            else:
                raise FileNotFoundError(f"Markdown input not found: {raw}")
    else:
        discovered = list(input_root.rglob("*.md")) if input_root.exists() else []
    return sorted({path.resolve() for path in discovered}, key=lambda path: path.as_posix())


def corpus_aggregate(entries: Sequence[dict[str, Any]]) -> dict[str, Any]:
    total_lines = sum(int(entry["coverage"]["source_line_count"]) for entry in entries)
    analyzed_lines = sum(int(entry["coverage"]["analyzed_line_record_count"]) for entry in entries)
    authors = Counter(str(entry["author_slug"]) for entry in entries)
    return {
        "schema_version": SCHEMA_VERSION,
        "analyzer_version": ANALYZER_VERSION,
        "paper_count": len(entries),
        "author_count": len(authors),
        "papers_by_author": dict(sorted(authors.items())),
        "source_line_count": total_lines,
        "analyzed_line_record_count": analyzed_lines,
        "line_coverage_ratio": round(analyzed_lines / total_lines, 6) if total_lines else 1.0,
        "byte_exact_paper_count": sum(
            1 for entry in entries if entry["coverage"]["byte_exact_reconstruction"]
        ),
        "sentence_count": sum(int(entry["sentence_count"]) for entry in entries),
        "word_count": sum(int(entry["word_count"]) for entry in entries),
        "papers": list(entries),
        "methodological_limitations": [
            "linguistic and rhetorical classifications are transparent deterministic heuristics, not gold annotations",
            "PDF-to-Markdown fidelity must be verified by the upstream converter; this analyzer verifies Markdown coverage",
            "tables and display equations are preserved and typed as lines but not semantically solved",
            "active_or_other is the complement of detected passive voice, not a dependency-parsed active-voice judgment",
        ],
    }


def write_corpus_indexes(
    output_root: Path, aggregate: dict[str, Any], stem: str = "corpus_index"
) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    json_path = output_root / f"{stem}.json"
    jsonl_path = output_root / f"{stem}.jsonl"
    aggregate_with_time = {
        **aggregate,
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    }
    json_temp = json_path.with_suffix(".json.tmp")
    json_temp.write_text(
        json.dumps(aggregate_with_time, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    json_temp.replace(json_path)
    jsonl_temp = jsonl_path.with_suffix(".jsonl.tmp")
    with jsonl_temp.open("w", encoding="utf-8", newline="") as stream:
        stream.write(
            json_line(
                {
                    "record_type": "corpus_metadata",
                    **{key: value for key, value in aggregate_with_time.items() if key != "papers"},
                }
            )
        )
        for entry in aggregate["papers"]:
            stream.write(json_line({"record_type": "paper_index", **entry}))
    jsonl_temp.replace(jsonl_path)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze every physical line of converted academic-paper Markdown into JSONL."
    )
    parser.add_argument("inputs", nargs="*", help="Optional Markdown files/directories; defaults to --input-dir.")
    parser.add_argument("--input-dir", default="parsed_md", help="Root containing converted Markdown papers.")
    parser.add_argument("--output-dir", default="analysis_cache", help="Root for per-paper JSONL and corpus index.")
    parser.add_argument(
        "--fail-on-empty", action="store_true", help="Return a non-zero status when no Markdown inputs are found."
    )
    parser.add_argument("--quiet", action="store_true", help="Suppress per-paper progress messages.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    input_root = Path(args.input_dir).resolve()
    output_root = Path(args.output_dir).resolve()
    try:
        inputs = discover_inputs(input_root, args.inputs)
    except (FileNotFoundError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    if not inputs:
        aggregate = corpus_aggregate([])
        write_corpus_indexes(output_root, aggregate)
        message = f"No Markdown papers found under {input_root}; wrote an empty corpus index."
        print(message, file=sys.stderr if args.fail_on_empty else sys.stdout)
        return 3 if args.fail_on_empty else 0

    entries: list[dict[str, Any]] = []
    for source in inputs:
        try:
            source.relative_to(input_root)
        except ValueError:
            print(f"ERROR: input is outside --input-dir and cannot be routed: {source}", file=sys.stderr)
            return 2
        try:
            entry = analyze_paper(source, input_root, output_root)
        except (OSError, UnicodeError, RuntimeError) as error:
            print(f"ERROR: {source}: {error}", file=sys.stderr)
            return 1
        entries.append(entry)
        if not args.quiet:
            coverage = entry["coverage"]
            print(
                f"ANALYZED {entry['source_relative_path']}: "
                f"{coverage['analyzed_line_record_count']}/{coverage['source_line_count']} lines, "
                f"{entry['sentence_count']} sentences, byte_exact={coverage['byte_exact_reconstruction']}"
            )

    aggregate = corpus_aggregate(entries)
    if args.inputs:
        digest = hashlib.sha256(
            "\n".join(entry["source_relative_path"] for entry in entries).encode("utf-8")
        ).hexdigest()[:12]
        write_corpus_indexes(output_root / "indexes", aggregate, f"batch_{digest}")
    else:
        write_corpus_indexes(output_root, aggregate)
    print(
        f"CORPUS papers={aggregate['paper_count']} authors={aggregate['author_count']} "
        f"lines={aggregate['analyzed_line_record_count']}/{aggregate['source_line_count']} "
        f"coverage={aggregate['line_coverage_ratio']:.6f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
