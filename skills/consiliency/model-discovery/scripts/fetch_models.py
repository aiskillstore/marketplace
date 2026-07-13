#!/usr/bin/env python3
"""Fetch model lists from all configured AI providers.

Usage:
    python fetch_models.py                  # Fetch all providers
    python fetch_models.py --provider anthropic  # Fetch specific provider
    python fetch_models.py --force          # Ignore cache, always fetch
    python fetch_models.py --cache-only     # Only read from cache
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

# Load environment variables from .env file
# Searches current directory and parent directories for .env
try:
    from dotenv import load_dotenv

    # Find project root by looking for .env file
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        env_file = parent / ".env"
        if env_file.exists():
            load_dotenv(env_file)
            break
    else:
        # Fall back to default behavior (loads from cwd)
        load_dotenv()
except ImportError:
    # python-dotenv not installed, rely on environment variables
    pass

# Configuration
CACHE_DIR = Path(__file__).parent.parent / "cache"
CACHE_FILE = CACHE_DIR / "models.json"
CACHE_TTL_HOURS = 24

# Provider settings (loaded from .env or environment)
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")


def is_cache_fresh() -> bool:
    """Check if cache exists and is within TTL."""
    if not CACHE_FILE.exists():
        return False

    try:
        data = json.loads(CACHE_FILE.read_text())
        fetched_at = datetime.fromisoformat(data.get("fetched_at", ""))
        return datetime.now(timezone.utc) - fetched_at < timedelta(hours=CACHE_TTL_HOURS)
    except (json.JSONDecodeError, ValueError):
        return False


def read_cache() -> dict[str, Any] | None:
    """Read cached model data if available."""
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text())
        except json.JSONDecodeError:
            return None
    return None


def fetch_anthropic() -> list[dict] | dict:
    """Fetch Anthropic Claude models."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return {"error": "ANTHROPIC_API_KEY not set"}

    try:
        result = subprocess.run(
            [
                "curl", "-s", "https://api.anthropic.com/v1/models",
                "-H", f"x-api-key: {api_key}",
                "-H", "anthropic-version: 2023-06-01"
            ],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            return {"error": f"curl failed: {result.stderr}"}

        data = json.loads(result.stdout)

        if "error" in data:
            return {"error": data["error"].get("message", str(data["error"]))}

        return [
            {
                "id": m["id"],
                "name": m.get("display_name", m["id"]),
                "created_at": m.get("created_at")
            }
            for m in data.get("data", [])
        ]
    except subprocess.TimeoutExpired:
        return {"error": "Request timed out"}
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON response: {e}"}
    except Exception as e:
        return {"error": str(e)}


def fetch_openai() -> list[dict] | dict:
    """Fetch OpenAI GPT models."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return {"error": "OPENAI_API_KEY not set"}

    try:
        result = subprocess.run(
            [
                "curl", "-s", "https://api.openai.com/v1/models",
                "-H", f"Authorization: Bearer {api_key}"
            ],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            return {"error": f"curl failed: {result.stderr}"}

        data = json.loads(result.stdout)

        if "error" in data:
            return {"error": data["error"].get("message", str(data["error"]))}

        # Filter to GPT-5.2 family only
        gpt_models = [
            m for m in data.get("data", [])
            if m["id"].startswith("gpt-5.2")
        ]

        return [
            {
                "id": m["id"],
                "name": m["id"],
                "owned_by": m.get("owned_by"),
                "created": m.get("created")
            }
            for m in gpt_models
        ]
    except subprocess.TimeoutExpired:
        return {"error": "Request timed out"}
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON response: {e}"}
    except Exception as e:
        return {"error": str(e)}


def fetch_gemini() -> list[dict] | dict:
    """Fetch Google Gemini models."""
    # Try GOOGLE_API_KEY first (matches .env.sample), fall back to GEMINI_API_KEY
    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {"error": "GOOGLE_API_KEY not set (also checked GEMINI_API_KEY)"}

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        result = subprocess.run(
            ["curl", "-s", url],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            return {"error": f"curl failed: {result.stderr}"}

        data = json.loads(result.stdout)

        if "error" in data:
            return {"error": data["error"].get("message", str(data["error"]))}

        return [
            {
                "id": m["name"],
                "name": m.get("displayName", m["name"]),
                "input_token_limit": m.get("inputTokenLimit"),
                "output_token_limit": m.get("outputTokenLimit"),
                "methods": m.get("supportedGenerationMethods", [])
            }
            for m in data.get("models", [])
        ]
    except subprocess.TimeoutExpired:
        return {"error": "Request timed out"}
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON response: {e}"}
    except Exception as e:
        return {"error": str(e)}


def fetch_ollama() -> list[dict] | dict:
    """Fetch local Ollama models."""
    try:
        result = subprocess.run(
            ["curl", "-s", f"{OLLAMA_HOST}/api/tags"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode != 0:
            return {"error": f"curl failed: {result.stderr}"}

        if not result.stdout.strip():
            return {"error": "Empty response - is Ollama running?"}

        data = json.loads(result.stdout)

        return [
            {
                "id": m["name"],
                "name": m["name"],
                "size_gb": round(m.get("size", 0) / 1073741824, 1),
                "modified_at": m.get("modified_at"),
                "parameter_size": m.get("details", {}).get("parameter_size"),
                "quantization": m.get("details", {}).get("quantization_level")
            }
            for m in data.get("models", [])
        ]
    except subprocess.TimeoutExpired:
        return {"error": f"Connection timed out - is Ollama running at {OLLAMA_HOST}?"}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response from Ollama"}
    except Exception as e:
        return {"error": str(e)}


PROVIDERS = {
    "anthropic": fetch_anthropic,
    "openai": fetch_openai,
    "gemini": fetch_gemini,
    "ollama": fetch_ollama,
}


def fetch_all(providers: list[str] | None = None) -> dict:
    """Fetch models from all or specified providers."""
    providers = providers or list(PROVIDERS.keys())

    result = {
        "fetched_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "providers": {}
    }

    for name in providers:
        if name in PROVIDERS:
            result["providers"][name] = PROVIDERS[name]()

    return result


def save_cache(data: dict) -> None:
    """Save model data to cache file."""
    CACHE_DIR.mkdir(exist_ok=True)
    CACHE_FILE.write_text(json.dumps(data, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Fetch AI model lists from providers")
    parser.add_argument(
        "--provider", "-p",
        choices=list(PROVIDERS.keys()),
        help="Fetch from specific provider only"
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Ignore cache, always fetch fresh data"
    )
    parser.add_argument(
        "--cache-only", "-c",
        action="store_true",
        help="Only read from cache, don't fetch"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress status messages"
    )
    parser.add_argument(
        "--check-new",
        action="store_true",
        help="After fetching, check for new unclassified models"
    )

    args = parser.parse_args()

    # Cache-only mode
    if args.cache_only:
        cached = read_cache()
        if cached:
            print(json.dumps(cached, indent=2))
            return 0
        else:
            if not args.quiet:
                print("No cache available", file=sys.stderr)
            return 1

    # Check cache unless forced
    if not args.force and is_cache_fresh():
        cached = read_cache()
        if cached:
            if not args.quiet:
                print(f"Using cached data from {cached.get('fetched_at', 'unknown')}", file=sys.stderr)
            print(json.dumps(cached, indent=2))
            return 0

    # Fetch fresh data
    providers = [args.provider] if args.provider else None
    if not args.quiet:
        provider_str = args.provider or "all providers"
        print(f"Fetching models from {provider_str}...", file=sys.stderr)

    data = fetch_all(providers)

    # Save to cache
    save_cache(data)

    # Output
    print(json.dumps(data, indent=2))

    # Report any errors
    errors = [
        f"{name}: {info['error']}"
        for name, info in data["providers"].items()
        if isinstance(info, dict) and "error" in info
    ]
    if errors and not args.quiet:
        print("\nErrors:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)

    # Check for new models if requested
    if args.check_new:
        try:
            from check_new_models import detect_new_models, generate_report
            new_models = detect_new_models(provider=args.provider, use_cache=True)
            if new_models:
                total = sum(len(m) for m in new_models.values())
                print(f"\n⚠️  {total} NEW MODEL(S) DETECTED - run check_new_models.py to classify", file=sys.stderr)
                for provider, models in new_models.items():
                    print(f"  {provider}:", file=sys.stderr)
                    for m in models[:5]:
                        hint = f" (suggested: {m['inferred_tier']})" if m.get('inferred_tier') else " ⚡ NEEDS CLASSIFICATION"
                        print(f"    - {m['id']}{hint}", file=sys.stderr)
                    if len(models) > 5:
                        print(f"    ... and {len(models) - 5} more", file=sys.stderr)
        except ImportError:
            pass  # check_new_models not available

    return 0


if __name__ == "__main__":
    sys.exit(main())
