"""Unit tests for camera-prompt-quickcheck linter."""

import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from lint_camera_prompt import lint_camera_prompt  # noqa: E402


class CameraPromptLinterTests(unittest.TestCase):
    def test_vague_zoom_prompt_scores_low(self) -> None:
        res = lint_camera_prompt("Cinematic epic shot, zoom in on hero face.")
        codes = {f["code"] for f in res["findings"]}
        self.assertIn("C02", codes)
        self.assertIn("C04", codes)
        self.assertIn("C05", codes)
        self.assertIn("C06", codes)
        self.assertLess(res["score"], 60)
        self.assertEqual(res["status"], "HIGH_RISK")

    def test_dolly_zoom_collision_detected(self) -> None:
        res = lint_camera_prompt("Slow dolly in and zoom out around the tower.")
        codes = {f["code"] for f in res["findings"]}
        self.assertIn("C03", codes)

    def test_well_formed_prompt_passes(self) -> None:
        prompt = (
            "Starting from a medium wide shot at eye level, slow steady dolly in toward "
            "the watchmaker while keeping his hands and horizon level, gently decelerating "
            "and settling into a sharp close-up on the golden gear."
        )
        res = lint_camera_prompt(prompt)
        self.assertGreaterEqual(res["score"], 85)
        self.assertEqual(res["status"], "PASS")
        self.assertEqual(res["findings"], [])


if __name__ == "__main__":
    unittest.main()
