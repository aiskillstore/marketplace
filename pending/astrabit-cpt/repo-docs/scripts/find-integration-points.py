#!/usr/bin/env python3
"""
Find cross-repository integration points in a codebase.

Usage: python find-integration-points.py [repo_path]
Output: List of potential integration points with other repositories
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple


# Patterns for finding integration points
# Format: (name, regex_pattern, file_extensions, description)
INTEGRATION_PATTERNS = [
    (
        "internal_npm_package",
        r'@[\w-]+/[\w-]+',
        [".ts", ".tsx", ".js", ".jsx"],
        "Internal npm packages (scoped packages)"
    ),
    (
        "go_module_import",
        r'github\.com/[\w-]+/[\w-]+',
        [".go"],
        "Go module imports from GitHub"
    ),
    (
        "python_internal_import",
        r'(?:from|import)\s+(?:[\w.]+\.)?(internal|shared|common)\.',
        [".py"],
        "Python internal/shared imports"
    ),
    (
        "java_company_import",
        r'import\s+com\.[\w.]+\.',
        [".java", ".kt"],
        "Java company/internal imports"
    ),
    (
        "dotnet_company_import",
        r'using\s+[\w.]+\.',
        [".cs"],
        "C# company/internal imports"
    ),
    (
        "http_fetch_calls",
        r'\bfetch\s*\(',
        [".ts", ".tsx", ".js", ".jsx", ".py", ".go"],
        "HTTP fetch calls (potential API calls)"
    ),
    (
        "axios_imports",
        r"import.*from\s+['\"]axios['\"]|require\(['\"]axios['\"]\)",
        [".ts", ".tsx", ".js", ".jsx"],
        "Axios HTTP client imports"
    ),
    (
        "grpc_import",
        r"@grpc/grpc-js|grpc\.|@grpc/",
        [".ts", ".tsx", ".js", ".jsx", ".go", ".py"],
        "gRPC imports"
    ),
    (
        "kafka_imports",
        r'kafka-|kafka\.|from\s+kafka',
        [".ts", ".tsx", ".js", ".jsx", ".py", ".go"],
        "Kafka client imports"
    ),
    (
        "redis_imports",
        r'redis\.|from\s+redis|import.*redis',
        [".ts", ".tsx", ".js", ".jsx", ".py", ".go"],
        "Redis client imports"
    ),
    (
        "graphql_import",
        r'graphql|@apollo/client|urql',
        [".ts", ".tsx", ".js", ".jsx"],
        "GraphQL client imports"
    ),
    (
        "rest_template",
        r'\bRestTemplate\b|WebClient|RestClient',
        [".java", ".kt"],
        "Java REST clients (RestTemplate, WebClient)"
    ),
    (
        "python_http_imports",
        r'(from\s+(requests|httpx|urllib|aiohttp))|(import\s+(requests|httpx|urllib|aiohttp))',
        [".py"],
        "Python HTTP library imports"
    ),
    (
        "database_client",
        r'\b(prisma|mongoose|sequelize|typeorm|knex|sqlalchemy|psycopg|pymongo)\b',
        [".ts", ".tsx", ".js", ".jsx", ".py"],
        "Database ORM/client imports"
    ),
    (
        "aws_sdk",
        r'@aws-sdk/|aws-sdk|boto3\.|import\s+boto',
        [".ts", ".tsx", ".js", ".jsx", ".py"],
        "AWS SDK imports"
    ),
    (
        "azure_sdk",
        r'@azure/|azure\.identity|azure\.storage',
        [".ts", ".tsx", ".js", ".jsx", ".py"],
        "Azure SDK imports"
    ),
]


def search_file_for_patterns(file_path: Path, patterns: List[Tuple]) -> Dict[str, Set[str]]:
    """Search a single file for all integration patterns."""
    results = {}

    try:
        content = file_path.read_text()
    except Exception:
        return results

    for name, pattern, extensions, _ in patterns:
        if file_path.suffix in extensions:
            matches = re.findall(pattern, content)
            if matches:
                if name not in results:
                    results[name] = set()
                results[name].update(matches)

    return results


def find_integration_points(repo_path: Path, exclude_dirs: List[str] = None) -> Dict[str, Dict]:
    """Scan repository for integration points."""
    if exclude_dirs is None:
        exclude_dirs = ["node_modules", ".git", "vendor", "target", "dist", "build",
                        "__pycache__", ".venv", "venv", "env", ".next", ".nuxt"]

    results = {}
    patterns_by_file = {}
    file_count = 0

    # First pass: collect all matches
    for file_path in repo_path.rglob("*"):
        if not file_path.is_file():
            continue

        # Skip excluded directories
        if any(excluded in file_path.parts for excluded in exclude_dirs):
            continue

        file_results = search_file_for_patterns(file_path, INTEGRATION_PATTERNS)
        if file_results:
            relative_path = file_path.relative_to(repo_path)
            patterns_by_file[str(relative_path)] = file_results
            file_count += 1

            for pattern_name, matches in file_results.items():
                if pattern_name not in results:
                    results[pattern_name] = {
                        "matches": set(),
                        "files": [],
                        "description": next(
                            (p[3] for p in INTEGRATION_PATTERNS if p[0] == pattern_name),
                            "Unknown"
                        )
                    }
                results[pattern_name]["matches"].update(matches)

    # Convert sets to sorted lists
    for pattern_name in results:
        results[pattern_name]["matches"] = sorted(list(results[pattern_name]["matches"]))
        # Find files that have this pattern
        matching_files = [
            {"file": f, "matches": list(patterns_by_file[f][pattern_name])}
            for f in patterns_by_file
            if pattern_name in patterns_by_file[f]
        ]
        results[pattern_name]["files"] = matching_files
        results[pattern_name]["file_count"] = len(matching_files)

    return results


def print_results(results: Dict[str, Dict], format: str = "markdown"):
    """Print integration point results."""
    if format == "markdown":
        print("# Integration Points Found\n")
        for pattern_name, data in sorted(results.items(), key=lambda x: -x[1]["file_count"]):
            print(f"## {data['description']}")
            print(f"**Pattern:** `{pattern_name}` | **Files:** {data['file_count']}\n")
            if data["matches"]:
                print("**Matches:**")
                for match in data["matches"][:20]:
                    print(f"- `{match}`")
                if len(data["matches"]) > 20:
                    print(f"- ... and {len(data['matches']) - 20} more")
            print()
    elif format == "json":
        import json
        # Convert sets to lists for JSON serialization
        json_results = {}
        for pattern_name, data in results.items():
            json_results[pattern_name] = {
                "description": data["description"],
                "matches": data["matches"],
                "file_count": data["file_count"],
            }
        print(json.dumps(json_results, indent=2))
    else:  # plain
        for pattern_name, data in sorted(results.items(), key=lambda x: -x[1]["file_count"]):
            print(f"\n{data['description']}")
            print(f"Pattern: {pattern_name}")
            print(f"Files: {data['file_count']}")
            print(f"Matches: {', '.join(data['matches'][:10])}")
            if len(data["matches"]) > 10:
                print(f"  ... and {len(data['matches']) - 10} more")


def main():
    parser = argparse.ArgumentParser(
        description="Find cross-repository integration points in a codebase"
    )
    parser.add_argument("repo_path", nargs="?", default=".", help="Path to repository")
    parser.add_argument("--format", "-f", choices=["markdown", "json", "plain"],
                       default="markdown", help="Output format")
    parser.add_argument("--exclude", "-e", action="append", dest="exclude_dirs",
                       help="Directories to exclude (can be used multiple times)")
    args = parser.parse_args()

    repo_path = Path(args.repo_path).resolve()

    if not repo_path.exists():
        print(f"Error: Path '{repo_path}' does not exist", file=sys.stderr)
        return 1

    exclude_dirs = args.exclude_dirs
    results = find_integration_points(repo_path, exclude_dirs)

    if not results:
        print("No integration points found.")
        return 0

    print_results(results, args.format)
    return 0


if __name__ == "__main__":
    sys.exit(main())
