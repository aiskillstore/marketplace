"""Exercise the zero-dependency screenshot CLI against a real local browser."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "shoot.mjs"
NODE = shutil.which("node")


def find_browser():
    candidates = [os.environ.get("CHROME_PATH")]
    if sys.platform == "darwin":
        candidates += [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        ]
    elif sys.platform == "win32":
        for variable in ("PROGRAMFILES", "PROGRAMFILES(X86)"):
            root = os.environ.get(variable)
            if root:
                candidates += [
                    str(Path(root) / "Google/Chrome/Application/chrome.exe"),
                    str(Path(root) / "Microsoft/Edge/Application/msedge.exe"),
                ]
    candidates += [shutil.which(name) for name in (
        "google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge",
    )]
    return next((path for path in candidates if path and Path(path).is_file()), None)


@unittest.skipUnless(NODE, "Node is not installed")
class ShootCLITests(unittest.TestCase):
    def test_help(self):
        result = subprocess.run([NODE, str(SCRIPT), "--help"], cwd=ROOT,
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("用法", result.stdout)

    def test_missing_target(self):
        result = subprocess.run([NODE, str(SCRIPT)], cwd=ROOT,
                                capture_output=True, text=True, timeout=10)
        self.assertNotEqual(result.returncode, 0)

    def test_unknown_option(self):
        help_result = subprocess.run([NODE, str(SCRIPT), "--help"], cwd=ROOT,
                                     capture_output=True, text=True, timeout=10)
        self.assertEqual(help_result.returncode, 0, help_result.stderr)
        options = [line.split()[0] for line in help_result.stdout.splitlines()
                   if line.startswith("  --")]
        for args in (("--xxx",), ("--xxx", "value")):
            with self.subTest(args=args):
                result = subprocess.run([NODE, str(SCRIPT), *args], cwd=ROOT,
                                        capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, 1)
                self.assertEqual(result.stderr.splitlines(), [
                    "shoot：不认识的选项 --xxx",
                    "可用选项：" + " ".join(options),
                ])
                self.assertEqual(result.stdout, "")

    def test_missing_option_value(self):
        for option in ("--out", "--size", "--states", "--param", "--zoom", "--steps", "--hold", "--wait"):
            for following in ((), ("--force",)):
                with self.subTest(option=option, following=following):
                    result = subprocess.run([NODE, str(SCRIPT), option, *following], cwd=ROOT,
                                            capture_output=True, text=True, timeout=10)
                    self.assertEqual(result.returncode, 1)
                    self.assertEqual(result.stderr, f"shoot：{option} 需要一个值\n")

    def test_force_is_ignored(self):
        result = subprocess.run([NODE, str(SCRIPT), "--force"], cwd=ROOT,
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr, "shoot：缺少页面地址或文件。\n")


class ShootBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not NODE:
            raise unittest.SkipTest("Node 22+ is not installed")
        version = subprocess.run([NODE, "--version"], capture_output=True, text=True, timeout=10)
        if version.returncode or int(version.stdout.strip().lstrip("v").split(".")[0]) < 22:
            raise unittest.SkipTest("Node 22+ is required")
        cls.browser = find_browser()
        if not cls.browser:
            raise unittest.SkipTest("Chrome, Chromium or Edge is not installed")

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="oil-shoot-test-")
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)
        self.page = self.folder / "sample.html"
        self.page.write_text('''<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" href="data:,">
<style>
body { margin: 0; padding: 24px; background: #fde68a; font: 20px sans-serif; }
body[data-state="b"] { background: #bfdbfe; }
button { padding: 16px; }
</style></head><body><h1 id="state"></h1><button id="go">切换</button>
<script>
const state = new URLSearchParams(location.search).get('state') || 'a';
function show(value) {
  document.body.dataset.state = value;
  document.querySelector('#state').textContent = value;
}
show(state);
document.querySelector('#go').onclick = () => show(document.body.dataset.state === 'a' ? 'b' : 'a');
</script></body></html>''', encoding="utf-8")
        self.env = dict(os.environ, CHROME_PATH=self.browser)
        self.profile_root = self.folder / "profiles"
        self.profile_root.mkdir()
        self.env.update(TMPDIR=str(self.profile_root), TMP=str(self.profile_root), TEMP=str(self.profile_root))

    def shoot(self, output, *args):
        result = subprocess.run([NODE, str(SCRIPT), str(self.page), "--out", str(output), *args],
                                cwd=ROOT, env=self.env, capture_output=True, text=True, timeout=90)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def assert_artifacts(self, output, names):
        for name in names:
            with self.subTest(file=name):
                artifact = output / name
                self.assertTrue(artifact.is_file(), name)
                self.assertGreater(artifact.stat().st_size, 0, name)
                if artifact.suffix == ".png":
                    self.assertTrue(artifact.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"), name)
                elif artifact.suffix == ".jpg":
                    self.assertTrue(artifact.read_bytes().startswith(b"\xff\xd8"), name)

    def test_states_masks_and_sheets(self):
        output = self.folder / "shots"
        self.shoot(output, "--states", "a,b", "--mask", "--sheet")
        self.assert_artifacts(output, (
            "a.png", "b.png", "a-masked.png", "b-masked.png",
            "sheet.png", "sheet-masked.png", "report.json",
        ))
        report = json.loads((output / "report.json").read_text(encoding="utf-8"))
        self.assertEqual([entry["state"] for entry in report], ["a", "b"])
        self.assertEqual([entry["issues"] for entry in report], [[], []])
        self.assertNotEqual((output / "a.png").read_bytes(), (output / "b.png").read_bytes())
        self.assertNotEqual((output / "a.png").read_bytes(), (output / "a-masked.png").read_bytes())
        self.assertEqual(list(self.profile_root.glob("oil-shoot-*")), [], "Temporary browser profiles leaked")

    def test_force_overwrites_existing_output(self):
        output = self.folder / "shots"
        output.mkdir()
        (output / "page.png").write_bytes(b"old screenshot")
        self.shoot(output, "--force")
        self.assert_artifacts(output, ("page.png", "report.json"))

    def test_record_steps(self):
        output = self.folder / "record's output"
        result = self.shoot(output, "--record", "--steps", "click #go; wait 300", "--hold", "300")
        self.assert_artifacts(output, ("motion-start.jpg", "motion-mid.jpg", "motion-end.jpg"))
        self.assertNotEqual((output / "motion-start.jpg").read_bytes(), (output / "motion-end.jpg").read_bytes())
        report = json.loads((output / "report.json").read_text(encoding="utf-8"))
        self.assertEqual([entry["issues"] for entry in report], [[]])
        self.assertEqual(list(self.profile_root.glob("oil-shoot-*")), [], "Temporary browser profiles leaked")
        if shutil.which("ffmpeg"):
            self.assertTrue((output / "record.mp4").is_file(), result.stdout + result.stderr)
            self.assert_artifacts(output, ("record.mp4",))

    def test_mask_preserves_current_color_icons(self):
        self.page.write_text('''<!doctype html><html><head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" href="data:,"></head><body>
<svg width="80" height="80" viewBox="0 0 80 80" style="color:#16a34a">
<circle cx="40" cy="40" r="32" fill="currentColor" /></svg>
</body></html>''', encoding="utf-8")
        output = self.folder / "icons"
        self.shoot(output, "--mask")
        self.assertEqual((output / "page.png").read_bytes(), (output / "page-masked.png").read_bytes(),
                         "Masking text must preserve icons using currentColor")

    def test_record_preserves_final_hold(self):
        if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
            self.skipTest("ffmpeg and ffprobe are required to check recording duration")
        output = self.folder / "hold"
        self.shoot(output, "--record", "--steps", "click #go; wait 300", "--hold", "2000")
        result = subprocess.run([
            "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json",
            str(output / "record.mp4"),
        ], capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertGreaterEqual(float(json.loads(result.stdout)["format"]["duration"]), 2.0)

    def test_reports_page_problems(self):
        self.page.write_text(self.page.read_text(encoding="utf-8").replace("</body>", '''
<div style="width:2000px">溢出</div><img src="missing.png">
<script>console.error('shoot-test-error'); throw new Error('shoot-test-exception');</script>
</body>'''), encoding="utf-8")
        for args in ((), ("--record", "--hold", "300")):
            with self.subTest(record=bool(args)):
                output = self.folder / ("problem-record" if args else "problem-shots")
                self.shoot(output, "--size", "1280x900", *args)
                report = json.loads((output / "report.json").read_text(encoding="utf-8"))
                issues = "\n".join(report[0]["issues"])
                for expected in ("shoot-test-error", "shoot-test-exception", "横向溢出", "图片没加载出来"):
                    self.assertIn(expected, issues)


if __name__ == "__main__":
    unittest.main()
