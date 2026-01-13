# REST API Wrapper Example

## Overview
MCP server that wraps GitHub's REST API, demonstrating external API integration with proper error handling.

## Complete Implementation

```python
import aiohttp
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import asyncio

app = Server("github-api-server")

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="get_user",
            description="Fetch GitHub user profile information",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "GitHub username"
                    }
                },
                "required": ["username"]
            }
        ),
        Tool(
            name="list_repos",
            description="List user's public repositories",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "GitHub username"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of repos to return",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 100
                    }
                },
                "required": ["username"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    async with aiohttp.ClientSession() as session:
        if name == "get_user":
            return await handle_get_user(session, arguments)
        elif name == "list_repos":
            return await handle_list_repos(session, arguments)
        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}",
                isError=True
            )]

async def handle_get_user(session: aiohttp.ClientSession, arguments: dict):
    """Fetch user profile from GitHub API"""
    username = arguments["username"]
    url = f"https://api.github.com/users/{username}"

    try:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                result = f"""User: {data['name'] or data['login']}
Bio: {data['bio'] or 'No bio available'}
Public Repos: {data['public_repos']}
Followers: {data['followers']}
Following: {data['following']}
Location: {data['location'] or 'Not specified'}
Company: {data['company'] or 'Not specified'}
"""
                return [TextContent(type="text", text=result)]
            elif response.status == 404:
                return [TextContent(
                    type="text",
                    text=f"User '{username}' not found on GitHub",
                    isError=True
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"GitHub API error: HTTP {response.status}",
                    isError=True
                )]
    except aiohttp.ClientError as e:
        return [TextContent(
            type="text",
            text=f"Network error: {str(e)}",
            isError=True
        )]

async def handle_list_repos(session: aiohttp.ClientSession, arguments: dict):
    """List user's repositories"""
    username = arguments["username"]
    limit = arguments.get("limit", 10)
    url = f"https://api.github.com/users/{username}/repos?per_page={limit}&sort=updated"

    try:
        async with session.get(url) as response:
            if response.status == 200:
                repos = await response.json()

                if not repos:
                    return [TextContent(
                        type="text",
                        text=f"User '{username}' has no public repositories"
                    )]

                repo_list = [f"Repositories for {username}:\n"]
                for repo in repos:
                    repo_list.append(
                        f"• {repo['name']}: {repo['description'] or 'No description'}\n"
                        f"  Stars: {repo['stargazers_count']} | Forks: {repo['forks_count']} | "
                        f"Language: {repo['language'] or 'Unknown'}"
                    )

                return [TextContent(type="text", text="\n".join(repo_list))]
            elif response.status == 404:
                return [TextContent(
                    type="text",
                    text=f"User '{username}' not found on GitHub",
                    isError=True
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"GitHub API error: HTTP {response.status}",
                    isError=True
                )]
    except aiohttp.ClientError as e:
        return [TextContent(
            type="text",
            text=f"Network error: {str(e)}",
            isError=True
        )]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
```

## Usage Example

With Claude Desktop configured, you can ask:
```
"Show me the GitHub profile for octocat"
"List the top 5 repositories for torvalds"
```

## Key Patterns
- **Session Management**: Reuse aiohttp session across requests
- **Error Handling**: Handle different HTTP status codes appropriately
- **Response Formatting**: Present API data in readable format
- **Rate Limiting Consideration**: GitHub API has rate limits (consider adding caching)
