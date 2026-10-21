#!/usr/bin/env python3
"""Explicit, metadata-only update check. Never imports finance inputs."""
import json
import re
import urllib.error
import urllib.request
from pathlib import Path

REPOSITORY = "JasonHMY/personal-finance-visualizer"
VERSION = "1.2.1"
URL = f"https://api.github.com/repos/{REPOSITORY}/releases/latest"


def version_tuple(tag):
    match = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)", tag)
    if not match:
        raise ValueError("Unsupported release tag")
    return tuple(map(int, match.groups()))


def main():
    request = urllib.request.Request(URL, headers={"Accept":"application/vnd.github+json", "User-Agent":"personal-finance-visualizer-update-check"})
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            release = json.loads(response.read(262144))
        tag = release["tag_name"]
        newer = version_tuple(tag) > version_tuple(VERSION)
        print(json.dumps({"installed":VERSION, "latest":tag, "updateAvailable":newer,
                          "release":f"https://github.com/{REPOSITORY}/releases/tag/{tag}"}))
        return 0
    except (OSError, ValueError, KeyError):
        print("Update status unavailable. Your installed version is unchanged.")
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
