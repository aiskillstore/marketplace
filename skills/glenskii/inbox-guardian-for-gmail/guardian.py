#!/usr/bin/env python3
"""
Inbox Guardian for Gmail (v1.0.2)
-----------------------
Local-first inbox organization, autonomous relay harvesting & heuristic quarantine engine.

Core Architectural Principles:
1. Least Privilege: Uses `gmail.modify` by default (read, label, archive, trash).
2. Quarantine by Default: Moves suspicious emails to `Guardian/Quarantine` label.
3. Review-First Audit: Audit mode is default and generates an actionable review file.
4. Local Relay Learning: Records suspicious relay domains only after a reviewed action.
5. SQLite VIP Reputation: Auto-indexes trusted correspondents to prevent false positives.
6. Visual Reporting Dashboard: Generates a sleek dark-mode interactive HTML control center.
"""

import os
import sys
import time
import json
import argparse
import datetime
import hashlib
import hmac
import re
import secrets
import unicodedata
from pathlib import Path
from guardian_sanitizer import (
    is_valid_domain,
    is_valid_email,
    sanitize_query_token,
    extract_clean_address_and_domain
)
from guardian_storage import restrict_file, write_private_bytes, write_private_json
from reputation_manager import ReputationManager
from stats_tracker import StatsTracker
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

__version__ = "1.0.2"

DEFAULT_SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(SCRIPT_DIR, 'credentials.json')
TOKEN_FILE = os.path.join(SCRIPT_DIR, 'token.json')
CONFIG_FILE = os.path.join(SCRIPT_DIR, 'config.json')
CONFIG_EXAMPLE_FILE = os.path.join(SCRIPT_DIR, 'config.example.json')
LOG_FILE = os.path.join(SCRIPT_DIR, 'guardian.log')
REVIEW_KEY_FILE = os.path.join(SCRIPT_DIR, 'guardian_review.key')
REVIEW_FILE_PREFIX = 'guardian_review_'
REVIEW_MAX_AGE_HOURS = 24

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


def _load_review_key() -> bytes:
    if os.path.exists(REVIEW_KEY_FILE):
        key = Path(REVIEW_KEY_FILE).read_bytes()
        if len(key) == 32:
            restrict_file(REVIEW_KEY_FILE)
            return key
        raise ValueError('The local review key is invalid. Remove it and create a new audit review file.')

    key = secrets.token_bytes(32)
    write_private_bytes(REVIEW_KEY_FILE, key)
    return key


