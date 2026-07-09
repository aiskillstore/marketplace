#!/usr/bin/env python3
"""
report_generator unit tests.

Usage: python tests/test_report_generator.py
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from report_generator import generate_report
from lang import Translator


# tech_to_business (via Translator)

def test_tech_to_business_field_delete_en():
    """English: field_del translates to 'removed'."""
    t = Translator("en")
    result = t.tech_to_business("field_del:mobile")
    assert "removed" in result or "Field" in result, f"Field delete should translate: {result}"
    print(f"  [OK] test_tech_to_business_field_delete_en: {result}")


def test_tech_to_business_field_delete_zh():
    """Chinese: field_del translates to 删除字段."""
    t = Translator("zh")
    result = t.tech_to_business("field_del:mobile")
    assert "删除字段" in result or "字段" in result, f"Field delete should translate to Chinese: {result}"
    print(f"  [OK] test_tech_to_business_field_delete_zh: {result}")


def test_tech_to_business_ddl_drop_en():
    """English: DDL DROP translates."""
    t = Translator("en")
    result = t.tech_to_business("ddl:ALTER TABLE user DROP COLUMN mobile")
    assert "Database" in result or "DDL" in result, f"DDL should translate: {result}"
    print(f"  [OK] test_tech_to_business_ddl_drop_en: {result}")


def test_tech_to_business_enum():
    """English: enum_add translates."""
    t = Translator("en")
    result = t.tech_to_business("enum_add:REFUNDING")
    assert "enum" in result.lower() or "New" in result, f"Enum add should translate: {result}"
    print(f"  [OK] test_tech_to_business_enum: {result}")


def test_tech_to_business_config():
    """English: config_add translates."""
    t = Translator("en")
    result = t.tech_to_business("config_add:order.timeout")
    assert "config" in result.lower() or "key" in result.lower(), f"Config add should translate: {result}"
    print(f"  [OK] test_tech_to_business_config: {result}")


def test_tech_to_business_java_detail():
    """English: java:+N/-M detail translates."""
    t = Translator("en")
    result = t.tech_to_business("java:+1/-1")
    assert "Java" in result, f"Java detail should translate: {result}"
    print(f"  [OK] test_tech_to_business_java_detail: {result}")


def test_tech_to_business_fallback():
    """No match → returns original text."""
    t = Translator("en")
    result = t.tech_to_business("some completely unrelated text")
    assert result == "some completely unrelated text", f"Fallback should return original: {result}"
    print(f"  [OK] test_tech_to_business_fallback")


# generate_report language-aware tests

def test_generate_report_has_decision_section_en():
    """English report contains Decision section."""
    manifest = {
        "summary": "Test change",
        "risk_level": "P0",
        "changes": [{
            "file": "TestDTO.java",
            "extension": "java",
            "symbols": ["field_del:mobile"],
            "details": "java:+1/-1",
            "risk_level": "P0",
            "type": "M",
        }]
    }
    matrix = {
        "summary": "Test change",
        "overall_impact": "CRITICAL",
        "consumer_impacts": [{"file": "TestDTO.java", "impact": "BREAKING", "detail": "layer.data | java:+1/-1"}],
        "data_migration": {"required": False, "risk": "LOW", "detail": ""},
        "api_compatibility": {"version_required": True, "suggestion": "Upgrade recommended"},
        "frontend_affected": False,
        "recommendation": "Requires confirmation",
    }
    report = generate_report(manifest, matrix, Translator("en"))
    assert "### Decision" in report, "English report should have 'Decision' section"
    assert "Accept" in report, "Decision section should have 'Accept'"
    assert "Reject" in report, "Decision section should have 'Reject'"
    print(f"  [OK] test_generate_report_has_decision_section_en")


def test_generate_report_has_decision_section_zh():
    """Chinese report contains 决策 section."""
    manifest = {
        "summary": "测试变更",
        "risk_level": "P0",
        "changes": [{
            "file": "TestDTO.java",
            "extension": "java",
            "symbols": ["field_del:mobile"],
            "details": "java:+1/-1",
            "risk_level": "P0",
            "type": "M",
        }]
    }
    matrix = {
        "summary": "测试变更",
        "overall_impact": "CRITICAL",
        "consumer_impacts": [{"file": "TestDTO.java", "impact": "BREAKING", "detail": "数据层 | java:+1/-1"}],
        "data_migration": {"required": False, "risk": "LOW", "detail": ""},
        "api_compatibility": {"version_required": True, "suggestion": "建议升级"},
        "frontend_affected": False,
        "recommendation": "需确认",
    }
    report = generate_report(manifest, matrix, Translator("zh"))
    assert "### 决策" in report, "Chinese report should have '决策' section"
    assert "采纳" in report, "Decision section should have '采纳'"
    assert "拒绝" in report, "Decision section should have '拒绝'"
    print(f"  [OK] test_generate_report_has_decision_section_zh")


def test_generate_report_risk_column_en():
    """English report shows risk column."""
    manifest = {
        "summary": "Risk test",
        "risk_level": "P0",
        "changes": [{
            "file": "Test.java",
            "extension": "java",
            "symbols": [],
            "details": "java:+1/-1",
            "risk_level": "P0",
            "type": "M",
        }]
    }
    matrix = {
        "summary": "Risk test",
        "overall_impact": "CRITICAL",
        "consumer_impacts": [{"file": "Test.java", "impact": "BREAKING", "detail": "layer.api | java:+1/-1"}],
        "data_migration": {"required": False, "risk": "LOW", "detail": ""},
        "api_compatibility": {"version_required": False, "suggestion": ""},
        "frontend_affected": False,
        "recommendation": "Requires confirmation",
    }
    report = generate_report(manifest, matrix, Translator("en"))
    assert "P0" in report, "Risk column should show P0"
    print(f"  [OK] test_generate_report_risk_column_en")


def test_generate_report_empty_changes_en():
    """Empty changes do not crash (English)."""
    manifest = {"summary": "", "risk_level": "P2", "changes": []}
    matrix = {
        "summary": "",
        "overall_impact": "INFO",
        "consumer_impacts": [],
        "data_migration": {"required": False, "risk": "LOW", "detail": ""},
        "api_compatibility": {"version_required": False, "suggestion": ""},
        "frontend_affected": False,
        "recommendation": "",
    }
    report = generate_report(manifest, matrix, Translator("en"))
    assert "Business Impact" in report, "Empty report should still have title"
    print(f"  [OK] test_generate_report_empty_changes_en")


def test_generate_report_empty_changes_zh():
    """Empty changes do not crash (Chinese)."""
    manifest = {"summary": "", "risk_level": "P2", "changes": []}
    matrix = {
        "summary": "",
        "overall_impact": "INFO",
        "consumer_impacts": [],
        "data_migration": {"required": False, "risk": "LOW", "detail": ""},
        "api_compatibility": {"version_required": False, "suggestion": ""},
        "frontend_affected": False,
        "recommendation": "",
    }
    report = generate_report(manifest, matrix, Translator("zh"))
    assert "业务影响分析报告" in report, "Empty report should still have Chinese title"
    print(f"  [OK] test_generate_report_empty_changes_zh")


if __name__ == "__main__":
    print(f"\n{'='*50}")
    print(f"  report_generator tests")
    print(f"{'='*50}\n")

    tests = [
        test_tech_to_business_field_delete_en,
        test_tech_to_business_field_delete_zh,
        test_tech_to_business_ddl_drop_en,
        test_tech_to_business_enum,
        test_tech_to_business_config,
        test_tech_to_business_java_detail,
        test_tech_to_business_fallback,
        test_generate_report_has_decision_section_en,
        test_generate_report_has_decision_section_zh,
        test_generate_report_risk_column_en,
        test_generate_report_empty_changes_en,
        test_generate_report_empty_changes_zh,
    ]

    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {t.__name__}: {e}")
            failed += 1

    print(f"\n{'='*50}")
    print(f"  Result: {passed} passed, {failed} failed")
    print(f"{'='*50}\n")
    sys.exit(0 if failed == 0 else 1)
