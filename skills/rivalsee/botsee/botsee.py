#!/usr/bin/env python3
"""BotSee CLI — AI-powered competitive intelligence via BotSee API."""

import argparse
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

# Version
__version__ = "0.3.0"

# API Configuration
BASE_URL = os.environ.get("BOTSEE_BASE_URL", "https://botsee.io")

# File Paths
USER_CONFIG = Path.home() / ".botsee" / "config.json"
WORKSPACE_CONFIG = Path(".context") / "botsee-config.json"
PENDING_SIGNUP = Path.home() / ".botsee" / "pending_signup.json"

# Polling Configuration
POLL_INTERVAL = 3  # seconds
SIGNUP_POLL_TIMEOUT = 300  # 5 minutes
ANALYSIS_POLL_TIMEOUT = 600  # 10 minutes

# HTTP Status Codes
HTTP_OK = 200
HTTP_CREATED = 201
HTTP_ACCEPTED = 202
HTTP_NO_CONTENT = 204
HTTP_PAYMENT_REQUIRED = 402
HTTP_NOT_FOUND = 404
HTTP_GONE = 410

# Validation Ranges
TYPES_MIN, TYPES_MAX = 1, 3
PERSONAS_MIN, PERSONAS_MAX = 1, 3
QUESTIONS_MIN, QUESTIONS_MAX = 3, 10

# Display Truncation
DESC_TRUNCATE_LEN = 50
TEXT_TRUNCATE_LEN = 80

# USDC / x402
USDC_MIN_CENTS = 250
USDC_MAX_CENTS = 100000
PAYMENT_HEADER_REQUIRED = "payment-required"
PAYMENT_HEADER_REQUEST = "payment"
PAYMENT_HEADER_SIGNATURE = "payment-signature"
PAYMENT_HEADER_RESPONSE = "payment-response"


def extract_payment_headers(headers):
    """Extract x402-related headers from an HTTP headers object."""
    if not headers:
        return {}

    payment_headers = {}
    for key in (PAYMENT_HEADER_REQUIRED, PAYMENT_HEADER_RESPONSE):
        value = headers.get(key)
        if value:
            payment_headers[key] = value
    return payment_headers


def show_payment_headers(response_data):
    """Display x402 headers if present in API response payload."""
    payment_headers = response_data.get("_payment_headers") if isinstance(response_data, dict) else None
    if not payment_headers:
        return

    print("x402 payment headers:")
    if payment_headers.get(PAYMENT_HEADER_REQUIRED):
        print(f"  {PAYMENT_HEADER_REQUIRED}: {payment_headers[PAYMENT_HEADER_REQUIRED]}")
    if payment_headers.get(PAYMENT_HEADER_RESPONSE):
        print(f"  {PAYMENT_HEADER_RESPONSE}: {payment_headers[PAYMENT_HEADER_RESPONSE]}")


def show_payment_required_help(response_data):
    """Display a concise hint when an endpoint requires payment."""
    if not isinstance(response_data, dict):
        return

    if response_data.get("_payment_headers"):
        print("")
        show_payment_headers(response_data)

    print("")
    print("Payment required (HTTP 402).")
    print("Top up credits with USDC on Base:")
    print(f"  /botsee topup-usdc --amount-cents {USDC_MIN_CENTS} --from-address 0x...")


def api_call(method, endpoint, data=None, api_key=None, timeout=30, params=None, extra_headers=None):
    """Make an API call to BotSee. Returns (response_dict, http_status)."""
    url = f"{BASE_URL}/api/v1{endpoint}"
    if params:
        query = urllib.parse.urlencode(params)
        url = f"{url}?{query}"

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    if extra_headers:
        headers.update(extra_headers)

    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    # Create SSL context with certificate validation
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = True
    ssl_context.verify_mode = ssl.CERT_REQUIRED

    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ssl_context) as resp:
            raw = resp.read()
            response_data = json.loads(raw) if raw else {}
            payment_headers = extract_payment_headers(resp.headers)
            if payment_headers:
                response_data["_payment_headers"] = payment_headers
            return response_data, resp.status
    except urllib.error.HTTPError as e:
        raw = e.read()
        payment_headers = extract_payment_headers(e.headers)
        try:
            error_data = json.loads(raw)
            # Sanitize error messages - don't leak API keys
            if "api_key" in str(error_data).lower():
                error_data = {"error": "Authentication failed"}
            if payment_headers:
                error_data["_payment_headers"] = payment_headers
            return error_data, e.code
        except (json.JSONDecodeError, ValueError):
            error_data = {"error": "Request failed"}
            if payment_headers:
                error_data["_payment_headers"] = payment_headers
            return error_data, e.code
    except urllib.error.URLError as e:
        print(f"Connection error: {e.reason}", file=sys.stderr)
        sys.exit(1)


def load_user_config():
    """Load user config from ~/.botsee/config.json."""
    if not USER_CONFIG.exists():
        return None
    with open(USER_CONFIG) as f:
        return json.load(f)


def save_user_config(api_key, site_uuid, contact_email=None, company_name=None):
    """Save user config to ~/.botsee/config.json with secure permissions."""
    USER_CONFIG.parent.mkdir(parents=True, exist_ok=True)

    # Read existing config to preserve fields
    existing_config = {}
    if USER_CONFIG.exists():
        try:
            with open(USER_CONFIG) as f:
                existing_config = json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

    # Build new config, preserving existing values if new ones not provided
    config = {
        "api_key": api_key,
        "site_uuid": site_uuid,
        "contact_email": contact_email or existing_config.get("contact_email"),
        "company_name": company_name or existing_config.get("company_name")
    }

    # Set umask to ensure file is created with secure permissions (no race window)
    old_umask = os.umask(0o077)  # Only owner can read/write
    try:
        with open(USER_CONFIG, "w") as f:
            json.dump(config, f, indent=2)
    finally:
        os.umask(old_umask)  # Restore original umask
    os.chmod(USER_CONFIG.parent, 0o700)


def load_workspace_config():
    """Load workspace config from .context/botsee-config.json."""
    if not WORKSPACE_CONFIG.exists():
        return None
    with open(WORKSPACE_CONFIG) as f:
        return json.load(f)


def save_workspace_config(domain, types, personas, questions):
    """Save workspace config to .context/botsee-config.json."""
    WORKSPACE_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    with open(WORKSPACE_CONFIG, "w") as f:
        json.dump({
            "domain": domain,
            "types": types,
            "personas_per_type": personas,
            "questions_per_persona": questions,
        }, f, indent=2)


def normalize_domain(domain):
    """Ensure domain has https:// prefix."""
    if not domain.startswith(("http://", "https://")):
        domain = f"https://{domain}"
    return domain


def normalize_endpoint(endpoint):
    """Normalize endpoint paths to /<resource> without /api/v1 prefix."""
    if endpoint.startswith(BASE_URL):
        endpoint = endpoint[len(BASE_URL):]
    if endpoint.startswith("/api/v1/"):
        endpoint = endpoint[len("/api/v1"):]
    return endpoint


def parse_comma_separated(value):
    """Parse a comma-separated argument into a list."""
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def require_user_config():
    """Load user config or exit with error."""
    config = load_user_config()
    if not config:
        print("No BotSee config found. Run: /botsee signup", file=sys.stderr)
        sys.exit(1)
    return config


def load_pending_signup():
    """Load pending signup metadata."""
    if not PENDING_SIGNUP.exists():
        return None
    with open(PENDING_SIGNUP) as f:
        return json.load(f)


def save_pending_signup(data):
    """Persist pending signup metadata with secure permissions."""
    PENDING_SIGNUP.parent.mkdir(parents=True, exist_ok=True)
    with open(PENDING_SIGNUP, "w") as f:
        json.dump(data, f, indent=2)
    os.chmod(PENDING_SIGNUP, 0o600)


def clear_pending_signup():
    """Delete pending signup metadata."""
    if PENDING_SIGNUP.exists():
        PENDING_SIGNUP.unlink()


def resolve_signup_token(explicit_token=None):
    """Resolve signup token from explicit argument or pending signup state."""
    if explicit_token:
        return explicit_token

    pending = load_pending_signup()
    if not pending:
        print("No pending signup found. Run /botsee signup --crypto first.", file=sys.stderr)
        sys.exit(1)

    setup_token = pending.get("setup_token")
    if not setup_token:
        print("Pending signup has no setup token. Run /botsee signup again.", file=sys.stderr)
        sys.exit(1)
    return setup_token


