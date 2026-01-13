#!/usr/bin/env python3
"""Jira API Helper Script

Makes authenticated requests to Jira Cloud REST API v3.

Usage:
    python jira_api.py <method> <endpoint> [--data JSON] [--query PARAMS]

Examples:
    # Get an issue
    python jira_api.py GET /issue/PROJ-123

    # Search with JQL
    python jira_api.py GET /search --query "jql=project=AOP&maxResults=10"

    # Create an issue
    python jira_api.py POST /issue --data '{"fields":{"project":{"key":"AOP"},...}}'

    # Add a comment
    python jira_api.py POST /issue/PROJ-123/comment --data '{"body":{"type":"doc",...}}'

    # Transition an issue
    python jira_api.py POST /issue/PROJ-123/transitions --data '{"transition":{"id":"21"}}'

Environment variables (or .env file):
    JIRA_DOMAIN - Your Jira domain (e.g., company.atlassian.net)
    JIRA_EMAIL - Your Jira account email
    JIRA_API_TOKEN - Your Jira API token
"""

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


def load_env():
    """Load environment variables from .env file if present."""
    env_file = Path.cwd() / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    value = value.strip().strip('"').strip("'")
                    if key not in os.environ:
                        os.environ[key] = value


def get_auth_header():
    """Get Basic Auth header from environment."""
    email = os.environ.get("JIRA_EMAIL")
    token = os.environ.get("JIRA_API_TOKEN")

    if not email or not token:
        print(
            "Error: JIRA_EMAIL and JIRA_API_TOKEN environment variables required", file=sys.stderr
        )
        sys.exit(1)

    credentials = f"{email}:{token}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded}"


def get_base_url():
    """Get Jira base URL from environment."""
    domain = os.environ.get("JIRA_DOMAIN")
    if not domain:
        print("Error: JIRA_DOMAIN environment variable required", file=sys.stderr)
        sys.exit(1)

    if not domain.startswith("http"):
        domain = f"https://{domain}"

    return f"{domain}/rest/api/3"


def make_request(method, endpoint, data=None, query=None):
    """Make an authenticated request to Jira API."""
    base_url = get_base_url()
    url = f"{base_url}{endpoint}"

    if query:
        url = f"{url}?{query}"

    headers = {
        "Authorization": get_auth_header(),
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    body = None
    if data:
        if isinstance(data, str):
            body = data.encode()
        else:
            body = json.dumps(data).encode()

    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 204:
                return {"status": "success", "code": 204}

            content = response.read().decode()
            if content:
                return json.loads(content)
            return {"status": "success", "code": response.status}

    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        try:
            error_json = json.loads(error_body)
            print(json.dumps(error_json, indent=2), file=sys.stderr)
        except json.JSONDecodeError:
            print(f"Error {e.code}: {error_body}", file=sys.stderr)
        sys.exit(1)

    except urllib.error.URLError as e:
        print(f"Connection error: {e.reason}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Jira API Helper")
    parser.add_argument("method", choices=["GET", "POST", "PUT", "DELETE"], help="HTTP method")
    parser.add_argument("endpoint", help="API endpoint (e.g., /issue/PROJ-123)")
    parser.add_argument("--data", "-d", help="JSON data for POST/PUT requests")
    parser.add_argument("--query", "-q", help="Query parameters (e.g., 'jql=project=AOP')")

    args = parser.parse_args()

    load_env()

    data = None
    if args.data:
        try:
            data = json.loads(args.data)
        except json.JSONDecodeError:
            print("Error: Invalid JSON data", file=sys.stderr)
            sys.exit(1)

    result = make_request(args.method, args.endpoint, data, args.query)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
