---
name: secret-scan
description: 'Find leaked API keys, tokens and passwords in files, commits, history or pasted text, and stop your coding agent from writing or committing them. Use when: Check a repository and its full git history before making it public; Block commits that contain API keys with a pre-commit hook; Stop Claude Code from hardcoding a key or committing one.'
license: MIT
metadata:
  author: Nex AI
  version: '1.1'
  agensi-slug: secret-scan
compatibility: 'Works with any agent that can run Python 3.8+: Claude Code, Codex, Cursor, Windsurf, Cowork. git is needed for staged, diff and history scans. The agent hook is for Claude Code.'
---

# Secret Scan

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/secret-scan). Scripts, extension source, and templates from the original package are not in this folder.

### What it does

One Python file that finds API keys, tokens, private keys and passwords **before** they reach a commit, a pushed branch, a chat message or a published package. Standard library only, **no network**: your code and secrets never leave the machine.

```bash
secret_scan.py                    # working tree
secret_scan.py --staged           # before a commit
secret_scan.py --diff origin/main # a branch or PR
secret_scan.py --history          # every commit, every branch
secret_scan.py package.zip        # a package before publishing
secret_scan.py --stdin            # text before you paste it
```

### Rules that fit real projects

- **39 provider-specific rules**: Anthropic, OpenAI, AWS, GitHub, GitLab, Stripe, Slack, Google, Groq, Supabase, Databricks, Telegram, Discord, Twilio, SendGrid, npm, PyPI, Hugging Face, Shopify, DigitalOcean, Azure and more
- Tuned heuristics for passwords, connection strings, config values, bearer tokens and committed `.env` files
- **Low noise**: placeholders, `${VAR}`, `os.environ[...]`, lockfiles and fixtures handled. Zero failing findings on two real open-source repositories of about 3,000 files
- Output is always **redacted**, with where to rotate each key. JSON and SARIF for GitHub code scanning. Baseline for existing repos

### Guard rails

- A **git pre-commit hook** that keeps your existing hook
- A **Claude Code hook** that blocks the agent from writing a key into a tracked file, or committing or pushing one (including `git add -A && git commit`, `git -C`, and first pushes), tells it to use an environment variable instead, and cannot be waved through by the agent itself

Includes a remediation playbook (rotate first, then fix, then decide about history) and CI recipes. 102 automated tests; the fake tokens in them are assembled at runtime, so the package itself scans clean.

Built by Nex AI, nex-ai.be

## When to use

- Check a repository and its full git history before making it public
- Block commits that contain API keys with a pre-commit hook
- Stop Claude Code from hardcoding a key or committing one
- Scan a package, skill or zip before publishing it
- Check text for keys before pasting it into a chat, ticket or document

## Known limitations

Pattern and entropy based: it finds the formats it knows and secret-looking assignments, and does not call providers to check whether a key is live. Skips binaries, files over 2 MB, lockfiles and source maps. History scans cover commits reachable from refs, not stashes or the reflog.

## Example

**Request**

I'm about to make this repo public. Check it for leaked keys first, including old commits.

**Result**

## Not ready to go public yet: 3 secrets found

```
$ secret_scan.py --history
CRITICAL Anthropic API key
         src/llm.py:2 @ 777f163563f4 (Dev)
         sk-a************************rS   fingerprint d0b5e145ef40a366
         rotate: Claude Console, API keys: delete the key and create a new one.
HIGH     Slack webhook URL
         src/notify.py:1 @ 19b35b09f5ed (Dev)
         http************************S7   fingerprint d560ac29ab5a8a8b
MEDIUM   Secret-looking config value
         config/settings.yml:3 @ 19b35b09f5ed (Dev)

3 finding(s) (git history): 1 critical, 1 high, 1 medium
```

The Anthropic key is no longer in the code, but it **is still in commit 777f163**. Anyone who clones the public repo gets it.

### Do this, in this order

1. **Rotate** the Anthropic key in the Claude Console and the Slack webhook in your Slack app settings. Removing them from git does not make them safe.
2. **Move the values to the environment**: I replaced them with `os.environ["ANTHROPIC_API_KEY"]`, `os.environ["SLACK_WEBHOOK_URL"]` and `${DB_PASSWORD}`, added the names to `.env.example`, and confirmed `.env` is git-ignored.
3. **Rewrite history** before publishing, since the repo is going public: `git filter-repo --replace-text` on a mirror clone (exact commands are in references/remediation.md), then push the mirror.
4. **Re-scan**: `secret_scan.py --history` must come back clean.
5. **Guard**: `secret_scan.py install-hook` blocks this at commit time from now on.

## Questions

### Does it check whether a key is live?

No. That would mean sending your keys to the provider. Treat high and critical findings as live and rotate them.

### Gitleaks and TruffleHog already exist. Why this?

They are excellent in CI. This needs nothing installed beyond Python, runs anywhere an agent runs, and comes with the agent hook and the remediation playbook.

### What if it flags something that is not a secret?

Add secret-scan: allow on the line, add the fingerprint to .secretscanignore, or create a baseline for an existing repo. In the Claude Code hook, only you can allow high and critical findings.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
