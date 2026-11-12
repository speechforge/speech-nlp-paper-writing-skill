#!/usr/bin/env python3
"""Build the interactive demo website for a project: audio A/B with live spectrograms, blind listening test,
text comparison, figure gallery, video, ranked results, credits and licenses. Static files, no external requests.

    build_demo_site.py PROJECT [--out demo/site] [--serve] [--port 8000] [--allow-venue-words]

Reads  PROJECT/project_meta.json (name, tagline, authors, licenses) and PROJECT/demo/samples.json.
Media referenced in samples.json lives under PROJECT/demo/assets/ and is copied into the site.
The site is named after the PROJECT. Conference, journal, and publisher names are refused in its
name and text (use --allow-venue-words only if the authors explicitly want them).

samples.json (every key is optional; sections appear only when their data exists):
{
  "tagline": "...", "summary": "Two or three plain-language sentences.", "citation": "...",
  "pipeline_lede": "...", "pipeline": [{"title": "Find the boundary", "text": "...", "image": "images/step1.png"}],
  "audio_samples": [{"title": "...", "transcript": "...",
      "systems": [{"name": "Reference", "file": "audio/s1_ref.wav", "reference": true},
                  {"name": "Baseline", "file": "audio/s1_base.wav"},
                  {"name": "Ours", "file": "audio/s1_ours.wav", "highlight": true, "spectrogram": "images/s1_ours.png"}]}],
  "blind_test": {"enabled": true, "question": "Which sample sounds more natural?"},
  "text_samples": [{"title": "...", "input": "...", "reference": "...", "outputs": [{"name": "Ours", "text": "...", "highlight": true}]}],
  "gallery": [{"title": "...", "file": "images/fig1_web.png", "caption": "...", "alt": "..."}],
  "videos": [{"title": "...", "file": "video/demo.mp4", "poster": "images/poster.png", "caption": "..."}],
  "results": {"title": "Listening test", "metric": "MOS", "direction": "up", "axis_min": 3.0, "decimals": 2,
              "rows": [{"name": "Baseline", "value": 3.86, "ci": 0.07}, {"name": "Ours", "value": 4.11, "ci": 0.08, "highlight": true}]}
}
Numbers in "results" must come from the project's results files (see references/15_interactive_demo_website.md).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import socketserver
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import load_json, save_json, slugify, venue_words  # noqa: E402
from _serve import static_handler  # noqa: E402

SKILL = Path(__file__).resolve().parent.parent
SITE_TPL = SKILL / "templates" / "demo_site"
MEDIA_EXT = {".wav", ".mp3", ".flac", ".ogg", ".m4a", ".png", ".jpg", ".jpeg", ".svg", ".webp", ".gif", ".mp4", ".webm", ".vtt", ".pdf"}
PATH_KEYS = {"file", "poster", "spectrogram", "image", "captions"}
TEXT_KEYS = {"project_name", "tagline", "summary", "title", "text", "transcript", "name", "caption", "question", "pipeline_lede", "note"}


def walk(obj, fn, path=()):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str):
                obj[k] = fn(k, v, path)
            else:
                walk(v, fn, path + (k,))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            if isinstance(v, str):
                obj[i] = fn(None, v, path)
            else:
                walk(v, fn, path)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project")
    ap.add_argument("--out", default="demo/site")
    ap.add_argument("--serve", action="store_true")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--allow-venue-words", action="store_true")
    args = ap.parse_args()
    root = Path(args.project).resolve()
    meta = load_json(root / "project_meta.json")
    samples = load_json(root / "demo" / "samples.json", {})
    out = (root / args.out).resolve()
    if root not in out.parents:
        raise SystemExit("error: --out must be inside the project")
    name = meta["project_name"]

    # 1. the site carries the project's identity, never a venue's
    texts = [("project name", name), ("tagline", samples.get("tagline", meta.get("tagline", ""))), ("summary", samples.get("summary", ""))]
    found = []
    walk(json.loads(json.dumps(samples)), lambda k, v, p: (found.append((k, v)) if k in TEXT_KEYS else None) or v)
    texts += [(k or "text", v) for k, v in found]
    bad = sorted({w for _, t in texts for w in venue_words(t)})
    if bad and not args.allow_venue_words:
        raise SystemExit(f"error: the demo site must be named after the project, not a venue. Found {', '.join(bad)}. Reword the text, or pass --allow-venue-words if the authors insist.")

    # 2. copy only referenced media, from inside demo/assets
    assets = (root / "demo" / "assets").resolve()
    copied, missing, total = {}, [], 0

    def relocate(key, value, _path):
        nonlocal total
        if key not in PATH_KEYS or not value or value.startswith(("http://", "https://", "assets/")):
            return value
        src = (assets / value).resolve()
        if assets not in src.parents or not src.is_file() or src.suffix.lower() not in MEDIA_EXT:
            missing.append(value)
            return value
        if value not in copied:
            dst = out / "assets" / value
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
            copied[value] = f"assets/{value}"
            total += src.stat().st_size
        return copied[value]

    if out.exists():
        shutil.rmtree(out / "assets", ignore_errors=True)
    out.mkdir(parents=True, exist_ok=True)
    walk(samples, relocate)
    if missing:
        raise SystemExit("error: media not found under demo/assets/ (or unsupported type): " + ", ".join(sorted(set(missing))))

    # 3. data + page
    credits = load_json(root / "demo" / "site_credits.json", {})
    data = {"project_name": name, "slug": meta.get("slug", slugify(name)), "tagline": samples.get("tagline", meta.get("tagline", "")), "summary": samples.get("summary", ""),
            "citation": samples.get("citation", ""), "pipeline_lede": samples.get("pipeline_lede", ""), "pipeline": samples.get("pipeline", []),
            "audio_samples": samples.get("audio_samples", []), "blind_test": samples.get("blind_test", {"enabled": True}), "text_samples": samples.get("text_samples", []),
            "gallery": samples.get("gallery", []), "videos": samples.get("videos", []), "results": samples.get("results", []),
            "credits": credits if not meta.get("anonymous", True) or samples.get("show_credits") else {k: v for k, v in credits.items() if k not in ("authors", "repository_url", "funding")}}
    hue = int(hashlib.sha256(data["slug"].encode()).hexdigest()[:4], 16) % 360
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    page = (SITE_TPL / "index.html").read_text(encoding="utf-8")
    for k, v in {"@@PROJECT_NAME@@": name.replace("<", "&lt;"), "@@TAGLINE@@": data["tagline"].replace('"', "&quot;"), "@@HUE@@": str(hue), "@@DATA@@": payload}.items():
        page = page.replace(k, v)
    (out / "index.html").write_text(page, encoding="utf-8")
    for f in ("style.css", "app.js"):
        shutil.copyfile(SITE_TPL / f, out / f)
    sections = [k for k in ("pipeline", "audio_samples", "text_samples", "gallery", "videos", "results") if data[k]]
    save_json(out / "site_manifest.json", {"project": name, "hue": hue, "sections": sections, "media_files": len(copied), "media_bytes": total,
                                           "audio_samples": len(data["audio_samples"]), "anonymous": meta.get("anonymous", True)})
    print(f"built {out}  (project: {name}, accent hue {hue}, sections: {', '.join(sections) or 'hero and credits only'}, media: {len(copied)} files, {total / 1e6:.1f} MB)")
    if total > 60e6:
        print("warning: more than 60 MB of media; compress audio (for example 48 kHz mono 16-bit) or trim the samples")
    if meta.get("anonymous", True):
        print("note: anonymous mode is on, so author names and the repository link are hidden on the site until you set anonymous to false in project_meta.json")
    if args.serve:
        with socketserver.ThreadingTCPServer(("127.0.0.1", args.port), static_handler(out)) as srv:
            print(f"serving http://127.0.0.1:{args.port}/  (Ctrl+C to stop)")
            try:
                srv.serve_forever()
            except KeyboardInterrupt:
                pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
