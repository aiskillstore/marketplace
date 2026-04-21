#!/usr/bin/env python3
"""Prepare and publish local skills across public skill marketplaces."""

from __future__ import annotations

import argparse
import http.cookiejar
import json
import re
import subprocess
import sys
import textwrap
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib import error, parse, request

try:
    import yaml
except ImportError:  # pragma: no cover - optional dependency
    yaml = None


USER_AGENT = "skill-market-publisher/1.0"

SKILLZ_CATEGORIES = [
    "automation",
    "code-generation",
    "code-review",
    "debugging",
    "documentation",
    "devops",
    "git",
    "refactoring",
    "security",
    "testing",
    "other",
]

BOGEN_CATEGORIES = [
    "real-estate",
    "marketing",
    "sales",
    "operations",
    "development",
]


MARKETS: dict[str, dict[str, Any]] = {
    "clawhub": {
        "title": "ClawHub",
        "mode": "auto-cli",
        "status": "verified",
        "auth": "CLI login",
        "requires": ["version"],
        "source_url": "https://raw.githubusercontent.com/openclaw/clawhub/main/docs/cli.md",
        "submit_url": None,
        "verify": "Use CLI output and the destination workspace listing; no stable public status API is documented here.",
        "notes": "Official CLI documents skill publish <path> and sync.",
        "recon": [
            {
                "url": "https://raw.githubusercontent.com/openclaw/clawhub/main/docs/cli.md",
                "markers": ["### `skill publish <path>`", "### `sync`"],
            }
        ],
    },
    "agent-skills-index": {
        "title": "Agent Skills Index",
        "mode": "manual-web",
        "status": "blocked",
        "auth": "Public submit page, but live submit path is currently blocked",
        "requires": ["repo_url"],
        "source_url": "https://agentskillsindex.com/en/docs/publishing",
        "submit_url": "https://agentskillsindex.com/en/submit",
        "verify": "Use platform search plus crawler discovery from a public repo tagged with ai-skill.",
        "notes": "Docs still advertise manual submit and crawler discovery, but the current submit surface is not stable enough to wrap safely. Treat ai-skill topic plus crawler discovery as the only current fallback.",
        "recon": [
            {
                "url": "https://agentskillsindex.com/en/submit",
                "markers": ['name=\"github_url\"', 'method=\"POST\"', "GitHub Repository URL"],
            }
        ],
    },
    "agentskill-sh": {
        "title": "AgentSkill.sh",
        "mode": "auto-http",
        "status": "verified",
        "auth": "None",
        "requires": ["repo_url"],
        "source_url": "https://agentskill.sh/submit",
        "submit_url": "https://agentskill.sh/api/skills/submit",
        "verify": "Check the public author page or skill page under https://agentskill.sh/@<owner>/<skill-name>.",
        "notes": "Public submit API accepts a repository URL and imports all discovered SKILL.md files from that repository.",
        "recon": [
            {
                "url": "https://agentskill.sh/submit",
                "markers": ["GitHub", "Submit", "skill"],
            }
        ],
    },
    "skillz-directory": {
        "title": "Skillz Directory",
        "mode": "auto-http",
        "status": "verified",
        "auth": "None",
        "requires": ["repo_url", "author_email", "skillz_category"],
        "source_url": "https://www.skillz.directory/submit",
        "submit_url": "https://www.skillz.directory/api/submit",
        "verify": "Query the public Convex API or open https://www.skillz.directory/skills/<slug>.",
        "notes": "Current front-end posts JSON to /api/submit. Categories are a fixed enum, so map domain-specific skills to the nearest supported value or other.",
        "recon": [
            {
                "url": "https://www.skillz.directory/submit",
                "markers": ["Submit a Skill", "/api/submit", "githubUrl"],
            }
        ],
    },
    "skillstore-io": {
        "title": "Skillstore",
        "mode": "auto-http",
        "status": "verified",
        "auth": "None",
        "requires": ["repo_url"],
        "source_url": "https://skillstore.io/submit",
        "submit_url": "https://skillstore.io/api/submit",
        "verify": "Use GET https://skillstore.io/api/submit?id=<submission_id> or the public submission page.",
        "notes": "Anonymous submit API accepts GitHub repo URLs and tree URLs, then exposes a public status API and workflow URL. Treat folder URLs as best-effort scoping until the status payload or final listing proves they stayed per-skill.",
        "recon": [
            {
                "url": "https://skillstore.io/submit",
                "markers": ["GitHub", "submit", "skill"],
            }
        ],
    },
    "a2a-market": {
        "title": "A2A Market",
        "mode": "auto-http",
        "status": "verified",
        "auth": "Seller wallet and market-side listing flow",
        "requires": ["a2a_price", "a2a_category", "a2a_seller"],
        "source_url": "https://a2amarket.live/skill.md",
        "submit_url": "https://api.a2amarket.live/v1/listings",
        "verify": "Check the resulting marketplace listing or seller-facing listing view after creation.",
        "notes": "Official published skill page documents POST /v1/listings.",
        "recon": [
            {
                "url": "https://a2amarket.live/skill.md",
                "markers": ["POST /v1/listings", "Base URL: `https://api.a2amarket.live`"],
            }
        ],
    },
    "skillnet-openkg": {
        "title": "SkillNet",
        "mode": "manual-web",
        "status": "verified",
        "auth": "Website contribution flow; search/download are public",
        "requires": [],
        "source_url": "https://github.com/zjunlp/SkillNet",
        "submit_url": "http://skillnet.openkg.cn/",
        "verify": "Query GET http://api-skillnet.openkg.cn/v1/search?q=<skill-name> or run skillnet search <skill-name>.",
        "notes": "Official docs describe Website -> Contribute -> Submit via URL / Upload Local Skill / Batch Upload Skills. Search and download are public; create and evaluate require an API key.",
        "recon": [
            {
                "url": "https://github.com/zjunlp/SkillNet",
                "markers": [
                    "Submit via URL / Upload Local Skill / Batch Upload Skills",
                    "GET http://api-skillnet.openkg.cn/v1/search",
                ],
            }
        ],
    },
    "agent-skills-md": {
        "title": "agent-skills.md",
        "mode": "auto-http",
        "status": "verified",
        "auth": "None",
        "requires": ["repo_url"],
        "source_url": "https://agent-skills.md/submit",
        "submit_url": "https://agent-skills.md/rpc/repos/submit",
        "verify": "Use public detail pages under https://agent-skills.md/skills/<owner>/<repo>/<skill-name>.",
        "notes": "Public submit flow posts an ORPC JSON envelope with a GitHub repo or folder URL. Re-runs can return alreadyExists, and pack-level submissions can import multiple skills from one repository scope.",
        "recon": [
            {
                "url": "https://agent-skills.md/submit",
                "markers": ["Paste a GitHub repo link", "Skills folder URL", "repo root defaults to skills/"],
            }
        ],
    },
    "skillsmd-dev": {
        "title": "SkillsMD",
        "mode": "auto-http",
        "status": "verified",
        "auth": "None",
        "requires": ["repo_url"],
        "source_url": "https://skillsmd.dev/",
        "submit_url": "https://skillsmd.dev/api/submit",
        "verify": "Check https://skillsmd.dev/api/search?q=<skill-name> and the public registry after review.",
        "notes": "Public review-queue API accepts owner/repo plus one skill name per submission. A 201 response means queued, not publicly listed yet.",
        "recon": [
            {
                "url": "https://skillsmd.dev/",
                "markers": ["Submit a Skill", "GitHub repo in owner/repo format", "npx skillsmd add"],
            }
        ],
    },
    "agentskillsrepo": {
        "title": "AgentSkillsRepo",
        "mode": "manual-web",
        "status": "verified",
        "auth": "Public submit surface visible",
        "requires": ["repo_url"],
        "source_url": "https://agentskillsrepo.com/",
        "submit_url": "https://agentskillsrepo.com/",
        "verify": "Use https://agentskillsrepo.com/search?q=<query> and the generated detail page.",
        "notes": "Official site accepts a GitHub repository URL containing SKILL.md and reviews it before listing. Raw non-browser fetches can be brittle, so browser recon is more reliable than the simple HTTP canary here.",
        "recon": [
            {
                "url": "https://agentskillsrepo.com/",
                "markers": ["Submit a GitHub repository URL containing a SKILL.md file", "All skills use the open SKILL.md standard"],
            }
        ],
    },
    "skills-re": {
        "title": "skills.re",
        "mode": "manual-web",
        "status": "verified",
        "auth": "Public submit surface visible",
        "requires": ["repo_url"],
        "source_url": "https://skills.re/submit",
        "submit_url": "https://skills.re/submit",
        "verify": "Use the public site listing after submit.",
        "notes": "Submit-page copy mentions a repo-root skills/ folder, but live preview and public read APIs can still accept some root-pack repositories. Verify backend behavior before forcing a publish mirror.",
        "recon": [
            {
                "url": "https://skills.re/submit",
                "markers": ["Repository URL", "FETCH", "SUBMIT"],
            }
        ],
    },
    "skillsdirectory-com": {
        "title": "Skills Directory",
        "mode": "manual-web",
        "status": "auth-required",
        "auth": "GitHub sign-in required",
        "requires": ["repo_url"],
        "source_url": "https://www.skillsdirectory.com/submit",
        "submit_url": "https://www.skillsdirectory.com/submit",
        "verify": "Query https://skillsdirectory.com/api/registry?q=<query> or open /skills/<slug>.",
        "notes": "Distinct from skillsdir.dev. Submit is login-gated, but the registry API is public and documented.",
        "recon": [
            {
                "url": "https://www.skillsdirectory.com/submit",
                "markers": ["Submit a Skill", "Sign in with GitHub to submit your skill to the directory"],
            },
            {
                "url": "https://www.skillsdirectory.com/docs/registry-api",
                "markers": ["https://skillsdirectory.com/api/registry", "GET /api/registry"],
            },
        ],
    },
    "skillsdir-dev": {
        "title": "Skills Directory",
        "mode": "manual-web",
        "status": "partial",
        "auth": "Public page, but current GitHub issue path is unreliable",
        "requires": ["repo_url"],
        "source_url": "https://www.skillsdir.dev/add",
        "submit_url": "https://www.skillsdir.dev/add",
        "verify": "Use the public site listing after submit.",
        "notes": "Site advertises GitHub submission and skill publish, but the current GitHub issue link is stale.",
        "recon": [
            {
                "url": "https://www.skillsdir.dev/add",
                "markers": ["Submit Skill on GitHub", "skill publish", "SKILL.md"],
            }
        ],
    },
    "skills-sh": {
        "title": "skills.sh",
        "mode": "index-only",
        "status": "verified",
        "auth": "None",
        "requires": [],
        "source_url": "https://skills.sh/",
        "submit_url": None,
        "verify": "Use https://skills.sh/api/search?q=<query>&limit=10 or npx -y skills find <query>.",
        "notes": "Treat this as a discovery surface rather than a direct publish API.",
        "recon": [
            {
                "url": "https://skills.sh/",
                "markers": ["skills.sh", "Discover", "skill"],
            }
        ],
    },
    "skillsfor-ai": {
        "title": "skillsfor.ai",
        "mode": "incompatible",
        "status": "verified",
        "auth": "N/A",
        "requires": [],
        "source_url": "https://skillsfor.ai/",
        "submit_url": None,
        "verify": "Not applicable without a translation layer.",
        "notes": "Uses a different artifact model than a plain SKILL.md folder.",
        "recon": [
            {
                "url": "https://skillsfor.ai/",
                "markers": ["OpenAPI", "API"],
            }
        ],
    },
    "skillscatalog-ai": {
        "title": "skillscatalog.ai",
        "mode": "manual-web",
        "status": "partial",
        "auth": "Public submit exists, but anonymous behavior is unstable",
        "requires": ["repo_url"],
        "source_url": "https://skillscatalog.ai/submit",
        "submit_url": "https://skillscatalog.ai/submit",
        "verify": "Use the public listing or search surface after submit.",
        "notes": "Public submit exists, but anonymous behavior has been unstable enough that this skill should not claim wrapped automation.",
        "recon": [{"url": "https://skillscatalog.ai/submit", "markers": ["submit", "GitHub", "skill"]}],
    },
    "mdskills-ai": {
        "title": "mdskills.ai",
        "mode": "manual-web",
        "status": "auth-required",
        "auth": "Login required",
        "requires": ["repo_url"],
        "source_url": "https://www.mdskills.ai/submit",
        "submit_url": "https://www.mdskills.ai/submit",
        "verify": "Use public search and listing pages under https://www.mdskills.ai/skills after submit.",
        "notes": "Public docs treat SKILL.md as a first-class ecosystem format, but the submit path redirects to login before the real form appears.",
        "recon": [
            {
                "url": "https://www.mdskills.ai/submit",
                "markers": ["Sign in", "Submit", "SKILL.md"],
            }
        ],
    },
    "skillery-dev": {
        "title": "Skillery",
        "mode": "manual-web",
        "status": "auth-required",
        "auth": "Login required",
        "requires": ["repo_url"],
        "source_url": "https://skillery.dev/submit",
        "submit_url": "https://skillery.dev/submit",
        "verify": "Use the public skills list or a generated detail page under https://skillery.dev/skills/.",
        "notes": "Public site and docs confirm GitHub-hosted skills and packaged skill downloads, but the submit flow is login-gated and no stable publish API is public.",
        "recon": [{"url": "https://skillery.dev/submit", "markers": ["submit", "login", "skill"]}],
    },
    "skillszoo": {
        "title": "SkillsZoo",
        "mode": "manual-web",
        "status": "auth-required",
        "auth": "Login required",
        "requires": ["repo_url"],
        "source_url": "https://www.skillszoo.com/submit",
        "submit_url": "https://www.skillszoo.com/submit",
        "verify": "Use site search plus profile-side My Submissions after a logged-in submit.",
        "notes": "Public form fields are visible, but the site uses a review queue and does not expose a stable documented submission API.",
        "recon": [{"url": "https://www.skillszoo.com/submit", "markers": ["Skill Name", "GitHub Repository URL", "My Submissions"]}],
    },
    "skillhub-club": {
        "title": "SkillHub",
        "mode": "manual-web",
        "status": "auth-required",
        "auth": "Login required for management and publish",
        "requires": [],
        "source_url": "https://www.skillhub.club/docs/cli",
        "submit_url": "https://www.skillhub.club/app/skills",
        "verify": "Use the public skills directory or generated detail page under https://www.skillhub.club/skills.",
        "notes": "Official CLI documents login, push, and publish, while the app also supports SKILL.md or zip uploads. This skill documents the flow but does not wrap the CLI yet.",
        "recon": [{"url": "https://www.skillhub.club/docs/cli", "markers": ["npx @skill-hub/cli login", "npx @skill-hub/cli publish", "Push local skill files to remote SkillHub"]}],
    },
    "skillshop-sh": {
        "title": "SkillShop",
        "mode": "index-only",
        "status": "verified",
        "auth": "GitHub App install required for sellers",
        "requires": [],
        "source_url": "https://skillshop.sh/agent.md",
        "submit_url": None,
        "verify": "Use GET https://skillshop.sh/api/skills/<org>/<repo> or the public /skills/<org>/<repo> page.",
        "notes": "Selling requires GitHub org setup and the SkillShop app. There is no normal upload API on SkillShop itself.",
        "recon": [{"url": "https://skillshop.sh/agent.md", "markers": ["there is no upload API on SkillShop itself", "GET /api/skills/{org}/{repo}"]}],
    },
    "skillhq-dev": {
        "title": "SkillHQ",
        "mode": "manual-web",
        "status": "auth-required",
        "auth": "Seller onboarding and payout setup",
        "requires": [],
        "source_url": "https://skillhq.dev/become-seller",
        "submit_url": "https://skillhq.dev/become-seller",
        "verify": "Use the public listing page after publish and the official install flow once the listing exists.",
        "notes": "Official seller docs describe skillhq validate ./my-skill and skillhq publish ./my-skill --price <usd> --category <category> for skills that include SKILL.md and README.md.",
        "recon": [{"url": "https://skillhq.dev/become-seller", "markers": ["skillhq validate ./my-skill", "skillhq publish ./my-skill --price 12 --category development", "SKILL.md"]}],
    },
    "bogen-ai": {
        "title": "Bogen.ai",
        "mode": "auto-http",
        "status": "verified",
        "auth": "None",
        "requires": ["author_name", "author_email", "bogen_category"],
        "source_url": "https://www.bogen.ai/skills/submit",
        "submit_url": "https://www.bogen.ai/api/skills/submit",
        "verify": "Use the public skills directory at https://www.bogen.ai/skills/ after review.",
        "notes": "Public API accepts pasted SKILL.md content and queues a review. Duplicate-name or pending-review 400 responses can still mean the listing identity is already in the pipeline.",
        "recon": [{"url": "https://www.bogen.ai/skills/submit", "markers": ["SKILL.md Content", "Submit Skill for Review", "Skill Name", "/api/skills/submit"]}],
    },
    "skillsrep": {
        "title": "skillsrep.com",
        "mode": "auto-http",
        "status": "verified",
        "auth": "None",
        "requires": ["repo_url", "version"],
        "source_url": "https://skillsrep.com/submit",
        "submit_url": "https://skillsrep.com/submit",
        "verify": "Use https://skillsrep.com/skill/<slug> and https://skillsrep.com/search?q=<skill-name>.",
        "notes": "Anonymous HTML form uses a server-side CSRF token and can redirect straight to a public detail page. A missing success flash is weaker evidence than the final URL.",
        "recon": [{"url": "https://skillsrep.com/submit", "markers": ["Code / Skill Definition", "CLAUDE.md Instructions", "MCP Server Config"]}],
    },
}


