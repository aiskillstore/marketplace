import os
import datetime
from email.utils import parseaddr
from guardian_storage import open_private_sqlite

DB_PATH = os.path.join(os.path.dirname(__file__), "sender_reputation.db")

class ReputationManager:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_conn(self):
        return open_private_sqlite(self.db_path)

    def _init_db(self):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS senders (
                    email TEXT PRIMARY KEY,
                    domain TEXT,
                    score INTEGER DEFAULT 1,
                    interactions INTEGER DEFAULT 1,
                    is_vip INTEGER DEFAULT 0,
                    first_seen TEXT,
                    last_seen TEXT,
                    notes TEXT
                )
            ''')
            conn.commit()

    def clean_address(self, raw_header):
        if not raw_header:
            return "", ""
        name, addr = parseaddr(raw_header)
        addr = addr.strip().lower()
        domain = addr.split('@')[-1] if '@' in addr else ''
        return addr, domain

    def record_interaction(self, raw_header, is_vip=False, score_delta=5, notes=""):
        email, domain = self.clean_address(raw_header)
        if not email or not domain:
            return
        
        now = datetime.datetime.now().isoformat()
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT score, interactions, is_vip FROM senders WHERE email = ?', (email,))
            row = cursor.fetchone()
            if row:
                cur_score, cur_inter, cur_vip = row
                new_vip = 1 if (cur_vip or is_vip) else 0
                cursor.execute('''
                    UPDATE senders
                    SET score = score + ?, interactions = interactions + 1, is_vip = ?, last_seen = ?, notes = COALESCE(notes, ?)
                    WHERE email = ?
                ''', (score_delta, new_vip, now, notes, email))
            else:
                cursor.execute('''
                    INSERT INTO senders (email, domain, score, interactions, is_vip, first_seen, last_seen, notes)
                    VALUES (?, ?, ?, 1, ?, ?, ?, ?)
                ''', (email, domain, score_delta, 1 if is_vip else 0, now, now, notes))
            conn.commit()

    def is_trusted(self, raw_from, raw_rp=""):
        from_email, from_domain = self.clean_address(raw_from)
        rp_email, rp_domain = self.clean_address(raw_rp)
        
        targets = [e for e in [from_email, rp_email] if e]
        if not targets:
            return False

        with self._get_conn() as conn:
            cursor = conn.cursor()
            placeholders = ','.join(['?'] * len(targets))
            cursor.execute(f'SELECT email, score, is_vip FROM senders WHERE email IN ({placeholders})', targets)
            rows = cursor.fetchall()
            for r in rows:
                if r[2] == 1 or r[1] >= 5:
                    return True
        return False

    def seed_from_mailbox(self, service):
        """Scans sent and starred folders to automatically seed legitimate correspondents."""
        print("[REPUTATION] Auto-seeding trusted contacts from Sent and Starred messages...")
        count = 0
        for folder in ['in:sent', 'is:starred']:
            try:
                res = service.users().messages().list(userId='me', q=folder, maxResults=50).execute()
                for m in res.get('messages', []):
                    try:
                        md = service.users().messages().get(userId='me', id=m['id'], format='metadata', metadataHeaders=['To', 'From']).execute()
                        headers = {x['name'].lower(): x['value'] for x in md.get('payload', {}).get('headers', [])}
                        to_h = headers.get('to', '')
                        from_h = headers.get('from', '')
                        
                        if folder == 'in:sent' and to_h:
                            for recip in to_h.split(','):
                                self.record_interaction(recip, is_vip=True, score_delta=10, notes="Sent recipient")
                                count += 1
                        elif folder == 'is:starred' and from_h:
                            self.record_interaction(from_h, is_vip=True, score_delta=10, notes="Starred sender")
                            count += 1
                    except Exception:
                        pass
            except Exception as e:
                print(f"[WARN] Error seeding {folder}: {e}")
        print(f"[REPUTATION] Successfully seeded {count} interactions into local SQLite reputation DB.")
