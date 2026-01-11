#!/usr/bin/env python3
"""Check for new models and prompt user for tier assignment.

Usage:
    python check_new_models.py              # Check all providers, interactive
    python check_new_models.py --provider anthropic  # Check specific provider
    python check_new_models.py --json       # Output JSON for agent consumption
    python check_new_models.py --auto       # Auto-classify using patterns (no prompt)
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Import fetch_models functions
from fetch_models import fetch_all, read_cache, CACHE_FILE

# Configuration
CONFIG_DIR = Path(__file__).parent.parent / "config"
KNOWN_MODELS_FILE = CONFIG_DIR / "known_models.json"
MODEL_TIERS_FILE = CONFIG_DIR / "model_tiers.json"


def load_known_models() -> dict[str, Any]:
    """Load the known models registry."""
    if KNOWN_MODELS_FILE.exists():
        return json.loads(KNOWN_MODELS_FILE.read_text())
    return {"known_models": {}, "excluded_patterns": []}


def load_model_tiers() -> dict[str, Any]:
    """Load the model tiers configuration."""
    if MODEL_TIERS_FILE.exists():
        return json.loads(MODEL_TIERS_FILE.read_text())
    return {"model_patterns": {"tier_inference": {}}}


def save_known_models(data: dict) -> None:
    """Save the known models registry."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    data["last_api_query"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    KNOWN_MODELS_FILE.write_text(json.dumps(data, indent=2))


def is_excluded(model_id: str, patterns: list[str]) -> bool:
    """Check if a model matches any exclusion pattern."""
    for pattern in patterns:
        if re.search(pattern, model_id, re.IGNORECASE):
            return True
    return False


def infer_tier(model_id: str, patterns: dict) -> str | None:
    """Try to infer tier from model name using patterns."""
    tier_patterns = patterns.get("tier_inference", {})

    # Check heavy patterns first (more specific)
    for pattern in tier_patterns.get("heavy_patterns", []):
        if pattern in model_id.lower():
            return "heavy"

    # Check fast patterns
    for pattern in tier_patterns.get("fast_patterns", []):
        if pattern in model_id.lower():
            return "fast"

    # Check default patterns (regex)
    for pattern in tier_patterns.get("default_patterns", []):
        if re.search(pattern, model_id, re.IGNORECASE):
            return "default"

    return None


def detect_new_models(
    provider: str | None = None,
    use_cache: bool = True
) -> dict[str, list[dict]]:
    """Detect new models not in the known models registry.

    Returns dict of provider -> list of new model info dicts.
    """
    known_data = load_known_models()
    tiers_data = load_model_tiers()
    excluded_patterns = known_data.get("excluded_patterns", [])
    model_patterns = tiers_data.get("model_patterns", {})

    # Get current models from API or cache
    if use_cache:
        current_data = read_cache()
        if not current_data:
            current_data = fetch_all([provider] if provider else None)
    else:
        current_data = fetch_all([provider] if provider else None)

    new_models: dict[str, list[dict]] = {}

    providers_to_check = [provider] if provider else list(current_data.get("providers", {}).keys())

    for prov in providers_to_check:
        provider_models = current_data.get("providers", {}).get(prov, [])

        # Skip if error response
        if isinstance(provider_models, dict) and "error" in provider_models:
            continue

        known_provider = known_data.get("known_models", {}).get(prov, {})
        known_ids = set(known_provider.get("models", {}).keys())

        new_for_provider = []

        for model in provider_models:
            model_id = model.get("id", "")

            # Skip if already known
            if model_id in known_ids:
                continue

            # Skip if matches exclusion pattern
            if is_excluded(model_id, excluded_patterns):
                continue

            # Try to infer tier
            inferred_tier = infer_tier(model_id, model_patterns)

            new_for_provider.append({
                "id": model_id,
                "name": model.get("name", model_id),
                "inferred_tier": inferred_tier,
                "created_at": model.get("created_at") or model.get("created"),
                "raw": model
            })

        if new_for_provider:
            new_models[prov] = new_for_provider

    return new_models


def prompt_tier_assignment(model: dict, provider: str) -> str | None:
    """Interactively prompt user for tier assignment."""
    print(f"\n{'='*60}")
    print(f"NEW MODEL DETECTED: {provider}")
    print(f"{'='*60}")
    print(f"  ID:   {model['id']}")
    print(f"  Name: {model['name']}")
    if model.get('created_at'):
        print(f"  Created: {model['created_at']}")
    if model.get('inferred_tier'):
        print(f"  Suggested tier: {model['inferred_tier']} (auto-detected)")
    print()
    print("Available tiers:")
    print("  [f] fast    - Speed/cost optimized, simple tasks")
    print("  [d] default - Balanced, general purpose")
    print("  [h] heavy   - Maximum capability, complex reasoning")
    print("  [s] skip    - Exclude this model (specialty/not for coding)")
    print("  [q] quit    - Stop processing")
    print()

    while True:
        default = model.get('inferred_tier', 'd')[0] if model.get('inferred_tier') else 'd'
        choice = input(f"Assign tier [{default}]: ").strip().lower() or default

        if choice in ('f', 'fast'):
            return "fast"
        elif choice in ('d', 'default'):
            return "default"
        elif choice in ('h', 'heavy'):
            return "heavy"
        elif choice in ('s', 'skip'):
            return None
        elif choice in ('q', 'quit'):
            raise KeyboardInterrupt
        else:
            print("Invalid choice. Please enter f, d, h, s, or q.")


