#!/usr/bin/env python3
"""
Gmail Guardian (v0.1.0)
-----------------------
Local-first inbox organization, autonomous relay harvesting & heuristic quarantine engine.

Core Architectural Principles:
1. Least Privilege: Uses `gmail.modify` by default (read, label, archive, trash).
2. Quarantine by Default: Moves suspicious emails to `Guardian/Quarantine` label.
3. Review-First Audit: Audit mode is default and generates an actionable review file.
4. Autonomous Relay Harvesting: Automatically learns rogue sending domains on detection.
5. SQLite VIP Reputation: Auto-indexes trusted correspondents to prevent false positives.
6. Visual Reporting Dashboard: Generates a sleek dark-mode interactive HTML control center.
"""

import os
import sys
import time
import json
import base64
import argparse
import datetime
import unicodedata
from guardian_sanitizer import (
    is_valid_domain,
    is_valid_email,
    sanitize_query_token,
    extract_clean_address_and_domain
)
from reputation_manager import ReputationManager
from stats_tracker import StatsTracker
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

__version__ = "1.0.1"

DEFAULT_SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
DESTRUCTIVE_SCOPE = ['https://mail.google.com/']

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(SCRIPT_DIR, 'credentials.json')
TOKEN_FILE = os.path.join(SCRIPT_DIR, 'token.json')
CONFIG_FILE = os.path.join(SCRIPT_DIR, 'config.json')
CONFIG_EXAMPLE_FILE = os.path.join(SCRIPT_DIR, 'config.example.json')
LOG_FILE = os.path.join(SCRIPT_DIR, 'guardian.log')

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

if sys.platform == 'win32':
    try:
        import ctypes
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)  # ES_CONTINUOUS
    except Exception:
        pass

reputation = ReputationManager()
stats = StatsTracker()

