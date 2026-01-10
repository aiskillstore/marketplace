#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "pydantic>=2.8.2",
#     "httpx>=0.27.2",
#     "PyYAML>=6.0.3",
#     "rich>=14.2.0",
#     "typer>=0.21.0",
# ]
# ///
"""一次性读取 GitHub PR 多维信息的脚本。"""

from __future__ import annotations

import re
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple
from urllib.parse import urlparse

import httpx
import typer
import yaml
from pydantic import BaseModel, ConfigDict
from rich.console import Console
from rich.panel import Panel

CONSOLE = Console()
API_BASE = "https://api.github.com"
DEFAULT_TIMEOUT = 30.0


def parse_pr_url(pr_url: str) -> Tuple[str, str, int]:
    """解析 GitHub PR URL 并返回 owner/repo/number。"""
    parsed = urlparse(pr_url)
    if parsed.netloc != "github.com":
        raise typer.BadParameter("仅支持 github.com 域名的 PR 链接。")

    match = re.match(r"^/([^/]+)/([^/]+)/pull/(\d+)", parsed.path)
    if not match:
        raise typer.BadParameter(
            "PR 链接格式应为 https://github.com/<owner>/<repo>/pull/<number>。"
        )

    owner, repo, number = match.group(1), match.group(2), int(match.group(3))
    return owner, repo, number


