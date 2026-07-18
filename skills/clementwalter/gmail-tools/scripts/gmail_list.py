#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""List recent emails from a Gmail account.

Usage:
    gmail_list.py <1password-item> [--limit 20] [--folder INBOX]

Example:
    gmail_list.py "Gmail Work" --limit 10
"""

import argparse
import email
import imaplib
import json
import subprocess
from email.header import decode_header


def get_credentials(item_name: str) -> dict:
    """Get username and password from 1Password item."""
    result = subprocess.run(
        ["op", "item", "get", item_name, "--format", "json"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise Exception(f"Failed to get 1Password item: {result.stderr}")

    item = json.loads(result.stdout)
    creds = {"username": None, "password": None}

    for field in item.get("fields", []):
        if field.get("id") == "username" or field.get("label") == "username":
            creds["username"] = field.get("value")
        elif field.get("id") == "password" or field.get("label") == "password":
            creds["password"] = field.get("value")

    return creds


def list_emails(item_name: str, limit: int = 20, folder: str = "INBOX"):
    """List recent emails."""
    creds = get_credentials(item_name)

    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(creds["username"], creds["password"])
    mail.select(folder)

    _, messages = mail.search(None, "ALL")
    email_ids = messages[0].split()

    results = []
    for eid in email_ids[-limit:][::-1]:
        _, msg_data = mail.fetch(eid, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])

        subject = decode_header(msg["Subject"])[0]
        subject = (
            subject[0].decode(subject[1] or "utf-8")
            if isinstance(subject[0], bytes)
            else subject[0]
        )

        from_header = decode_header(msg["From"])[0]
        from_addr = (
            from_header[0].decode(from_header[1] or "utf-8")
            if isinstance(from_header[0], bytes)
            else from_header[0]
        )

        results.append(
            {
                "id": eid.decode(),
                "from": from_addr,
                "subject": subject,
                "date": msg["Date"],
            }
        )

    mail.logout()
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="List recent emails")
    parser.add_argument("item_name", help="1Password item name")
    parser.add_argument(
        "--limit", "-l", type=int, default=20, help="Max emails to return"
    )
    parser.add_argument(
        "--folder", "-f", default="INBOX", help="Folder to list (default: INBOX)"
    )
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    emails = list_emails(args.item_name, args.limit, args.folder)

    if args.json:
        print(json.dumps(emails, indent=2, ensure_ascii=False))
    else:
        for e in emails:
            print(f"ID: {e['id']}")
            print(f"From: {e['from']}")
            print(f"Subject: {e['subject']}")
            print(f"Date: {e['date']}")
            print("-" * 50)
