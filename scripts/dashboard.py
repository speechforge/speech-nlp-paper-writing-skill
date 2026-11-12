#!/usr/bin/env python3
"""Local progress dashboard for a manuscript workspace. Costs zero model tokens: it only reads project files.

    dashboard.py PROJECT [--port 8765] [--open]

Then open http://127.0.0.1:8765/ . The page refreshes itself every few seconds and shows:
the ten-stage pipeline, what blocks submission, the next actions, section completion, the claim-evidence
balance, citation verification, experiments, figures, the built demo website (/demo/) and the PDF (/files/...).
Stage status is derived from real files, never self-reported. Loopback only; foreign Host headers are refused;
the single action it can run is `paper_check.py PROJECT ready`.
"""
from __future__ import annotations

import argparse
import http.server
import json
import re
import socketserver
import subprocess
import sys
import threading
import webbrowser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import load_json, now_iso  # noqa: E402
from _serve import safe_join, send_file  # noqa: E402
import citations  # noqa: E402
import experiments  # noqa: E402
import paper_check  # noqa: E402

HERE = Path(__file__).resolve().parent
PAGE = HERE.parent / "templates" / "dashboard" / "index.html"
FILE_ROOTS = ["paper/figures", "paper/tables", "demo/assets", "paper"]
FILE_EXT = {".png", ".jpg", ".jpeg", ".svg", ".pdf", ".wav", ".mp3"}

STAGES = [
    ("context", "Context", "Run context_digest.py on the notes or folder and read the digest."),
    ("story", "Story", "Fill the thesis, novelty keywords, and contributions in paper_story.md."),
    ("evidence", "Evidence", "List every claim in claim_evidence_map.md and tie each to a table, figure, or number."),
    ("experiments", "Experiments", "Write the brief for each claim that needs an experiment and get approval to run it."),
    ("draft", "Draft", "Replace the remaining [INSERT] markers, one section file at a time."),
    ("figures", "Figures", "Generate the teaser, method diagram, result plots, and tables from data."),
    ("citations", "Citations", "Search, verify with two sources, and read each cited abstract against its sentence."),
    ("review", "Review", "Write reviewer_analysis.md as a skeptical reviewer and turn high risks into edits."),
    ("build", "Build", "Compile the paper and clear the log of errors and undefined references."),
    ("site", "Website", "Fill demo/samples.json and run build_demo_site.py."),
]


def words(text: str) -> int:
    text = re.sub(r"(?<!\\)%.*", "", text)
    text = re.sub(r"\[INSERT[^\]]*\]", " ", text)
    return len(re.findall(r"[A-Za-z]{2,}", re.sub(r"\\[a-zA-Z]+", " ", text)))


def story_fraction(root: Path) -> tuple[float, str]:
    f = root / "paper_story.md"
    if not f.exists():
        return 0.0, "paper_story.md missing"
    t = f.read_text(encoding="utf-8")
    checks = {"thesis": "[artifact or idea]" not in t, "novelty keywords": "[3-5 terms" not in t and bool(paper_check.novelty_terms(root, None)),
              "contributions": bool(re.search(r"^1\.\s+\S", t.split("## Contributions")[-1] if "## Contributions" in t else "", re.M))}
    missing = [k for k, v in checks.items() if not v]
    return sum(checks.values()) / 3, ("complete" if not missing else "missing: " + ", ".join(missing))


