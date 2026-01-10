#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "httpx>=0.28.1",
#     "pydantic>=2.12.5",
#     "rich>=14.2.0",
#     "typer>=0.20.1",
# ]
# ///
"""Exa 搜索与代码上下文命令行入口。"""

from __future__ import annotations

import json
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Any

import httpx
import typer
from pydantic import BaseModel, Field, ValidationError
from rich.console import Console

app = typer.Typer(help="Exa 搜索与代码上下文命令行工具")
console = Console()

DEFAULT_ENDPOINT = "https://mcp.exa.ai/mcp"
CACHE_TTL_SECONDS = 3600
CLIENT_INFO = {"name": "exa-cli", "version": "0.1.0"}
PROTOCOL_VERSION = "2024-11-05"


class ToolSpec(BaseModel):
    """工具的结构化描述。"""

    name: str
    required: list[str] = Field(default_factory=list)
    optional: list[str] = Field(default_factory=list)
    description: str | None = None


class McpRequest(BaseModel):
    """MCP JSON-RPC 请求模型。"""

    jsonrpc: str = "2.0"
    id: str
    method: str
    params: dict[str, Any] = Field(default_factory=dict)


class McpError(RuntimeError):
    """MCP 调用失败时的异常类型。"""


class CacheData(BaseModel):
    """本地缓存数据结构。"""

    created_at: float
    expires_at: float
    initialize_result: dict[str, Any] | None = None
    tools_list: dict[str, Any] | None = None


TOOL_SPECS: dict[str, ToolSpec] = {
    "web_search_exa": ToolSpec(
        name="web_search_exa",
        required=["query"],
        optional=["type", "livecrawl", "numResults", "contextMaxCharacters"],
        description="通用网页搜索与内容抓取",
    ),
    "get_code_context_exa": ToolSpec(
        name="get_code_context_exa",
        required=["query"],
        optional=["tokensNum"],
        description="获取编程相关的上下文信息",
    ),
}


def load_tool_spec(name: str) -> ToolSpec | None:
    """根据名称读取硬编码工具定义。"""

    return TOOL_SPECS.get(name)


def ensure_required(spec: ToolSpec | None, params: dict[str, Any]) -> None:
    """校验必填参数是否齐全。"""

    if not spec:
        return
    missing = [key for key in spec.required if key not in params]
    if missing:
        raise McpError(f"缺少必填参数: {', '.join(missing)}")