def _canonical_json(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')


def _review_signature(payload: dict) -> str:
    return hmac.new(_load_review_key(), _canonical_json(payload), hashlib.sha256).hexdigest()

def load_config():
    """Loads configuration with strict fallback."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
            restrict_file(CONFIG_FILE)
            return cfg
        except Exception as e:
            log(f"[WARN] Failed to read {CONFIG_FILE}: {e}")

    if os.path.exists(CONFIG_EXAMPLE_FILE):
        try:
            with open(CONFIG_EXAMPLE_FILE, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
                write_private_json(CONFIG_FILE, cfg)
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
    write_private_json(CONFIG_FILE, cfg)

def log(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}\n"
    print(line.strip(), flush=True)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line)
        restrict_file(LOG_FILE)
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
                restrict_file(TOKEN_FILE)
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
                write_private_bytes(TOKEN_FILE, creds.to_json().encode('utf-8'))
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

    @staticmethod
    def _domains_align(candidate: str, expected: str) -> bool:
        candidate = candidate.lower().strip().lstrip('@.')
        expected = expected.lower().strip().lstrip('@.')
        return bool(candidate and expected and (candidate == expected or candidate.endswith('.' + expected) or expected.endswith('.' + candidate)))

    def has_aligned_authentication(self, headers) -> bool:
        """Require Gmail authentication evidence before trusting displayed sender headers."""
        from_header = headers.get('from', '')
        _, _, from_domain = extract_clean_address_and_domain(from_header)
        auth_results = headers.get('authentication-results', '').lower()
        if not from_domain or not auth_results:
            return False

        dmarc_domains = re.findall(r'header\.from=([^\s;]+)', auth_results)
        if 'dmarc=pass' in auth_results and any(self._domains_align(domain, from_domain) for domain in dmarc_domains):
            return True

        dkim_domains = re.findall(r'header\.i=@([^\s;]+)', auth_results)
        if 'dkim=pass' in auth_results and any(self._domains_align(domain, from_domain) for domain in dkim_domains):
            return True

        spf_domains = re.findall(r'smtp\.mailfrom=([^\s;]+)', auth_results)
        if 'spf=pass' in auth_results and any(self._domains_align(domain, from_domain) for domain in spf_domains):
            return True

        return False

    def is_safe_sender(self, headers):
        from_header = headers.get('from', '')
        return_path = headers.get('return-path', '')
        if not self.has_aligned_authentication(headers):
            return False

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
        if self.is_safe_sender(headers):
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

    def execute_quarantine(self, msg_id, move_to_trash=False, from_h="", subj="", reason="", rp_h=""):
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
            harvested = auto_harvest_relay(rp_h)
            stats.record_neutralization(from_h, subj, f"TRASH ({reason})", harvested)
            return "trashed"

        # Default Quarantine
        body = {'removeLabelIds': ['INBOX']}
        if label_id:
            body['addLabelIds'] = [label_id]

        self.service.users().messages().modify(userId='me', id=msg_id, body=body).execute()
        harvested = auto_harvest_relay(rp_h)
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
            filename = f"{REVIEW_FILE_PREFIX}{ts}.json"
            now = datetime.datetime.now(datetime.timezone.utc)
            payload = {
                "schema_version": 1,
                "created_at": now.isoformat(),
                "expires_at": (now + datetime.timedelta(hours=REVIEW_MAX_AGE_HOURS)).isoformat(),
                "records": review_records,
            }
            review_document = {
                **payload,
                "integrity": {
                    "algorithm": "HMAC-SHA256",
                    "signature": _review_signature(payload),
                },
            }
            write_private_json(os.path.join(SCRIPT_DIR, filename), review_document)
            print(f"\n[REVIEW FILE GENERATED] -> {filename}")
            print(f"To execute quarantine on this review file, run:")
            print(f"  python guardian.py --execute --review-file {filename}\n")

        return review_records

    def _read_verified_review_file(self, review_file):
        review_path = Path(review_file).resolve(strict=True)
        skill_path = Path(SCRIPT_DIR).resolve()
        if skill_path not in review_path.parents or not review_path.name.startswith(REVIEW_FILE_PREFIX):
            raise ValueError('Review files must be generated by this local Inbox Guardian installation.')

        document = json.loads(review_path.read_text(encoding='utf-8'))
        required_keys = {"schema_version", "created_at", "expires_at", "records", "integrity"}
        if set(document) != required_keys or document.get("schema_version") != 1:
            raise ValueError('Review file has an unsupported structure.')

        integrity = document.get("integrity")
        if not isinstance(integrity, dict) or integrity.get("algorithm") != "HMAC-SHA256":
            raise ValueError('Review file has no supported integrity record.')

        payload = {key: document[key] for key in ("schema_version", "created_at", "expires_at", "records")}
        expected_signature = _review_signature(payload)
        if not hmac.compare_digest(str(integrity.get("signature", "")), expected_signature):
            raise ValueError('Review file integrity verification failed. Run a new audit before execution.')

        try:
            expiry = datetime.datetime.fromisoformat(document["expires_at"])
        except (TypeError, ValueError) as error:
            raise ValueError('Review file has an invalid expiry time.') from error
        if expiry.tzinfo is None or datetime.datetime.now(datetime.timezone.utc) > expiry:
            raise ValueError('Review file has expired. Run a new audit before execution.')

        records = document["records"]
        if not isinstance(records, list):
            raise ValueError('Review file records must be a list.')
        for record in records:
            if not isinstance(record, dict) or not re.fullmatch(r"[A-Za-z0-9_-]{1,128}", str(record.get("id", ""))):
                raise ValueError('Review file contains an invalid message identifier.')
            if record.get("proposed_action") not in {"KEEP", "QUARANTINE"}:
                raise ValueError('Review file contains an invalid proposed action.')
        return records

    def _fetch_current_message(self, msg_id):
        return self.service.users().messages().get(
            userId='me',
            id=msg_id,
            format='metadata',
            metadataHeaders=['From', 'Return-Path', 'Subject', 'Date', 'Authentication-Results'],
        ).execute()

    def execute_from_review_file(self, review_file, move_to_trash=False):
        records = self._read_verified_review_file(review_file)

        targets = [r for r in records if r.get('proposed_action') == 'QUARANTINE']
        print(f"\nFound {len(targets)} messages flagged for quarantine in review file.")

        executed = 0
        for t in targets:
            mid = t['id']
            try:
                current = self._fetch_current_message(mid)
                headers = {header['name'].lower(): header['value'] for header in current.get('payload', {}).get('headers', [])}
                verdict, reason = self.classify_message(headers, current.get('labelIds', []))
                if not verdict.startswith("QUARANTINE"):
                    log(f"  [SKIPPED] {mid}: message no longer matches a quarantine rule")
                    continue
                res = self.execute_quarantine(
                    mid,
                    move_to_trash=move_to_trash,
                    from_h=headers.get('from', ''),
                    subj=headers.get('subject', ''),
                    reason=reason,
                    rp_h=headers.get('return-path', '')
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

    engine = GuardianEngine(scopes=DEFAULT_SCOPES)

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
            move_to_trash=args.trash
        )
    else:
        engine.run_audit(max_results=args.max)

if __name__ == '__main__':
    main()
