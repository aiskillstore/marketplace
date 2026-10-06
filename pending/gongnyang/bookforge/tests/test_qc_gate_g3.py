import json
import math
import unittest

from scripts import qc_gate


class FakePage:
    def __init__(self, blocks):
        self.rect = qc_gate.fitz.Rect(0, 0, 566.91796875, 750.9598999023438)
        self.blocks = blocks

    def get_text(self, _mode):
        return {"blocks": self.blocks}


class FakeDocument:
    def __init__(self, *pages):
        self.pages = pages
        self.page_count = len(pages)

    def __getitem__(self, index):
        return self.pages[index]


class ClassifyBboxTests(unittest.TestCase):
    def setUp(self):
        self.clip = qc_gate.fitz.Rect(-qc_gate.TOL, -qc_gate.TOL,
                                      566.91796875 + qc_gate.TOL,
                                      750.9598999023438 + qc_gate.TOL)

    def assert_status(self, expected, bbox):
        status, _ = qc_gate.classify_bbox(bbox, self.clip)
        self.assertEqual(expected, status)

    def test_valid_bbox_classification(self):
        cases = (
            ("inside", [566.9999389648438, 0.0, 566.91796875, 300.742431640625]),
            ("inside", [0.0, 750.9598999023438, 566.91796875, 300.742431640625]),
            ("inside", [10, 20, 100, 200]),
            ("overflow", [-10, 10, 100, 100]),
            ("empty", [10, 20, 10, 200]),
            ("empty", [10, 20, 100, 20]),
        )
        for expected, bbox in cases:
            with self.subTest(expected=expected, bbox=bbox):
                self.assert_status(expected, bbox)

    def test_invalid_bbox_classification(self):
        cases = (
            [1, 2, 3],
            [1, 2, "3", 4],
            [1, 2, math.nan, 4],
            [1, 2, math.inf, 4],
            [1, 2, -math.inf, 4],
        )
        for bbox in cases:
            with self.subTest(bbox=bbox):
                self.assert_status("invalid", bbox)


class G3AggregationTests(unittest.TestCase):
    def test_invalid_fails_empty_does_not_and_legacy_fields_remain(self):
        empty_report = qc_gate.g3_check(FakeDocument(FakePage([
            {"type": 1, "bbox": [10, 20, 10, 200]},
        ])))
        self.assertTrue(empty_report["ok"])
        self.assertEqual(1, empty_report["empty_count"])

        doc = FakeDocument(FakePage([
            {"type": 1, "bbox": [1, 2, math.nan, 4]},
        ]))

        report = qc_gate.g3_check(doc)

        self.assertEqual([], report["overflows"])
        self.assertEqual(0, report["count"])
        self.assertFalse(report["ok"])
        self.assertEqual(0, report["empty_count"])
        self.assertEqual(1, report["invalid_count"])
        self.assertEqual("image", report["invalid_bboxes"][0]["kind"])
        json.dumps(report, allow_nan=False)

    def test_text_and_image_overflows_are_both_reported(self):
        report = qc_gate.g3_check(FakeDocument(FakePage([
            {"type": 0, "bbox": [-10, 10, 100, 100]},
            {"type": 1, "bbox": [10, 10, 600, 100]},
        ])))

        self.assertEqual(2, report["count"])
        self.assertEqual(["text", "image"], [item["kind"] for item in report["overflows"]])
        self.assertFalse(report["ok"])


if __name__ == "__main__":
    unittest.main()
