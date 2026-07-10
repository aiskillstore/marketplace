# Shared Pre-flight Check

> Shared across all onchainos skills. Run ONCE at the start of each conversation, before the first `onchainos` command; don't repeat it on later turns.

## Default — do this, then stop

1. Run: `onchainos preflight --skill-version <this skill's frontmatter version>`
2. Read `data.action` from the JSON it prints (preflight always exits 0 — don't block on it):
   - **null** → continue silently; don't echo routine output.
   - **non-null** → show it to the user (their language) and do exactly what it says (e.g. re-read this SKILL.md; for a package-manager skill, update via its manager; on integrity/update failure run `onchainos upgrade --force`).

`preflight` already updates the binary + skill checkouts, verifies integrity, and reports version + drift. That is the whole check — **do NOT run any other onchainos command** (`--version`, `upgrade`, `which`, ...) on your own initiative; then proceed to the user's request.

## Fallbacks — ignore this whole section unless its exact trigger fires

- **The `onchainos preflight` command above errored with "command not found"** (onchainos not installed) → download `install.sh` + `installer-checksums.txt` for the latest release, verify SHA256, run it, then re-run preflight (append `--beta` if this skill's version contains `-beta`; `install.ps1` on Windows). Stop only if the install itself fails.
- **A later onchainos command fails** → don't auto-reinstall; report the error and suggest a manual reinstall.
- **A command is rate-limited** → the shared API key is throttled; suggest a personal key at the [OKX Developer Portal](https://web3.okx.com/onchain-os/dev-portal), and remind the user to add any `.env` to `.gitignore`.
