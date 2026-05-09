---
name: routeros-app-yaml
description: "RouterOS /app YAML format for container applications (7.21+ builtin app, 7.22+ custom YAML creation). Use when: writing or validating RouterOS /app YAML files, working with MikroTik container apps, building docker-compose-like definitions for RouterOS, creating /app store schemas, debugging /app validation errors, or when the user mentions /app, tikapp, or RouterOS container YAML."
---

# RouterOS /app YAML Format (7.21+)

RouterOS 7.21 introduced the `/app` path (built-in app listing and management). The full YAML app creation feature (`/app/add`) appeared in **7.22** (first seen in 7.22beta5). Think of it as MikroTik's opinionated alternative to `docker-compose` — but it is NOT docker-compose, with significant differences.

## What /app Is

The `/app` subsystem lets users define one or more containers as a single "application" in YAML. RouterOS parses the YAML, creates containers, volumes, networks, and config files, then manages the lifecycle.

**Key concepts:**
- Each `/app` is defined by a YAML document with services, configs, volumes, and networks
- The YAML is loaded into RouterOS via CLI (`/app/add yaml-url=...`) or REST API
- Built-in apps ship with RouterOS (visible at `GET /rest/app`)
- Custom apps can be added from URLs or inline YAML
- App stores (`app-store-urls=`) provide curated collections

## Critical Differences from docker-compose

| Feature | docker-compose | RouterOS /app |
|---|---|---|
| Port format | `host:container[/protocol]` | Two styles (see below) |
| Environment | `KEY=value` or list | Same, but placeholders expand |
| Volumes | Named or bind mounts | Subset — no bind mount options |
| Networks | Full docker network model | Simplified — name + external |
| Build | Full Dockerfile support | Minimal (context + dockerfile) |
| Configs | Docker configs API | Inline `content` only |
| Deploy/resources | Yes | No — not supported |
| Top-level `version:` | Deprecated (was required) | Not used |
| File extension | `.yml` / `.yaml` | `.tikapp.yaml` (convention) |

## Top-Level Properties

| Property | Type | Required | Description |
|---|---|---|---|
| `name` | string | No | Unique identifier for the /app |
| `descr` | string | No | Human-readable description shown in app UI |
| `page` | string (URI) | No | Project homepage URL |
| `category` | string (enum) | No | App store classification |
| `icon` | string (URI) | No | Icon URL (shown in WebFig with `show-in-webfig=yes`) |
| `default-credentials` | string or null | No | `username:password` shown in UI |
| `url-path` | string | No | URL path suffix for browser access (e.g., `/admin`) |
| `credentials` | string | No | Credential hint (alternative to default-credentials) |
| `option` | boolean | No | Whether app is optional |
| `auto-update` | boolean | No | Pull and restart containers on every boot |
| `services` | object | **Yes** | Container service definitions (≥1 required) |
| `volumes` | object | No | Named volume declarations |
| `networks` | object | No | Network declarations |
| `configs` | object | No | Config file declarations with inline content |

### Category Values (Exhaustive)

```
productivity, storage, networking, development, communication,
file-management, search, video, media, media-management,
home-automation, monitoring, database, automation, ai,
messaging, radio, security, business
```

New categories appear when MikroTik adds built-in apps. The CI schema validation catches these.

## Service Properties

Each key under `services:` defines one container. Required property: `image`.

