#!/usr/bin/env python3
"""orova-seo-check: command-line client for the public Orova SEO Check API.

Usage:
    orova_seo.py check <url> [--locale en|vi] [--json] [--timeout 240] [--interval 3]
    orova_seo.py backlinks <domain> [--limit 50] [--json]

No API key and no signup are needed. Only the URL or domain you pass is sent
to the Orova API. Python 3.9+ and the standard library only.

Exit codes: 0 ok, 1 usage error, 2 network/HTTP error, 3 scan failed, 4 timeout.
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

VERSION = "1.0.0"
DEFAULT_BASE_URL = "https://orova.vn"
USER_AGENT = "orova-seo-check-skill/1.0 (+https://github.com/nguyendotrongan-netizen/orova-seo-check)"
OROVA_SEO_LINE = (
    "For daily monitoring, Search Console insights and AI content tools, "
    "see Orova SEO: https://orova.vn/en/seo"
)
BACKLINKS_NOTE = "Domain-level data from Common Crawl; small sites may show 0."

EXIT_OK = 0
EXIT_USAGE = 1
EXIT_HTTP = 2
EXIT_FAILED = 3
EXIT_TIMEOUT = 4

# Guest rate limits per IP, used in error messages.
SCAN_LIMIT_PER_HOUR = 5
BACKLINKS_LIMIT_PER_HOUR = 30

GROUP_LABELS = {
    "access": "Access & HTTP",
    "security": "Security headers",
    "head": "Head & meta",
    "content": "Content",
    "images": "Images",
    "social": "Social sharing",
    "structured": "Structured data",
    "intl": "International",
    "crawl": "Crawlability",
    "samples": "Sample pages",
    "speed": "Speed",
    "links": "Links & authority",
}

GROUP_ORDER = [
    "access", "security", "head", "content", "images", "social",
    "structured", "intl", "crawl", "samples", "speed", "links",
]

# Check code -> short English statement of what a passing site does.
CHECK_LABELS = {
    # access
    "home_200": "Homepage returns HTTP 200",
    "response_fast": "Homepage responds quickly",
    "ttfb_fast": "Time to first byte is fast",
    "https_on": "Site is served over HTTPS",
    "cert_valid_30d": "TLS certificate is valid for 30+ more days",
    "http_redirects_https": "HTTP redirects to HTTPS",
    "www_consistent": "www and non-www resolve to one host",
    "no_redirect_chain": "No redirect chain on the homepage",
    "custom_404": "Missing pages return a real 404",
    "compression_on": "Compression (gzip/brotli) is enabled",
    "charset_declared": "Character encoding is declared",
    "http2_or_h3": "HTTP/2 or HTTP/3 is supported",
    # security
    "hsts": "Strict-Transport-Security header is set",
    "x_frame_options": "X-Frame-Options header is set",
    "x_content_type_options": "X-Content-Type-Options header is set",
    "csp_present": "Content-Security-Policy header is set",
    "referrer_policy": "Referrer-Policy header is set",
    "no_mixed_content": "No mixed (HTTP) content on HTTPS pages",
    # head
    "title_present": "Page has a title tag",
    "title_length": "Title length is in the recommended range",
    "meta_desc_present": "Page has a meta description",
    "meta_desc_length": "Meta description length is in the recommended range",
    "canonical_present": "Canonical link is present",
    "canonical_self": "Canonical points to the page itself",
    "lang_declared": "HTML lang attribute is declared",
    "viewport_present": "Mobile viewport meta tag is present",
    "not_noindex": "Page is not set to noindex",
    "no_meta_refresh": "No meta refresh redirect",
    "favicon": "Favicon is present",
    "apple_touch_icon": "Apple touch icon is present",
    "theme_color": "Theme color meta tag is present",
    # content
    "h1_present": "Page has an H1 heading",
    "h1_single": "Page has exactly one H1",
    "h2_present": "Page has H2 headings",
    "heading_order": "Headings follow a logical order",
    "word_count_300": "Page has at least 300 words",
    "text_html_ratio": "Text-to-HTML ratio is healthy",
    "no_lorem_ipsum": "No placeholder (lorem ipsum) text",
    "no_empty_anchors": "No empty link anchors",
    "internal_links_5": "Page has at least 5 internal links",
    "no_generic_anchors": "No generic anchor text (e.g. 'click here')",
    # images
    "images_alt_all": "All images have alt text",
    "images_alt_descriptive": "Image alt text is descriptive",
    "images_lazy": "Images use lazy loading",
    "images_modern_format": "Images use modern formats (WebP/AVIF)",
    "images_dimensions": "Images declare width and height",
    # social
    "og_title": "Open Graph title is set",
    "og_description": "Open Graph description is set",
    "og_image": "Open Graph image is set",
    "og_type": "Open Graph type is set",
    "og_url": "Open Graph URL is set",
    "twitter_card": "Twitter card is set",
    # structured
    "jsonld_present": "JSON-LD structured data is present",
    "jsonld_valid": "JSON-LD parses without errors",
    "jsonld_types": "JSON-LD declares useful schema types",
    "breadcrumb_schema": "Breadcrumb schema is present",
    # intl
    "hreflang_present": "hreflang tags are present",
    "hreflang_x_default": "hreflang x-default is set",
    "hreflang_self": "hreflang includes a self reference",
    # crawl
    "robots_exists": "robots.txt exists",
    "robots_not_blocking_all": "robots.txt does not block the whole site",
    "robots_sitemap_ref": "robots.txt references a sitemap",
    "sitemap_exists": "XML sitemap exists",
    "sitemap_valid_xml": "Sitemap is valid XML",
    "sitemap_urls_5": "Sitemap lists at least 5 URLs",
    "sitemap_recent_60d": "Sitemap was updated in the last 60 days",
    "sitemap_same_domain": "Sitemap URLs are on the same domain",
    "sitemap_https_urls": "Sitemap URLs use HTTPS",
    "internal_links_no_broken": "No broken internal links found",
    # samples
    "samples_found": "Sample inner pages were found",
    "samples_fast": "Sample pages respond quickly",
    "samples_title": "Sample pages have titles",
    "samples_h1_single": "Sample pages have exactly one H1",
    "samples_meta": "Sample pages have meta descriptions",
    "samples_img_alt": "Sample page images have alt text",
    # speed
    "psi_perf_mobile": "PageSpeed performance (mobile) is good",
    "psi_perf_desktop": "PageSpeed performance (desktop) is good",
    "psi_seo": "PageSpeed SEO score is good",
    "psi_a11y": "PageSpeed accessibility score is good",
    "psi_best_practices": "PageSpeed best-practices score is good",
    "lcp_ok": "Largest Contentful Paint is within target",
    "cls_ok": "Cumulative Layout Shift is within target",
    "tbt_ok": "Total Blocking Time is within target",
    "page_size_ok": "Page weight is reasonable",
    "scripts_count_ok": "Number of scripts is reasonable",
    "inline_css_small": "Inline CSS is small",
    # links
    "external_links_count": "External link count is reasonable",
    "outbound_https": "Outbound links use HTTPS",
    "outbound_nofollow_info": "Outbound nofollow usage (info)",
    "outbound_no_broken": "No broken outbound links found",
    "referring_domains": "Site has referring domains",
    "domain_rank": "Domain has a rank in the link graph",
}


# ---------------------------------------------------------------- helpers

def check_label(code):
    """Return a readable label for a check code; unknown codes never crash."""
    code = str(code or "")
    return CHECK_LABELS.get(code) or code.replace("_", " ").strip() or "unknown check"


def group_label(key):
    key = str(key or "")
    return GROUP_LABELS.get(key) or key.replace("_", " ").strip() or "other"


def _num(value):
    """Format a number without a trailing .0; pass other values through."""
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return "{:.1f}".format(value)
    if value is None:
        return "-"
    return str(value)


def _cell(value):
    """Make a value safe for a Markdown table cell."""
    return _num(value).replace("|", "\\|").replace("\n", " ")


def _params_text(params, max_len=100):
    if not isinstance(params, dict) or not params:
        return ""
    parts = []
    for key, value in params.items():
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=True)
        parts.append("{}={}".format(key, _num(value)))
    text = ", ".join(parts)
    if len(text) > max_len:
        text = text[: max_len - 3] + "..."
    return text


def _ordered_groups(groups):
    if not isinstance(groups, list):
        return []
    rank = {k: i for i, k in enumerate(GROUP_ORDER)}
    valid = [g for g in groups if isinstance(g, dict)]
    return sorted(valid, key=lambda g: rank.get(g.get("key"), len(rank)))


def _unwrap_result(payload):
    """Accept either the full /result response or just its `result` object."""
    if not isinstance(payload, dict):
        return {}
    if isinstance(payload.get("result"), dict) and "groups" not in payload:
        return payload["result"]
    return payload


def report_url(scan_id, locale="en", base_url=DEFAULT_BASE_URL):
    locale = locale if locale in ("en", "vi") else "en"
    return "{}/{}/seo-check?id={}".format(base_url.rstrip("/"), locale, scan_id)


# ---------------------------------------------------------------- renderers

def render_backlinks_section(backlinks, top=10, heading="## Backlinks"):
    lines = [heading, ""]
    if not isinstance(backlinks, dict):
        lines.append("Backlink data is not available for this scan.")
        lines.append("")
        lines.append(BACKLINKS_NOTE)
        return lines
    found = bool(backlinks.get("found"))
    lines.append("- Referring domains: {}".format(_num(backlinks.get("referring_domains", 0))))
    lines.append("- Domain rank: {}".format(_num(backlinks.get("domain_rank"))))
    items = backlinks.get("referring_domains_list") or []
    if not isinstance(items, list):
        items = []
    items = [i for i in items if isinstance(i, dict)]
    if found and items:
        shown = items[:top] if top else items
        lines.append("")
        lines.append("| Domain | Links | Rank |")
        lines.append("|---|---:|---:|")
        for item in shown:
            lines.append("| {} | {} | {} |".format(
                _cell(item.get("domain")), _cell(item.get("in_degree")), _cell(item.get("rank"))))
    elif not found:
        lines.append("")
        lines.append("No referring domains found in the Common Crawl graph.")
    lines.append("")
    lines.append(_source_line(backlinks))
    lines.append(BACKLINKS_NOTE)
    return lines


def _source_line(backlinks):
    source = backlinks.get("source") or "commoncrawl"
    dataset = backlinks.get("dataset") or "unknown dataset"
    fetched = backlinks.get("fetched_at")
    line = "Source: {} ({})".format(source, dataset)
    if fetched:
        line += ", fetched {}".format(fetched)
    return line + "."


def render_check_markdown(payload, locale="en", scan_id=None, base_url=DEFAULT_BASE_URL):
    """Render a scan result as Markdown.

    `payload` may be the full /u/seo-check/result/<id> response or its
    `result` object. Never raises on missing or unknown fields.
    """
    full = payload if isinstance(payload, dict) else {}
    result = _unwrap_result(full)
    if scan_id is None:
        scan_id = full.get("id")
    domain = result.get("domain") or full.get("domain") or result.get("url") or "unknown"

    out = ["# SEO Check \u2014 {}".format(domain), ""]
    out.append("Score: {}/100".format(_num(result.get("score"))))
    out.append("Scanned: {} \u00b7 {} ms".format(
        result.get("scanned_at") or full.get("finished_at") or "-",
        _num(result.get("duration_ms"))))
    if result.get("url"):
        out.append("URL: {}".format(result.get("url")))
    out.append("")

    groups = _ordered_groups(result.get("groups"))
    out.append("| Group | Score | Max |")
    out.append("|---|---:|---:|")
    for g in groups:
        out.append("| {} | {} | {} |".format(
            _cell(group_label(g.get("key"))), _cell(g.get("score")), _cell(g.get("max"))))
    out.append("")

    failed, warned, passed, skipped = [], [], 0, 0
    for g in groups:
        items = g.get("items") or []
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            status = item.get("status")
            code = item.get("code") or ""
            line = "- {}: {} (`{}`)".format(group_label(g.get("key")), check_label(code), code)
            extra = _params_text(item.get("params"))
            if extra:
                line += " \u2014 {}".format(extra)
            if status == "fail":
                failed.append(line)
            elif status == "warn":
                warned.append(line)
            elif status == "pass":
                passed += 1
            else:
                skipped += 1

    out.append("## Failed checks")
    out.append("")
    out.extend(failed or ["None."])
    out.append("")
    out.append("## Warnings")
    out.append("")
    out.extend(warned or ["None."])
    out.append("")
    out.append("## Passed")
    out.append("")
    passed_line = "{} checks passed.".format(passed)
    if skipped:
        passed_line += " {} skipped.".format(skipped)
    out.append(passed_line)
    out.append("")

    out.extend(render_backlinks_section(result.get("backlinks")))
    out.append("")

    unavailable = result.get("unavailable") or []
    if isinstance(unavailable, list) and unavailable:
        out.append("## Not available in this scan")
        out.append("")
        for entry in unavailable:
            if isinstance(entry, dict):
                entry = json.dumps(entry, ensure_ascii=True)
            out.append("- {}".format(entry))
        out.append("")

    if scan_id:
        out.append("Full report: {}".format(report_url(scan_id, locale, base_url)))
        out.append("")
    out.append(OROVA_SEO_LINE)
    return "\n".join(out) + "\n"


def render_backlinks_markdown(payload):
    """Render a /u/seo-check/backlinks response as Markdown. Never raises."""
    data = payload if isinstance(payload, dict) else {}
    domain = data.get("domain") or "unknown"
    out = ["# Backlinks \u2014 {}".format(domain), ""]
    out.append("- Referring domains: {}".format(_num(data.get("referring_domains", 0))))
    out.append("- Domain rank: {}".format(_num(data.get("domain_rank"))))
    items = data.get("referring_domains_list") or []
    if not isinstance(items, list):
        items = []
    items = [i for i in items if isinstance(i, dict)]
    out.append("")
    if data.get("found") and items:
        out.append("| # | Domain | Links | Rank |")
        out.append("|---:|---|---:|---:|")
        for n, item in enumerate(items, 1):
            out.append("| {} | {} | {} | {} |".format(
                n, _cell(item.get("domain")), _cell(item.get("in_degree")), _cell(item.get("rank"))))
        out.append("")
        total = "Showing {} of {} referring domains".format(
            len(items), _num(data.get("referring_domains", len(items))))
        if data.get("truncated"):
            total += " (truncated)"
        out.append(total + ".")
    else:
        out.append("No referring domains found in the Common Crawl graph.")
    out.append("")
    out.append(_source_line(data))
    out.append(BACKLINKS_NOTE)
    out.append("")
    out.append(OROVA_SEO_LINE)
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- HTTP

class ApiError(Exception):
    def __init__(self, message, status=None, body=None):
        Exception.__init__(self, message)
        self.status = status
        self.body = body or {}


def _request(method, url, body=None, timeout=30):
    data = None
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", "replace")
            status = resp.status
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", "replace") if exc.fp else ""
        try:
            parsed = json.loads(raw) if raw else {}
        except ValueError:
            parsed = {}
        raise ApiError("HTTP {}".format(exc.code), status=exc.code, body=parsed)
    except urllib.error.URLError as exc:
        raise ApiError("Network error: {}".format(exc.reason))
    except (OSError, ValueError) as exc:
        raise ApiError("Network error: {}".format(exc))
    try:
        return status, json.loads(raw) if raw else {}
    except ValueError:
        raise ApiError("Unexpected non-JSON response (HTTP {})".format(status), status=status)


def _explain_error(exc, base_url, per_hour):
    body = exc.body if isinstance(exc.body, dict) else {}
    err = body.get("err") or ""
    page = "{}/en/seo-check".format(base_url.rstrip("/"))
    if exc.status == 429 or err == "rate_limited":
        retry = body.get("retry_after")
        retry_txt = "{} s".format(_num(retry)) if retry is not None else "a while"
        return ("Rate limit reached ({}/hour per IP). Retry after {}, "
                "or open {} in a browser.".format(per_hour, retry_txt, page))
    if err == "invalid_url":
        return "Invalid URL. Pass a full address such as https://example.com."
    if err == "invalid_domain":
        return "Invalid domain. Pass a host such as example.com."
    if err == "busy":
        return "The Orova scanner is busy right now. Try again in a minute."
    if err == "unavailable":
        return "Backlink data is temporarily unavailable. Try again later."
    if err == "not_found":
        return "Scan not found."
    if err == "expired":
        return "Scan result has expired. Run the check again."
    if exc.status:
        return "Orova API error: HTTP {}{}".format(exc.status, " ({})".format(err) if err else "")
    return str(exc)


def resolve_base_url(cli_value):
    return (cli_value or os.environ.get("OROVA_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")


def _normalize_url(url):
    url = (url or "").strip()
    if url and "://" not in url:
        url = "https://" + url
    return url


# ---------------------------------------------------------------- commands

def cmd_check(args):
    base = resolve_base_url(args.base_url)
    url = _normalize_url(args.url)
    try:
        _, started = _request("POST", base + "/u/seo-check/scan",
                              {"url": url, "locale": args.locale})
    except ApiError as exc:
        sys.stderr.write(_explain_error(exc, base, SCAN_LIMIT_PER_HOUR) + "\n")
        return EXIT_HTTP
    scan_id = started.get("id")
    if not started.get("ok") or not scan_id:
        sys.stderr.write("Orova API did not return a scan id: {}\n".format(
            json.dumps(started, ensure_ascii=True)))
        return EXIT_HTTP
    if started.get("cached"):
        sys.stderr.write("Using a cached result from the last 24 hours.\n")

    deadline = time.time() + max(1.0, float(args.timeout))
    interval = max(1.0, float(args.interval))
    last_note = None
    payload = None
    while True:
        try:
            _, payload = _request("GET", "{}/u/seo-check/result/{}".format(
                base, urllib.parse.quote(scan_id)))
        except ApiError as exc:
            sys.stderr.write(_explain_error(exc, base, SCAN_LIMIT_PER_HOUR) + "\n")
            return EXIT_HTTP
        status = payload.get("status")
        if status == "done":
            break
        if status == "failed":
            sys.stderr.write("Scan failed for {}. Full report: {}\n".format(
                url, report_url(scan_id, args.locale, base)))
            return EXIT_FAILED
        note = "Scanning {}: {}% {}".format(url, _num(payload.get("progress", 0)),
                                            payload.get("step") or status or "")
        if note != last_note:
            sys.stderr.write(note.rstrip() + "\n")
            last_note = note
        if time.time() + interval > deadline:
            sys.stderr.write("Timed out after {} s. The scan may still finish; open {}\n".format(
                _num(args.timeout), report_url(scan_id, args.locale, base)))
            return EXIT_TIMEOUT
        time.sleep(interval)

    if args.json:
        out = dict(payload)
        out.setdefault("id", scan_id)
        sys.stdout.write(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    else:
        sys.stdout.write(render_check_markdown(payload, args.locale, scan_id, base))
    return EXIT_OK


def cmd_backlinks(args):
    base = resolve_base_url(args.base_url)
    limit = max(1, min(100, int(args.limit)))
    query = urllib.parse.urlencode({"domain": args.domain.strip(), "limit": limit})
    try:
        _, payload = _request("GET", "{}/u/seo-check/backlinks?{}".format(base, query))
    except ApiError as exc:
        sys.stderr.write(_explain_error(exc, base, BACKLINKS_LIMIT_PER_HOUR) + "\n")
        return EXIT_HTTP
    if args.json:
        sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    else:
        sys.stdout.write(render_backlinks_markdown(payload))
    return EXIT_OK


def build_parser():
    parser = argparse.ArgumentParser(
        prog="orova_seo.py",
        description="SEO check and backlinks via the public Orova API (no API key, no signup).")
    parser.add_argument("--version", action="version", version="%(prog)s " + VERSION)
    sub = parser.add_subparsers(dest="command")

    def add_base(p):
        p.add_argument("--base-url", default=None,
                       help="API base URL (default: $OROVA_BASE_URL or https://orova.vn)")

    p_check = sub.add_parser("check", help="Run a full SEO check on a URL")
    p_check.add_argument("url")
    p_check.add_argument("--locale", choices=["en", "vi"], default="en")
    p_check.add_argument("--json", action="store_true", help="Print raw JSON instead of Markdown")
    p_check.add_argument("--timeout", type=float, default=240, help="Max seconds to wait (default 240)")
    p_check.add_argument("--interval", type=float, default=3, help="Poll interval in seconds (default 3)")
    add_base(p_check)
    p_check.set_defaults(func=cmd_check)

    p_bl = sub.add_parser("backlinks", help="List referring domains for a domain")
    p_bl.add_argument("domain")
    p_bl.add_argument("--limit", type=int, default=50, help="1..100 (default 50)")
    p_bl.add_argument("--json", action="store_true", help="Print raw JSON instead of Markdown")
    add_base(p_bl)
    p_bl.set_defaults(func=cmd_backlinks)
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "func", None):
        parser.print_help(sys.stderr)
        return EXIT_USAGE
    try:
        return args.func(args)
    except KeyboardInterrupt:
        sys.stderr.write("Interrupted.\n")
        return 130


if __name__ == "__main__":
    sys.exit(main())
