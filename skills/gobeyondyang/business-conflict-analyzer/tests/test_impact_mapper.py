#!/usr/bin/env python3
"""
impact_mapper unit tests.

Usage: python tests/test_impact_mapper.py
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from impact_mapper import (
    identify_layer, match_pattern, map_impact,
    ConsumerImpact, ImpactMatrix, load_common_patterns,
    find_references,
)
from lang import Translator


def test_identify_layer_controller():
    """Controller path → layer.api"""
    kw, layer = identify_layer("src/main/java/com/example/controller/UserController.java")
    assert layer == "layer.api", f"Controller should map to layer.api: {layer}"
    print(f"  [OK] test_identify_layer_controller: {layer}")


def test_identify_layer_dto():
    """DTO path → layer.data"""
    kw, layer = identify_layer("src/main/java/com/example/dto/UserDTO.java")
    assert layer == "layer.data", f"DTO should map to layer.data: {layer}"
    print(f"  [OK] test_identify_layer_dto: {layer}")


def test_identify_layer_feign():
    """Feign path → layer.rpc"""
    kw, layer = identify_layer("src/main/java/com/example/feign/OrderFeignClient.java")
    assert layer == "layer.rpc", f"Feign should map to layer.rpc: {layer}"
    print(f"  [OK] test_identify_layer_feign: {layer}")


def test_identify_layer_service():
    """Service path → layer.business"""
    kw, layer = identify_layer("src/main/java/com/example/service/UserService.java")
    assert layer == "layer.business", f"Service should map to layer.business: {layer}"
    print(f"  [OK] test_identify_layer_service: {layer}")


def test_identify_layer_unknown():
    """Unknown path returns layer.other (or matches config keyword)."""
    kw, layer = identify_layer("src/main/java/com/example/config/SecurityConfig.java")
    assert layer in ("layer.other", "layer.config"), f"Config file should map: {layer}"
    print(f"  [OK] test_identify_layer_unknown: {layer}")


def test_identify_layer_windows_path():
    """Windows-style paths also work."""
    kw, layer = identify_layer("src\\main\\java\\com\\example\\controller\\TestController.java")
    assert layer == "layer.api", f"Windows path should map: {layer}"
    print(f"  [OK] test_identify_layer_windows_path")


def test_identify_layer_python_views():
    """Python views path → layer.api"""
    kw, layer = identify_layer("myapp/views/user_views.py")
    assert layer == "layer.api", f"Python views should map: {layer}"
    print(f"  [OK] test_identify_layer_python_views: {layer}")


def test_identify_layer_python_serializers():
    """Python serializers → layer.data"""
    kw, layer = identify_layer("myapp/serializers/user_serializer.py")
    assert layer == "layer.data", f"Python serializers should map: {layer}"
    print(f"  [OK] test_identify_layer_python_serializers: {layer}")


def test_identify_layer_typescript_interfaces():
    """TypeScript interfaces → layer.type_contract"""
    kw, layer = identify_layer("src/interfaces/user.interface.ts")
    assert "layer.type_contract" in layer, f"TS interfaces should map: {layer}"
    print(f"  [OK] test_identify_layer_typescript_interfaces: {layer}")


def test_identify_layer_go_handler():
    """Go handler → layer.handler"""
    kw, layer = identify_layer("internal/handler/user_handler.go")
    assert layer == "layer.handler", f"Go handler should map: {layer}"
    print(f"  [OK] test_identify_layer_go_handler: {layer}")


def test_identify_layer_react_components():
    """React components → layer.frontend_component"""
    kw, layer = identify_layer("frontend/src/components/UserProfile.tsx")
    assert layer == "layer.frontend_component", f"React components should map: {layer}"
    print(f"  [OK] test_identify_layer_react_components: {layer}")


def test_identify_layer_django_migrations():
    """Django migrations → layer.data_migration"""
    kw, layer = identify_layer("myapp/migrations/0002_add_email.py")
    assert layer == "layer.data_migration", f"Django migrations should map: {layer}"
    print(f"  [OK] test_identify_layer_django_migrations: {layer}")


def test_load_common_patterns_structure():
    """Pattern library loads with correct field structure."""
    patterns = load_common_patterns(
        str(Path(__file__).parent.parent / "references" / "common_patterns.md")
    )
    assert len(patterns) >= 15, f"Expected ≥15 patterns, got {len(patterns)}"
    for p in patterns:
        assert "name" in p, f"Pattern missing name: {p}"
        assert "trigger" in p, f"Pattern missing trigger: {p.get('name')}"
        assert "impact" in p, f"Pattern missing impact: {p.get('name')}"
        assert "impact_level" in p, f"Pattern missing impact_level: {p.get('name')}"
    print(f"  [OK] test_load_common_patterns_structure: {len(patterns)} patterns")


def test_load_common_patterns_scope_cost():
    """Pattern library includes scope and cost fields."""
    patterns = load_common_patterns(
        str(Path(__file__).parent.parent / "references" / "common_patterns.md")
    )
    has_scope = any(p.get("scope") for p in patterns)
    has_cost = any(p.get("cost") for p in patterns)
    assert has_scope, "At least one pattern should have scope"
    assert has_cost, "At least one pattern should have cost"
    print(f"  [OK] test_load_common_patterns_scope_cost")


def test_map_impact_dto_field_delete():
    """DTO field delete → BREAKING."""
    manifest = {
        "summary": "UserDTO field changes",
        "risk_level": "P0",
        "changes": [{
            "file": "src/main/java/com/example/dto/UserDTO.java",
            "extension": "java",
            "type": "M",
            "risk_level": "P0",
            "symbols": ["field_del:mobile"],
            "details": "java:+1/-1",
        }]
    }
    matrix = map_impact(manifest)
    assert len(matrix.consumer_impacts) == 1
    assert matrix.consumer_impacts[0].impact == "BREAKING"
    assert matrix.overall_impact == "CRITICAL"
    assert matrix.summary == "UserDTO field changes"
    print(f"  [OK] test_map_impact_dto_field_delete: {matrix.overall_impact}")


def test_map_impact_sql_ddl():
    """DDL change triggers data migration flag."""
    manifest = {
        "summary": "DDL changes",
        "risk_level": "P0",
        "changes": [{
            "file": "src/main/resources/db/V2__alter_user.sql",
            "extension": "sql",
            "type": "M",
            "risk_level": "P0",
            "symbols": ["ddl:ALTER TABLE user DROP COLUMN mobile"],
            "details": "sql:1 DDL",
        }]
    }
    matrix = map_impact(manifest)
    assert matrix.data_migration.required, "DDL should flag data migration"
    assert matrix.api_compatibility.version_required, "DDL should flag version compatibility"
    print(f"  [OK] test_map_impact_sql_ddl: migration={matrix.data_migration.required}")


def test_map_impact_internal_refactor():
    """Internal refactor → COMPATIBLE."""
    manifest = {
        "summary": "Internal refactor",
        "risk_level": "P2",
        "changes": [{
            "file": "src/main/java/com/example/util/StringUtils.java",
            "extension": "java",
            "type": "M",
            "risk_level": "P2",
            "symbols": [],
            "details": "java:+5/-3",
        }]
    }
    matrix = map_impact(manifest)
    assert matrix.overall_impact == "MINOR"
    print(f"  [OK] test_map_impact_internal_refactor: {matrix.overall_impact}")


def test_map_impact_empty():
    """Empty changes do not crash."""
    manifest = {"summary": "", "risk_level": "P2", "changes": []}
    matrix = map_impact(manifest)
    assert len(matrix.consumer_impacts) == 0
    assert matrix.overall_impact == "MINOR"
    print(f"  [OK] test_map_impact_empty")


# i18n test: translated across languages

def test_map_impact_i18n_en():
    """map_impact with English translator produces English layer names."""
    manifest = {
        "summary": "API change",
        "risk_level": "P1",
        "changes": [{
            "file": "src/main/java/com/example/controller/UserController.java",
            "extension": "java",
            "type": "M",
            "risk_level": "P1",
            "symbols": ["field_add:email"],
            "details": "java:+1/-0",
        }]
    }
    t = Translator("en")
    matrix = map_impact(manifest, t)
    detail = matrix.consumer_impacts[0].detail
    assert "API layer" in detail, f"English layer name expected: {detail}"
    assert "field_add" in detail or "New field" in detail, f"Symbol translation expected: {detail}"
    print(f"  [OK] test_map_impact_i18n_en")


def test_map_impact_i18n_zh():
    """map_impact with Chinese translator produces Chinese layer names."""
    manifest = {
        "summary": "API 变更",
        "risk_level": "P1",
        "changes": [{
            "file": "src/main/java/com/example/controller/UserController.java",
            "extension": "java",
            "type": "M",
            "risk_level": "P1",
            "symbols": ["field_add:email"],
            "details": "java:+1/-0",
        }]
    }
    t = Translator("zh")
    matrix = map_impact(manifest, t)
    detail = matrix.consumer_impacts[0].detail
    assert "API 层" in detail, f"Chinese layer name expected: {detail}"
    print(f"  [OK] test_map_impact_i18n_zh")


def test_find_references():
    """find_references returns matching source files."""
    import tempfile, os
    with tempfile.TemporaryDirectory() as tmp:
        # Create a small "project" with a reference to search for
        os.makedirs(f"{tmp}/src", exist_ok=True)
        with open(f"{tmp}/src/Service.java", "w") as f:
            f.write("class Service { UserDTO user; }")
        with open(f"{tmp}/src/Other.java", "w") as f:
            f.write("class Other { String mobile; }")

        refs = find_references("UserDTO", project_root=tmp)
        assert any("Service.java" in r for r in refs), f"Should find Service.java: {refs}"
        assert not any("Other.java" in r for r in refs), f"Should NOT find Other.java: {refs}"
    print(f"  [OK] test_find_references: {len(refs)} reference(s)")


def test_find_references_annotation():
    """find_references handles @-prefixed symbols (regression)."""
    import tempfile, os
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(f"{tmp}/src", exist_ok=True)
        with open(f"{tmp}/src/MyDTO.java", "w") as f:
            f.write("import jakarta.validation.constraints.NotNull;\n")
            f.write("class MyDTO { @NotNull String name; }")

        refs = find_references("@NotNull", project_root=tmp)
        # @NotNull search should find the file (regression: \b@ fails)
        assert any("MyDTO.java" in r for r in refs), \
            f"find_references(@NotNull) should find file: {refs}"
    print(f"  [OK] test_find_references_annotation: {len(refs)} reference(s)")


if __name__ == "__main__":
    print(f"\n{'='*50}")
    print(f"  impact_mapper tests")
    print(f"{'='*50}\n")

    tests = [
        test_identify_layer_controller,
        test_identify_layer_dto,
        test_identify_layer_feign,
        test_identify_layer_service,
        test_identify_layer_unknown,
        test_identify_layer_windows_path,
        test_identify_layer_python_views,
        test_identify_layer_python_serializers,
        test_identify_layer_typescript_interfaces,
        test_identify_layer_go_handler,
        test_identify_layer_react_components,
        test_identify_layer_django_migrations,
        test_load_common_patterns_structure,
        test_load_common_patterns_scope_cost,
        test_map_impact_dto_field_delete,
        test_map_impact_sql_ddl,
        test_map_impact_internal_refactor,
        test_map_impact_empty,
        test_map_impact_i18n_en,
        test_map_impact_i18n_zh,
        test_find_references,
        test_find_references_annotation,
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
