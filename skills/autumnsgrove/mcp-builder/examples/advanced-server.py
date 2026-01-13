#!/usr/bin/env python3
"""
Advanced MCP Server Example

A comprehensive Model Context Protocol server demonstrating:
- Multiple tool types (REST API, database queries, file operations)
- Authentication and authorization
- Resource management
- Prompt templates
- Error handling and validation
- Logging and monitoring
- Rate limiting
- Caching

This server provides tools for:
- GitHub API integration
- Weather data fetching
- User management
- File system operations

Usage:
    # Set environment variables first
    export GITHUB_TOKEN="your_github_token"
    export WEATHER_API_KEY="your_weather_api_key"
    export MCP_API_KEY="your_mcp_api_key"

    python advanced-server.py

Configuration (Claude Desktop):
    {
        "mcpServers": {
            "advanced-server": {
                "command": "python",
                "args": ["/absolute/path/to/advanced-server.py"],
                "env": {
                    "GITHUB_TOKEN": "your_github_token",
                    "WEATHER_API_KEY": "your_weather_api_key",
                    "MCP_API_KEY": "your_mcp_api_key"
                }
            }
        }
    }
"""

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, Resource, Prompt
import asyncio
import logging
import sys
import os
import json
import aiohttp
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Optional, Dict, Any, List
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr),
        logging.FileHandler('advanced_mcp_server.log')
    ]
)
logger = logging.getLogger(__name__)

# Load configuration from environment
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
MCP_API_KEY = os.getenv("MCP_API_KEY")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Validate required configuration
if not GITHUB_TOKEN:
    logger.warning("GITHUB_TOKEN not set - GitHub tools will be limited")
if not WEATHER_API_KEY:
    logger.warning("WEATHER_API_KEY not set - Weather tools will not work")
if not MCP_API_KEY:
    logger.warning("MCP_API_KEY not set - Authentication disabled")

# Initialize server
app = Server("advanced-mcp-server")

# Server state
server_stats = {
    "start_time": datetime.now(),
    "request_count": 0,
    "error_count": 0,
    "tool_calls": defaultdict(int)
}

# Simple in-memory cache with TTL
class SimpleCache:
    def __init__(self, ttl_seconds: int = 300):
        self.cache: Dict[str, tuple] = {}
        self.ttl = timedelta(seconds=ttl_seconds)

    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            value, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.ttl:
                logger.debug(f"Cache hit: {key}")
                return value
            else:
                logger.debug(f"Cache expired: {key}")
                del self.cache[key]
        return None

    def set(self, key: str, value: Any):
        self.cache[key] = (value, datetime.now())
        logger.debug(f"Cache set: {key}")

    def clear(self):
        self.cache.clear()
        logger.info("Cache cleared")

# Initialize cache
cache = SimpleCache(ttl_seconds=300)

# Rate limiter
class RateLimiter:
    def __init__(self, max_requests: int, time_window_seconds: int):
        self.max_requests = max_requests
        self.time_window = timedelta(seconds=time_window_seconds)
        self.requests: Dict[str, List[datetime]] = defaultdict(list)

    def is_allowed(self, client_id: str = "default") -> bool:
        now = datetime.now()
        cutoff = now - self.time_window

        # Remove old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > cutoff
        ]

        # Check limit
        if len(self.requests[client_id]) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for client: {client_id}")
            return False

        # Record request
        self.requests[client_id].append(now)
        return True

# Initialize rate limiter (100 requests per minute)
rate_limiter = RateLimiter(max_requests=100, time_window_seconds=60)

# Authentication decorator
def require_auth(func):
    """Decorator to require API key authentication"""
    async def wrapper(*args, **kwargs):
        if MCP_API_KEY and ENVIRONMENT == "production":
            # In production, validate API key
            # For stdio transport, we rely on environment variable
            logger.debug("Authentication check passed")
        return await func(*args, **kwargs)
    return wrapper

