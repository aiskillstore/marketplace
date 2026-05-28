#!/usr/bin/env python3
"""
Equipment Maintenance Log
Track lab equipment calibration and maintenance.
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path


def parse_date(date_str):
    """Parse a date string in YYYY-MM-DD format. Exits with error on invalid input."""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        print("Invalid date format. Use YYYY-MM-DD.")
        sys.exit(1)


class EquipmentLog:
    """Manage equipment maintenance records."""

    def __init__(self, data_file="~/.openclaw/equipment_log.json"):
        self.data_file = Path(data_file).expanduser()
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        self.equipment = self._load()

    def _load(self):
        if self.data_file.exists():
            try:
                with open(self.data_file) as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading data file: {e}", file=sys.stderr)
                return {}
        return {}

    def _save(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.equipment, f, indent=2)

    def add(self, name, calibration_date, interval_months, location=""):
        """Add equipment to log. calibration_date must be YYYY-MM-DD."""
        # Validate date format
        parse_date(calibration_date)  # exits on invalid date
        self.equipment[name] = {
            "calibration_date": calibration_date,
            "interval_months": interval_months,
            "location": location or "",
            "added": datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        }
        self._save()
        print(f"Added: {name}")

    def update(self, name, calibration_date=None, interval_months=None, location=None):
        """Update an existing equipment record."""
        if name not in self.equipment:
            print(f"Equipment not found: {name}")
            print(f"Available: {', '.join(self.equipment.keys()) or 'none'}")
            sys.exit(1)
        if calibration_date is not None:
            parse_date(calibration_date)  # validate before storing
            self.equipment[name]["calibration_date"] = calibration_date
        if interval_months is not None:
            self.equipment[name]["interval_months"] = interval_months
        if location is not None:
            self.equipment[name]["location"] = location
        self._save()
        print(f"Updated: {name}")

    def delete(self, name):
        """Delete an equipment record."""
        if name not in self.equipment:
            print(f"Equipment not found: {name}")
            print(f"Available: {', '.join(self.equipment.keys()) or 'none'}")
            sys.exit(1)
        del self.equipment[name]
        self._save()
        print(f"Deleted: {name}")

    def _parse_stored_date(self, name, date_str):
        """Parse a stored date string; skip with warning if malformed."""
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            print(f"Warning: skipping '{name}' - stored date '{date_str}' is invalid.")
            return None

    def check(self):
        """Check for upcoming maintenance."""
        today = datetime.now()
        alerts = {"overdue": [], "30days": [], "60days": [], "90days": []}

        for name, data in self.equipment.items():
            # Use strptime for Python 3.6 compatibility
            last_cal = self._parse_stored_date(name, data["calibration_date"])
            if last_cal is None:
                continue
            next_cal = last_cal + timedelta(days=data["interval_months"] * 30)
            days_until = (next_cal - today).days

            if days_until < 0:
                alerts["overdue"].append((name, abs(days_until)))
            elif days_until <= 30:
                alerts["30days"].append((name, days_until))
            elif days_until <= 60:
                alerts["60days"].append((name, days_until))
            elif days_until <= 90:
                alerts["90days"].append((name, days_until))

        self._print_alerts(alerts)
        return alerts

    def _print_alerts(self, alerts):
        print("\n=== Equipment Maintenance Alerts ===")
        if alerts["overdue"]:
            print("\nOVERDUE:")
            for name, days in alerts["overdue"]:
                print(f"  {name}: {days} days overdue")
        if alerts["30days"]:
            print("\nDue within 30 days:")
            for name, days in alerts["30days"]:
                print(f"  {name}: {days} days")
        if alerts["60days"]:
            print("\nDue within 60 days:")
            for name, days in alerts["60days"]:
                print(f"  {name}: {days} days")
        if not any(alerts.values()):
            print("  All equipment is up to date.")

    def list_all(self):
        """List all equipment."""
        print("\n=== Equipment List ===")
        if not self.equipment:
            print("  No equipment recorded.")
            return
        for name, data in self.equipment.items():
            print(f"\n{name}")
            print(f"  Last calibration: {data['calibration_date']}")
            print(f"  Interval: {data['interval_months']} months")
            if data.get("location"):
                print(f"  Location: {data['location']}")

    def report(self):
        """Generate a maintenance summary report (JSON schema)."""
        today = datetime.now()
        equipment_list = []

        for name, data in self.equipment.items():
            last_cal = self._parse_stored_date(name, data["calibration_date"])
            if last_cal is None:
                continue
            next_cal = last_cal + timedelta(days=data["interval_months"] * 30)
            days_until = (next_cal - today).days

            if days_until < 0:
                status = "OVERDUE"
            elif days_until <= 30:
                status = "DUE_SOON"
            else:
                status = "OK"

            equipment_list.append({
                "name": name,
                "location": data.get("location", ""),
                "last_calibration_date": data["calibration_date"],
                "interval_months": data["interval_months"],
                "next_due_date": next_cal.strftime('%Y-%m-%d'),
                "days_until_due": days_until,
                "status": status
            })

        overdue = sum(1 for e in equipment_list if e["status"] == "OVERDUE")
        due_soon = sum(1 for e in equipment_list if e["status"] == "DUE_SOON")

        report_data = {
            "report_date": today.strftime('%Y-%m-%d'),
            "total_equipment": len(equipment_list),
            "summary": {
                "overdue": overdue,
                "due_within_30_days": due_soon,
                "ok": len(equipment_list) - overdue - due_soon
            },
            "equipment": equipment_list
        }

        print(json.dumps(report_data, indent=2))
        return report_data


def main():
    parser = argparse.ArgumentParser(description="Equipment Maintenance Log")
    parser.add_argument("--add", metavar="NAME", help="Equipment name to add")
    parser.add_argument("--update", metavar="NAME", help="Equipment name to update")
    parser.add_argument("--delete", metavar="NAME", help="Equipment name to delete")
    parser.add_argument("--calibration-date", help="Last calibration date (YYYY-MM-DD)")
    parser.add_argument("--interval", type=int, help="Calibration interval (months)")
    parser.add_argument("--location", help="Equipment location")
    parser.add_argument("--check", action="store_true", help="Check for upcoming maintenance")
    parser.add_argument("--list", action="store_true", help="List all equipment")
    parser.add_argument("--report", action="store_true",
                        help="Generate maintenance summary report (JSON)")

    args = parser.parse_args()

    log = EquipmentLog()

    if args.add:
        if not args.calibration_date:
            print("Error: --calibration-date is required when using --add")
            sys.exit(1)
        if not args.interval:
            print("Error: --interval is required when using --add")
            sys.exit(1)
        log.add(args.add, args.calibration_date, args.interval, args.location or "")
    elif args.update:
        log.update(args.update, args.calibration_date, args.interval, args.location)
    elif args.delete:
        log.delete(args.delete)
    elif args.check:
        log.check()
    elif args.list:
        log.list_all()
    elif args.report:
        log.report()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
