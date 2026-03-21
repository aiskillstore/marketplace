#!/usr/bin/env python3
"""
Skywork authentication module for skywork skills.

Provides token acquisition and validation.
Token is stored in user home directory as ~/.skywork_token (JSON format).

Main interface:
    get_skywork_token(interactive=True) -> str  # Returns valid token, auto-login if needed

Usage in interactive environment (command line):
    token = get_skywork_token(interactive=True)  # Will open browser and print URL

Usage in non-interactive environment (OpenClaw, skills platform):
    try:
        token = get_skywork_token(interactive=False)  # Will raise exception if login needed
    except LoginRequiredException as e:
        # Platform can display this URL to user
        return f"Please log in at: {e.login_url}"
"""

import json
import os
import time
import subprocess
import platform
import sys
from urllib import request, error
from typing import Optional, Dict, Any


# Custom exception for non-interactive login requirement
class LoginRequiredException(Exception):
    """Raised when login is required in non-interactive mode."""
    def __init__(self, login_url: str, message: str = None):
        self.login_url = login_url
        self.message = message or f"Login required. Please visit: {login_url}"
        super().__init__(self.message)

# Configuration (override via env; defaults are production)
API_BASE = os.environ.get("SKYWORK_API_BASE", "https://api.skywork.ai")
LOGIN_BASE_URL = os.environ.get("SKYWORK_WEB_BASE", "https://skywork.ai")
# Store token in user home directory (global location, shared by all skills)
TOKEN_FILE = os.path.expanduser("~/.skywork_token")
CLIENT_PREFIX = "skywork-skills-search"
CLIENT_ID = "10000"
POLL_INTERVAL = 0.5  # seconds
POLL_TIMEOUT = 300   # seconds (5 minutes)


def _get_login_key() -> str:
    """Get login key from server."""
    url = f"{API_BASE}/usercenter/key"
    data = json.dumps({"prefix": CLIENT_PREFIX}).encode("utf-8")
    req = request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with request.urlopen(req, timeout=20) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            if result.get("code") == 0:
                return result["data"]["key"]
            else:
                raise Exception(f"Failed to get login key: {result.get('message', 'Unknown error')}")
    except error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        raise Exception(f"HTTP error {e.code}: {error_body}")
    except error.URLError as e:
        raise Exception(f"Network error: {e.reason}")


