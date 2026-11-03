# scripts/tests/test_quality_gate.py
import importlib.util, os, shutil, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
REFERENCES = os.path.join(ROOT, "references")
sys.path.insert(0, REFERENCES)
import quality_inspect  # noqa: E402

INSPECT = os.path.join(REFERENCES, "quality_inspect.py")
VALIDATOR = os.path.join(REFERENCES, "tikz-validator.py")
PDF_CHECKER = os.path.join(REFERENCES, "pdf-overlap-checker.py")
FIXTURE = os.path.join(ROOT, "tests", "fixtures", "title_band_collision.tex")
HAS_PDF_DEPS = all(importlib.util.find_spec(m) for m in ("fitz", "pdfplumber"))


def run(script, *args):
    return subprocess.run([sys.executable, script] + list(args),
                          capture_output=True, text=True, cwd=ROOT)


class QualityGateCase(unittest.TestCase):
    def test_validator_is_not_shadowed_by_inspect_module(self):
        # regression: references/inspect.py used to shadow the stdlib module
        r = run(VALIDATOR, FIXTURE)
        self.assertNotIn("AttributeError", r.stderr)
        self.assertNotIn("Traceback", r.stderr)
        self.assertEqual(r.returncode, 1)
        self.assertIn("Collision", r.stdout)

    def test_validator_emits_json_block(self):
        r = run(VALIDATOR, FIXTURE)
        self.assertIn("--- JSON ---", r.stdout)
        self.assertIn('"check": "tikz-validator"', r.stdout)

    def test_inspector_reports_fixture_collision(self):
        r = run(INSPECT, FIXTURE)
        self.assertEqual(r.returncode, 1)
        self.assertIn("Inspection: 1 warnings", r.stdout)
        self.assertIn("'Policy starts'", r.stdout)
        self.assertNotIn("FAILED SENSORS", r.stdout)

    def test_crashing_sensor_reports_fail(self):
        tmp = tempfile.mkdtemp()
        try:
            with open(os.path.join(tmp, "boom.py"), "w") as f:
                f.write("import sys\nprint('boom')\nsys.exit(3)\n")
            old = quality_inspect.SCRIPT_DIR
            quality_inspect.SCRIPT_DIR = tmp
            try:
                out = quality_inspect.run_sensor("boom.py")
            finally:
                quality_inspect.SCRIPT_DIR = old
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["level"], "FAIL")
        self.assertIn("exit 3", out[0]["message"])

    def test_clean_sensor_returns_no_findings(self):
        tmp = tempfile.mkdtemp()
        try:
            with open(os.path.join(tmp, "quiet.py"), "w") as f:
                f.write("print('PASS')\n")
            old = quality_inspect.SCRIPT_DIR
            quality_inspect.SCRIPT_DIR = tmp
            try:
                out = quality_inspect.run_sensor("quiet.py")
            finally:
                quality_inspect.SCRIPT_DIR = old
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        self.assertEqual(out, [])

    def test_pdf_checker_is_py39_safe(self):
        # regression: "BBox | None" needs postponed evaluation on Python <= 3.9
        with open(PDF_CHECKER, encoding="utf-8") as f:
            src = f.read()
        uses_pep604 = "| None" in src or "None |" in src
        has_future = "from __future__ import annotations" in src
        self.assertFalse(uses_pep604 and not has_future,
                         "PEP 604 annotations require 'from __future__ import annotations' before 3.10")

    def test_pdf_checker_imports_cleanly(self):
        code = "import runpy; runpy.run_path(%r, run_name='probe')" % PDF_CHECKER
        r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(r.returncode, 0, r.stderr)

    @unittest.skipUnless(HAS_PDF_DEPS, "needs pymupdf + pdfplumber")
    def test_inspector_with_tex_and_pdf(self):
        import fitz
        tmp = tempfile.mkdtemp()
        try:
            pdf = os.path.join(tmp, "probe.pdf")
            doc = fitz.open()
            page = doc.new_page()
            page.insert_text((72, 72), "clean page")
            doc.save(pdf)
            doc.close()
            r = run(INSPECT, FIXTURE, pdf)
            self.assertNotIn("FAILED SENSORS", r.stdout)
            self.assertNotIn('"level": "FAIL"', r.stdout)
            self.assertIn("Inspection:", r.stdout)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

if __name__ == "__main__":
    unittest.main()
