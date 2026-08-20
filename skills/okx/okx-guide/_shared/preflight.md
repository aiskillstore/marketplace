# Shared Pre-flight Check

> Run ONCE at the start of each conversation, before the first `onchainos` command; don't repeat it on later turns.

## Default — do this, then stop

1. Run: `onchainos preflight --skill-version <this skill's frontmatter version>`
2. Read `data.action` from the JSON it prints (preflight always exits 0 — don't block on it):
   - **null** → continue silently; don't echo routine output.
   - **non-null** → show it to the user (their language) and do exactly what it says (e.g. re-read this SKILL.md; for a package-manager skill, update via its manager; on integrity/update failure run `onchainos upgrade --force`).

`preflight` already updates the binary + skill checkouts, verifies integrity, and reports version + drift. That is the whole check — **do NOT run any other onchainos command** (`--version`, `upgrade`, `which`, ...) on your own initiative; then proceed to the user's request.

## Fallbacks — ignore this whole section unless its exact trigger fires

- **The `onchainos preflight` command above errored with "command not found"** (onchainos not installed) → open the README "Install CLI" section (`https://github.com/okx/onchainos-skills?tab=readme-ov-file#install-cli`), identify the current OS, and run the install command from that section matching it (macOS/Linux: the shell command; Windows: the PowerShell command); use the `-beta` install variant if this skill's frontmatter version contains `-beta`. Then re-run preflight (`onchainos preflight --skill-version <this skill's frontmatter version>`) and continue the user's original request. Stop only if the install itself fails.
- **A later onchainos command fails** → don't auto-reinstall; report the error and suggest a manual reinstall.
- **A global install printed `PromptScript does not support global skill installation`** (only with `npx skills add … --yes -g`) → known upstream `npx skills` limitation: the skill files installed correctly. Tell the user it's safe to ignore.
