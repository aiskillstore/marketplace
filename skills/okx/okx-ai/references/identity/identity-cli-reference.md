# Identity CLI Reference

## Commands

### `agent pre-check`

#### Syntax

```bash
onchainos agent pre-check --role <user|asp|evaluator> [--consent-key <uuid>]
```

Run without `--consent-key` first. After consent, reuse the returned key. Read
`canCreate`, `role`, `reason`, `consent`, and `existingSameRole`.

### `agent upload`

#### Syntax

```bash
onchainos agent upload --file <local-image-path>
```

Use only for a directly uploaded PNG, JPEG, or WebP image up to 1 MB. Read
`url` and pass the returned CDN URL as `--picture`; never pass the local path.

### `agent validate-listing`

#### Syntax

```bash
onchainos agent validate-listing --role <role> [--name <name>] [--description <text>] --service '<json-array>'
```

Use only at the ASP registration or update QA gate. Read `pass` and
`findings[]` (`field`, `severity`, `message`); never expose the diagnostic
`code`.

### `agent create`

#### Syntax

```bash
onchainos agent create --role <role> --name <name> [--description <text>] [--picture <cdn-url>] [--service '<json-array>']
```

ASP requires `description`, `picture`, and at least one service. User and
Evaluator omit `--service`. Read `newAgentId` first, then `agent.agentId` as a
fallback.

### `agent get-agents`

#### Syntax

```bash
onchainos agent get-agents --agent-ids <id[,id...]>
```

Read the returned agent array and render its display-ready `card[]` to confirm
the target identity.

### `agent service-list`

#### Syntax

```bash
onchainos agent service-list --agent-id <id> --page <n> --page-size 3 [--service-id <uuid>]
```

Use the matched record's `id`; `serviceId` is query-only. Render `cells[]`
directly and use `serviceGuide` when present.

### `agent update`

#### Syntax

```bash
onchainos agent update --agent-id <id> [--name <name>] [--description <text>] [--picture <cdn-url>] [--service '<delta-json-array>']
```

Omit unchanged identity fields. Send only service deltas defined by
[`service-contract.md`](service-contract.md). `--description ""` does not clear
a description. Success returns `txHash`; `agent` is optional.
