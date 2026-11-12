"""Unit tests for the paper-writing skill scripts. Offline: citation tests use stubbed records.

    python3 -m unittest discover -s tests -v
Set PAPER_SKILL_ONLINE=1 to also run the live citation check against public APIs.
"""
from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
SCRIPTS = SKILL / "scripts"
sys.path.insert(0, str(SCRIPTS))

import _common  # noqa: E402
import citations  # noqa: E402
import prose_lint  # noqa: E402
import credits_license  # noqa: E402


def run(script: str, *args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, args)], capture_output=True, text=True)


def new_project(tmp: Path, name="TestProj", venue="acl") -> Path:
    root = tmp / "proj"
    r = run("paper_init.py", "init", root, "--name", name, "--venue", venue)
    assert r.returncode == 0, r.stderr + r.stdout
    return root


class CommonTests(unittest.TestCase):
    def test_venue_words(self):
        self.assertEqual(_common.venue_words("ICASSP demo"), ["ICASSP"])
        self.assertEqual(_common.venue_words("BoundaryVoc"), [])
        self.assertEqual(_common.venue_words("Oracle of the miracle"), [])  # no false hit on 'acl' inside words
        self.assertEqual(_common.venue_words("Interspeech samples"), ["Interspeech"])

    def test_slugify(self):
        self.assertEqual(_common.slugify("Boundary Voc: v2!"), "boundary-voc-v2")


class ProseLintTests(unittest.TestCase):
    def lint(self, text, suffix=".tex", name="x"):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / (name + suffix)
            p.write_text(text, encoding="utf-8")
            return prose_lint.lint(p, set())

    def cats(self, findings, sev=None):
        return {f[3] for f in findings if sev is None or f[2] == sev}

    def test_code_terms_flagged_high(self):
        f = self.lint("We run \\texttt{train\\_vocoder.py} with --batch-size 32 and call build_model().")
        self.assertTrue({"code-span", "file-name", "cli-flag", "identifier", "function-call"} <= self.cats(f, "high"))

    def test_clean_prose_passes(self):
        f = self.lint("Pitch error falls from 4.1 to 2.9 Hz on LJSpeech (Table~\\ref{t}), a 29\\% reduction.\nThe sampling rate is 22.05 kHz with $n_{fft}=1024$.")
        self.assertEqual(f, [])

    def test_unbacked_claim_vs_backed(self):
        bad = self.lint("Our method achieves state-of-the-art performance and is superior.")
        self.assertIn("unbacked-claim", self.cats(bad))
        good = self.lint("Our method achieves a new state-of-the-art pitch error of 2.9 Hz on LJSpeech.")
        self.assertNotIn("unbacked-claim", self.cats(good))

    def test_preamble_and_math_ignored(self):
        f = self.lint("\\documentclass{article}\n\\author{A \\texttt{a@b.org}}\n\\begin{document}\nWe study $train\\_loop$ effects.\n\\end{document}\n")
        self.assertEqual(f, [])

    def test_availability_section_allows_repository_word(self):
        f = self.lint("\\section{Code Availability}\nThe repository and scripts are released.\n")
        self.assertNotIn("implementation-vocabulary", self.cats(f))
        g = self.lint("\\section{Method}\nThe repository and scripts define the model.\n")
        self.assertIn("implementation-vocabulary", self.cats(g))

    def test_markdown_code_block_flagged(self):
        f = self.lint("Intro\n```\nprint(1)\n```\n", suffix=".md")
        self.assertIn("code-block", self.cats(f, "high"))


