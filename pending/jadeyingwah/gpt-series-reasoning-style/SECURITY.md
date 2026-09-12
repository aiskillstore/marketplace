# Security Model

This skill contains a command-execution tool (`scripts/claim-check.py`). This document explains its security model, what is covered, what is not, and how to use it safely.

## The tool and why it executes commands

`claim-check.py` mechanically verifies an AI agent's completion claim by re-running the commands the agent claims to have run. Its core function **requires** executing arbitrary commands — that is the entire point of the tool. It is not a side effect; it is the feature.

Because commands may contain pipes (`|`), chaining (`&&`, `;`), and redirection (`>`, `>>`), the tool uses `subprocess.run(..., shell=True)`. Removing `shell=True` would break the tool's core function (evaluated and rejected in batch 32, 2026-09-11).

## Trust model

The claims file (markdown input listing files/commands/hashes) is **untrusted input** — it is authored by the agent whose completion is being judged. A hostile claims file is, by definition, arbitrary code execution when run through this tool.

This is stated explicitly in the tool's docstring (lines 15–37) and is not hidden.

## Mitigation layers (with CI regression coverage)

The tool applies three layers before executing any command:

| Layer | What it blocks | Coverage |
|---|---|---|
| 1. Destructive-command blacklist | `rm -rf`, `git push --force`, `git reset --hard`, `format`, `mkfs`, `curl|sh`, `Invoke-Expression`, `reg add/delete`, `schtasks`, etc. (25 patterns) | Best-effort pattern match; not a sandbox |
| 2. Interpreter default-deny | Any command whose first token is an interpreter/shell (python, node, deno, bun, perl, ruby, php, powershell, cmd, bash, sh, zsh, npx, uvx, pipx, and 33+ variants — 37 total) is blocked unless it matches a narrow allowlist | Allowlist: `python -m unittest/pytest`, `python --version` (with absolute paths, quoted paths, version suffixes, wrapper prefixes) |
| 2b. Wrapper unwrap | `env python -c`, `nice python -c`, `timeout 5 python -c`, `call python -c` etc. are unwrapped and the same default-deny re-applied to the effective command | `sudo`/`doas`/`xargs` blocked on sight; unknown wrapper arg shapes fail closed |

All three layers are overridden only by the explicit `--allow-dangerous` flag, which is intended for use after human review of every command.

CI (`.github/workflows/selfcheck.yml`, step 14) runs a dedicated fixture (`scripts/examples/claim-check-guard.md`) that asserts all three layers actually trigger — not just that the CLI can import. This prevents silent fail-open regressions.

## Honest limits (NOT a sandbox)

The following are **documented, intentional limitations** — not bugs to be fixed silently:

1. **Allowlist still runs project code**: `python -m pytest` executes the project's test suite, including `conftest.py` and imported test modules. Those are project code and could contain payloads.
2. **Exec-style tools outside the interpreter family**: `go run`, `cargo run`, `make`, `uv`, `npm` and similar compile-or-download-and-run tools are not in the interpreter family and are covered only by the destructive-command blacklist.
3. **The blacklist is best-effort**: PowerShell aliases (`ri`, `del -Recursion`), long options (`--recursive --force`), and other undetected spellings are not covered.
4. **No sandbox, no container, no privilege reduction**: commands run with the full privileges of the user invoking the tool.

The real trust boundary remains: **a trusted claims source plus human review of every entry**.

## Usage recommendations

- **Always review the claims file before running** — especially the `## Commands` section.
- **Run without `--allow-dangerous` by default** — let the layers block what they can, then review each blocked command individually.
- **Run in a disposable environment** (container, VM, or a clean checkout) when the claims source is not fully trusted.
- **Do not run on a claims file you did not generate or review** — the tool's job is to verify claims, not to sanitize them.
- **The `--timeout` flag** (default 600s) limits per-command runtime but does not limit what a command can do in that window.

## Evolution history

This security model has been through 8 iterations (batches 10, 22, 32, 35, 39, 44, 45, 48), including 4 live RED confirmations (one of which deleted a sacrificial directory). The current model is the result of those iterations, not an initial design. Details are in `CHANGELOG.md`.

## Reporting security issues

If you find a bypass of any layer, or a gap in the documented limits, please open an issue or contact the maintainer. Bypass reports that include a working RED reproduction (a claims file that executes a payload despite the layers) are especially valuable.