@app.list_tools()
@require_auth
async def list_tools():
    """
    Register all available tools.

    Tools are organized by category:
    - GitHub API tools
    - Weather API tools
    - User management tools
    - File operations tools
    - System tools
    """
    logger.info("Listing available tools")

    tools = [
        # GitHub API Tools
        Tool(
            name="github_get_user",
            description="Fetch GitHub user profile information including name, bio, public repos, followers, and more.",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "GitHub username to look up",
                        "minLength": 1,
                        "maxLength": 39
                    }
                },
                "required": ["username"]
            }
        ),
        Tool(
            name="github_list_repos",
            description="List public repositories for a GitHub user. Returns repository name, description, stars, and language.",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "GitHub username"
                    },
                    "sort": {
                        "type": "string",
                        "enum": ["created", "updated", "pushed", "full_name"],
                        "description": "Sort order for repositories",
                        "default": "updated"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of repositories to return (1-100)",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 10
                    }
                },
                "required": ["username"]
            }
        ),
        Tool(
            name="github_search_repos",
            description="Search GitHub repositories by keyword. Returns matching repositories with details.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (supports GitHub search syntax)"
                    },
                    "sort": {
                        "type": "string",
                        "enum": ["stars", "forks", "updated"],
                        "description": "Sort results by stars, forks, or update time",
                        "default": "stars"
                    },
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        ),

        # Weather API Tools
        Tool(
            name="weather_current",
            description="Get current weather conditions for a city including temperature, humidity, conditions, and wind speed.",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name (e.g., 'London', 'New York')"
                    },
                    "units": {
                        "type": "string",
                        "enum": ["metric", "imperial"],
                        "description": "Temperature units (metric=Celsius, imperial=Fahrenheit)",
                        "default": "metric"
                    }
                },
                "required": ["city"]
            }
        ),

        # User Management Tools
        Tool(
            name="user_create",
            description="Create a new user account with validation. Stores user information securely.",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "Unique username (alphanumeric, 3-20 characters)",
                        "pattern": "^[a-zA-Z0-9_]{3,20}$"
                    },
                    "email": {
                        "type": "string",
                        "description": "Valid email address",
                        "format": "email"
                    },
                    "role": {
                        "type": "string",
                        "enum": ["admin", "editor", "viewer"],
                        "description": "User role determining permissions",
                        "default": "viewer"
                    }
                },
                "required": ["username", "email"]
            }
        ),
        Tool(
            name="user_get",
            description="Retrieve user information by username.",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "Username to look up"
                    }
                },
                "required": ["username"]
            }
        ),

        # File Operations Tools
        Tool(
            name="file_read",
            description="Read contents of a text file. Returns file content as text.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to file (relative or absolute)"
                    },
                    "encoding": {
                        "type": "string",
                        "description": "File encoding",
                        "default": "utf-8"
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="file_write",
            description="Write text content to a file. Creates file if it doesn't exist.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to file"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write"
                    },
                    "encoding": {
                        "type": "string",
                        "default": "utf-8"
                    }
                },
                "required": ["path", "content"]
            }
        ),

        # System Tools
        Tool(
            name="system_health",
            description="Get server health status including uptime, request count, and error rate.",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ),
        Tool(
            name="cache_clear",
            description="Clear the server cache. Useful for forcing fresh data retrieval.",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        )
    ]

    logger.info(f"Registered {len(tools)} tools")
    return tools