@dataclass
class SkillInfo:
    name: str
    title: str
    description: str
    overview: str
    path: str
    repo_root: str | None
    relative_skill_dir: str
    repo_layout: str
    license: str | None


def fail(message: str) -> None:
    print(f"[ERROR] {message}", file=sys.stderr)
    raise SystemExit(1)


def read_text(url: str, timeout: int = 20) -> str:
    req = request.Request(url, headers={"User-Agent": USER_AGENT})
    with request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", "ignore")


def unquote_scalar(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def parse_simple_frontmatter(frontmatter_text: str) -> dict[str, Any]:
    parsed: dict[str, Any] = {}
    current_key: str | None = None
    for raw_line in frontmatter_text.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if raw_line.startswith((" ", "\t")):
            if current_key:
                continuation = raw_line.strip()
                if continuation:
                    parsed[current_key] = f"{parsed.get(current_key, '')} {continuation}".strip()
            continue
        if ":" not in raw_line:
            current_key = None
            continue
        key, value = raw_line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not re.match(r"^[A-Za-z0-9_-]+$", key):
            current_key = None
            continue
        parsed[key] = unquote_scalar(value)
        current_key = key
    return parsed


def parse_frontmatter_text(frontmatter_text: str) -> dict[str, Any]:
    if yaml is not None:
        parsed = yaml.safe_load(frontmatter_text)
        if isinstance(parsed, dict):
            return parsed
    return parse_simple_frontmatter(frontmatter_text)


def strip_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    match = re.match(r"^---\n(.*?)\n---\n?", content, re.DOTALL)
    if not match:
        fail("SKILL.md is missing YAML frontmatter.")
    frontmatter = parse_frontmatter_text(match.group(1))
    if not isinstance(frontmatter, dict):
        fail("SKILL.md frontmatter must be a YAML dictionary.")
    return frontmatter, content[match.end() :]


def find_first_heading(body: str) -> str | None:
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None


def first_paragraph(body: str) -> str:
    in_code = False
    buffer: list[str] = []
    for raw_line in body.splitlines():
        line = raw_line.rstrip()
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        stripped = line.strip()
        if not stripped:
            paragraph = " ".join(buffer).strip()
            if paragraph:
                return paragraph
            buffer = []
            continue
        if stripped.startswith(("#", "-", "*", ">", "|")) or re.match(r"^\d+\.\s", stripped):
            if buffer:
                paragraph = " ".join(buffer).strip()
                if paragraph:
                    return paragraph
                buffer = []
            continue
        buffer.append(stripped)
    return " ".join(buffer).strip()


def title_case(name: str) -> str:
    return " ".join(part.capitalize() for part in name.split("-"))


def run_git_root(cwd: Path) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def detect_repo_layout(skill_path: Path, repo_root: Path | None) -> tuple[str, str]:
    if repo_root is None:
        return "standalone-skill-dir", "."

    if skill_path == repo_root:
        return "single-skill-repo", "."

    relative_dir = skill_path.relative_to(repo_root).as_posix()
    skills_dir = repo_root / "skills"
    if skills_dir.exists() and skill_path.is_relative_to(skills_dir):
        return "skills-subdir-pack", relative_dir

    root_skill_count = len(list(repo_root.glob("*/SKILL.md")))
    if skill_path.parent == repo_root and root_skill_count > 1:
        return "root-pack", relative_dir

    return "nested-skill-dir", relative_dir


def load_skill(skill_target: str) -> SkillInfo:
    skill_path = Path(skill_target).expanduser().resolve()
    if skill_path.is_file():
        if skill_path.name != "SKILL.md":
            fail("If a file path is provided, it must point to SKILL.md.")
        skill_path = skill_path.parent

    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        fail(f"SKILL.md not found under {skill_path}")

    frontmatter, body = strip_frontmatter(skill_md.read_text())
    name = str(frontmatter.get("name") or "").strip()
    description = str(frontmatter.get("description") or "").strip()
    if not name or not description:
        fail("SKILL.md frontmatter must include both name and description.")

    title = find_first_heading(body) or title_case(name)
    overview = first_paragraph(body) or description
    repo_root_str = run_git_root(skill_path)
    repo_root = Path(repo_root_str).resolve() if repo_root_str else None
    repo_layout, relative_skill_dir = detect_repo_layout(skill_path, repo_root)

    license_value = frontmatter.get("license")
    return SkillInfo(
        name=name,
        title=title,
        description=description,
        overview=overview,
        path=str(skill_path),
        repo_root=str(repo_root) if repo_root else None,
        relative_skill_dir=relative_skill_dir,
        repo_layout=repo_layout,
        license=str(license_value).strip() if license_value else None,
    )


def clean_repo_url(repo_url: str | None) -> str | None:
    if not repo_url:
        return None
    normalized = repo_url.strip().rstrip("/")
    if normalized.endswith(".git"):
        normalized = normalized[:-4]
    return normalized


def github_repo_parts(repo_url: str | None) -> tuple[str, str] | None:
    if not repo_url:
        return None
    parsed = parse.urlparse(repo_url)
    if parsed.netloc not in {"github.com", "www.github.com"}:
        return None
    parts = [part for part in parsed.path.strip("/").split("/") if part]
    if len(parts) < 2:
        return None
    return parts[0], parts[1]


def github_repo_slug(repo_url: str | None) -> str | None:
    parts = github_repo_parts(repo_url)
    if not parts:
        return None
    owner, repo = parts
    return f"{owner}/{repo}"


def github_owner_url(repo_url: str | None) -> str | None:
    parts = github_repo_parts(repo_url)
    if not parts:
        return None
    owner, _repo = parts
    return f"https://github.com/{owner}"


def github_skill_urls(repo_url: str | None, git_ref: str | None, relative_skill_dir: str) -> dict[str, str | None]:
    if not repo_url or not git_ref:
        return {"skill_url": None, "raw_skill_url": None}

    parts = github_repo_parts(repo_url)
    if not parts:
        return {"skill_url": None, "raw_skill_url": None}

    owner, repo = parts
    skill_md_path = "SKILL.md" if relative_skill_dir == "." else f"{relative_skill_dir}/SKILL.md"
    return {
        "skill_url": f"https://github.com/{owner}/{repo}/blob/{git_ref}/{skill_md_path}",
        "raw_skill_url": f"https://raw.githubusercontent.com/{owner}/{repo}/{git_ref}/{skill_md_path}",
    }


def github_tree_url(repo_url: str | None, git_ref: str | None, relative_skill_dir: str) -> str | None:
    if not repo_url:
        return None
    parts = github_repo_parts(repo_url)
    if not parts:
        return repo_url
    if not git_ref or relative_skill_dir == ".":
        return repo_url
    owner, repo = parts
    return f"https://github.com/{owner}/{repo}/tree/{git_ref}/{relative_skill_dir}"


def github_pack_url(context: dict[str, Any]) -> str | None:
    repo_url = context["repo"]["repo_url"]
    git_ref = context["repo"]["git_ref"]
    if not repo_url:
        return None

    parts = github_repo_parts(repo_url)
    if not parts or not git_ref:
        return repo_url

    owner, repo = parts
    layout = context["skill"]["repo_layout"]
    if layout == "skills-subdir-pack":
        return f"https://github.com/{owner}/{repo}/tree/{git_ref}/skills"
    if layout == "root-pack":
        return f"https://github.com/{owner}/{repo}/tree/{git_ref}"
    return github_tree_url(repo_url, git_ref, context["skill"]["relative_skill_dir"]) or repo_url


def unique_tags(values: list[str]) -> list[str]:
    seen: set[str] = set()
    tags: list[str] = []
    for raw in values:
        for part in raw.split(","):
            tag = part.strip()
            if tag and tag not in seen:
                seen.add(tag)
                tags.append(tag)
    return tags


def read_skill_markdown(context: dict[str, Any]) -> str:
    return (Path(context["skill"]["path"]) / "SKILL.md").read_text()


def summarize(text: str, limit: int = 180) -> str:
    sentence = re.split(r"(?<=[.!?])\s+", text.strip(), maxsplit=1)[0]
    candidate = sentence if sentence else text.strip()
    if len(candidate) <= limit:
        return candidate
    clipped = candidate[: limit - 1].rstrip()
    if " " in clipped:
        clipped = clipped.rsplit(" ", 1)[0]
    return clipped + "..."


def build_context(args: argparse.Namespace) -> dict[str, Any]:
    skill = load_skill(args.skill_path)
    repo_url = clean_repo_url(getattr(args, "repo_url", None))
    tags = unique_tags(getattr(args, "tags", []) or [])
    summary_source = getattr(args, "summary", None) or skill.overview or skill.description
    urls = github_skill_urls(repo_url, getattr(args, "git_ref", None), skill.relative_skill_dir)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "skill": asdict(skill),
        "repo": {
            "repo_url": repo_url,
            "git_ref": getattr(args, "git_ref", None),
            "skill_url": urls["skill_url"],
            "raw_skill_url": urls["raw_skill_url"],
        },
        "submission": {
            "summary": summarize(summary_source),
            "description": skill.description,
            "overview": skill.overview,
            "tags": tags,
            "version": getattr(args, "version", None),
            "author_name": getattr(args, "author_name", None),
            "author_email": getattr(args, "author_email", None),
            "image_url": getattr(args, "image_url", None),
            "skillz_category": getattr(args, "skillz_category", None),
            "bogen_category": getattr(args, "bogen_category", None),
            "a2a_price": getattr(args, "a2a_price", None),
            "a2a_category": getattr(args, "a2a_category", None),
            "a2a_seller": getattr(args, "a2a_seller", None),
        },
    }


