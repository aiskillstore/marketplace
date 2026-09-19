#!/usr/bin/env python3
"""Enable macOS Dictation and set the Dictation shortcut to Control-Control."""

from __future__ import annotations

import plistlib
import subprocess
from pathlib import Path


HOTKEY_ID = "164"
CONTROL_CONTROL_HOTKEY = {
    "enabled": True,
    "value": {
        "parameters": [262144, 18446744073709289471],
        "type": "modifier",
    },
}


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, check=check, text=True, capture_output=True)


def defaults_write(domain: str, key: str, value_type: str, value: str) -> None:
    run("defaults", "write", domain, key, value_type, value)


def enable_dictation_flags() -> None:
    defaults_write("com.apple.HIToolbox", "AppleDictationAutoEnable", "-bool", "true")
    defaults_write("com.apple.assistant.support", "Dictation Enabled", "-bool", "true")
    defaults_write(
        "com.apple.speech.recognition.AppleSpeechRecognition.prefs",
        "DictationIMMasterDictationEnabled",
        "-bool",
        "true",
    )


def update_hotkey() -> None:
    prefs = Path.home() / "Library/Preferences/com.apple.symbolichotkeys.plist"
    if prefs.exists():
        with prefs.open("rb") as handle:
            data = plistlib.load(handle)
    else:
        data = {}

    hotkeys = data.setdefault("AppleSymbolicHotKeys", {})
    hotkeys[HOTKEY_ID] = CONTROL_CONTROL_HOTKEY

    prefs.parent.mkdir(parents=True, exist_ok=True)
    with prefs.open("wb") as handle:
        plistlib.dump(data, handle, fmt=plistlib.FMT_BINARY)


def restart_preference_services() -> None:
    for process in ("cfprefsd", "SystemUIServer"):
        subprocess.run(("killall", process), check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def open_keyboard_settings() -> None:
    subprocess.run(
        ("open", "x-apple.systempreferences:com.apple.Keyboard-Settings.extension"),
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def read_setting(*args: str) -> str:
    result = run(*args, check=False)
    return (result.stdout or result.stderr).strip()


def main() -> int:
    if not Path("/System/Library/CoreServices/SystemVersion.plist").exists():
        print("This script only supports macOS.")
        return 1

    enable_dictation_flags()
    update_hotkey()
    restart_preference_services()
    open_keyboard_settings()

    print("Dictation setup applied.")
    print("AppleDictationAutoEnable:", read_setting("defaults", "read", "com.apple.HIToolbox", "AppleDictationAutoEnable"))
    print("Dictation Enabled:", read_setting("defaults", "read", "com.apple.assistant.support", "Dictation Enabled"))
    print("Shortcut: Control-Control via AppleSymbolicHotKeys id 164")
    print("If System Settings shows a Dictation prompt, click Enable.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