def resolve_token() -> str:
    """从 gh auth token 读取 GitHub Token。"""
    try:
        result = subprocess.run(
            ["gh", "auth", "token"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as exc:
        CONSOLE.print(Panel.fit("[red]未找到 gh 命令，请先安装 GitHub CLI。[/red]"))
        raise typer.Exit(code=1) from exc
    token = result.stdout.strip() if result.returncode == 0 else ""
    if not token:
        CONSOLE.print(
            Panel.fit(
                "[red]无法从 gh auth token 获取访问令牌。[/red]\n"
                "请先执行 gh auth login 再运行脚本。"
            )
        )
        raise typer.Exit(code=1)
    return token


def build_headers(
    token: str, accept: str = "application/vnd.github+json"
) -> Dict[str, str]:
    """构造 GitHub API 请求头。"""
    return {
        "Accept": accept,
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def update_rate_limit_info(headers: httpx.Headers, info: Dict[str, Any]) -> None:
    """从响应头更新 rate limit 信息。"""
    limit = headers.get("X-RateLimit-Limit")
    remaining = headers.get("X-RateLimit-Remaining")
    reset = headers.get("X-RateLimit-Reset")
    if limit is not None:
        info["limit"] = int(limit)
    if remaining is not None:
        info["remaining"] = int(remaining)
    if reset is not None:
        try:
            info["reset_at"] = datetime.fromtimestamp(
                int(reset), tz=timezone.utc
            ).isoformat()
        except ValueError:
            info["reset_at"] = None


def request_json(
    client: httpx.Client,
    url: str,
    headers: Dict[str, str],
    params: Dict[str, Any] | None = None,
    rate_info: Dict[str, Any] | None = None,
) -> Any:
    """发送 JSON 请求并返回解析数据。"""
    response = client.get(url, headers=headers, params=params, timeout=DEFAULT_TIMEOUT)
    if rate_info is not None:
        update_rate_limit_info(response.headers, rate_info)
    if response.status_code >= 400:
        CONSOLE.print(Panel.fit(f"[red]{response.text}[/red]", title="请求失败"))
        raise typer.Exit(code=1)
    return response.json()


def request_text(
    client: httpx.Client,
    url: str,
    headers: Dict[str, str],
    params: Dict[str, Any] | None = None,
    rate_info: Dict[str, Any] | None = None,
) -> str:
    """发送文本请求并返回响应内容。"""
    response = client.get(url, headers=headers, params=params, timeout=DEFAULT_TIMEOUT)
    if rate_info is not None:
        update_rate_limit_info(response.headers, rate_info)
    if response.status_code >= 400:
        CONSOLE.print(Panel.fit(f"[red]{response.text}[/red]", title="请求失败"))
        raise typer.Exit(code=1)
    return response.text


def paginate(
    fetch_page: callable,
    limit: int,
    per_page: int = 100,
) -> List[Any]:
    """处理分页请求，最多拉取 limit 条。"""
    if limit <= 0:
        return []
    items: List[Any] = []
    page = 1
    while len(items) < limit:
        data = fetch_page(page, per_page)
        if not data:
            break
        remaining = limit - len(items)
        items.extend(data[:remaining])
        if len(data) < per_page:
            break
        page += 1
    return items


class ApiBaseModel(BaseModel):
    """GitHub REST API 精简模型基类。"""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)


class UserSlim(ApiBaseModel):
    """用户信息裁剪模型。"""

    login: str | None = None
    id: int | None = None


class ReviewSlim(ApiBaseModel):
    """PR review 信息裁剪模型。"""

    id: int | None = None
    state: str | None = None
    body: str | None = None
    submitted_at: str | None = None
    updated_at: str | None = None
    user: UserSlim | None = None


class IssueCommentSlim(ApiBaseModel):
    """Issue 评论信息裁剪模型。"""

    id: int | None = None
    body: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    user: UserSlim | None = None


class ReviewCommentSlim(ApiBaseModel):
    """Review 评论信息裁剪模型。"""

    id: int | None = None
    body: str | None = None
    path: str | None = None
    line: int | None = None
    created_at: str | None = None
    updated_at: str | None = None
    user: UserSlim | None = None


class FileSlim(ApiBaseModel):
    """文件变更信息裁剪模型。"""

    filename: str | None = None
    status: str | None = None
    additions: int | None = None
    deletions: int | None = None
    changes: int | None = None


class CommitAuthorSlim(ApiBaseModel):
    """提交作者信息裁剪模型。"""

    name: str | None = None
    date: str | None = None


class CommitInfoSlim(ApiBaseModel):
    """提交元信息裁剪模型。"""

    message: str | None = None
    author: CommitAuthorSlim | None = None


class CommitSlim(ApiBaseModel):
    """提交信息裁剪模型。"""

    sha: str | None = None
    commit: CommitInfoSlim | None = None


class SourceInfo(ApiBaseModel):
    """输出来源信息模型。"""

    url: str
    generated_at: str


class RateLimitInfo(ApiBaseModel):
    """GitHub API rate limit 信息模型。"""

    limit: int | None = None
    remaining: int | None = None
    reset_at: str | None = None


class CountedNodes(ApiBaseModel):
    """带总数统计的节点列表模型。"""

    totalCount: int
    nodes: List[Dict[str, Any]]


class Payload(ApiBaseModel):
    """脚本最终输出载体模型。"""

    source: SourceInfo
    viewer: UserSlim | None = None
    pr: Dict[str, Any] | None = None
    files: List[Dict[str, Any]] | None = None
    commits: List[Dict[str, Any]] | None = None
    comments: CountedNodes | None = None
    reviews: CountedNodes | None = None
    review_comments: CountedNodes | None = None
    diff: str | None = None
    rate_limit: RateLimitInfo | None = None


def to_dict_list(
    model: type[ApiBaseModel], items: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """用 pydantic 模型裁剪列表数据。"""
    return [model.model_validate(item).model_dump() for item in items]


def drop_none(value: Any) -> Any:
    """递归移除 None，避免 TOML 序列化失败。"""
    if isinstance(value, dict):
        return {key: drop_none(val) for key, val in value.items() if val is not None}
    if isinstance(value, list):
        return [drop_none(item) for item in value if item is not None]
    return value


def resolve_selection(
    body: bool,
    comments: bool,
    reviews: bool,
    review_comments: bool,
    files: bool,
    commits: bool,
    stats: bool,
    diff: bool,
) -> Dict[str, bool]:
    """统一输出每个模块是否需要拉取。"""
    return {
        "body": body,
        "comments": comments,
        "reviews": reviews,
        "review_comments": review_comments,
        "files": files,
        "commits": commits,
        "stats": stats,
        "diff": diff,
    }


def build_payload(
    pr_url: str,
    selection: Dict[str, bool],
    reviews_limit: int,
    comments_limit: int,
    review_comments_limit: int,
    files_limit: int,
    commits_limit: int,
    with_rate_limit: bool,
) -> Payload:
    """拉取所需信息并构造输出。"""
    payload = Payload(
        source=SourceInfo(
            url=pr_url,
            generated_at=datetime.now(timezone.utc).isoformat(),
        )
    )

    owner, repo, number = parse_pr_url(pr_url)
    token = resolve_token()
    base_headers = build_headers(token)

    rate_info: Dict[str, Any] = {}

    with httpx.Client(base_url=API_BASE, headers=base_headers) as client:
        viewer_data = request_json(
            client,
            "/user",
            base_headers,
            rate_info=rate_info,
        )
        payload.viewer = UserSlim.model_validate(viewer_data)
        if selection["body"] or selection["stats"]:
            pr_data = request_json(
                client,
                f"/repos/{owner}/{repo}/pulls/{number}",
                base_headers,
                rate_info=rate_info,
            )
            pr_payload: Dict[str, Any] = {}
            if selection["body"]:
                pr_payload["body"] = pr_data.get("body")
                pr_payload["title"] = pr_data.get("title")
                pr_payload["url"] = pr_data.get("html_url")
            if selection["stats"]:
                pr_payload["additions"] = pr_data.get("additions")
                pr_payload["deletions"] = pr_data.get("deletions")
                pr_payload["changedFiles"] = pr_data.get("changed_files")
            if pr_payload:
                payload.pr = pr_payload

        if selection["files"]:
            files = paginate(
                lambda page, per_page: request_json(
                    client,
                    f"/repos/{owner}/{repo}/pulls/{number}/files",
                    base_headers,
                    params={"page": page, "per_page": per_page},
                    rate_info=rate_info,
                ),
                limit=files_limit,
            )
            payload.files = to_dict_list(FileSlim, files)

        if selection["commits"]:
            commits = paginate(
                lambda page, per_page: request_json(
                    client,
                    f"/repos/{owner}/{repo}/pulls/{number}/commits",
                    base_headers,
                    params={"page": page, "per_page": per_page},
                    rate_info=rate_info,
                ),
                limit=commits_limit,
            )
            payload.commits = to_dict_list(CommitSlim, commits)

        if selection["comments"]:
            comments = paginate(
                lambda page, per_page: request_json(
                    client,
                    f"/repos/{owner}/{repo}/issues/{number}/comments",
                    base_headers,
                    params={"page": page, "per_page": per_page},
                    rate_info=rate_info,
                ),
                limit=comments_limit,
            )
            payload.comments = CountedNodes(
                totalCount=len(comments),
                nodes=to_dict_list(IssueCommentSlim, comments),
            )

        if selection["reviews"]:
            reviews = paginate(
                lambda page, per_page: request_json(
                    client,
                    f"/repos/{owner}/{repo}/pulls/{number}/reviews",
                    base_headers,
                    params={"page": page, "per_page": per_page},
                    rate_info=rate_info,
                ),
                limit=reviews_limit,
            )
            payload.reviews = CountedNodes(
                totalCount=len(reviews),
                nodes=to_dict_list(ReviewSlim, reviews),
            )

        if selection["review_comments"]:
            review_comments = paginate(
                lambda page, per_page: request_json(
                    client,
                    f"/repos/{owner}/{repo}/pulls/{number}/comments",
                    base_headers,
                    params={"page": page, "per_page": per_page},
                    rate_info=rate_info,
                ),
                limit=review_comments_limit,
            )
            payload.review_comments = CountedNodes(
                totalCount=len(review_comments),
                nodes=to_dict_list(ReviewCommentSlim, review_comments),
            )

        if selection["diff"]:
            diff_headers = build_headers(token, accept="application/vnd.github.v3.diff")
            payload.diff = request_text(
                client,
                f"/repos/{owner}/{repo}/pulls/{number}",
                diff_headers,
                rate_info=rate_info,
            )

    if with_rate_limit:
        payload.rate_limit = RateLimitInfo.model_validate(rate_info)

    return payload


def fetch(
    pr_url: str = typer.Argument(
        ...,
        help="PR 链接，例如 https://github.com/OWNER/REPO/pull/123。",
    ),
    body: bool = typer.Option(False, "--with-body", help="是否包含 PR body。"),
    comments: bool = typer.Option(
        False, "--with-comments", help="是否包含 issue comments。"
    ),
    reviews: bool = typer.Option(False, "--with-reviews", help="是否包含 reviews。"),
    review_comments: bool = typer.Option(
        False,
        "--with-review-comments",
        help="是否包含 review comments（REST 不提供线程结构）。",
    ),
    files: bool = typer.Option(False, "--with-files", help="是否包含文件列表。"),
    commits: bool = typer.Option(False, "--with-commits", help="是否包含提交列表。"),
    stats: bool = typer.Option(False, "--with-stats", help="是否包含增删行统计。"),
    diff: bool = typer.Option(False, "--with-diff", help="是否包含 diff 内容。"),
    with_rate_limit: bool = typer.Option(
        False, "--with-rate-limit", help="是否包含 rate limit 信息。"
    ),
    reviews_limit: int = typer.Option(20, help="reviews 最大数量。"),
    comments_limit: int = typer.Option(20, help="comments 最大数量。"),
    review_comments_limit: int = typer.Option(20, help="review comments 最大数量。"),
    files_limit: int = typer.Option(20, help="文件列表最大数量。"),
    commits_limit: int = typer.Option(20, help="提交列表最大数量。"),
) -> None:
    """拉取 PR 的主体信息、diff、评论与评审数据。"""
    selection = resolve_selection(
        body=body,
        comments=comments,
        reviews=reviews,
        review_comments=review_comments,
        files=files,
        commits=commits,
        stats=stats,
        diff=diff,
    )
    payload = build_payload(
        pr_url,
        selection,
        reviews_limit,
        comments_limit,
        review_comments_limit,
        files_limit,
        commits_limit,
        with_rate_limit,
    )
    sys.stdout.write(
        yaml.safe_dump(
            drop_none(payload.model_dump()),
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
        )
    )


if __name__ == "__main__":
    typer.run(fetch)