def required_value(context: dict[str, Any], field: str) -> Any:
    if field == "repo_url":
        return context["repo"]["repo_url"]
    if field == "git_ref":
        return context["repo"]["git_ref"]
    return context["submission"].get(field)


def build_plan(context: dict[str, Any]) -> list[dict[str, Any]]:
    layout = context["skill"]["repo_layout"]
    plan: list[dict[str, Any]] = []
    for slug, market in MARKETS.items():
        missing = [field for field in market.get("requires", []) if not required_value(context, field)]
        warnings: list[str] = []
        preferred_layouts = market.get("preferred_layouts")
        if preferred_layouts and layout not in preferred_layouts:
            warnings.append(
                f"Current repo layout is {layout}; preferred layouts: {', '.join(preferred_layouts)}"
            )

        live_possible = market["mode"] in {"auto-cli", "auto-http"} and not missing and not warnings
        bundle_possible = market["mode"] != "incompatible" and not missing
        plan.append(
            {
                "market": slug,
                "title": market["title"],
                "mode": market["mode"],
                "status": market["status"],
                "ready_for_bundle": bundle_possible,
                "ready_for_live_publish": live_possible,
                "missing": missing,
                "warnings": warnings,
                "auth": market.get("auth"),
                "verify": market.get("verify"),
                "notes": market["notes"],
                "source_url": market["source_url"],
                "submit_url": market["submit_url"],
            }
        )
    return plan


