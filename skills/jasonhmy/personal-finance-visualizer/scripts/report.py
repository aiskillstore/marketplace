#!/usr/bin/env python3
"""Render a local report without persisting imported data by default."""
import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import secrets
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

ASSETS = Path(__file__).resolve().parents[1] / "assets"
MAX_BYTES = 25 * 1024 * 1024


def load_input(raw, *, currency=None, start=None, end=None, language=None):
    if len(raw) > MAX_BYTES:
        raise ValueError("Input is larger than 25 MiB. Split it into smaller reports.")
    content = raw.decode("utf-8-sig")
    if content.lstrip().startswith("{"):
        data = json.loads(content)
    else:
        if not all([currency, start, end]):
            raise ValueError("CSV requires --currency, --start and --end.")
        reader = csv.DictReader(io.StringIO(content))
        if not {"id", "date", "amount", "kind"}.issubset(reader.fieldnames or []):
            raise ValueError("CSV requires id, date, amount and kind columns. See references/schema.md.")
        rows = list(reader)
        data = dict(schemaVersion=1, currency=currency, coverage=dict(start=start,end=end),
                    transactions=rows, refunds=[], settlements=[], notes=[])
    if not isinstance(data, dict) or data.get("schemaVersion") != 1 or not isinstance(data.get("transactions"), list):
        raise ValueError("Expected a version 1 report object. See references/schema.md.")
    if language:
        data["language"] = language
    return data


def render(data):
    # Escape the HTML parser boundary before any user content enters a script.
    payload = json.dumps(data, ensure_ascii=True, allow_nan=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    html = (ASSETS / "report.html").read_text()
    parts = {"__STYLE__": (ASSETS / "report.css").read_text(),
             "__ENGINE__": (ASSETS / "engine.js").read_text(),
             "__APP__": (ASSETS / "app.js").read_text(), "__DATA__": payload}
    # One pass: user strings cannot activate another template replacement.
    import re
    html = re.sub(r"__STYLE__|__ENGINE__|__APP__|__DATA__", lambda m: parts[m.group()], html)
    scripts = re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>", html, flags=re.S)
    import base64
    hashes = " ".join("'sha256-"+base64.b64encode(hashlib.sha256(s.encode()).digest()).decode()+"'" for s in scripts)
    policy = "default-src 'none'; script-src " + hashes + "; style-src 'unsafe-inline'; img-src data:; connect-src 'none'; base-uri 'none'; form-action 'none'"
    html = html.replace("<head>", '<head><meta http-equiv="Content-Security-Policy" content="'+policy+'"><meta name="referrer" content="no-referrer">',1)
    return html.encode("utf-8")


def export_report(destination, html):
    path = Path(destination).expanduser()
    if not path.is_absolute():
        raise ValueError("Choose an absolute path for the explicit local export.")
    path = path.resolve()
    if any((p / ".git").exists() for p in [path.parent, *path.parent.parents]):
        raise ValueError("Save private reports outside Git repositories.")
    skill = Path(__file__).resolve().parents[1]
    if path.resolve().is_relative_to(skill):
        raise ValueError("Save private reports outside the installed skill.")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as output:
        output.write(html)


def create_server(html):
    token = secrets.token_urlsafe(24)
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def do_GET(self):
            host = f"127.0.0.1:{self.server.server_port}"
            if self.headers.get("Host") != host or self.path != "/"+token:
                self.send_response(404)
                self.end_headers()
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "DENY")
            self.end_headers()
            self.wfile.write(html)
    server = HTTPServer(("127.0.0.1", 0), Handler)
    return server, f"http://127.0.0.1:{server.server_port}/{token}"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", help="Normalized JSON/CSV path, or - for stdin")
    source.add_argument("--demo", action="store_true", help="Use entirely invented records")
    for name in ["currency", "start", "end"]:
        parser.add_argument("--"+name)
    parser.add_argument("--language", choices=["en", "zh-CN"])
    parser.add_argument("--export", metavar="ABSOLUTE_HTML_PATH", help="Explicit local export; never overwrite")
    args = parser.parse_args()
    try:
        if args.demo:
            from demo_data import make_demo
            data = make_demo(args.language or "en")
        else:
            if args.input == "-":
                raw = sys.stdin.buffer.read(MAX_BYTES+1)
            else:
                with open(args.input, "rb") as source_file:
                    raw = source_file.read(MAX_BYTES+1)
            data = load_input(raw, currency=args.currency, start=args.start, end=args.end, language=args.language)
        html = render(data)
        if args.export:
            export_report(args.export, html)
            print("Local report exported. It contains the imported data; keep it private.")
        else:
            server, url = create_server(html)
            print(url, flush=True)
            print("Memory-only report. Stop with Ctrl+C when finished. No request log is kept.", flush=True)
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass
            finally:
                server.server_close()
        return 0
    except (OSError, UnicodeError, ValueError, TypeError):
        print("Unable to prepare the report. Check input schema, UTF-8 encoding, CSV options and a new writable export path. No source data was modified.", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