def compute(root: Path) -> dict:
    meta = load_json(root / "project_meta.json", {})
    state = load_json(root / "paper_state.json", {})
    pdir = root / "paper"
    sections = []
    for f in sorted((pdir / "sections").glob("*.tex"), key=lambda q: (0 if q.stem == "abstract" else 1 if q.stem[:1].isdigit() else 2, q.stem)) if (pdir / "sections").is_dir() else []:
        t = f.read_text(encoding="utf-8", errors="replace")
        name = re.sub(r"^\d+_", "", f.stem).replace("_", " ").capitalize()
        sections.append({"name": name, "words": words(t), "markers": len(re.findall(r"\[INSERT", t))})
    claims, cprobs = paper_check.claim_map_status(root)
    total_claims = sum(claims.values())
    ledger = load_json(root / "experiments" / "ledger.json", {"experiments": []})
    exps = ledger.get("experiments", [])
    needs_exp = 0
    for r in experiments.claim_rows(root):
        if r.get("status", "").lower() == "needs experiment":
            needs_exp += 1
    done_exp = sum(1 for e in exps if e["status"] == "ingested")
    pending = [e for e in exps if e["status"] not in ("ingested", "cancelled")]
    lock = load_json(root / "citation_lock.json", {"entries": {}})["entries"]
    cited, _, markers = citations.collect_keys(root)
    verified = sum(1 for k in cited if lock.get(k, {}).get("status") == "verified")
    figs, seen = [], set()
    for p in sorted((pdir / "figures").glob("*")) if (pdir / "figures").is_dir() else []:
        if p.suffix in (".pdf", ".png") and not p.name.endswith("_web.png") and p.stem not in seen:
            seen.add(p.stem)
            figs.append(p)
    tabs = list((pdir / "tables").glob("*.tex")) if (pdir / "tables").is_dir() else []
    build = load_json(root / ".paper" / "build_record.json", {})
    checks = load_json(root / ".paper" / "checks.json", {})
    review_rows = 0
    rf = root / "reviewer_analysis.md"
    if rf.exists():
        in_risks = False
        for line in rf.read_text(encoding="utf-8").splitlines():
            if line.startswith("## Major risks"):
                in_risks = True
            elif line.startswith("## ") and in_risks:
                in_risks = False
            elif in_risks and line.startswith("|") and not re.match(r"^\|[\s:-]+\|", line) and not line.lower().startswith("| id"):
                review_rows += any(c.strip() for c in line.strip("|").split("|")[:3])
    site = load_json(root / "demo" / "site" / "site_manifest.json", {})
    fr = {}
    fr["context"] = (1.0 if (root / "context_digest.md").exists() else 0.0, "digest ready" if (root / "context_digest.md").exists() else "no digest yet")
    fr["story"] = story_fraction(root)
    fr["evidence"] = ((claims["supported"] + 0.5 * claims["partial"]) / total_claims if total_claims else 0.0,
                      f"{claims['supported']} supported, {claims['partial']} bounded, {claims['open']} open" if total_claims else "no claims listed")
    gap = needs_exp + len(pending)
    fr["experiments"] = (1.0 if gap == 0 else done_exp / max(1, done_exp + gap), "none needed" if gap == 0 and not exps else f"{done_exp} ingested, {gap} outstanding")
    secs_done = sum(1 for s in sections if s["markers"] == 0 and s["words"] > 15)
    fr["draft"] = (secs_done / len(sections) if sections else 0.0, f"{secs_done} of {len(sections)} sections free of placeholders" if sections else "no sections")
    fr["figures"] = (min(1.0, (len(figs) + len(tabs)) / 4), f"{len(figs)} figures, {len(tabs)} tables")
    fr["citations"] = (verified / len(cited) if cited else 0.0, f"{verified} of {len(cited)} cited works verified" + (f"; {len(markers)} marker(s)" if markers else "") if cited else "nothing cited yet")
    fr["review"] = (min(1.0, review_rows / 3), f"{review_rows} risk(s) analysed")
    b = build.get("status")
    fr["build"] = (1.0 if b == "ok" else 0.0, {"ok": "compiled", "failed": "build failed", "tex-unavailable": "no TeX here; compile on Overleaf", None: "not built yet"}.get(b, b or "not built yet"))
    fr["site"] = (1.0 if site.get("sections") or (root / "demo" / "site" / "index.html").exists() and site else (0.4 if (root / "demo" / "samples.json").exists() else 0.0),
                  f"built: {', '.join(site.get('sections', [])) or 'hero only'}" if site else ("samples.json ready, not built" if (root / "demo" / "samples.json").exists() else "no samples yet"))
    stages, active_set = [], False
    for sid, name, hint in STAGES:
        frac, detail = fr[sid]
        st = "done" if frac >= 0.999 else ("progress" if frac > 0 else "todo")
        active = False
        if st != "done" and not active_set:
            active, active_set = True, True
        stages.append({"id": sid, "name": name, "state": st, "fraction": round(frac, 3), "detail": detail, "active": active, "hint": hint})
    overall = sum(s["fraction"] for s in stages) / len(stages)
    nxt = [f"{s['name']}: {s['hint']}" for s in stages if s["state"] != "done"][:3]
    thumbs = [{"name": p.name, "url": "/files/paper/figures/" + (p.stem + "_web.png" if (p.parent / (p.stem + "_web.png")).exists() else p.name)} for p in figs if p.suffix == ".png" or (p.parent / (p.stem + "_web.png")).exists()][:12]
    return {"project": meta.get("project_name", root.name), "venue": state.get("venue_family", ""), "journey": state.get("journey", ""), "updated": now_iso(),
            "overall": round(overall, 3), "stages": stages, "next": nxt, "gates": checks.get("gates", []), "checks_at": checks.get("checked_at", ""),
            "sections": sections, "claims": claims, "citations": {"cited": len(cited), "verified": verified,
                                                                  "statuses": sorted({v.get("status", "?") for k, v in lock.items() if k in cited})},
            "experiments": [{"id": e["id"], "title": e["title"], "status": e["status"], "summary": e.get("summary", "")} for e in exps],
            "figures": thumbs, "demo": bool(site), "pdf": (pdir / "main.pdf").exists(), "anonymous": meta.get("anonymous", True),
            "sources": {k: v for k, v in load_json(HERE.parent / "skills" / "ACTIVE_PROFILE.json", {}).items() if k in ("profile", "enabled", "precedence")}}


