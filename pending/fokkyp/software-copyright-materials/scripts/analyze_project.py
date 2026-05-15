#!/usr/bin/env python3
"""Analyze a project and produce facts used by the copyright material workflow."""

from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path
from typing import Any

from common import CODE_EXTS, FRONTEND_EXTS, count_text_lines, iter_project_files, read_json, read_text, rel, write_json, normalize_title


DEPENDENCY_FRAMEWORKS = {
    "vue": "Vue",
    "@vue/runtime-core": "Vue",
    "react": "React",
    "next": "Next.js",
    "nuxt": "Nuxt",
    "svelte": "Svelte",
    "astro": "Astro",
    "@angular/core": "Angular",
    "vite": "Vite",
    "uni-app": "UniApp",
    "@dcloudio/uni-app": "UniApp",
    "electron": "Electron",
    "@tauri-apps/api": "Tauri",
}

ENTRY_NAMES = {
    "main.ts",
    "main.js",
    "main.tsx",
    "main.jsx",
    "index.tsx",
    "index.jsx",
    "app.vue",
    "App.vue",
    "app.tsx",
}


def load_package(project: Path) -> tuple[dict[str, Any] | None, Path | None]:
    candidates = [
        project / "package.json",
        project / "frontend/package.json",
        project / "client/package.json",
        project / "web/package.json",
        project / "app/package.json",
    ]
    for package_path in candidates:
        if not package_path.exists():
            continue
        try:
            return read_json(package_path), package_path
        except Exception:
            continue
    return None, None


def detect_frameworks(package: dict[str, Any] | None, files: list[Path], project: Path) -> list[str]:
    found: set[str] = set()
    deps: dict[str, Any] = {}
    if package:
        for key in ("dependencies", "devDependencies", "peerDependencies"):
            deps.update(package.get(key) or {})
        for dep in deps:
            if dep in DEPENDENCY_FRAMEWORKS:
                found.add(DEPENDENCY_FRAMEWORKS[dep])
    suffixes = {p.suffix.lower() for p in files}
    if ".vue" in suffixes:
        found.add("Vue")
    if ".tsx" in suffixes or ".jsx" in suffixes:
        if "Vue" not in found:
            found.add("React")
    if (project / "vite.config.ts").exists() or (project / "vite.config.js").exists():
        found.add("Vite")
    if (project / "next.config.js").exists() or (project / "next.config.ts").exists() or any(p.name in {"next.config.js", "next.config.ts"} for p in files):
        found.add("Next.js")
    return sorted(found)


def classify(path: Path, project: Path) -> str:
    r = rel(path, project).lower()
    name = path.name
    if name in ENTRY_NAMES or r in {"src/app/page.tsx", "src/app/layout.tsx", "app/page.tsx", "app/layout.tsx"} or r.endswith("/src/app/page.tsx") or r.endswith("/src/app/layout.tsx"):
        return "entry"
    if path.suffix.lower() in {".css", ".scss", ".sass", ".less"}:
        return "style"
    if any(part in r for part in ("/router/", "/routes/", "router.", "routes.")):
        return "route"
    if any(part in r for part in ("/pages/", "/views/", "/app/", "/screens/")):
        return "page"
    if "/components/" in r:
        return "component"
    if any(part in r for part in ("/api/", "/apis/", "/services/", "request.", "/request/")):
        return "api"
    if any(part in r for part in ("/store/", "/stores/", "/pinia/", "/redux/", "/zustand/")):
        return "state"
    if any(part in r for part in ("/utils/", "/lib/", "/hooks/", "/composables/")):
        return "utility"
    return "source"


def extract_route_paths(path: Path) -> list[str]:
    try:
        text = read_text(path, limit=200_000)
    except Exception:
        return []
    patterns = [
        r"path\s*:\s*['\"]([^'\"]+)['\"]",
        r"<Route[^>]+path=['\"]([^'\"]+)['\"]",
        r"href=['\"](/[^'\"]*)['\"]",
    ]
    routes: list[str] = []
    for pattern in patterns:
        for match in re.findall(pattern, text):
            if match.startswith("/") and len(match) < 120 and "*" not in match:
                routes.append(match)
    return routes


def summarize_readme(project: Path) -> str:
    for name in ("README.md", "README.zh.md", "readme.md", "Readme.md"):
        path = project / name
        if path.exists():
            text = read_text(path, limit=4000)
            return "\n".join(line.strip() for line in text.splitlines()[:60] if line.strip())
    return ""


def analyze(project: Path) -> dict[str, Any]:
    project = project.resolve()
    package, package_path = load_package(project)
    files = list(iter_project_files(project, CODE_EXTS))
    source_files = [p for p in files if p.suffix.lower() in FRONTEND_EXTS]
    class_counts: Counter[str] = Counter()
    extension_counts: Counter[str] = Counter()
    source_lines = 0
    categorized: dict[str, list[str]] = {
        "entry": [],
        "route": [],
        "page": [],
        "component": [],
        "api": [],
        "state": [],
        "utility": [],
        "style": [],
        "source": [],
    }
    route_paths: list[str] = ["/"]

    for path in source_files:
        category = classify(path, project)
        class_counts[category] += 1
        extension_counts[path.suffix.lower()] += 1
        categorized[category].append(rel(path, project))
        source_lines += count_text_lines(path)
        if category in {"route", "page", "entry"}:
            route_paths.extend(extract_route_paths(path))

    package_name = ""
    scripts: dict[str, str] = {}
    dependencies: dict[str, str] = {}
    if package:
        package_name = str(package.get("name") or "")
        scripts = {k: str(v) for k, v in (package.get("scripts") or {}).items()}
        for key in ("dependencies", "devDependencies"):
            dependencies.update({k: str(v) for k, v in (package.get(key) or {}).items()})

    frameworks = detect_frameworks(package, source_files, project)
    language = infer_language(extension_counts, frameworks)
    route_paths = sorted(set(route_paths), key=lambda x: (x.count("/"), x))

    return {
        "project_root": str(project),
        "project_name": project.name,
        "software_name_candidate": normalize_title(package_name or project.name),
        "package": {
            "name": package_name,
            "path": rel(package_path, project) if package_path else "",
            "version": str(package.get("version") or "V1.0") if package else "V1.0",
            "scripts": scripts,
            "dependency_names": sorted(dependencies),
        },
        "frameworks": frameworks,
        "language": language,
        "source": {
            "file_count": len(source_files),
            "line_count": source_lines,
            "extension_counts": dict(sorted(extension_counts.items())),
            "category_counts": dict(sorted(class_counts.items())),
            "categorized_files": {k: v[:80] for k, v in categorized.items() if v},
        },
        "routes": route_paths[:80],
        "readme_excerpt": summarize_readme(project),
        "run_command_candidates": infer_run_commands(scripts),
        "feature_candidates": infer_features(categorized, route_paths),
    }


