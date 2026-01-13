#!/usr/bin/env python3
"""
Generate catalog-info.yaml metadata for a repository.

Usage: python generate-metadata.py [repo_path]
Output: catalog-info.yaml content

This script analyzes a repository to generate structured metadata
following the Astrabit catalog-info.yaml schema (based on Backstage conventions.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set


# Technology detection patterns
LANGUAGE_PATTERNS = {
    "nodejs": ["package.json", "tsconfig.json"],
    "python": ["pyproject.toml", "requirements.txt", "setup.py", "Pipfile"],
    "go": ["go.mod"],
    "java": ["pom.xml", "build.gradle", "build.gradle.kts"],
    "rust": ["Cargo.toml"],
    "ruby": ["Gemfile"],
}

FRAMEWORK_PATTERNS = {
    "nestjs": ["package.json:@nestjs/core"],
    "fastapi": ["pyproject.toml:fastapi", "requirements.txt:fastapi"],
    "flask": ["requirements.txt:Flask"],
    "django": ["requirements.txt:Django", "manage.py"],
    "spring": ["pom.xml:spring-boot", "@SpringBootApplication"],
    "echo": ["go.mod:labstack/echo"],
    "gin": ["go.mod:gin-gonic"],
}


def detect_language_and_framework(repo_path: Path) -> tuple[str, str]:
    """Detect runtime and framework from repo files."""
    runtime = "unknown"
    framework = "none"

    for lang, files in LANGUAGE_PATTERNS.items():
        for file in files:
            if ":" in file:
                f, pattern = file.split(":")
                file_path = repo_path / f
                if file_path.exists():
                    content = file_path.read_text()
                    if pattern in content:
                        runtime = lang
                        break
            else:
                if (repo_path / file).exists():
                    runtime = lang
                    break
        if runtime != "unknown":
            break

    for fw, patterns in FRAMEWORK_PATTERNS.items():
        for pattern in patterns:
            if ":" in pattern:
                file, search = pattern.split(":")
                file_path = repo_path / file
                if file_path.exists():
                    content = file_path.read_text()
                    if search in content:
                        framework = fw
                        break
            else:
                if (repo_path / pattern).exists():
                    framework = fw
                    break
        if framework != "none":
            break

    return runtime, framework


def find_integration_points(repo_path: Path) -> Dict[str, List[str]]:
    """Find integration points by scanning code."""
    integrations = {
        "http_clients": [],
        "kafka_producers": [],
        "kafka_consumers": [],
        "grpc_clients": [],
        "databases": [],
    }

    # Pattern definitions
    patterns = {
        "http_clients": [
            (r"@nestjs/axios|axios|fetch\s*\(|RestTemplate|WebClient",
             [".ts", ".js", ".java", ".kt"]),
        ],
        "kafka_producers": [
            (r"ClientProxy\.send|kafka\.producer|@KafkaTemplate|KafkaTemplate",
             [".ts", ".js", ".java", ".kt", ".py"]),
        ],
        "kafka_consumers": [
            (r"@EventPattern|@KafkaListener|@EventListener|kafka\.consumer",
             [".ts", ".js", ".java", ".kt", ".py"]),
        ],
        "grpc_clients": [
            (r"@grpc/grpc-js|grpc\.Client|@GrpcClient",
             [".ts", ".js", ".go", ".py"]),
        ],
        "databases": [
            (r"TypeORM|PrismaClient|mongoose|sequelize|sqlalchemy|psycopg",
             [".ts", ".js", ".py"]),
        ],
    }

    for category, category_patterns in patterns.items():
        for pattern, extensions in category_patterns:
            regex = re.compile(pattern)
            for ext in extensions:
                for file_path in repo_path.rglob(f"*{ext}"):
                    try:
                        content = file_path.read_text()
                        if regex.search(content):
                            # Add unique entries
                            if category not in integrations:
                                integrations[category] = []
                            integrations[category].append(str(file_path.relative_to(repo_path)))
                    except Exception:
                        continue

    return {k: list(set(v)) for k, v in integrations.items() if v}


def detect_service_type(integrations: Dict, repo_path: Path) -> str:
    """
    Detect service type based on patterns.

    Returns: service, gateway, worker, library, frontend, database
    """
    # Check for frontend
    if any((repo_path / f).exists() for f in ["package.json"]):
        package_json = repo_path / "package.json"
        if package_json.exists():
            try:
                content = package_json.read_text()
                if '"type": "frontend"' in content or re.search(r'"next"|react|vue|angular', content):
                    # Check if it has API routes - could be Next.js API
                    if not (repo_path / "pages/api").exists() and not (repo_path / "app/api").exists():
                        return "frontend"
            except Exception:
                pass

    # Check for database
    if (repo_path / "migrations").exists() or (repo_path / "schema.sql").exists():
        # But also check if it's a service with migrations
        if not (repo_path / "src").exists() and not (repo_path / "app").exists():
            return "database"

    has_http = bool(integrations.get("http_clients", []))
    has_kafka_prod = bool(integrations.get("kafka_producers", []))
    has_kafka_cons = bool(integrations.get("kafka_consumers", []))

    # Gateway: has HTTP clients but no consumers (routes to others)
    # Service: has both producers and consumers
    # Worker: only consumers (background processing)
    if has_kafka_cons and not has_kafka_prod and not has_http:
        return "worker"

    if has_http and not has_kafka_cons:
        # Could be a gateway - check for routing patterns
        return "gateway"

    if has_http or has_kafka_prod or has_kafka_cons:
        return "service"

    return "library"


def read_existing_docs(repo_path: Path) -> Dict:
    """Read existing documentation for metadata."""
    docs = {
        "readme": None,
        "integrations": None,
        "architecture": None,
    }

    for doc_name, doc_path in [
        ("readme", "README.md"),
        ("integrations", "INTEGRATIONS.md"),
        ("architecture", "ARCHITECTURE.md"),
    ]:
        path = repo_path / doc_path
        if path.exists():
            try:
                docs[doc_name] = path.read_text()
            except Exception:
                pass

    return docs


def extract_name(repo_path: Path) -> str:
    """Extract component name from repo."""
    # Try package.json
    package_json = repo_path / "package.json"
    if package_json.exists():
        try:
            content = package_json.read_text()
            match = re.search(r'"name"\s*:\s*"([^"]+)"', content)
            if match:
                return match.group(1).replace("@", "").replace("/", "-")
        except Exception:
            pass

    # Try pyproject.toml
    pyproject = repo_path / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text()
            match = re.search(r'name\s*=\s*"([^"]+)"', content)
            if match:
                return match.group(1)
        except Exception:
            pass

    # Use directory name
    return repo_path.name.lower().replace("_", "-")


def generate_catalog_info(repo_path: Path) -> Dict:
    """Generate catalog-info.yaml structure."""
    repo_path = repo_path.resolve()

    # Detect basic info
    name = extract_name(repo_path)
    runtime, framework = detect_language_and_framework(repo_path)
    integrations = find_integration_points(repo_path)
    docs = read_existing_docs(repo_path)

    # Detect service type
    service_type = detect_service_type(integrations, repo_path)

    # Detect domain and owner from patterns
    domain, owner = detect_domain_and_owner(repo_path.name)

    # Extract description from README
    description = ""
    if docs.get("readme"):
        lines = docs["readme"].split("\n")[:5]
        for line in lines:
            line = line.strip("#").strip()
            if line and not line.startswith("#"):
                description = line
                break

    # Build catalog info
    catalog = {
        "apiVersion": "astrabit.io/v1",
        "kind": "Component",
        "metadata": {
            "name": name,
            "description": description or f"{service_type} component",
            "tags": [service_type, runtime, domain],
        },
        "spec": {
            "type": service_type,
            "category": "frontend" if service_type == "frontend" else "backend",
            "domain": domain,
            "owner": owner,
            "lifecycle": "production",
            "runtime": runtime,
            "framework": framework,
        },
    }

    # Add dependencies based on integrations
    depends_on = []
    if integrations.get("databases"):
        depends_on.append({"component": "database", "type": "database"})
    if integrations.get("kafka_consumers"):
        depends_on.append({"component": "kafka", "type": "message-queue"})

    if depends_on:
        catalog["spec"]["dependsOn"] = depends_on

    # Add events
    if integrations.get("kafka_producers"):
        catalog["spec"]["eventProducers"] = [
            {"name": "events", "type": "kafka", "topic": "unknown", "schema": "unknown"}
        ]
    if integrations.get("kafka_consumers"):
        catalog["spec"]["eventConsumers"] = [
            {"name": "events", "type": "kafka", "topic": "unknown", "group": f"{name}-group"}
        ]

    # Add routes for gateways and services
    if service_type in ["gateway", "service"]:
        catalog["spec"]["providesApis"] = [
            {"name": f"{name.capitalize()} API", "type": "REST", "definition": "./openapi.yaml"}
        ]

        if service_type == "gateway":
            catalog["spec"]["routes"] = [
                {"path": "/api/*", "methods": ["GET", "POST", "PUT", "DELETE"], "forwardsTo": "unknown"}
            ]

    return catalog


def detect_domain_and_owner(repo_name: str) -> tuple[str, str]:
    """Detect domain and owner from repository name patterns."""
    # Domain patterns
    domain_patterns = {
        "trading": ["*gateway", "*service", "order-log", "trade-pair", "exchange",
                    "tradingview", "copy", "bot", "portfolio", "position", "strategy",
                    "signal", "commission", "promo-code", "payment", "nexus"],
        "user": ["user-*", "glob-*", "kyc"],
        "product": ["product-*"],
        "infrastructure": ["devops", "*-iac", "docker-compose", "concourse",
                          "proxy-manager", "event-bus", "uptime-watcher", "migrate-db"],
        "data": ["public-data", "kline-crawler", "exchange-data", "indicator",
                 "geometry", "ml-*", "*-adapter", "database-schema"],
        "frontend": ["*-frontend", "*-web", "*-app", "*-panel", "web", "adex-*",
                     "glob-*", "charting-library"],
        "integrations": ["discord", "zammad", "wordpress", "mailhog", "keycloak"],
        "platform": ["defi", "staking"],
        "documentation": ["wiki", "docs"],
    }

    # Team patterns
    team_patterns = {
        "trading-team": ["*gateway", "*service", "exchange", "tradingview", "bot",
                          "strategy", "signal", "commission", "position", "portfolio"],
        "backend-team": ["user-*", "product-*", "payment", "kyc", "promo-code"],
        "frontend-team": ["*-frontend", "*-web", "*-app", "*-panel", "adex-*", "glob-*"],
        "infrastructure-team": ["devops", "*-iac", "docker-compose", "concourse"],
        "data-team": ["*data", "*crawler", "indicator", "ml-*", "geometry"],
        "platform-team": ["defi", "staking"],
    }

    def match(name: str, patterns: list) -> bool:
        for pattern in patterns:
            if "*" in pattern:
                regex = "^" + pattern.replace("*", ".*") + "$"
                if re.match(regex, name, re.IGNORECASE):
                    return True
            elif pattern.lower() in name.lower():
                return True
        return False

    # Detect domain
    domain = "unknown"
    for d, patterns in domain_patterns.items():
        if match(repo_name, patterns):
            domain = d
            break

    # Detect team
    team = "unknown"
    for t, patterns in team_patterns.items():
        if match(repo_name, patterns):
            team = t
            break

    # Map team to owner format
    owner_map = {
        "trading-team": "trading-team",
        "backend-team": "backend-team",
        "frontend-team": "frontend-team",
        "infrastructure-team": "infrastructure-team",
        "data-team": "data-team",
        "platform-team": "platform-team",
    }
    owner = owner_map.get(team, team)

    return domain, owner


def to_yaml(data: Dict, indent: int = 0) -> str:
    """Simple YAML converter for catalog info."""
    lines = []

    def dump(obj, depth=0, in_list=False):
        if isinstance(obj, dict):
            if in_list and depth == 0:
                # Top-level dict in list - just dump key-value pairs on same line
                pass
            for k, v in obj.items():
                if v is None:
                    continue
                if isinstance(v, dict):
                    if v:
                        lines.append("  " * depth + f"{k}:")
                        dump(v, depth + 1, False)
                elif isinstance(v, list):
                    if v:
                        lines.append("  " * depth + f"{k}:")
                        dump(v, depth + 1, False)
                else:
                    lines.append("  " * depth + f"{k}: {yaml_val(v)}")
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, dict):
                    # First line opens the dict
                    first = True
                    for k, v in item.items():
                        if v is None:
                            continue
                        if first:
                            # First key on same line as dash
                            if isinstance(v, (dict, list)):
                                if v:
                                    lines.append("  " * depth + f"- {k}:")
                                    dump(v, depth + 1, False)
                                else:
                                    lines.append("  " * depth + f"- {k}: null")
                            else:
                                lines.append("  " * depth + f"- {k}: {yaml_val(v)}")
                            first = False
                        else:
                            # Subsequent keys indented
                            if isinstance(v, dict):
                                if v:
                                    lines.append("  " * (depth + 1) + f"{k}:")
                                    dump(v, depth + 2, False)
                            elif isinstance(v, list):
                                if v:
                                    lines.append("  " * (depth + 1) + f"{k}:")
                                    dump(v, depth + 2, False)
                            else:
                                lines.append("  " * (depth + 1) + f"{k}: {yaml_val(v)}")
                elif isinstance(item, list):
                    if item:
                        lines.append("  " * depth + "-")
                        dump(item, depth + 1, True)
                else:
                    lines.append("  " * depth + f"- {yaml_val(item)}")

    def yaml_val(v):
        if isinstance(v, bool):
            return "true" if v else "false"
        if isinstance(v, str):
            # Quote strings that have special characters or look like booleans
            if v in ["true", "false", "null"] or v.startswith(":") or " " in v:
                return f'"{v}"'
            return v
        return str(v)

    dump(data)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate catalog-info.yaml for a repository"
    )
    parser.add_argument("repo_path", nargs="?", default=".", help="Path to repository")
    parser.add_argument("--format", choices=["yaml", "json"], default="yaml",
                       help="Output format")
    args = parser.parse_args()

    repo_path = Path(args.repo_path)

    if not repo_path.exists():
        print(f"Error: Path '{repo_path}' does not exist", file=sys.stderr)
        return 1

    catalog = generate_catalog_info(repo_path)

    if args.format == "json":
        print(json.dumps(catalog, indent=2))
    else:
        print(to_yaml(catalog))

    return 0


if __name__ == "__main__":
    sys.exit(main())