def make_handler(root: Path, port: int):
    class H(http.server.BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _host_ok(self) -> bool:
            host = self.headers.get("Host", "")
            return host in (f"127.0.0.1:{port}", f"localhost:{port}")

        def _json(self, obj, code=200):
            body = json.dumps(obj).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if not self._host_ok():
                self.send_error(403, "unexpected Host header")
                return
            path = self.path.split("?", 1)[0]
            if path == "/":
                body = PAGE.read_text(encoding="utf-8").encode()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(body)
            elif path == "/api/state":
                try:
                    self._json(compute(root))
                except Exception as exc:  # keep the page alive while files are mid-edit
                    self._json({"error": str(exc)}, 500)
            elif path.startswith("/demo"):
                rel = path[len("/demo"):] or "/"
                if rel == "/":
                    rel = "/index.html"
                if path == "/demo":
                    self.send_response(301)
                    self.send_header("Location", "/demo/")
                    self.end_headers()
                    return
                target = safe_join(root / "demo" / "site", rel)
                send_file(self, target) if target else self.send_error(404)
            elif path.startswith("/files/"):
                rel = path[len("/files/"):]
                target = next((safe_join(root, rel) for base in FILE_ROOTS if rel.startswith(base + "/") or rel == base), None)
                if target and target.suffix.lower() in FILE_EXT:
                    send_file(self, target)
                else:
                    self.send_error(404)
            else:
                self.send_error(404)

        def do_POST(self):
            if not self._host_ok() or self.path != "/api/run-checks":
                self.send_error(403)
                return
            if (self.headers.get("Origin") or "").rstrip("/") not in ("", f"http://127.0.0.1:{port}", f"http://localhost:{port}"):
                self.send_error(403, "cross-origin request refused")
                return
            r = subprocess.run([sys.executable, str(HERE / "paper_check.py"), str(root), "ready"], capture_output=True, text=True, timeout=180)
            self._json({"ok": r.returncode == 0, "output": "\n".join(r.stdout.splitlines()[-30:])})
    return H


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--open", action="store_true", help="open the page in the default browser")
    args = ap.parse_args()
    root = Path(args.project).resolve()
    if not root.is_dir():
        raise SystemExit(f"error: {root} is not a folder")
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("127.0.0.1", args.port), make_handler(root, args.port)) as srv:
        url = f"http://127.0.0.1:{args.port}/"
        print(f"dashboard for {root.name}: {url}   (Ctrl+C to stop; nothing leaves this machine)")
        if args.open:
            threading.Timer(0.5, lambda: webbrowser.open(url)).start()
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
