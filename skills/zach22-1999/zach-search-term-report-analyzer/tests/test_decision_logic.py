#!/usr/bin/env python3
"""搜索词分析规则的最小回归测试。"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import analyze_search_term_decisions as analyzer


class DecisionLogicTests(unittest.TestCase):
    def test_infer_competitor_tokens_filters_generic_words(self) -> None:
        df = pd.DataFrame(
            {
                "search_term": [
                    "jbl karaoke machine",
                    "jbl karaoke machine with screen",
                    "professional karaoke machine",
                    "portable karaoke machine",
                ],
                "clicks": [20, 15, 30, 10],
            }
        )
        tokens = analyzer.infer_competitor_tokens(
            df=df,
            own_brand_tokens={"examplebrand"},
            known_brands=[],
            core_tokens={"karaoke"},
            threshold=analyzer.DEFAULT_THRESHOLDS["brand_similarity_threshold"],
            min_frequency=2,
        )
        self.assertIn("jbl", tokens)
        self.assertNotIn("professional", tokens)
        self.assertNotIn("portable", tokens)

    def test_brand_typos_are_classified_as_brand_terms(self) -> None:
        context = analyzer.AnalysisContext(
            brand="ExampleBrand",
            asin="B0PUBLIC01",
            site_code="US",
            report_type="SP",
            target_acos=0.1,
            core_tokens={"karaoke"},
            brand_tokens={"examplebrand"},
            competitor_tokens=set(),
            listing_title="ExampleBrand Smart Karaoke Machine with Lyrics Display",
            listing_context_text=None,
            listing_tokens={"smart", "lyrics", "display"},
            listing_source=None,
        )
        category = analyzer.detect_term_category(
            "examplebrnd karaoke machine",
            context,
            analyzer.DEFAULT_THRESHOLDS["brand_similarity_threshold"],
        )
        self.assertEqual(category, "brand_term")

    def test_high_cvr_small_sample_does_not_scale_up_immediately(self) -> None:
        context = analyzer.AnalysisContext(
            brand="ExampleBrand",
            asin="B0PUBLIC01",
            site_code="US",
            report_type="SP",
            target_acos=0.1,
            core_tokens={"karaoke"},
            brand_tokens={"examplebrand"},
            competitor_tokens=set(),
            listing_title="ExampleBrand Smart Karaoke Machine with Lyrics Display",
            listing_context_text=None,
            listing_tokens={"smart", "lyrics", "display"},
            listing_source=None,
        )
        row = pd.Series(
            {
                "term_category": "attribute_term",
                "trend_flag": "improving",
                "confidence_level": "high",
                "listing_feedback_candidate": True,
                "30d_clicks": 11,
                "30d_orders": 1,
                "30d_spend": 20,
                "30d_cvr": 0.10,
                "30d_acos": 0.08,
            }
        )
        tag, _ = analyzer.choose_decision_tag(
            row,
            context,
            asin_baseline_cvr=0.05,
            asin_baseline_acos=0.12,
            thresholds=analyzer.DEFAULT_THRESHOLDS,
        )
        self.assertIn(tag, {"hold_test", "listing_feedback"})
        self.assertNotEqual(tag, "scale_up")

    def test_zero_order_high_spend_attribute_term_reduces_bid(self) -> None:
        context = analyzer.AnalysisContext(
            brand="ExampleBrand",
            asin="B0PUBLIC01",
            site_code="US",
            report_type="SP",
            target_acos=0.1,
            core_tokens={"karaoke"},
            brand_tokens={"examplebrand"},
            competitor_tokens=set(),
            listing_title="ExampleBrand Smart Karaoke Machine with Lyrics Display",
            listing_context_text=None,
            listing_tokens={"smart", "lyrics", "display"},
            listing_source=None,
        )
        row = pd.Series(
            {
                "term_category": "attribute_term",
                "trend_flag": "insufficient_data",
                "confidence_level": "medium",
                "listing_feedback_candidate": False,
                "30d_clicks": 25,
                "30d_orders": 0,
                "30d_spend": 120,
                "30d_cvr": 0.0,
                "30d_acos": pd.NA,
            }
        )
        tag, _ = analyzer.choose_decision_tag(
            row,
            context,
            asin_baseline_cvr=0.05,
            asin_baseline_acos=0.12,
            thresholds=analyzer.DEFAULT_THRESHOLDS,
        )
        self.assertEqual(tag, "reduce_bid")

    def test_listing_alignment_detects_relevant_tokens(self) -> None:
        context = analyzer.AnalysisContext(
            brand="ExampleBrand",
            asin="B0PUBLIC01",
            site_code="US",
            report_type="SP",
            target_acos=0.1,
            core_tokens={"karaoke"},
            brand_tokens={"examplebrand"},
            competitor_tokens=set(),
            listing_title="ExampleBrand Smart Karaoke Machine with Lyrics Display",
            listing_context_text="Portable party speaker with 2 wireless microphones",
            listing_tokens={"smart", "lyrics", "display", "portable", "party", "wireless", "microphones"},
            listing_source=None,
        )
        score, matched = analyzer.compute_listing_alignment(
            "karaoke machine with lyrics display",
            context,
            analyzer.DEFAULT_THRESHOLDS["brand_similarity_threshold"],
        )
        self.assertGreater(score, 0.4)
        self.assertIn("lyrics", matched)


if __name__ == "__main__":
    unittest.main()