def update_known_models(provider: str, model_id: str, tier: str) -> None:
    """Add a model to the known models registry."""
    data = load_known_models()

    if provider not in data.get("known_models", {}):
        data.setdefault("known_models", {})[provider] = {"models": {}}

    data["known_models"][provider]["models"][model_id] = {
        "tier": tier,
        "added": datetime.now(timezone.utc).strftime("%Y-%m-%d")
    }
    data["known_models"][provider]["last_checked"] = (
        datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    )

    save_known_models(data)


def generate_report(new_models: dict[str, list[dict]], json_output: bool = False) -> dict:
    """Generate a report of new models for agent consumption."""
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "has_new_models": bool(new_models),
        "total_new": sum(len(models) for models in new_models.values()),
        "by_provider": {}
    }

    for provider, models in new_models.items():
        report["by_provider"][provider] = {
            "count": len(models),
            "models": [
                {
                    "id": m["id"],
                    "name": m["name"],
                    "inferred_tier": m.get("inferred_tier"),
                    "needs_classification": m.get("inferred_tier") is None
                }
                for m in models
            ]
        }

    if json_output:
        print(json.dumps(report, indent=2))

    return report


def main():
    parser = argparse.ArgumentParser(description="Check for new AI models and assign tiers")
    parser.add_argument(
        "--provider", "-p",
        choices=["anthropic", "openai", "gemini", "ollama"],
        help="Check specific provider only"
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output JSON report (for agent consumption)"
    )
    parser.add_argument(
        "--auto", "-a",
        action="store_true",
        help="Auto-classify using patterns, no interactive prompts"
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Don't save changes, just report"
    )
    parser.add_argument(
        "--refresh", "-r",
        action="store_true",
        help="Fetch fresh data from APIs (ignore cache)"
    )

    args = parser.parse_args()

    # Detect new models
    new_models = detect_new_models(
        provider=args.provider,
        use_cache=not args.refresh
    )

    # JSON output mode (for agents)
    if args.json:
        generate_report(new_models, json_output=True)
        return 0 if not new_models else 1  # Exit 1 if new models need attention

    # No new models
    if not new_models:
        print("No new models detected. All models are classified.")
        return 0

    # Report new models
    total = sum(len(m) for m in new_models.values())
    print(f"\nFound {total} new model(s) across {len(new_models)} provider(s):\n")

    for provider, models in new_models.items():
        print(f"  {provider}: {len(models)} new")
        for m in models[:3]:  # Show first 3
            tier_hint = f" (suggested: {m['inferred_tier']})" if m.get('inferred_tier') else ""
            print(f"    - {m['id']}{tier_hint}")
        if len(models) > 3:
            print(f"    ... and {len(models) - 3} more")

    # Auto mode - use inferred tiers
    if args.auto:
        print("\n[Auto mode] Classifying models using pattern matching...")
        classified = 0
        skipped = 0

        for provider, models in new_models.items():
            for model in models:
                if model.get('inferred_tier'):
                    if not args.dry_run:
                        update_known_models(provider, model['id'], model['inferred_tier'])
                    classified += 1
                    print(f"  {model['id']} -> {model['inferred_tier']}")
                else:
                    skipped += 1
                    print(f"  {model['id']} -> SKIPPED (no pattern match)")

        print(f"\nClassified: {classified}, Skipped: {skipped}")
        if skipped > 0:
            print("Run without --auto to manually classify skipped models.")
        return 0

    # Interactive mode
    print("\nStarting interactive classification...\n")

    try:
        for provider, models in new_models.items():
            for model in models:
                tier = prompt_tier_assignment(model, provider)

                if tier and not args.dry_run:
                    update_known_models(provider, model['id'], tier)
                    print(f"  -> Saved: {model['id']} as {tier}")
                elif tier:
                    print(f"  -> Would save: {model['id']} as {tier} (dry-run)")
                else:
                    print(f"  -> Skipped: {model['id']}")

    except KeyboardInterrupt:
        print("\n\nClassification interrupted. Progress saved.")
        return 1

    print("\nClassification complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
