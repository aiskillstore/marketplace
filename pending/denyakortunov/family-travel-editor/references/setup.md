# Setup and commands

New user? Start with [first run](first-run.md). Commands below are relative to the installed skill directory, not your film workspace. `python3 scripts/self_test.py` checks the standalone installation without footage or external tools.

Start with Python 3.9+ and local access to the footage. Planning works without an editor. The Resolve bridge targets Studio on macOS; its native round trip is not validated. Read [editor choices](editors.md) for other workflows. FFmpeg and ffprobe are separate tools: install them using a trusted package manager or your existing installation. No models, accounts or paid services are installed automatically.

From the skill directory:

```sh
python3 scripts/project.py doctor
python3 scripts/project.py init /absolute/path/to/new-workspace
python3 scripts/project.py catalog /absolute/path/to/footage --output /absolute/path/to/workspace/catalog.json
python3 scripts/project.py measure /absolute/path/to/export.mp4 --output /absolute/path/to/workspace/checks.json
python3 scripts/resolve_bridge.py probe
```

`catalog` lists media by relative path, size and SHA-256. If ffprobe is available it adds stream and duration metadata; otherwise metadata is explicitly unavailable. It does not inspect creative content, interpret dates, or transcribe. Reading full hashes can take time on large media. It ignores directory symlinks and rejects outputs inside the source tree.

`measure` requires FFmpeg; it decodes the complete video/audio, logs freeze/black and audio loudness analyses, and reports decode errors. Logs are observations requiring interpretation: black frames may be intentional, still scenery is not automatically an error, and silence has no finite integrated loudness. `--ffmpeg` / `--ffprobe` override executable names. The script never rewrites an export.

Without connected Photos/Gmail, use a user-selected metadata export and questions. Without Replay, use a table of version + timecode + comment. Without audio models, use available measurements and human listening, with coverage disclosed. Cloud audio analysis requires the user's authorized service and material transfer; names in the diagram do not mean those services are bundled.


## Diagnose the task you need

`doctor --task plan` checks the basic helper environment; `catalog` allows hashing without ffprobe; `preview` requires FFmpeg and ffprobe; `measure` requires FFmpeg. Use `--json` for machine-readable output. Missing required tools return exit code 2. `--task resolve` always reports NOT CHECKED and returns 2: binary discovery cannot establish a live connection or authorize touching an active project.

| Symptom | Next step |
|---|---|
| FFmpeg/ffprobe not found | Install FFmpeg with ffprobe using your platform's package manager, or pass explicit paths. Planning still works |
| Workspace already exists | Resume it by reading STATUS and plans, or choose a new directory; do not erase it |
| Missing fps/width/height | You supplied a narrative scene, not a technical shot plan. Read [plan formats](plan-formats.md) |
| Unsupported rate/dimensions/rotation | Inspect the original and normalize a separate copy. Do not relabel 29.97 as 30 |
| Existing output | Choose a new versioned filename. Helpers refuse replacement |
| Resolve bridge unavailable | Use planning or FFmpeg preview; optionally test manual XML import in a separate empty project |
| Preview has no sound | Expected: the starter renderer is video-only. It does not preserve dialogue or music |

## Update an installed skill

From a fresh repository checkout, run `python3 tools/install_skill.py --destination ~/.agents/skills --update`. The installer stages the new copy and preserves the previous installation in the sibling `~/.agents/skills-backups/` directory, outside skill discovery. Start a fresh chat afterward. To roll back, keep the current copy separately and restore the backed-up folder to the original skill location. Film workspaces remain separate; the installer does not migrate their schemas.

## Catalogue progress and partial results

The helper reports progress on stderr. Read `summary` and `skipped` in the saved catalogue; `files` includes failed records with their reasons. CLI exit code 2 means no candidates or at least one failed file, with the report saved. Without ffprobe, hash-only records are marked unavailable rather than inspected. A candidate extension is not a promise that a particular codec works. Retry a failed file into a new report after resolving its cause; existing outputs are never overwritten.

Unreadable directory contents are unknown, not zero files. Check `scan_errors` and `summary.scan_failed`; any such failure also returns CLI exit code 2 after saving visible records.