def infer_workdir(out: Path) -> Path:
    if out.parent.name == "analysis":
        return out.parent.parent
    return out.parent


def check_environment_gate(out: Path) -> None:
    workdir = infer_workdir(out)
    env_path = workdir / "环境检查.json"
    if not env_path.exists():
        return
    env = read_json(env_path)
    if not env.get("requires_user_input"):
        return
    confirmation_path = workdir / "环境确认.json"
    confirmed = False
    if confirmation_path.exists():
        confirmed = bool(read_json(confirmation_path).get("environment_confirmed"))
    if not confirmed:
        raise SystemExit(
            "STOP_FOR_USER\n"
            "NEXT_ACTION: 完整 DOCX 环境未确认。请先让用户选择安装完整环境或使用基础 DOCX 兜底继续，"
            "然后运行 `python3 scripts/confirm_stage.py --workdir 软件著作权申请资料 --stage environment --note \"<用户选择>\"`。"
        )


def infer_language(extension_counts: Counter[str], frameworks: list[str]) -> str:
    langs: list[str] = []
    if "Vue" in frameworks:
        langs.append("Vue")
    if "React" in frameworks or "Next.js" in frameworks:
        langs.append("React")
    if extension_counts.get(".ts") or extension_counts.get(".tsx"):
        langs.append("TypeScript")
    if extension_counts.get(".js") or extension_counts.get(".jsx"):
        langs.append("JavaScript")
    if not langs:
        langs = [ext.lstrip(".").upper() for ext, _ in extension_counts.most_common(3)]
    return "、".join(dict.fromkeys(langs)) or "待用户确认"


def infer_run_commands(scripts: dict[str, str]) -> list[str]:
    preferred = ["dev", "start", "serve", "preview"]
    commands = []
    for name in preferred:
        if name in scripts:
            commands.append(f"npm run {name}")
    return commands


def infer_features(categorized: dict[str, list[str]], routes: list[str]) -> list[str]:
    stop = {
        "index",
        "main",
        "app",
        "layout",
        "page",
        "globals",
        "providers",
        "loading",
        "error",
        "not-found",
        "template",
        "default",
        "button",
        "input",
        "label",
        "avatar",
        "card",
        "textarea",
        "scroll area",
    }
    names: list[str] = []
    for route in routes:
        cleaned = route.strip("/").replace("-", " ").replace("_", " ")
        if cleaned and not cleaned.startswith(":") and cleaned.lower() not in stop:
            names.append(cleaned)
    for file in categorized.get("page", [])[:60]:
        route_name = feature_from_page_path(file)
        if route_name and route_name.lower() not in stop:
            names.append(route_name)
    for category in ("api", "component"):
        for file in categorized.get(category, [])[:30]:
            lowered = file.lower()
            if "/ui/" in lowered or "/components/ui/" in lowered:
                continue
            stem = Path(file).stem
            normalized = stem.replace("-", " ").replace("_", " ").strip()
            if normalized.lower() not in stop:
                names.append(normalized)
    unique: list[str] = []
    for name in names:
        normalized = re.sub(r"\s+", " ", name).strip()
        if normalized and normalized not in unique:
            unique.append(normalized)
    return unique[:30]


def feature_from_page_path(file: str) -> str:
    parts = Path(file).parts
    useful: list[str] = []
    for part in parts:
        if part in {"src", "app", "pages", "views", "screens", "frontend", "client", "web"}:
            continue
        if part.startswith("(") and part.endswith(")"):
            continue
        stem = Path(part).stem
        if stem in {"page", "layout", "index", "route", "loading", "error", "globals", "providers"}:
            continue
        if stem.startswith("[") and stem.endswith("]"):
            continue
        useful.append(stem)
    return " ".join(useful[-2:]).replace("-", " ").replace("_", " ").strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True, help="Project root directory")
    parser.add_argument("--out", default="软件著作权申请资料/analysis/project.json")
    args = parser.parse_args()

    project = Path(args.project)
    if not project.exists():
        raise SystemExit(f"Project not found: {project}")

    out = Path(args.out)
    check_environment_gate(out)
    result = analyze(project)
    write_json(out, result)
    print(f"OK analysis: {out}")
    print(f"Project: {result['project_name']}")
    print(f"Frameworks: {', '.join(result['frameworks']) or 'unknown'}")
    print(f"Language: {result['language']}")
    print(f"Source files: {result['source']['file_count']}")
    print(f"Source lines: {result['source']['line_count']}")


if __name__ == "__main__":
    main()
