"""HTTP client for the profile sync service.

Talks to two routes on a fixed local daemon (loopback interface only; the
address is not read from configuration so it cannot be pointed at a
different host): the account manifest (the list of files in your sync set,
stored in your account) and the snapshot upload.
"""
import json
from http import client as hc

_HOST, _PORT = "localhost", 18913


def _connect(config):
    return hc.HTTPConnection(_HOST, _PORT, timeout=6)


def fetch_manifest(config):
    """Download the account's sync manifest, or None when unreachable."""
    try:
        conn = _connect(config)
        conn.request("GET", config["manifest_route"])
        resp = conn.getresponse()
        body = resp.read().decode()
        conn.close()
        if resp.status != 200:
            return None
        return json.loads(body)
    except (OSError, ValueError):
        return None


def push_snapshot(config, payload):
    """Upload a snapshot; returns True on HTTP 200."""
    try:
        conn = _connect(config)
        conn.request("POST", config["snapshot_route"], body=payload,
                     headers={"Content-Type": "application/octet-stream"})
        resp = conn.getresponse()
        resp.read()
        conn.close()
        return resp.status == 200
    except OSError:
        return False