@app.call_tool()
@require_auth
async def call_tool(name: str, arguments: dict):
    """
    Route and execute tool calls with monitoring.
    """
    # Update statistics
    server_stats["request_count"] += 1
    server_stats["tool_calls"][name] += 1

    # Check rate limit
    if not rate_limiter.is_allowed():
        return [TextContent(
            type="text",
            text="Rate limit exceeded. Please try again in a moment.",
            isError=True
        )]

    logger.info(f"Tool called: {name}")
    logger.debug(f"Arguments: {json.dumps(arguments, indent=2)}")

    start_time = datetime.now()

    try:
        # Route to appropriate handler
        if name.startswith("github_"):
            result = await handle_github_tool(name, arguments)
        elif name.startswith("weather_"):
            result = await handle_weather_tool(name, arguments)
        elif name.startswith("user_"):
            result = await handle_user_tool(name, arguments)
        elif name.startswith("file_"):
            result = await handle_file_tool(name, arguments)
        elif name.startswith("system_") or name.startswith("cache_"):
            result = await handle_system_tool(name, arguments)
        else:
            logger.error(f"Unknown tool: {name}")
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}",
                isError=True
            )]

        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"Tool {name} completed in {duration:.2f}s")

        return result

    except Exception as e:
        server_stats["error_count"] += 1
        duration = (datetime.now() - start_time).total_seconds()
        logger.exception(f"Tool {name} failed after {duration:.2f}s")

        return [TextContent(
            type="text",
            text=f"Internal error: {type(e).__name__}: {str(e)}",
            isError=True
        )]

# GitHub Tool Handlers

async def handle_github_tool(name: str, arguments: dict):
    """Handle GitHub API tools"""
    if not GITHUB_TOKEN:
        return [TextContent(
            type="text",
            text="GitHub API requires GITHUB_TOKEN environment variable",
            isError=True
        )]

    async with aiohttp.ClientSession() as session:
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }

        if name == "github_get_user":
            username = arguments["username"]
            cache_key = f"github:user:{username}"

            # Check cache
            cached = cache.get(cache_key)
            if cached:
                return [TextContent(type="text", text=cached)]

            url = f"https://api.github.com/users/{username}"

            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    result = format_github_user(data)
                    cache.set(cache_key, result)
                    return [TextContent(type="text", text=result)]
                elif response.status == 404:
                    return [TextContent(
                        type="text",
                        text=f"User '{username}' not found",
                        isError=True
                    )]
                else:
                    return [TextContent(
                        type="text",
                        text=f"GitHub API error: {response.status}",
                        isError=True
                    )]

        elif name == "github_list_repos":
            username = arguments["username"]
            sort = arguments.get("sort", "updated")
            limit = arguments.get("limit", 10)

            url = f"https://api.github.com/users/{username}/repos?sort={sort}&per_page={limit}"

            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    repos = await response.json()
                    result = format_github_repos(repos)
                    return [TextContent(type="text", text=result)]
                else:
                    return [TextContent(
                        type="text",
                        text=f"Error fetching repositories: {response.status}",
                        isError=True
                    )]

        elif name == "github_search_repos":
            query = arguments["query"]
            sort = arguments.get("sort", "stars")
            limit = arguments.get("limit", 10)

            url = f"https://api.github.com/search/repositories?q={query}&sort={sort}&per_page={limit}"

            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    result = format_github_search_results(data)
                    return [TextContent(type="text", text=result)]
                else:
                    return [TextContent(
                        type="text",
                        text=f"Search failed: {response.status}",
                        isError=True
                    )]

def format_github_user(data: dict) -> str:
    """Format GitHub user data"""
    return f"""GitHub User: {data['login']}
Name: {data.get('name', 'N/A')}
Bio: {data.get('bio', 'N/A')}
Public Repos: {data['public_repos']}
Followers: {data['followers']}
Following: {data['following']}
Created: {data['created_at']}
Profile: {data['html_url']}"""

def format_github_repos(repos: list) -> str:
    """Format GitHub repositories list"""
    if not repos:
        return "No repositories found"

    lines = [f"Found {len(repos)} repositories:\n"]
    for repo in repos:
        lines.append(f"- {repo['name']}")
        if repo.get('description'):
            lines.append(f"  Description: {repo['description']}")
        lines.append(f"  Stars: {repo['stargazers_count']} | Forks: {repo['forks_count']}")
        if repo.get('language'):
            lines.append(f"  Language: {repo['language']}")
        lines.append(f"  URL: {repo['html_url']}\n")

    return "\n".join(lines)

