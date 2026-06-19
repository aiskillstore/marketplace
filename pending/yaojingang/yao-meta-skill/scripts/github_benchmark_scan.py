#!/usr/bin/env python3
import argparse
import json
import os
import re
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen


API_ROOT = "https://api.github.com"
API_VERSION = "2022-11-28"
USER_AGENT = "yao-meta-skill/1.0"
DEFAULT_TOP_N = 3
DEFAULT_PER_PAGE = 8
MIN_STARS = 50
ALLOWED_API_HOSTS = {"api.github.com"}

STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "into",
    "from",
    "this",
    "that",
    "your",
    "will",
    "make",
    "turn",
    "build",
    "create",
    "reusable",
    "skill",
    "package",
    "agent",
    "workflow",
    "prompt",
    "notes",
    "docs",
    "internal",
    "team",
    "real",
    "output",
    "outputs",
    "input",
    "inputs",
}

PATTERN_RULES = [
    {
        "category": "method",
        "keywords": ["workflow", "process", "pipeline", "orchestrat", "runbook", "playbook"],
        "borrow": "Borrow the way it turns a messy workflow into a repeatable operating path.",
        "avoid": "Do not import process overhead that only exists for that project's scale.",
    },
    {
        "category": "execution",
        "keywords": ["cli", "command", "shell", "script", "automation", "toolchain"],
        "borrow": "Borrow the clear execution entrypoints and command structure.",
        "avoid": "Do not copy repo-specific commands or environment assumptions verbatim.",
    },
    {
        "category": "evaluation",
        "keywords": ["test", "benchmark", "eval", "assert", "validation", "quality"],
        "borrow": "Borrow explicit validation and quality gates that make iteration safer.",
        "avoid": "Do not clone heavyweight evaluation scaffolding if a lighter gate is enough here.",
    },
    {
        "category": "structure",
        "keywords": ["template", "example", "guide", "docs", "reference", "starter"],
        "borrow": "Borrow the way it separates explanation, examples, and reusable structure.",
        "avoid": "Do not mirror documentation bulk that adds context cost without improving reliability.",
    },
    {
        "category": "portability",
        "keywords": ["adapter", "portable", "plugin", "integration", "export", "compatibility"],
        "borrow": "Borrow how it keeps core semantics stable across environments or integrations.",
        "avoid": "Do not inherit platform lock-in or vendor-specific branching unless truly required.",
    },
    {
        "category": "governance",
        "keywords": ["govern", "policy", "security", "audit", "compliance", "review"],
        "borrow": "Borrow the explicit review, safety, or operational trust boundaries.",
        "avoid": "Do not import compliance-heavy process where the new skill does not need it.",
    },
]


def github_headers() -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": API_VERSION,
        "User-Agent": USER_AGENT,
    }
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def ensure_allowed_api_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_API_HOSTS:
        raise ValueError(f"Refusing outbound request to non-GitHub API host: {url}")
    return url


def api_get(url: str) -> dict[str, Any]:
    request = Request(ensure_allowed_api_url(url), headers=github_headers())
    with urlopen(request, timeout=15) as response:  # nosec B310 - GitHub API fetch
        data = response.read().decode("utf-8")
    return json.loads(data)


def load_fixture_bundle(fixture_dir: Path | None) -> dict[str, Any] | None:
    if not fixture_dir:
        return None
    bundle_path = fixture_dir / "bundle.json"
    if not bundle_path.exists():
        raise FileNotFoundError(f"Missing fixture bundle: {bundle_path}")
    return json.loads(bundle_path.read_text(encoding="utf-8"))


def build_query(seed_text: str) -> str:
    words = re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}", seed_text.lower())
    keywords = []
    seen = set()
    for word in words:
        if word in STOPWORDS or word in seen:
            continue
        seen.add(word)
        keywords.append(word)
        if len(keywords) == 4:
            break
    if keywords:
        return " ".join(keywords)
    compact = re.sub(r"\s+", " ", seed_text.strip())
    return compact[:64] or "agent workflow automation"