def build_tool_call_params(tool: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """构造 MCP tools/call 的 params 结构。"""

    return {"name": tool, "arguments": arguments}


def build_request(method: str, params: dict[str, Any]) -> McpRequest:
    """构造 MCP JSON-RPC 请求对象。"""

    return McpRequest(id=str(uuid.uuid4()), method=method, params=params)


def resolve_token(cli_token: str | None) -> str | None:
    """解析认证令牌来源。"""

    return cli_token or os.getenv("EXA_API_KEY") or os.getenv("EXA_MCP_TOKEN")


def post_jsonrpc(
    endpoint: str,
    token: str | None,
    request: McpRequest,
    timeout: float,
) -> tuple[dict[str, Any], float]:
    """发送 MCP JSON-RPC 请求并返回响应。"""

    start = time.perf_counter()
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    with httpx.Client(timeout=timeout) as client:
        response = client.post(endpoint, json=request.model_dump(), headers=headers)
    payload = parse_response_payload(response)
    if response.is_error:
        message = payload.get("error") if isinstance(payload, dict) else payload
        raise McpError(f"HTTP {response.status_code}: {message}")
    elapsed_ms = (time.perf_counter() - start) * 1000
    return payload, elapsed_ms


def parse_response_payload(response: httpx.Response) -> dict[str, Any]:
    """解析 JSON 或 SSE 响应内容。"""

    content_type = response.headers.get("Content-Type", "")
    if "text/event-stream" in content_type:
        return parse_sse_payload(response.text)
    try:
        return response.json()
    except json.JSONDecodeError as exc:
        raise McpError("响应不是合法 JSON") from exc


def parse_sse_payload(body: str) -> dict[str, Any]:
    """解析 SSE data 事件中的 JSON。"""

    data_lines: list[str] = []
    for line in body.splitlines():
        if line.startswith("data:"):
            data_lines.append(line.removeprefix("data:").strip())
    if not data_lines:
        raise McpError("SSE 响应中未找到 data 事件")
    data = "\n".join(data_lines)
    try:
        return json.loads(data)
    except json.JSONDecodeError as exc:
        raise McpError("SSE data 不是合法 JSON") from exc


def render_response(payload: dict[str, Any], as_json: bool) -> None:
    """格式化输出响应内容。"""

    if as_json:
        console.print_json(data=payload)
        return
    if "result" in payload:
        console.print(payload["result"])
        return
    console.print(payload)


def filter_none(values: dict[str, Any]) -> dict[str, Any]:
    """过滤值为 None 的参数。"""

    return {key: value for key, value in values.items() if value is not None}


def log_verbose(message: str, verbose: bool) -> None:
    """输出调试日志。"""

    if verbose:
        console.print(f"[cyan]debug[/cyan] {message}")


def cache_path() -> Path:
    """生成缓存文件路径。"""

    base = Path(os.getenv("XDG_CACHE_HOME", Path.home() / ".cache"))
    return base / "exa-cli" / "cache.json"


def load_cache(ttl_seconds: int) -> CacheData | None:
    """读取并校验缓存数据。"""

    path = cache_path()
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        cache = CacheData.model_validate(payload)
    except (OSError, json.JSONDecodeError, ValidationError):
        return None
    now = time.time()
    if cache.expires_at < now or ttl_seconds <= 0:
        return None
    return cache


def save_cache(initialize_result: dict[str, Any] | None, tools_list: dict[str, Any] | None, ttl_seconds: int) -> None:
    """保存缓存数据到本地文件。"""

    if ttl_seconds <= 0:
        return
    now = time.time()
    cache = CacheData(
        created_at=now,
        expires_at=now + ttl_seconds,
        initialize_result=initialize_result,
        tools_list=tools_list,
    )
    path = cache_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(cache.model_dump_json(indent=2), encoding="utf-8")


def initialize_session(
    endpoint: str,
    token: str | None,
    timeout: float,
    verbose: bool,
) -> tuple[dict[str, Any], float]:
    """执行 MCP initialize 请求。"""

    params = {
        "protocolVersion": PROTOCOL_VERSION,
        "capabilities": {},
        "clientInfo": CLIENT_INFO,
    }
    request = build_request("initialize", params)
    log_verbose("发送 initialize 请求", verbose)
    return post_jsonrpc(endpoint, token, request, timeout)


def list_tools(
    endpoint: str,
    token: str | None,
    timeout: float,
    verbose: bool,
) -> tuple[dict[str, Any], float]:
    """执行 MCP tools/list 请求。"""

    request = build_request("tools/list", {})
    log_verbose("发送 tools/list 请求", verbose)
    return post_jsonrpc(endpoint, token, request, timeout)


def call_mcp_tool(
    tool: str,
    arguments: dict[str, Any],
    endpoint: str,
    token: str | None,
    timeout: float,
    as_json: bool,
    cache_ttl: int,
    use_cache: bool,
    verbose: bool,
    method: str = "tools/call",
) -> None:
    """调用 MCP 工具并渲染输出。"""

    cached = load_cache(cache_ttl) if use_cache else None
    if cached is None:
        log_verbose("缓存未命中，开始初始化会话", verbose)
        init_result, init_ms = initialize_session(endpoint, token, timeout, verbose)
        log_verbose(f"initialize 完成，耗时 {init_ms:.1f} ms", verbose)
        tools_result, tools_ms = list_tools(endpoint, token, timeout, verbose)
        log_verbose(f"tools/list 完成，耗时 {tools_ms:.1f} ms", verbose)
        save_cache(init_result, tools_result, cache_ttl)
    else:
        log_verbose("缓存命中，跳过 initialize/tools/list", verbose)
    spec = load_tool_spec(tool)
    ensure_required(spec, arguments)
    request_params = build_tool_call_params(tool, arguments)
    request = build_request(method, request_params)
    payload, call_ms = post_jsonrpc(endpoint, resolve_token(token), request, timeout)
    log_verbose(f"{method} 完成，耗时 {call_ms:.1f} ms", verbose)
    render_response(payload, as_json)


@app.command("web-search-exa")
def web_search_exa(
    query: str = typer.Argument(..., help="搜索查询语句"),
    search_type: str | None = typer.Option(None, "--type", help="搜索类型：auto/fast/deep"),
    livecrawl: str | None = typer.Option(None, "--livecrawl", help="抓取模式：fallback/preferred"),
    num_results: int | None = typer.Option(None, "--num-results", help="返回结果数量"),
    context_max_characters: int | None = typer.Option(
        None,
        "--context-max-characters",
        help="返回上下文的最大字符数",
    ),
    endpoint: str = typer.Option(DEFAULT_ENDPOINT, "--endpoint", help="服务地址"),
    token: str | None = typer.Option(None, "--token", help="认证令牌，默认读取环境变量"),
    timeout: float = typer.Option(30.0, "--timeout", help="请求超时秒数"),
    cache_ttl: int = typer.Option(CACHE_TTL_SECONDS, "--cache-ttl", help="缓存有效期（秒）"),
    no_cache: bool = typer.Option(False, "--no-cache", help="禁用本地缓存"),
    as_json: bool = typer.Option(False, "--json", help="以 JSON 输出完整响应"),
    verbose: bool = typer.Option(False, "--verbose", help="输出调试日志"),
) -> None:
    """实时网页搜索并返回结果与正文片段。"""

    try:
        arguments = filter_none(
            {
                "query": query,
                "type": search_type,
                "livecrawl": livecrawl,
                "numResults": num_results,
                "contextMaxCharacters": context_max_characters,
            }
        )
        call_mcp_tool(
            tool="web_search_exa",
            arguments=arguments,
            endpoint=endpoint,
            token=token,
            timeout=timeout,
            cache_ttl=cache_ttl,
            use_cache=not no_cache,
            as_json=as_json,
            verbose=verbose,
        )
    except (McpError, ValidationError, json.JSONDecodeError) as exc:
        console.print(f"[red]错误:[/red] {exc}")
        sys.exit(1)


@app.command("get-code-context-exa")
def get_code_context_exa(
    query: str = typer.Argument(..., help="上下文检索查询"),
    tokens_num: int | None = typer.Option(None, "--tokens-num", help="返回的 token 数量"),
    endpoint: str = typer.Option(DEFAULT_ENDPOINT, "--endpoint", help="服务地址"),
    token: str | None = typer.Option(None, "--token", help="认证令牌，默认读取环境变量"),
    timeout: float = typer.Option(30.0, "--timeout", help="请求超时秒数"),
    cache_ttl: int = typer.Option(CACHE_TTL_SECONDS, "--cache-ttl", help="缓存有效期（秒）"),
    no_cache: bool = typer.Option(False, "--no-cache", help="禁用本地缓存"),
    as_json: bool = typer.Option(False, "--json", help="以 JSON 输出完整响应"),
    verbose: bool = typer.Option(False, "--verbose", help="输出调试日志"),
) -> None:
    """面向编程问题的检索，返回高质量上下文信息。"""

    try:
        arguments = filter_none({"query": query, "tokensNum": tokens_num})
        call_mcp_tool(
            tool="get_code_context_exa",
            arguments=arguments,
            endpoint=endpoint,
            token=token,
            timeout=timeout,
            cache_ttl=cache_ttl,
            use_cache=not no_cache,
            as_json=as_json,
            verbose=verbose,
        )
    except (McpError, ValidationError, json.JSONDecodeError) as exc:
        console.print(f"[red]错误:[/red] {exc}")
        sys.exit(1)


def main() -> None:
    """CLI 入口函数。"""

    app()


if __name__ == "__main__":
    main()
