---
name: whatileaked
description: Scan local Claude Code, Codex and Cursor transcripts and instruction files (CLAUDE.md, AGENTS.md) for credentials that were already sent to a model provider. Use when the user asks about leaked keys, agent history hygiene, rotating credentials, or cleaning up before sharing a machine.
---

# whatileaked

Coding agents write every session to disk. Anything pasted into a chat, or read out of a .env, stays there in plain text. Instruction files like CLAUDE.md and AGENTS.md are re-read at the start of every session, so a credential in one keeps going to the provider until the file is edited.

## Running a scan

Check whether the CLI is already available:

    whatileaked --version

If it is, run:

    whatileaked scan

If it is not, and you are working inside this repository, run it from source instead:

    node dist/cli.js scan

If neither applies, ask the user before installing anything, then:

    npm install -g whatileaked

`scan` only reads. It changes nothing, and takes about 20 seconds for a year of history.

## Reading the output

Each finding carries a rule name from gitleaks, the project the session belonged to, how many messages carried the credential, a masked line of surrounding code, and the file path. The 12 character code is a one way fingerprint, not the secret: the tool never prints a credential, so the output is safe to paste into an issue or a chat.

Two rows sharing a fingerprint are one credential reused in two places. Two different fingerprints are two different credentials.

## What to tell the user

Rotate anything real before cleaning up. The credential already reached a model provider, and deleting the local copy does not call it back.

Some findings are test fixtures. Judge them from the masked context line: `const TEST_KEY = ***` is a fixture, `AWS_ACCESS_KEY_ID=***` probably is not. Well known example keys are filtered out already.

## Wiping

Only run this when the user explicitly asks for it:

    node dist/cli.js wipe

It lists every file it would touch, then waits for the user to type the word wipe. It rewrites those files in place and cannot be undone. Never try to answer that prompt automatically, and never pipe input into it.

## Exit codes

0 means nothing was found, 1 means credentials were found, 2 means an error.
