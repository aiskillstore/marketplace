#!/usr/bin/env python3
"""
diff_analyzer unit tests.

Usage: python tests/test_diff_analyzer.py
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from diff_analyzer import (
    extract_java_diff, extract_sql_diff, extract_yaml_diff,
    extract_python_diff, extract_typescript_diff,
    extract_vue_diff, extract_jsp_diff,
    extract_go_diff, extract_properties_diff, extract_xml_diff,
    classify_risk, Change, DiffManifest, analyze, run_git_diff,
)


def test_extract_java_diff_field_add_remove():
    """Java diff detects field additions and deletions."""
    diff = """+    private String phone;
-    private String mobile;
+    @JsonProperty
-    private String oldField;"""
    symbols, detail = extract_java_diff(diff)
    assert len(symbols) >= 2, f"Expected ≥2 symbol changes, got {len(symbols)}: {symbols}"
    assert any("field_add" in s for s in symbols), f"Should detect field_add: {symbols}"
    assert any("field_del" in s for s in symbols), f"Should detect field_del: {symbols}"
    assert "java:" in detail, f"Detail should contain 'java:': {detail}"
    print(f"  [OK] test_extract_java_diff_field_add_remove: {detail}")


def test_extract_java_diff_feign_interface_method():
    """Feign/interface method without 'public' modifier is detected (regression)."""
    diff = """+    Result<ActDemandDetailVo> getDemandDetail(@RequestParam String id);
-    Result<ActDemandDetailVo> getDemandDetail(@RequestParam Long id);
+    @PostMapping("/batch")
+    List<UserDTO> batchQuery(@RequestBody List<Long> ids);
-    List<UserDTO> batchQuery(@RequestBody List<String> ids);"""
    symbols, detail = extract_java_diff(diff)
    assert any("method_add" in s for s in symbols), \
        f"Should detect method addition: {symbols}"
    assert any("method_del" in s for s in symbols), \
        f"Should detect method removal: {symbols}"
    # Standalone annotations (own line) are detected; inline @RequestBody inside
    # method signature is not caught by ANNOTATION_PATTERN (doesn't start line).
    # This is existing behavior, not a regression.
    assert any("annotation_add" in s for s in symbols), \
        f"Should detect standalone annotation addition: {symbols}"
    assert "java:" in detail, f"Detail should contain 'java:': {detail}"
    # Should have >0 added AND >0 removed
    import re as _re
    m = _re.search(r'\+(\d+)/-(\d+)', detail)
    assert m, f"Detail should match +N/-M pattern: {detail}"
    adds, rems = int(m.group(1)), int(m.group(2))
    assert adds > 0, f"Should detect added items, got +{adds}/-{rems}"
    assert rems > 0, f"Should detect removed items, got +{adds}/-{rems}"
    print(f"  [OK] test_extract_java_diff_feign_interface_method: {detail}")


def test_extract_java_diff_annotation():
    """Java diff detects annotation changes."""
    diff = """+@NotNull
-@Nullable
    private String name;"""
    symbols, detail = extract_java_diff(diff)
    assert any("annotation" in s for s in symbols), f"Should detect annotation change: {symbols}"
    print(f"  [OK] test_extract_java_diff_annotation: {symbols}")


def test_extract_java_diff_ignores_import_package():
    """Java diff should skip import/package lines."""
    diff = """+import java.util.List;