def _open_browser(key: str):
    """Open browser for user login (non-blocking)."""
    url = f"{LOGIN_BASE_URL}/?from={CLIENT_PREFIX}&sk_id={key}"

    print(f"[LOGIN_URL] {url}", flush=True)
    print(f"Please log in via browser: {url}", flush=True)
    print("If browser doesn't open, please visit the URL above.", flush=True)

    system = platform.system()
    try:
        if system == "Darwin":  # macOS
            subprocess.Popen(["open", url], start_new_session=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif system == "Windows":
            subprocess.Popen(["start", url], shell=True, start_new_session=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif system == "Linux":
            subprocess.Popen(["xdg-open", url], start_new_session=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            print("Unknown OS, please open the URL manually.", flush=True)
    except Exception as e:
        print(f"Warning: Failed to open browser: {e}", flush=True)
        print(f"Please manually visit: {url}", flush=True)


def _poll_for_token(key: str) -> Dict[str, str]:
    """Poll server until token is available."""
    url = f"{API_BASE}/usercenter/key/{key}"
    start_time = time.time()

    print("Waiting for login", end="", flush=True)

    while time.time() - start_time < POLL_TIMEOUT:
        req = request.Request(url, method="GET")
        try:
            with request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                if result.get("code") == 0:
                    data = result.get("data", {})
                    if data and "token_key" in data and "token" in data:
                        print()  # newline
                        return data
        except:
            pass  # Continue polling on any error

        time.sleep(POLL_INTERVAL)
        sys.stdout.write(".")
        sys.stdout.flush()

    print()  # newline
    raise TimeoutError(f"Login timeout after {POLL_TIMEOUT} seconds. Please try again.")


def _check_token(token: str) -> bool:
    """
    Validate token with Skywork API.
    Returns True if token is valid.
    """
    url = f"{API_BASE}/usercenter/inner/auth/token/check"
    data = json.dumps({"token": token}).encode("utf-8")
    req = request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "K-Client-Id": CLIENT_ID
        },
        method="POST"
    )

    try:
        with request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            # Check response structure: {code, msg, data: {uid, nick_name, ...}}
            if result.get("code") == 0 and result.get("data"):
                return True
            return False
    except:
        return False


def _load_token_from_file() -> Optional[Dict[str, Any]]:
    """Load token data from file."""
    if not os.path.exists(TOKEN_FILE):
        return None

    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None


def _save_token_to_file(token_data: Dict[str, Any]):
    """Save token data to file."""
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        json.dump(token_data, f, indent=2)


def _login() -> Dict[str, Any]:
    """
    Perform full login flow:
    1. Get login key
    2. Open browser
    3. Poll for token
    4. Save token to file
    Returns token data dict.
    """
    print("Starting Skywork login...", flush=True)

    # Step 1: Get login key
    key = _get_login_key()
    print(f"Login key: {key}", flush=True)

    # Step 2: Open browser
    _open_browser(key)

    # Step 3: Poll for token
    token_data = _poll_for_token(key)
    print("Token received!", flush=True)

    # Step 4: Save token
    _save_token_to_file(token_data)
    print(f"Token saved to {TOKEN_FILE}", flush=True)

    return token_data


def get_skywork_token() -> str:
    """
    Get valid Skywork token.

    Flow:
    1. Try to load token from file
    2. If exists and valid, return it
    3. If not exists or invalid, start login flow (open browser + poll)
    4. Return token

    Returns:
        str: Valid token string

    Raises:
        LoginRequiredException: If user needs to manually login (e.g., timeout)
        Exception: If network error or other failures
    """
    # Priority 1: Environment variable (from SkyClaw pod)
    env_token = os.environ.get("SKYBOT_TOKEN", "")
    if env_token:
        return env_token

    # Priority 2: Try to load from file
    token_data = _load_token_from_file()
    if token_data and "token" in token_data:
        token = token_data["token"]
        # Check if token is still valid
        if _check_token(token):
            return token

    # No token or token expired - perform login
    try:
        token_data = _login()
        return token_data["token"]
    except TimeoutError as e:
        # Login timeout - user needs to manually visit URL
        key = _get_login_key()
        login_url = f"{LOGIN_BASE_URL}/?from={CLIENT_PREFIX}&sk_id={key}"
        raise LoginRequiredException(
            login_url=login_url,
            message=f"Login timeout. Please visit: {login_url}"
        )
    except Exception as e:
        raise


# Command line interface for testing
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Skywork authentication for skywork skills")
    parser.add_argument("--check", action="store_true", help="Check current token validity")
    parser.add_argument("--login", action="store_true", help="Force new login")
    parser.add_argument("--show", action="store_true", help="Show token info (masked)")

    args = parser.parse_args()

    if args.check:
        token_data = _load_token_from_file()
        if token_data and "token" in token_data:
            if _check_token(token_data["token"]):
                print("Token is valid.", flush=True)
                sys.exit(0)
            else:
                print("Token is invalid.", flush=True)
                sys.exit(1)
        else:
            print("No token found.", flush=True)
            sys.exit(1)

    elif args.login:
        _login()

    elif args.show:
        token_data = _load_token_from_file()
        if token_data:
            masked = {k: (v[:8] + "..." if k == "token" else v) for k, v in token_data.items()}
            print(json.dumps(masked, indent=2))
        else:
            print("No token stored.", flush=True)

    else:
        # Default: authenticate (check env, check file, or login)
        try:
            env_token = os.environ.get("SKYBOT_TOKEN", "")
            if env_token and _check_token(env_token):
                print("Authentication successful (env token)", flush=True)
                sys.exit(0)

            token = get_skywork_token()
            print("Authentication successful", flush=True)
            sys.exit(0)
        except Exception as e:
            print(f"Authentication failed: {e}", file=sys.stderr, flush=True)
            sys.exit(1)
