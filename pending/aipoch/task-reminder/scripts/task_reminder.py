#!/usr/bin/env python3
"""
Task Reminder
Organize tasks and generate reminders (daily/weekly/deadline).
"""

import argparse
import csv
import json
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import List


DATE_FMT = "%Y-%m-%d"


@dataclass
class Task:
    title: str
    deadline: str | None
    priority: int
    estimate_hours: float
    tags: List[str]


def parse_date(value: str) -> date:
    return datetime.strptime(value, DATE_FMT).date()


def date_range(start: date, end: date) -> List[date]:
    days = []
    current = start
    while current <= end:
        days.append(current)
        current += timedelta(days=1)
    return days


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def prompt(text: str) -> str:
    return input(text).strip()


def prompt_int(text: str, minimum: int = 0) -> int:
    while True:
        value = prompt(text)
        if not value:
            continue
        try:
            parsed = int(value)
            if parsed < minimum:
                continue
            return parsed
        except ValueError:
            continue


def prompt_float(text: str, minimum: float = 0.0) -> float:
    while True:
        value = prompt(text)
        if not value:
            continue
        try:
            parsed = float(value)
            if parsed < minimum:
                continue
            return parsed
        except ValueError:
            continue


def collect_interactive() -> dict:
    start_date = prompt("Start date (YYYY-MM-DD): ")
    end_date = prompt("End date (YYYY-MM-DD): ")
    reminder_mode = prompt("Reminder mode (daily/weekly/deadline/all): ").strip()
    if not reminder_mode:
        reminder_mode = "all"
    weekly_day = prompt("Weekly day (0=Mon..6=Sun, default 0): ").strip()
    weekly_day = int(weekly_day) if weekly_day else 0
    count = prompt_int("How many tasks? ", minimum=1)
    tasks = []
    for idx in range(count):
        print(f"Task {idx + 1}:")
        title = prompt("  Title: ")
        deadline = prompt("  Deadline (YYYY-MM-DD, optional): ")
        priority = prompt_int("  Priority (1-5): ", minimum=1)
        estimate = prompt_float("  Estimate hours: ", minimum=0.5)
        tags_raw = prompt("  Tags (comma-separated, optional): ")
        tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
        tasks.append(
            {
                "title": title,
                "deadline": deadline or None,
                "priority": priority,
                "estimate_hours": estimate,
                "tags": tags,
            }
        )
    return {
        "start_date": start_date,
        "end_date": end_date,
        "tasks": tasks,
        "reminder_mode": reminder_mode,
        "weekly_day": weekly_day,
    }


def validate_payload(payload: dict) -> None:
    for key in ["start_date", "end_date", "tasks"]:
        if key not in payload:
            raise ValueError(f"Missing required field: {key}")
    start = parse_date(payload["start_date"])
    end = parse_date(payload["end_date"])
    if end < start:
        raise ValueError("end_date must be on or after start_date")

    reminder_mode = payload.get("reminder_mode", "all")
    if reminder_mode not in {"daily", "weekly", "deadline", "all"}:
        raise ValueError("reminder_mode must be daily/weekly/deadline/all")
    weekly_day = payload.get("weekly_day", 0)
    if not isinstance(weekly_day, int) or not (0 <= weekly_day <= 6):
        raise ValueError("weekly_day must be 0-6")


def normalize_tasks(tasks: List[dict]) -> List[Task]:
    normalized = []
    for t in tasks:
        normalized.append(
            Task(
                title=t["title"],
                deadline=t.get("deadline"),
                priority=int(t.get("priority", 3)),
                estimate_hours=float(t.get("estimate_hours", 1)),
                tags=t.get("tags", []),
            )
        )
    return normalized


def build_reminders(
    tasks: List[Task],
    start: date,
    end: date,
    reminder_mode: str,
    weekly_day: int,
) -> List[dict]:
    reminders = []
    for day in date_range(start, end):
        for task in tasks:
            if task.deadline:
                deadline = parse_date(task.deadline)
                if reminder_mode in {"deadline", "all"} and day == deadline:
                    reminders.append(
                        {
                            "date": day,
                            "type": "deadline",
                            "task": task.title,
                        }
                    )
            if reminder_mode in {"weekly", "all"} and day.weekday() == weekly_day:
                reminders.append(
                    {
                        "date": day,
                        "type": "weekly",
                        "task": task.title,
                    }
                )
            if reminder_mode in {"daily", "all"}:
                reminders.append({"date": day, "type": "daily", "task": task.title})
    return reminders


def render_markdown(
    tasks: List[Task], reminders: List[dict], output_path: Path
) -> None:
    lines = []
    lines.append("#Task reminder output")
    lines.append("")
    lines.append("## Executable manifest")
    for task in tasks:
        tags = ", ".join(task.tags) if task.tags else "none"
        deadline = task.deadline or "not specified"
        lines.append(
            f"- {task.title} | Deadline: {deadline} | priority: {task.priority} | estimate time: {task.estimate_hours}h | Label: {tags}"
        )
    lines.append("")
    lines.append("## Reminder Schedule")
    for r in reminders:
        lines.append(f"- {r['date'].strftime(DATE_FMT)} | {r['type']} | {r['task']}")
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_csv(reminders: List[dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "type", "task"])
        for r in reminders:
            writer.writerow([r["date"].strftime(DATE_FMT), r["type"], r["task"]])


def main() -> None:
    parser = argparse.ArgumentParser(description="Task Reminder")
    parser.add_argument("--json", help="Path to input JSON")
    parser.add_argument("--out-md", default="reminders.md")
    parser.add_argument("--out-csv", default="reminders.csv")
    parser.add_argument("--notify", action="store_true")
    args = parser.parse_args()

    payload = load_json(args.json) if args.json else collect_interactive()
    validate_payload(payload)

    tasks = normalize_tasks(payload["tasks"])
    start = parse_date(payload["start_date"])
    end = parse_date(payload["end_date"])
    reminder_mode = payload.get("reminder_mode", "all")
    weekly_day = payload.get("weekly_day", 0)
    reminders = build_reminders(tasks, start, end, reminder_mode, weekly_day)

    render_markdown(tasks, reminders, Path(args.out_md))
    render_csv(reminders, Path(args.out_csv))

    if args.notify:
        print("System notifications are not enabled by default.")

    print("DONE")


if __name__ == "__main__":
    main()
