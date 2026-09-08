#!/usr/bin/env python3
"""Emit one fresh local-time anchor as one JSON object.

Timezone precedence:
1. ``--timezone``
2. ``PROFILE_TIMEZONE`` environment variable
3. system local timezone

Exit 0 prints exactly one JSON object. Exit 2 prints a stable error
prefix to stderr and emits no JSON.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


def arguments(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--timezone",
        help="IANA timezone name; overrides PROFILE_TIMEZONE",
    )
    return parser.parse_args(argv)


def configured_timezone(args):
    if args.timezone:
        return args.timezone.strip(), "argument"
    environment = os.environ.get("PROFILE_TIMEZONE", "").strip()
    if environment:
        return environment, "profile-environment"
    return None, "system-local"


def current_time(args):
    timezone_name, source = configured_timezone(args)
    if timezone_name:
        return datetime.now(ZoneInfo(timezone_name)), timezone_name, source
    local = datetime.now().astimezone()
    label = getattr(local.tzinfo, "key", None) or str(local.tzinfo) or "system-local"
    return local, label, "system-local"


def offset_text(value):
    offset = value.utcoffset()
    if offset is None:
        raise RuntimeError("local timezone has no UTC offset")
    seconds = int(offset.total_seconds())
    sign = "+" if seconds >= 0 else "-"
    hours, remainder = divmod(abs(seconds), 3600)
    return f"{sign}{hours:02d}:{remainder // 60:02d}"


def payload(now, timezone_name, source):
    today = now.date()
    return {
        "captured_at": now.isoformat(timespec="seconds"),
        "date": today.isoformat(),
        "source": source,
        "time": now.strftime("%H:%M:%S"),
        "timezone": timezone_name,
        "tomorrow": (today + timedelta(days=1)).isoformat(),
        "utc_offset": offset_text(now),
        "weekday": now.strftime("%A"),
        "yesterday": (today - timedelta(days=1)).isoformat(),
        "zone_abbreviation": now.tzname() or "local",
    }


def main(argv=None):
    try:
        now, timezone_name, source = current_time(arguments(argv))
        result = payload(now, timezone_name, source)
    except Exception as error:
        print(f"current_anchor_error: {type(error).__name__}: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