def print_json(data: Any) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))


def print_inspect(context: dict[str, Any], json_mode: bool) -> None:
    if json_mode:
        print_json(context)
        return
    skill = context["skill"]
    repo = context["repo"]
    submission = context["submission"]
    print(f"Name: {skill['name']}")
    print(f"Title: {skill['title']}")
    print(f"Path: {skill['path']}")
    print(f"Repo layout: {skill['repo_layout']}")
    print(f"Repo root: {skill['repo_root'] or '(none)'}")
    print(f"Relative skill dir: {skill['relative_skill_dir']}")
    print(f"Repo URL: {repo['repo_url'] or '(none)'}")
    print(f"Skill URL: {repo['skill_url'] or '(none)'}")
    print(f"Summary: {submission['summary']}")


def print_plan(plan: list[dict[str, Any]], json_mode: bool) -> None:
    if json_mode:
        print_json(plan)
        return

    header = f"{'Market':22} {'Mode':12} {'Bundle':7} {'Live':5} Missing"
    print(header)
    print("-" * len(header))
    for item in plan:
        missing = ", ".join(item["missing"]) if item["missing"] else "-"
        bundle = "yes" if item["ready_for_bundle"] else "no"
        live = "yes" if item["ready_for_live_publish"] else "no"
        print(f"{item['market']:22} {item['mode']:12} {bundle:7} {live:5} {missing}")
        for warning in item["warnings"]:
            print(f"  warning: {warning}")


