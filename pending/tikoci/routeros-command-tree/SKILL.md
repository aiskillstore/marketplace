---
name: routeros-command-tree
description: "RouterOS command tree introspection via /console/inspect API. Use when: building tools that parse RouterOS commands, generating API schemas from RouterOS, working with /console/inspect, mapping CLI commands to REST verbs, traversing the RouterOS command hierarchy, or when the user mentions inspect, command tree, RAML, or OpenAPI generation for RouterOS."
---

# RouterOS Command Tree & /console/inspect

## Overview

RouterOS organizes all configuration and commands in a **hierarchical tree**. Every path in the CLI
(like `/ip/address/add`) corresponds to a node in this tree. The `/console/inspect` REST endpoint
lets you **programmatically explore the entire tree** — this is how tools like `restraml` (RAML/OpenAPI
schema generator) and `rosetta` (MCP command lookup) build their databases.

## The Command Tree Structure

RouterOS's command hierarchy has four node types:

| Node Type | Meaning | Example |
|---|---|---|
| `dir` | Directory — contains child paths | `/ip`, `/system` |
| `path` | Path — a navigable level (often has commands) | `/ip/address`, `/interface/bridge` |
| `cmd` | Command — an executable action | `add`, `set`, `print`, `remove`, `get`, `export` |
| `arg` | Argument — a parameter to a command | `address=`, `interface=`, `disabled=` |

### Tree Example

```
/ (root dir)
├── ip/ (dir)
│   ├── address/ (path)
│   │   ├── add (cmd)
│   │   │   ├── address (arg) — "IP address"
│   │   │   ├── interface (arg) — "Interface name"
│   │   │   └── disabled (arg) — "yes | no"
│   │   ├── set (cmd)
│   │   ├── remove (cmd)
│   │   ├── get (cmd)
│   │   ├── print (cmd)
│   │   └── export (cmd)
│   ├── route/ (path)
│   │   └── ...
│   └── dns/ (path)
│       ├── set (cmd)
│       ├── cache/ (path)
│       │   ├── print (cmd)
│       │   └── flush (cmd)
│       └── ...
├── interface/ (dir)
│   └── ...
├── system/ (dir)
│   └── ...
└── ...
```

## /console/inspect API

### Endpoint

```
POST /rest/console/inspect
```

Requires basic authentication. Available on all RouterOS 7.x versions.

### Request Types

| Request | Purpose | Returns |
|---|---|---|
| `child` | List children of a path | Array of `{type: "child", name, "node-type"}` |
| `syntax` | Get help text for a node | Array of `{type: "syntax", text}` |
| `highlight` | Syntax highlighting data | Tokenized output (rarely used) |
| `completion` | Tab-completion suggestions | Completion candidates |

### Listing Children

```typescript
// List children of /ip
const children = await fetch(`${base}/console/inspect`, {
  method: "POST",
  headers: { ...authHeaders, "Content-Type": "application/json" },
  body: JSON.stringify({
    request: "child",
    path: "ip",
  }),
}).then(r => r.json());

// Response:
// [
//   { "type": "child", "name": "address",    "node-type": "path" },
//   { "type": "child", "name": "arp",        "node-type": "path" },
//   { "type": "child", "name": "cloud",      "node-type": "path" },
//   { "type": "child", "name": "dhcp-client", "node-type": "path" },
//   { "type": "child", "name": "dns",        "node-type": "path" },
//   { "type": "child", "name": "route",      "node-type": "path" },
//   ...
// ]
```

### Getting Syntax Help

```typescript
// Get description for /ip/address/add → address argument
const syntax = await fetch(`${base}/console/inspect`, {
  method: "POST",
  headers: { ...authHeaders, "Content-Type": "application/json" },
  body: JSON.stringify({
    request: "syntax",
    path: "ip,address,add,address",   // comma-separated path
  }),
}).then(r => r.json());

// Response:
// [{ "type": "syntax", "text": "IP address" }]
```

### Path Format

The `path` field uses **comma-separated** segments (not slashes):
- Root: `""` (empty string)
- `/ip`: `"ip"`
- `/ip/address`: `"ip,address"`
- `/ip/address/add`: `"ip,address,add"`
- `/ip/address/add → address arg`: `"ip,address,add,address"`

When using the JavaScript `Array.toString()` method, this comma-separated format is produced
naturally from an array: `["ip", "address", "add"].toString()` → `"ip,address,add"`.

## Tree Traversal Pattern

To walk the entire tree recursively:

```typescript
async function walkTree(path = [], tree = {}) {
  const children = await fetchInspect("child", path.toString());

  for (const child of children) {
    if (child.type !== "child") continue;

    const childPath = [...path, child.name];
    tree[child.name] = { _type: child["node-type"] };

    // For args, fetch the syntax description — but NOT inside dangerous subtrees
    if (child["node-type"] === "arg") {
      if (DANGEROUS_PATHS.some(p => childPath.includes(p))) continue;

      const syntax = await fetchInspect("syntax", childPath.toString());
      if (syntax.length === 1 && syntax[0].text.length > 0) {
        tree[child.name].desc = syntax[0].text;
      }
    }

    // Recurse into this child (child enumeration is safe even in dangerous subtrees)
    await walkTree(childPath, tree[child.name]);
  }

  return tree;
}
```

### Dangerous Paths — Must Skip

These path segments **crash the RouterOS REST server** when their `arg` nodes are queried
for syntax via `/console/inspect`. Always skip syntax lookups for args inside subtrees
containing any of these names:

```
where, do, else, rule, command, on-error
```

