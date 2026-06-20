# Contributing to VisionCraft

Thanks for your interest in VisionCraft! This project is small and focused, so the bar for contributions is correspondingly simple.

## Reporting issues

- Search existing issues before opening a new one.
- Include the PowerShell version (`$PSVersionTable.PSVersion`), the exact command you ran, and the full error output.
- For API errors, include the HTTP status code and the response body (redact your API key — never paste it).

## Suggesting features

VisionCraft intentionally stays a thin, script-driven wrapper around the Agnes AI APIs. Good suggestions fit that shape:

- ✅ A new workflow the API supports that isn't exposed yet (e.g. a parameter the script doesn't surface).
- ✅ Ergonomic shortcuts (like `-Ratio` / `-Seconds`) that make existing capability easier to use.
- ✅ Robustness fixes: better error messages, timeout handling, retry logic.
- ❌ A second runtime (Python, Node). This skill is PowerShell-first by design.
- ❌ Bundling features unrelated to image/video generation.

## Pull requests

1. Fork and branch from `main`.
2. Keep changes minimal and focused — one feature or fix per PR.
3. Match the existing code style (PowerShell: `PascalCase` parameters, `ConvertTo-Json` for bodies, `MEDIA:` output line on success).
4. If you change a script's parameters or defaults, update `SKILL.md`, `references/parameters.md`, `README.md`, and `examples/README.md` in the same PR.
5. **Never commit a real API key.** The CI of this repo is human review — help keep it that way.

## Code style notes

- PowerShell 7+ target.
- Build request bodies as hashtables and serialize with `ConvertTo-Json -Depth 10`. Do not hand-concatenate JSON strings.
- Scripts must read the key from `$env:AGNES_API_KEY` only.
- Surface the final URL as a `MEDIA:<url>` line on its own, so downstream tooling can scrape it.

By contributing, you agree that your contributions are licensed under the [MIT License](LICENSE).
