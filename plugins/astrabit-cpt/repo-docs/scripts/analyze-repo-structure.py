#!/usr/bin/env python3
"""
Analyze repository structure and generate summary for documentation.

Usage: python analyze-repo-structure.py [repo_path]
Output: JSON summary of repo structure, technologies, and patterns detected
"""

import argparse
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional


# Technology detection patterns
TECH_PATTERNS = {
    "javascript_typescript": {
        "files": ["package.json", "tsconfig.json"],
        "extensions": [".ts", ".tsx", ".js", ".jsx"],
    },
    "python": {
        "files": ["pyproject.toml", "requirements.txt", "setup.py", "Pipfile"],
        "extensions": [".py"],
    },
    "go": {
        "files": ["go.mod", "go.sum"],
        "extensions": [".go"],
    },
    "rust": {
        "files": ["Cargo.toml", "Cargo.lock"],
        "extensions": [".rs"],
    },
    "java": {
        "files": ["pom.xml", "build.gradle", "build.gradle.kts"],
        "extensions": [".java", ".kt"],
    },
    "ruby": {
        "files": ["Gemfile", "Rakefile"],
        "extensions": [".rb"],
    },
    "csharp": {
        "files": [".csproj", "packages.config"],
        "extensions": [".cs"],
    },
    "php": {
        "files": ["composer.json"],
        "extensions": [".php"],
    },
}


# Framework detection patterns
FRAMEWORK_PATTERNS = {
    "react": ["package.json:react"],
    "vue": ["package.json:vue", ".vue files"],
    "angular": ["angular.json", "package.json:@angular/"],
    "nextjs": ["next.config.js", "app/ directory", "pages/ directory"],
    "django": ["manage.py", "settings.py"],
    "fastapi": ["pyproject.toml:fastapi", "requirements.txt:fastapi"],
    "flask": ["requirements.txt:Flask", "app.py:Flask"],
    "spring_boot": ["pom.xml:spring-boot", "@SpringBootApplication"],
    "gin": ["go.mod:gin-gonic"],
    "echo": ["go.mod:labstack/echo"],
}


# Integration point patterns (regex)
INTEGRATION_PATTERNS = {
    "internal_package_js": r"@[\w-]+/[\w-]+",
    "internal_package_py": r"from\s+(?:[\w.]+\.)?internal\.|import\s+(?:[\w.]+\.)?internal\.",
    "go_module": r"github\.com/[\w-]+/[\w-]+",
    "java_internal": r"import\s+com\.[\w.]+\.",
    "http_client": r"\b(fetch|axios|RestTemplate|WebClient|requests|httpx)\b",
    "grpc": r"\bgrpc\.|grpc/|@grpc/grpc-js",
    "kafka": r"\bkafka\.|kafka-|kafka\(",
    "database": r"\b(prisma|mongoose|sequelize|typeorm|sqlalchemy|psycopg|pymongo)\b",
}


def detect_language(repo_path: Path) -> List[str]:
    """Detect primary programming languages."""
    detected = []
    for lang, patterns in TECH_PATTERNS.items():
        for file in patterns["files"]:
            if (repo_path / file).exists():
                detected.append(lang)
                break
        if not detected or lang in detected:
            for ext in patterns["extensions"]:
                if list(repo_path.rglob(f"*{ext}")):
                    if lang not in detected:
                        detected.append(lang)
                    break
    return detected


def detect_frameworks(repo_path: Path, languages: List[str]) -> List[str]:
    """Detect frameworks based on language and files."""
    frameworks = []
    for framework, indicators in FRAMEWORK_PATTERNS.items():
        for indicator in indicators:
            if ":" in indicator:
                file, pattern = indicator.split(":", 1)
                file_path = repo_path / file
                if file_path.exists():
                    content = file_path.read_text()
                    if pattern in content:
                        frameworks.append(framework)
                        break
            elif " " in indicator:
                # Directory or file pattern
                if (repo_path / indicator).exists():
                    frameworks.append(framework)
                    break
            else:
                if (repo_path / indicator).exists():
                    frameworks.append(framework)
                    break
    return list(set(frameworks))


