---
name: routeros-container
description: "RouterOS /container subsystem for running OCI containers on MikroTik devices. Use when: enabling containers on RouterOS, setting up VETH/bridge networking for containers, managing container lifecycle via CLI or REST API, building OCI images for RouterOS, configuring container environment variables, troubleshooting container issues, or when the user mentions RouterOS container, /container, VETH, device-mode container, or MikroTik Docker."
---

# RouterOS Container Subsystem

## Overview

RouterOS 7.x includes a container subsystem (`/container`) that runs OCI-compatible container images directly on MikroTik hardware. It is NOT Docker — it's MikroTik's own implementation with significant differences.

**Requirements:**
- RouterOS 7.x with `container` extra package installed
- Device-mode must be enabled (requires physical access for initial setup)
- Sufficient storage (external USB disk recommended, 100+ MB/s, 10K+ random IOPS)
- ARM, ARM64, or x86 architecture (MIPS not supported for containers)

## Device-Mode — Physical Access Required

Container support is gated behind device-mode, which requires physical confirmation (reset button press or power cycle) to enable:

```routeros
# Enable container mode
/system/device-mode/update mode=advanced container=yes

# After executing: physically confirm within activation-timeout
# - Press reset button, OR
# - Power cycle the device
```

Device-mode is a general RouterOS security feature — not container-specific. It gates many features (scheduler, fetch, sniffer, etc.) across four modes (`home`, `basic`, `advanced`, `rose`) with device-dependent factory defaults.

For the full feature matrix, modes, update properties, and physical confirmation details: see the [Device-mode reference](../routeros-fundamentals/references/device-mode.md) in the `routeros-fundamentals` skill.

**Mode script bypass (7.22+):** During netinstall, a mode script (`-sm`) can set device-mode on first boot, automatically triggering a reboot. See the `routeros-netinstall` skill.

## Installing the Container Package

```routeros
# Check if container package is already installed
/system/package/print where name=container
```

**Method 1: Upload .npk file + reboot** (offline)
```sh
# Upload via SCP (or Winbox drag-and-drop, or WebFig file upload)
scp container-7.22-arm64.npk admin@router:/
```
```routeros
# Then reboot to activate
/system/reboot
```

**Method 2: Online package update** (requires internet)
```routeros
/system/package/update check-for-updates
/system/package/update install
```
This downloads and installs all available updates including extra packages. To enable a specific package already uploaded but not active, use `/system/package/enable container` then `/system/reboot`.

## Networking Setup

### VETH (Virtual Ethernet)

Containers connect to RouterOS networking via VETH interfaces:

```routeros
# Create VETH pair
/interface/veth/add name=veth-myapp address=172.17.0.2/24 gateway=172.17.0.1

# The VETH name IS the container's interface name (RouterOS 7.21+)
```

### Bridge Setup

```routeros
# Create a bridge for containers
/interface/bridge/add name=containers

# Add VETH to the bridge
/interface/bridge/port/add bridge=containers interface=veth-myapp

# Assign IP to bridge (acts as gateway for containers)
/ip/address/add address=172.17.0.1/24 interface=containers
```

### NAT / Firewall

```routeros
# Masquerade container traffic for internet access
/ip/firewall/nat/add chain=srcnat action=masquerade src-address=172.17.0.0/24

# Port forwarding from host to container
/ip/firewall/nat/add chain=dstnat action=dst-nat \
  dst-port=8080 protocol=tcp to-addresses=172.17.0.2 to-ports=80

# Allow container bridge in interface list (if firewall restricts)
/interface/list/member/add list=LAN interface=containers
```

### Layer 2 Networking (Bridge Mode)

For containers that need to be on the same L2 network as physical interfaces (e.g., netinstall):

```routeros
# Add both physical port and VETH to the same bridge
/interface/bridge/port/add bridge=mybridge interface=ether5
/interface/bridge/port/add bridge=mybridge interface=veth-netinstall
```

This gives the container direct L2 access to devices on ether5.

## Environment Variables and Mounts

There are two ways to attach env vars and mounts to a container (from 7.21+):

### Inline (preferred for 7.21+)

Set `env=` and `mount=` directly on `/container/add` — keeps the container self-contained:

```routeros
# Inline env vars and mount (7.21+)
/container/add remote-image=pihole/pihole:latest interface=veth1 \
  env="TZ=Europe/Riga,WEBPASSWORD=secret" \
  mount="src=disk1/pihole,dst=/etc/pihole" \
  root-dir=disk1/images/pihole logging=yes
```

