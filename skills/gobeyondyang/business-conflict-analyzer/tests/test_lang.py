#!/usr/bin/env python3
"""
lang.py unit tests — Translator core functionality.

Usage: python tests/test_lang.py
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from lang import Translator, STRINGS, LANGUAGES


def test_translator_default_valid():
    """Default language is a valid language (depends on system locale)."""
    t = Translator()
    assert t.lang in ("en", "zh"), f"Default should be 'en' or 'zh', got '{t.lang}'"
    print(f"  [OK] test_translator_default_valid: lang={t.lang}")


def test_translator_explicit():
    """Explicit language setting works."""
    t_en = Translator("en")
    assert t_en.lang == "en"
    t_zh = Translator("zh")
    assert t_zh.lang == "zh"
    print(f"  [OK] test_translator_explicit")


def test_translator_env_var(monkeypatch=None):
    """LANG env var is detected."""
    # Save original and set
    old_lang = os.environ.get("LANG", "")
    os.environ["LANG"] = "zh_CN.UTF-8"
    try:
        t = Translator()
        assert t.lang == "zh", f"LANG=zh_CN should give 'zh', got '{t.lang}'"
    finally:
        if old_lang:
            os.environ["LANG"] = old_lang
        else:
            del os.environ["LANG"]
    print(f"  [OK] test_translator_env_var")


def test_translator_env_var_en():
    """LANG=en is detected as English."""
    old_lang = os.environ.get("LANG", "")
    os.environ["LANG"] = "en_US.UTF-8"
    try:
        t = Translator()
        assert t.lang == "en", f"LANG=en_US should give 'en', got '{t.lang}'"
    finally:
        if old_lang:
            os.environ["LANG"] = old_lang
        else:
            del os.environ["LANG"]
    print(f"  [OK] test_translator_env_var_en")


def test_t_basic_lookup():
    """t() returns the correct string for a key."""
    t = Translator("en")
    result = t.t("diff.summary.no_changes")
    assert result == "No uncommitted changes found", f"Unexpected: {result}"
    print(f"  [OK] test_t_basic_lookup: {result}")


def test_t_basic_lookup_zh():
    """t() returns Chinese string for zh."""
    t = Translator("zh")
    result = t.t("diff.summary.no_changes")
    assert result == "无未提交变更", f"Unexpected: {result}"
    print(f"  [OK] test_t_basic_lookup_zh: {result}")


def test_t_with_format():
    """t() supports format arguments."""
    t = Translator("en")
    result = t.t("diff.summary.p0", count=3)
    assert "3" in result, f"Should contain count: {result}"
    print(f"  [OK] test_t_with_format: {result}")


def test_t_with_format_zh():
    """t() with format works in Chinese too."""
    t = Translator("zh")
    result = t.t("diff.summary.p0", count=3)
    assert "3" in result, f"Should contain count: {result}"
    print(f"  [OK] test_t_with_format_zh: {result}")


def test_t_missing_key():
    """Missing key returns the key itself."""
    t = Translator("en")
    result = t.t("nonexistent.key.404")
    assert result == "nonexistent.key.404", f"Missing key should return key: {result}"
    print(f"  [OK] test_t_missing_key")


def test_tech_to_business_symbol_en():
    """tech_to_business translates field_add symbol in English."""
    t = Translator("en")
    result = t.tech_to_business("field_add:phone")
    assert "New field" in result or "phone" in result, f"Unexpected: {result}"
    print(f"  [OK] test_tech_to_business_symbol_en: {result}")


def test_tech_to_business_symbol_zh():
    """tech_to_business translates field_del symbol in Chinese."""
    t = Translator("zh")
    result = t.tech_to_business("field_del:mobile")
    assert "删除" in result, f"Should contain '删除': {result}"
    print(f"  [OK] test_tech_to_business_symbol_zh: {result}")


def test_tech_to_business_detail_en():
    """tech_to_business translates java detail in English."""
    t = Translator("en")
    result = t.tech_to_business("java:+3/-2")
    assert "Java" in result, f"Should contain 'Java': {result}"
    print(f"  [OK] test_tech_to_business_detail_en: {result}")


def test_risk_display():
    """risk_display returns correct label/note tuples."""
    t = Translator("en")
    critical_label, critical_note = t.risk_display("CRITICAL")
    assert "High" in critical_label or "CRITICAL" in critical_label.upper(), f"Unexpected label: {critical_label}"
    assert "compilation" in critical_note.lower() or "downstream" in critical_note.lower(), f"Unexpected note: {critical_note}"

    info_label, info_note = t.risk_display("INFO")
    assert "Info" in info_label or "INFO" in info_label.upper(), f"Unexpected label: {info_label}"
    print(f"  [OK] test_risk_display")


def test_all_languages_have_keys():
    """EN and ZH key sets must be identical (bidirectional check)."""
    en_keys = set(STRINGS["en"].keys())
    zh_keys = set(STRINGS["zh"].keys())
    extra_zh = zh_keys - en_keys
    missing_zh = en_keys - zh_keys
    assert not extra_zh, f"ZH has keys not in EN: {extra_zh}"
    assert not missing_zh, f"EN has keys missing in ZH: {missing_zh}"
    assert en_keys == zh_keys, f"Key sets differ: EN={len(en_keys)} ZH={len(zh_keys)}"
    print(f"  [OK] test_all_languages_have_keys: {len(en_keys)} EN / {len(zh_keys)} ZH keys (identical)")


if __name__ == "__main__":
    print(f"\n{'='*50}")
    print(f"  lang.py tests")
    print(f"{'='*50}\n")

    tests = [
        test_translator_default_valid,
        test_translator_explicit,
        test_translator_env_var,
        test_translator_env_var_en,
        test_t_basic_lookup,
        test_t_basic_lookup_zh,
        test_t_with_format,
        test_t_with_format_zh,
        test_t_missing_key,
        test_tech_to_business_symbol_en,
        test_tech_to_business_symbol_zh,
        test_tech_to_business_detail_en,
        test_risk_display,
        test_all_languages_have_keys,
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
