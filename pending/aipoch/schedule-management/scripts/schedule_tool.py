import argparse
import csv
import json
import pathlib
from datetime import datetime, timedelta

DATETIME_FMT = "%Y-%m-%d %H:%M"


def parse_dt(value):
    return datetime.strptime(value, DATETIME_FMT)


def load_events(data_dir):
    path = data_dir / "events.jsonl"
    if not path.exists():
        return []
    events = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events


def append_event(data_dir, event):
    path = data_dir / "events.jsonl"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def overlaps(a_start, a_end, b_start, b_end):
    return a_start < b_end and b_start < a_end


def detect_conflicts(events):
    conflicts = []
    parsed = []
    for e in events:
        try:
            start = parse_dt(e["start"])
            end = parse_dt(e["end"])
            parsed.append((e, start, end))
        except Exception:
            continue
    for i in range(len(parsed)):
        for j in range(i + 1, len(parsed)):
            e1, s1, e1e = parsed[i]
            e2, s2, e2e = parsed[j]
            if s1.date() != s2.date():
                continue
            if overlaps(s1, e1e, s2, e2e):
                conflicts.append((e1, e2))
    return conflicts


def export_reminders(events, output_path, now_dt):
    rows = []
    for e in events:
        remind = e.get("remind_minutes")
        if remind is None:
            continue
        try:
            start = parse_dt(e["start"])
        except Exception:
            continue
        reminder_time = start - timedelta(minutes=int(remind))
        if reminder_time >= now_dt:
            rows.append(
                {
                    "title": e.get("title", ""),
                    "start": e.get("start", ""),
                    "reminder_time": reminder_time.strftime(DATETIME_FMT),
                    "remind_minutes": str(remind),
                }
            )
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["title", "start", "reminder_time", "remind_minutes"])
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def main():
    parser = argparse.ArgumentParser(description="Local schedule management tool")
    parser.add_argument("--operation", required=True, help="add|import|list|conflicts|reminders")
    parser.add_argument("--data-dir", required=True, help="Directory for schedule data")
    parser.add_argument("--title")
    parser.add_argument("--start")
    parser.add_argument("--end")
    parser.add_argument("--type", dest="event_type", default="meeting")
    parser.add_argument("--location")
    parser.add_argument("--notes")
    parser.add_argument("--tags", default="")
    parser.add_argument("--remind", type=int, default=None)
    parser.add_argument("--input", help="Input CSV for import")
    args = parser.parse_args()

    data_dir = pathlib.Path(args.data_dir).expanduser()
    data_dir.mkdir(parents=True, exist_ok=True)

    op = args.operation

    if op == "add":
        if not args.title or not args.start or not args.end:
            raise SystemExit("add requires --title --start --end")
        try:
            parse_dt(args.start)
            parse_dt(args.end)
        except Exception:
            raise SystemExit("Invalid datetime format. Use YYYY-MM-DD HH:MM")
        event = {
            "title": args.title,
            "start": args.start,
            "end": args.end,
            "type": args.event_type,
            "location": args.location or "",
            "notes": args.notes or "",
            "tags": [t for t in args.tags.split(",") if t],
            "remind_minutes": args.remind,
        }
        append_event(data_dir, event)
        print({"added": 1})
        return

    events = load_events(data_dir)

    if op == "import":
        if not args.input:
            raise SystemExit("import requires --input")
        input_path = pathlib.Path(args.input)
        if not input_path.exists():
            raise SystemExit("input file not found")
        added = 0
        with input_path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row.get("title") or not row.get("start") or not row.get("end"):
                    continue
                try:
                    parse_dt(row["start"])
                    parse_dt(row["end"])
                except Exception:
                    continue
                event = {
                    "title": row.get("title", ""),
                    "start": row.get("start", ""),
                    "end": row.get("end", ""),
                    "type": row.get("type", "meeting"),
                    "location": row.get("location", ""),
                    "notes": row.get("notes", ""),
                    "tags": [t for t in (row.get("tags", "").split(",") if row.get("tags") else []) if t],
                    "remind_minutes": int(row["remind_minutes"]) if row.get("remind_minutes") else None,
                }
                append_event(data_dir, event)
                added += 1
        print({"imported": added})
        return

    if op == "list":
        print({"count": len(events), "events": events})
        return

    if op == "conflicts":
        conflicts = detect_conflicts(events)
        print({"conflicts": len(conflicts), "pairs": conflicts})
        return

    if op == "reminders":
        output_path = data_dir / "reminders.csv"
        count = export_reminders(events, output_path, datetime.now())
        print({"reminders": count, "output": str(output_path)})
        return

    raise SystemExit("Unsupported operation")


if __name__ == "__main__":
    main()
