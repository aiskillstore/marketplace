# Connect Vectoree

Use this playbook for **S01–S04** and **C01**. Parent skill: `SKILL.md` in this folder (or https://raw.githubusercontent.com/VectoreeAI/vectoree-skills/main/skills/vectoree/SKILL.md)

Goal: this directory is linked to a Vectoree Cloud project, a scoped API key exists, and the key is not in git.

This is **Cloud connect** (`login` / `link`). It is **not** App Auth (login for your app's end users — see `scenarios/auth.md` / C09).

---

## S01 / C01: set up Vectoree

**Probe first.** If already connected, skip login/link:

```bash
npx @vectoree/cli whoami
npx @vectoree/cli current
npx @vectoree/cli ai chat "ping"   # ONLY install validation
```

If all three succeed, report **already connected** and stop. Do **not** re-run `login` / `link`. Do **not** probe speech / image / video / embed / transcribe during setup.

Only if probe failed:

```bash
npx @vectoree/cli login
npx @vectoree/cli link
npx @vectoree/cli ai chat "ping"
```

`login` opens a browser (PKCE). `link` interactively picks or creates a project and writes a scoped key into `.vectoree/config.json`.

Then:

1. Copy the key into `.env` as `VECTOREE_API_KEY` (and `VECTOREE_API_URL=https://vectoree.ai`).
2. Ensure `.gitignore` contains `.vectoree/` and `.env`.
3. Do not print the full key back to the user.

Done when `npx @vectoree/cli ai chat "ping"` returns a normal reply. `ai status` is optional path/config info — not a substitute for chat.

---

## S02: link this directory to an existing project

Already logged in. Run `npx @vectoree/cli link` and pick the existing project. Do not create a new one unless the user asked.

If not logged in, do S01 first.

---

## S03: CI / no browser

Do not default to `login --use-device-code`. Set env and probe:

```bash
export VECTOREE_API_URL=https://vectoree.ai
export VECTOREE_API_KEY=sk-ve-v1-your_key_here
npx @vectoree/cli ai chat "ping"
```

Create the key in Dashboard → API Keys (or from a prior `link` on a laptop).

`VECTOREE_API_URL` is the origin (no trailing `/api`).

Device code is only if the user explicitly cannot set an API key and has no loopback browser:

```bash
npx @vectoree/cli login --use-device-code
```

---

## S04: am I connected / which project?

Read-only:

```bash
npx @vectoree/cli whoami
npx @vectoree/cli current
npx @vectoree/cli ai chat "ping"
```

Do not relink unless these fail.

---

## Unlink

```bash
npx @vectoree/cli unlink            # local only
npx @vectoree/cli unlink --revoke   # also revoke the cloud key
```
