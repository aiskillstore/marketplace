#!/usr/bin/env python3
"""
Plan Generator
Generate review plans or lab schedules.
"""

import argparse
import json
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


DATE_FMT = "%Y-%m-%d"


def parse_date(value: str) -> date:
    return datetime.strptime(value, DATE_FMT).date()


def date_range(start: date, end: date) -> List[date]:
    days = []
    current = start
    while current <= end:
        days.append(current)
        current += timedelta(days=1)
    return days


def is_weekend(day: date) -> bool:
    return day.weekday() >= 5


def read_json(path: str) -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def prompt(text: str) -> str:
    return input(text).strip()


def prompt_required(text: str) -> str:
    value = ""
    while not value:
        value = prompt(text)
    return value


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


def collect_common_inputs() -> Dict:
    plan_type = prompt_required("Plan type (review/lab): ").lower()
    while plan_type not in {"review", "lab"}:
        plan_type = prompt_required("Plan type (review/lab): ").lower()

    start_date = prompt_required("Start date (YYYY-MM-DD): ")
    end_date = prompt_required("End date (YYYY-MM-DD): ")

    weekday_hours = prompt_float("Daily hours (weekday): ", minimum=0.5)
    weekend_hours = prompt_float("Daily hours (weekend): ", minimum=0.5)

    items = []
    item_count = prompt_int("How many items? ", minimum=1)
    for index in range(item_count):
        print(f"Item {index + 1}:")
        name = prompt_required("  Name: ")
        if plan_type == "review":
            exam_date = prompt("  Exam date (YYYY-MM-DD, optional): ")
            importance = prompt_int("  Importance (1-5): ", minimum=1)
            topics_raw = prompt("  Topics (comma-separated, optional): ")
            topics = [t.strip() for t in topics_raw.split(",") if t.strip()]
            items.append(
                {
                    "name": name,
                    "exam_date": exam_date or None,
                    "importance": importance,
                    "topics": topics,
                }
            )
        else:
            duration_hours = prompt_float("  Duration hours: ", minimum=0.5)
            deps_raw = prompt("  Dependencies (comma-separated, optional): ")
            resources_raw = prompt("  Resources (comma-separated, optional): ")
            dependencies = [d.strip() for d in deps_raw.split(",") if d.strip()]
            resources = [r.strip() for r in resources_raw.split(",") if r.strip()]
            items.append(
                {
                    "name": name,
                    "duration_hours": duration_hours,
                    "dependencies": dependencies,
                    "resources": resources,
                }
            )

    return {
        "plan_type": plan_type,
        "start_date": start_date,
        "end_date": end_date,
        "daily_hours": {"weekday": weekday_hours, "weekend": weekend_hours},
        "items": items,
    }


def validate_payload(payload: Dict) -> None:
    required = ["plan_type", "start_date", "end_date", "items", "daily_hours"]
    for key in required:
        if key not in payload:
            raise ValueError(f"Missing required field: {key}")

    if payload["plan_type"] not in {"review", "lab"}:
        raise ValueError("plan_type must be review or lab")

    start = parse_date(payload["start_date"])
    end = parse_date(payload["end_date"])
    if end < start:
        raise ValueError("end_date must be on or after start_date")

    daily = payload["daily_hours"]
    if "weekday" not in daily or "weekend" not in daily:
        raise ValueError("daily_hours must include weekday and weekend")


def review_plan(payload: Dict) -> Dict:
    start = parse_date(payload["start_date"])
    end = parse_date(payload["end_date"])
    days = date_range(start, end)

    items = payload["items"]
    items_sorted = sorted(items, key=lambda x: x.get("importance", 1), reverse=True)

    schedule = []
    idx = 0
    for day in days:
        item = items_sorted[idx % len(items_sorted)]
        topics = item.get("topics") or []
        topic = topics[idx % len(topics)] if topics else "Review points"
        hours = payload["daily_hours"]["weekend" if is_weekend(day) else "weekday"]
        schedule.append(
            {
                "date": day,
                "title": item["name"],
                "detail": topic,
                "hours": hours,
            }
        )
        idx += 1

    return {"schedule": schedule, "items": items_sorted}