def build_agent_skills_index_payload(context: dict[str, Any]) -> dict[str, str]:
    repo_url = context["repo"]["repo_url"]
    if not repo_url:
        raise ValueError("agent-skills-index requires --repo-url.")
    return {"github_url": repo_url}


def build_agent_skills_md_payload(context: dict[str, Any]) -> dict[str, Any]:
    repo_url = github_pack_url(context)
    if not repo_url:
        raise ValueError("agent-skills-md requires --repo-url.")
    return {"json": {"url": repo_url}}


def build_agentskill_sh_payload(context: dict[str, Any]) -> dict[str, str]:
    repo_url = context["repo"]["repo_url"]
    if not repo_url:
        raise ValueError("agentskill-sh requires --repo-url.")
    return {"url": repo_url}


def build_skillz_payload(context: dict[str, Any]) -> dict[str, Any]:
    submission = context["submission"]
    repo_url = context["repo"]["repo_url"]
    if not repo_url:
        raise ValueError("skillz-directory requires --repo-url.")
    if not submission["author_email"]:
        raise ValueError("skillz-directory requires --author-email.")
    if not submission["skillz_category"]:
        raise ValueError("skillz-directory requires --skillz-category.")
    return {
        "name": context["skill"]["title"],
        "email": submission["author_email"],
        "description": context["skill"]["description"],
        "githubUrl": repo_url,
        "category": submission["skillz_category"],
        "tags": submission["tags"],
        "imageUrl": submission["image_url"] or "",
    }


def build_skillstore_payload(context: dict[str, Any]) -> dict[str, str]:
    repo_url = context["repo"]["repo_url"]
    if not repo_url:
        raise ValueError("skillstore-io requires --repo-url.")
    target_url = github_tree_url(repo_url, context["repo"]["git_ref"], context["skill"]["relative_skill_dir"]) or repo_url
    return {"github_url": target_url}


def build_a2a_payload(context: dict[str, Any]) -> dict[str, Any]:
    submission = context["submission"]
    missing = [field for field in ("a2a_price", "a2a_category", "a2a_seller") if not submission[field]]
    if missing:
        raise ValueError(f"a2a-market requires: {', '.join(missing)}")
    return {
        "name": context["skill"]["title"],
        "description": context["skill"]["description"],
        "price": submission["a2a_price"],
        "category": submission["a2a_category"],
        "seller": submission["a2a_seller"],
    }


