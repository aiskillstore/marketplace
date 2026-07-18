#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Reply to a Gmail email with proper threading and attachment support.

Usage:
    gmail_reply.py <1password-item> <email-id> --body "Message" [--attachment file.pdf] [--dry-run]

Example:
    gmail_reply.py "Gmail Work" "46" --body "Thanks for your email." --attachment ~/doc.pdf
"""

import argparse
import email
import imaplib
import json
import os
import smtplib
import subprocess
from email import encoders
from email.header import decode_header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


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


def get_email_for_reply(item_name: str, email_id: str, folder: str = "INBOX"):
    """Get email details needed for reply (headers for threading)."""
    creds = get_credentials(item_name)

    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(creds["username"], creds["password"])
    mail.select(folder)

    _, msg_data = mail.fetch(email_id.encode(), "(RFC822)")
    msg = email.message_from_bytes(msg_data[0][1])

    # Decode subject
    subject = decode_header(msg["Subject"])[0]
    subject = (
        subject[0].decode(subject[1] or "utf-8")
        if isinstance(subject[0], bytes)
        else subject[0]
    )

    # Get From for Reply-To
    from_header = decode_header(msg["From"])[0]
    from_addr = (
        from_header[0].decode(from_header[1] or "utf-8")
        if isinstance(from_header[0], bytes)
        else from_header[0]
    )

    # Extract just the email address from "Name <email>" format
    if "<" in from_addr and ">" in from_addr:
        reply_to = from_addr[from_addr.index("<") + 1 : from_addr.index(">")]
    else:
        reply_to = from_addr

    mail.logout()

    return {
        "message_id": msg["Message-ID"],
        "references": msg["References"] or "",
        "subject": subject,
        "reply_to": reply_to,
        "from": from_addr,
    }


def send_reply(
    item_name: str,
    email_id: str,
    body: str,
    attachments: list = None,
    folder: str = "INBOX",
):
    """Send a reply to an email, maintaining the thread."""
    creds = get_credentials(item_name)

    # Get original email details for threading
    original = get_email_for_reply(item_name, email_id, folder)

    # Build references header (original references + original message-id)
    references = original["references"]
    if references:
        references = f"{references} {original['message_id']}"
    else:
        references = original["message_id"]

    # Prepare subject (add RE: if not present)
    subject = original["subject"]
    if not subject.upper().startswith("RE:"):
        subject = f"RE: {subject}"

    # Create message
    if attachments:
        msg = MIMEMultipart()
        msg.attach(MIMEText(body, "plain", "utf-8"))

        for filepath in attachments:
            if os.path.exists(filepath):
                with open(filepath, "rb") as f:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(f.read())
                encoders.encode_base64(part)
                filename = os.path.basename(filepath)
                part.add_header(
                    "Content-Disposition", f"attachment; filename={filename}"
                )
                msg.attach(part)
    else:
        msg = MIMEText(body, "plain", "utf-8")

    msg["From"] = creds["username"]
    msg["To"] = original["reply_to"]
    msg["Subject"] = subject
    msg["In-Reply-To"] = original["message_id"]
    msg["References"] = references

    # Send via SMTP
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(creds["username"], creds["password"])
        server.send_message(msg)

    return {
        "status": "sent",
        "to": original["reply_to"],
        "subject": subject,
        "attachments": [os.path.basename(a) for a in (attachments or [])],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reply to an email")
    parser.add_argument("item_name", help="1Password item name")
    parser.add_argument("email_id", help="Email ID to reply to")
    parser.add_argument("--body", "-b", required=True, help="Reply body text")
    parser.add_argument(
        "--attachment",
        "-a",
        action="append",
        help="File to attach (can be used multiple times)",
    )
    parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="Show what would be sent without sending",
    )
    parser.add_argument(
        "--folder", "-f", default="INBOX", help="Folder containing the email"
    )

    args = parser.parse_args()

    if args.dry_run:
        original = get_email_for_reply(args.item_name, args.email_id, args.folder)
        subject = original["subject"]
        if not subject.upper().startswith("RE:"):
            subject = f"RE: {subject}"
        print("=== DRY RUN - Email would be sent as follows ===")
        print(f"To: {original['reply_to']}")
        print(f"Subject: {subject}")
        print(f"In-Reply-To: {original['message_id']}")
        print(f"Attachments: {args.attachment or 'None'}")
        print("=" * 50)
        print(args.body)
    else:
        result = send_reply(
            args.item_name, args.email_id, args.body, args.attachment, args.folder
        )
        print("Email sent successfully!")
        print(f"To: {result['to']}")
        print(f"Subject: {result['subject']}")
        if result["attachments"]:
            print(f"Attachments: {', '.join(result['attachments'])}")
