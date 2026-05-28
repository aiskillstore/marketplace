#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""List or back up LabArchives notebooks with safe dry-run support."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

import yaml


def load_config(config_path: str = "config.yaml") -> dict:
    try:
        with open(config_path, "r", encoding="utf-8") as handle:
            config = yaml.safe_load(handle) or {}
    except FileNotFoundError as exc:
        raise RuntimeError(f"Configuration file not found: {config_path}. Run setup_config.py first.") from exc
    except Exception as exc:
        raise RuntimeError(f"Error loading configuration: {exc}") from exc

    required = ["api_url", "access_key_id", "access_password", "user_email", "user_external_password"]
    missing = [key for key in required if not config.get(key)]
    if missing:
        raise RuntimeError(f"Configuration is missing required fields: {', '.join(missing)}")
    return config


def init_client(config: dict):
    try:
        from labarchivespy.client import Client
    except ImportError as exc:
        raise RuntimeError(
            "labarchives-py package not installed. Install with: pip install git+https://github.com/mcmero/labarchives-py"
        ) from exc

    return Client(config["api_url"], config["access_key_id"], config["access_password"])


def get_user_id(client, config: dict) -> str:
    import xml.etree.ElementTree as ET

    response = client.make_call(
        "users",
        "user_access_info",
        params={"login_or_email": config["user_email"], "password": config["user_external_password"]},
    )
    if response.status_code != 200:
        raise RuntimeError(f"Authentication failed: HTTP {response.status_code}")
    return ET.fromstring(response.content)[0].text


def list_notebooks(client, uid: str) -> list[dict[str, str]]:
    import xml.etree.ElementTree as ET

    response = client.make_call("users", "user_access_info", params={"uid": uid})
    if response.status_code != 200:
        raise RuntimeError(f"Failed to list notebooks: HTTP {response.status_code}")

    root = ET.fromstring(response.content)
    notebooks = []
    for notebook in root.findall(".//notebook"):
        notebooks.append(
            {
                "nbid": notebook.findtext("nbid", default="N/A"),
                "name": notebook.findtext("name", default="Unnamed"),
                "role": notebook.findtext("role", default="N/A"),
            }
        )
    return notebooks


def backup_notebook(client, uid: str, nbid: str, output_dir: str, json_format: bool, no_attachments: bool) -> str:
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    response = client.make_call(
        "notebooks",
        "notebook_backup",
        params={
            "uid": uid,
            "nbid": nbid,
            "json": "true" if json_format else "false",
            "no_attachments": "true" if no_attachments else "false",
        },
    )
    if response.status_code != 200:
        raise RuntimeError(f"Backup failed: HTTP {response.status_code}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if no_attachments:
        ext = "json" if json_format else "xml"
        filename = f"notebook_{nbid}_{timestamp}.{ext}"
    else:
        filename = f"notebook_{nbid}_{timestamp}.7z"

    output_file = output_path / filename
    with open(output_file, "wb") as handle:
        handle.write(response.content)
    return str(output_file)


def run_dry(command: str, args: argparse.Namespace) -> int:
    print("DRY RUN")
    print(f"Command: {command}")
    if command == "list":
        print("Would authenticate with config and list accessible notebooks.")
    elif command == "backup":
        print(
            f"Would back up notebook {args.nbid} to {args.output} "
            f"(json={args.json}, no_attachments={args.no_attachments})."
        )
    elif command == "backup-all":
        print(
            f"Would back up all notebooks to {args.output} "
            f"(json={args.json}, no_attachments={args.no_attachments})."
        )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="LabArchives Notebook Operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--config", default="config.yaml", help="Path to configuration file.")
    parser.add_argument("--dry-run", action="store_true", help="Validate arguments without making network calls.")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    subparsers.add_parser("list", help="List all accessible notebooks")

    backup_parser = subparsers.add_parser("backup", help="Backup a specific notebook")
    backup_parser.add_argument("--nbid", required=True, help="Notebook ID to backup")
    backup_parser.add_argument("--output", default="backups", help="Output directory")
    backup_parser.add_argument("--json", action="store_true", help="Return data in JSON format")
    backup_parser.add_argument("--no-attachments", action="store_true", help="Exclude attachments from backup")

    backup_all_parser = subparsers.add_parser("backup-all", help="Backup all accessible notebooks")
    backup_all_parser.add_argument("--output", default="backups", help="Output directory")
    backup_all_parser.add_argument("--json", action="store_true", help="Return data in JSON format")
    backup_all_parser.add_argument("--no-attachments", action="store_true", help="Exclude attachments from backup")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 1
    if args.dry_run:
        return run_dry(args.command, args)

    try:
        config = load_config(args.config)
        client = init_client(config)
        uid = get_user_id(client, config)

        if args.command == "list":
            notebooks = list_notebooks(client, uid)
            if not notebooks:
                print("No notebooks found.")
                return 0
            print(f"{'Notebook ID':<15} {'Name':<40} {'Role':<10}")
            print("-" * 70)
            for notebook in notebooks:
                print(f"{notebook['nbid']:<15} {notebook['name']:<40} {notebook['role']:<10}")
            print(f"\nTotal notebooks: {len(notebooks)}")
            return 0

        if args.command == "backup":
            output_file = backup_notebook(client, uid, args.nbid, args.output, args.json, args.no_attachments)
            print(f"Backup saved: {output_file}")
            return 0

        notebooks = list_notebooks(client, uid)
        success_count = 0
        for notebook in notebooks:
            backup_notebook(client, uid, notebook["nbid"], args.output, args.json, args.no_attachments)
            success_count += 1
        print(f"Backed up {success_count} notebooks.")
        return 0

    except RuntimeError as exc:
        print(str(exc))
        return 1


if __name__ == "__main__":
    sys.exit(main())