def build_skillsmd_payload(context: dict[str, Any]) -> dict[str, Any]:
    repo_slug = github_repo_slug(context["repo"]["repo_url"])
    if not repo_slug:
        raise ValueError("skillsmd-dev requires a GitHub --repo-url like https://github.com/owner/repo.")
    payload: dict[str, Any] = {
        "repo": repo_slug,
        "name": context["skill"]["name"],
        "description": context["skill"]["description"],
    }
    if context["submission"]["author_email"]:
        payload["email"] = context["submission"]["author_email"]
    return payload


def build_bogen_payload(context: dict[str, Any]) -> dict[str, Any]:
    submission = context["submission"]
    missing = [field for field in ("author_name", "author_email", "bogen_category") if not submission[field]]
    if missing:
        raise ValueError(f"bogen-ai requires: {', '.join(missing)}")
    payload: dict[str, Any] = {
        "name": context["skill"]["name"],
        "category": submission["bogen_category"],
        "description": context["skill"]["description"],
        "skill_content": read_skill_markdown(context),
        "author_name": submission["author_name"],
        "author_email": submission["author_email"],
        "is_free": True,
    }
    author_website = github_owner_url(context["repo"]["repo_url"]) or context["repo"]["repo_url"]
    if author_website:
        payload["author_website"] = author_website
    return payload


def build_skillsrep_payload(context: dict[str, Any]) -> dict[str, str]:
    repo_url = context["repo"]["repo_url"]
    version = context["submission"]["version"]
    if not repo_url:
        raise ValueError("skillsrep requires --repo-url.")
    if not version:
        raise ValueError("skillsrep requires --version.")

    submission = context["submission"]
    skill_dir_url = github_tree_url(repo_url, context["repo"]["git_ref"], context["skill"]["relative_skill_dir"]) or repo_url
    usage_examples = "\n".join(
        [
            f"Open {context['repo']['skill_url'] or skill_dir_url} and review the skill instructions.",
            f"Use this skill when you need {submission['summary']}",
        ]
    )
    tags = submission["tags"] or [context["skill"]["name"]]
    creator_name = submission["author_name"] or (github_repo_parts(repo_url)[0] if github_repo_parts(repo_url) else "")
    creator_url = github_owner_url(repo_url) or repo_url
    return {
        "name": context["skill"]["name"],
        "description": context["skill"]["description"],
        "code_snippet": read_skill_markdown(context),
        "usage_examples": usage_examples,
        "version": version,
        "external_url": skill_dir_url,
        "github_url": repo_url,
        "tags": ", ".join(tags),
        "creator_name": creator_name,
        "creator_url": creator_url,
        "submitter_name": creator_name,
    }


def build_clawhub_command(context: dict[str, Any], args: argparse.Namespace) -> list[str]:
    version = context["submission"]["version"]
    if not version:
        raise ValueError("clawhub requires --version.")
    return [args.clawhub_bin, "skill", "publish", context["skill"]["path"], "--version", version]


def manual_notes(context: dict[str, Any], plan: list[dict[str, Any]]) -> str:
    repo_url = context["repo"]["repo_url"] or "(set --repo-url first)"
    skill_url = context["repo"]["skill_url"] or "(set --repo-url and --git-ref first)"
    lines = [
        "# Manual Submission Notes",
        "",
        f"- Repository URL: {repo_url}",
        f"- SKILL.md URL: {skill_url}",
        f"- Repo layout: {context['skill']['repo_layout']}",
        "",
    ]
    for item in plan:
        if item["mode"] not in {"manual-web", "index-only", "needs-recon", "incompatible"}:
            continue
        lines.append(f"## {item['title']} (`{item['market']}`)")
        lines.append("")
        lines.append(f"- Mode: `{item['mode']}`")
        if item.get("auth"):
            lines.append(f"- Auth: {item['auth']}")
        if item["submit_url"]:
            lines.append(f"- Submit URL: {item['submit_url']}")
        lines.append(f"- Status: `{item['status']}`")
        if item["missing"]:
            lines.append(f"- Missing inputs: {', '.join(item['missing'])}")
        if item["warnings"]:
            for warning in item["warnings"]:
                lines.append(f"- Warning: {warning}")
        if item.get("verify"):
            lines.append(f"- Verify: {item['verify']}")
        lines.append(f"- Notes: {item['notes']}")
        lines.append("")
    return "\n".join(lines)


def write_bundle(context: dict[str, Any], plan: list[dict[str, Any]], out_dir: Path, args: argparse.Namespace) -> None:
    payload_dir = out_dir / "payloads"
    payload_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "manifest.json").write_text(json.dumps(context, indent=2, ensure_ascii=False) + "\n")
    (out_dir / "market-plan.json").write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n")
    (out_dir / "manual-submissions.md").write_text(manual_notes(context, plan) + "\n")

    payload_builders = {
        "agent-skills-index.form.json": lambda: build_agent_skills_index_payload(context),
        "agent-skills-md.json": lambda: build_agent_skills_md_payload(context),
        "agentskill-sh.json": lambda: build_agentskill_sh_payload(context),
        "skillz-directory.json": lambda: build_skillz_payload(context),
        "skillstore-io.json": lambda: build_skillstore_payload(context),
        "skillsmd-dev.json": lambda: build_skillsmd_payload(context),
        "bogen-ai.json": lambda: build_bogen_payload(context),
        "skillsrep.form.json": lambda: build_skillsrep_payload(context),
        "a2a-market.json": lambda: build_a2a_payload(context),
        "clawhub-command.txt": lambda: build_clawhub_command(context, args),
    }
    for filename, builder in payload_builders.items():
        output_path = payload_dir / filename
        try:
            payload = builder()
        except ValueError as exc:
            output_path.with_suffix(output_path.suffix + ".missing").write_text(str(exc) + "\n")
            continue
        if isinstance(payload, list):
            output_path.write_text(" ".join(payload) + "\n")
        else:
            output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def dry_run_output(market: str, payload: Any) -> None:
    print(f"[DRY RUN] {market}")
    if isinstance(payload, list):
        print("Command:")
        print(" ".join(payload))
        return
    print_json(payload)


