---
name: setup-macbook-productivity
description: "Configure repeatable macOS productivity settings on a user's MacBook, especially voice typing / Dictation setup. Use when Codex is asked to set up, repair, or document MacBook productivity features such as voice typing, Dictation, Dictation shortcuts, microphone input for Dictation, or future local macOS workflow preferences."
---

# Setup MacBook Productivity

## Overview

Use this skill to configure local macOS productivity preferences with a bias toward repeatable setup, verification, and opening the relevant System Settings pane when macOS requires a user confirmation.

The current supported workflow is **voice typing / Dictation** with a Control-Control shortcut.

## Voice Typing Workflow

1. Confirm the host is macOS:

```bash
sw_vers
```

2. Run the bundled setup script:

```bash
python3 "$CODEX_HOME/skills/setup-macbook-productivity/scripts/setup_voice_typing.py"
```

When `CODEX_HOME` is unset, use:

```bash
python3 "$HOME/.codex/skills/setup-macbook-productivity/scripts/setup_voice_typing.py"
```

3. Tell the user that macOS may still show a one-time Dictation privacy or download prompt. They should click **Enable** if asked. For Apple audio sharing, recommend **Not Now** unless the user explicitly wants to share recordings.

4. Ask the user to test in any text field by pressing **Control** twice. They can stop Dictation with **Esc** or by pressing the same shortcut again.

## What The Script Does

The script:

- Enables the known Dictation preference flags.
- Sets the Dictation symbolic hotkey (`AppleSymbolicHotKeys` id `164`) to the working Control-Control modifier shortcut.
- Restarts preference services so macOS notices the change.
- Opens **System Settings > Keyboard** so the user can approve any required prompt and inspect Dictation settings.
- Prints the resulting Dictation and shortcut state for verification.

## Verification

Use these checks after setup:

```bash
defaults read com.apple.HIToolbox AppleDictationAutoEnable 2>/dev/null
defaults read com.apple.assistant.support "Dictation Enabled" 2>/dev/null
defaults read com.apple.symbolichotkeys AppleSymbolicHotKeys | sed -n '/164 =/,/};/p'
```

Expected signal:

- The first two commands return `1`.
- Hotkey `164` has `enabled = 1`, `type = modifier`, and parameters matching Control-Control.

If Dictation still does not start, open **System Settings > Keyboard > Dictation**, verify Dictation is on, set **Shortcut** to **Press Control Key Twice**, and choose the intended microphone source.

## Boundaries

Do not try to bypass macOS privacy prompts. Open Settings and let the user approve prompts that require a human choice.

Do not enable full **Voice Control** unless the user asks for Mac control by voice. Voice Control replaces standard Dictation behavior while it is on.
