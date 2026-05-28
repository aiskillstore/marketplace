#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Create and validate a LabArchives configuration file."""

from __future__ import annotations

import os
from pathlib import Path

import yaml


def get_regional_endpoint() -> str:
    print("\nSelect your regional API endpoint:")
    print("1. US/International")
    print("2. Australia")
    print("3. UK")
    print("4. Custom endpoint")

    choice = input("\nEnter choice (1-4): ").strip()
    endpoints = {
        "1": "https://api.labarchives.com/api",
        "2": "https://auapi.labarchives.com/api",
        "3": "https://ukapi.labarchives.com/api",
    }

    if choice in endpoints:
        return endpoints[choice]
    if choice == "4":
        return input("Enter custom API endpoint URL: ").strip()

    print("Warning: invalid choice. Defaulting to US/International.")
    return endpoints["1"]


def get_credentials() -> dict[str, str]:
    print("\n" + "=" * 60)
    print("LabArchives API Credentials")
    print("=" * 60)
    print("You need both institutional API credentials and a user external-app password.\n")

    access_key_id = input("Access Key ID: ").strip()
    access_password = input("Access Password: ").strip()
    user_email = input("LabArchives email: ").strip()
    user_password = input("External Applications Password: ").strip()

    return {
        "access_key_id": access_key_id,
        "access_password": access_password,
        "user_email": user_email,
        "user_external_password": user_password,
    }


def create_config_file(config_data: dict[str, str], output_path: str = "config.yaml") -> None:
    with open(output_path, "w", encoding="utf-8") as handle:
        yaml.safe_dump(config_data, handle, default_flow_style=False, sort_keys=False, allow_unicode=True)

    try:
        os.chmod(output_path, 0o600)
    except OSError:
        pass

    print(f"\nConfiguration saved to: {os.path.abspath(output_path)}")


def verify_config(config_path: str = "config.yaml") -> bool:
    try:
        with open(config_path, "r", encoding="utf-8") as handle:
            config = yaml.safe_load(handle) or {}
    except Exception as exc:
        print(f"Error verifying configuration: {exc}")
        return False

    required_keys = [
        "api_url",
        "access_key_id",
        "access_password",
        "user_email",
        "user_external_password",
    ]
    missing = [key for key in required_keys if not config.get(key)]
    if missing:
        print(f"Warning: missing required fields: {', '.join(missing)}")
        return False

    print("Configuration file verified successfully.")
    return True


def main() -> None:
    print("=" * 60)
    print("LabArchives API Configuration Setup")
    print("=" * 60)

    config_path = Path("config.yaml")
    if config_path.exists():
        overwrite = input("config.yaml already exists. Overwrite? (y/n): ").strip().lower()
        if overwrite != "y":
            print("Setup cancelled.")
            return

    config_data = {
        "api_url": get_regional_endpoint(),
        **get_credentials(),
    }
    create_config_file(config_data)
    verify_config()

    print("\nNext steps:")
    print("1. Keep config.yaml out of version control.")
    print("2. Run notebook_operations.py --dry-run <command> first.")
    print("3. Generate writing outputs only from authorized notebook data.")


if __name__ == "__main__":
    main()
