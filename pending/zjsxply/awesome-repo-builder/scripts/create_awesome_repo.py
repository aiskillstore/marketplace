#!/usr/bin/env python3
"""Create an awesome-list repository scaffold from a JSON spec."""

from __future__ import annotations

import argparse
import json
import re
import textwrap
from pathlib import Path
from typing import Any


CC0_LICENSE = """CC0 1.0 Universal

The person who associated a work with this deed has dedicated the work to the
public domain by waiving all of his or her rights to the work worldwide under
copyright law, including all related and neighboring rights, to the extent
allowed by law.

You can copy, modify, distribute and perform the work, even for commercial
purposes, all without asking permission.

https://creativecommons.org/publicdomain/zero/1.0/
"""


VERIFY_URLS = r'''#!/usr/bin/env python3
"""Verify HTTP(S) URLs in README.md."""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


def extract_urls(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    urls = set()
    for match in re.finditer(r"\[([^\]]*)\]\(([^)\s]+)\)", text):
        url = match.group(2).strip()
        if url.startswith(("http://", "https://")):
            urls.add(url)
    for match in re.finditer(r"https?://[^\s>)]+", text):
        urls.add(match.group(0).rstrip(".,"))
    return sorted(urls)


def check_url(url: str, timeout: int) -> dict[str, object]:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; awesome-url-checker/1.0)"},
    )
    started = time.time()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = int(response.status)
            final_url = response.geturl()
            return {
                "url": url,
                "ok": 200 <= status < 400,
                "status": status,
                "final_url": final_url if final_url != url else None,
                "elapsed": round(time.time() - started, 3),
            }
    except urllib.error.HTTPError as exc:
        return {
            "url": url,
            "ok": False,
            "status": exc.code,
            "error": str(exc),
            "elapsed": round(time.time() - started, 3),
        }
    except Exception as exc:
        return {
            "url": url,
            "ok": False,
            "status": None,
            "error": str(exc),
            "elapsed": round(time.time() - started, 3),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify URLs in README.md")
    parser.add_argument("--file", "-f", default="README.md")
    parser.add_argument("--output", "-o", default="url_verification_results.json")
    parser.add_argument("--timeout", "-t", type=int, default=10)
    parser.add_argument("--limit", "-l", type=int)
    args = parser.parse_args()

    readme = Path(args.file)
    if not readme.exists():
        print(f"Error: {readme} not found", file=sys.stderr)
        return 2

    urls = extract_urls(readme)
    if args.limit:
        urls = urls[: args.limit]
    print(f"Found {len(urls)} URLs")

    results = []
    for index, url in enumerate(urls, 1):
        result = check_url(url, args.timeout)
        results.append(result)
        marker = "OK" if result["ok"] else "FAIL"
        print(f"[{index}/{len(urls)}] {marker} {url}")

    Path(args.output).write_text(json.dumps(results, indent=2), encoding="utf-8")
    failures = [item for item in results if not item["ok"]]
    print(f"Saved results to {args.output}")
    if failures:
        print(f"{len(failures)} URL(s) failed")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = value.strip("-")
    return value or "awesome-list"


def anchor(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"`", "", value)
    value = re.sub(r"[^a-z0-9\s-]", "", value)
    value = re.sub(r"\s+", "-", value)
    return value


def ensure_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def entry_line(entry: dict[str, Any]) -> str:
    title = str(entry.get("title", "Untitled")).strip()
    url = str(entry.get("url", "")).strip()
    note = str(entry.get("note", "")).strip()
    if not note:
        note = "Add a short note explaining why this resource is worth including."
    if url:
        return f"- [{title}]({url}) - {note}"
    return f"- {title} - {note}"


def section_entries(section: dict[str, Any], initial_entries: dict[str, Any]) -> list[dict[str, Any]]:
    entries = ensure_list(section.get("entries"))
    if entries:
        return entries
    name = str(section.get("name", ""))
    return ensure_list(initial_entries.get(name))


def render_contents(taxonomy: list[dict[str, Any]], include_templates: bool, related_lists: list[Any]) -> str:
    lines = ["## Contents", ""]
    for section in taxonomy:
        name = str(section.get("name", "Section"))
        lines.append(f"- [{name}](#{anchor(name)})")
        for subsection in ensure_list(section.get("subsections")):
            sub_name = str(subsection.get("name", "Subsection"))
            lines.append(f"  - [{sub_name}](#{anchor(sub_name)})")
    if include_templates:
        lines.append("- [Templates](#templates)")
    if related_lists:
        lines.append("- [Related Awesome Lists](#related-awesome-lists)")
    lines.append("- [Contributing](#contributing)")
    return "\n".join(lines)


def render_section(section: dict[str, Any], initial_entries: dict[str, Any]) -> str:
    name = str(section.get("name", "Section"))
    description = str(section.get("description", "")).strip()
    lines = [f"## {name}", ""]
    if description:
        lines.extend([description, ""])

    entries = section_entries(section, initial_entries)
    if entries:
        lines.extend(entry_line(entry) for entry in entries)
    elif not ensure_list(section.get("subsections")):
        lines.append("- [Add resource](https://example.com) - Add a short note explaining why this resource is worth including.")

    for subsection in ensure_list(section.get("subsections")):
        sub_name = str(subsection.get("name", "Subsection"))
        sub_description = str(subsection.get("description", "")).strip()
        lines.extend(["", f"### {sub_name}", ""])
        if sub_description:
            lines.extend([sub_description, ""])
        sub_entries = section_entries(subsection, initial_entries)
        if sub_entries:
            lines.extend(entry_line(entry) for entry in sub_entries)
        else:
            lines.append("- [Add resource](https://example.com) - Add a short note explaining why this resource is worth including.")
    return "\n".join(lines)


def render_readme(spec: dict[str, Any]) -> str:
    title = str(spec.get("title") or f"Awesome {spec.get('topic', 'List')}").strip()
    slug = str(spec.get("slug") or slugify(title)).strip()
    tagline = str(spec.get("tagline") or f"Curated resources for {spec.get('topic', title)}.").strip()
    description = str(spec.get("description") or tagline).strip()
    repo_url = str(spec.get("repository_url", "")).strip()
    taxonomy = ensure_list(spec.get("taxonomy"))
    if not taxonomy:
        taxonomy = [{"name": "Resources", "description": "", "entries": []}]
    initial_entries = spec.get("initial_entries") or {}
    related_lists = ensure_list(spec.get("related_lists"))
    include_templates = bool(spec.get("include_templates", True))

    badges = [
        '<a href="https://awesome.re"><img src="https://awesome.re/badge.svg" alt="Awesome"></a>',
        '<a href="LICENSE"><img src="https://img.shields.io/badge/License-CC0-lightgrey.svg" alt="License: CC0"></a>',
    ]
    if repo_url:
        repo_path = repo_url.rstrip("/").removeprefix("https://github.com/")
        badges.extend([
            f'<a href="{repo_url}/stargazers"><img src="https://img.shields.io/github/stars/{repo_path}?style=social" alt="GitHub Stars"></a>',
            f'<a href="{repo_url}/network/members"><img src="https://img.shields.io/github/forks/{repo_path}?style=social" alt="GitHub Forks"></a>',
            f'<a href="{repo_url}/commits/main"><img src="https://img.shields.io/github/last-commit/{repo_path}" alt="Last Commit"></a>',
        ])

    header = [
        '<div align="center">',
        f"  <h1>{title}</h1>",
        f"  <p>{tagline}</p>",
        "  <p>",
        *[f"    {badge}" for badge in badges],
        "  </p>",
        "</div>",
        "",
        description,
        "",
        "---",
        "",
        render_contents(taxonomy, include_templates, related_lists),
        "",
        "---",
        "",
    ]
    sections = "\n\n".join(render_section(section, initial_entries) for section in taxonomy)

    tail: list[str] = []
    if include_templates:
        tail.extend([
            "## Templates",
            "",
            "Reusable Markdown templates for this topic.",
            "",
            "- [AGENTS.md](templates/AGENTS.md) - Project-level instructions for AI agents.",
            "- [PLAN.md](templates/PLAN.md) - Planning artifact for non-trivial work.",
            "- [IMPLEMENT.md](templates/IMPLEMENT.md) - Append-only implementation log.",
            "- [CHECKLIST.md](templates/CHECKLIST.md) - Review checklist for topic-specific artifacts.",
            "",
        ])
    if related_lists:
        tail.extend(["## Related Awesome Lists", ""])
        for item in related_lists:
            if isinstance(item, dict):
                tail.append(entry_line(item))
            else:
                tail.append(f"- {item}")
        tail.append("")
    tail.extend([
        "## Contributing",
        "",
        "Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).",
        "",
    ])
    return "\n".join(header) + "\n" + sections + "\n\n" + "\n".join(tail)


def render_contributing(spec: dict[str, Any]) -> str:
    criteria = spec.get("criteria") or {}
    belongs = ensure_list(criteria.get("belongs"))
    excludes = ensure_list(criteria.get("excludes"))
    if not belongs:
        belongs = [
            f"Directly addresses {spec.get('topic', 'the topic')}.",
            "Is useful enough to justify a short explanatory note.",
        ]
    if not excludes:
        excludes = [
            "Generic resources without a clear connection to the topic.",
            "Product marketing without technical or practical substance.",
        ]

    lines = ["# Contributing", "", "## Criteria", "", "A resource belongs in this list if it:", ""]
    for index, item in enumerate(belongs, 1):
        lines.append(f"{index}. {item}")
    lines.extend(["", "## What does not belong", ""])
    lines.extend(f"- {item}" for item in excludes)
    lines.extend([
        "",
        "## How to contribute",
        "",
        "1. Fork and create a branch.",
        "2. Add your resource to the appropriate section in `README.md`.",
        "3. Format: `- [Title](URL) - 1-2 sentence note explaining why it is worth including.`",
        "4. Open a pull request with a brief description of what you are adding and why.",
        "",
        "## Updating existing entries",
        "",
        "If a link is dead or a resource has a better successor, open an issue or pull request with the replacement.",
        "",
        "## Template contributions",
        "",
        "If this repository includes `templates/`, add only templates that are reusable and relevant to the topic.",
        "",
    ])
    return "\n".join(lines)


def render_agents(spec: dict[str, Any]) -> str:
    topic = str(spec.get("topic", "this topic"))
    criteria = spec.get("criteria") or {}
    belongs = ensure_list(criteria.get("belongs"))
    excludes = ensure_list(criteria.get("excludes"))
    belongs_text = "\n".join(f"- {item}" for item in belongs) or f"- Resources that directly address {topic}"
    excludes_text = "\n".join(f"- {item}" for item in excludes) or "- Generic resources without a clear connection to the topic"
    return f"""# AGENTS.md

> Instructions for AI agents contributing to this repository.

## What this repo is

A curated awesome list for {topic}. The primary artifact is `README.md`.

## Conventions

- Keep entries concise and useful.
- Each resource entry follows the format: `- [Title](URL) - 1-2 sentence note explaining why it is worth including.`
- Notes should explain why the resource matters, not just what it is.
- Do not add resources without a note.
- Organize sections by the problem being solved or the role in the topic, not by vendor.

## What belongs

{belongs_text}

## What does not belong

{excludes_text}

## Templates

Files in `templates/` are reusable starting points. Preserve comments when editing templates.

## Verification

Before any pull request:

- [ ] All URLs are reachable
- [ ] All entries have a short explanatory note
- [ ] `README.md` renders correctly as Markdown
"""


def render_gitignore() -> str:
    return """url_verification_results.json
__pycache__/
.DS_Store
.env
"""


def render_template_agents() -> str:
    return """# AGENTS.md

> Project-level instructions for AI agents working in this repository.

## Project overview

<!-- One paragraph: what this project does and what success looks like. -->

## Repository structure

<!-- Describe the main directories and files. -->

## Conventions

<!-- Language, style, naming, and contribution conventions. -->

## Tool permissions

Allowed:
- Read and edit project documentation

Restricted:
- Running destructive commands
- Publishing releases

## Verification gates

- [ ] Required checks pass
- [ ] Changed files are within the intended scope
"""


def render_template_plan() -> str:
    return """# PLAN.md

> Task planning artifact. Create this at the start of a non-trivial task.

## Task

<!-- One sentence describing the task. -->

## Context

<!-- Why this task exists and what success looks like. -->

## Approach

<!-- High-level strategy and key trade-offs. -->

## Milestones

- [ ] **M1: <name>** - <done state> | verify: `<command or check>`
- [ ] **M2: <name>** - <done state> | verify: `<command or check>`
- [ ] **Final: verify output** - verify: `<command or check>`

## Scope boundaries

In scope:
-

Out of scope:
-

## Open questions

- [ ]
"""


def render_template_implement() -> str:
    return """# IMPLEMENT.md

> Append-only implementation log. Capture decisions, deviations, and open questions.

## Task reference

<!-- Link to or copy the task description from PLAN.md. -->

## Log

### YYYY-MM-DD HH:MM - <brief title>

**What happened:**
<!-- What was done, found, or decided. -->

**Decision:**
<!-- What was chosen and why. -->

**Deviation from plan:**
<!-- If this deviates from PLAN.md, describe the deviation. -->

**Next:**
<!-- What comes immediately next. -->

## Open questions

- [ ]
"""


def render_template_checklist(spec: dict[str, Any]) -> str:
    topic = str(spec.get("topic", "the topic"))
    return f"""# Review Checklist

> Use this before publishing a {topic} artifact or accepting a substantial addition.

- [ ] The resource is in scope for {topic}
- [ ] The URL is reachable
- [ ] The entry has a concise explanatory note
- [ ] The section placement is appropriate
- [ ] The Markdown renders correctly
"""


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def create_repo(spec: dict[str, Any], output: Path, force: bool) -> None:
    if output.exists() and any(output.iterdir()) and not force:
        raise SystemExit(f"Output directory is not empty: {output}. Use --force to overwrite generated files.")
    output.mkdir(parents=True, exist_ok=True)

    write_file(output / "README.md", render_readme(spec))
    write_file(output / "CONTRIBUTING.md", render_contributing(spec))
    write_file(output / "AGENTS.md", render_agents(spec))
    write_file(output / "LICENSE", CC0_LICENSE)
    write_file(output / ".gitignore", render_gitignore())
    write_file(output / "verify_urls.py", VERIFY_URLS)
    templates = output / "templates"
    write_file(templates / "AGENTS.md", render_template_agents())
    write_file(templates / "PLAN.md", render_template_plan())
    write_file(templates / "IMPLEMENT.md", render_template_implement())
    write_file(templates / "CHECKLIST.md", render_template_checklist(spec))


def main() -> int:
    parser = argparse.ArgumentParser(description="Create an awesome-list repository scaffold")
    parser.add_argument("--spec", required=True, help="Path to JSON spec")
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument("--force", action="store_true", help="Overwrite generated files in a non-empty directory")
    args = parser.parse_args()

    spec_path = Path(args.spec)
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    output = Path(args.output)
    create_repo(spec, output, args.force)
    print(f"Created awesome repo scaffold at {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
