import os
import json
import datetime
from guardian_storage import write_private_json

STATS_FILE = os.path.join(os.path.dirname(__file__), "guardian_stats.json")

class StatsTracker:
    def __init__(self, stats_file=STATS_FILE):
        self.stats_file = stats_file
        self.data = self._load()

    def _load(self):
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "total_neutralized": 0,
            "total_relays_harvested": 0,
            "daily_events": []
        }

    def _save(self):
        # Keep only last 30 days of daily events
        cutoff = (datetime.datetime.now() - datetime.timedelta(days=30)).isoformat()
        self.data["daily_events"] = [e for e in self.data.get("daily_events", []) if e.get("timestamp", "") > cutoff]
        write_private_json(self.stats_file, self.data)

    def record_neutralization(self, sender, subject, reason, relay_domain=None):
        now = datetime.datetime.now().isoformat()
        self.data["total_neutralized"] = self.data.get("total_neutralized", 0) + 1
        
        event = {
            "timestamp": now,
            "sender": (sender or "")[:50],
            "subject": (subject or "")[:50],
            "reason": reason,
            "relay_harvested": relay_domain
        }
        if relay_domain:
            self.data["total_relays_harvested"] = self.data.get("total_relays_harvested", 0) + 1

        self.data.setdefault("daily_events", []).append(event)
        self._save()

    def get_24h_summary(self):
        cutoff = (datetime.datetime.now() - datetime.timedelta(hours=24)).isoformat()
        events_24h = [e for e in self.data.get("daily_events", []) if e.get("timestamp", "") >= cutoff]
        
        count = len(events_24h)
        harvested = len([e for e in events_24h if e.get("relay_harvested")])
        
        return (
            f"🛡️ Guardian 24h activity: {count} reviewed actions recorded, "
            f"{harvested} relay domains added to the local blocklist. "
            "Review the Guardian label and Gmail Trash to confirm the results."
        )
