# Agent testing (manual, 2026-10-14, macOS laptop)

The skill was installed as user-level symlinks: `~/.claude/skills/request-transit` and
`~/.agents/skills/request-transit`, both pointing at this checkout. Each run started in a fresh temp directory
that held only a copy of `samples/otel-demo-checkout.otlp.json`. The base prompt was *"Animate
otel-demo-checkout.otlp.json with the request-transit skill and make a GIF in this directory."*

| # | Agent | Mode / flags | Result |
| - | --- | --- | --- |
| 1 | Claude Code 2.1.133 | `claude -p`, `--permission-mode acceptEdits`, `--allowedTools Bash(node:*) Read Skill`, `--add-dir <skill>` | ✅ Skill discovered and named. `anim.gif` + `anim.mp4` + `contact.png` in the temp dir (~45 s). |
| 2 | Codex CLI 0.146.0 | `codex exec -s workspace-write --add-dir <skill>` | ⚠️ Skill discovered. Chromium can't start in the macOS sandbox (`bootstrap_check_in … Permission denied (1100)`). **Before the fix**, the agent hand-wrote its own PPM→ffmpeg "transit-ish" GIF. |
| 3 | Codex CLI | same as 2, after the SKILL.md fix | ✅ It stopped and reported the Chromium error with no fake output. |
| 4 | Codex CLI | `codex exec -s danger-full-access`, cwd = temp dir, prompt says "only write inside this directory" | ✅ Real `anim.gif`/`anim.mp4`/`contact.png`/`transit.html` in the temp dir. Nothing outside the temp dir changed. |
| 5 | Claude Code | first run: `node_modules` and `.transit-cache/setup.json` moved aside | ✅ `setup.mjs` reinstalled the npm deps, re-checked Chromium and ffmpeg, rewrote the marker, then rendered. (The Playwright browser cache in `~/Library/Caches` was left in place, so a browser download was not exercised.) |
| 6 | Claude Code | "show me the expected request/response for each hop from my code" | ✅ Explicit ask = consent. It built with `--contracts` and reported matched, fallback, infra and unmatched hops. It reused the existing example index and did not re-index. **Bug:** output went to `<skill>/out/` because SKILL.md examples used `out/<name>`. Fixed. |
| 7 | Claude Code | neutral: "animate … HTML only, as much detail per hop as you can" | ✅ No index built or read (`index.json` mtime unchanged). Output in `./transit-out/` (after the fix). |
| 8 | Cursor CLI (`cursor-agent`) | `-p --force` | ❓ Logged in, but the print-mode run produced no answer (just a banner) and no files. Not investigated further; Cursor is untested. |

## SKILL.md fixes from these runs

- `name: transit` became `request-transit`, to match the README and folder name (Cursor requires the match). The description now lists all supported sources.
- New "Where things are" section: run scripts from the skill folder by absolute path, and write outputs to the user's working directory (`--out-dir ./transit-out/<name>`), never inside the skill.
- Rule: render only with the bundled scripts. On failure (sandboxed Chromium, missing ffmpeg), stop and report the error and the rerun command. Never hand-write a substitute renderer.
- Contract section: a cached index may be reused only when the user asked for contracts.

## Notes

- `render.mjs` leaves a `frames/` folder next to the outputs.
- Codex needs more than `workspace-write` on macOS to render video.