This is also how `/app` YAML works under the hood — inline is the modern pattern and easier for automation (no separate linked objects to manage).

### Named Lists (works across all versions)

Create env vars and mounts as separate objects, then reference by name:

```routeros
# Create named env list (7.20+ uses 'list=', pre-7.20 used 'name=')
/container/envs/add list=MYAPP key=TZ value="Europe/Riga"
/container/envs/add list=MYAPP key=WEBPASSWORD value="secret"

# Create named mount
/container/mounts/add name=appdata src=disk1/appdata dst=/data

# Reference from container (7.20+ uses 'envlists=', pre-7.20 used 'envlist=')
/container/add file=myimage.tar interface=veth1 \
  envlists=MYAPP mountlists=appdata root-dir=disk1/myapp
```

**Best practice:** Always place container volumes on external disk (`disk1/`), never on internal flash storage.

### Property Name History

The naming of env/mount reference properties changed at version boundaries:

| Version | Env list grouping (`/container/envs/add`) | Container env reference (`/container/add`) | Container mount reference |
|---|---|---|---|
| Pre-7.20 | `key=`, `value=` only (no grouping property) | *(no env reference property)* | *(not available)* |
| 7.20 | `list=` added | `envlists=` (plural) added | *(not available)* |
| 7.21+ | `list=` | `envlists=` + inline `env=` | `mountlists=` + inline `mount=` |

> **Version note:** Property names for 7.20+ are confirmed against `/console/inspect` command tree data. Pre-7.20, `/container/envs/add` had only `key` and `value` with no grouping mechanism; `/container/add` had no env reference property. Inline `env=` and `mount=` were added at 7.21.

## Container Image Formats

RouterOS accepts container images in these formats:

### Option A: Pull from Registry
```routeros
/container/config/set registry-url=https://registry-1.docker.io tmpdir=disk1/pull
/container/add remote-image=library/alpine:latest interface=veth-myapp
```

### Option B: Import Local Tar File
Upload a Docker v1 tar to the router, then:
```routeros
/container/add file=myimage.tar interface=veth-myapp
```

### OCI Image Requirements for Local Import

RouterOS's container loader has specific requirements for local tar files:

1. **Single layer only** — multi-layer images are not supported
2. **No gzip compression** — layers must be uncompressed tar
3. **Docker v1 manifest format** — `manifest.json` + `config.json` + `layer.tar`

```
myimage.tar
├── manifest.json    # [{"Config":"config.json","RepoTags":["name:tag"],"Layers":["layer.tar"]}]
├── config.json      # {"architecture":"arm64","os":"linux","config":{...},"rootfs":{...}}
└── layer.tar        # Uncompressed tar of the full filesystem
```

See the `tikoci-oci-image-building` skill for building compliant images without Docker.

## Container Lifecycle

### CLI

```routeros
# Create container (7.21+ inline syntax)
/container/add file=myimage.tar interface=veth-myapp \
  env="MY_VAR=hello" mount="src=disk1/appdata,dst=/data" \
  root-dir=disk1/myapp logging=yes

# Start
/container/start [find tag~"myapp"]

# Stop
/container/stop [find tag~"myapp"]

# View status
/container/print

# View logs (if logging=yes)
/log/print where topics~"container"

# Remove (must be fully stopped first)
/container/remove [find tag~"myapp"]
```

### REST API

```typescript
const base = "http://192.168.1.1/rest";
const auth = { headers: { Authorization: `Basic ${btoa("admin:")}` } };

// List containers
const containers = await fetch(`${base}/container`, auth).then(r => r.json());

// Start container by ID
await fetch(`${base}/container/start`, {
  method: "POST", ...auth,
  headers: { ...auth.headers, "Content-Type": "application/json" },
  body: JSON.stringify({ ".id": "*1" }),
});

// Check status — .running field is "true"/"false" (strings!)
const status = await fetch(`${base}/container/*1`, auth).then(r => r.json());
if (status.running === "true") { /* container is running */ }

// Stop container
await fetch(`${base}/container/stop`, {
  method: "POST", ...auth,
  body: JSON.stringify({ ".id": "*1" }),
});