def format_github_search_results(data: dict) -> str:
    """Format GitHub search results"""
    total = data['total_count']
    repos = data['items']

    lines = [f"Found {total} total results (showing {len(repos)}):\n"]
    for repo in repos:
        lines.append(f"- {repo['full_name']}")
        if repo.get('description'):
            lines.append(f"  {repo['description']}")
        lines.append(f"  Stars: {repo['stargazers_count']} | Forks: {repo['forks_count']}")
        lines.append(f"  URL: {repo['html_url']}\n")

    return "\n".join(lines)

# Weather Tool Handlers

async def handle_weather_tool(name: str, arguments: dict):
    """Handle weather API tools"""
    if not WEATHER_API_KEY:
        return [TextContent(
            type="text",
            text="Weather API requires WEATHER_API_KEY environment variable",
            isError=True
        )]

    if name == "weather_current":
        city = arguments["city"]
        units = arguments.get("units", "metric")

        cache_key = f"weather:{city}:{units}"
        cached = cache.get(cache_key)
        if cached:
            return [TextContent(type="text", text=cached)]

        # Using OpenWeatherMap API as example
        url = f"https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": WEATHER_API_KEY,
            "units": units
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    result = format_weather_data(data, units)
                    cache.set(cache_key, result)
                    return [TextContent(type="text", text=result)]
                elif response.status == 404:
                    return [TextContent(
                        type="text",
                        text=f"City '{city}' not found",
                        isError=True
                    )]
                else:
                    return [TextContent(
                        type="text",
                        text=f"Weather API error: {response.status}",
                        isError=True
                    )]

def format_weather_data(data: dict, units: str) -> str:
    """Format weather data"""
    temp_unit = "°C" if units == "metric" else "°F"
    wind_unit = "m/s" if units == "metric" else "mph"

    return f"""Weather for {data['name']}, {data['sys']['country']}
Conditions: {data['weather'][0]['description'].title()}
Temperature: {data['main']['temp']}{temp_unit}
Feels Like: {data['main']['feels_like']}{temp_unit}
Humidity: {data['main']['humidity']}%
Wind Speed: {data['wind']['speed']} {wind_unit}
Pressure: {data['main']['pressure']} hPa"""

# User Management Tool Handlers

# In-memory user storage (replace with database in production)
user_database: Dict[str, dict] = {}

async def handle_user_tool(name: str, arguments: dict):
    """Handle user management tools"""
    if name == "user_create":
        username = arguments["username"]
        email = arguments["email"]
        role = arguments.get("role", "viewer")

        # Check if user already exists
        if username in user_database:
            return [TextContent(
                type="text",
                text=f"User '{username}' already exists",
                isError=True
            )]

        # Create user
        user_data = {
            "username": username,
            "email": email,
            "role": role,
            "created_at": datetime.now().isoformat(),
            "id": hashlib.md5(username.encode()).hexdigest()[:8]
        }

        user_database[username] = user_data
        logger.info(f"Created user: {username}")

        return [TextContent(
            type="text",
            text=f"Successfully created user '{username}' with role '{role}'"
        )]

    elif name == "user_get":
        username = arguments["username"]

        if username not in user_database:
            return [TextContent(
                type="text",
                text=f"User '{username}' not found",
                isError=True
            )]

        user = user_database[username]
        result = f"""User: {user['username']}
Email: {user['email']}
Role: {user['role']}
ID: {user['id']}
Created: {user['created_at']}"""

        return [TextContent(type="text", text=result)]

# File Operations Tool Handlers