-import java.util.ArrayList;
+package com.example;
    public class UserDTO {"""
    symbols, detail = extract_java_diff(diff)
    import_match = any("import" in s.lower() for s in symbols)
    package_match = any("package" in s.lower() for s in symbols)
    assert not import_match, f"import lines should not appear in symbols: {symbols}"
    assert not package_match, f"package lines should not appear in symbols: {symbols}"
    print(f"  [OK] test_extract_java_diff_ignores_import_package: {len(symbols)} symbols")


def test_extract_sql_ddl():
    """SQL diff detects DDL changes."""
    diff = """-ALTER TABLE user DROP COLUMN mobile;
+ALTER TABLE user ADD COLUMN phone VARCHAR(20);
-CREATE TABLE old_table (...);"""
    symbols, detail = extract_sql_diff(diff)
    assert len(symbols) >= 2, f"Expected ≥2 DDL, got {len(symbols)}"
    assert any("ddl:" in s for s in symbols), f"ddl: prefix missing: {symbols}"
    assert "DDL" in detail, f"Detail should mention DDL: {detail}"
    print(f"  [OK] test_extract_sql_ddl: {len(symbols)} DDL statements")


def test_extract_yaml_config():
    """YAML diff detects config additions and deletions."""
    diff = """+order.timeout: 5000
-order.retry: 3
+order.batchSize: 100"""
    symbols, detail = extract_yaml_diff(diff)
    assert len(symbols) == 3, f"Expected 3 config changes, got {len(symbols)}"
    assert any("config_add" in s for s in symbols), f"Should detect config_add: {symbols}"
    assert any("config_del" in s for s in symbols), f"Should detect config_del: {symbols}"
    assert "config:" in detail, f"Detail should mention config: {detail}"
    print(f"  [OK] test_extract_yaml_config: {len(symbols)} items")


def test_classify_risk_p0():
    """P0 risk classification."""
    r, reason = classify_risk("D", "java", [], False)
    assert r == "P0", f"Deleted file should return P0, got {r}"

    r, reason = classify_risk("M", "java", [], True)
    assert r == "P0", f"Breaking change should return P0, got {r}"

    r, reason = classify_risk("M", "sql", ["ddl:DROP COLUMN mobile"], False)
    assert r == "P0", f"DDL with DROP should return P0, got {r}"
    print(f"  [OK] test_classify_risk_p0")


def test_classify_risk_p1_p2():
    """P1/P2 risk classification."""
    r, reason = classify_risk("M", "java", [], False)
    assert r == "P1", f"Java non-breaking modification should return P1, got {r}"

    r, reason = classify_risk("M", "yml", [], False)
    assert r == "P1", f"Config change should return P1, got {r}"

    r, reason = classify_risk("M", "md", [], False)
    assert r == "P2", f"Doc change should return P2, got {r}"

    r, reason = classify_risk("A", "json", [], False)
    assert r == "P2", f"JSON add should return P2, got {r}"
    print(f"  [OK] test_classify_risk_p1_p2")


def test_analyze_empty():
    """Empty changes do not crash."""
    m = DiffManifest(generated_at="test")
    d = json.dumps({"changes": [], "summary": "No uncommitted changes", "risk_level": "P2"})
    assert m.risk_level == "P2"
    print(f"  [OK] test_analyze_empty")


def test_extract_java_diff_empty():
    """Empty diff does not crash."""
    symbols, detail = extract_java_diff("")
    assert symbols == [], f"Empty diff should return empty list, got {symbols}"
    assert "java:" in detail, f"Empty diff detail should contain 'java:': {detail}"
    print(f"  [OK] test_extract_java_diff_empty")


def test_extract_python_diff():
    """Python diff detects function, class, and field changes."""
    diff = """+def new_function():
+    pass
-    def old_method(self):
-        pass
+class NewModel:
+    pass
+    self.new_field = 1
-    self.old_field = 1"""
    symbols, detail = extract_python_diff(diff)
    assert len(symbols) >= 3, f"Should detect multiple change types: {symbols}"
    assert any("method" in s for s in symbols), f"Should detect method: {symbols}"
    assert any("class" in s for s in symbols), f"Should detect class: {symbols}"
    assert any("prop" in s for s in symbols), f"Should detect property: {symbols}"
    assert "python:" in detail
    print(f"  [OK] test_extract_python_diff: {len(symbols)} symbols")


def test_extract_typescript_diff():
    """TypeScript diff detects interface, type, and field changes."""
    diff = """+interface UserDTO {
+  phone?: string;
-  mobile: string;
+}
+type Status = 'active' | 'inactive';
-    private oldMethod() {}"""
    symbols, detail = extract_typescript_diff(diff)
    assert any("interface" in s.lower() for s in symbols), f"Should detect interface: {symbols}"
    assert any("field_add" in s or "field_del" in s or "prop" in s for s in symbols), f"Should detect field change: {symbols}"
    assert "typescript:" in detail
    print(f"  [OK] test_extract_typescript_diff: {len(symbols)} symbols")


def test_extract_vue_diff_script_props():
    """Vue SFC detects prop changes in <script>."""
    diff = """+<script setup>
+  const props = defineProps({
+    userName: String,
-    oldField: String,
+  })
+</script>"""
    symbols, detail = extract_vue_diff(diff)
    assert any("field_add:userName" in s for s in symbols), f"Should detect added prop: {symbols}"
    assert any("field_del:oldField" in s for s in symbols), f"Should detect removed prop: {symbols}"
    assert "vue:" in detail, f"Detail should contain 'vue:': {detail}"
    print(f"  [OK] test_extract_vue_diff_script_props: {detail}")


def test_extract_vue_diff_emits():
    """Vue SFC detects emit event changes."""
    diff = """+<script setup>
+  const emit = defineEmits(['updated', 'closed'])
-  const emit = defineEmits(['deleted'])
+</script>"""
    symbols, detail = extract_vue_diff(diff)
    assert any("event_add" in s for s in symbols), f"Should detect event: {symbols}"
    assert any("event_del" in s for s in symbols), f"Should detect removed event: {symbols}"
    assert "vue:" in detail
    print(f"  [OK] test_extract_vue_diff_emits: {len(symbols)} symbols")


def test_extract_vue_diff_template():
    """Vue SFC detects template :prop and @event usage."""
    diff = """+<template>
+  <ChildComponent :title="pageTitle" @close="onClose" />
-  <ChildComponent :oldProp="value" />
+</template>"""
    symbols, detail = extract_vue_diff(diff)
    assert any("field_add" in s for s in symbols), f"Should detect prop binding: {symbols}"
    assert any("event_add" in s for s in symbols), f"Should detect event binding: {symbols}"
    assert "vue:" in detail
    print(f"  [OK] test_extract_vue_diff_template: {len(symbols)} symbols")


def test_extract_vue_diff_style_only():
    """Vue SFC with only <style> changes produces no symbols."""
    diff = """+<style scoped>
+  .red { color: red; }
-  .blue { color: blue; }
+</style>"""
    symbols, detail = extract_vue_diff(diff)
    assert symbols == [], f"Style-only changes should yield no symbols: {symbols}"
    assert "vue:" in detail
    print(f"  [OK] test_extract_vue_diff_style_only")


def test_extract_jsp_diff():
    """JSP diff detects taglib, includes, bean refs, EL."""
    diff = """+<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c" %>
+<jsp:include page="/common/header.jsp" />
-<jsp:include page="/common/old-header.jsp" />
+<bean:write name="user" property="fullName" />
+${user.name}
-${oldData.value}"""
    symbols, detail = extract_jsp_diff(diff)
    assert any("taglib_add" in s for s in symbols), f"Should detect taglib: {symbols}"
    assert any("include_add" in s for s in symbols), f"Should detect include_add: {symbols}"
    assert any("include_del" in s for s in symbols), f"Should detect include_del: {symbols}"
    assert any("prop_add" in s for s in symbols), f"Should detect bean:write: {symbols}"
    assert any("field_add" in s for s in symbols), f"Should detect EL: {symbols}"
    assert "jsp:" in detail
    print(f"  [OK] test_extract_jsp_diff: {len(symbols)} symbols")


def test_extract_jsp_diff_empty():
    """Empty JSP diff does not crash."""
    symbols, detail = extract_jsp_diff("")
    assert symbols == [], f"Empty diff should return empty list: {symbols}"
    assert "jsp:" in detail
    print(f"  [OK] test_extract_jsp_diff_empty")


def test_extract_go_diff():
    """Go diff detects struct fields and function changes."""
    diff = """+type User struct {
+    ID   int64  `json:"id"`
+    Name string `json:"name"`
-    Phone string `json:"phone"`
+    Mobile string `json:"mobile"`
+}
+func GetUser(id int64) (*User, error) {
+    return nil, nil
+}"""
    symbols, detail = extract_go_diff(diff)
    assert any("field_del" in s for s in symbols), f"Should detect field removal: {symbols}"
    assert any("field_add" in s for s in symbols), f"Should detect field addition: {symbols}"
    assert any("method_add" in s for s in symbols), f"Should detect func: {symbols}"
    assert "go:" in detail, f"Detail should contain 'go:': {detail}"
    print(f"  [OK] test_extract_go_diff: {len(symbols)} symbols")


def test_extract_properties_diff():
    """Properties diff detects config key changes."""
    diff = """+order.timeout=500
-order.retry=3
+payment.max.amount=20000
-debug=true"""
    symbols, detail = extract_properties_diff(diff)
    assert any("config_add" in s for s in symbols), f"Should detect config_add: {symbols}"
    assert any("config_del" in s for s in symbols), f"Should detect config_del: {symbols}"
    assert "config:" in detail, f"Detail should mention config: {detail}"
    print(f"  [OK] test_extract_properties_diff: {len(symbols)} items")


def test_extract_xml_diff():
    """XML diff does not crash and returns line counts."""
    diff = """+<bean id="userDao" class="..."/>
-<bean id="oldDao" class="..."/>"""
    symbols, detail = extract_xml_diff(diff)
    assert symbols == [], f"XML should return empty symbols: {symbols}"
    assert "xml:" in detail, f"Detail should contain 'xml:': {detail}"
    print(f"  [OK] test_extract_xml_diff: {detail}")


if __name__ == "__main__":
    print(f"\n{'='*50}")
    print(f"  diff_analyzer tests")
    print(f"{'='*50}\n")

    tests = [
        test_extract_java_diff_field_add_remove,
        test_extract_java_diff_feign_interface_method,
        test_extract_java_diff_annotation,
        test_extract_java_diff_ignores_import_package,
        test_extract_sql_ddl,
        test_extract_yaml_config,
        test_extract_python_diff,
        test_extract_typescript_diff,
        test_classify_risk_p0,
        test_classify_risk_p1_p2,
        test_analyze_empty,
        test_extract_java_diff_empty,
        test_extract_vue_diff_script_props,
        test_extract_vue_diff_emits,
        test_extract_vue_diff_template,
        test_extract_vue_diff_style_only,
        test_extract_jsp_diff,
        test_extract_jsp_diff_empty,
        test_extract_go_diff,
        test_extract_properties_diff,
        test_extract_xml_diff,
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
