# @atomicmail/agentic-core

Shared Atomic Mail runtime for integrations — PoW auth, JMAP batch execution, presets, and help topics.

Use this package when building connectors (Activepieces, custom hosts) instead of shelling out to MCP or AgentSkill.

## Install

```bash
npm install @atomicmail/agentic-core
```

## Quick start

```typescript
import {
  createAgentSessionFromKeyValue,
  runJmapRequest,
  getHelp,
} from "@atomicmail/agentic-core";

const session = await createAgentSessionFromKeyValue({
  storage: myHostKeyValueStore,
  accountId: "default",
  apiKey: process.env.ATOMIC_MAIL_API_KEY,
});

const result = await session.register("myagent01");
// result.apiKey — present on first signup

const jmap = await runJmapRequest({
  session,
  opsJson: await Deno.readTextFile("presets/list_inbox.json"),
  defaultUsing: ["urn:ietf:params:jmap:core", "urn:ietf:params:jmap:mail"],
  sourceLabel: "list_inbox.json",
});

const help = await getHelp("presets");
```

## Key exports

- `AgentSession` — register, JWT refresh, JMAP session cache
- `runJmapRequest` — preset/ops execution with `$VAR` substitution and attachments
- `getHelp`, `HELP_TOPIC_LIST` — runtime help topics
- `KeyValueCredentialStore` — persist credentials in host storage (Activepieces Store, etc.)
- `createAgentSession`, `createAgentSessionFromKeyValue` — integration session factory

Bundled assets: `shared/` presets and help topics, `presets/` JMAP JSON files.

## PoW / timeout guidance for integration hosts

- Run PoW in **flow actions** (register, jmap_request), not in connection `validate()`.
- Cache session JWTs in host storage; PoW re-runs only when JWT expires (~1h).
- Do not use sync webhooks for register or other PoW-heavy steps.

See the Atomic Mail Agentic repo for full integration guidelines.
