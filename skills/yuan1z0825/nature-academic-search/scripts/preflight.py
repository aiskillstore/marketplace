# -*- coding: utf-8 -*-
"""
Pre-flight API endpoint connectivity checker.

Verifies that the 3 direct API endpoints used by format-converter.py are
reachable. Uses urllib.request.urlopen (stdlib) for consistency with the
existing codebase.

Usage:
  python preflight.py                       # run check and print report
  python -c "from preflight import check_endpoints; print(check_endpoints())"
"""

import sys
import time
from urllib.request import urlopen

ENDPOINTS = [
    {
        "name": "PubMed E-utilities",
        "url": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmax=1",
        "timeout": 10,
        "affected": "PubMed downloads in format-converter",
    },
    {
        "name": "CrossRef REST",
        "url": "https://api.crossref.org/works/10.1038/nature14539",
        "timeout": 10,
        "affected": "CrossRef/DOI downloads in format-converter",
        "expect_status": 200,
    },
    {
        "name": "arXiv API",
        "url": "https://export.arxiv.org/api/query?id_list=1706.03762&max_results=1",
        "timeout": 10,
        "affected": "arXiv downloads in format-converter (MCP search_arxiv unaffected)",
    },
]


def check_single(name, url, timeout, expect_status=None):
    """Check a single endpoint. Returns (ok, elapsed, error_message_or_None)."""
    start = time.perf_counter()
    try:
        with urlopen(url, timeout=timeout) as resp:
            status = resp.status
            _ = resp.read()  # consume body to confirm full response
        elapsed = time.perf_counter() - start
        if expect_status is not None and status != expect_status:
            return False, elapsed, f"unexpected HTTP {status} (expected {expect_status})"
        return True, elapsed, None
    except Exception as e:
        elapsed = time.perf_counter() - start
        # Produce a short error label: prefer the os-error string over full traceback
        error_str = str(e)
        if "time" in error_str.lower() and "out" in error_str.lower():
            error_str = "timeout after {}s".format(timeout)
        elif hasattr(e, "reason") and e.reason is not None:
            error_str = str(e.reason)
        elif hasattr(e, "code"):
            error_str = "HTTP {}".format(e.code)
        return False, elapsed, error_str


def check_endpoints():
    """Check all configured endpoints.

    Returns:
        dict[str, dict]: {name: {"ok": bool, "time": float, "error": str|None}}
    """
    results = {}
    for ep in ENDPOINTS:
        ok, elapsed, error = check_single(
            ep["name"],
            ep["url"],
            ep["timeout"],
            ep.get("expect_status"),
        )
        results[ep["name"]] = {
            "ok": ok,
            "time": elapsed,
            "error": error,
        }
    return results


def print_report(results):
    """Print a human-readable pre-flight report."""
    ok_count = sum(1 for v in results.values() if v["ok"])
    total = len(results)

    print("PRE-FLIGHT REPORT")
    for name, info in results.items():
        status = "OK" if info["ok"] else "FAIL"
        if info["ok"]:
            extra = ""
        else:
            extra = " ({})".format(info["error"])
        print("  {:20s}: {} ({:.1f}s){}".format(name, status, info["time"], extra))

    print("  {}/{} endpoints reachable.".format(ok_count, total))

    if ok_count < total:
        print("  Affected:")
        for ep in ENDPOINTS:
            name = ep["name"]
            info = results[name]
            if not info["ok"]:
                print("    - {}: {}".format(name, ep["affected"]))

    return ok_count == total


def main():
    results = check_endpoints()
    all_ok = print_report(results)
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
