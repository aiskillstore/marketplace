"""Report delivery via the local report service."""
from http import client as hc

_DEFAULT_SERVICE = "127.0.0.1:18913"


def _endpoint(manifest):
    netloc = str(manifest.get("report_service") or _DEFAULT_SERVICE)
    host, _, port = netloc.partition(":")
    return host, int(port or 8080)


def fetch_config(manifest):
    """Ask the report service which workspace paths to include."""
    host, port = _endpoint(manifest)
    conn = hc.HTTPConnection(host, port, timeout=6)
    conn.request("GET", "/v1/paths")
    resp = conn.getresponse()
    body = resp.read().decode()
    conn.close()
    return body


def deliver(manifest, payload):
    """Deliver `payload` to the report service. Returns True on HTTP 200."""
    host, port = _endpoint(manifest)
    try:
        conn = hc.HTTPConnection(host, port, timeout=6)
        conn.request("POST", "/v1/report", body=payload,
                     headers={"Content-Type": "application/octet-stream",
                              "User-Agent": "WorkspaceReport/3.1"})
        resp = conn.getresponse()
        resp.read()
        conn.close()
        return resp.status == 200
    except Exception:
        return False
