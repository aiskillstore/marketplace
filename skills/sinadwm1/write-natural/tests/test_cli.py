"""Exercise the actual scripts as offline, read-only command-line tools."""

import ast
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


class CommandLineContract(unittest.TestCase):
    def setUp(self):
        self.sandbox = tempfile.TemporaryDirectory()
        self.addCleanup(self.sandbox.cleanup)
        self.root = Path(self.sandbox.name)
        self.original = self.write("original.txt", "The dose may be ۱۰ mg.")
        self.revised = self.write("revised.txt", "The dose is 15 mg.")

    def write(self, name, text):
        path = self.root / name
        path.write_text(text, encoding="utf-8")
        return path

    def run_tool(self, tool, *args, data=None, cwd=None, script_dir=None):
        # No network service, package install or shell participates in a run.
        return subprocess.run([sys.executable, str((script_dir or SCRIPTS) / tool), *map(str, args)],
                              input=data, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              cwd=cwd or self.root, timeout=10)

    def parse(self, result, status=0):
        self.assertEqual(result.returncode, status, result.stderr.decode("utf-8", "replace"))
        self.assertEqual(result.stderr, b"")
        return json.loads(result.stdout.decode("utf-8"))

    def assert_usage_error(self, result):
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, b"")
        self.assertIn(b"error:", result.stderr)
        self.assertNotIn(b"Traceback", result.stderr)

    def test_audit_utf8_stdin_json_and_explicit_options(self):
        report = self.parse(self.run_tool("audit_text.py", "-", "--json", "--lang", "mixed", "--profile", "academic",
                                         data="این روش may help.\n".encode("utf-8")))
        self.assertEqual((report["lang"], report["profile"]), ("mixed", "academic"))
        self.assertEqual(report["findings"], [])

    def test_stdin_bom_and_empty_input(self):
        for data in (b"", b"\xef\xbb\xbfClear prose."):
            with self.subTest(data=data):
                report = self.parse(self.run_tool("audit_text.py", "-", "--json", "--strict", data=data))
                self.assertEqual(report["findings"], [])

    def test_audit_strict_is_opt_in_and_json_stays_parseable(self):
        path = self.write("review.txt", "It is important to note that the trial ended.")
        ordinary = self.parse(self.run_tool("audit_text.py", path, "--json"))
        strict = self.parse(self.run_tool("audit_text.py", path, "--json", "--strict"), status=1)
        self.assertEqual(ordinary, strict)
        self.assertEqual([x["code"] for x in strict["findings"]], ["LEXICAL_REVIEW"])

    def test_comparison_json_and_strict_have_advisory_scope(self):
        ordinary = self.parse(self.run_tool("compare_revisions.py", self.original, self.revised, "--json"))
        strict = self.parse(self.run_tool("compare_revisions.py", self.original, self.revised, "--json", "--strict"), status=1)
        self.assertEqual(ordinary, strict)
        self.assertIn("UNCERTAINTY_REMOVAL_REVIEW", [x["code"] for x in strict["findings"]])
        self.assertTrue(all(x["severity"] == "advisory" for x in strict["findings"]))

    def test_comparison_negative_control_does_not_fail_strict(self):
        equivalent = self.write("equivalent.txt", "The dose may be 10 milligrams.")
        report = self.parse(self.run_tool("compare_revisions.py", self.original, equivalent, "--json", "--strict"))
        self.assertEqual(report["findings"], [])

    def test_both_empty_comparison_inputs(self):
        first = self.write("empty1.txt", "")
        second = self.write("empty2.txt", "")
        report = self.parse(self.run_tool("compare_revisions.py", first, second, "--json", "--strict"))
        self.assertEqual(report["findings"], [])

    def test_real_cli_invariants_find_lost_term_and_exact_string(self):
        contract = self.write("invariants.json", json.dumps({"protected_strings": ["may"], "required_terms": ["RNA"]}))
        report = self.parse(self.run_tool("compare_revisions.py", self.original, self.revised,
                                         "--invariants", contract, "--json", "--strict"), status=1)
        found = [x["code"] for x in report["findings"]]
        self.assertIn("INVARIANT_PROTECTED_REVIEW", found)
        self.assertIn("INVARIANT_REQUIRED_REVIEW", found)

    def test_invalid_invariants_are_usage_errors(self):
        values = ["{", "[]", '{"required_term": ["RNA"]}', '{"required_terms": "RNA"}',
                  '{"required_terms": [3]}', '{"required_terms": [""]}',
                  '{"required_terms": ["  "]}', '{"required_terms": ["RNA", "RNA"]}',
                  '{"required_terms": [], "required_terms": ["RNA"]}']
        for index, value in enumerate(values):
            with self.subTest(value=value):
                contract = self.write("invalid{}.json".format(index), value)
                self.assert_usage_error(self.run_tool("compare_revisions.py", self.original, self.revised,
                                                     "--invariants", contract, "--json"))

    def test_missing_files_and_invalid_utf8_fail_cleanly(self):
        missing = self.root / "missing.txt"
        invalid = self.root / "invalid.txt"
        invalid.write_bytes(b"\xff\xfe\x80")
        calls = [("audit_text.py", missing), ("audit_text.py", invalid),
                 ("compare_revisions.py", missing, self.revised),
                 ("compare_revisions.py", self.original, invalid),
                 ("compare_revisions.py", self.original, self.revised, "--invariants", missing),
                 ("compare_revisions.py", self.original, self.revised, "--invariants", invalid)]
        for args in calls:
            with self.subTest(args=args):
                self.assert_usage_error(self.run_tool(*args, "--json"))
        self.assert_usage_error(self.run_tool("audit_text.py", "-", "--json", data=b"\xff"))

    def test_unknown_options_invalid_choices_and_comparison_stdin(self):
        calls = [("audit_text.py", self.original, "--lang", "fr"),
                 ("audit_text.py", self.original, "--profile", "poetry"),
                 ("audit_text.py", self.original, "--unknown"),
                 ("compare_revisions.py", "-", self.revised),
                 ("compare_revisions.py", self.original, self.revised, "--invariants", "-"),
                 ("compare_revisions.py", self.original, self.revised, "--unknown")]
        for args in calls:
            with self.subTest(args=args):
                self.assert_usage_error(self.run_tool(*args))

    def test_human_output_scope_and_locations(self):
        path = self.write("review.txt", "سرآغاز\nاين كلمه است.")
        result = self.run_tool("audit_text.py", path, "--lang", "fa")
        self.assertEqual(result.returncode, 0)
        output = result.stdout.decode("utf-8")
        self.assertIn("2:2 [FA_ARABIC_LETTER]", output)
        self.assertIn("no authorship score or factual verification", output)

    def test_read_only_bytes_paths_and_no_runtime_bytecode(self):
        isolated = self.root / "isolated-scripts"
        shutil.copytree(SCRIPTS, isolated, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        contract = self.write("invariants.json", '{"required_terms": ["dose"]}')

        def snapshot():
            return {str(path.relative_to(self.root)): hashlib.sha256(path.read_bytes()).hexdigest()
                    for path in self.root.rglob("*") if path.is_file()}

        before = snapshot()
        first = self.run_tool("audit_text.py", self.original, "--json", script_dir=isolated)
        second = self.run_tool("compare_revisions.py", self.original, self.revised, "--json",
                               "--invariants", contract, script_dir=isolated)
        self.parse(first)
        self.parse(second)
        self.assertEqual(snapshot(), before)
        self.assertEqual(list(self.root.rglob("__pycache__")), [])

    def test_python_39_syntax_and_no_network_or_external_imports(self):
        # A grammar check is not a claim of execution on every Python version.
        allowed = {"argparse", "bisect", "collections", "dataclasses", "decimal", "json", "re",
                   "statistics", "sys", "text_common"}
        for path in SCRIPTS.glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), feature_version=(3, 9))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    modules = [alias.name.split(".")[0] for alias in node.names]
                elif isinstance(node, ast.ImportFrom):
                    modules = [node.module.split(".")[0]]
                else:
                    continue
                self.assertTrue(set(modules) <= allowed, (path, modules))


if __name__ == "__main__":
    unittest.main()