class CitationLogicTests(unittest.TestCase):
    def rec(self, **kw):
        base = dict(source="crossref", url="u", title="Attention Is All You Need", authors=["Vaswani, Ashish"], year=2017,
                    venue="", doi="10.1/x", arxiv="", abstract="abs", typ="")
        base.update(kw)
        return citations.rec(base.pop("source"), base.pop("url"), base["title"], base["authors"], base["year"], base["venue"], base["doi"], base["arxiv"], base["abstract"], base["typ"])

    def test_agree_and_conflict(self):
        p = self.rec()
        self.assertTrue(citations.agree(p, self.rec(source="openalex", authors=["Ashish Vaswani"], year=2018))[0])
        ok, why = citations.agree(p, self.rec(source="openalex", title="A completely different paper on parsing"))
        self.assertFalse(ok)
        self.assertTrue(any("title" in w for w in why))
        self.assertFalse(citations.agree(p, self.rec(source="openalex", authors=["Smith, John"]))[0])
        self.assertFalse(citations.agree(p, self.rec(source="openalex", year=2012))[0])

    def test_verify_entry_statuses(self):
        prim, good = self.rec(), self.rec(source="openalex", authors=["Ashish Vaswani"])
        orig = (citations.f_crossref, citations.f_datacite, citations.f_openalex, citations.f_s2, citations.f_arxiv)
        try:
            citations.f_crossref = lambda net, doi: prim
            citations.f_datacite = lambda net, doi: None
            citations.f_openalex = lambda net, doi="", arxiv="", title="": good
            citations.f_s2 = lambda net, doi="", arxiv="", acl="": None
            citations.f_arxiv = lambda net, a: None
            net = citations.Net(None, offline=True)
            r = citations.verify_entry(net, {"doi": "10.1/x", "supports": [{"sentence": "s", "relation": "direct"}]}, "ieee", None)
            self.assertEqual(r["status"], "verified")
            self.assertIn("@", r["bibtex"])
            self.assertIn("{{Attention Is All You Need}}", r["bibtex"])
            r2 = citations.verify_entry(net, {"doi": "10.1/x"}, "ieee", None)  # no supports -> claim pending
            self.assertEqual(r2["status"], "metadata-verified")
            r3 = citations.verify_entry(net, {"doi": "10.1/x", "supports": [{"sentence": "s", "relation": "weak"}]}, "ieee", None)
            self.assertNotEqual(r3["status"], "verified")
            citations.f_openalex = lambda net, doi="", arxiv="", title="": self.rec(source="openalex", title="Unrelated parsing study")
            r4 = citations.verify_entry(net, {"doi": "10.1/x"}, "ieee", None)
            self.assertEqual(r4["status"], "conflict")
            citations.f_openalex = lambda net, doi="", arxiv="", title="": None
            r5 = citations.verify_entry(net, {"doi": "10.1/x"}, "ieee", None)
            self.assertEqual(r5["status"], "single-source")
            citations.f_crossref = lambda net, doi: None
            r6 = citations.verify_entry(net, {"doi": "10.9/none"}, "ieee", None)
            self.assertEqual(r6["status"], "not-found")
            self.assertNotIn("bibtex", r6)
        finally:
            (citations.f_crossref, citations.f_datacite, citations.f_openalex, citations.f_s2, citations.f_arxiv) = orig

    def test_bibtex_style_author_truncation(self):
        r = self.rec(authors=[f"Author{i}, A" for i in range(9)])
        self.assertIn("and others", citations.build_bibtex("k", r, "ieee", None))
        self.assertNotIn("and others", citations.build_bibtex("k", r, "acl", None))

    def test_check_gate(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "paper").mkdir()
            (root / "paper" / "main.tex").write_text("\\providecommand{\\citep}[1]{\\cite{#1}}\nA \\citep{a2020x}. B \\cite{ghost}. C \\cite{PLACEHOLDER_x}. % \\cite{commented}\n")
            (root / "paper" / "references.bib").write_text("@article{a2020x,\n title={T}\n}\n@article{a2020x,\n title={T}\n}\n")
            (root / "citation_lock.json").write_text(json.dumps({"entries": {"a2020x": {"status": "verified", "claim_status": "ok"}}}))
            r = run("citations.py", "check", root, "--strict")
            self.assertEqual(r.returncode, 1)
            self.assertIn("ghost", r.stdout)
            self.assertIn("duplicate BibTeX key", r.stdout)
            self.assertIn("PLACEHOLDER_x", r.stdout)
            self.assertNotIn("commented", r.stdout)
            self.assertNotIn("'#1'", r.stdout)

    @unittest.skipUnless(os.environ.get("PAPER_SKILL_ONLINE"), "needs network")
    def test_live_verification(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "citation_requests.json").write_text(json.dumps({"entries": [{"acl": "N19-1423", "supports": [{"sentence": "s", "relation": "direct"}]}]}))
            r = run("citations.py", "verify", root)
            self.assertIn("verified", r.stdout)