def find_integration_points(repo_path: Path, languages: List[str]) -> Dict[str, List[str]]:
    """Search for cross-repository integration points."""
    integrations = {}

    # Define file extensions to search based on detected languages
    ext_map = {
        "javascript_typescript": [".ts", ".tsx", ".js", ".jsx"],
        "python": [".py"],
        "go": [".go"],
        "java": [".java", ".kt"],
        "rust": [".rs"],
        "ruby": [".rb"],
        "csharp": [".cs"],
        "php": [".php"],
    }

    extensions = []
    for lang in languages:
        extensions.extend(ext_map.get(lang, []))

    if not extensions:
        return integrations

    # Search for integration patterns
    for pattern_name, pattern in INTEGRATION_PATTERNS.items():
        matches = set()
        regex = re.compile(pattern)
        for ext in extensions:
            for file_path in repo_path.rglob(f"*{ext}"):
                try:
                    content = file_path.read_text()
                    for match in regex.findall(content):
                        matches.add(match)
                except Exception:
                    continue
        if matches:
            integrations[pattern_name] = sorted(list(matches))

    return integrations


def find_directories(repo_path: Path) -> Dict[str, List[str]]:
    """Find common directory structures."""
    dirs = {
        "source": [],
        "config": [],
        "docs": [],
        "tests": [],
        "scripts": [],
    }

    common_dirs = {
        "source": ["src", "lib", "app", "internal", "pkg", "handler", "server"],
        "config": ["config", "configs", ".config", "settings", "k8s", "kube", "docker"],
        "docs": ["docs", "doc", "documentation", "wiki"],
        "tests": ["tests", "test", "__tests__", "spec", "specs"],
        "scripts": ["scripts", "bin", "tools", "hack"],
    }

    for category, dir_names in common_dirs.items():
        for dir_name in dir_names:
            if (repo_path / dir_name).is_dir():
                dirs[category].append(dir_name)

    return dirs


def find_ci_cd(repo_path: Path) -> List[str]:
    """Detect CI/CD platforms."""
    ci_indicators = {
        "GitHub Actions": ".github/workflows",
        "GitLab CI": ".gitlab-ci.yml",
        "CircleCI": ".circleci/config.yml",
        "Travis CI": ".travis.yml",
        "Jenkins": "Jenkinsfile",
        "Azure Pipelines": "azure-pipelines.yml",
        "Bitbucket": "bitbucket-pipelines.yml",
    }

    detected = []
    for platform, indicator in ci_indicators.items():
        if "/" in indicator:
            if (repo_path / indicator).exists():
                detected.append(platform)
        else:
            if (repo_path / indicator).exists():
                detected.append(platform)

    return detected


def analyze(repo_path: Path) -> Dict:
    """Perform complete repository analysis."""
    languages = detect_language(repo_path)
    frameworks = detect_frameworks(repo_path, languages)
    integrations = find_integration_points(repo_path, languages)
    directories = find_directories(repo_path)
    ci_cd = find_ci_cd(repo_path)

    return {
        "path": str(repo_path),
        "languages": languages,
        "frameworks": frameworks,
        "directories": directories,
        "ci_cd": ci_cd,
        "integration_points": integrations,
    }


def main():
    parser = argparse.ArgumentParser(description="Analyze repository structure")
    parser.add_argument("repo_path", nargs="?", default=".", help="Path to repository")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    repo_path = Path(args.repo_path).resolve()

    if not repo_path.exists():
        print(f"Error: Path '{repo_path}' does not exist")
        return 1

    result = analyze(repo_path)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"# Repository Analysis: {repo_path.name}\n")
        print(f"**Languages:** {', '.join(result['languages']) or 'Unknown'}")
        print(f"**Frameworks:** {', '.join(result['frameworks']) or 'None detected'}")
        print(f"**CI/CD:** {', '.join(result['ci_cd']) or 'None detected'}")

        print("\n## Directory Structure")
        for category, dirs in result['directories'].items():
            if dirs:
                print(f"- {category.capitalize()}: {', '.join(dirs)}")

        if result['integration_points']:
            print("\n## Potential Integration Points")
            for pattern, matches in result['integration_points'].items():
                print(f"- {pattern}: {', '.join(matches[:5])}")
                if len(matches) > 5:
                    print(f"  ... and {len(matches) - 5} more")

    return 0


if __name__ == "__main__":
    exit(main())
