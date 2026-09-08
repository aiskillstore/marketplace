"""User-facing tests for the dedupe inspection command."""
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = SKILL_DIR / "scripts" / "dedupe.py"


def run_request(request):
    with tempfile.TemporaryDirectory() as tmp:
        path = pathlib.Path(tmp) / "request.json"
        path.write_text(json.dumps(request), encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "inspect", "--request", str(path)],
            capture_output=True, text=True, timeout=30)
    return result


class TestListAdapter(unittest.TestCase):
    def test_exact_duplicates_keep_first_and_do_not_mutate(self):
        request = {"adapter": "list", "mode": "exact", "items": ["a", "a", "b"]}
        result = run_request(request)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertFalse(report["mutated"])
        self.assertEqual(report["canonical_indices"], [0, 2])
        self.assertEqual(report["groups"][0]["member_indices"], [0, 1])
        self.assertEqual(report["duplicate_count"], 1)

    def test_normalized_scalar_list_keeps_type_boundaries(self):
        request = {"adapter": "list", "mode": "normalized",
                   "items": [" A ", "a", 1, 1.0],
                   "normalization": {"casefold": True, "whitespace": "collapse"}}
        result = run_request(request)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["groups"][0]["member_indices"], [0, 1])
        self.assertEqual(report["canonical_indices"], [0, 2, 3])


class TestTextAdapter(unittest.TestCase):
    def test_normalized_text_exposes_assumptions(self):
        request = {
            "adapter": "text", "mode": "normalized",
            "items": [" Café ", "cafe\u0301", "tea"],
            "normalization": {"unicode": "NFKC", "casefold": True,
                              "whitespace": "collapse"}}
        result = run_request(request)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["groups"][0]["member_indices"], [0, 1])
        self.assertEqual(report["normalization"], request["normalization"])
        self.assertEqual(report["duplicate_count"], 1)

    def test_similarity_candidates_do_not_collapse_items(self):
        request = {
            "adapter": "text", "mode": "similarity",
            "items": ["alpha beta", "alpha beta!", "far away"],
            "normalization": {"casefold": True, "whitespace": "collapse"},
            "similarity_threshold": 0.9}
        result = run_request(request)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["duplicate_count"], 0)
        self.assertEqual(report["canonical_indices"], [0, 1, 2])
        self.assertEqual(report["similarity_candidates"][0]["indices"], [0, 1])
        self.assertGreaterEqual(report["similarity_candidates"][0]["score"], 0.9)


class TestRecordAdapter(unittest.TestCase):
    def test_key_match_reports_non_key_conflicts(self):
        request = {
            "adapter": "record", "mode": "normalized",
            "items": [
                {"id": 1, "email": " A@X.COM ", "name": "A"},
                {"id": 2, "email": "a@x.com", "name": "Alice"}],
            "key_fields": ["email"],
            "normalization": {"casefold": True, "whitespace": "collapse"}}
        result = run_request(request)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["groups"][0]["member_indices"], [0, 1])
        self.assertEqual(report["groups"][0]["conflict_fields"], ["id", "name"])
        self.assertFalse(report["mutated"])


class TestUrlAdapter(unittest.TestCase):
    def test_canonical_url_uses_only_declared_policy(self):
        request = {
            "adapter": "url", "mode": "normalized",
            "items": ["HTTPS://Example.COM:443/a?b=2&a=1#top",
                      "https://example.com/a?a=1&b=2"],
            "url_policy": {"strip_fragment": True, "sort_query": True,
                           "drop_query_params": []}}
        result = run_request(request)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["groups"][0]["member_indices"], [0, 1])
        self.assertEqual(report["url_policy"], request["url_policy"])
        self.assertEqual(report["duplicate_count"], 1)


class TestFileAdapter(unittest.TestCase):
    def test_exact_file_content_keeps_path_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            paths = [root / "a.txt", root / "b.txt", root / "c.txt"]
            paths[0].write_text("same", encoding="utf-8")
            paths[1].write_text("same", encoding="utf-8")
            paths[2].write_text("different", encoding="utf-8")
            request = {"adapter": "file", "mode": "exact",
                       "items": [str(path) for path in paths]}
            result = run_request(request)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["groups"][0]["member_indices"], [0, 1])
        self.assertEqual(report["provenance"][0]["path"], str(paths[0]))
        self.assertEqual(report["provenance"][0]["sha256"],
                         report["provenance"][1]["sha256"])

    def test_symlink_is_unresolved_without_follow_authority(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            target = root / "target.txt"
            link = root / "link.txt"
            target.write_text("same", encoding="utf-8")
            link.symlink_to(target)
            request = {"adapter": "file", "mode": "exact",
                       "items": [str(target), str(link)]}
            result = run_request(request)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["unresolved"][0]["index"], 1)
        self.assertIn("follow_symlinks", report["unresolved"][0]["reason"])
        self.assertEqual(report["canonical_indices"], [0])

    def test_normalized_text_files_require_explicit_policy(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            paths = [root / "a.txt", root / "b.txt"]
            paths[0].write_text(" A \r\n", encoding="utf-8")
            paths[1].write_text("a\n", encoding="utf-8")
            request = {"adapter": "file", "mode": "normalized",
                       "items": [str(path) for path in paths], "encoding": "utf-8",
                       "normalization": {"casefold": True, "whitespace": "collapse"}}
            result = run_request(request)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["groups"][0]["member_indices"], [0, 1])
        self.assertEqual(report["normalization"], request["normalization"])


class TestSkillAdapter(unittest.TestCase):
    def test_exact_skill_packets_include_support_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            roots = [pathlib.Path(tmp) / "one", pathlib.Path(tmp) / "two"]
            for root in roots:
                (root / "references").mkdir(parents=True)
                (root / "SKILL.md").write_text(
                    "---\nname: sample\ndescription: Use when testing.\nversion: 1.0.0\n---\n# Sample\n",
                    encoding="utf-8")
                (root / "references" / "rule.md").write_text("same\n", encoding="utf-8")
            request = {"adapter": "skill", "mode": "exact",
                       "items": [str(root) for root in roots]}
            result = run_request(request)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["groups"][0]["member_indices"], [0, 1])
        self.assertEqual(report["provenance"][0]["name"], "sample")
        self.assertEqual(report["provenance"][0]["packet_sha256"],
                         report["provenance"][1]["packet_sha256"])

    def test_same_name_different_packets_are_conflicts(self):
        with tempfile.TemporaryDirectory() as tmp:
            roots = [pathlib.Path(tmp) / "one", pathlib.Path(tmp) / "two"]
            for index, root in enumerate(roots):
                root.mkdir()
                (root / "SKILL.md").write_text(
                    f"---\nname: sample\ndescription: Use when testing.\n---\n# Version {index}\n",
                    encoding="utf-8")
            request = {"adapter": "skill", "mode": "exact",
                       "items": [str(root) for root in roots]}
            result = run_request(request)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["groups"], [])
        self.assertEqual(report["identity_conflicts"][0]["indices"], [0, 1])
        self.assertEqual(report["identity_conflicts"][0]["name"], "sample")


if __name__ == "__main__":
    unittest.main()
