#!/usr/bin/env python3
"""
Fulltext Fetcher
Fetch HTML from URL/DOI/PMID and save to files.
"""

import argparse
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import List, Tuple


DEFAULT_TIMEOUT_SECONDS = 30
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 2

ALLOWED_HOSTS = {
    "doi.org",
    "pubmed.ncbi.nlm.nih.gov",
    "ncbi.nlm.nih.gov",
    "www.ncbi.nlm.nih.gov",
    "pmc.ncbi.nlm.nih.gov",
}


def is_allowed(url: str, allow_all: bool) -> bool:
    if allow_all:
        return True
    host = urllib.parse.urlparse(url).netloc.lower()
    return host in ALLOWED_HOSTS


def fetch_url(url: str, allow_all: bool) -> Tuple[bytes, str]:
    if not is_allowed(url, allow_all):
        raise ValueError("Host not in allowlist. Use --allow-all to override.")

    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (compatible; FulltextFetcher/1.0)"},
            )
            with urllib.request.urlopen(req, timeout=DEFAULT_TIMEOUT_SECONDS) as resp:
                content = resp.read()
                final_url = resp.geturl()
                if not is_allowed(final_url, allow_all):
                    raise ValueError("Final host not in allowlist. Use --allow-all.")
                return content, final_url
        except urllib.error.HTTPError as e:
            if 500 <= e.code < 600 and attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF_SECONDS * attempt)
                continue
            raise
        except (urllib.error.URLError, TimeoutError) as e:
            last_error = e
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF_SECONDS * attempt)
                continue
            raise

    if last_error:
        raise last_error
    raise RuntimeError("Request failed")


def resolve_doi(doi: str) -> str:
    return f"https://doi.org/{doi}"


def resolve_pmid(pmid: str) -> str:
    return f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"


def find_pmc_url(html: bytes) -> str | None:
    text = html.decode("utf-8", errors="ignore")
    match = re.search(r"https?://www\.ncbi\.nlm\.nih\.gov/pmc/articles/PMC\d+/", text)
    if match:
        return match.group(0)
    return None


def safe_filename(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9._-]+", "_", value)
    return value[:120] if len(value) > 120 else value


def write_output(out_dir: Path, label: str, content: bytes) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    base = safe_filename(label) or "output"
    path = out_dir / f"{base}.html"
    if path.exists():
        suffix = 1
        while True:
            candidate = out_dir / f"{base}_{suffix}.html"
            if not candidate.exists():
                path = candidate
                break
            suffix += 1
    path.write_bytes(content)
    return path


def handle_url(url: str, out_dir: Path, allow_all: bool) -> Path:
    content, final_url = fetch_url(url, allow_all)
    label = (
        urllib.parse.urlparse(final_url).netloc + urllib.parse.urlparse(final_url).path
    )
    return write_output(out_dir, label, content)


def handle_doi(doi: str, out_dir: Path, allow_all: bool) -> Path:
    url = resolve_doi(doi)
    content, final_url = fetch_url(url, allow_all)
    label = f"doi_{doi}"
    return write_output(out_dir, label, content)


def handle_pmid(pmid: str, out_dir: Path, allow_all: bool) -> Path:
    url = resolve_pmid(pmid)
    content, _ = fetch_url(url, allow_all)
    pmc_url = find_pmc_url(content)
    if pmc_url:
        pmc_content, _ = fetch_url(pmc_url, allow_all)
        return write_output(out_dir, f"pmc_{pmid}", pmc_content)
    return write_output(out_dir, f"pmid_{pmid}", content)


def main() -> None:
    parser = argparse.ArgumentParser(description="Fulltext Fetcher")
    parser.add_argument("--url", action="append", default=[])
    parser.add_argument("--doi", action="append", default=[])
    parser.add_argument("--pmid", action="append", default=[])
    parser.add_argument("--out-dir", default="outputs")
    parser.add_argument("--allow-all", action="store_true")
    args = parser.parse_args()

    if not args.url and not args.doi and not args.pmid:
        raise SystemExit("No input provided")

    out_dir = Path(args.out_dir)
    allow_all = args.allow_all or os.getenv("FULLTEXT_ALLOW_ALL") == "1"

    for url in args.url:
        out_path = handle_url(url, out_dir, allow_all)
        print(f"Saved: {out_path}")

    for doi in args.doi:
        out_path = handle_doi(doi, out_dir, allow_all)
        print(f"Saved: {out_path}")

    for pmid in args.pmid:
        out_path = handle_pmid(pmid, out_dir, allow_all)
        print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
