from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
import zipfile
from datetime import date
from html import escape
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPT_PATH = SKILL_DIR / "scripts" / "analyze_cvr_rank_threshold.py"
spec = importlib.util.spec_from_file_location("analyze_cvr_rank_threshold", SCRIPT_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules["analyze_cvr_rank_threshold"] = module
spec.loader.exec_module(module)


class AnalyzeCvrRankThresholdTests(unittest.TestCase):
    def make_config(self, report_path: Path, output_dir: Path, sif_cache: Path | None = None):
        return module.AnalysisConfig(
            business_report=report_path,
            asin="B0PUBLIC01",
            site="US",
            brand="ExampleBrand",
            launch_date=date(2026, 1, 5),
            core_keywords=["portable espresso maker", "travel coffee maker"],
            sif_cache=sif_cache,
            output_dir=output_dir,
            analysis_date="2026-01-20",
        )

    def test_load_csv_percent_aliases(self):
        sample = SKILL_DIR / "examples" / "business-report-sample.csv"
        with tempfile.TemporaryDirectory() as tmp:
            rows = module.load_business_rows(self.make_config(sample, Path(tmp)))

        self.assertEqual(len(rows), 12)
        self.assertEqual(rows[0].day, date(2026, 1, 1))
        self.assertEqual(rows[0].cvr, 0.045)
        self.assertEqual(rows[4].ad_cvr, 0.031)

    def test_load_xlsx_falls_back_to_minimal_reader(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            report_path = tmp_path / "business.xlsx"
            write_minimal_xlsx(
                report_path,
                [
                    ["日期", "ASIN", "Sessions-Total", "CVR", "广告CVR", "自然CVR", "自然订单量"],
                    ["2026-01-01", "B0PUBLIC01", "100", "2.5%", "3.0%", "2.0%", "2"],
                    ["2026-01-02", "B0PUBLIC01", "110", "2.0", "2.8", "-1.0", "-1"],
                    ["2026-01-03", "B0PUBLIC01", "120", "0.03", "0.035", "2.5%", "3"],
                ],
            )

            rows = module.load_business_rows(self.make_config(report_path, tmp_path))

        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0].cvr, 0.025)
        self.assertEqual(rows[1].cvr, 0.02)
        self.assertEqual(rows[2].cvr, 0.03)
        panel = module.build_panel(rows, {}, ["portable espresso maker"], [], date(2026, 1, 2))
        self.assertTrue(panel[1]["organic_negative_adjustment"])

    def test_sif_normalization_and_rank_event_detection(self):
        raw = {
            "daily": {
                "2026-01-01": {
                    "details": [
                        {
                            "keyword": "portable espresso maker",
                            "scoreRatio": 0.01,
                            "pchangeReason": {"nfInfo": {"change": "10_10"}, "spInfo": {"change": "1_1"}},
                        }
                    ]
                },
                "2026-01-02": {
                    "details": [
                        {
                            "keyword": "portable espresso maker",
                            "scoreRatio": 0.01,
                            "pchangeReason": {"nfInfo": {"change": "10_16"}, "spInfo": {"change": "1_2"}},
                        }
                    ]
                },
            }
        }
        sif_by_day = module.normalize_sif(raw)
        self.assertEqual(sif_by_day[date(2026, 1, 2)]["portable espresso maker"]["nf_rank_before"], 10)
        self.assertEqual(sif_by_day[date(2026, 1, 2)]["portable espresso maker"]["nf_rank_after"], 16)

        rows = [
            module.BusinessRow(day=date(2026, 1, 1), sessions_total=100, cvr=0.04),
            module.BusinessRow(day=date(2026, 1, 2), sessions_total=100, cvr=0.02),
        ]
        panel = module.build_panel(rows, sif_by_day, ["portable espresso maker"], [], date(2026, 1, 2))
        self.assertTrue(panel[1]["event_lag0_rank_volatility"])

    def test_missing_sif_cache_blocks_with_actionable_message(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing.json"
            config = self.make_config(SKILL_DIR / "examples" / "business-report-sample.csv", Path(tmp), missing)
            with self.assertRaisesRegex(RuntimeError, "Missing SIF cache JSON"):
                module.load_sif_cache(config)

    def test_sample_end_to_end_generates_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "outputs"
            config = self.make_config(
                SKILL_DIR / "examples" / "business-report-sample.csv",
                output_dir,
                SKILL_DIR / "examples" / "sif-daily-keyword-sample.json",
            )
            result = module.run_analysis(config)

            self.assertEqual(result["business_rows"], 12)
            self.assertEqual(result["sif_days"], 12)
            self.assertIsNotNone(result["observation"])
            self.assertIsNotNone(result["danger"])
            self.assertTrue(Path(result["paths"]["report"]).exists())


def write_minimal_xlsx(path: Path, rows: list[list[str]]) -> None:
    row_xml = []
    for row_index, row in enumerate(rows, start=1):
        cells = []
        for col_index, value in enumerate(row):
            ref = f"{column_letters(col_index)}{row_index}"
            cells.append(f'<c r="{ref}" t="inlineStr"><is><t>{escape(value)}</t></is></c>')
        row_xml.append(f'<row r="{row_index}">{"".join(cells)}</row>')
    sheet_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<sheetData>{"".join(row_xml)}</sheetData>'
        "</worksheet>"
    )
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("xl/worksheets/sheet1.xml", sheet_xml)


def column_letters(index: int) -> str:
    value = index + 1
    letters = ""
    while value:
        value, remainder = divmod(value - 1, 26)
        letters = chr(ord("A") + remainder) + letters
    return letters


if __name__ == "__main__":
    unittest.main()
