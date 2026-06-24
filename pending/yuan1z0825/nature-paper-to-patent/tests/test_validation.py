import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_patent_draft", ROOT / "scripts" / "validate_patent_draft.py"
)
VALIDATOR = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = VALIDATOR
SPEC.loader.exec_module(VALIDATOR)


def valid_draft():
    return {
        "title": "一种工业图像缺陷检测方法",
        "metadata": {"draft_status": "供复核"},
        "source_analysis": {
            "contains_core_formulas": True,
            "contains_methodology_figures": False,
        },
        "source_map": [
            {"id": "P001", "type": "paper-text", "locator": "第3页", "summary": "流程"},
            {"id": "E001", "type": "equation", "locator": "第4页公式1", "summary": "融合"},
        ],
        "terminology_ledger": [
            {
                "concept": "融合特征",
                "canonical_zh": "融合特征",
                "source_terms": ["fused feature"],
                "forbidden_aliases": [],
            }
        ],
        "formula_inventory": [
            {
                "source_id": "E001",
                "source_number": "(1)",
                "technical_role": "融合不同尺度特征",
                "disposition": "specification-equation-1",
            }
        ],
        "figure_inventory": [
            {
                "source_id": "P001",
                "source_number": "方法章节",
                "type": "flowchart",
                "disposition": "redraw-as-figure-1",
            }
        ],
        "evidence_ledger": [
            {
                "id": "EV1",
                "feature": "多尺度特征融合",
                "source_ids": ["P001", "E001"],
                "support_status": "explicit",
            }
        ],
        "claims": [
            {
                "number": 1,
                "text": "一种工业图像缺陷检测方法，其特征在于，包括：S1，获取工业图像；S2，对工业图像进行多尺度特征融合；S3，根据融合特征输出缺陷检测结果。",
            }
        ],
        "claim_feature_map": [
            {"claim_number": 1, "feature": "多尺度特征融合", "evidence_ids": ["EV1"]}
        ],
        "abstract_figure_number": 1,
        "figures": [
            {
                "number": 1,
                "title": "方法流程图",
                "type": "flowchart",
                "orientation": "vertical",
                "claim_number": 1,
                "complete_claim_flow": True,
                "source_ids": ["P001"],
                "nodes": [
                    {"id": "S1", "label": "S1：获取工业图像", "claim_step": "S1"},
                    {
                        "id": "S2",
                        "label": "S2：进行多尺度特征融合",
                        "claim_step": "S2",
                    },
                    {
                        "id": "S3",
                        "label": "S3：输出缺陷检测结果",
                        "claim_step": "S3",
                    },
                ],
                "edges": [{"from": "S1", "to": "S2"}, {"from": "S2", "to": "S3"}],
            }
        ],
        "specification": {
            "technical_field": ["本发明涉及工业视觉检测领域。"],
            "background": ["现有方法对小缺陷表征不足。"],
            "invention_content": {
                "problem": ["提高小缺陷检测能力。"],
                "solution": ["采用多尺度特征融合。"],
                "beneficial_effects": ["保留不同尺度的缺陷信息。"],
            },
            "figure_descriptions": ["图1为方法流程图。"],
            "equations": [
                {
                    "number": 1,
                    "source_ids": ["E001"],
                    "latex": "F=F_1+F_2",
                    "expression": "F=F1+F2",
                    "symbols": [
                        {"symbol": "F", "meaning": "融合特征"},
                        {"symbol": "F_1", "meaning": "第一尺度特征"},
                    ],
                    "technical_role": "融合不同尺度特征",
                    "description": "其中，F表示融合特征，F1和F2表示不同尺度特征。",
                }
            ],
            "embodiments": [{"heading": "实施例1", "paragraphs": ["执行上述步骤。"]}],
        },
        "abstract": "本发明公开一种工业图像缺陷检测方法，通过多尺度特征融合输出缺陷检测结果。",
        "quality_assessment": {
            "status": "review-draft",
            "scores": {
                "evidence_support": {"score": 4, "evidence": "特征均有来源。"},
                "claim_architecture": {"score": 4, "evidence": "技术链闭合。"},
                "terminology_consistency": {"score": 4, "evidence": "术语一致。"},
                "enablement_detail": {"score": 3, "evidence": "已说明主要步骤。"},
                "technical_effect_reasoning": {"score": 3, "evidence": "效果关联手段。"},
                "formula_coverage": {"score": 4, "evidence": "核心公式已收录。"},
                "figure_alignment": {"score": 4, "evidence": "附图与步骤一致。"},
            }
        },
    }


class DraftValidationTests(unittest.TestCase):
    def test_valid_draft_passes(self):
        self.assertEqual([], VALIDATOR.validate(valid_draft()))

    def test_unmapped_claim_fails(self):
        draft = valid_draft()
        draft["claim_feature_map"] = []
        codes = {item.code for item in VALIDATOR.validate(draft)}
        self.assertIn("CLAIM_NOT_MAPPED", codes)

    def test_missing_core_equation_fails(self):
        draft = valid_draft()
        draft["specification"]["equations"] = []
        codes = {item.code for item in VALIDATOR.validate(draft)}
        self.assertIn("MISSING_CORE_EQUATIONS", codes)


if __name__ == "__main__":
    unittest.main()