def post_json(submit_url: str, payload: dict[str, Any], headers: dict[str, str] | None = None) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req_headers = {
        "User-Agent": USER_AGENT,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if headers:
        req_headers.update(headers)
    req = request.Request(
        submit_url,
        data=data,
        headers=req_headers,
        method="POST",
    )
    with request.urlopen(req, timeout=20) as resp:
        body = resp.read().decode("utf-8", "ignore")
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            parsed = body
        return {"status": resp.status, "body": parsed}


def fetch_html(url: str, opener: request.OpenerDirector | None = None, timeout: int = 20) -> tuple[int, str, str]:
    req = request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    opener = opener or request.build_opener()
    with opener.open(req, timeout=timeout) as resp:
        return resp.status, resp.geturl(), resp.read().decode("utf-8", "ignore")


def post_form(
    submit_url: str,
    payload: dict[str, str],
    opener: request.OpenerDirector | None = None,
    headers: dict[str, str] | None = None,
    timeout: int = 20,
) -> dict[str, Any]:
    data = parse.urlencode(payload).encode("utf-8")
    req_headers = {
        "User-Agent": USER_AGENT,
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "text/html,application/xhtml+xml",
    }
    if headers:
        req_headers.update(headers)
    req = request.Request(submit_url, data=data, headers=req_headers, method="POST")
    opener = opener or request.build_opener()
    with opener.open(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8", "ignore")
        return {
            "status": resp.status,
            "final_url": resp.geturl(),
            "body_excerpt": body[:500],
        }


def extract_hidden_input(html: str, name: str) -> str | None:
    pattern = rf'<input[^>]+name=["\']{re.escape(name)}["\'][^>]+value=["\']([^"\']+)["\']'
    match = re.search(pattern, html, re.IGNORECASE)
    return match.group(1) if match else None


def submit_agentskill_sh(context: dict[str, Any], execute: bool) -> dict[str, Any]:
    try:
        payload = build_agentskill_sh_payload(context)
    except ValueError as exc:
        fail(str(exc))
    if not execute:
        dry_run_output("agentskill-sh", payload)
        return {"dry_run": True, "payload": payload}
    return post_json(MARKETS["agentskill-sh"]["submit_url"], payload)


def submit_agent_skills_md(context: dict[str, Any], execute: bool) -> dict[str, Any]:
    try:
        payload = build_agent_skills_md_payload(context)
    except ValueError as exc:
        fail(str(exc))
    if not execute:
        dry_run_output("agent-skills-md", payload)
        return {"dry_run": True, "payload": payload}
    return post_json(MARKETS["agent-skills-md"]["submit_url"], payload)


def submit_skillz_directory(context: dict[str, Any], execute: bool) -> dict[str, Any]:
    try:
        payload = build_skillz_payload(context)
    except ValueError as exc:
        fail(str(exc))
    if not execute:
        dry_run_output("skillz-directory", payload)
        return {"dry_run": True, "payload": payload}
    return post_json(MARKETS["skillz-directory"]["submit_url"], payload)


def submit_skillstore_io(context: dict[str, Any], execute: bool) -> dict[str, Any]:
    try:
        payload = build_skillstore_payload(context)
    except ValueError as exc:
        fail(str(exc))
    if not execute:
        dry_run_output("skillstore-io", payload)
        return {"dry_run": True, "payload": payload}
    return post_json(MARKETS["skillstore-io"]["submit_url"], payload)


def submit_skillsmd_dev(context: dict[str, Any], execute: bool) -> dict[str, Any]:
    try:
        payload = build_skillsmd_payload(context)
    except ValueError as exc:
        fail(str(exc))
    if not execute:
        dry_run_output("skillsmd-dev", payload)
        return {"dry_run": True, "payload": payload}
    return post_json(MARKETS["skillsmd-dev"]["submit_url"], payload)


def submit_bogen_ai(context: dict[str, Any], execute: bool) -> dict[str, Any]:
    try:
        payload = build_bogen_payload(context)
    except ValueError as exc:
        fail(str(exc))
    if not execute:
        dry_run_output("bogen-ai", payload)
        return {"dry_run": True, "payload": payload}
    return post_json(MARKETS["bogen-ai"]["submit_url"], payload)


def submit_skillsrep(context: dict[str, Any], execute: bool) -> dict[str, Any]:
    try:
        payload = build_skillsrep_payload(context)
    except ValueError as exc:
        fail(str(exc))
    if not execute:
        dry_run_output("skillsrep", payload)
        return {"dry_run": True, "payload": payload}

    opener = request.build_opener(request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    _status, _url, html = fetch_html(MARKETS["skillsrep"]["submit_url"], opener=opener)
    csrf_token = extract_hidden_input(html, "csrf_token")
    if not csrf_token:
        fail("skillsrep submit page did not expose csrf_token.")

    result = post_form(
        MARKETS["skillsrep"]["submit_url"],
        {"csrf_token": csrf_token, **payload},
        opener=opener,
        headers={"Referer": MARKETS["skillsrep"]["submit_url"]},
    )
    result["success_flash"] = "submitted successfully" in result["body_excerpt"].lower()
    return result


def submit_a2a_market(context: dict[str, Any], execute: bool) -> dict[str, Any]:
    try:
        payload = build_a2a_payload(context)
    except ValueError as exc:
        fail(str(exc))
    if not execute:
        dry_run_output("a2a-market", payload)
        return {"dry_run": True, "payload": payload}
    return post_json(MARKETS["a2a-market"]["submit_url"], payload)


def submit_clawhub(context: dict[str, Any], args: argparse.Namespace, execute: bool) -> dict[str, Any]:
    try:
        command = build_clawhub_command(context, args)
    except ValueError as exc:
        fail(str(exc))
    if not execute:
        dry_run_output("clawhub", command)
        return {"dry_run": True, "command": command}

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def fetch_recon(url: str) -> str:
    try:
        return read_text(url)
    except error.HTTPError as exc:
        return exc.read().decode("utf-8", "ignore")
    except error.URLError as exc:
        return f"URL_ERROR:{exc}"


def collect_recon_content(market_name: str, url: str) -> str:
    content = fetch_recon(url)
    if market_name != "skillz-directory":
        return content

    chunk_paths = re.findall(r'src="([^"]+_next/static/chunks/[^"]+)"', content)
    combined = [content]
    base_url = "https://www.skillz.directory"
    for chunk_path in chunk_paths[:20]:
        absolute = parse.urljoin(base_url, chunk_path)
        chunk = fetch_recon(absolute)
        if "/api/submit" in chunk or "githubUrl" in chunk:
            combined.append(chunk)
            break
    return "\n".join(combined)


def run_recon(markets: list[str]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for market_name in markets:
        if market_name not in MARKETS:
            fail(f"Unknown market: {market_name}")
        market = MARKETS[market_name]
        for probe in market.get("recon", []):
            content = collect_recon_content(market_name, probe["url"])
            matched = [marker for marker in probe["markers"] if marker in content]
            results.append(
                {
                    "market": market_name,
                    "url": probe["url"],
                    "matched": matched,
                    "missing": [marker for marker in probe["markers"] if marker not in content],
                    "ok": len(matched) == len(probe["markers"]),
                }
            )
    return results


def print_recon(results: list[dict[str, Any]], json_mode: bool) -> None:
    if json_mode:
        print_json(results)
        return
    for item in results:
        status = "ok" if item["ok"] else "check"
        print(f"{item['market']}: {status}")
        print(f"  url: {item['url']}")
        print(f"  matched: {', '.join(item['matched']) if item['matched'] else '-'}")
        if item["missing"]:
            print(f"  missing: {', '.join(item['missing'])}")


def add_shared_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("skill_path", help="Path to the skill directory or SKILL.md file")
    parser.add_argument("--repo-url", help="Public repository URL for repository-based markets")
    parser.add_argument("--git-ref", help="Git ref used to build SKILL.md URLs")
    parser.add_argument("--tag", dest="tags", action="append", default=[], help="Tag to include in the bundle")
    parser.add_argument("--summary", help="Override the generated short summary")
    parser.add_argument("--version", help="Version for versioned markets such as ClawHub")
    parser.add_argument("--author-name", help="Author or submitter name for markets that require it")
    parser.add_argument("--author-email", help="Contact email for markets that require it")
    parser.add_argument("--image-url", help="Optional image URL for directory submissions")
    parser.add_argument(
        "--skillz-category",
        choices=SKILLZ_CATEGORIES,
        help="Category used by Skillz Directory",
    )
    parser.add_argument(
        "--bogen-category",
        choices=BOGEN_CATEGORIES,
        help="Category used by Bogen.ai",
    )
    parser.add_argument("--a2a-price", type=float, help="Listing price for A2A Market")
    parser.add_argument("--a2a-category", help="Listing category for A2A Market")
    parser.add_argument("--a2a-seller", help="Seller wallet address for A2A Market")
    parser.add_argument("--json", action="store_true", help="Emit JSON")


def command_inspect(args: argparse.Namespace) -> None:
    context = build_context(args)
    print_inspect(context, args.json)


def command_plan(args: argparse.Namespace) -> None:
    context = build_context(args)
    plan = build_plan(context)
    print_plan(plan, args.json)


def command_bundle(args: argparse.Namespace) -> None:
    context = build_context(args)
    plan = build_plan(context)
    out_dir = Path(args.out_dir).expanduser().resolve()
    write_bundle(context, plan, out_dir, args)
    print(f"[OK] Wrote bundle to {out_dir}")


def command_publish(args: argparse.Namespace) -> None:
    context = build_context(args)
    market = args.market
    if market not in MARKETS:
        fail(f"Unknown market: {market}")

    try:
        if market == "agent-skills-md":
            result = submit_agent_skills_md(context, args.execute)
        elif market == "agentskill-sh":
            result = submit_agentskill_sh(context, args.execute)
        elif market == "skillz-directory":
            result = submit_skillz_directory(context, args.execute)
        elif market == "skillstore-io":
            result = submit_skillstore_io(context, args.execute)
        elif market == "skillsmd-dev":
            result = submit_skillsmd_dev(context, args.execute)
        elif market == "bogen-ai":
            result = submit_bogen_ai(context, args.execute)
        elif market == "skillsrep":
            result = submit_skillsrep(context, args.execute)
        elif market == "a2a-market":
            result = submit_a2a_market(context, args.execute)
        elif market == "clawhub":
            result = submit_clawhub(context, args, args.execute)
        else:
            fail(f"Live publish is not implemented for {market}.")
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", "ignore")
        fail(f"HTTP {exc.code} from {market}: {body[:500]}")

    if args.json:
        print_json(result)
    elif not args.execute:
        return
    else:
        print_json(result)


def command_recon(args: argparse.Namespace) -> None:
    market_names = args.markets or list(MARKETS.keys())
    results = run_recon(market_names)
    print_recon(results, args.json)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Prepare and publish local skills across public skill marketplaces.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """\
            Examples:
              python3 scripts/skill_market_publish.py plan ./my-skill --repo-url https://github.com/owner/repo
              python3 scripts/skill_market_publish.py bundle ./my-skill --repo-url https://github.com/owner/repo --git-ref main --author-name "Your Name" --author-email you@example.com --skillz-category automation --bogen-category development --a2a-price 5 --a2a-category development --a2a-seller 0xabc --out-dir /tmp/skill-market-bundle
              python3 scripts/skill_market_publish.py publish agentskill-sh ./my-skill --repo-url https://github.com/owner/repo --execute
            """
        ),
    )
    parser.set_defaults(func=None)

    inspect_parser = parser.add_subparsers(dest="command")

    sub = inspect_parser.add_parser("inspect", help="Inspect one skill")
    add_shared_arguments(sub)
    sub.set_defaults(func=command_inspect)

    sub = inspect_parser.add_parser("plan", help="Build a market readiness plan")
    add_shared_arguments(sub)
    sub.set_defaults(func=command_plan)

    sub = inspect_parser.add_parser("bundle", help="Write a reusable submission bundle")
    add_shared_arguments(sub)
    sub.add_argument("--out-dir", required=True, help="Output directory for the bundle")
    sub.add_argument("--clawhub-bin", default="clawhub", help="Executable name for the ClawHub CLI")
    sub.set_defaults(func=command_bundle)

    sub = inspect_parser.add_parser("publish", help="Publish one verified market")
    sub.add_argument(
        "market",
        choices=[
            "clawhub",
            "agent-skills-md",
            "agentskill-sh",
            "skillz-directory",
            "skillstore-io",
            "skillsmd-dev",
            "bogen-ai",
            "skillsrep",
            "a2a-market",
        ],
    )
    add_shared_arguments(sub)
    sub.add_argument("--execute", action="store_true", help="Perform the live publish instead of a dry run")
    sub.add_argument("--clawhub-bin", default="clawhub", help="Executable name for the ClawHub CLI")
    sub.set_defaults(func=command_publish)

    sub = inspect_parser.add_parser("recon", help="Re-verify known market surfaces")
    sub.add_argument("markets", nargs="*", help="Specific markets to verify")
    sub.add_argument("--json", action="store_true", help="Emit JSON")
    sub.set_defaults(func=command_recon)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if not args.func:
        parser.print_help()
        raise SystemExit(1)
    args.func(args)


if __name__ == "__main__":
    main()