def show_usdc_payment_instructions(resp):
    """Display x402 payment requirements returned by USDC endpoints."""
    # New x402 shape: accepts or payment_requirements array
    requirements = resp.get("accepts") or resp.get("payment_requirements") or []
    req = requirements[0] if requirements else {}

    amount_raw = req.get("amount", "?")
    # amount is in USDC micro-units (6 decimals); convert to readable
    try:
        amount_usdc = f"{int(amount_raw) / 1_000_000:.2f}"
    except (ValueError, TypeError):
        amount_usdc = amount_raw

    print("Payment required (HTTP 402).")
    print(f"   Network: {req.get('network', '?')}")
    print(f"   Amount:  {amount_usdc} USDC")
    print(f"   Send to: {req.get('payTo', '?')}")
    print(f"   Asset:   {req.get('asset', '?')}")

    expires_at = resp.get("expires_at")
    if expires_at:
        print(f"   Expires: {expires_at}")



# --- Generic CRUD helpers (reduces duplication) ---


def api_get(endpoint, expected_status=HTTP_OK):
    """Fetch from API and return response, exit on error."""
    config = require_user_config()
    resp, status = api_call("GET", endpoint, api_key=config["api_key"])
    if status != expected_status:
        print(f"Failed (HTTP {status}): {resp}", file=sys.stderr)
        if status == HTTP_PAYMENT_REQUIRED:
            show_payment_required_help(resp)
        sys.exit(1)
    return resp


def api_delete(endpoint, resource_name, expected_status=HTTP_NO_CONTENT):
    """Delete resource and print success message."""
    config = require_user_config()
    resp, status = api_call("DELETE", endpoint, api_key=config["api_key"])
    if status == expected_status:
        print(f"✅ {resource_name} archived")
    else:
        print(f"Failed (HTTP {status}): {resp}", file=sys.stderr)
        if status == HTTP_PAYMENT_REQUIRED:
            show_payment_required_help(resp)
        sys.exit(1)


# --- High-level workflow commands ---


def cmd_status(args):
    """Show account status and balance."""
    config = load_user_config()
    if not config:
        print("🤖 BotSee - AI Competitive Intelligence")
        print("")
        print("Get started: /botsee signup")
        print("Learn more: https://botsee.io/docs")
        return

    usage_params = {}
    if getattr(args, "limit", None):
        usage_params["limit"] = args.limit
    if getattr(args, "cursor", None):
        usage_params["cursor"] = args.cursor
    if getattr(args, "from_time", None):
        usage_params["from"] = args.from_time
    if getattr(args, "to_time", None):
        usage_params["to"] = args.to_time

    resp, status = api_call(
        "GET",
        "/usage",
        api_key=config["api_key"],
        params=usage_params or None,
    )
    if status != HTTP_OK:
        print(f"API error ({status}). Run: /botsee signup", file=sys.stderr)
        sys.exit(1)

    # Get active site details if available
    active_site = None
    site_uuid = config.get("site_uuid")
    if site_uuid:
        site_resp, site_status = api_call("GET", f"/sites/{site_uuid}", api_key=config["api_key"])
        if site_status == HTTP_OK:
            active_site = site_resp.get("site", {})

    # Show only last 4 characters of API key for security
    key_suffix = config["api_key"][-4:] if len(config["api_key"]) >= 4 else "****"

    print("🤖 BotSee")
    print("━━━━━━━━━━━━━━━")
    print(f"💰 Credits: {resp.get('balance', '?')}")
    if active_site:
        site_url = active_site.get("url", "?")
        site_name = active_site.get("product_name", "?")
        print(f"📍 Active: {site_name} ({site_url})")
    print(f"🔑 Key: ...{key_suffix}")
    print("")
    print("Commands:")
    print("  /botsee account               - View account details")
    print("  /botsee signup                - Signup with credit card")
    print("  /botsee signup-usdc           - Signup with USDC on Base")
    print("  /botsee topup-usdc            - Add credits with USDC")
    print("  /botsee create-site <domain>  - Create site")
    print("  /botsee analyze               - Analyze website")
    print("  /botsee content               - Generate blog post")