def load_config():
    """Loads configuration with strict fallback."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            log(f"[WARN] Failed to read {CONFIG_FILE}: {e}")

    if os.path.exists(CONFIG_EXAMPLE_FILE):
        try:
            with open(CONFIG_EXAMPLE_FILE, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
                with open(CONFIG_FILE, 'w', encoding='utf-8') as out:
                    json.dump(cfg, out, indent=2)
                return cfg
        except Exception:
            pass

    return {
        "whitelist_domains": ["google.com", "github.com"],
        "whitelist_emails": [],
        "blocklist_domains": [],
        "blocklist_senders": [],
        "trusted_unsub_domains": ["substack.com", "medium.com", "github.com", "linkedin.com"],
        "suspicious_sender_tlds": [".biz", ".web.id", ".my.id", ".top", ".xyz", ".at", ".us", ".me", ".info"],
        "quarantine_keywords": [
            "last reminder", "blocked your account", "cloud_account", "viruses found",
            "antivirus expired", "photos and videos will be", "account is locked", "unauthorized access"
        ],
        "quarantine_label_name": "Guardian/Quarantine",
        "sweep_interval_minutes": 15
    }

def save_config(cfg):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, indent=2)

def log(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}\n"
    print(line.strip(), flush=True)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass

def normalize_text(text: str) -> str:
    """Converts stylized/mathematical unicode bold/italic text into canonical ASCII."""
    if not text:
        return ""
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii').lower()

def auto_harvest_relay(rp_header):
    """Automatically learns and stores root sending domains of identified spam."""
    _, _, dom = extract_clean_address_and_domain(rp_header)
    if not dom or len(dom) < 4 or '.' not in dom:
        return None
    
    cfg = load_config()
    whitelist = [w.lower() for w in cfg.get("whitelist_domains", [])]
    if any(dom == w or dom.endswith('.' + w) for w in whitelist + ["google.com", "gmail.com", "github.com", "stripe.com"]):
        return None

    blocklist = cfg.setdefault("blocklist_domains", [])
    if dom not in blocklist:
        blocklist.append(dom)
        save_config(cfg)
        log(f"  🧬 [AUTONOMOUS HARVEST] Learned and blocklisted rogue relay domain: '{dom}'")
        return dom
    return None

class GmailAuth:
    @staticmethod
    def get_service(scopes=DEFAULT_SCOPES):
        creds = None
        if os.path.exists(TOKEN_FILE):
            try:
                creds = Credentials.from_authorized_user_file(TOKEN_FILE, scopes)
            except Exception:
                creds = None

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception:
                    creds = None
            if not creds:
                if not os.path.exists(CREDENTIALS_FILE):
                    raise FileNotFoundError(
                        f"Missing '{CREDENTIALS_FILE}'. Please obtain OAuth 2.0 Client credentials from "
                        f"Google Cloud Console and save them to '{CREDENTIALS_FILE}'."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, scopes)
                print("\n[AUTH] Opening browser to complete Google OAuth authorization...")
                creds = flow.run_local_server(port=0)
                with open(TOKEN_FILE, 'w') as token:
                    token.write(creds.to_json())
                print(f"[AUTH] Authorized user credentials saved to '{TOKEN_FILE}'.\n")

        return build('gmail', 'v1', credentials=creds)

def print_oauth_setup_instructions():
    print("\nOAuth setup required:")
    print("1. Open https://console.cloud.google.com/ and create or choose a project.")
    print("2. Enable the Gmail API under APIs & Services > Library.")
    print("3. Configure the OAuth consent screen, then create a Desktop app OAuth client.")
    print(f"4. Download the client file, rename it to '{os.path.basename(CREDENTIALS_FILE)}', and place it in:")
    print(f"   {SCRIPT_DIR}")
    print("5. Run this command again. Your browser will open for owner approval.\n")


def run_setup(scopes=DEFAULT_SCOPES):
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"Missing '{CREDENTIALS_FILE}'.")
        print_oauth_setup_instructions()
        return 1
    load_config()
    try:
        service = GmailAuth.get_service(scopes=scopes)
        profile = service.users().getProfile(userId="me").execute()
        email = profile.get("emailAddress", "unknown")
        print(f"Connected to {email}")
        return 0
    except Exception as e:
        print(f"Setup failed: {e}")
        return 1

class GuardianEngine:
    def __init__(self, service=None, scopes=DEFAULT_SCOPES):
        self.config = load_config()
        self.scopes = scopes
        self.service = service if service else GmailAuth.get_service(scopes=scopes)
        self._labels_cache = {}
        self._init_labels()

    def reload_config(self):
        self.config = load_config()

    def _init_labels(self):
        try:
            res = self.service.users().labels().list(userId='me').execute()
            for l in res.get('labels', []):
                self._labels_cache[l['name']] = l['id']
        except Exception as e:
            log(f"[WARN] Error fetching Gmail labels: {e}")

    def get_or_create_label(self, label_name):
        if label_name in self._labels_cache:
            return self._labels_cache[label_name]
        try:
            body = {
                "name": label_name,
                "labelListVisibility": "labelShow",
                "messageListVisibility": "show"
            }
            lbl = self.service.users().labels().create(userId='me', body=body).execute()
            self._labels_cache[label_name] = lbl['id']
            return lbl['id']
        except Exception as e:
            log(f"[WARN] Could not create label '{label_name}': {e}")
            return None

    def is_safe_sender(self, from_header, return_path):
        if reputation.is_trusted(from_header, return_path):
            return True

        _, from_email, from_domain = extract_clean_address_and_domain(from_header)
        _, rp_email, rp_domain = extract_clean_address_and_domain(return_path)

        for w_dom in self.config.get("whitelist_domains", []):
            w_dom = w_dom.lower().strip()
            if from_domain == w_dom or from_domain.endswith('.' + w_dom):
                return True
            if rp_domain == w_dom or rp_domain.endswith('.' + w_dom):
                return True

        for w_email in self.config.get("whitelist_emails", []):
            w_email = w_email.lower().strip()
            if from_email == w_email or rp_email == w_email:
                return True

        return False

    def is_blocked_sender(self, from_header, return_path):
        _, from_email, from_domain = extract_clean_address_and_domain(from_header)
        _, rp_email, rp_domain = extract_clean_address_and_domain(return_path)

        for b_dom in self.config.get("blocklist_domains", []):
            b_dom = b_dom.lower().strip()
            if from_domain == b_dom or from_domain.endswith('.' + b_dom):
                return True
            if rp_domain == b_dom or rp_domain.endswith('.' + b_dom):
                return True

        for b_email in self.config.get("blocklist_senders", []):
            b_email = b_email.lower().strip()
            if from_email == b_email or rp_email == b_email:
                return True

        return False

    def classify_message(self, headers, labels):
        from_h = headers.get('from', '')
        rp = headers.get('return-path', '')
        raw_subj = headers.get('subject', '')
        
        # 1. Starred, Sent, Drafts
        if 'STARRED' in labels:
            return "SAFE", "Starred message (User protected)"
        if 'SENT' in labels or 'DRAFT' in labels:
            return "SAFE", "Sent / Draft communication"

        # 2. Whitelist & Reputation Precedence
        if self.is_safe_sender(from_h, rp):
            return "SAFE", "Whitelisted or VIP trusted correspondent"

        # 3. Explicit Blocklist
        if self.is_blocked_sender(from_h, rp):
            return "QUARANTINE_BLOCKLIST", "Matched explicit blocklist"

        clean_subj = normalize_text(raw_subj)
        clean_from = normalize_text(from_h)
        _, _, from_dom = extract_clean_address_and_domain(from_h)
        _, _, rp_dom = extract_clean_address_and_domain(rp)

        # 4. Keyword Matches
        for kw in self.config.get("quarantine_keywords", []):
            if kw.lower() in clean_subj:
                return "QUARANTINE_KEYWORD", f"Matched heuristic keyword: '{kw}'"

        # 5. Suspicious TLD Matches
        for tld in self.config.get("suspicious_sender_tlds", []):
            tld = tld.lower().strip()
            if from_dom.endswith(tld) or rp_dom.endswith(tld):
                return "QUARANTINE_TLD", f"Matched suspicious sender TLD: '{tld}'"

        return "LEGITIMATE", "Standard communication"

    def fetch_messages_paginated(self, query="in:inbox", max_results=100):
        messages = []
        page_token = None
        
        while len(messages) < max_results:
            batch_size = min(50, max_results - len(messages))
            try:
                res = self.service.users().messages().list(
                    userId='me',
                    q=query,
                    maxResults=batch_size,
                    pageToken=page_token
                ).execute()
                
                msg_ids = res.get('messages', [])
                for m in msg_ids:
                    try:
                        full = self.service.users().messages().get(
                            userId='me',
                            id=m['id'],
                            format='metadata',
                            metadataHeaders=['From', 'Return-Path', 'Subject', 'Date', 'List-Unsubscribe', 'List-Unsubscribe-Post', 'Authentication-Results']
                        ).execute()
                        messages.append(full)
                    except HttpError as he:
                        log(f"[WARN] Failed to fetch message metadata {m['id']}: {he}")
                
                page_token = res.get('nextPageToken')
                if not page_token:
                    break
            except HttpError as e:
                log(f"[ERROR] Gmail API query failed for '{query}': {e}")
                break
                
        return messages

    def execute_quarantine(self, msg_id, move_to_trash=False, hard_delete=False, from_h="", subj="", reason="", rp_h=""):
        harvested = auto_harvest_relay(rp_h)

        if hard_delete:
            self.service.users().messages().delete(userId='me', id=msg_id).execute()
            stats.record_neutralization(from_h, subj, f"HARD_DELETE ({reason})", harvested)
            return "hard_deleted"

        label_name = self.config.get("quarantine_label_name", "Guardian/Quarantine")
        label_id = self.get_or_create_label(label_name)

        if move_to_trash:
            if label_id:
                try:
                    self.service.users().messages().modify(
                        userId='me',
                        id=msg_id,
                        body={'addLabelIds': [label_id], 'removeLabelIds': ['INBOX']}
                    ).execute()
                except Exception:
                    pass
            self.service.users().messages().trash(userId='me', id=msg_id).execute()
            stats.record_neutralization(from_h, subj, f"TRASH ({reason})", harvested)
            return "trashed"

        # Default Quarantine
        body = {'removeLabelIds': ['INBOX']}
        if label_id:
            body['addLabelIds'] = [label_id]

        self.service.users().messages().modify(userId='me', id=msg_id, body=body).execute()
        stats.record_neutralization(from_h, subj, f"QUARANTINE ({reason})", harvested)
        return "quarantined"

    def run_audit(self, max_results=50, output_review_file=True):
        print(f"\n=======================================================")
        print(f"        GMAIL GUARDIAN INBOX AUDIT (DRY RUN)           ")
        print(f"=======================================================")
        print(f"Scanning up to {max_results} recent messages in Inbox...")
        
        messages = self.fetch_messages_paginated(query="in:inbox", max_results=max_results)
        if not messages:
            print("Inbox is empty or no messages returned.")
            return []

        review_records = []
        counts = {"SAFE": 0, "LEGITIMATE": 0, "QUARANTINE_KEYWORD": 0, "QUARANTINE_TLD": 0, "QUARANTINE_BLOCKLIST": 0}

        for m in messages:
            labels = m.get('labelIds', [])
            headers = {x['name'].lower(): x['value'] for x in m.get('payload', {}).get('headers', [])}
            verdict, reason = self.classify_message(headers, labels)
            counts[verdict] = counts.get(verdict, 0) + 1

            record = {
                "id": m.get('id'),
                "date": headers.get('date', ''),
                "from": headers.get('from', ''),
                "return_path": headers.get('return-path', ''),
                "subject": headers.get('subject', ''),
                "classification": verdict,
                "reason": reason,
                "proposed_action": "QUARANTINE" if verdict.startswith("QUARANTINE") else "KEEP"
            }
            review_records.append(record)

            f_str = (headers.get('from', ''))[:30]
            s_str = (headers.get('subject', ''))[:35]
            print(f"[{verdict.ljust(20)}] {f_str.ljust(32)} | {s_str}")

        print("\n--- CLASSIFICATION SUMMARY ---")
        for k, v in counts.items():
            print(f"  {k.ljust(22)}: {v}")

        if output_review_file:
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"guardian_review_{ts}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(review_records, f, indent=2)
            print(f"\n[REVIEW FILE GENERATED] -> {filename}")
            print(f"To execute quarantine on this review file, run:")
            print(f"  python guardian.py --execute --review-file {filename}\n")

        return review_records

    def execute_from_review_file(self, review_file, move_to_trash=False, hard_delete=False):
        if not os.path.exists(review_file):
            raise FileNotFoundError(f"Review file '{review_file}' does not exist.")

        with open(review_file, 'r', encoding='utf-8') as f:
            records = json.load(f)

        targets = [r for r in records if r.get('proposed_action') == 'QUARANTINE']
        print(f"\nFound {len(targets)} messages flagged for quarantine in review file.")

        if hard_delete:
            print("\n" + "!"*60)
            print("WARNING: DESTRUCTIVE HARD-DELETE REQUESTED")
            print("Messages will be permanently erased from Google servers.")
            print("!"*60)
            confirm = input("Type 'CONFIRM' to execute hard deletion: ").strip()
            if confirm != "CONFIRM":
                print("Hard deletion cancelled by user.")
                return

        executed = 0
        for t in targets:
            mid = t['id']
            try:
                res = self.execute_quarantine(
                    mid,
                    move_to_trash=move_to_trash,
                    hard_delete=hard_delete,
                    from_h=t.get('from', ''),
                    subj=t.get('subject', ''),
                    reason=t.get('reason', ''),
                    rp_h=t.get('return_path', '')
                )
                executed += 1
                log(f"  [{res.upper()}] {t.get('from', '')[:30]} | Subj: {t.get('subject', '')[:35]}")
            except Exception as e:
                log(f"  [ERROR] Failed on {mid}: {e}")

        print(f"\nExecution Complete. {executed} items processed.")
        try:
            from guardian_dashboard import generate_dashboard_html
            generate_dashboard_html()
        except Exception:
            pass

    def review_unsubscribes(self, max_results=50):
        print(f"\n=======================================================")
        print(f"        UNSUBSCRIBE CONFIRMATION REVIEW                ")
        print(f"=======================================================")
        messages = self.fetch_messages_paginated(query="in:inbox", max_results=max_results)
        
        unsub_list = []
        for m in messages:
            headers = {x['name'].lower(): x['value'] for x in m.get('payload', {}).get('headers', [])}
            unsub_header = headers.get('list-unsubscribe')
            if unsub_header:
                unsub_list.append({
                    "id": m.get('id'),
                    "from": headers.get('from'),
                    "subject": headers.get('subject'),
                    "list_unsubscribe": unsub_header
                })

        print(f"Found {len(unsub_list)} emails with explicit List-Unsubscribe headers.\n")
        for idx, u in enumerate(unsub_list, 1):
            print(f"[{idx}] Sender:  {u['from']}")
            print(f"    Subject: {u['subject']}")
            print(f"    Header:  {u['list_unsubscribe']}")
            print("    ---------------------------------------------------")
        print("\nNote: Zero automatic unsubscribe requests are sent.")
        print("To unsubscribe, copy the trusted vendor link or contact the vendor directly.\n")

def main():
    parser = argparse.ArgumentParser(
        description=f"Gmail Guardian v{__version__}: Local Inbox Hygiene, Autonomous Harvesting & Dashboard"
    )
    parser.add_argument('--setup', action='store_true', help="Verify authentication and confirm connected account")
    parser.add_argument('--audit', action='store_true', help="Run non-destructive audit on Inbox (Default)")
    parser.add_argument('--max', type=int, default=50, help="Maximum messages to scan (default: 50)")
    parser.add_argument('--dashboard', action='store_true', help="Generate and open the visual reporting dashboard")
    parser.add_argument('--summary', action='store_true', help="Print 24-hour defense telemetry summary")
    parser.add_argument('--seed-reputation', action='store_true', help="Auto-index trusted correspondents from Sent and Starred messages")
    parser.add_argument('--review-unsub', action='store_true', help="Review legitimate unsubscribe headers (confirmation-only)")
    parser.add_argument('--execute', action='store_true', help="Execute actions from a generated review file")
    parser.add_argument('--review-file', type=str, help="Path to audit review JSON file to execute")
    parser.add_argument('--trash', action='store_true', help="Move quarantined items to Trash instead of labeling/archiving")
    parser.add_argument('--hard-delete', action='store_true', help="Permanently destroy quarantined items (Requires --confirm-destructive)")
    parser.add_argument('--confirm-destructive', action='store_true', help="Explicit confirmation for permanent deletion")
    
    parser.add_argument('--block-domain', type=str, help="Add validated domain to blocklist")
    parser.add_argument('--add-whitelist-domain', type=str, help="Add validated domain to safe whitelist")
    parser.add_argument('--add-whitelist-email', type=str, help="Add validated email to safe whitelist")
    parser.add_argument('--show-config', action='store_true', help="Display active configuration")

    args = parser.parse_args()

    if args.setup:
        sys.exit(run_setup())

    if args.dashboard:
        from guardian_dashboard import main as dash_main
        dash_main()
        return

    if args.summary:
        print("\n" + stats.get_24h_summary() + "\n")
        return

    cfg = load_config()

    if args.add_whitelist_domain:
        dom = args.add_whitelist_domain.strip().lower().lstrip('@.')
        if not is_valid_domain(dom):
            print(f"[ERROR] Invalid domain format: '{args.add_whitelist_domain}'")
            sys.exit(1)
        if dom not in cfg.setdefault('whitelist_domains', []):
            cfg['whitelist_domains'].append(dom)
            save_config(cfg)
            print(f"[CONFIG] Added '{dom}' to safe whitelist domains.")
        return

    if args.add_whitelist_email:
        em = args.add_whitelist_email.strip().lower()
        if not is_valid_email(em):
            print(f"[ERROR] Invalid email format: '{args.add_whitelist_email}'")
            sys.exit(1)
        if em not in cfg.setdefault('whitelist_emails', []):
            cfg['whitelist_emails'].append(em)
            save_config(cfg)
            print(f"[CONFIG] Added '{em}' to safe whitelist emails.")
        return

    if args.block_domain:
        dom = args.block_domain.strip().lower().lstrip('@.')
        if not is_valid_domain(dom):
            print(f"[ERROR] Invalid domain format: '{args.block_domain}'")
            sys.exit(1)
        if dom not in cfg.setdefault('blocklist_domains', []):
            cfg['blocklist_domains'].append(dom)
            save_config(cfg)
            print(f"[CONFIG] Added '{dom}' to blocklist domains.")
        return

    if args.show_config:
        print(json.dumps(cfg, indent=2))
        return

    scopes = DEFAULT_SCOPES
    if args.hard_delete:
        if not args.confirm_destructive:
            print("[ERROR] Hard-delete requires both '--hard-delete' AND '--confirm-destructive'.")
            sys.exit(1)
        scopes = DESTRUCTIVE_SCOPE

    engine = GuardianEngine(scopes=scopes)

    if args.seed_reputation:
        reputation.seed_from_mailbox(engine.service)
        return

    if args.review_unsub:
        engine.review_unsubscribes(max_results=args.max)
    elif args.execute:
        if not args.review_file:
            print("[ERROR] '--execute' requires '--review-file <path_to_json_file>'.")
            sys.exit(1)
        engine.execute_from_review_file(
            args.review_file,
            move_to_trash=args.trash,
            hard_delete=args.hard_delete
        )
    else:
        engine.run_audit(max_results=args.max)

if __name__ == '__main__':
    main()