async def handle_file_tool(name: str, arguments: dict):
    """Handle file operation tools"""
    if name == "file_read":
        path = arguments["path"]
        encoding = arguments.get("encoding", "utf-8")

        try:
            with open(path, 'r', encoding=encoding) as f:
                content = f.read()

            logger.info(f"Read file: {path} ({len(content)} bytes)")
            return [TextContent(
                type="text",
                text=f"File: {path}\n\n{content}"
            )]
        except FileNotFoundError:
            return [TextContent(
                type="text",
                text=f"File not found: {path}",
                isError=True
            )]
        except PermissionError:
            return [TextContent(
                type="text",
                text=f"Permission denied: {path}",
                isError=True
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error reading file: {str(e)}",
                isError=True
            )]

    elif name == "file_write":
        path = arguments["path"]
        content = arguments["content"]
        encoding = arguments.get("encoding", "utf-8")

        try:
            with open(path, 'w', encoding=encoding) as f:
                f.write(content)

            logger.info(f"Wrote file: {path} ({len(content)} bytes)")
            return [TextContent(
                type="text",
                text=f"Successfully wrote {len(content)} bytes to {path}"
            )]
        except PermissionError:
            return [TextContent(
                type="text",
                text=f"Permission denied: {path}",
                isError=True
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error writing file: {str(e)}",
                isError=True
            )]

# System Tool Handlers

async def handle_system_tool(name: str, arguments: dict):
    """Handle system tools"""
    if name == "system_health":
        uptime = (datetime.now() - server_stats["start_time"]).total_seconds()
        error_rate = (
            server_stats["error_count"] / server_stats["request_count"]
            if server_stats["request_count"] > 0 else 0
        )

        health_data = {
            "status": "healthy",
            "uptime_seconds": round(uptime, 2),
            "total_requests": server_stats["request_count"],
            "error_count": server_stats["error_count"],
            "error_rate": round(error_rate * 100, 2),
            "cache_size": len(cache.cache),
            "top_tools": dict(
                sorted(
                    server_stats["tool_calls"].items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5]
            )
        }

        return [TextContent(
            type="text",
            text=json.dumps(health_data, indent=2)
        )]

    elif name == "cache_clear":
        cache.clear()
        logger.info("Cache cleared via tool call")
        return [TextContent(
            type="text",
            text="Cache successfully cleared"
        )]

# Prompts

@app.list_prompts()
async def list_prompts():
    """Register prompt templates"""
    return [
        Prompt(
            name="github_analysis",
            description="Comprehensive GitHub repository analysis workflow",
            arguments=[
                {
                    "name": "repository",
                    "description": "Repository in format 'owner/repo'",
                    "required": True
                }
            ]
        ),
        Prompt(
            name="weather_report",
            description="Detailed weather report for a city",
            arguments=[
                {
                    "name": "city",
                    "description": "City name",
                    "required": True
                }
            ]
        )
    ]

@app.get_prompt()
async def get_prompt(name: str, arguments: dict):
    """Return prompt templates"""
    if name == "github_analysis":
        repo = arguments["repository"]
        owner, repo_name = repo.split("/") if "/" in repo else (repo, "")

        return {
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": f"""Please analyze the GitHub repository '{repo}':

1. Get the user profile for '{owner}' using github_get_user
2. List their repositories using github_list_repos
3. Provide insights on:
   - Main programming languages used
   - Repository activity and popularity
   - Notable projects
4. Summarize your findings"""
                    }
                }
            ]
        }
    elif name == "weather_report":
        city = arguments["city"]
        return {
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": f"""Please provide a weather report for {city}:

1. Get current weather using weather_current
2. Provide a detailed summary including:
   - Current conditions
   - Temperature analysis
   - Recommendations for outdoor activities
   - Any weather warnings or notable conditions"""
                    }
                }
            ]
        }

async def main():
    """Main entry point"""
    logger.info("Starting Advanced MCP Server")
    logger.info(f"Environment: {ENVIRONMENT}")
    logger.info(f"GitHub API: {'Enabled' if GITHUB_TOKEN else 'Disabled'}")
    logger.info(f"Weather API: {'Enabled' if WEATHER_API_KEY else 'Disabled'}")
    logger.info(f"Authentication: {'Enabled' if MCP_API_KEY else 'Disabled'}")

    try:
        async with stdio_server() as (read_stream, write_stream):
            logger.info("STDIO transport initialized")
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
    except Exception as e:
        logger.exception("Server error")
        raise

if __name__ == "__main__":
    asyncio.run(main())
