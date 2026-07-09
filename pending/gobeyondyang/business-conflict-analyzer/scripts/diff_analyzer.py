#!/usr/bin/env python3
"""
diff_analyzer.py (Step 1) — Parse git diff into structured changes.

Usage:
    python diff_analyzer.py                          # Uncommitted changes
    python diff_analyzer.py --cached                 # Staged changes
    python diff_analyzer.py --since HEAD~1
    python diff_analyzer.py --lang zh
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path

_script_dir = str(Path(__file__).parent.resolve())
if _script_dir not in sys.path:
    sys.path.insert(0, _script_dir)
from lang import Translator, DELETION_PREFIXES as _DEL_PREFIXES

@dataclass
class Change:
    type: str          # A (Added) / M (Modified) / D (Deleted) / R (Renamed) / C (Copied) / T (TypeChanged)
    file: str
    extension: str
    risk_level: str    # P0 / P1 / P2
    symbols: list = field(default_factory=list)
    details: str = ""
    reason: str = ""   # i18n key explaining why this risk level was assigned

@dataclass
class DiffManifest:
    changes: list = field(default_factory=list)
    summary: str = ""
    risk_level: str = "P2"
    counts: dict = field(default_factory=lambda: {"p0": 0, "p1": 0, "p2": 0})
    generated_at: str = ""
    lang: str = "en"

    # Structured summary fields (translated at output time)
    summary_key: str = "diff.summary.no_changes"
    summary_params: dict = field(default_factory=dict)

def _detect_encoding() -> str:
    """Detect the system encoding for subprocess output on Windows."""
    import locale
    try:
        return locale.getpreferredencoding(do_setlocale=False) or "utf-8"
    except Exception:
        return "utf-8"

def run_git_diff(*args: str) -> str:
    """Run git diff with given args and return stdout. Exits on error."""
    cmd = ["git", "diff"] + list(args)
    try:
        # Try UTF-8 first (works on Linux/macOS/Git Bash)
        result = subprocess.run(
            cmd, capture_output=True, text=True,
            encoding="utf-8", errors="replace"
        )
        output = result.stdout

        # On Windows with Chinese locale, git output may use GBK.
        # Check if replacement chars indicate an encoding mismatch.
        if "�" in output or "?" in output:
            sys_enc = _detect_encoding()
            if sys_enc.lower() != "utf-8":
                result2 = subprocess.run(
                    cmd, capture_output=True, text=True,
                    encoding=sys_enc, errors="replace"
                )
                output2 = result2.stdout
                # Use the re-decoded output if it has fewer replacement chars
                if output2.count("�") + output2.count("?") < output.count("�") + output.count("?"):
                    return output2
        return output
    except FileNotFoundError:
        t = Translator()
        print(t.t("error.git_diff_failed", stderr="git not found in PATH"), file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        t = Translator()
        print(t.t("error.git_diff_failed", stderr=str(e)), file=sys.stderr)
        sys.exit(1)

def get_changed_files(target: str = "HEAD") -> list[tuple[str, str]]:
    """Get (status, filepath) tuples from git diff --name-status for the given target."""
    if target == "--cached":
        args = ["--cached", "--name-status"]
    else:
        args = ["--name-status", target]
    raw = run_git_diff(*args).strip()
    if not raw:
        return []
    files = []
    for line in raw.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2:
            status = parts[0]
            # Normalize rename status (R100, R050, etc.) to "R"
            if status.startswith("R") and status != "R":
                status = "R"
            if status.startswith("C") and status != "C":
                status = "C"
            files.append((status, parts[1]))
    return files

# Separate patterns for class/method declarations to avoid backtracking issues.
_JAVA_CLASS_PATTERN = re.compile(
    r'^\s*(?:public|private|protected|static|final|abstract|synchronized|default)\s+.*'
    r'(class|interface|enum|@interface)\s+\w+'
)
_JAVA_METHOD_MOD_PATTERN = re.compile(
    r'(?:public|private|protected|static|final|abstract|synchronized|default)\s+.*'
    r'(\w+)\s*\([^)]*\)\s*(?:\{|throws|$)'
)
_JAVA_METHOD_NOMOD_PATTERN = re.compile(
    r'^\s*[\w<>,?\[\].]+\s+(\w+)\s*\([^)]*\)\s*(?:\{|;|throws)'
)
# Package-private class/interface/enum (no modifier prefix)
_JAVA_PKGPRIVATE_CLASS_PATTERN = re.compile(
    r'^\s*(class|interface|enum)\s+\w+'
)
FIELD_PATTERN = re.compile(
    r'^\s*(private|public|protected|static|final|transient|volatile)\s+[\w<>,?\[\]]+\s+\w+'
)
ANNOTATION_PATTERN = re.compile(r'^\s*@\w+')
SQL_DDL_PATTERN = re.compile(
    r'(ALTER\s+TABLE|DROP\s+(TABLE|COLUMN|INDEX)|CREATE\s+TABLE|'
    r'MODIFY\s+COLUMN|CHANGE\s+COLUMN|RENAME\s+(TO|COLUMN))',
    re.IGNORECASE
)
YAML_KEY_PATTERN = re.compile(r'^[+-]\s*(?:[\w.-]+|["\'](?:[^"\']+)["\'])\s*:')

_SYM_ADD  = "field_add"   # field_add:name
_SYM_DEL  = "field_del"   # field_del:name
_SYM_MADD = "method_add"
_SYM_MDEL = "method_del"
_SYM_CADD = "class_add"
_SYM_CDEL = "class_del"
_SYM_AADD = "annotation_add"
_SYM_ADEL = "annotation_del"
_SYM_DADD = "decorator_add"
_SYM_DDEL = "decorator_del"
_SYM_IADD = "interface_add"
_SYM_IDEL = "interface_del"
_SYM_TADD = "type_add"
_SYM_TDEL = "type_del"
_SYM_EADD = "enum_add"
_SYM_EDEL = "enum_del"
_SYM_PADD = "prop_add"
_SYM_PDEL = "prop_del"

def _sym(prefix_add: str, prefix_del: str, is_addition: bool, name: str) -> str:
    """Build a symbol string: prefix_add:name (addition) or prefix_del:name (deletion)."""
    prefix = prefix_add if is_addition else prefix_del
    return f"{prefix}:{name}"

def _detail(lang: str, added: int, removed: int) -> str:
    """Build a detail string like 'java:+3/-2' for a given language."""
    return f"{lang}:+{added}/-{removed}"

def _detail_sql(count: int) -> str:
    return f"sql:{count} DDL"

def _detail_config(count: int) -> str:
    return f"config:{count} changes"

def extract_java_diff(diff_text: str) -> tuple[list[str], str]:
    """Parse Java diff — class, interface, enum, method, field, annotation changes."""
    symbols = []
    added = 0
    removed = 0

    for line in diff_text.splitlines():
        stripped = line[1:].strip() if line.startswith(("+", "-")) else ""
        if not stripped or stripped.startswith(("import ", "package ")):
            continue
        is_addition = line.startswith("+")

        if _JAVA_CLASS_PATTERN.match(stripped):
            m = re.search(r'(class|interface|enum)\s+(\w+)', stripped)
            if m:
                kind = m.group(1)
                name = m.group(2)
                if kind == "interface":
                    symbols.append(_sym(_SYM_IADD, _SYM_IDEL, is_addition, name))
                elif kind == "enum":
                    symbols.append(_sym(_SYM_EADD, _SYM_EDEL, is_addition, name))
                else:
                    symbols.append(_sym(_SYM_CADD, _SYM_CDEL, is_addition, name))
                if is_addition:
                    added += 1
                else:
                    removed += 1
        elif _JAVA_PKGPRIVATE_CLASS_PATTERN.match(stripped):
            m = re.search(r'(class|interface|enum)\s+(\w+)', stripped)
            if m:
                kind = m.group(1)
                name = m.group(2)
                if kind == "interface":
                    symbols.append(_sym(_SYM_IADD, _SYM_IDEL, is_addition, name))
                elif kind == "enum":
                    symbols.append(_sym(_SYM_EADD, _SYM_EDEL, is_addition, name))
                else:
                    symbols.append(_sym(_SYM_CADD, _SYM_CDEL, is_addition, name))
                if is_addition:
                    added += 1
                else:
                    removed += 1
        elif _JAVA_METHOD_MOD_PATTERN.match(stripped) or _JAVA_METHOD_NOMOD_PATTERN.match(stripped):
            m = re.search(r'(?:public|private|protected|static|final|\s)*\s*(\w+)\s*\(', stripped) or \
                re.search(r'(\w+)\s*\(', stripped)
            if m:
                symbols.append(_sym(_SYM_MADD, _SYM_MDEL, is_addition, m.group(1)))
                if is_addition: added += 1
                else: removed += 1
        elif FIELD_PATTERN.match(stripped):
            field_match = re.search(r'[\w<>,?\[\]]+\s+(\w+)\s*[;=]', stripped)
            if field_match:
                symbols.append(_sym(_SYM_ADD, _SYM_DEL, is_addition, field_match.group(1)))
                if is_addition:
                    added += 1
                else:
                    removed += 1
        elif ANNOTATION_PATTERN.match(stripped):
            symbols.append(_sym(_SYM_AADD, _SYM_ADEL, is_addition, stripped))
            if is_addition:
                added += 1
            else:
                removed += 1
        elif re.match(r'^\s*\w+\s*\(', stripped) and not stripped.startswith(
                ("if", "for", "while", "switch", "catch", "return", "new", "this", "super")):
            # Catches package-private constructors: ClassName(param) { ... }
            # and other modifier-less methods. Excludes control-flow keywords.
            m = re.match(r'^\s*(\w+)\s*\(', stripped)
            if m:
                symbols.append(_sym(_SYM_MADD, _SYM_MDEL, is_addition, m.group(1)))
                if is_addition:
                    added += 1
                else:
                    removed += 1

    return symbols, _detail("java", added, removed)

def extract_sql_diff(diff_text: str) -> tuple[list[str], str]:
    """Parse SQL diff — ALTER/CREATE/DROP DDL statements."""
    symbols = []
    for line in diff_text.splitlines():
        stripped = line[1:].strip() if line.startswith(("+", "-")) else ""
        if SQL_DDL_PATTERN.match(stripped):
            symbols.append(f"ddl:{stripped}")
    return symbols, _detail_sql(len(symbols))

def extract_yaml_diff(diff_text: str) -> tuple[list[str], str]:
    """Parse YAML diff — config key additions and deletions."""
    symbols = []
    for line in diff_text.splitlines():
        if line.startswith("+") and YAML_KEY_PATTERN.match(line):
            key = line[1:].strip().rstrip(":")
            symbols.append(f"config_add:{key}")
        elif line.startswith("-") and YAML_KEY_PATTERN.match(line):
            key = line[1:].strip().rstrip(":")
            symbols.append(f"config_del:{key}")
    return symbols, _detail_config(len(symbols))


def extract_properties_diff(diff_text: str) -> tuple[list[str], str]:
    """Parse .properties / .conf file diff — key=value changes."""
    symbols = []
    for line in diff_text.splitlines():
        if not line.startswith(("+", "-")):
            continue
        stripped = line[1:].strip()
        is_addition = line.startswith("+")
        # key=value or key: value format
        m = re.match(r'^([\w.-]+)\s*[=:]', stripped)
        if m:
            key = m.group(1).rstrip(":")
            symbols.append(f"config_{'add' if is_addition else 'del'}:{key}")
    return symbols, _detail_config(len(symbols))


def extract_xml_diff(diff_text: str) -> tuple[list[str], str]:
    """Parse XML diff — count added/removed lines for element-level change awareness."""
    added = sum(1 for line in diff_text.splitlines()
                if line.startswith("+") and line[1:].strip())
    removed = sum(1 for line in diff_text.splitlines()
                  if line.startswith("-") and line[1:].strip())
    return [], f"xml:+{added}/-{removed}"

def extract_python_diff(diff_text: str) -> tuple[list[str], str]:
    """Parse Python diff — class, function, decorator, field changes."""
    symbols = []
    added = 0
    removed = 0

    for line in diff_text.splitlines():
        stripped = line[1:].strip() if line.startswith(("+", "-")) else ""
        if not stripped or stripped.startswith(("import ", "from ", "# ", "\"\"\"", "'''")):
            continue
        is_addition = line.startswith("+")

        if re.match(r'^\s*def\s+\w+\s*\(', stripped):
            match = re.search(r'def\s+(\w+)', stripped)
            if match:
                symbols.append(_sym(_SYM_MADD, _SYM_MDEL, is_addition, match.group(1)))
                if is_addition:
                    added += 1
                else:
                    removed += 1
        elif re.match(r'^\s*class\s+\w+', stripped):
            match = re.search(r'class\s+(\w+)', stripped)
            if match:
                symbols.append(_sym(_SYM_CADD, _SYM_CDEL, is_addition, match.group(1)))
                if is_addition:
                    added += 1
                else:
                    removed += 1
        elif re.match(r'^\s*@\w+', stripped):
            symbols.append(_sym(_SYM_DADD, _SYM_DDEL, is_addition, stripped))
            if is_addition:
                added += 1
            else:
                removed += 1
        elif re.match(r'^\s*self\.\w+\s*[=:]', stripped) or \
             re.match(r'^\s*\w+\s*[=:]\s*(?!.*(?:return|pass|if|for|while|def|class))', stripped):
            match_field = re.search(r'(\w+)\s*[=:]', stripped)
            if match_field and match_field.group(1) not in ("self", "cls", "return", "pass", "if", "else", "for"):
                symbols.append(_sym(_SYM_PADD, _SYM_PDEL, is_addition, match_field.group(1)))
                if is_addition:
                    added += 1
                else:
                    removed += 1

    return symbols, _detail("python", added, removed)

def extract_typescript_diff(diff_text: str) -> tuple[list[str], str]:
    """Parse TypeScript/JS diff — interface, type, class, enum, method, field changes."""
    symbols = []
    added = 0
    removed = 0

    for line in diff_text.splitlines():
        stripped = line[1:].strip() if line.startswith(("+", "-")) else ""
        if not stripped or stripped.startswith(("import ", "export type {", "export type{", "//", "/*")):
            continue
        is_addition = line.startswith("+")

        if re.match(r'^\s*\w+\??\s*[?:]\s*[\w\[\]|&<>]', stripped) and \
           not stripped.startswith(("interface", "type", "class", "function", "const", "let", "var")):
            match = re.search(r'(\w+)\s*[?:]', stripped)
            if match:
                symbols.append(_sym(_SYM_ADD, _SYM_DEL, is_addition, match.group(1)))
                if is_addition:
                    added += 1
                else:
                    removed += 1
        elif re.match(r'^\s*(export\s+)?(interface|type|class|enum|abstract class)\s+', stripped):
            match = re.search(r'(interface|type|class|enum)\s+(\w+)', stripped)
            if match:
                kind = match.group(1)
                name = match.group(2)
                if kind == "interface":
                    symbols.append(_sym(_SYM_IADD, _SYM_IDEL, is_addition, name))
                elif kind == "type":
                    symbols.append(_sym(_SYM_TADD, _SYM_TDEL, is_addition, name))
                elif kind == "enum":
                    symbols.append(_sym(_SYM_EADD, _SYM_EDEL, is_addition, name))
                else:
                    symbols.append(_sym(_SYM_CADD, _SYM_CDEL, is_addition, name))
                if is_addition:
                    added += 1
                else:
                    removed += 1
        elif re.match(r'^\s*(public|private|protected|static|async|abstract|readonly|\s)*\w+\s*\(', stripped) or \
             re.match(r'^\s*\w+\s*\(.*\)\s*[:\{]', stripped):
            match = re.search(r'(\w+)\s*\(', stripped)
            if match and match.group(1) not in ("if", "for", "while", "switch", "catch"):
                symbols.append(_sym(_SYM_MADD, _SYM_MDEL, is_addition, match.group(1)))
                if is_addition:
                    added += 1
                else:
                    removed += 1
        elif re.match(r'^\s*@\w+', stripped):
            symbols.append(_sym(_SYM_DADD, _SYM_DDEL, is_addition, stripped))
            if is_addition:
                added += 1
            else:
                removed += 1

    return symbols, _detail("typescript", added, removed)


def extract_go_diff(diff_text: str) -> tuple[list[str], str]:
    """Parse Go diff — struct fields, interface methods, function signatures."""
    symbols = []

    _GO_FIELD_RE = re.compile(r'^\s*(\w+)\s+[\w.*\[\]]+')
    _GO_FUNC_RE = re.compile(r'^\s*(?:func\s+(?:\([^)]*\)\s+)?(\w+))\s*\(')

    for line in diff_text.splitlines():
        if not line.startswith(("+", "-")):
            continue
        stripped = line[1:].strip()
        is_addition = line.startswith("+")

        # Function/method: func Name(...) or func (r *T) Name(...)
        m = _GO_FUNC_RE.search(stripped)
        if m:
            symbols.append(_sym(_SYM_MADD, _SYM_MDEL, is_addition, m.group(1)))
            continue

        # Struct field: Name Type
        m = _GO_FIELD_RE.match(stripped)
        if m:
            symbols.append(_sym(_SYM_ADD, _SYM_DEL, is_addition, m.group(1)))
            continue

        # Interface declaration: type Name interface
        if re.match(r'^\s*type\s+\w+\s+interface', stripped):
            m = re.search(r'type\s+(\w+)\s+interface', stripped)
            if m:
                symbols.append(_sym(_SYM_IADD, _SYM_IDEL, is_addition, m.group(1)))
                continue

        # Struct declaration: type Name struct
        if re.match(r'^\s*type\s+\w+\s+struct', stripped):
            m = re.search(r'type\s+(\w+)\s+struct', stripped)
            if m:
                symbols.append(_sym(_SYM_CADD, _SYM_CDEL, is_addition, m.group(1)))
                continue

    symbols = list(dict.fromkeys(symbols))
    go_adds = sum(1 for s in symbols if "_add:" in s)
    go_dels = sum(1 for s in symbols if "_del:" in s)
    return symbols, _detail("go", go_adds, go_dels)


# Vue SFC parser

_VUE_SCRIPT_RE = re.compile(r'^\s*<script\b')
_VUE_SCRIPT_END_RE = re.compile(r'^\s*</script>')
_VUE_TEMPLATE_RE = re.compile(r'^\s*<template\b')
_VUE_TEMPLATE_END_RE = re.compile(r'^\s*</template>')

def extract_vue_diff(diff_text: str) -> tuple[list[str], str]:
    """Parse Vue SFC diff — <script> props/emits/state, <template> bindings."""
    symbols = []
    in_script = False
    in_template = False

    for line in diff_text.splitlines():
        if not line:
            continue
        prefix = line[0]
        # Track <script>/<template> sections across context + diff lines,
        # extract symbols only from +/- lines.
        stripped = line[1:].strip() if prefix in ("+", "-", " ") else line.strip()

        if _VUE_SCRIPT_RE.match(stripped):
            in_script, in_template = True, False
            continue
        if _VUE_SCRIPT_END_RE.match(stripped):
            in_script, in_template = False, False
            continue
        if _VUE_TEMPLATE_RE.match(stripped):
            in_template, in_script = True, False
            continue
        if _VUE_TEMPLATE_END_RE.match(stripped):
            in_template = False
            continue

        if prefix not in ("+", "-"):
            continue
        is_addition = prefix == "+"

        if in_script:
            if stripped.startswith(("//", "/*", "*", "import ", "export default")):
                continue

            m = re.search(r"""defineModel\s*\(\s*['"](\w[\w-]*)['"]""", stripped)
            if m:
                symbols.append(_sym(_SYM_ADD, _SYM_DEL, is_addition, m.group(1)))
                continue

            m = re.search(r"""defineEmits\s*\(\s*\[([^\]]+)\]""", stripped)
            if m:
                for evt in re.findall(r"""['"](\w[\w-]*)['"]""", m.group(1)):
                    symbols.append(f"event_{'add' if is_addition else 'del'}:{evt}")
                continue

            m = re.match(r"""^\s*['"](\w[\w-]*)['"]\s*[,)\]]""", stripped)
            if m:
                symbols.append(f"event_{'add' if is_addition else 'del'}:{m.group(1)}")
                continue

            m = re.match(r'^\s*(?:const|let|var)\s+(\w+)\s*=\s*(?:ref|reactive|computed|shallowRef|shallowReactive)\s*\(', stripped)
            if m:
                symbols.append(_sym(_SYM_PADD, _SYM_PDEL, is_addition, m.group(1)))
                continue

            m = re.match(r"""^\s*['"]?(\w+)['"]?\s*:\s*(?:\{|String|Number|Boolean|Array|Object|Function|Date|RegExp|Symbol)\b""", stripped)
            if m and m.group(1) not in ('props', 'emits', 'type', 'default', 'required', 'validator', 'setup', 'data', 'methods', 'computed', 'watch', 'components', 'directives', 'filters'):
                symbols.append(_sym(_SYM_ADD, _SYM_DEL, is_addition, m.group(1)))
                continue

        elif in_template:
            # :prop / v-bind:prop (consumer side)
            for m in re.finditer(r'(?:v-bind|:)([\w-]+)\s*=', stripped):
                symbols.append(_sym(_SYM_ADD, _SYM_DEL, is_addition, m.group(1)))
            # @event (consumer side)
            for m in re.finditer(r'@([\w-]+)\s*=', stripped):
                symbols.append(f"event_{'add' if is_addition else 'del'}:{m.group(1)}")
            # {{ obj.field }} interpolation (track field-level changes)
            for m in re.finditer(r'\{\{\s*(\w+)\.(\w+)\s*\}\}', stripped):
                symbols.append(_sym(_SYM_ADD, _SYM_DEL, is_addition, m.group(2)))

    # Dedup same prop appearing in both <script> and <template>
    symbols = list(dict.fromkeys(symbols))
    vue_adds = sum(1 for s in symbols if "_add:" in s)
    vue_dels = sum(1 for s in symbols if "_del:" in s)
    return symbols, _detail("vue", vue_adds, vue_dels)

# JSP parser

_JSP_TAGLIB_RE = re.compile(r'<%@\s*taglib\s+uri\s*=\s*["\']([^"\']+)["\']')
_JSP_INCLUDE_RE = re.compile(r'<jsp:include\s+[^>]*page\s*=\s*["\']([^"\']+)["\']')
_JSP_FORWARD_RE = re.compile(r'<jsp:forward\s+[^>]*page\s*=\s*["\']([^"\']+)["\']')
_JSP_USE_BEAN_RE = re.compile(r'<jsp:useBean\s+[^>]*id\s*=\s*["\']([^"\']+)["\']')
_JSP_GET_PROPERTY_RE = re.compile(r'<jsp:getProperty\s+[^>]*property\s*=\s*["\']([^"\']+)["\']')
_JSP_BEAN_WRITE_RE = re.compile(r'<bean:write\s+[^>]*(?:name|property)\s*=\s*["\']([^"\']+)["\']')
_JSP_BEAN_DEFINE_RE = re.compile(r'<bean:define\s+[^>]*name\s*=\s*["\']([^"\']+)["\']')
_JSP_BEAN_MSG_RE = re.compile(r'<bean:message\s+[^>]*key\s*=\s*["\']([^"\']+)["\']')
_JSP_EL_RE = re.compile(r'\$\{([^}]+)\}')

def extract_jsp_diff(diff_text: str) -> tuple[list[str], str]:
    """Parse JSP diff — taglib, includes, bean refs, EL expressions."""
    symbols = []
    added = 0
    removed = 0

    for line in diff_text.splitlines():
        if not line.startswith(("+", "-")):
            continue
        stripped = line[1:].strip()
        is_addition = line.startswith("+")

        for m in _JSP_TAGLIB_RE.finditer(stripped):
            symbols.append(f"taglib_{'add' if is_addition else 'del'}:{m.group(1)}")
            if is_addition: added += 1
            else: removed += 1

        for m in list(_JSP_INCLUDE_RE.finditer(stripped)) + list(_JSP_FORWARD_RE.finditer(stripped)):
            symbols.append(f"include_{'add' if is_addition else 'del'}:{m.group(1)}")
            if is_addition: added += 1
            else: removed += 1

        for m in _JSP_USE_BEAN_RE.finditer(stripped):
            symbols.append(_sym(_SYM_ADD, _SYM_DEL, is_addition, m.group(1)))
            if is_addition: added += 1
            else: removed += 1

        for m in list(_JSP_BEAN_WRITE_RE.finditer(stripped)) + list(_JSP_BEAN_DEFINE_RE.finditer(stripped)):
            symbols.append(_sym(_SYM_PADD, _SYM_PDEL, is_addition, m.group(1)))
            if is_addition: added += 1
            else: removed += 1

        for m in _JSP_BEAN_MSG_RE.finditer(stripped):
            symbols.append(f"config_{'add' if is_addition else 'del'}:{m.group(1)}")
            if is_addition: added += 1
            else: removed += 1

        for m in _JSP_GET_PROPERTY_RE.finditer(stripped):
            symbols.append(_sym(_SYM_PADD, _SYM_PDEL, is_addition, m.group(1)))
            if is_addition: added += 1
            else: removed += 1

        for m in _JSP_EL_RE.finditer(stripped):
            expr = m.group(1).strip()
            if '.' in expr:
                # ${user.mobile} → extract just "mobile" (field name)
                field = expr.rsplit('.', 1)[-1].strip()
                if field:
                    symbols.append(_sym(_SYM_ADD, _SYM_DEL, is_addition, field))
                    if is_addition:
                        added += 1
                    else:
                        removed += 1
            elif re.match(r'^\w+$', expr):
                symbols.append(_sym(_SYM_ADD, _SYM_DEL, is_addition, expr))
                if is_addition: added += 1
                else: removed += 1

    return symbols, _detail("jsp", added, removed)

def classify_risk(status: str, extension: str, symbols: list, is_breaking: bool) -> tuple[str, str]:
    """Determine risk level (P0/P1/P2) and a reason i18n key based on change metadata."""
    if status == "D":
        return "P0", "diff.reason.file_deleted"
    if is_breaking:
        return "P0", "diff.reason.breaking"

    p0_exts = {".java", ".kt", ".kts", ".sql", ".ddl"}
    p1_exts = {".py", ".pyi", ".ts", ".tsx", ".js", ".jsx", ".go", ".vue",
               ".jsp", ".jspf", ".tag",
               ".yml", ".yaml", ".properties", ".xml", ".conf"}

    ext = f".{extension}"
    if ext in p0_exts:
        if extension in ("sql", "ddl") and any("DROP" in s.upper() for s in symbols):
            return "P0", "diff.reason.ddl"
        return "P1", "diff.reason.file_change"
    if ext in p1_exts:
        return "P1", "diff.reason.config_change"
    return "P2", "diff.reason.internal_refactor"

def _has_deletion(symbols: list[str]) -> bool:
    """Check if any symbol represents a deletion (matched against DELETION_PREFIXES)."""
    return any(s.startswith(_DEL_PREFIXES) for s in symbols)

def _detail_fallback(extension: str, status: str, t: Translator) -> str:
    """Fallback detail when no extractor matched. Produces language-appropriate output."""
    if t.lang == "zh":
        labels_zh = {"A": "新增", "M": "已修改", "D": "已删除", "R": "已重命名"}
        return f"{extension} 文件{labels_zh.get(status, '已变更')}"
    labels = {"A": "added", "M": "modified", "D": "deleted", "R": "renamed"}
    return f"{extension} file {labels.get(status, 'changed')}"

def analyze(target: str = "HEAD", lang: str | None = None) -> DiffManifest:
    """Run analysis and return a DiffManifest.

    Args:
        target: Git diff target ('HEAD', '--cached', or a commit range)
        lang: Language hint for summary generation
    """
    t = Translator(lang)
    manifest = DiffManifest(generated_at=datetime.now().isoformat(), lang=t.lang_for_pipe())

    files = get_changed_files(target)
    if not files:
        manifest.summary_key = "diff.summary.no_changes"
        manifest.summary = t.t("diff.summary.no_changes")
        return manifest

    for status, filepath in files:
        ext = Path(filepath).suffix.lstrip(".") or "unknown"
        diff_text = ""
        if status != "D":
            diff_args = ["--cached"] if target == "--cached" else [target]
            diff_text = run_git_diff(*diff_args, "--", filepath)

        symbols = []
        detail = ""
        is_breaking = False

        if ext == "java":
            symbols, detail = extract_java_diff(diff_text)
            path_lower = filepath.lower()
            if any(kw in path_lower for kw in ["controller", "dto", "vo", "feign", "client", "api"]):
                is_breaking = True
            if _has_deletion(symbols):
                is_breaking = True

        elif ext in ("py", "pyi"):
            symbols, detail = extract_python_diff(diff_text)
            path_lower = filepath.lower()
            if any(kw in path_lower for kw in ["views", "serializers", "routers", "api", "urls", "schemas"]):
                is_breaking = True
            if _has_deletion(symbols):
                is_breaking = True

        elif ext in ("ts", "tsx", "js", "jsx"):
            symbols, detail = extract_typescript_diff(diff_text)
            path_lower = filepath.lower()
            if any(kw in path_lower for kw in ["interfaces", "types", "api", "controllers", "services", "components", "pages", "views"]):
                is_breaking = True
            if _has_deletion(symbols):
                is_breaking = True

        elif ext in ("kt", "kts"):
            symbols, detail = extract_java_diff(diff_text)
            path_lower = filepath.lower()
            if any(kw in path_lower for kw in ["controller", "dto", "vo", "feign", "client", "api", "ktor"]):
                is_breaking = True
            if _has_deletion(symbols):
                is_breaking = True

        elif ext == "go":
            symbols, detail = extract_go_diff(diff_text)
            path_lower = filepath.lower()
            if any(kw in path_lower for kw in ["handler", "api", "transport", "endpoint", "delivery"]):
                is_breaking = True
            if _has_deletion(symbols):
                is_breaking = True

        elif ext == "vue":
            symbols, detail = extract_vue_diff(diff_text)
            path_lower = filepath.lower()
            if any(kw in path_lower for kw in ["components", "pages", "views"]):
                is_breaking = True
            if _has_deletion(symbols):
                is_breaking = True

        elif ext in ("jsp", "jspf", "tag"):
            symbols, detail = extract_jsp_diff(diff_text)
            if _has_deletion(symbols):
                is_breaking = True

        elif ext in ("sql", "ddl"):
            symbols, detail = extract_sql_diff(diff_text)
            if symbols and any("DROP" in s.upper() for s in symbols):
                is_breaking = True

        elif ext in ("yml", "yaml"):
            symbols, detail = extract_yaml_diff(diff_text)
        elif ext in ("properties", "conf"):
            symbols, detail = extract_properties_diff(diff_text)
        elif ext == "xml":
            symbols, detail = extract_xml_diff(diff_text)

        if not detail:
            detail = _detail_fallback(ext, status, t)

        risk_level, risk_reason_key = classify_risk(status, ext, symbols, is_breaking)
        change = Change(
            type=status,
            file=filepath,
            extension=ext,
            risk_level=risk_level,
            symbols=symbols,
            details=detail,
            reason=risk_reason_key,
        )
        manifest.changes.append(change)

    # Risk count
    for ch in manifest.changes:
        if ch.risk_level == "P0":
            manifest.counts["p0"] += 1
        elif ch.risk_level == "P1":
            manifest.counts["p1"] += 1
        else:
            manifest.counts["p2"] += 1

    # Summary (structured)
    total = sum(manifest.counts.values())
    if manifest.counts["p0"] > 0:
        manifest.summary_key = "diff.summary.p0"
        manifest.summary_params = {"count": manifest.counts["p0"]}
        manifest.risk_level = "P0"
    elif manifest.counts["p1"] > 0:
        manifest.summary_key = "diff.summary.p1"
        manifest.summary_params = {"count": manifest.counts["p1"]}
        manifest.risk_level = "P1"
    else:
        manifest.summary_key = "diff.summary.p2"
        manifest.summary_params = {"count": total, "files": t.t("common.files")}
        manifest.risk_level = "P2"

    manifest.summary = t.t(manifest.summary_key, **manifest.summary_params)
    return manifest

def main():
    parser = argparse.ArgumentParser(
        description="Extract structured code changes from git diff"
    )
    parser.add_argument("--cached", action="store_true",
                        help="Analyze staged changes")
    parser.add_argument("--since",
                        help="Analyze changes since a commit, e.g. HEAD~1")
    parser.add_argument("--lang", choices=("en", "zh"), default=None,
                        help="Output language (en/zh, auto-detected by default)")
    args = parser.parse_args()

    target = "HEAD"
    if args.cached:
        target = "--cached"
    elif args.since:
        target = args.since

    manifest = analyze(target, lang=args.lang)
    # Serialise with lang tag
    out = asdict(manifest)
    out["lang"] = manifest.lang
    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
