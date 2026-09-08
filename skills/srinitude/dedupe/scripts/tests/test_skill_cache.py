"""Regression test for transient files in skill packet identity."""
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
        return subprocess.run(
            [sys.executable, str(SCRIPT), "inspect", "--request", str(path)],
            capture_output=True, text=True, check=False)


class TestSkillPacketCaches(unittest.TestCase):
    def test_runtime_bytecode_does_not_change_skill_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            roots = [pathlib.Path(tmp) / "one", pathlib.Path(tmp) / "two"]
            for index, root in enumerate(roots):
                cache = root / "scripts" / "__pycache__"
                cache.mkdir(parents=True)
                (root / "SKILL.md").write_text(
                    "---\nname: sample\ndescription: Use when testing.\n---\n# Sample\n",
                    encoding="utf-8")
                (cache / "runtime.pyc").write_bytes(bytes([index]))
            request = {"adapter": "skill", "mode": "exact",
                       "items": [str(root) for root in roots]}
            result = run_request(request)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["groups"][0]["member_indices"], [0, 1])
        self.assertEqual(report["provenance"][0]["packet_file_count"], 1)


if __name__ == "__main__":
    unittest.main()