// Delete — must be fully stopped. Poll .running and retry.
async function deleteContainer(id) {
  for (let i = 0; i < 5; i++) {
    const c = await fetch(`${base}/container/${id}`, auth).then(r => r.json());
    if (c.running === "false") {
      await fetch(`${base}/container/${id}`, { method: "DELETE", ...auth });
      return;
    }
    await new Promise(r => setTimeout(r, 3000));
  }
  throw new Error("Container did not stop in time");
}
```

### REST API Gotchas for Containers

- **`.running` field** is the status indicator — values are strings `"true"` / `"false"`, not booleans
- **No `.stopped` field exists** — only check `.running`
- **Delete while stopping = HTTP 400** — must poll `.running` until `"false"` before DELETE
- **`file=` for local tar**, `remote-image=` for registry pull
- **Container `envlists=`** (plural, 7.20+) references the env list name — note the plural. Pre-7.20 used `envlist=` (singular). See env/mount version history above.

## Container Properties (from 7.22)

Selected properties from `/container/add`. This is **not exhaustive** — use `rosetta` MCP tools (`routeros_command_tree` at `/container/add`) for the full list on a specific version.

| Property | Description |
|---|---|
| `interface` | VETH interface |
| `env` | Inline environment variables (7.21+). Comma-separated `KEY=value` pairs |
| `envlists` | Named env list reference (7.20+). See env/mount section above |
| `mount` | Inline volume mount (7.21+). `src=host/path,dst=/container/path` |
| `mountlists` | Named mount list reference (7.21+). See env/mount section above |
| `root-dir` | Storage location for container filesystem |
| `file` | Container tar file (local import) |
| `remote-image` | Container image name (registry pull) |
| `cmd` | Override container CMD |
| `entrypoint` | Override container ENTRYPOINT |
| `hostname` | Container hostname |
| `dns` | DNS server for container |
| `logging` | Enable container stdout/stderr to RouterOS log (`yes`/`no`) |
| `start-on-boot` | Auto-start container on device boot (`yes`/`no`) |
| `workdir` | Override working directory |
| `name` | Container name (for `[find where name=...]`) |
| `devices` | Pass through physical devices (7.20+) |
| `cpu-list` | CPU core affinity |
| `memory-high` | RAM usage limit in bytes |

## Architecture Mapping

When pulling from registries or building images, map RouterOS architecture to Docker platform:

| RouterOS `architecture-name` | Docker Platform |
|---|---|
| `arm` | `linux/arm/v7` |
| `arm64` | `linux/arm64` |
| `x86` | `linux/amd64` |

Query the router's architecture:
```typescript
const resource = await fetch(`${base}/system/resource`, auth).then(r => r.json());
const arch = resource["architecture-name"]; // "arm64", "arm", "x86"
```

## /app System (7.21+/7.22+)

RouterOS 7.21 introduced the `/app` path (built-in app listing). Full YAML app creation (`/app/add`) was added in 7.22. See the `routeros-app-yaml` skill for the full YAML specification.

```routeros
# List available apps
/app/print

# Add app from URL
/app/add yaml-url=https://example.com/myapp.tikapp.yaml
```

### /app vs Manual Container Setup

| Concern | Manual (this page) | /app YAML |
|---|---|---|
| Networking | Full control — any bridge/VETH/L2 topology | Docker-style: `internal` subnet with port forwarding (NAT) |
| L2 bridge access | Yes — add VETH + physical port to same bridge | Not directly — but can assign a bridge post-creation via `/app/set network=<bridge>` |
| Multi-container | Manual per-container setup | Declarative YAML, multiple services |
| Use case | Raw L2 access (netinstall, DHCP relay, etc.) | Standard app deployment with port forwarding |

Netinstall specifically requires L2 bridge access for BOOTP/TFTP, which is why the manual VETH+bridge approach is used rather than /app. For typical containers that only need port-forwarded TCP/UDP services, `/app` is simpler.

## Additional Resources

**Related skills:**
- For netinstall and device-mode automation: see the `routeros-netinstall` skill
- For building OCI images compatible with RouterOS: see the `tikoci-oci-image-building` skill
- For the /app YAML format: see the `routeros-app-yaml` skill
- For general RouterOS fundamentals (CLI, REST, scripting): see the `routeros-fundamentals` skill

**MCP tools:**
- For RouterOS documentation and property lookups: use the `rosetta` MCP server tools (`routeros_search`, `routeros_get_page`, `routeros_search_properties`)

**External docs:**
- MikroTik official docs: https://help.mikrotik.com/docs/spaces/ROS/pages/84901929/Container