def cmd_usage_by_site(args):
    """Show credit usage grouped by site (totals + per-category breakdown)."""
    config = require_user_config()
    params = {}
    if getattr(args, "from_time", None):
        params["from"] = args.from_time
    if getattr(args, "to_time", None):
        params["to"] = args.to_time
    if getattr(args, "site_uuid", None):
        params["site_uuid"] = args.site_uuid

    resp, status = api_call(
        "GET",
        "/usage/by-site",
        api_key=config["api_key"],
        params=params or None,
    )
    if status != HTTP_OK:
        print(f"Failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    sites = resp.get("sites", [])
    if not sites:
        print("No usage in this range.")
        return

    print(f"Usage by site ({len(sites)}):")
    for s in sites:
        print(f"  {s.get('domain', '?')} - {s.get('total_credits', 0)} credits")
        for b in s.get("breakdown", []):
            print(f"      {b.get('category', '?')}: {b.get('credits', 0)}")


def cmd_usage_line_items(args):
    """List individual paid operations (line items), newest first."""
    config = require_user_config()
    params = {}
    if getattr(args, "from_time", None):
        params["from"] = args.from_time
    if getattr(args, "to_time", None):
        params["to"] = args.to_time
    if getattr(args, "site_uuid", None):
        params["site_uuid"] = args.site_uuid
    if getattr(args, "category", None):
        params["category"] = args.category
    if getattr(args, "limit", None):
        params["limit"] = args.limit

    resp, status = api_call(
        "GET",
        "/usage/line-items",
        api_key=config["api_key"],
        params=params or None,
    )
    if status != HTTP_OK:
        print(f"Failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    items = resp.get("line_items", [])
    if not items:
        print("No usage in this range.")
        return

    print(f"Line items ({len(items)}):")
    for i in items:
        when = i.get("last_charged_at", "?")
        print(
            f"  {when} - {i.get('domain', '?')} - "
            f"{i.get('category', '?')}/{i.get('operation', '?')} - "
            f"{i.get('credits', 0)} credits"
        )


def cmd_account(_args):
    """Show account details including email and company."""
    config = require_user_config()

    resp, status = api_call("GET", "/account", api_key=config["api_key"])
    if status != HTTP_OK:
        print(f"Failed to fetch account (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    email = resp.get("owner_email")
    company = resp.get("company_name")
    owner_name = resp.get("owner_name")
    site_count = resp.get("site_count", 0)

    # Update config if email/company were missing
    if email or company:
        site_uuid = config.get("site_uuid")
        save_user_config(config["api_key"], site_uuid, email, company)

    print("🤖 BotSee Account")
    print("━━━━━━━━━━━━━━━━━")
    if owner_name:
        print(f"👤 Name: {owner_name}")
    if email:
        print(f"📧 Email: {email}")
    if company:
        print(f"🏢 Company: {company}")
    print(f"🌐 Sites: {site_count}")


def signup_resume():
    """Resume a pending signup by checking its status."""
    print("🤖 BotSee Signup")
    print("")
    print("⏳ Checking signup status...")

    pending = load_pending_signup()
    if not pending:
        print("No pending signup found. Run /botsee signup.", file=sys.stderr)
        sys.exit(1)

    status_url = pending.get("status_url")
    setup_token = pending.get("setup_token")

    # Check status once
    poll_url = normalize_endpoint(status_url) if status_url else f"/signup/{setup_token}/status"
    poll_resp, poll_status = api_call("GET", poll_url)

    if poll_status == HTTP_OK:
        response_setup_url = poll_resp.get("setup_url")
        if response_setup_url and response_setup_url != pending.get("setup_url"):
            pending["setup_url"] = response_setup_url
            save_pending_signup(pending)

        signup_status = poll_resp.get("status")
        if signup_status == "completed":
            api_key = poll_resp.get("api_key")
            contact_email = poll_resp.get("contact_email")
            company_name = poll_resp.get("company_name")
            if api_key:
                # Save API key and account info, clean up pending signup
                save_user_config(api_key, None, contact_email, company_name)
                clear_pending_signup()

                print(f"✅ Signup complete!")
                print("")
                print(f"Next: /botsee create-site <domain>")
                return
        elif signup_status == "expired":
            clear_pending_signup()
            print("Signup token expired. Run /botsee signup --reset to start over.", file=sys.stderr)
            sys.exit(1)
    elif poll_status in (HTTP_NOT_FOUND, HTTP_GONE):
        clear_pending_signup()
        print("Signup link is invalid or expired. Run /botsee signup --reset for a new setup URL.", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"Signup status check failed (HTTP {poll_status}): {poll_resp}", file=sys.stderr)
        if poll_status == HTTP_PAYMENT_REQUIRED:
            show_payment_required_help(poll_resp)
        sys.exit(1)

    # Still pending
    setup_url = pending.get("setup_url")
    if not setup_url:
        print("Signup is still pending but no setup URL is available. Run /botsee signup --reset to start over.", file=sys.stderr)
        sys.exit(1)
    print(f"📋 Signup not yet complete. Please visit:")
    print(f"")
    print(f"   {setup_url}")
    print(f"")
    print("After completing signup, run /botsee signup-status to save your API key.")
    sys.exit(1)  # Exit with error - signup incomplete


def signup_new(args):
    """Create a new credit-card signup token and save for later completion."""
    signup_data = {}
    if args.email:
        signup_data["contact_email"] = args.email
    if args.name:
        signup_data["contact_name"] = args.name
    if args.company:
        signup_data["company_name"] = args.company
    if hasattr(args, 'webhook_url') and args.webhook_url:
        signup_data["webhook_url"] = args.webhook_url

    resp, status = api_call("POST", "/signup", data=signup_data)
    if status not in (HTTP_OK, HTTP_CREATED):
        print(f"Signup failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    setup_token = resp.get("setup_token")
    setup_url = resp.get("setup_url")
    status_url = resp.get("status_url")

    if not setup_token or not setup_url:
        print(f"Unexpected signup response: {resp}", file=sys.stderr)
        sys.exit(1)

    print("")
    print("Credit card signup token created.")
    print(f"Complete signup: {setup_url}")
    print("")

    save_pending_signup({
        "setup_token": setup_token,
        "setup_url": setup_url,
        "status_url": status_url,
        "payment_method": "credit_card",
    })

    print("After completing signup, run /botsee signup-status to save your API key.")


def signup_save_key(api_key):
    """Save API key directly without signup flow."""
    # Validate API key format
    if not api_key.startswith("bts_"):
        print("Error: API key must start with 'bts_'", file=sys.stderr)
        sys.exit(1)

    # Save to config
    config_path = os.path.join(os.path.expanduser("~/.botsee"), "config.json")
    os.makedirs(os.path.dirname(config_path), exist_ok=True)

    # Load existing config or create new
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = json.load(f)
    else:
        config = {}

    # Update API key
    config["api_key"] = api_key

    # Write back
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    os.chmod(config_path, 0o600)

    print("✓ API key saved successfully")
    print("\nNext step: Run /botsee create-site <domain> to get started")


def cmd_signup(args):
    """Signup for BotSee: create account and get API key."""
    # If API key provided directly, save it and skip signup
    if hasattr(args, 'api_key') and args.api_key:
        return signup_save_key(args.api_key)

    if getattr(args, "reset", False):
        if PENDING_SIGNUP.exists():
            print("Discarding pending signup state...", file=sys.stderr)
        clear_pending_signup()

    if PENDING_SIGNUP.exists():
        return signup_resume()

    return signup_new(args)


def cmd_signup_usdc(args):
    """Create a USDC signup token via the dedicated /signup/usdc endpoint."""
    signup_data = {}
    if args.email:
        signup_data["contact_email"] = args.email
    if args.name:
        signup_data["contact_name"] = args.name
    if args.company:
        signup_data["company_name"] = args.company
    if args.no_email:
        signup_data["no_email"] = True

    resp, status = api_call("POST", "/signup/usdc", data=signup_data)
    if status not in (HTTP_OK, HTTP_CREATED):
        print(f"USDC signup failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    setup_token = resp.get("setup_token")
    setup_url = resp.get("setup_url")
    status_url = resp.get("status_url")

    if not setup_token:
        print(f"Unexpected signup response: {resp}", file=sys.stderr)
        sys.exit(1)

    print("USDC signup token created.")
    if setup_url:
        print(f"Setup URL: {setup_url}")
    print("")
    print("Next steps:")
    print(f"  /botsee signup-pay-usdc --amount-cents {USDC_MIN_CENTS} --token {setup_token}")
    print(f"  /botsee signup-status --token {setup_token}")

    save_pending_signup({
        "setup_token": setup_token,
        "setup_url": setup_url,
        "status_url": status_url,
        "payment_method": "usdc",
    })


def cmd_signup_pay_usdc(args):
    """Initiate USDC x402 payment for signup token."""
    token = resolve_signup_token(args.token)

    if not (USDC_MIN_CENTS <= args.amount_cents <= USDC_MAX_CENTS):
        print(
            f"amount-cents must be between {USDC_MIN_CENTS} and {USDC_MAX_CENTS}",
            file=sys.stderr,
        )
        sys.exit(1)

    payment_headers = {PAYMENT_HEADER_SIGNATURE: args.payment} if args.payment else None
    resp, status = api_call(
        "POST",
        f"/signup/{token}/pay-usdc",
        data={"amount_cents": args.amount_cents},
        extra_headers=payment_headers,
    )

    if status == HTTP_PAYMENT_REQUIRED:
        show_usdc_payment_instructions(resp)
        print("")
        print(f"Use a wallet to pay, then retry with --payment <proof>:")
        print(f"  /botsee signup-pay-usdc --token {token} --amount-cents {args.amount_cents} --payment <proof>")
        return

    if status not in (HTTP_OK, HTTP_CREATED, HTTP_ACCEPTED):
        print(f"USDC signup payment failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    show_payment_headers(resp)
    print("✅ USDC payment submitted.")
    print(f"Check status: /botsee signup-status --token {token}")

    pending = load_pending_signup() or {}
    pending.update({
        "setup_token": token,
        "status_url": resp.get("status_url", pending.get("status_url")),
        "payment_method": "usdc",
    })
    save_pending_signup(pending)


def cmd_signup_status(args):
    """Check signup token status and save API key when complete."""
    token = resolve_signup_token(args.token)
    resp, status = api_call("GET", f"/signup/{token}/status")

    if status != HTTP_OK:
        if status in (HTTP_NOT_FOUND, HTTP_GONE):
            pending = load_pending_signup()
            if pending and pending.get("setup_token") == token:
                clear_pending_signup()
            print("Signup link is invalid or expired. Run /botsee signup --reset for a new setup URL.", file=sys.stderr)
            sys.exit(1)
        print(f"Signup status check failed (HTTP {status}): {resp}", file=sys.stderr)
        if status == HTTP_PAYMENT_REQUIRED:
            show_payment_required_help(resp)
        sys.exit(1)

    pending = load_pending_signup()
    response_setup_url = resp.get("setup_url")
    if pending and pending.get("setup_token") == token and response_setup_url and response_setup_url != pending.get("setup_url"):
        pending["setup_url"] = response_setup_url
        save_pending_signup(pending)

    signup_status = resp.get("status", "unknown")
    payment_method = resp.get("payment_method")
    print(f"Signup status: {signup_status}")
    if payment_method:
        print(f"Payment method: {payment_method}")

    if signup_status == "completed":
        api_key = resp.get("api_key")
        if not api_key:
            if resp.get("key_already_delivered"):
                print("✅ Signup complete. API key was already retrieved and saved.")
                print("Your key is in ~/.botsee/config.json — run /botsee status to verify.")
            else:
                print("Signup completed but API key was not returned.", file=sys.stderr)
                sys.exit(1)
            return

        save_user_config(
            api_key,
            None,
            resp.get("contact_email"),
            resp.get("company_name"),
        )
        if pending and pending.get("setup_token") == token:
            clear_pending_signup()

        print("✅ Signup complete. API key saved.")
        print("Next: /botsee create-site <domain>")
        return

    if signup_status == "expired":
        if pending and pending.get("setup_token") == token:
            clear_pending_signup()
        print("Signup token expired. Run /botsee signup again.", file=sys.stderr)
        sys.exit(1)

    if pending and pending.get("setup_url"):
        print(f"Complete in browser: {pending['setup_url']}")



def cmd_revoke_api_key(args):
    """Revoke an API key by ID."""
    config = require_user_config()
    resp, status = api_call("DELETE", f"/api-keys/{args.id}", api_key=config["api_key"])

    if status != 204:
        error = resp.get("error", "Failed to revoke API key") if isinstance(resp, dict) else "Failed to revoke API key"
        msg = error.get("message", str(error)) if isinstance(error, dict) else str(error)
        print(f"Error: {msg} (HTTP {status})", file=sys.stderr)
        sys.exit(1)

    print(f"✅ API key {args.id} revoked.")


def cmd_reset_api_key(args):
    """Exchange a one-time reset token for a new API key."""
    resp, status = api_call("POST", "/api-keys/reset", data={"token": args.token})

    if status != HTTP_OK:
        error = resp.get("error", "Failed to reset API key") if isinstance(resp, dict) else "Failed to reset API key"
        msg = error.get("message", str(error)) if isinstance(error, dict) else str(error)
        print(f"Error: {msg} (HTTP {status})", file=sys.stderr)
        sys.exit(1)

    api_key_data = resp.get("api_key", {})
    raw_key = api_key_data.get("key")

    if not raw_key:
        print("Error: No API key returned from server", file=sys.stderr)
        sys.exit(1)

    # Preserve existing site_uuid from config
    existing_config = load_user_config() or {}
    site_uuid = existing_config.get("site_uuid")

    save_user_config(raw_key, site_uuid)

    print("✅ API key reset successfully.")
    print(f"New key saved to ~/.botsee/config.json")
    print("")
    print("Next: Run /botsee to verify your account status")


def cmd_rotate_api_key(args):
    """Atomically rotate an API key: creates a new key, revokes the old one."""
    config = require_user_config()
    resp, status = api_call("POST", f"/api-keys/{args.id}/rotate", api_key=config["api_key"])

    if status != 201:
        error = resp.get("error", "Failed to rotate API key") if isinstance(resp, dict) else "Failed to rotate API key"
        msg = error.get("message", str(error)) if isinstance(error, dict) else str(error)
        print(f"Error: {msg} (HTTP {status})", file=sys.stderr)
        sys.exit(1)

    api_key_data = resp.get("api_key", {})
    raw_key = api_key_data.get("key")

    if not raw_key:
        print("Error: No API key returned from server", file=sys.stderr)
        sys.exit(1)

    # Preserve existing site_uuid from config
    existing_config = load_user_config() or {}
    site_uuid = existing_config.get("site_uuid")

    save_user_config(raw_key, site_uuid)

    print("✅ API key rotated successfully.")
    print(f"New key prefix: {api_key_data.get('key_prefix', '')}")
    print(f"New key saved to ~/.botsee/config.json")
    print("")
    print("Your old key has been revoked.")


def cmd_topup_usdc(args):
    """Add credits via USDC x402 challenge flow."""
    config = require_user_config()

    if not (USDC_MIN_CENTS <= args.amount_cents <= USDC_MAX_CENTS):
        print(
            f"amount-cents must be between {USDC_MIN_CENTS} and {USDC_MAX_CENTS}",
            file=sys.stderr,
        )
        sys.exit(1)

    payment_headers = {PAYMENT_HEADER_SIGNATURE: args.payment} if args.payment else None
    resp, status = api_call(
        "POST",
        "/billing/topups/usdc",
        data={"amount_cents": args.amount_cents},
        api_key=config["api_key"],
        extra_headers=payment_headers,
    )

    if status == HTTP_PAYMENT_REQUIRED:
        show_usdc_payment_instructions(resp)
        print("")
        print(f"Use a wallet to pay, then retry with --payment <proof>:")
        print(f"  /botsee topup-usdc --amount-cents {args.amount_cents} --payment <proof>")
        return

    if status not in (HTTP_OK, HTTP_CREATED, HTTP_ACCEPTED):
        print(f"USDC top-up failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    show_payment_headers(resp)
    print("✅ USDC top-up submitted.")
    credits = resp.get("credits")
    if credits is not None:
        print(f"Credits to add on confirmation: {credits}")


def cmd_create_site(args):
    """Create site and generate content."""
    # Require user config (API key must exist from signup)
    config = require_user_config()
    api_key = config.get("api_key")

    domain = normalize_domain(args.domain)
    types = args.types
    personas = args.personas
    questions = args.questions

    # Validate ranges
    if not (TYPES_MIN <= types <= TYPES_MAX):
        print(f"Error: types must be between {TYPES_MIN} and {TYPES_MAX}", file=sys.stderr)
        sys.exit(1)
    if not (PERSONAS_MIN <= personas <= PERSONAS_MAX):
        print(f"Error: personas must be between {PERSONAS_MIN} and {PERSONAS_MAX}", file=sys.stderr)
        sys.exit(1)
    if not (QUESTIONS_MIN <= questions <= QUESTIONS_MAX):
        print(f"Error: questions must be between {QUESTIONS_MIN} and {QUESTIONS_MAX}", file=sys.stderr)
        sys.exit(1)

    print(f"🤖 BotSee Configuration")
    print("")
    print(f"Using: {types} types, {personas} personas/type, {questions} questions/persona")
    print("")

    # Create site
    print(f"⏳ Creating site: {domain}")
    resp, status = api_call("POST", "/sites", data={"url": domain}, api_key=api_key)
    if status not in (HTTP_OK, HTTP_CREATED):
        print(f"Site creation failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)
    site_uuid = resp.get("site", {}).get("uuid")
    print(f"✅ Site created: {site_uuid}")
    print("")

    # Generate customer types
    print(f"⏳ Generating {types} customer type(s)...")
    resp, status = api_call(
        "POST", f"/sites/{site_uuid}/customer-types/generate",
        data={"count": types}, api_key=api_key
    )
    if status not in (200, 201):
        print(f"Customer type generation failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    ct_list = resp.get("customer_types", [])
    print("📋 Customer Types:")
    for ct in ct_list:
        print(f"  • {ct.get('name', '?')}")
    print("")

    # Generate personas per type
    all_persona_uuids = []
    print(f"⏳ Generating personas ({personas} per type)...")
    for ct in ct_list:
        ct_uuid = ct.get("uuid")
        ct_name = ct.get("name", "?")
        resp, status = api_call(
            "POST", f"/customer-types/{ct_uuid}/personas/generate",
            data={"count": personas}, api_key=api_key
        )
        if status not in (200, 201):
            print(f"  ✗ {ct_name}: failed (HTTP {status})", file=sys.stderr)
            continue
        p_list = resp.get("personas", [])
        all_persona_uuids.extend(p.get("uuid") for p in p_list)
        print(f"  ✓ {ct_name}: {len(p_list)} persona(s)")

    total_personas = len(all_persona_uuids)
    print(f"✅ Generated {total_personas} persona(s)")
    print("")

    # Generate questions per persona
    total_questions = 0
    print(f"⏳ Generating questions ({questions} per persona)...")
    for p_uuid in all_persona_uuids:
        resp, status = api_call(
            "POST", f"/personas/{p_uuid}/questions/generate",
            data={"count": questions}, api_key=api_key
        )
        if status not in (200, 201):
            continue
        total_questions += len(resp.get("questions", []))
    print(f"✅ Generated {total_questions} question(s)")
    print("")

    # Save configs
    save_user_config(api_key, site_uuid)
    save_workspace_config(domain, types, personas, questions)

    # Re-fetch balance
    usage_resp, _ = api_call("GET", "/usage", api_key=api_key)
    balance = usage_resp.get("balance", "?")

    print("✅ Configuration complete!")
    print("")
    print("Generated:")
    print(f"  • {len(ct_list)} customer type(s)")
    print(f"  • {total_personas} persona(s)")
    print(f"  • {total_questions} question(s)")
    print("")
    print(f"💰 Remaining: {balance} credits")
    print("")
    print("Next steps:")
    print("  /botsee analyze           - Run competitive analysis")
    print("")
    print("View your content:")
    print("  /botsee list-types        - View customer types")
    print("  /botsee list-personas     - View all personas")
    print("  /botsee get-site          - View site details")


def cmd_config_show(_args):
    """Display saved workspace configuration."""
    config = load_workspace_config()
    if not config:
        print("No workspace config found. Run: /botsee create-site <domain>")
        return

    print("📋 BotSee Configuration")
    print("━━━━━━━━━━━━━━━━━━━━━")
    print(f"Domain: {config.get('domain', '?')}")
    print(f"Customer Types: {config.get('types', '?')}")
    print(f"Personas per Type: {config.get('personas_per_type', '?')}")
    print(f"Questions per Persona: {config.get('questions_per_persona', '?')}")
    print("")
    print("This configuration was used when creating the site.")


def cmd_analyze(args):
    """Run competitive analysis on configured site."""
    config = require_user_config()
    api_key = config["api_key"]

    # Use provided site_uuid or fall back to config
    site_uuid = args.site_uuid if hasattr(args, 'site_uuid') and args.site_uuid else config.get("site_uuid")

    print("🤖 BotSee Analysis")
    print("━━━━━━━━━━━━━━━━━━")
    print("")

    # Start analysis
    print("⏳ Starting analysis...")
    analysis_payload = {"site_uuid": site_uuid}
    if args.scope:
        analysis_payload["scope"] = args.scope
    models = parse_comma_separated(args.models)
    if models:
        analysis_payload["models"] = models

    resp, status = api_call(
        "POST",
        "/analysis",
        data=analysis_payload,
        api_key=api_key,
    )
    if status not in (200, 201, 202):
        print(f"Analysis failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    analysis_uuid = resp.get("analysis", {}).get("uuid")
    if not analysis_uuid:
        print(f"Unexpected response: {resp}", file=sys.stderr)
        sys.exit(1)

    print(f"📊 Analysis started: {analysis_uuid}")
    print("⏳ Processing (this may take a few minutes)...")

    # Poll for completion with exponential backoff
    wait_time = 1  # Start with 1 second
    max_wait = 30  # Cap at 30 seconds
    start_time = time.time()

    while True:
        elapsed = time.time() - start_time
        if elapsed >= ANALYSIS_POLL_TIMEOUT:
            print("Analysis timed out.", file=sys.stderr)
            sys.exit(1)

        # Check status immediately on first iteration, then wait before subsequent checks
        if elapsed > 0:
            time.sleep(wait_time)
            # Exponential backoff: 1s → 2s → 4s → 8s → ... → max 30s
            wait_time = min(wait_time * 2, max_wait)

        resp, status = api_call("GET", f"/analysis/{analysis_uuid}", api_key=api_key)
        if status != HTTP_OK:
            continue

        analysis_status = resp.get("analysis", {}).get("status")
        if analysis_status == "completed":
            print("✅ Analysis complete!")
            print("")
            break
        elif analysis_status == "failed":
            print("Analysis failed.", file=sys.stderr)
            sys.exit(1)

    # Fetch results
    comp_resp, _ = api_call("GET", f"/analysis/{analysis_uuid}/competitors", api_key=api_key)
    kw_resp, _ = api_call("GET", f"/analysis/{analysis_uuid}/keywords", api_key=api_key)
    src_resp, _ = api_call("GET", f"/analysis/{analysis_uuid}/sources", api_key=api_key)

    # Display competitors by customer type
    by_customer_type = comp_resp.get("by_customer_type", [])
    overall_summary = comp_resp.get("overall_summary", {})

    if by_customer_type:
        print("📊 Competitors by Customer Type:")
        print("")
        for group in by_customer_type:
            customer_type_name = group.get("customer_type_name", "Unknown")
            competitors = group.get("competitors", [])[:5]  # Top 5 per type

            if competitors:
                print(f"  {customer_type_name}:")
                for c in competitors:
                    name = c.get("name", "?")
                    appearance = c.get("appearance_percentage", 0)
                    avg_rank = c.get("avg_rank", "?")
                    mentions = c.get("mentions", 0)
                    print(f"    • {name} - {appearance:.0f}% appearance, avg rank {avg_rank}, {mentions} mentions")
                print("")

        # Show overall summary
        total_competitors = overall_summary.get("total_unique_competitors", 0)
        total_responses = overall_summary.get("total_responses_analyzed", 0)
        print(f"  Total: {total_competitors} unique competitors across {total_responses} responses")
        print("")

    # Display keywords
    keywords = kw_resp.get("keywords", [])[:10]
    if keywords:
        print("🔑 Top Keywords:")
        for k in keywords:
            keyword = k.get("keyword", "?")
            freq = k.get("frequency", 0)
            print(f"  • \"{keyword}\" ({freq}x)")
        print("")

    # Display sources
    sources = src_resp.get("sources", [])[:10]
    if sources:
        print("📄 Top Sources:")
        for s in sources:
            url = s.get("url", "?")
            mentions = s.get("mentions", 0)
            own = " ⭐" if s.get("own_company_mentioned") else ""
            print(f"  • {url} ({mentions}x){own}")
        print("")

    # Show balance
    usage_resp, _ = api_call("GET", "/usage", api_key=api_key)
    balance = usage_resp.get("balance", "?")
    print(f"💰 Remaining: {balance} credits")


def cmd_content(args):
    """Generate blog post from latest analysis."""
    config = require_user_config()
    api_key = config["api_key"]
    site_uuid = config["site_uuid"]

    # Get latest analysis
    resp, status = api_call(
        "GET",
        f"/sites/{site_uuid}/analysis",
        api_key=api_key,
        params={"limit": 1},
    )
    if status != 200:
        print(f"Failed to fetch analyses (HTTP {status})", file=sys.stderr)
        sys.exit(1)

    analyses = resp.get("analyses", [])
    if not analyses:
        print("No analysis found. Run /botsee analyze first.", file=sys.stderr)
        sys.exit(1)

    analysis_uuid = analyses[0].get("uuid")

    print("⏳ Generating blog post...")
    content_payload = {}
    if args.question_uuid:
        content_payload["question_uuid"] = args.question_uuid
    if args.provider:
        content_payload["provider"] = args.provider

    resp, status = api_call(
        "POST", f"/analysis/{analysis_uuid}/content",
        data=content_payload, api_key=api_key
    )
    if status not in (200, 201):
        print(f"Content generation failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    content = resp.get("content", "")
    credits_used = resp.get("credits_used", "?")

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(content)
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("")
    print(f"💰 Used: {credits_used} credits")

    # Auto-save
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"botsee-{timestamp}.md"
    with open(filename, "w") as f:
        f.write(content)
    print(f"✅ Saved: {filename}")


def cmd_recommend(args):
    """Get AI-generated recommendations to improve AI visibility."""
    config = require_user_config()
    api_key = config["api_key"]
    site_uuid = config["site_uuid"]

    analysis_uuid = args.analysis_uuid
    if not analysis_uuid:
        resp, status = api_call(
            "GET",
            f"/sites/{site_uuid}/analysis",
            api_key=api_key,
            params={"limit": 1},
        )
        if status != HTTP_OK or not resp.get("analyses"):
            print("No analysis found. Run /botsee analyze first.", file=sys.stderr)
            sys.exit(1)
        analysis_uuid = resp["analyses"][0]["uuid"]

    print("⏳ Generating recommendations...")
    resp, status = api_call("POST", f"/analysis/{analysis_uuid}/recommendations", api_key=api_key)

    if status == HTTP_PAYMENT_REQUIRED:
        show_payment_required_help(resp)
        sys.exit(1)
    if status == 422:
        print("Analysis is not yet complete. Wait for it to finish.", file=sys.stderr)
        sys.exit(1)
    if status not in (HTTP_OK, HTTP_CREATED):
        print(f"Failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    recommendations = resp.get("recommendations", [])
    credits_used = resp.get("credits_used", 0)

    print("💡 AI Visibility Recommendations")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("")
    for i, rec in enumerate(recommendations, 1):
        priority = rec.get("priority", "?").upper()
        action = rec.get("action", "?")
        reasoning = rec.get("reasoning", "")
        print(f"  {i}. [{priority}] {action}")
        if reasoning:
            print(f"     {reasoning}")
        print("")

    if credits_used:
        print(f"💰 Used: {credits_used} credits")
    else:
        print("💰 Cached result (no credits used)")


# --- Sites CRUD ---


def cmd_list_sites(args):
    """List all sites."""
    config = require_user_config()
    params = {}
    if args.limit:
        params["limit"] = args.limit
    if args.cursor:
        params["cursor"] = args.cursor
    if args.include_archived:
        params["include_archived"] = "true"

    resp, status = api_call(
        "GET",
        "/sites",
        api_key=config["api_key"],
        params=params or None,
    )
    if status != 200:
        print(f"Failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    sites = resp.get("sites", [])
    if not sites:
        print("No sites found.")
        return

    active_uuid = config.get("site_uuid")

    print(f"Sites ({len(sites)}):")
    for s in sites:
        uuid = s.get("uuid", "?")
        url = s.get("url", "?")
        name = s.get("product_name", "?")
        active_marker = " ⭐" if uuid == active_uuid else ""
        print(f"  {uuid} - {url} ({name}){active_marker}")


def cmd_get_site(args):
    """Get a site by UUID."""
    config = require_user_config()
    resp, status = api_call("GET", f"/sites/{args.uuid}", api_key=config["api_key"])
    if status != 200:
        print(f"Failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    site = resp.get("site", {})
    print(json.dumps(site, indent=2))


def cmd_archive_site(args):
    """Archive (soft-delete) a site."""
    config = require_user_config()
    resp, status = api_call("DELETE", f"/sites/{args.uuid}", api_key=config["api_key"])
    if status == 204:
        print(f"✅ Site {args.uuid} archived")
    else:
        print(f"Failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)


def cmd_use_site(args):
    """Switch active site."""
    config = require_user_config()
    api_key = config["api_key"]
    site_uuid = args.uuid

    # Verify site exists
    resp, status = api_call("GET", f"/sites/{site_uuid}", api_key=api_key)
    if status != 200:
        print(f"Failed to fetch site (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    site = resp.get("site", {})
    site_url = site.get("url", "?")
    site_name = site.get("product_name", "?")

    # Update config with new active site
    save_user_config(api_key, site_uuid)

    print(f"✅ Active site changed to: {site_name}")
    print(f"   URL: {site_url}")
    print(f"   UUID: {site_uuid}")


# --- Customer Types CRUD ---


def cmd_list_types(args):
    """List customer types for a site."""
    config = require_user_config()
    site_uuid = args.site_uuid or config["site_uuid"]
    resp = api_get(f"/sites/{site_uuid}/customer-types")
    types = resp.get("customer_types", [])
    if not types:
        print("No customer types found.")
        return

    print(f"Customer Types ({len(types)}):")
    for t in types:
        uuid = t.get("uuid", "?")
        name = t.get("name", "?")
        desc = t.get("description", "")[:50]
        print(f"  {uuid} - {name}")
        if desc:
            print(f"    {desc}...")


def cmd_get_type(args):
    """Get a customer type by UUID."""
    resp = api_get(f"/customer-types/{args.uuid}")
    ct = resp.get("customer_type", {})
    print(json.dumps(ct, indent=2))


def cmd_create_type(args):
    """Create a customer type manually (FREE)."""
    config = require_user_config()
    data = {"name": args.name}
    if args.description:
        data["description"] = args.description

    resp, status = api_call(
        "POST", f"/sites/{args.site_uuid}/customer-types",
        data=data, api_key=config["api_key"]
    )
    if status not in (200, 201):
        print(f"Failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    ct = resp.get("customer_type", {})
    uuid = ct.get("uuid", "?")
    print(f"✅ Customer type created: {uuid}")
    print(json.dumps(ct, indent=2))


def cmd_generate_types(args):
    """AI-generate customer types (5 credits each)."""
    config = require_user_config()
    site_uuid = args.site_uuid or config["site_uuid"]
    resp, status = api_call(
        "POST", f"/sites/{site_uuid}/customer-types/generate",
        data={"count": args.count}, api_key=config["api_key"]
    )
    if status not in (200, 201):
        print(f"Failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    types = resp.get("customer_types", [])
    print(f"✅ Generated {len(types)} customer type(s)")
    for t in types:
        print(f"  • {t.get('name', '?')}")


def cmd_update_type(args):
    """Update a customer type."""
    config = require_user_config()
    data = {}
    if args.name:
        data["name"] = args.name
    if args.description:
        data["description"] = args.description

    resp, status = api_call(
        "PUT", f"/customer-types/{args.uuid}",
        data=data, api_key=config["api_key"]
    )
    if status not in (200, 204):
        print(f"Failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    print(f"✅ Customer type {args.uuid} updated")


def cmd_archive_type(args):
    """Archive a customer type."""
    api_delete(f"/customer-types/{args.uuid}", f"Customer type {args.uuid}")


# --- Personas CRUD ---


def cmd_list_personas(args):
    """List personas for a customer type."""
    resp = api_get(f"/customer-types/{args.type_uuid}/personas")
    personas = resp.get("personas", [])
    if not personas:
        print("No personas found.")
        return

    print(f"Personas ({len(personas)}):")
    for p in personas:
        uuid = p.get("uuid", "?")
        name = p.get("name", "?")
        desc = p.get("description", "")[:50]
        print(f"  {uuid} - {name}")
        if desc:
            print(f"    {desc}...")


def cmd_get_persona(args):
    """Get a persona by UUID."""
    resp = api_get(f"/personas/{args.uuid}")
    persona = resp.get("persona", {})
    print(json.dumps(persona, indent=2))


def cmd_create_persona(args):
    """Create a persona manually (FREE)."""
    config = require_user_config()
    data = {"name": args.name}
    if args.description:
        data["description"] = args.description

    resp, status = api_call(
        "POST", f"/customer-types/{args.type_uuid}/personas",
        data=data, api_key=config["api_key"]
    )
    if status not in (200, 201):
        print(f"Failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    persona = resp.get("persona", {})
    uuid = persona.get("uuid", "?")
    print(f"✅ Persona created: {uuid}")
    print(json.dumps(persona, indent=2))


def cmd_generate_personas(args):
    """AI-generate personas (5 credits each)."""
    config = require_user_config()
    resp, status = api_call(
        "POST", f"/customer-types/{args.type_uuid}/personas/generate",
        data={"count": args.count}, api_key=config["api_key"]
    )
    if status not in (200, 201):
        print(f"Failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    personas = resp.get("personas", [])
    print(f"✅ Generated {len(personas)} persona(s)")
    for p in personas:
        print(f"  • {p.get('name', '?')}")


def cmd_update_persona(args):
    """Update a persona."""
    config = require_user_config()
    data = {}
    if args.name:
        data["name"] = args.name
    if args.description:
        data["description"] = args.description

    resp, status = api_call(
        "PUT", f"/personas/{args.uuid}",
        data=data, api_key=config["api_key"]
    )
    if status not in (200, 204):
        print(f"Failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    print(f"✅ Persona {args.uuid} updated")


def cmd_archive_persona(args):
    """Archive a persona."""
    api_delete(f"/personas/{args.uuid}", f"Persona {args.uuid}")


# --- Questions CRUD ---


def cmd_list_questions(args):
    """List questions for a persona."""
    resp = api_get(f"/personas/{args.persona_uuid}/questions")
    questions = resp.get("questions", [])
    if not questions:
        print("No questions found.")
        return

    print(f"Questions ({len(questions)}):")
    for q in questions:
        uuid = q.get("uuid", "?")
        text = (q.get("text") or q.get("question") or "?")[:80]
        print(f"  {uuid} - {text}")


def cmd_get_question(args):
    """Get a question by UUID."""
    resp = api_get(f"/questions/{args.uuid}/results")
    question = resp.get("question", {})
    print(json.dumps(question, indent=2))


def cmd_create_question(args):
    """Create a question manually (FREE)."""
    config = require_user_config()
    # Send both keys for compatibility across API versions/docs examples.
    data = {"question": args.text, "text": args.text}

    resp, status = api_call(
        "POST", f"/personas/{args.persona_uuid}/questions",
        data=data, api_key=config["api_key"]
    )
    if status not in (200, 201):
        print(f"Failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    question = resp.get("question", {})
    uuid = question.get("uuid", "?")
    print(f"✅ Question created: {uuid}")
    print(json.dumps(question, indent=2))


def cmd_generate_questions(args):
    """AI-generate questions (10 credits flat)."""
    config = require_user_config()
    resp, status = api_call(
        "POST", f"/personas/{args.persona_uuid}/questions/generate",
        data={"count": args.count}, api_key=config["api_key"]
    )
    if status not in (200, 201):
        print(f"Failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    questions = resp.get("questions", [])
    print(f"✅ Generated {len(questions)} question(s)")
    for q in questions:
        text = (q.get("text") or q.get("question") or "?")[:80]
        print(f"  • {text}")


def cmd_update_question(args):
    """Update a question."""
    config = require_user_config()
    data = {}
    if args.text:
        # Send both keys for compatibility across API versions/docs examples.
        data["question"] = args.text
        data["text"] = args.text
    if args.priority:
        data["priority"] = args.priority
    if not data:
        print("Provide --text and/or --priority.", file=sys.stderr)
        sys.exit(1)

    resp, status = api_call(
        "PUT", f"/questions/{args.uuid}",
        data=data, api_key=config["api_key"]
    )
    if status not in (200, 204):
        print(f"Failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    print(f"✅ Question {args.uuid} updated")


def cmd_delete_question(args):
    """Delete a question (permanent)."""
    api_delete(f"/questions/{args.uuid}", f"Question {args.uuid}", expected_status=HTTP_NO_CONTENT)


# --- Results commands ---


def cmd_results_competitors(args):
    """Get competitors from analysis."""
    resp = api_get(f"/analysis/{args.analysis_uuid}/competitors")
    # Return full response with by_customer_type and overall_summary
    print(json.dumps(resp, indent=2))


def cmd_results_keywords(args):
    """Get keywords from analysis."""
    resp = api_get(f"/analysis/{args.analysis_uuid}/keywords")
    keywords = resp.get("keywords", [])
    print(json.dumps(keywords, indent=2))


def cmd_results_sources(args):
    """Get sources from analysis."""
    resp = api_get(f"/analysis/{args.analysis_uuid}/sources")
    sources = resp.get("sources", [])
    print(json.dumps(sources, indent=2))


def cmd_results_responses(args):
    """Get raw LLM responses from analysis."""
    resp = api_get(f"/analysis/{args.analysis_uuid}/responses")
    responses = resp.get("responses", [])
    print(json.dumps(responses, indent=2))


def cmd_results_keyword_opportunities(args):
    """Get keyword opportunities from analysis."""
    config = require_user_config()
    params = {}
    if args.threshold is not None:
        params["threshold"] = args.threshold
    if args.rank_threshold is not None:
        params["rank_threshold"] = args.rank_threshold
    resp, status = api_call(
        "GET",
        f"/analysis/{args.analysis_uuid}/keyword_opportunities",
        api_key=config["api_key"],
        params=params or None,
    )
    if status != HTTP_OK:
        print(f"Failed (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(resp, indent=2))


def cmd_results_source_opportunities(args):
    """Get source opportunities from analysis."""
    resp = api_get(f"/analysis/{args.analysis_uuid}/source_opportunities")
    print(json.dumps(resp, indent=2))


def cmd_list_analyses(args):
    """List analysis runs for a site."""
    config = require_user_config()
    site_uuid = args.site_uuid or config.get("site_uuid")

    if not site_uuid:
        print("Error: No site specified. Use --site-uuid or run use-site first.", file=sys.stderr)
        sys.exit(1)

    # Build query params
    params = {}
    if args.limit:
        params["limit"] = args.limit
    if args.cursor:
        params["cursor"] = args.cursor
    if args.persona_uuid:
        params["persona_uuid"] = args.persona_uuid
    if args.model:
        params["model"] = args.model
    if args.from_time:
        params["from"] = args.from_time
    if args.to_time:
        params["to"] = args.to_time

    resp, status = api_call(
        "GET",
        f"/sites/{site_uuid}/analysis",
        api_key=config["api_key"],
        params=params,
    )

    if status != HTTP_OK:
        print(f"Failed to list analyses (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    # Display analyses
    analyses = resp.get("analyses", [])
    if not analyses:
        print("No analyses found.")
        return

    print(f"Analysis runs for site {site_uuid}:\n")
    for analysis in analyses:
        status_emoji = "✓" if analysis["status"] == "completed" else "⋯"
        models_str = ", ".join(analysis.get("models", []))
        print(f"{status_emoji} {analysis['uuid']}")
        print(f"   Status: {analysis['status']}")
        print(f"   Models: {models_str}")
        print(f"   Credits: {analysis.get('credits_used', 0)}")
        print(f"   Responses: {analysis.get('response_count', 0)}")
        print(f"   Started: {analysis['started_at']}")
        if analysis.get('completed_at'):
            print(f"   Completed: {analysis['completed_at']}")
        print()

    # Show pagination
    if resp.get("cursor"):
        print(f"More results available. Use --cursor {resp['cursor']}")


def cmd_get_question_results(args):
    """Get analysis results for a specific question."""
    config = require_user_config()
    question_uuid = args.uuid

    # Build query params
    params = {}
    if args.fields:
        params["fields"] = args.fields

    resp, status = api_call(
        "GET",
        f"/questions/{question_uuid}/results",
        api_key=config["api_key"],
        params=params,
    )

    if status != HTTP_OK:
        print(f"Failed to get question results (HTTP {status}): {resp}", file=sys.stderr)
        sys.exit(1)

    # Display results
    print(json.dumps(resp, indent=2))


# --- Main ---


def main():
    parser = argparse.ArgumentParser(
        description="BotSee CLI — AI-powered competitive intelligence"
    )
    subparsers = parser.add_subparsers(dest="command")

    # High-level workflow commands
    status_parser = subparsers.add_parser("status", help="Show account status and balance")
    status_parser.add_argument("--limit", type=int, help="Max usage events to return")
    status_parser.add_argument("--cursor", help="Usage pagination cursor")
    status_parser.add_argument("--from", dest="from_time", help="Usage window start timestamp")
    status_parser.add_argument("--to", dest="to_time", help="Usage window end timestamp")

    usage_by_site_parser = subparsers.add_parser(
        "usage-by-site", help="Credit usage grouped by site (totals + breakdown)"
    )
    usage_by_site_parser.add_argument("--from", dest="from_time", help="Start date (ISO 8601)")
    usage_by_site_parser.add_argument("--to", dest="to_time", help="End date (ISO 8601)")
    usage_by_site_parser.add_argument("--site-uuid", help="Limit to one site")

    usage_line_items_parser = subparsers.add_parser(
        "usage-line-items", help="Individual paid operations, newest first"
    )
    usage_line_items_parser.add_argument("--from", dest="from_time", help="Start date (ISO 8601)")
    usage_line_items_parser.add_argument("--to", dest="to_time", help="End date (ISO 8601)")
    usage_line_items_parser.add_argument("--site-uuid", help="Limit to one site")
    usage_line_items_parser.add_argument("--category", help="Limit to one operation category")
    usage_line_items_parser.add_argument("--limit", type=int, help="Max line items (default 200)")

    subparsers.add_parser("account", help="Show account details (email, company)")

    signup_parser = subparsers.add_parser(
        "signup",
        help="Signup for BotSee with credit card",
    )
    signup_parser.add_argument("--email", help="Contact email (optional)")
    signup_parser.add_argument("--name", help="Contact name (optional)")
    signup_parser.add_argument("--company", help="Company name (optional)")
    signup_parser.add_argument("--api-key", help="API key if you already have one (skips signup flow)")
    signup_parser.add_argument("--webhook-url", help="Webhook URL for signup completion notification")
    signup_parser.add_argument(
        "--reset",
        action="store_true",
        help="Discard pending signup state and create a new signup link",
    )

    signup_usdc_parser = subparsers.add_parser(
        "signup-usdc",
        help="Signup for BotSee with USDC on Base",
    )
    signup_usdc_parser.add_argument("--email", help="Contact email (optional)")
    signup_usdc_parser.add_argument("--name", help="Contact name (optional)")
    signup_usdc_parser.add_argument("--company", help="Company name (optional)")
    signup_usdc_parser.add_argument(
        "--no-email",
        action="store_true",
        help="Skip email verification (for autonomous agent flows)",
    )

    signup_status_parser = subparsers.add_parser("signup-status", help="Check signup token status")
    signup_status_parser.add_argument("--token", help="Signup token (defaults to pending signup token)")

    revoke_api_key_parser = subparsers.add_parser(
        "revoke-api-key",
        help="Revoke an API key by ID",
    )
    revoke_api_key_parser.add_argument("--id", required=True, help="ID of the API key to revoke")

    reset_api_key_parser = subparsers.add_parser(
        "reset-api-key",
        help="Exchange a one-time reset token for a new API key",
    )
    reset_api_key_parser.add_argument("--token", required=True, help="Reset token from the BotSee web dashboard")

    rotate_api_key_parser = subparsers.add_parser(
        "rotate-api-key",
        help="Atomically rotate an API key (creates new key, revokes old one)",
    )
    rotate_api_key_parser.add_argument("--id", required=True, help="ID of the API key to rotate")

    signup_pay_usdc_parser = subparsers.add_parser(
        "signup-pay-usdc",
        help="Pay for USDC signup via x402 challenge",
    )
    signup_pay_usdc_parser.add_argument("--token", help="Signup token (defaults to pending signup token)")
    signup_pay_usdc_parser.add_argument(
        "--amount-cents",
        type=int,
        required=True,
        help=f"USD amount in cents ({USDC_MIN_CENTS}-{USDC_MAX_CENTS})",
    )
    signup_pay_usdc_parser.add_argument(
        "--payment",
        help="x402 payment-signature proof (omit to get 402 challenge)",
    )

    create_site_parser = subparsers.add_parser("create-site", help="Create site and generate content")
    create_site_parser.add_argument("domain", help="Website URL to analyze")
    create_site_parser.add_argument("--types", type=int, default=2, help="Number of customer types (default: 2)")
    create_site_parser.add_argument("--personas", type=int, default=2, help="Personas per customer type (default: 2)")
    create_site_parser.add_argument("--questions", type=int, default=5, help="Questions per persona (default: 5)")

    subparsers.add_parser("config-show", help="Display saved configuration")

    analyze_parser = subparsers.add_parser("analyze", help="Run competitive analysis")
    analyze_parser.add_argument("site_uuid", nargs="?", help="Site UUID (optional, defaults to active site)")
    analyze_parser.add_argument("--scope", help="Analysis scope (e.g. site)")
    analyze_parser.add_argument("--models", help="Comma-separated models (e.g. openai,claude,perplexity)")

    content_parser = subparsers.add_parser("content", help="Generate blog post from analysis")
    content_parser.add_argument("--question-uuid", help="Target question UUID for content generation")
    content_parser.add_argument("--provider", help="Preferred provider (e.g. gemini)")

    recommend_parser = subparsers.add_parser("recommend", help="Get AI recommendations to improve AI visibility")
    recommend_parser.add_argument("analysis_uuid", nargs="?", help="Analysis UUID (defaults to latest)")

    topup_usdc_parser = subparsers.add_parser(
        "topup-usdc",
        help="Add credits via USDC x402 challenge",
    )
    topup_usdc_parser.add_argument(
        "--amount-cents",
        type=int,
        required=True,
        help=f"USD amount in cents ({USDC_MIN_CENTS}-{USDC_MAX_CENTS})",
    )
    topup_usdc_parser.add_argument(
        "--payment",
        help="x402 payment-signature proof (omit to get 402 challenge)",
    )

    # Sites CRUD
    list_sites_parser = subparsers.add_parser("list-sites", help="List all sites")
    list_sites_parser.add_argument("--limit", type=int, help="Max sites to return")
    list_sites_parser.add_argument("--cursor", help="Pagination cursor")
    list_sites_parser.add_argument(
        "--include-archived",
        action="store_true",
        help="Include archived sites",
    )
    get_site_parser = subparsers.add_parser("get-site", help="Get site by UUID")
    get_site_parser.add_argument("uuid", help="Site UUID")

    archive_site_parser = subparsers.add_parser("archive-site", help="Archive a site")
    archive_site_parser.add_argument("uuid", help="Site UUID")

    use_site_parser = subparsers.add_parser("use-site", help="Switch active site")
    use_site_parser.add_argument("uuid", help="Site UUID")

    # Customer Types CRUD
    list_types_parser = subparsers.add_parser("list-types", help="List customer types")
    list_types_parser.add_argument("--site-uuid", help="Site UUID (defaults to config)")

    get_type_parser = subparsers.add_parser("get-type", help="Get customer type by UUID")
    get_type_parser.add_argument("uuid", help="Customer type UUID")

    create_type_parser = subparsers.add_parser("create-type", help="Create customer type (FREE)")
    create_type_parser.add_argument("site_uuid", help="Site UUID")
    create_type_parser.add_argument("--name", required=True, help="Type name")
    create_type_parser.add_argument("--description", help="Type description")

    gen_types_parser = subparsers.add_parser("generate-types", help="AI-generate types (5 credits each)")
    gen_types_parser.add_argument("--site-uuid", help="Site UUID (defaults to config)")
    gen_types_parser.add_argument("--count", type=int, default=2, help="Number to generate")

    update_type_parser = subparsers.add_parser("update-type", help="Update customer type")
    update_type_parser.add_argument("uuid", help="Customer type UUID")
    update_type_parser.add_argument("--name", help="New name")
    update_type_parser.add_argument("--description", help="New description")

    archive_type_parser = subparsers.add_parser("archive-type", help="Archive customer type")
    archive_type_parser.add_argument("uuid", help="Customer type UUID")

    # Personas CRUD
    list_personas_parser = subparsers.add_parser("list-personas", help="List personas for type")
    list_personas_parser.add_argument("type_uuid", help="Customer type UUID")

    get_persona_parser = subparsers.add_parser("get-persona", help="Get persona by UUID")
    get_persona_parser.add_argument("uuid", help="Persona UUID")

    create_persona_parser = subparsers.add_parser("create-persona", help="Create persona (FREE)")
    create_persona_parser.add_argument("type_uuid", help="Customer type UUID")
    create_persona_parser.add_argument("--name", required=True, help="Persona name")
    create_persona_parser.add_argument("--description", help="Persona description")

    gen_personas_parser = subparsers.add_parser("generate-personas", help="AI-generate personas (5 credits each)")
    gen_personas_parser.add_argument("type_uuid", help="Customer type UUID")
    gen_personas_parser.add_argument("--count", type=int, default=2, help="Number to generate")

    update_persona_parser = subparsers.add_parser("update-persona", help="Update persona")
    update_persona_parser.add_argument("uuid", help="Persona UUID")
    update_persona_parser.add_argument("--name", help="New name")
    update_persona_parser.add_argument("--description", help="New description")

    archive_persona_parser = subparsers.add_parser("archive-persona", help="Archive persona")
    archive_persona_parser.add_argument("uuid", help="Persona UUID")

    # Questions CRUD
    list_questions_parser = subparsers.add_parser("list-questions", help="List questions for persona")
    list_questions_parser.add_argument("persona_uuid", help="Persona UUID")

    get_question_parser = subparsers.add_parser("get-question", help="Get question by UUID")
    get_question_parser.add_argument("uuid", help="Question UUID")

    create_question_parser = subparsers.add_parser("create-question", help="Create question (FREE)")
    create_question_parser.add_argument("persona_uuid", help="Persona UUID")
    create_question_parser.add_argument("--text", required=True, help="Question text")

    gen_questions_parser = subparsers.add_parser("generate-questions", help="AI-generate questions (10 credits)")
    gen_questions_parser.add_argument("persona_uuid", help="Persona UUID")
    gen_questions_parser.add_argument("--count", type=int, default=5, help="Number to generate")

    update_question_parser = subparsers.add_parser("update-question", help="Update question")
    update_question_parser.add_argument("uuid", help="Question UUID")
    update_question_parser.add_argument("--text", help="New question text")
    update_question_parser.add_argument("--priority", help="Question priority")

    delete_question_parser = subparsers.add_parser("delete-question", help="Delete question (permanent)")
    delete_question_parser.add_argument("uuid", help="Question UUID")

    # Results commands
    results_comp_parser = subparsers.add_parser("results-competitors", help="Get competitors")
    results_comp_parser.add_argument("analysis_uuid", help="Analysis UUID")

    results_kw_parser = subparsers.add_parser("results-keywords", help="Get keywords")
    results_kw_parser.add_argument("analysis_uuid", help="Analysis UUID")

    results_src_parser = subparsers.add_parser("results-sources", help="Get sources")
    results_src_parser.add_argument("analysis_uuid", help="Analysis UUID")

    results_resp_parser = subparsers.add_parser("results-responses", help="Get raw responses")
    results_resp_parser.add_argument("analysis_uuid", help="Analysis UUID")

    results_kw_opp_parser = subparsers.add_parser("results-keyword-opportunities", help="Get keyword opportunities")
    results_kw_opp_parser.add_argument("analysis_uuid", help="Analysis UUID")
    results_kw_opp_parser.add_argument("--threshold", type=float, help="Mention rate threshold 0.0-1.0 (default 1.0)")
    results_kw_opp_parser.add_argument("--rank-threshold", dest="rank_threshold", type=int, help="Flag questions where brand ranked worse than this position")

    results_src_opp_parser = subparsers.add_parser("results-source-opportunities", help="Get source opportunities")
    results_src_opp_parser.add_argument("analysis_uuid", help="Analysis UUID")

    # Analysis listing
    list_analyses_parser = subparsers.add_parser("list-analyses", help="List analysis runs for a site")
    list_analyses_parser.add_argument("--site-uuid", help="Site UUID (defaults to active site)")
    list_analyses_parser.add_argument("--limit", type=int, help="Max results to return")
    list_analyses_parser.add_argument("--cursor", help="Pagination cursor")
    list_analyses_parser.add_argument("--persona-uuid", help="Filter by persona")
    list_analyses_parser.add_argument("--model", help="Filter by model")
    list_analyses_parser.add_argument("--from", dest="from_time", help="Filter start timestamp")
    list_analyses_parser.add_argument("--to", dest="to_time", help="Filter end timestamp")

    # Question results
    question_results_parser = subparsers.add_parser("get-question-results", help="Get analysis results for a specific question")
    question_results_parser.add_argument("uuid", help="Question UUID")
    question_results_parser.add_argument("--fields", help="Comma-separated fields: keywords,competitors,sources,responses")

    args = parser.parse_args()

    commands = {
        "status": cmd_status,
        "usage-by-site": cmd_usage_by_site,
        "usage-line-items": cmd_usage_line_items,
        "account": cmd_account,
        "signup": cmd_signup,
        "signup-usdc": cmd_signup_usdc,
        "signup-status": cmd_signup_status,
        "revoke-api-key": cmd_revoke_api_key,
        "reset-api-key": cmd_reset_api_key,
        "rotate-api-key": cmd_rotate_api_key,
        "signup-pay-usdc": cmd_signup_pay_usdc,
        "create-site": cmd_create_site,
        "config-show": cmd_config_show,
        "analyze": cmd_analyze,
        "content": cmd_content,
        "recommend": cmd_recommend,
        "topup-usdc": cmd_topup_usdc,
        "list-sites": cmd_list_sites,
        "get-site": cmd_get_site,
        "archive-site": cmd_archive_site,
        "use-site": cmd_use_site,
        "list-types": cmd_list_types,
        "get-type": cmd_get_type,
        "create-type": cmd_create_type,
        "generate-types": cmd_generate_types,
        "update-type": cmd_update_type,
        "archive-type": cmd_archive_type,
        "list-personas": cmd_list_personas,
        "get-persona": cmd_get_persona,
        "create-persona": cmd_create_persona,
        "generate-personas": cmd_generate_personas,
        "update-persona": cmd_update_persona,
        "archive-persona": cmd_archive_persona,
        "list-questions": cmd_list_questions,
        "get-question": cmd_get_question,
        "create-question": cmd_create_question,
        "generate-questions": cmd_generate_questions,
        "update-question": cmd_update_question,
        "delete-question": cmd_delete_question,
        "results-competitors": cmd_results_competitors,
        "results-keywords": cmd_results_keywords,
        "results-sources": cmd_results_sources,
        "results-responses": cmd_results_responses,
        "results-keyword-opportunities": cmd_results_keyword_opportunities,
        "results-source-opportunities": cmd_results_source_opportunities,
        "list-analyses": cmd_list_analyses,
        "get-question-results": cmd_get_question_results,
    }

    if args.command is None:
        cmd_status(args)
    elif args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
