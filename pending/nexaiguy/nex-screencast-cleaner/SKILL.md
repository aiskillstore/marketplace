---
name: nex-screencast-cleaner
description: 'Automatically crops OS taskbars and removes dead air from screen recordings for upload-ready demos. Use when: Crop Windows taskbar or macOS Dock from screen captures automatically; Remove static pauses from demos to create high-density product clips; Normalize non-standard recording resolutions to 1080p for web players.'
license: MIT
metadata:
  author: Nex AI
  version: '1.0'
  agensi-slug: nex-screencast-cleaner
compatibility: Claude Code, Cursor, Aider, Windsurf, and VS Code.
---

# Nex Screencast Cleaner

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nex-screencast-cleaner). Scripts, extension source, and templates from the original package are not in this folder.

## The problem

Raw screen recordings are usually unsuitable for production due to visible OS taskbars, inconsistent dimensions, and "dead air" where nothing happens. Manual editing to remove these pauses is tedious and often results in non-standard resolutions that look unprofessional on product pages.

## What it does

- Detects and crops OS chrome like the Windows taskbar or macOS Dock by identifying sharp brightness steps at frame edges.
- Identifies and removes static frames where no pixels change, tightening the video without visible jump cuts.
- Normalizes output to a clean 1920x1080 resolution with `+faststart` for instant web playback.
- Automatically generates H.264 MP4 files compatible with all major social platforms and HTML5 video tags.

## Frameworks & tools

Python 3 and FFmpeg. Works with any standard MP4 screen capture from OBS, QuickTime, or Windows Game Bar.

## Why this beats prompting it yourself

Simple prompts cannot perform the per-frame pixel analysis required to identify motion spans or calculate brightness gradients for chrome detection. This skill uses a specialized logic gate to ensure cuts are only made when frames are identical, ensuring the result looks like a continuous take rather than a choppy edit.

## Use cases

- Tightening a 40-second software demo into a 15-second high-impact clip for a marketplace listing.
- Removing a visible Windows taskbar from a recording that was captured in windowed mode.
- Cleaning up "bursty" motion recordings, such as mouse-wheel scrolling, to remove pauses between movements.
- Preparing raw captures for social media reframing by removing all dead time first.

## Known limitations

Not suitable for camera or talking-head footage as cuts will be visible. Audio is dropped by default as the temporal cuts break synchronization. Recordings with constant background animations may prevent automatic pause detection.

## Example

**Request**

Clean up this raw capture raw_demo.mp4. The taskbar is showing and there is a lot of dead air while I was waiting for the page to load. Output it as clean.mp4.

**Result**

source      1912x1084  42.5s
chrome      bottom 46px
segments    14 kept, 12.2s of 42.5s (28%)
removed     30.3s of dead time
written     clean.mp4 (1920x1080, 30fps)

## Questions

### How does the skill automatically remove pauses from my recordings?

The skill uses pixel-level analysis to detect static frames where no movement occurs, automatically cutting these 'dead' moments to create a tight, fast-paced demo without manual editing.

### Can I keep the original audio track in the cleaned-up video?

By default, audio is stripped from the output because the temporal cuts are designed for visual flow, which would cause audio to desync or sound jittery.

### What software or agents do I need to run nex-screencast-cleaner?

This skill is compatible with any AI agent or automation environment that supports Python 3 and FFmpeg, working seamlessly with raw MP4 files from tools like OBS or QuickTime.

### Does the OS taskbar removal work on both Mac and Windows recordings?

The tool identifies sharp brightness gradients at the top or bottom of the frame to isolate and crop out the Windows taskbar or macOS Dock, resulting in a professional, full-screen appearance.

### What is included in my purchase of this skill?

You will receive the complete source code and logic for the video processing pipeline, plus documentation on how to integrate it into your existing content workflows.

### Can I use this to edit videos that feature a presenter's face?

The skill is specialized for UI screen recordings; it is not recommended for webcam or 'talking head' footage, as the frame-cutting logic will create visible and jarring jump cuts in human motion.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
