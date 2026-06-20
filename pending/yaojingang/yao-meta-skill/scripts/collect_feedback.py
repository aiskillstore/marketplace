#!/usr/bin/env python3
import argparse
import json
from datetime import datetime
from pathlib import Path


def load_entries(path: Path) -> list[dict]:
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    entries = payload.get("entries", []) if isinstance(payload, dict) else []
    return entries if isinstance(entries, list) else []


def summarize(entries: list[dict]) -> dict:
    if not entries:
        return {
            "count": 0,
            "average_rating": 0,
            "latest_category": "none",
            "latest_note": "",
        }
    ratings = [entry["rating"] for entry in entries if isinstance(entry.get("rating"), int)]
    latest = entries[-1]
    return {
        "count": len(entries),
        "average_rating": round(sum(ratings) / len(ratings), 2) if ratings else 0,
        "latest_category": latest.get("category", "general"),
        "latest_note": latest.get("note", ""),
    }


def render_markdown(payload: dict) -> str:
    lines = [
        "# Feedback Log",
        "",
        f"- Entries: `{payload['summary']['count']}`",
        f"- Average rating: `{payload['summary']['average_rating']}`",
        "",
        "## Recent Feedback",
        "",
    ]
    if not payload["entries"]:
        lines.append("- No feedback captured yet.")
    for entry in reversed(payload["entries"][-10:]):
        lines.extend(
            [
                f"### {entry['created_at']}",
                f"- Category: `{entry['category']}`",
                f"- Rating: `{entry['rating']}`",
                f"- Note: {entry['note']}",
                f"- Recommended action: {entry['recommended_action']}",
                "",
            ]
        )
    return "\n".join(lines).strip() + "\n"


def collect_feedback(
    skill_dir: Path,
    note: str | None = None,
    rating: int = 3,
    category: str = "general",
    recommended_action: str = "review",
    output_json: Path | None = None,
    output_md: Path | None = None,
) -> dict:
    skill_dir = skill_dir.resolve()
    reports_dir = skill_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_json = output_json or reports_dir / "feedback-log.json"
    output_md = output_md or reports_dir / "feedback-log.md"

    entries = load_entries(output_json)
    if note:
        entries.append(
            {
                "created_at": datetime.now().isoformat(timespec="seconds"),
                "category": category,
                "rating": max(1, min(rating, 5)),
                "note": note,
                "recommended_action": recommended_action,
            }
        )

    payload = {
        "skill_dir": str(skill_dir),
        "entries": entries,
        "summary": summarize(entries),
    }
    output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    output_md.write_text(render_markdown(payload), encoding="utf-8")
    return {
        "ok": True,
        "skill_dir": str(skill_dir),
        "artifacts": {
            "json": str(output_json),
            "markdown": str(output_md),
        },
        "summary": payload["summary"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect lightweight feedback for a skill package.")
    parser.add_argument("skill_dir", nargs="?", default=".")
    parser.add_argument("--note")
    parser.add_argument("--rating", type=int, default=3)
    parser.add_argument("--category", default="general")
    parser.add_argument("--recommended-action", default="review")
    parser.add_argument("--output-json")
    parser.add_argument("--output-md")
    args = parser.parse_args()
    result = collect_feedback(
        Path(args.skill_dir),
        note=args.note,
        rating=args.rating,
        category=args.category,
        recommended_action=args.recommended_action,
        output_json=Path(args.output_json).resolve() if args.output_json else None,
        output_md=Path(args.output_md).resolve() if args.output_md else None,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
