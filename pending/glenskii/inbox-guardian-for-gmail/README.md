# Inbox Guardian for Gmail (v1.0.2)

![Inbox Guardian for Gmail](assets/social-preview.png)

> Local Gmail inbox review with owner-approved spam rules, audit-first quarantine, and clear recovery paths.
> It runs on your computer and connects only to Gmail through your own Google Cloud OAuth client.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-pytest-brightgreen.svg)]()

---

## System Architecture

![How the system eliminates spam](assets/how-the-system-eliminates-spam.png)

---

## What This Tool Does

Gmail Guardian helps you take back control of your inbox. It targets persistent spam, fake security warnings, and spoofed senders while protecting your genuine contacts.

Key features include:

1. **Least-Privilege Access**: The default Gmail scope can read message headers, label messages, archive them, and move them to Trash. It does not grant administrative account access.
2. **Audit Before Action**: A normal run writes a local review file. Nothing changes in Gmail until the owner executes that reviewed file.
3. **Recoverable Quarantine**: Reviewed candidates receive the `Guardian/Quarantine` label and leave the Inbox. The owner can restore them in Gmail.
4. **Local Sender Learning**: When a reviewed action is applied, the tool can add the related return-path domain to the local blocklist. Trusted contacts built from Sent and Starred mail take precedence over matching rules.
5. **Local Dashboard**: A browser dashboard reads local activity data and rules. It does not host the dashboard or send it to a third-party service.
6. **Header Review Only**: The tool can display `List-Unsubscribe` headers for inspection. It does not follow links, send unsubscribe requests, or treat a header as proof that a sender is legitimate.
7. **Text Normalization**: It converts styled Unicode text to a plain form before comparing configured rules.

---

## Requirements

- Python 3.9 or higher
- A personal Gmail or Google Workspace account
- A free Google Cloud OAuth client credentials file (`credentials.json`)

---

## Installation and Setup

### 1. Download and Set Up

#### On macOS and Linux:
```bash
git clone https://github.com/Glenskii/Glenski-Toolkit.git
cd Glenski-Toolkit/skills/inbox-guardian-for-gmail
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
cp config.example.json config.json
```

#### On Windows (PowerShell):
```powershell
git clone https://github.com/Glenskii/Glenski-Toolkit.git
cd Glenski-Toolkit\skills\inbox-guardian-for-gmail
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -r requirements-dev.txt
copy config.example.json config.json
```

---

### 2. Google Cloud Setup

To allow the script to connect to your Gmail:

Follow the complete [Google OAuth setup guide](docs/google-oauth-setup.md). Place your downloaded Desktop app client file beside `guardian.py` as `credentials.json`, then run:

```bash
python guardian.py --setup
```

The setup command creates local configuration if needed, opens the owner's browser for Google consent, stores the resulting local token with private file permissions where supported, and confirms the connected mailbox. It does not scan, label, move, or delete mail.

---

## How to Use the Tool

### 1. Verify Connection and Account
Check that your OAuth credentials are valid and confirm the active account:
```bash
python guardian.py --setup
```

### 2. Open the Visual Dashboard
To generate and view your status report in your web browser:
```bash
python guardian.py --dashboard
```

### 3. Index Your Trusted Contacts
Scan your Sent and Starred messages to register your frequent contacts:
```bash
python guardian.py --seed-reputation
```

### 4. Print a 24-Hour Summary
To see a quick one-line summary in your terminal:
```bash
python guardian.py --summary
```

### 5. Run an Inbox Audit (Dry Run)
Inspect your recent emails, view classifications, and write a review file:
```bash
python guardian.py
```
This generates a file named `guardian_review_YYYYMMDD_HHMMSS.json`.

### 6. Apply Quarantine from a Review File
Move flagged items to the `Guardian/Quarantine` label based on your audit:
```bash
python guardian.py --execute --review-file guardian_review_20260826_080000.json
```

### 7. Move Flagged Items to Trash
If you prefer moving flagged items directly to Trash:
```bash
python guardian.py --execute --review-file guardian_review_20260826_080000.json --trash
```

### 8. Review Unsubscribe Headers
Display messages that contain `List-Unsubscribe` headers:
```bash
python guardian.py --review-unsub
```

---

## Scheduled Audits

This release does not install or remove operating-system schedules. After a successful `--setup`, you can schedule the standard audit command through Windows Task Scheduler, macOS `launchd`, or Linux cron. Read the [scheduled audit guide](docs/scheduled-runs.md) before enabling it.

Scheduled runs should remain audit-only. Each generated review file is signed, expires after 24 hours, and is rechecked against current mailbox metadata before an owner runs a quarantine or Trash command.

---

## Running Tests

To verify that the rules and functions pass all unit tests:
```bash
pytest tests/ -v
```

---

## Local Data and Privacy

The tool stores its OAuth token, configuration, review files, local reputation database, and activity history beside the skill. Activity history can contain sender and subject excerpts for reviewed actions. These files are ignored by Git and should not be copied into support requests. The only network service used by the tool is the official Gmail API through the mailbox owner's OAuth client. Read [SECURITY.md](SECURITY.md) and the detailed [safety model](docs/safety-model.md).

---

## License

Released under the [MIT License](LICENSE). Copyright (c) 2026 Glen E. Grant.
