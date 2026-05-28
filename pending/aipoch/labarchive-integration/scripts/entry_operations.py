#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Create entries or upload attachments to LabArchives with dry-run support."""

from __future__ import annotations

import argparse
import sys
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


def create_entry(client, uid: str, nbid: str, title: str, content: str | None = None, date: str | None = None):
    params = {"uid": uid, "nbid": nbid, "title": title}
    if content:
        params["content"] = content if content.startswith("<") else f"<p>{content}</p>"
    if date:
        params["date"] = date

    response = client.make_call("entries", "create_entry", params=params)
    if response.status_code != 200:
        raise RuntimeError(f"Entry creation failed: HTTP {response.status_code}")

    try:
        import xml.etree.ElementTree as ET

        root = ET.fromstring(response.content)
        return root.findtext(".//entry_id", default="created")
    except Exception:
        return "created"


def create_comment(client, uid: str, nbid: str, entry_id: str, comment: str) -> None:
    response = client.make_call(
        "entries",
        "create_comment",
        params={"uid": uid, "nbid": nbid, "entry_id": entry_id, "comment": comment},
    )
    if response.status_code != 200:
        raise RuntimeError(f"Comment creation failed: HTTP {response.status_code}")


def upload_attachment(client, config: dict, uid: str, nbid: str, entry_id: str, file_path: str) -> None:
    import requests

    attachment = Path(file_path)
    if not attachment.exists():
        raise RuntimeError(f"File not found: {attachment}")

    with open(attachment, "rb") as handle:
        response = requests.post(
            f"{config['api_url']}/entries/upload_attachment",
            files={"file": handle},
            data={
                "uid": uid,
                "nbid": nbid,
                "entry_id": entry_id,
                "filename": attachment.name,
                "access_key_id": config["access_key_id"],
                "access_password": config["access_password"],
            },
        )

    if response.status_code != 200:
        raise RuntimeError(f"Upload failed: HTTP {response.status_code}")


def batch_upload(client, config: dict, uid: str, nbid: str, entry_id: str, directory: str) -> tuple[int, int]:
    source_dir = Path(directory)
    if not source_dir.is_dir():
        raise RuntimeError(f"Directory not found: {source_dir}")

    files = [item for item in source_dir.glob("*") if item.is_file()]
    if not files:
        raise RuntimeError(f"No files found in {source_dir}")

    success_count = 0
    failure_count = 0
    for item in files:
        try:
            upload_attachment(client, config, uid, nbid, entry_id, str(item))
            success_count += 1
        except RuntimeError:
            failure_count += 1
    return success_count, failure_count


def run_dry(args: argparse.Namespace) -> int:
    print("DRY RUN")
    print(f"Command: {args.command}")
    if args.command == "create":
        print(f"Would create entry '{args.title}' in notebook {args.nbid}.")
    elif args.command == "upload":
        print(f"Would upload file {args.file} to entry {args.entry_id} in notebook {args.nbid}.")
    elif args.command == "batch-upload":
        print(f"Would upload all files from {args.directory} to entry {args.entry_id} in notebook {args.nbid}.")
    elif args.command == "comment":
        print(f"Would add a comment to entry {args.entry_id} in notebook {args.nbid}.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="LabArchives Entry Operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--config", default="config.yaml", help="Path to configuration file.")
    parser.add_argument("--nbid", required=True, help="Notebook ID")
    parser.add_argument("--dry-run", action="store_true", help="Validate arguments without making network calls.")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    create_parser = subparsers.add_parser("create", help="Create new entry")
    create_parser.add_argument("--title", required=True, help="Entry title")
    create_parser.add_argument("--content", help="Entry content (HTML supported)")
    create_parser.add_argument("--date", help="Entry date (YYYY-MM-DD)")
    create_parser.add_argument("--attachments", nargs="+", help="Files to attach to the new entry")

    upload_parser = subparsers.add_parser("upload", help="Upload attachment to entry")
    upload_parser.add_argument("--entry-id", required=True, help="Entry ID")
    upload_parser.add_argument("--file", required=True, help="File to upload")

    batch_parser = subparsers.add_parser("batch-upload", help="Upload all files from directory")
    batch_parser.add_argument("--entry-id", required=True, help="Entry ID")
    batch_parser.add_argument("--directory", required=True, help="Directory containing files to upload")

    comment_parser = subparsers.add_parser("comment", help="Add comment to entry")
    comment_parser.add_argument("--entry-id", required=True, help="Entry ID")
    comment_parser.add_argument("--text", required=True, help="Comment text")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 1
    if args.dry_run:
        return run_dry(args)

    try:
        config = load_config(args.config)
        client = init_client(config)
        uid = get_user_id(client, config)

        if args.command == "create":
            entry_id = create_entry(client, uid, args.nbid, args.title, args.content, args.date)
            print(f"Entry created: {entry_id}")
            if args.attachments:
                for attachment in args.attachments:
                    upload_attachment(client, config, uid, args.nbid, entry_id, attachment)
                print(f"Uploaded {len(args.attachments)} attachment(s).")
            return 0

        if args.command == "upload":
            upload_attachment(client, config, uid, args.nbid, args.entry_id, args.file)
            print("Attachment uploaded successfully.")
            return 0

        if args.command == "batch-upload":
            success_count, failure_count = batch_upload(client, config, uid, args.nbid, args.entry_id, args.directory)
            print(f"Batch upload complete: {success_count} successful, {failure_count} failed.")
            return 0

        create_comment(client, uid, args.nbid, args.entry_id, args.text)
        print("Comment added successfully.")
        return 0

    except RuntimeError as exc:
        print(str(exc))
        return 1


if __name__ == "__main__":
    sys.exit(main())
