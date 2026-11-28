---
name: api-guardian
description: "Keep OpenAI, Anthropic, GitHub, or Stripe API keys out of plaintext .env files where coding agents might leak them: tiny zero-dependency Python CLI and Agent Skill that stores secrets in your system password vault (macOS Keychain, Windows Credential Manager, or Linux Secret Service / secret-tool), shows masked previews, and injects credentials into environment variables only when running a command. 不想把API Key明文写在.env文件里怕AI写代码泄露？将密钥存进电脑系统自带密码库/钥匙串，默认掩码脱敏，运行命令时临时注入子进程环境变量。"
license: MIT
---

# API Guardian

## Overview

Use this skill to handle API keys and tokens as secrets. Prefer the bundled `scripts/api_guard.py` helper so credentials live in an OS-backed secret store and are injected into commands without being printed.

## Security Rules

- Never include raw API keys, bearer tokens, refresh tokens, passwords, private keys, or webhook signing secrets in final responses.
- Never write secrets to `.env`, config files, logs, notebooks, screenshots, transcripts, or git-tracked files unless the user explicitly requests a file-based credential workflow.
- Prefer hidden prompts, stdin, or already-set environment variables over command-line arguments because shell history and process listings can expose arguments.
- Use placeholders such as `<API_KEY>` in examples and documentation.
- Before committing, check for accidental secrets with `git status`, `git diff --cached`, and a targeted scan for likely secret files or token-looking strings.
- If a secret is exposed, treat it as compromised: tell the user to rotate it, remove it from files/history, and store the replacement with this skill.

## Bundled Helper

Use `scripts/api_guard.py` from this skill directory.

Supported stores:

- Windows: Windows Credential Manager via DPAPI-protected user credentials.
- macOS: Keychain through `/usr/bin/security`.
- Linux: Secret Service through `secret-tool`; fail closed if unavailable.

The helper intentionally has no plaintext fallback.

## Common Workflows

### Store a Credential

Prefer a hidden prompt:

```bash
python scripts/api_guard.py store openai
```

Use stdin when another tool supplies the key:

```bash
printf "%s" "$OPENAI_API_KEY" | python scripts/api_guard.py store openai --stdin
```

Use an existing environment variable:

```bash
python scripts/api_guard.py store openai --from-env OPENAI_API_KEY
```

### Use a Credential Without Printing It

Inject the stored secret into a child process:

```bash
python scripts/api_guard.py run openai OPENAI_API_KEY -- python app.py
```

For shell commands, pass the command after `--`:

```bash
python scripts/api_guard.py run openai OPENAI_API_KEY -- npm test
```

### Retrieve a Credential

Default retrieval is redacted:

```bash
python scripts/api_guard.py get openai
```

Only reveal when the user explicitly needs the raw value:

```bash
python scripts/api_guard.py get openai --reveal
```

Do not paste a revealed secret into chat. If the secret must be moved, prefer a direct command pipeline or environment injection.

### List or Delete Credentials

```bash
python scripts/api_guard.py list
python scripts/api_guard.py delete openai
```

### Rotate a Credential

1. Ask the provider to create or regenerate the replacement key.
2. Store the replacement under the same logical name:

```bash
python scripts/api_guard.py store openai
```

3. Run a smoke test with `run`.
4. Revoke the old key in the provider console.

## Naming

Use short logical names such as `openai`, `github`, `stripe-prod`, `stripe-test`, or `anthropic-dev`. Do not put the secret value in the name.

## Git Safety Checklist

Before staging or pushing work that involved credentials:

```bash
git status --short
git diff
git diff --cached
```

Also inspect likely local secret files:

```bash
git ls-files --others --exclude-standard
```

If `.env`, credential JSON, PEM files, or token caches appear, add safe ignore rules or remove the files from the repo before committing.
