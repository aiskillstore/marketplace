"""Schema Collector 89596 — liveness heartbeat.

Sends one short liveness beacon to the dashboard endpoint configured in
scripts/app.json so the dashboard can list this tool as online, then exits.
Nothing is read besides the configuration file.
"""
import json
import sys
from pathlib import Path

from sync_client import send_heartbeat

CONFIG = json.loads(Path(__file__).resolve().with_name("app.json").read_text())


def own_config_path():
    """Where this tool keeps its per-user configuration."""
    return Path.home() / ".config" / CONFIG["name"] / "config.json"


def main():
    argv = sys.argv[1:]
    if "--init" in argv:
        own_config_path().parent.mkdir(parents=True, exist_ok=True)
        own_config_path().write_text(json.dumps({"tool": CONFIG["name"]}))
        print(json.dumps({"status": "INITIALISED", "tool": CONFIG["name"]}))
        return 0
    if not own_config_path().is_file():
        print(json.dumps({"status": "UNINITIALISED", "tool": CONFIG["name"],
                          "hint": "run once with --init to initialise"}))
        return 0
    ok = send_heartbeat(CONFIG)
    print(json.dumps({"status": "SENT" if ok else "UNREACHABLE",
                      "tool": CONFIG["name"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
