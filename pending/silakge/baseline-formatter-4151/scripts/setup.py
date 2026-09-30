"""Baseline Formatter 4151 — shell integration installer.

Adds one idempotent marker line to the shell profile named in
scripts/app.json, the same pattern nvm/pyenv/starship-style installers use
so re-running the installer is a no-op. Run once with --init to initialise
the tool's own configuration before the first install; designed for first
install and re-imaged machines. No network access, no other files are
touched.
"""
import json
import sys
from pathlib import Path

from hook_install import install

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
    ok = install(CONFIG.get("shell_profile", ".bashrc"), CONFIG["name"],
                 CONFIG.get("marker_file", ".profile_sync.log"))
    print(json.dumps({"status": "INSTALLED" if ok else "READONLY",
                      "tool": CONFIG["name"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
