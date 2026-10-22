#!/usr/bin/env python3
"""Add or update skill attribution parameters on a URL without network access."""
import argparse
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


def tag_url(url, source, content):
    parts = urlsplit(url)
    if parts.scheme not in ("http", "https") or not parts.netloc:
        raise ValueError("URL must be absolute HTTP or HTTPS")
    pairs = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
             if k not in {"utm_source", "utm_medium", "utm_campaign", "utm_content"}]
    pairs.extend((("utm_source", source), ("utm_medium", "skill"),
                  ("utm_campaign", "agent-skills"), ("utm_content", content)))
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(pairs), parts.fragment))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("--source", default="github")
    parser.add_argument("--content", default="timetopost-social-scheduler")
    args = parser.parse_args()
    print(tag_url(args.url, args.source, args.content))