class WorkflowTests(unittest.TestCase):
    def test_init_blocks_venue_names(self):
        with tempfile.TemporaryDirectory() as d:
            r = run("paper_init.py", "init", Path(d) / "p", "--name", "ICASSP Demo")
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("venue", (r.stderr + r.stdout).lower())

    def test_init_and_convert_keep_prose(self):
        with tempfile.TemporaryDirectory() as d:
            root = new_project(Path(d), "ConvTest", "acl")
            sec = root / "paper" / "sections" / "06_conclusion.tex"
            sec.write_text("We showed a thing.\n")
            r = run("paper_init.py", "convert", root, "--to", "ieee")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("IEEEtran", (root / "paper" / "main.tex").read_text())
            self.assertEqual(sec.read_text(), "We showed a thing.\n")
            self.assertTrue((root / ".paper" / "wrappers" / "main.acl.tex").exists())
            self.assertFalse(list((root / "paper").glob("main.*.tex")))  # backups never pollute the manuscript tree

    def test_ready_gate_fails_on_skeleton_and_checks_novelty_thread(self):
        with tempfile.TemporaryDirectory() as d:
            root = new_project(Path(d))
            r = run("paper_check.py", root, "ready")
            self.assertEqual(r.returncode, 1)
            self.assertIn("NOT READY", r.stdout)
            self.assertTrue((root / ".paper" / "checks.json").exists())
            for name in ("abstract", "01_introduction", "03_method", "05_results", "06_conclusion"):
                (root / "paper" / "sections" / f"{name}.tex").write_text("We study boundary-aware training here.\n")
            r = run("paper_check.py", root, "thread", "--terms", "boundary-aware")
            self.assertEqual(r.returncode, 0, r.stdout)
            (root / "paper" / "sections" / "06_conclusion.tex").write_text("We conclude.\n")
            r = run("paper_check.py", root, "thread", "--terms", "boundary-aware")
            self.assertEqual(r.returncode, 1)
            self.assertIn("conclusion", r.stdout)

    def test_credit_and_license(self):
        meta = {"project_name": "P", "anonymous": True, "authors": [
            {"name": "Ada Lovelace", "roles": ["Conceptualization", "Writing - original draft"], "equal_contribution": True},
            {"name": "Bad Roles", "roles": ["Wizardry"]}],
            "licenses": {"paper": "CC-BY-4.0", "code": "Apache-2.0"},
            "third_party": [{"name": "SomeCorpus", "kind": "dataset", "license": "CC-BY-NC-4.0", "url": "https://x"}],
            "funding": [{"agency": "Ministry of Electronics and Information Technology (MeitY)", "grant": "11(1)/2022-HCC(TDIL)"}]}
        errors, _ = credits_license.validate(meta)
        self.assertTrue(any("Wizardry" in e for e in errors))
        meta["authors"].pop()
        self.assertEqual(credits_license.validate(meta)[0], [])
        self.assertIn("A.L.", credits_license.credit_tex(meta))
        lic = credits_license.license_tex(meta)
        self.assertIn("anonymised repository", lic)
        self.assertIn("non-commercial", lic)
        ack = credits_license.ack_tex(meta)
        self.assertIn("Government of India, under Project Grant ID: 11(1)/2022-HCC(TDIL).", ack)
        meta["human_subjects"] = {"involved": True}
        self.assertTrue(any("consent" in e for e in credits_license.validate(meta)[0]))

    def test_context_digest(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "README.md").write_text("# T\nNotes about arXiv:2010.05646 here.\n")
            (root / "results").mkdir()
            with open(root / "results" / "main.csv", "w", newline="") as fh:
                w = csv.writer(fh)
                w.writerows([["method", "seed", "pitch_err_hz"], ["a", 1, 4.1], ["b", 1, 2.9]])
            (root / "m.py").write_text('"""Does a thing."""\nclass Foo: pass\n')
            r = run("context_digest.py", root)
            self.assertEqual(r.returncode, 0)
            out = r.stdout
            self.assertIn("arXiv:2010.05646", out)
            self.assertIn("pitch_err_hz", out)
            self.assertIn("uncertainty column (std/ci/err): NO", out)  # 'err' in a metric name is not an error bar
            self.assertIn("FOR UNDERSTANDING ONLY", out)

    def test_latex_table(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "r.csv"
            f.write_text("method,mos,rtf\nA,3.9,0.2\nB,4.1,0.1\n")
            r = run("make_latex_table.py", f, "--direction", "mos:up,rtf:down", "--family", "ieee")
            self.assertIn("\\textbf{4.10}", r.stdout)
            self.assertIn("\\textbf{0.10}", r.stdout)
            self.assertNotIn("\\textbf{3.90}", r.stdout)
            self.assertLess(r.stdout.index("\\caption"), r.stdout.index("\\toprule"))  # IEEE: caption above
            r2 = run("make_latex_table.py", f, "--family", "acl")
            self.assertGreater(r2.stdout.index("\\caption"), r2.stdout.index("\\bottomrule"))  # ACL: caption below
            self.assertNotIn("|", r.stdout.split("\\begin{tabular}")[1].split("\n")[0])  # no vertical rules

    def test_experiment_loop_guards(self):
        with tempfile.TemporaryDirectory() as d:
            root = new_project(Path(d))
            r = run("experiments.py", "brief", root, "--title", "t", "--hypothesis", "h", "--claims", "1")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertNotEqual(run("experiments.py", "run", root, "EXP-001", "--", "echo", "x").returncode, 0)  # not approved
            run("experiments.py", "approve", root, "EXP-001")
            self.assertNotEqual(run("experiments.py", "run", root, "EXP-001", "--", "echo", "x").returncode, 0)  # [INSERT] left in brief
            brief = root / "experiments" / "briefs" / "EXP-001.md"
            import re
            brief.write_text(re.sub(r"\[INSERT[^\]]*\]", "done", brief.read_text()))
            res = run("experiments.py", "run", root, "EXP-001", "--", "sh", "-c", "echo 'system,seed,m' > results.csv; echo 'a,1,2' >> results.csv")
            self.assertEqual(res.returncode, 0, res.stderr)
            exit_file = root / "experiments" / "logs" / "EXP-001.exit"
            for _ in range(100):
                if exit_file.exists() and exit_file.read_text().strip():
                    break
                import time
                time.sleep(0.1)
            self.assertIn("done", run("experiments.py", "status", root).stdout)
            ing = run("experiments.py", "ingest", root, "EXP-001", root / "results.csv")
            self.assertEqual(ing.returncode, 0, ing.stderr)
            self.assertTrue((root / "experiments" / "results" / "EXP-001.summary.md").exists())
            self.assertIn("ingested", run("experiments.py", "status", root).stdout)

    def test_demo_site_naming_and_build(self):
        with tempfile.TemporaryDirectory() as d:
            root = new_project(Path(d), "SiteTest")
            (root / "demo" / "samples.json").write_text(json.dumps({"tagline": "Accepted at EMNLP", "summary": "x"}))
            r = run("build_demo_site.py", root)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("EMNLP", r.stdout + r.stderr)
            (root / "demo" / "samples.json").write_text(json.dumps({"tagline": "Plain words.", "summary": "A <b>test</b>.",
                                                                    "results": {"metric": "MOS", "rows": [{"name": "A", "value": 3.0}]}}))
            r = run("build_demo_site.py", root)
            self.assertEqual(r.returncode, 0, r.stderr)
            page = (root / "demo" / "site" / "index.html").read_text()
            self.assertIn("<title>SiteTest</title>", page)
            self.assertNotIn("<b>test</b>", page.split('id="data"')[0])
            (root / "demo" / "samples.json").write_text(json.dumps({"audio_samples": [{"title": "t", "systems": [{"name": "A", "file": "../../etc/passwd"}]}]}))
            self.assertNotEqual(run("build_demo_site.py", root).returncode, 0)  # path traversal refused


class DashboardTests(unittest.TestCase):
    def test_state_and_route_safety(self):
        import dashboard
        with tempfile.TemporaryDirectory() as d:
            root = new_project(Path(d))
            st = dashboard.compute(root)
            self.assertEqual(len(st["stages"]), 10)
            self.assertEqual(sum(1 for s in st["stages"] if s["active"]), 1)
            self.assertEqual(st["sections"][0]["name"], "Abstract")
            from _serve import safe_join
            (root / "paper" / "figures").mkdir(exist_ok=True)
            (root / "paper" / "figures" / "a.png").write_bytes(b"x")
            self.assertIsNotNone(safe_join(root, "paper/figures/a.png"))
            self.assertIsNone(safe_join(root, "../../etc/passwd"))
            self.assertIsNone(safe_join(root / "paper", "../project_meta.json"))


class SkillFormatTests(unittest.TestCase):
    def test_front_matter_meets_agent_skills_limits(self):
        import re
        head = (SKILL / "SKILL.md").read_text(encoding="utf-8").split("---")[1]
        name = re.search(r"^name:\s*(\S+)\s*$", head, re.M).group(1)
        desc = re.search(r"^description:\s*(.+)$", head, re.M).group(1)
        self.assertRegex(name, r"^[a-z0-9]+(-[a-z0-9]+)*$")
        self.assertLessEqual(len(name), 64)
        self.assertLessEqual(len(desc), 1024)   # Codex enforces this and may skip a longer description
        self.assertTrue(desc.startswith("Scientific and academic paper writing, drafting, structuring, and adversarial review"))  # the original text is intact
        self.assertTrue((SKILL / "agents" / "openai.yaml").is_file())


class PackagingTests(unittest.TestCase):
    def test_lean_zip_excludes_corpus(self):
        import re
        import zipfile
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "x.zip"
            r = run("package_skill.py", "--out", out)
            self.assertEqual(r.returncode, 0, r.stderr)
            names = zipfile.ZipFile(out).namelist()
            skill_id = re.search(r"^name:\s*(\S+)", (SKILL / "SKILL.md").read_text(encoding="utf-8").split("---")[1], re.M).group(1)
            self.assertIn(f"{skill_id}/SKILL.md", names)
            self.assertFalse(any("/Authors/" in n or "/parsed_md/" in n or "__pycache__" in n for n in names))


def skill_copy(tmp: Path) -> Path:
    """A throwaway copy of the skill (no PDF corpus) so tests never touch the real skill state."""
    import shutil
    dst = tmp / "skill"
    shutil.copytree(SKILL, dst, ignore=shutil.ignore_patterns("Authors", "parsed_md", "analysis_cache", "dist", "__pycache__", ".git", ".paper"))
    return dst


def prof(skill: Path, *args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(skill / "scripts" / "skill_profile.py"), *map(str, args)], capture_output=True, text=True)


class VenueTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((SKILL / "templates" / "venues.json").read_text(encoding="utf-8"))
        self.man = json.loads((SKILL / "templates" / "template_manifest.json").read_text(encoding="utf-8"))

    def test_data_integrity(self):
        ids = [i["id"] for i in self.data["universal"]]
        self.assertEqual(len(ids), len(set(ids)))
        kinds = {"manual", "file_ready", "regex", "regex_all", "forbidden", "claims", "citations", "statement", "captions", "build", "anon", "abstract_words", "meta", "no_marker"}
        for vid, v in self.data["venues"].items():
            self.assertTrue((SKILL / "templates" / v["family"] / "main.tex").is_file(), f"wrapper for {vid}")
            vids = [i["id"] for i in v["items"]]
            self.assertEqual(len(vids), len(set(vids)), vid)
            for it in v["items"] + self.data["universal"]:
                self.assertIn(it["auto"]["kind"], kinds, it["id"])
        self.assertEqual(len(self.data["venues"]["neurips"]["items"]), 16)  # the 16-item NeurIPS checklist
        for fam in ("acl", "ieee", "icml", "iclr", "colm", "neurips", "aaai"):
            self.assertIn(fam, self.man["families"])

    def test_every_wrapper_inputs_resolve_and_no_placeholder(self):
        import re
        sections = {p.stem for p in (SKILL / "templates" / "sections").glob("*.tex")}
        statements = {"credit_statement", "license_statement", "acknowledgments", "ai_disclosure"}
        for fam in ("acl", "ieee", "icml", "iclr", "colm", "neurips", "aaai", "generic"):
            main = re.sub(r"(?<!\\)%.*", "", (SKILL / "templates" / fam / "main.tex").read_text(encoding="utf-8"))
            for target in re.findall(r"\\input\{([^}]+)\}", main):
                name = Path(target).stem
                self.assertTrue(name in sections or name in statements or name in ("math_commands", "checklist"), f"{fam}: {target}")  # these two are optional files from the official kit
            self.assertEqual(main.count("{") - main.count("}") - main.count("\\{") + main.count("\\}"), 0, f"{fam} braces")
            self.assertIn("@@TITLE@@", main)

    def test_init_every_venue_and_checks(self):
        with tempfile.TemporaryDirectory() as d:
            for v in ("acl", "ieee", "neurips", "icml", "iclr", "aaai", "colm", "emnlp", "icassp"):
                root = Path(d) / v
                r = run("paper_init.py", "init", root, "--name", "Demo", "--venue", v)
                self.assertEqual(r.returncode, 0, v + r.stderr)
                self.assertNotIn("@@", (root / "paper" / "main.tex").read_text())
                c = run("venue_check.py", root, "--quiet")
                self.assertIn("SUMMARY", c.stdout)
                self.assertEqual(c.returncode, 1, f"{v}: an empty skeleton must not pass its blocking items")

    def test_checklist_needs_real_evidence_not_placeholders(self):
        with tempfile.TemporaryDirectory() as d:
            root = new_project(Path(d), "Chk", "neurips")
            out = run("venue_check.py", root).stdout
            self.assertRegex(out, r"FAIL\s+\S?\s*Compute resources: worker types")  # placeholder text is not evidence
            (root / "paper" / "sections" / "04_setup.tex").write_text("We use 4 GPUs for 12 hours per run; hyperparameters and the train split are listed; 3 seeds with standard deviation.\n")
            (root / "paper" / "sections" / "05_results.tex").write_text("Means and standard deviation over 3 seeds.\n")
            out = run("venue_check.py", root).stdout
            self.assertRegex(out, r"OK\s+\S?\s*Compute resources: worker types")
            self.assertRegex(out, r"OK\s+\S?\s*Experimental details")
            self.assertIn("N/A", out)  # human-subjects items are not applicable by default

    def test_aaai_forbidden_scan(self):
        with tempfile.TemporaryDirectory() as d:
            root = new_project(Path(d), "A", "aaai")
            self.assertRegex(run("venue_check.py", root).stdout, r"OK\s+\*\s+No forbidden packages")
            main = root / "paper" / "main.tex"
            main.write_text(main.read_text().replace("\\usepackage{multirow}", "\\usepackage{multirow}\n\\usepackage{hyperref}\n\\bibliographystyle{aaai2026}"))
            out = run("venue_check.py", root).stdout
            self.assertRegex(out, r"FAIL\s+\*\s+No forbidden packages")
            self.assertRegex(out, r"FAIL\s+\*\s+No .bibliographystyle")

    def test_anonymity_switch_is_checked(self):
        with tempfile.TemporaryDirectory() as d:
            root = new_project(Path(d), "Anon", "icml")
            self.assertRegex(run("venue_check.py", root).stdout, r"OK\s+\*\s+Review version is anonymous")
            main = root / "paper" / "main.tex"
            main.write_text(main.read_text().replace("\\camerareadyfalse", "\\camerareadytrue"))
            self.assertRegex(run("venue_check.py", root).stdout, r"FAIL\s+\*\s+Review version is anonymous")


