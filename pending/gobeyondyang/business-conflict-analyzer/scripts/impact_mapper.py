#!/usr/bin/env python3
"""
impact_mapper.py (Step 2) — Map git diff changes to business impact.

Reads diff_analyzer.py JSON from stdin, produces impact matrix.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

_script_dir = str(Path(__file__).parent.resolve())
if _script_dir not in sys.path:
    sys.path.insert(0, _script_dir)
from lang import Translator

@dataclass
class ConsumerImpact:
    file: str
    impact: str          # BREAKING / COMPATIBLE / NONE
    detail: str = ""

@dataclass
class DataMigration:
    required: bool = False
    risk: str = "LOW"    # HIGH / MEDIUM / LOW
    detail: str = ""

@dataclass
class ApiCompatibility:
    version_required: bool = False
    suggestion: str = ""

@dataclass
class ImpactMatrix:
    summary: str = ""
    consumer_impacts: list = field(default_factory=list)
    data_migration: DataMigration = field(default_factory=DataMigration)
    api_compatibility: ApiCompatibility = field(default_factory=ApiCompatibility)
    frontend_affected: bool = False
    frontend_files: list = field(default_factory=list)
    overall_impact: str = "INFO"    # CRITICAL / MAJOR / MINOR / INFO
    recommendation: str = ""
    lang: str = "en"

ARCH_LAYERS = {
    "controller": "layer.api",
    "api": "layer.api",
    "web": "layer.api",
    "feign": "layer.rpc",
    "client": "layer.rpc",
    "dto": "layer.data",
    "vo": "layer.data",
    "request": "layer.data_request",
    "response": "layer.data_response",
    "service": "layer.business",
    "impl": "layer.business_impl",
    "mapper": "layer.data_access",
    "repository": "layer.data_access",
    "dao": "layer.data_access",
    "enum": "layer.common",
    "constant": "layer.common",
    "config": "layer.config",
    "properties": "layer.config",

    "views": "layer.api",
    "view": "layer.api",
    "urls": "layer.api_route",
    "routers": "layer.api_route",
    "router": "layer.api_route",
    "routes": "layer.api_route",
    "serializers": "layer.data",
    "serializer": "layer.data",
    "schemas": "layer.data",
    "schema": "layer.data",
    "models": "layer.data_model",
    "model": "layer.data_model",
    "entities": "layer.data_model",
    "entity": "layer.data_model",
    "forms": "layer.data_form",
    "middleware": "layer.middleware",
    "pipelines": "layer.pipeline",
    "admin": "layer.admin",
    "apps": "layer.app_module",
    "migrations": "layer.data_migration",
    "alembic": "layer.data_migration",
    "apps.py": "layer.app_config",

    "components": "layer.frontend_component",
    "hooks": "layer.frontend_logic",
    "store": "layer.frontend_state",
    "redux": "layer.frontend_state",
    "vuex": "layer.frontend_state",
    "pages": "layer.frontend_page",
    "layouts": "layer.frontend_layout",
    "interfaces": "layer.type_contract",
    "interface": "layer.type_contract",
    "types": "layer.type_contract",
    "type": "layer.type_contract",
    "decorators": "layer.decorator",
    "decorator": "layer.decorator",
    "guards": "layer.guard",
    "pipes": "layer.pipe",
    "filters": "layer.filter",
    "interceptors": "layer.interceptor",
    "resolvers": "layer.resolver",
    "modules": "layer.module",
    "module": "layer.module",
    "providers": "layer.provider",
    "nest": "layer.nest",

    "handler": "layer.handler",
    "handlers": "layer.handler",
    "transport": "layer.transport",
    "delivery": "layer.delivery",
    "endpoint": "layer.endpoint",
    "usecase": "layer.usecase",
    "usecases": "layer.usecase",
    "struct": "layer.struct",
    "structs": "layer.struct",

    "ktor": "layer.ktor",
    "coroutines": "layer.concurrent",

    "tests": "layer.test",
    "test": "layer.test",
    "specs": "layer.test",
    "__test__": "layer.test",
    "docs": "layer.doc",
    "doc": "layer.doc",
}

def identify_layer(filepath: str) -> tuple[str, str]:
    
    path_lower = filepath.lower().replace("\\", "/")
    for keyword, layer_key in ARCH_LAYERS.items():
        if keyword in path_lower:
            return keyword, layer_key
    if path_lower.endswith(".vue"):
        return ".vue", "layer.frontend_component"
    if path_lower.endswith((".jsp", ".jspf", ".tag")):
        return ".jsp", "layer.frontend_page"
    return "other", "layer.other"

# File extension sets for grep include / Python walk
_INCLUDE_EXTS = {
    ".java", ".kt", ".kts",
    ".ts", ".tsx", ".vue",
    ".js", ".jsx",
    ".py", ".pyi", ".go",
    ".jsp", ".jspf", ".tag",
    ".yml", ".yaml",
    ".properties", ".conf",
    ".xml",
}
_EXCLUDE_DIRS = {
    ".git", "node_modules", "target", "build", "__pycache__", ".venv",
    "dist", ".next", ".nuxt", "out", "generated", "gen",
    ".m2", "gradle", ".gradle",
    ".idea", ".settings", ".vscode", ".vs",
    "assets", "public", "static", "uploads",
    "coverage", ".nyc_output",
    "helm", "charts", "vendor",
}

_REF_CACHE: dict[tuple[str, str], list[str]] = {}
_MAX_REFS = 100

def _build_regex(symbol: str) -> str:
    """Build a combined regex for finding references to `symbol`."""
    esc = re.escape(symbol)
    if symbol.startswith("@"):
        patterns = [esc]
    else:
        patterns = [rf'\b{esc}\b']
    if not symbol.startswith("@") and symbol and symbol[0].islower():
        cap = symbol[0].upper() + symbol[1:]
        patterns.extend([
            rf'\bget{cap}\b',
            rf'\bset{cap}\b',
            rf'\.{esc}\b',
        ])
    return '|'.join(patterns)

def _find_references_grep(regex: str, project_root: str) -> list[str]:
    """Fast path: use system grep (works on Linux/macOS/Git Bash)."""
    result = subprocess.run(
        ["grep", "-r", "-E",
         "--include=*.java", "--include=*.kt", "--include=*.kts",
         "--include=*.ts", "--include=*.tsx", "--include=*.vue",
         "--include=*.js", "--include=*.jsx",
         "--include=*.py", "--include=*.pyi", "--include=*.go",
         "--include=*.jsp", "--include=*.jspf", "--include=*.tag",
         "--include=*.yml", "--include=*.yaml",
         "--include=*.properties", "--include=*.conf",
         "--include=*.xml",
         "--exclude-dir=.git", "--exclude-dir=node_modules",
         "--exclude-dir=target", "--exclude-dir=build",
         "--exclude-dir=dist", "--exclude-dir=.next", "--exclude-dir=out",
         "--exclude-dir=generated", "--exclude-dir=.gradle",
         "--exclude-dir=.idea", "--exclude-dir=.vscode",
         "-l", regex, project_root],
        capture_output=True, text=True, timeout=30,
        encoding="utf-8", errors="replace"
    )
    return [p.strip() for p in result.stdout.strip().splitlines() if p.strip()]

def _find_references_python(regex: str, project_root: str) -> list[str]:
    """Pure Python file search (works everywhere, including Windows cmd/PowerShell)."""
    refs = []
    root = Path(project_root).resolve()
    compiled = re.compile(regex)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in _EXCLUDE_DIRS]
        for fn in filenames:
            ext = Path(fn).suffix.lower()
            if ext not in _INCLUDE_EXTS:
                continue
            fpath = Path(dirpath) / fn
            rel = str(fpath.relative_to(root)).replace("\\", "/")
            try:
                with fpath.open("r", encoding="utf-8", errors="replace") as f:
                    for line in f:
                        if compiled.search(line):
                            refs.append(rel)
                            break
            except (OSError, UnicodeDecodeError):
                continue
            if len(refs) >= _MAX_REFS:
                return refs
    return refs


def find_references(symbol: str, exclude_file: str = "", project_root: str = ".") -> list[str]:
    """Search for symbol references in the project with caching.

    Tries system grep first (fast), falls back to pure Python (slow but portable).
    Results are cached per (symbol, project_root) to avoid redundant searches.
    """
    cache_key = (symbol, project_root)
    if cache_key not in _REF_CACHE:
        regex = _build_regex(symbol)
        try:
            _REF_CACHE[cache_key] = _find_references_grep(regex, project_root)
        except FileNotFoundError:
            _REF_CACHE[cache_key] = _find_references_python(regex, project_root)
        except subprocess.TimeoutExpired:
            _REF_CACHE[cache_key] = _find_references_python(regex, project_root)

    refs = _REF_CACHE[cache_key]
    if exclude_file:
        return [p for p in refs if exclude_file not in p]
    return list(refs)

def find_historical_relations(symbol: str, project_root: str = ".") -> list[str]:
    
    refs = set()
    try:
        raw = subprocess.run(
            ["git", "log", "-S", symbol, "--since=6.months.ago",
             "--format=%H", "--max-count=10"],
            capture_output=True, text=True, timeout=30, cwd=project_root,
            encoding="utf-8", errors="replace"
        )
        commits = raw.stdout.strip().splitlines()
        for commit in commits[:5]:
            diff = subprocess.run(
                ["git", "diff-tree", "--no-commit-id", "-r", "--name-only", commit],
                capture_output=True, text=True, timeout=10, cwd=project_root,
                encoding="utf-8", errors="replace"
            )
            for path in diff.stdout.strip().splitlines():
                p = path.strip()
                if p and not any(ign in p for ign in
                                 [".git", "node_modules", "target", "build"]):
                    refs.add(p)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return list(refs)

COMMON_PATTERNS_CACHE = None

def load_common_patterns(pattern_path: str | None = None) -> list[dict]:

    global COMMON_PATTERNS_CACHE
    if COMMON_PATTERNS_CACHE is not None:
        return COMMON_PATTERNS_CACHE

    # Resolve relative to this script's directory, not cwd.
    # This ensures the file is found even when running via commit_guard.py
    # (where cwd is the user's project, not the skill directory).
    if pattern_path:
        p = Path(pattern_path)
        if not p.is_absolute():
            p = Path(__file__).parent.parent / pattern_path
    else:
        p = Path(__file__).parent.parent / "references" / "common_patterns.md"
    patterns = []
    if not p.exists():
        return patterns

    content = p.read_text(encoding="utf-8")
    current = None
    for line in content.splitlines():
        if line.startswith("## "):
            if current:
                patterns.append(current)
            current = {"name": line[3:].strip(), "trigger": "", "impact": "",
                       "action": "", "scope": "", "cost": ""}
        elif current:
            # Strip list marker
            text = line.lstrip("- ").strip() if line.startswith("- ") else line
            if text.startswith("**触发"):
                current["trigger"] = _extract_pattern_value(text)
            elif text.startswith("**关键词") or text.startswith("**Key"):
                current["keywords"] = _extract_pattern_value(text)
            elif text.startswith("**影响范围"):
                current["scope"] = _extract_pattern_value(text)
            elif text.startswith("**影响等级"):
                current["impact_level"] = "MAJOR"
                if "BREAKING" in text:
                    current["impact_level"] = "BREAKING"
                elif "COMPATIBLE" in text:
                    current["impact_level"] = "COMPATIBLE"
            elif text.startswith("**影响"):
                current["impact"] = _extract_pattern_value(text)
            elif text.startswith("**建议"):
                current["action"] = _extract_pattern_value(text)
            elif text.startswith("**修复代价"):
                current["cost"] = _extract_pattern_value(text)
    if current:
        patterns.append(current)

    COMMON_PATTERNS_CACHE = patterns
    return patterns

def _extract_pattern_value(text: str) -> str:
    """Extract value after bold label in pattern lines.

    Handles both:
      **影响范围**：...  (old Chinese format)
      **影响范围 / Scope**: ...  (bilingual format)
    """
    # Split on **： or **: and take the rest
    for sep in ("**：", "**:"):
        if sep in text:
            return text.split(sep, 1)[-1].strip()
    return ""

def match_pattern(symbols: list[str], filepath: str) -> Optional[dict]:
    """Match changes against the common_patterns.md keyword library.

    Each pattern defines a set of space-separated keywords. A pattern matches
    when at least 2 of its keywords appear in the combined symbol+filepath text.
    """
    patterns = load_common_patterns()
    text = " ".join(symbols) + " " + filepath.lower()
    for p in patterns:
        keywords = p.get("keywords", "")
        if not keywords:
            continue
        kws = keywords.split()
        hit_count = sum(1 for kw in kws if len(kw) > 2 and kw in text)
        if hit_count >= 2:
            return p
    return None

def check_frontend_impact(symbols: list[str], project_root: str = ".") -> list[str]:
    """Search frontend project for symbol references. Returns list of affected files.

    Frontend root resolution (first match wins):
      1. FRONTEND_ROOT env var (path-separated list)
      2. Common monorepo relative paths
    """
    env_roots = os.environ.get("FRONTEND_ROOT", "")
    project_root_path = Path(project_root).resolve()
    frontend_paths = []
    if env_roots:
        for r in env_roots.split(os.pathsep):
            r = r.strip()
            if r:
                frontend_paths.append(str(project_root_path / r) if not Path(r).is_absolute() else r)
    # Fallback: common monorepo layouts
    if not frontend_paths:
        for rel in ("../frontend", "../web", "../../frontend",
                    "frontend", "web", "app", "client"):
            fp = project_root_path / rel
            if fp.exists():
                frontend_paths.append(str(fp.resolve()))
                break  # Use the first match only
    all_refs = []
    for fp in frontend_paths:
        if Path(fp).exists():
            for symbol in symbols:
                sym_name = symbol.split(":")[-1].strip() if ":" in symbol else symbol
                if len(sym_name) < 3:
                    continue
                refs = find_references(sym_name, project_root=fp)
                all_refs.extend(refs)
    seen = set()
    result = []
    for r in all_refs:
        if r not in seen:
            seen.add(r)
            result.append(r)
    return result

def _extract_symbol_name(raw_sym: str) -> str:
    """Extract pure symbol name from language-agnostic symbol string.

    Examples:
      "field_del:mobile"        → "mobile"
      "field_add:phone"         → "phone"
      "class_del:UserDTO"       → "UserDTO"
      "annotation_add:@NotNull" → "@NotNull"
    """
    name = raw_sym.split(":", 1)[-1].strip() if ":" in raw_sym else raw_sym
    # Clean trailing braces/semicolons from any remaining code snippets
    if re.search(r'[{;]\s*$', name) or (" " in name and len(name) > 30):
        m = re.search(r'(\w+)\s*[;,\)]\s*\}?\s*$', name)
        if m:
            name = m.group(1)
    return name

def map_impact(manifest: dict, translator: Optional[Translator] = None) -> ImpactMatrix:
    """Map diff manifest to business impact matrix.

    Args:
        manifest: Diff manifest dict (from diff_analyzer JSON).
        translator: Optional Translator; defaults to English.
    """
    t = translator or Translator("en")
    matrix = ImpactMatrix(lang=t.lang_for_pipe())
    matrix.summary = manifest.get("summary", "")
    changes = manifest.get("changes", [])
    breaking_count = 0
    major_count = 0

    for ch in changes:
        filepath = ch.get("file", "")
        ext = ch.get("extension", "")
        symbols = ch.get("symbols", [])
        risk_level = ch.get("risk_level", "P2")
        status = ch.get("type", "")

        layer_keyword, layer_key = identify_layer(filepath)
        layer_display = t.t(layer_key)

        # Determine impact level
        matched = match_pattern(symbols, filepath)
        if matched:
            impact_level = matched.get("impact_level", "BREAKING")
        elif risk_level == "P0":
            impact_level = "BREAKING"
        elif risk_level == "P1":
            impact_level = "MAJOR"
        else:
            impact_level = "COMPATIBLE"

        if impact_level == "BREAKING":
            breaking_count += 1
        elif impact_level == "MAJOR":
            major_count += 1

        # Reference search (P0/P1 only, skip added files)
        refs = []
        hist_refs = set()
        if risk_level in ("P0", "P1") and status != "A":
            seen_syms = set()
            unique_syms = []
            for sym in symbols:
                name = _extract_symbol_name(sym)
                if len(name) > 2 and not name.startswith(("@", "//", "/*")) and name not in seen_syms:
                    seen_syms.add(name)
                    unique_syms.append(name)
            for sym_name in unique_syms:
                found = find_references(sym_name, exclude_file=filepath)
                refs.extend(found)
                if risk_level == "P0" and found:
                    hist = find_historical_relations(sym_name)
                    hist_refs.update(hist)

        # Build translated detail
        detail_parts = [layer_display]
        orig_details = ch.get("details", "")
        if orig_details:
            detail_parts.append(orig_details)
        if refs:
            detail_parts.append(t.t("impact.refs_found", count=len(refs)))
        if hist_refs:
            hist_list = ", ".join(sorted(hist_refs)[:5])
            detail_parts.append(t.t("impact.git_history", files=hist_list))
        if symbols:
            display_symbols = []
            for s in symbols[:3]:
                translated = t.translate_symbol(s)
                display_symbols.append(translated)
            detail_parts.append(f"{'; '.join(display_symbols)}")
        if matched:
            detail_parts.append(t.t("impact.matched_pattern", name=matched.get("name", "")))
            if matched.get("scope"):
                detail_parts.append(t.t("impact.pattern_scope", scope=matched["scope"]))
            if matched.get("cost"):
                detail_parts.append(t.t("impact.pattern_cost", cost=matched["cost"]))

        detail = " | ".join(detail_parts) if detail_parts else f"{filepath}"

        matrix.consumer_impacts.append(ConsumerImpact(
            file=filepath,
            impact=impact_level,
            detail=detail
        ))

    # Data migration — check consumer impact (accounts for pattern upgrades)
    sql_breaking_files = {
        ch.get("file") for ch in changes
        if ch.get("extension") in ("sql", "ddl")
    }
    has_sql_breaking = any(
        ci.impact == "BREAKING" and ci.file in sql_breaking_files
        for ci in matrix.consumer_impacts
    )
    if has_sql_breaking:
        matrix.data_migration = DataMigration(
            required=True,
            risk="HIGH",
            detail=t.t("impact.data_migration.detail")
        )

    # API compatibility
    api_impacts = [c for c in matrix.consumer_impacts if c.impact == "BREAKING" and
                   any(kw in c.file.lower() for kw in ["controller", "feign", "api", "dto", "sql", "ddl", "db"])]
    if api_impacts:
        matrix.api_compatibility = ApiCompatibility(
            version_required=True,
            suggestion=t.t("impact.api_compatibility.suggestion")
        )

    # Frontend impact
    all_symbols = sum((ch.get("symbols", []) for ch in changes), [])
    if all_symbols:
        frontend_files = check_frontend_impact(all_symbols)
        if frontend_files:
            matrix.frontend_affected = True
            matrix.frontend_files = frontend_files

    # Overall impact & recommendation
    if breaking_count > 0:
        matrix.overall_impact = "CRITICAL"
        matrix.recommendation = t.t("impact.recommend.critical")
    elif major_count > 0:
        matrix.overall_impact = "MAJOR"
        matrix.recommendation = t.t("impact.recommend.major")
    else:
        matrix.overall_impact = "MINOR"
        matrix.recommendation = t.t("impact.recommend.minor")

    return matrix

def main():
    raw = sys.stdin.read()
    if not raw:
        t = Translator()
        print(t.t("error.pipe_required"), file=sys.stderr)
        print(t.t("error.usage_diff"), file=sys.stderr)
        sys.exit(1)

    data = json.loads(raw)

    # Detect language from pipe JSON, CLI, env, or default
    pipe_lang = data.get("lang") if isinstance(data, dict) else None
    t = Translator(pipe_lang)

    # Parse CLI --lang if provided (overrides pipe)
    if "--lang" in sys.argv:
        try:
            idx = sys.argv.index("--lang")
            if idx + 1 < len(sys.argv) and sys.argv[idx + 1] in ("en", "zh"):
                t = Translator(sys.argv[idx + 1])
        except (ValueError, IndexError):
            pass

    matrix = map_impact(data, t)

    print("=" * 50, file=sys.stderr)
    print(t.t("impact.stderr.analysis_done"), file=sys.stderr)
    print(t.t("impact.stderr.overall_level", level=matrix.overall_impact), file=sys.stderr)
    print(t.t("impact.stderr.breaking_count",
              count=sum(1 for c in matrix.consumer_impacts if c.impact == "BREAKING")), file=sys.stderr)
    if matrix.data_migration.required:
        print(t.t("impact.stderr.data_migration_needed", risk=matrix.data_migration.risk), file=sys.stderr)
    if matrix.api_compatibility.version_required:
        print(t.t("impact.stderr.api_version_needed"), file=sys.stderr)
    if matrix.frontend_affected:
        print(t.t("impact.stderr.frontend_affected"), file=sys.stderr)
    print("=" * 50, file=sys.stderr)
    print(file=sys.stderr)

    result = asdict(matrix)
    result["consumer_impacts"] = [asdict(c) for c in matrix.consumer_impacts]
    result["data_migration"] = asdict(matrix.data_migration)
    result["api_compatibility"] = asdict(matrix.api_compatibility)
    result["lang"] = t.lang_for_pipe()
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