def search_repositories(query: str, top_n: int, fixture_bundle: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    if fixture_bundle is not None:
        items = fixture_bundle.get("search_items", [])
        return items[:top_n]

    github_query = f"{query} fork:false archived:false stars:>={MIN_STARS}"
    url = (
        f"{API_ROOT}/search/repositories?q={quote(github_query)}"
        f"&sort=stars&order=desc&per_page={DEFAULT_PER_PAGE}"
    )
    payload = api_get(url)
    items = payload.get("items", [])
    filtered = [item for item in items if not item.get("fork") and not item.get("archived")]
    return filtered[:top_n]


def fetch_readme(full_name: str, fixture_bundle: dict[str, Any] | None = None) -> str:
    if fixture_bundle is not None:
        return fixture_bundle.get("readmes", {}).get(full_name, "")

    url = f"{API_ROOT}/repos/{full_name}/readme"
    request = Request(
        ensure_allowed_api_url(url),
        headers={**github_headers(), "Accept": "application/vnd.github.raw+json"},
    )
    with urlopen(request, timeout=15) as response:  # nosec B310 - GitHub API fetch
        return response.read().decode("utf-8", errors="replace")


def detect_patterns(text: str) -> list[dict[str, str]]:
    lowered = text.lower()
    hits = []
    for rule in PATTERN_RULES:
        matched = [token for token in rule["keywords"] if token in lowered]
        if matched:
            hits.append(
                {
                    "category": rule["category"],
                    "matched": ", ".join(matched[:4]),
                    "borrow": rule["borrow"],
                    "avoid": rule["avoid"],
                }
            )
    return hits[:4]


def repo_summary(repo: dict[str, Any], readme_text: str) -> dict[str, Any]:
    combined = " ".join(
        filter(
            None,
            [
                repo.get("name", ""),
                repo.get("description", "") or "",
                " ".join(repo.get("topics") or []),
                readme_text[:4000],
            ],
        )
    )
    patterns = detect_patterns(combined)
    if not patterns:
        patterns = [
            {
                "category": "general",
                "matched": "high-level fit",
                "borrow": "Borrow only the parts that make the new skill clearer, safer, or easier to reuse.",
                "avoid": "Do not import source-specific scope, branding, or excess weight.",
            }
        ]

    borrow = [item["borrow"] for item in patterns[:3]]
    avoid = [item["avoid"] for item in patterns[:3]]
    return {
        "full_name": repo.get("full_name"),
        "html_url": repo.get("html_url"),
        "description": repo.get("description"),
        "stars": repo.get("stargazers_count", 0),
        "topics": repo.get("topics") or [],
        "primary_language": repo.get("language"),
        "patterns": patterns,
        "borrow": borrow,
        "avoid": avoid,
        "readme_excerpt": readme_text[:1200].strip(),
    }


def cross_repo_insights(repos: list[dict[str, Any]]) -> dict[str, list[str]]:
    borrow = []
    avoid = []
    seen_borrow = set()
    seen_avoid = set()
    if not repos:
        return {
            "borrow": [],
            "avoid": [],
        }
    for repo in repos:
        for item in repo.get("borrow", []):
            if item not in seen_borrow:
                seen_borrow.add(item)
                borrow.append(item)
        for item in repo.get("avoid", []):
            if item not in seen_avoid:
                seen_avoid.add(item)
                avoid.append(item)
    borrow.append("Ask the user which of these patterns feels most worth borrowing before freezing the package shape.")
    return {"borrow": borrow[:6], "avoid": avoid[:6]}


def repo_to_external_reference(repo: dict[str, Any]) -> dict[str, str]:
    primary = repo.get("patterns", [{}])[0]
    return {
        "name": repo.get("full_name") or "Unnamed repo",
        "category": primary.get("category", "general"),
        "borrow": repo.get("borrow", ["Borrow the strongest reusable pattern."])[0],
        "avoid": repo.get("avoid", ["Do not copy source-specific language or excess scope."])[0],
        "source": "external",
    }


def render_markdown(payload: dict[str, Any]) -> str:
    repo_count = len(payload["repositories"])
    next_step = (
        f"Review the {repo_count} benchmark object{'s' if repo_count != 1 else ''} below, "
        "then decide whether any of their patterns are worth borrowing into the new skill."
        if repo_count
        else "No benchmark repositories were collected; adjust the query or attach manual references before treating the scan as evidence."
    )
    lines = [
        "# GitHub Benchmark Scan",
        "",
        f"- Query: `{payload['query']}`",
        f"- Source: `{payload['source']}`",
        f"- Top repositories: `{repo_count}`",
        "",
        "## Suggested Next Step",
        "",
        next_step,
        "",
    ]

    if not payload["repositories"]:
        lines.extend(
            [
                "No benchmark repositories were collected.",
                "",
                "Possible reasons:",
                "- the query was too weak or too local",
                "- the network or API rate limit blocked the scan",
                "- this skill idea may need a manual benchmark query",
            ]
        )
        return "\n".join(lines).strip() + "\n"

    lines.extend([f"## Top {repo_count} Benchmark Repositories", ""])
    for repo in payload["repositories"]:
        lines.extend(
            [
                f"### {repo['full_name']}",
                f"- URL: {repo['html_url']}",
                f"- Stars: `{repo['stars']}`",
                f"- Description: {repo.get('description') or 'No public description provided.'}",
                f"- Topics: {', '.join(repo.get('topics') or []) or 'None'}",
                "",
                "#### Patterns worth studying",
                "",
            ]
        )
        for pattern in repo["patterns"]:
            lines.append(
                f"- **{pattern['category']}** (`{pattern['matched']}`): {pattern['borrow']}"
            )
        lines.extend(["", "#### Borrow", ""])
        for item in repo["borrow"]:
            lines.append(f"- {item}")
        lines.extend(["", "#### Avoid", ""])
        for item in repo["avoid"]:
            lines.append(f"- {item}")
        lines.extend(["", "#### README glimpse", "", repo["readme_excerpt"] or "No README excerpt collected.", ""])

    lines.extend(["## Cross-Repo Borrow Recommendations", ""])
    for item in payload["cross_repo"]["borrow"]:
        lines.append(f"- {item}")

    lines.extend(["", "## Cross-Repo Avoid Recommendations", ""])
    for item in payload["cross_repo"]["avoid"]:
        lines.append(f"- {item}")

    lines.extend(
        [
            "",
            "## Borrow Prompt",
            "",
            payload["borrow_prompt"],
            "",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def run_github_benchmark_scan(
    skill_dir: Path,
    query: str,
    top_n: int = DEFAULT_TOP_N,
    fixture_dir: Path | None = None,
    output_md: Path | None = None,
    output_json: Path | None = None,
) -> dict[str, Any]:
    skill_dir = skill_dir.resolve()
    reports_dir = skill_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_md = output_md or reports_dir / "github-benchmark-scan.md"
    output_json = output_json or reports_dir / "github-benchmark-scan.json"
    fixture_bundle = load_fixture_bundle(fixture_dir)

    warnings = []
    try:
        repos = search_repositories(query, top_n=top_n, fixture_bundle=fixture_bundle)
        repo_summaries = []
        for repo in repos:
            readme_text = fetch_readme(repo["full_name"], fixture_bundle=fixture_bundle)
            repo_summaries.append(repo_summary(repo, readme_text))
        cross_repo = cross_repo_insights(repo_summaries)
        payload = {
            "ok": True,
            "query": query,
            "source": "fixture" if fixture_bundle is not None else "github-api",
            "network_boundary": "github-api-only",
            "repositories": repo_summaries,
            "cross_repo": cross_repo,
            "external_references": [repo_to_external_reference(repo) for repo in repo_summaries],
            "borrow_prompt": (
                f"I found {len(repo_summaries)} public GitHub project"
                f"{'s' if len(repo_summaries) != 1 else ''} worth studying. "
                "Do you want to borrow any of these patterns for method, structure, execution, or portability?"
                if repo_summaries
                else "No benchmark suggestions were collected yet. You can retry with a stronger query or add manual references."
            ),
            "warnings": warnings,
        }
    except Exception as exc:  # pragma: no cover - network failures are environment-dependent
        payload = {
            "ok": False,
            "query": query,
            "source": "fixture" if fixture_bundle is not None else "github-api",
            "network_boundary": "github-api-only",
            "repositories": [],
            "cross_repo": {
                "borrow": [],
                "avoid": [],
            },
            "external_references": [],
            "borrow_prompt": "No benchmark suggestions were collected yet. You can retry with a stronger query or add manual references.",
            "warnings": [f"GitHub benchmark scan failed: {exc}"],
        }

    output_md.write_text(render_markdown(payload), encoding="utf-8")
    output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    payload["artifacts"] = {
        "markdown": str(output_md),
        "json": str(output_json),
    }
    payload["skill_dir"] = str(skill_dir)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Search GitHub for top benchmark repositories and extract reusable patterns.")
    parser.add_argument("skill_dir", nargs="?", default=".")
    parser.add_argument("--query", required=True)
    parser.add_argument("--top-n", type=int, default=DEFAULT_TOP_N)
    parser.add_argument("--fixture-dir")
    parser.add_argument("--output-md")
    parser.add_argument("--output-json")
    args = parser.parse_args()

    result = run_github_benchmark_scan(
        Path(args.skill_dir),
        query=args.query,
        top_n=args.top_n,
        fixture_dir=Path(args.fixture_dir).resolve() if args.fixture_dir else None,
        output_md=Path(args.output_md).resolve() if args.output_md else None,
        output_json=Path(args.output_json).resolve() if args.output_json else None,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
