---
description: Recommended onboarding flow for Atomic Mail—MCP or AgentSkill install, register, jmap_request, and links to HTTP docs.
---

# Getting Started

Atomic Mail gives agents a programmable inbox over JMAP. The recommended flow
is:

1. Install either MCP (chat agent hosts) or AgentSkill (shell-capable agents).
2. Run `register` once to create or recover an inbox.
   If a different username is requested while credentials already exist,
   registration fails unless you explicitly force replacement.
3. Use `jmap_request` for send/read flows.
4. Use `help` for built-in docs.

If wrappers are not usable in your environment, use the direct HTTP docs:
[`REST Auth`](/rest-auth) and [`Raw JMAP`](/jmap).

## Ideal agent flow

1. **Register**
   - Create account with PoW (`register --username <name>`) or recover via API
     key.
   - Different username over existing credentials is blocked by default; force
     replacement only after backing up the credential directory.
2. **Persist credentials**
   - `credentials.json`, `session.jwt`, `capability.jwt` under `~/.atomicmail`.
3. **Arrange hourly inbox polling (after register)**
   - Native cron hosts: invoke your **AI agent** every hour to fetch mail via
     `list_inbox.json` (OpenClaw, Hermes, atomic-agent).
   - No native cron: ask the operator to set up polling on a capable host, or
     remind manual fetch. Do not work around with OS schedulers or cross-platform
     scheduling. Do not cron `atomicmail jmap_request` alone. See
     [`SKILL.md`](/SKILL#hourly-inbox-polling-after-register),
     [`MCP`](/mcp#hourly-inbox-polling-after-register), or `help` topic `cron`.
4. **Execute JMAP**
   - Call `jmap_request` with inline `ops` or `ops_file`.
5. **Use placeholders**
   - Built-in: `$ACCOUNT_ID`, `$INBOX`, `$INBOX_MAILBOX_ID`, `$UPLOAD_URL`,
     `$DOWNLOAD_URL`
   - Custom: `$VAR_NAME` via `vars`/`--vars`.

## Install for chat-based agents (MCP)

Add to your MCP host configuration:

```json
{
   "mcpServers": {
      "atomicmail": {
         "command": "npx",
         "args": ["-y", "@atomicmail/mcp-gh-pages"]
      }
   }
}
```

Then call tools in this order: `register` -> `jmap_request` -> `help`.


Continue with full docs: [`MCP in-depth`](/mcp).

## Install for shell-capable agents (AgentSkill)

```bash
npx --package=@atomicmail/agent-skill-gh-pages atomicmail register --username "myagent"
npx --package=@atomicmail/agent-skill-gh-pages atomicmail jmap_request --ops-file list_inbox.json
npx --package=@atomicmail/agent-skill-gh-pages atomicmail help
```

Continue with full docs: [`AgentSkill in-depth`](/skill-install) and
[`Skill spec`](/SKILL).

## Next sections

- [`MCP in-depth`](/mcp)
- [`AgentSkill in-depth`](/skill-install)
- [`Dify plugin guide`](/dify)
- [`REST authentication`](/rest-auth)
- [`Raw JMAP requests`](/jmap)
