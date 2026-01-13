#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Read full content of a Gmail email.

Usage:
    gmail_read.py <1password-item> <email-id> [--folder INBOX]

Example:
    gmail_read.py "Gmail Work" "46"
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


def read_email(item_name: str, email_id: str, folder: str = "INBOX"):
    """Read full email content."""
    creds = get_credentials(item_name)

    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(creds["username"], creds["password"])
    mail.select(folder)

    _, msg_data = mail.fetch(email_id.encode(), "(RFC822)")
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

    # Get body
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                payload = part.get_payload(decode=True)
                charset = part.get_content_charset() or "utf-8"
                body = payload.decode(charset, errors="replace")
                break
            elif content_type == "text/html" and not body:
                payload = part.get_payload(decode=True)
                charset = part.get_content_charset() or "utf-8"
                body = payload.decode(charset, errors="replace")
    else:
        payload = msg.get_payload(decode=True)
        charset = msg.get_content_charset() or "utf-8"
        body = payload.decode(charset, errors="replace")

    mail.logout()

    return {
        "id": email_id,
        "from": from_addr,
        "to": msg["To"],
        "subject": subject,
        "date": msg["Date"],
        "message_id": msg["Message-ID"],
        "body": body,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Read email content")
    parser.add_argument("item_name", help="1Password item name")
    parser.add_argument("email_id", help="Email ID to read")
    parser.add_argument(
        "--folder", "-f", default="INBOX", help="Folder containing the email"
    )
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    e = read_email(args.item_name, args.email_id, args.folder)

    if args.json:
        print(json.dumps(e, indent=2, ensure_ascii=False))
    else:
        print(f"From: {e['from']}")
        print(f"To: {e['to']}")
        print(f"Subject: {e['subject']}")
        print(f"Date: {e['date']}")
        print("=" * 50)
        print(e["body"])