def topo_sort(items: List[Dict]) -> List[Dict]:
    name_to_item = {item["name"]: item for item in items}
    remaining = set(name_to_item.keys())
    resolved = []

    while remaining:
        progress = False
        for name in list(remaining):
            deps = set(name_to_item[name].get("dependencies") or [])
            if deps.issubset({i["name"] for i in resolved}):
                resolved.append(name_to_item[name])
                remaining.remove(name)
                progress = True
        if not progress:
            # Fallback: append remaining to avoid infinite loop
            for name in list(remaining):
                resolved.append(name_to_item[name])
                remaining.remove(name)
    return resolved


def lab_plan(payload: Dict) -> Dict:
    start = parse_date(payload["start_date"])
    end = parse_date(payload["end_date"])
    days = date_range(start, end)

    items_sorted = topo_sort(payload["items"])
    schedule = []
    day_index = 0

    for item in items_sorted:
        hours_left = float(item.get("duration_hours", 0))
        while hours_left > 0 and day_index < len(days):
            day = days[day_index]
            capacity = payload["daily_hours"][
                "weekend" if is_weekend(day) else "weekday"
            ]
            used = min(hours_left, capacity)
            resources = ", ".join(item.get("resources") or []) or "none"
            schedule.append(
                {
                    "date": day,
                    "title": item["name"],
                    "detail": f"resource: {resources}",
                    "hours": used,
                }
            )
            hours_left -= used
            day_index += 1

    return {"schedule": schedule, "items": items_sorted}


def render_markdown(payload: Dict, plan: Dict) -> str:
    lines = []
    lines.append(f"# Plan generator output ({payload['plan_type']})")
    lines.append("")
    lines.append("## Summary")
    lines.append(f"- Start and end date: {payload['start_date']} ~ {payload['end_date']}")
    lines.append(
        f"- Daily available time: working day {payload['daily_hours']['weekday']} Hour, weekend {payload['daily_hours']['weekend']} Hour"
    )
    lines.append("")

    lines.append("## Schedule")
    for entry in plan["schedule"]:
        lines.append(
            f"- {entry['date'].strftime(DATE_FMT)} | {entry['title']} | {entry['detail']} | {entry['hours']}h"
        )

    lines.append("")
    lines.append("## Task list")
    for item in plan["items"]:
        if payload["plan_type"] == "review":
            exam = item.get("exam_date") or "not specified"
            topics = ", ".join(item.get("topics") or []) or "not specified"
            lines.append(f"- {item['name']} | take an exam: {exam} | theme: {topics}")
        else:
            deps = ", ".join(item.get("dependencies") or []) or "none"
            resources = ", ".join(item.get("resources") or []) or "none"
            lines.append(
                f"- {item['name']} | duration: {item.get('duration_hours')}h | rely: {deps} | resource: {resources}"
            )

    return "\n".join(lines) + "\n"


def output_path(payload: Dict, override: Optional[str]) -> Path:
    if override:
        return Path(override)
    suffix = payload["plan_type"]
    return Path(f"plan_{suffix}.md")


def main() -> None:
    parser = argparse.ArgumentParser(description="Plan Generator")
    parser.add_argument("--json", help="Path to input JSON")
    parser.add_argument("--output", help="Output markdown path")
    args = parser.parse_args()

    if args.json:
        payload = read_json(args.json)
    else:
        payload = collect_common_inputs()

    validate_payload(payload)

    if payload["plan_type"] == "review":
        plan = review_plan(payload)
    else:
        plan = lab_plan(payload)

    md = render_markdown(payload, plan)
    out_path = output_path(payload, args.output)
    out_path.write_text(md, encoding="utf-8")
    print(f"Plan saved to {out_path}")


if __name__ == "__main__":
    main()