| Property | Type | Description |
|---|---|---|
| `image` | string | Container image (omit registry to use `/container/config`'s `registry-url`) |
| `container_name` | string | Explicit name; used as base for file paths under `/container` |
| `hostname` | string | Container hostname |
| `entrypoint` | string or string[] | Override default entrypoint |
| `command` | string or string[] | Override default command |
| `ports` | array | Port mappings (see format section) |
| `environment` | object or array or null | Environment variables (`KEY=value` list or `{KEY: value}` map) |
| `volumes` | array of strings | Volume mounts (e.g., `my-vol:/data`) |
| `configs` | array of objects | Config file placements (`{source, target, mode}`) |
| `restart` | enum | `no`, `always`, `on-failure`, `unless-stopped` |
| `depends_on` | array or object | Service dependency ordering |
| `devices` | array of strings | Device mappings passed to container |
| `user` | string | User to run container as |
| `security_opt` | array of strings | Security options |
| `shm_size` | string | Shared memory size |
| `stop_grace_period` | string or int | Time before SIGKILL |
| `ulimits` | object | Resource limits (e.g., `nofile: {soft: 65536, hard: 65536}`) |
| `build` | object or string | Build configuration (context, dockerfile, args) |
| `healthcheck` | object | Health check (test, interval, timeout, retries, start_period) |
| `stdin_open` | boolean | Keep stdin open |
| `expose` | array | Internal ports (not published to host) |
| `secrets` | array of strings | Secrets to expose |
| `attach` | boolean | Attach to stdio |

## Port Format — Two Styles

RouterOS supports two port mapping string formats. Both are valid; new apps from 7.23beta2+ prefer the colon style.

### Old OCI-style (pre-7.23)

```
[ip:]host_port:container_port[/tcp|/udp][:label]
```

Examples:
```yaml
ports:
  - "8080:80/tcp"
  - "8443:443/tcp:https"
  - "192.168.1.1:53:53/udp:dns"
```

### New RouterOS style (7.23+)

```
[ip:]host_port:container_port[:label][:tcp|:udp]
```

Protocol is appended with colon instead of slash:
```yaml
ports:
  - "8080:80:web:tcp"
  - "8443:443:https:tcp"
  - "53:53:dns:udp"
```

### Long-form (object) syntax

```yaml
ports:
  - target: 80
    published: 8080
    protocol: tcp
    name: web
    app_protocol: http
```

### IP Addresses and Placeholders in Ports

Port strings can include literal IPs or placeholder expressions:
```yaml
ports:
  - "[accessIP]:[accessPort]:80/tcp:web"      # Old style with placeholders
  - "[accessIP]:[accessPort]:80:web:tcp"       # New style with placeholders
```

## Placeholders

RouterOS expands these placeholders at deploy time:

| Placeholder | Expands to |
|---|---|
| `[accessIP]` | IP address for accessing the app from outside |
| `[accessPort]` | Primary host port for external access |
| `[accessPort2]` | Secondary host port |
| `[containerIP]` | IP address assigned to the container |
| `[routerIP]` | Router's own IP address |

Placeholders appear in port mappings, environment values, and config content.

## Configs (Inline Files)

Top-level `configs:` declares config content; services reference them:

```yaml
configs:
  my-config:
    content: |
      server {
        listen 80;
        server_name [accessIP];
      }

services:
  web:
    image: nginx:alpine
    configs:
      - source: my-config
        target: /etc/nginx/conf.d/default.conf
        mode: 0644
```

## Volumes and Networks

```yaml
volumes:
  app-data: {}      # Named volume (null or empty object)

networks:
  app-net:
    name: my-network
    external: true   # Use existing RouterOS network
```

## Store Schema (app-store-urls)

RouterOS can load app collections from URLs configured via `app-store-urls=`. The store format is simply a **YAML array** of /app definitions:

```yaml
- name: app-one
  services:
    web:
      image: nginx:alpine
- name: app-two
  services:
    db:
      image: postgres:16
```

Store files use the `.tikappstore.yaml` extension by convention.

## REST API for /app

```typescript
// List all /app entries (built-in + custom)
const apps = await fetch(`${base}/app`, auth).then(r => r.json());

// Each entry has: .id, name, yaml (raw YAML string), and metadata
// The 'yaml' field is a RouterOS string containing the full YAML document

// Add a custom /app from URL
await fetch(`${base}/app`, {
  method: "PUT",
  ...auth,
  body: JSON.stringify({ "yaml-url": "https://example.com/my-app.tikapp.yaml" }),
});
```

**Note:** The `/app` endpoint requires the **container** extra package to be installed.

## JSON Schema for Validation

Two schema variants exist for each /app document:

| Schema | Purpose | Port validation | Env var names |
|---|---|---|---|
| `*.latest.json` | CI/strict validation | Regex patterns enforced | `^[A-Z_][A-Z0-9_]*$` only |
| `*.editor.json` | Editor/SchemaStore UX | No regex (allows autocompletion) | Case-insensitive |

The strict schema has regex `pattern` on port strings which **prevents VSCode autocompletion** — the YAML extension won't suggest values for fields with patterns. The editor variant removes these patterns.

### VSCode Integration

Add to VSCode settings for YAML autocompletion:
```json
{
  "yaml.schemas": {
    "https://tikoci.github.io/restraml/routeros-app-yaml-schema.latest.json": "*.tikapp.yaml",
    "https://tikoci.github.io/restraml/routeros-app-yaml-store-schema.latest.json": "*.tikappstore.yaml"
  }
}
```

Use `.editor.json` URLs for better autocompletion at the cost of less strict validation.

## Version History

- **7.22**: Initial /app support with basic service properties
- **7.23beta2**: New colon-style port format (`:tcp`/`:udp` suffix)
- **7.23+**: Additional service properties (`devices`, `expose`, `secrets`, `attach`)

## Common Mistakes

- **Assuming docker-compose compatibility** — not all properties are supported, some behave differently
- **Using `version:` key** — RouterOS ignores it; not needed
- **Mixing port format styles** in a single entry — each port string must use ONE style exclusively
- **Uppercase env var names required** in strict validation — use `*.editor.json` for mixed case
- **Forgetting the container package** — `/app` returns 404 without the `container` extra package
- **Using `deploy:` or `resources:`** — not supported by RouterOS

## Additional Resources

- For RouterOS fundamentals, CLI syntax, REST API: see the `routeros-fundamentals` skill
- For running CHR in QEMU (needed to test /app): see the `routeros-qemu-chr` skill
- MikroTik forum reference: https://forum.mikrotik.com/t/amm0s-manual-for-custom-app-containers-7-22beta/268036/22