These are RouterOS scripting constructs. Specifically, **`fetchSyntax()` on `arg` node-types**
within these subtrees terminates the HTTP server process. Enumerating children (`child` request)
is safe even inside these paths — only the syntax/description lookup for arguments crashes.

The conservative approach (used in the example above) skips the entire arg when any ancestor
matches a dangerous path. The actual `rest2raml.js` implementation matches this pattern.

```typescript
const DANGEROUS_PATHS = ["where", "do", "else", "rule", "command", "on-error"];
```

## CLI Command → REST Verb Mapping

RouterOS CLI commands map to HTTP verbs in the REST API:

| CLI Command | HTTP Verb | REST URL Pattern | Notes |
|---|---|---|---|
| `get` (print) | `GET` | `/rest/ip/address` | Returns array of all entries |
| `get` (single) | `GET` | `/rest/ip/address/*1` | Single entry by ID |
| `add` | `PUT` | `/rest/ip/address` | **Creates** new entry (not POST!) |
| `set` | `PATCH` | `/rest/ip/address/*1` | Updates existing entry |
| `remove` | `DELETE` | `/rest/ip/address/*1` | Deletes entry by ID |
| `print` | `POST` | `/rest/ip/address/print` | Action-style (also works as GET) |
| Other commands | `POST` | `/rest/path/command` | Action — reboot, flush, etc. |

**Key insight:** REST `PUT` = create, `PATCH` = update. This is the **opposite** of many REST API conventions where PUT is idempotent update and POST is create.

### RAML/OpenAPI Schema Generation

When generating API schemas from the command tree:

1. Walk the tree to collect all paths, commands, and arguments
2. For each `cmd` node:
   - `get` → generates both `GET /path` (list) and `GET /path/{id}` (single)
   - `add` → generates `PUT /path` with arg-based request body
   - `set` → generates `PATCH /path/{id}` with arg-based request body
   - `remove` → generates `DELETE /path/{id}`
   - Other commands → `POST /path/command`
3. For each `arg` under a command, generate request body properties or query parameters
4. The `desc` field from syntax lookups becomes the description

### The .proplist and .query Parameters

All POST-based command endpoints accept two special parameters:
- `.proplist` — selects which properties to return (like SQL SELECT)
- `.query` — filter expression array (like SQL WHERE)

These are RouterOS REST API conventions, not standard REST patterns.

## Output Formats

The inspect tree can be converted to multiple schema formats:

### inspect.json (Raw Output)

The raw tree as returned by recursive `/console/inspect` calls. Each node has:
```json
{
  "address": {
    "_type": "path",
    "add": {
      "_type": "cmd",
      "address": { "_type": "arg", "desc": "IP address" },
      "interface": { "_type": "arg", "desc": "Interface name" }
    },
    "set": { "_type": "cmd", ... },
    "print": { "_type": "cmd", ... }
  }
}
```

### RAML 1.0 (schema.raml)

Converted to RAML 1.0 resource/method notation:
```yaml
/ip:
  /address:
    get:
      queryParameters: ...
      responses: ...
    put:
      body:
        application/json:
          properties:
            address: { type: any, description: "IP address" }
    /{id}:
      get: ...
      patch: ...
      delete: ...
```

### OpenAPI 3.0 (openapi.json)

Standard OpenAPI 3.0 schema generated from the same inspect tree (7.21.1+).

## The inspect.json Data Model

Each version's `inspect.json` is the **canonical source of truth** for that RouterOS version's
command tree. It captures:

- Every navigable path in the CLI hierarchy
- Every executable command at each path level
- Every argument (parameter) for each command
- Syntax descriptions for arguments

Tools can parse `inspect.json` offline without needing a live router — set `INSPECTFILE` env var
and the schema generator will use the cached file instead of querying a router.

## Common Patterns for Working with the Tree

### Finding Commands at a Path

```typescript
// Given an inspect.json node for /ip/address
const node = inspectData.ip.address;

// Commands are children with _type === "cmd"
const commands = Object.entries(node)
  .filter(([key, val]) => val._type === "cmd")
  .map(([key]) => key);
// → ["add", "set", "remove", "get", "print", "export", ...]
```

### Finding Arguments for a Command

```typescript
// Arguments of /ip/address/add
const addCmd = inspectData.ip.address.add;
const args = Object.entries(addCmd)
  .filter(([key, val]) => val._type === "arg")
  .map(([key, val]) => ({ name: key, description: val.desc }));
// → [{name: "address", description: "IP address"}, ...]
```

### Traversing Directories

```typescript
// Directories and paths (navigable children)
const children = Object.entries(node)
  .filter(([key, val]) => val._type === "dir" || val._type === "path")
  .map(([key]) => key);
```

## Performance Notes

- **Full tree traversal takes many minutes** against a live router (thousands of HTTP requests,
  each a separate POST to `/console/inspect`). With KVM acceleration the CHR responds quickly,
  but the sheer number of sequential requests adds up.
- Each `/console/inspect` call is a separate HTTP request — no batch API
- Use `INSPECTFILE` for development/testing to avoid repeated live queries
- The tree is version-specific — different RouterOS versions have different command sets
- Extra packages (container, iot, zerotier, etc.) add additional command tree branches

## Additional Resources

- For REST API details: see `routeros-fundamentals` skill → [REST API patterns](../routeros-fundamentals/references/rest-api-patterns.md)
- For running a CHR to query: see the `routeros-qemu-chr` skill
- For /app YAML format (a feature visible in the tree under 7.22+): see the `routeros-app-yaml` skill