class FetchTemplateTests(unittest.TestCase):
    def test_hash_and_local_import(self):
        import fetch_template as ft
        import hashlib
        with self.assertRaises(SystemExit):
            ft.check(b"tampered", "0" * 64, "x.sty", False)
        ft.check(b"ok", hashlib.sha256(b"ok").hexdigest(), "x.sty", False)
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "kit" / "sub"
            src.mkdir(parents=True)
            (src / "a.sty").write_bytes(b"official")
            fam = {"files": {"a.sty": hashlib.sha256(b"official").hexdigest()}, "install_as": {"a.sty": "b.sty"}, "local_hint": "hint"}
            self.assertEqual(ft.from_local(fam, Path(d) / "kit", False), {"b.sty": b"official"})  # found recursively, installed under its new name
            (src / "a.sty").write_bytes(b"modified")
            with self.assertRaises(SystemExit):
                ft.from_local(fam, Path(d) / "kit", False)
            with self.assertRaises(SystemExit):
                ft.from_local(fam, Path(d) / "empty", False)  # not found
            dest = Path(d) / "out"
            dest.mkdir()
            with self.assertRaises(SystemExit):
                ft.write_safe(dest, "../escape.sty", b"x", True)  # path traversal refused


class SkillProfileTests(unittest.TestCase):
    def test_use_only_and_cascade(self):
        with tempfile.TemporaryDirectory() as d:
            sk = skill_copy(Path(d))
            self.assertEqual(prof(sk, "use", "ieee-lab").returncode, 0)
            act = (sk / "skills" / "ACTIVE.md").read_text()
            enabled, disabled = act.split("## Disabled")[0], act.split("## Disabled")[1].split("## Always on")[0]
            self.assertIn("**author_ieee_lab**", enabled)
            self.assertNotIn("**author_clinical**", enabled)
            self.assertIn("author_clinical", disabled)
            prof(sk, "use", "full")
            prof(sk, "only", "author_clinical")
            act = (sk / "skills" / "ACTIVE.md").read_text()
            self.assertIn("**author_clinical** (author overlay (precedence 1))", act)
            self.assertIn("- **author_ieee_lab** (author)", act)  # listed as disabled
            self.assertEqual(prof(sk, "disable", "speech_base").returncode, 0)
            st = json.loads((sk / "skills" / "ACTIVE_PROFILE.json").read_text())
            self.assertNotIn("author_clinical", st["enabled"])  # requires speech_base, so it went off too
            self.assertEqual(prof(sk, "doctor").returncode, 0)
            self.assertNotEqual(prof(sk, "enable", "nonsense").returncode, 0)

    def test_merge_sheet_finds_shared_interlock(self):
        with tempfile.TemporaryDirectory() as d:
            sk = skill_copy(Path(d))
            r = prof(sk, "merge", "author_ieee_lab", "author_clinical", "--name", "t")
            self.assertEqual(r.returncode, 0, r.stderr)
            sheet = (sk / "skills" / "merged" / "t.md").read_text()
            self.assertIn("RULE_SEC_03_CONTRIB", sheet)
            self.assertIn("RULE_IEEELAB_03_CONTRIBUTION_FORMAT", sheet)
            self.assertIn("RULE_CLINICAL_01_HYPOTHESIS_DRIVEN_PROPOSAL", sheet)
            self.assertIn("Precedence: author_ieee_lab > author_clinical", sheet)
            self.assertIn("Precedence: author_ieee_lab > author_clinical", (sk / "skills" / "ACTIVE.md").read_text())
            self.assertNotEqual(prof(sk, "merge", "author_ieee_lab").returncode, 0)          # needs two or more authors
            self.assertNotEqual(prof(sk, "merge", "author_ieee_lab", "domain_tts").returncode, 0)  # authors only

    def test_register_unregister_safety(self):
        with tempfile.TemporaryDirectory() as d:
            sk = skill_copy(Path(d))
            f = sk / "skills" / "authors" / "my_lab.md"
            f.write_text("# SKILL_ID: AUTHOR::MY_LAB\n\nRULE_MYLAB_01_A:\n  STRUCTURE: One.\n  INTERLOCK: RULE_MYLAB_01_A <-> DEFAULT::RULE_SEC_03_CONTRIB\n")
            self.assertEqual(prof(sk, "register", "my_lab", "--kind", "author", "--file", "skills/authors/my_lab.md", "--requires", "speech_base").returncode, 0)
            self.assertIn("my_lab", json.loads((sk / "skills" / "ACTIVE_PROFILE.json").read_text())["enabled"])
            self.assertNotEqual(prof(sk, "unregister", "speech_base").returncode, 0)  # others require it
            self.assertNotEqual(prof(sk, "unregister", "my_lab", "--delete-files").returncode, 0)  # needs --yes
            self.assertIn("my_lab", (sk / "skills" / "registry.json").read_text())  # the refusal changed nothing
            self.assertTrue(f.exists())
            self.assertEqual(prof(sk, "unregister", "my_lab", "--delete-files", "--yes").returncode, 0)
            self.assertFalse(f.exists())
            self.assertNotIn("my_lab", (sk / "skills" / "registry.json").read_text())

    def test_export_and_prune(self):
        with tempfile.TemporaryDirectory() as d:
            sk = skill_copy(Path(d))
            prof(sk, "use", "clinical")
            out = Path(d) / "exported"
            r = prof(sk, "export", out)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertFalse((out / "skills" / "authors" / "ieee_lab_style.md").exists())
            self.assertTrue((out / "skills" / "authors" / "clinical_multimodal_style.md").exists())
            skill_md = (out / "SKILL.md").read_text()
            self.assertNotIn("ieee_lab_style", skill_md)
            self.assertNotIn("01_ieee_lab_rules", skill_md)
            self.assertIn("paper_story", skill_md)  # core content survives the filter
            router = (out / "skills" / "SKILL_ROUTER.md").read_text()
            self.assertNotIn("IEEE_LAB_STYLE", router)
            self.assertIn("CLINICAL_MULTIMODAL_STYLE", router)
            self.assertEqual(json.loads((out / "skills" / "ACTIVE_PROFILE.json").read_text())["profile"], "clinical")
            ex = subprocess.run([sys.executable, str(out / "scripts" / "skill_profile.py"), "doctor"], capture_output=True, text=True)
            self.assertEqual(ex.returncode, 0, ex.stdout)
            self.assertNotEqual(prof(sk, "export", out).returncode, 0)  # refuses a non-empty target
            before = (sk / "references" / "01_ieee_lab_rules.md").exists()
            dry = prof(sk, "prune")
            self.assertIn("dry run", dry.stdout)
            self.assertEqual((sk / "references" / "01_ieee_lab_rules.md").exists(), before)  # nothing deleted without --apply
            prof(sk, "prune", "--apply")
            self.assertFalse((sk / "references" / "01_ieee_lab_rules.md").exists())
            self.assertTrue((sk / "references" / "11_workflow_journeys_and_artifacts.md").exists())  # core is never pruned

    def test_provenance_survives_without_pdfs(self):
        with tempfile.TemporaryDirectory() as d:
            sk = skill_copy(Path(d))
            # the public skill ships no corpus; a user who adds papers gets a manifest, so build a tiny synthetic one
            (sk / "manifest.json").write_text(json.dumps({"files": {"example_style/paper_one.pdf": {"author_slug": "ieee_lab_style", "sha256": "a" * 64, "domains": ["tts_and_vocoders"]}}}))
            self.assertEqual(prof(sk, "provenance", "--write").returncode, 0)
            prov = json.loads((sk / "skills" / "PROVENANCE.json").read_text())
            self.assertEqual(len(prov["sources"]["author_ieee_lab"]["papers"]), 1)
            self.assertTrue(all(len(p["sha256"]) == 64 for p in prov["sources"]["author_ieee_lab"]["papers"]))
            self.assertFalse((sk / "Authors").exists())  # the PDFs are not needed for any of this
if __name__ == "__main__":
    unittest.main()
