---
name: routeros-fundamentals
description: "RouterOS v7 domain knowledge for AI agents. Use when: working with MikroTik RouterOS, writing RouterOS CLI/script commands, calling RouterOS REST API, debugging why a Linux command fails on RouterOS, or when the user mentions MikroTik, RouterOS, CHR, or /ip /system /interface paths. Scope: RouterOS 7.x (long-term and newer) only — v6 is NOT covered and accuracy for v6 problems will be low."
---

# RouterOS Fundamentals

## RouterOS Is NOT GNU/Linux

RouterOS runs a Linux kernel (5.6.3) but **everything above the kernel is MikroTik's proprietary `nova` system**. This is the single most important fact for agents to internalize.

**What does NOT exist on RouterOS:**
- No `/bin`, `/usr`, `/etc`, `/var` — no FHS layout
- No bash, sh, ash, zsh — no Unix shell at all
- No coreutils (`ls`, `cat`, `grep`, `ps`, `mount`, `ip`, `iptables`, etc.)
- No glibc, musl, busybox
- No apt, pkg, opkg — no package manager (packages are `.npk` files installed via upload + reboot)
- No `systemctl`, `service`, init system
- No `/proc` or `/sys` accessible from userland
- No `docker`, `podman` — RouterOS has its own `/container` subsystem (7.x+)

**What DOES exist:**
- RouterOS CLI — its own language, not shell. Accessed via SSH, serial, WinBox, or WebFig
- REST API at `/rest/` (HTTP, port 80 by default) — the primary programmatic interface
- RouterOS scripting language (`.rsc` files) — its own syntax, not bash. See [Scripting reference](./references/scripting.md)
- WebFig (web UI) on port 80
- WinBox protocol on port 8291

**Common agent mistakes to avoid:**
- Do NOT try `ssh admin@host 'ls /'` — it opens RouterOS CLI, not a shell
- Do NOT suggest `mount`, `fdisk`, `mkfs` — use `/disk` commands instead
- Do NOT look for config files at `/etc/` — configuration is in the RouterOS database
- Do NOT assume `ping` works the same — it's `/tool/ping` or `/ping` in CLI
- Do NOT suggest installing packages via `apt` or `opkg` — upload `.npk` via SCP then `/system/reboot`
- See [Extra packages reference](./references/extra-packages.md) for the full package list and installation pattern

## RouterOS CLI Syntax

RouterOS CLI uses path-based navigation, not Unix command pipelines:

```routeros
# Navigation
/ip/address/print
/interface/print
/system/resource/print

# Adding entries
/ip/address/add address=192.168.1.1/24 interface=ether1

# Modifying (by internal ID or find expression)
/ip/address/set [find interface=ether1] address=10.0.0.1/24

# Removing
/ip/address/remove [find address="192.168.1.1/24"]

# Running a command
/system/reboot
/tool/fetch url="http://example.com/file.npk" dst-path="/"
```

**Key syntax differences from shell:**
- `=` assigns properties (no spaces around it)
- `[find ...]` is the query expression (like WHERE)
- Strings use `""` (double quotes only)
- Comments use `#`
- Variables: `:local myVar "value"` and `$myVar`
- No pipes, no redirection, no subshell

## REST API Patterns

RouterOS REST API (v7.x+) at `http://HOST:PORT/rest/`:

```typescript
// Base pattern — use fetch() or Bun-native HTTP
const base = "http://192.168.1.1/rest";
const auth = { headers: { Authorization: `Basic ${btoa("admin:")}` } };

// GET = print (list/read)
const interfaces = await fetch(`${base}/interface`, auth).then(r => r.json());

// PUT = add (create new entry)
await fetch(`${base}/ip/address`, {
  method: "PUT",
  ...auth,
  headers: { ...auth.headers, "Content-Type": "application/json" },
  body: JSON.stringify({ address: "192.168.1.1/24", interface: "ether1" }),
});

// PATCH = set (modify existing)
await fetch(`${base}/ip/address/*1`, {
  method: "PATCH",
  ...auth,
  body: JSON.stringify({ address: "10.0.0.1/24" }),
});

// DELETE = remove
await fetch(`${base}/ip/address/*1`, { method: "DELETE", ...auth });

// POST = command (execute an action)
await fetch(`${base}/ip/dns/cache/flush`, { method: "POST", ...auth });
```

**REST gotchas:**
- `PUT` creates, `PATCH` updates — opposite of many APIs
- Empty password: `admin:` (colon required, empty string after)
- WebFig (port 80, GET `/`) returns HTTP 200 without auth — useful for health checks
- REST API (`/rest/`) returns HTTP 401 without auth
- Property names may differ from CLI names (hyphens vs underscores vary by version)
- `.id` field is `*HEX` format (e.g., `*1`, `*A`)
- POST to `/rest/system/reboot` — no body needed for action commands

## Version Scheme

Format: `MAJOR.MINOR[.PATCH][betaN|rcN]` — e.g., `7.22`, `7.22.1`, `7.23beta2`, `7.22rc1`

**Channels** (from `upgrade.mikrotik.com/routeros/NEWESTa7.<channel>`):
- `stable` — production recommended
- `long-term` — conservative, gets backported fixes
- `testing` — pre-release candidates
- `development` — beta features

```typescript
// Resolve current version for a channel
const version = await fetch(
  "https://upgrade.mikrotik.com/routeros/NEWESTa7.stable"
).then(r => r.text());
```

**Download URLs:**
- Standard: `https://download.mikrotik.com/routeros/<ver>/chr-<ver>.img.zip` (x86_64)
- ARM64: `https://download.mikrotik.com/routeros/<ver>/chr-<ver>-arm64.img.zip`

## Architecture Names

MikroTik uses these architecture identifiers (not standard Linux arch names):

| MikroTik name | CPU | Common hardware |
|---|---|---|
| `x86` | x86_64 | CHR, x86-based RouterBOARDs |
| `arm64` | aarch64 | Modern ARM boards (RB5009, Chateau) |
| `arm` | ARMv7 | Older ARM boards |
| `mipsbe` | MIPS big-endian | Legacy RouterBOARDs |
| `mmips` | MIPS multi-core | hAP ac, RB4011 |
| `smips` | MIPS single-core | hAP lite, mAP |
| `ppc` | PowerPC | CCR1xxx series |
| `tile` | Tilera | CCR (older models) |

CHR (Cloud Hosted Router) is available only for `x86` and `arm64`.

## Default Credentials

- Username: `admin`
- Password: (empty — no password)
- On first login via SSH/console, RouterOS 7.x prompts to set a password or press `a` to skip
- REST API and WebFig allow empty-password access

## Inspecting Hardware from RouterOS CLI

```routeros
# PCI devices (the RouterOS equivalent of lspci)
/system/resource/hardware/print

# IRQ assignments (shows driver binding)
/system/resource/irq/print

# System overview
/system/resource/print

# Disk info
/disk/print

# Installed packages
/system/package/print

# IP services and ports
/ip/service/print

# Network interfaces
/interface/print
```

## Additional Resources

**Reference files:**
- For REST API details and `/console/inspect` command tree: see [REST API reference](./references/rest-api-patterns.md)
- For version parsing, comparison, and download URL logic: see [Version parsing reference](./references/version-parsing.md)
- For extra packages (container, iot, zerotier, etc.): see [Extra packages reference](./references/extra-packages.md)
- For device-mode (modes, feature matrix, physical confirmation): see [Device-mode reference](./references/device-mode.md)
- For RouterOS scripting language syntax: see [Scripting reference](./references/scripting.md)

**Related skills:**
- For the /container subsystem (VETH, device-mode, lifecycle): see the `routeros-container` skill
- For netinstall-cli and device flashing: see the `routeros-netinstall` skill
- For the /app YAML container format (7.22+): see the `routeros-app-yaml` skill
- For /console/inspect tree traversal and schema generation: see the `routeros-command-tree` skill
- For running CHR in QEMU (local or CI): see the `routeros-qemu-chr` skill
- For QEMU user-mode emulation and macOS VM bridging: see the `tikoci-qemu-user-emulation` skill
- For building OCI images for RouterOS: see the `tikoci-oci-image-building` skill

**MCP tools:**
- For command tree browsing and property lookups: use the `rosetta` MCP server tools (`routeros_search`, `routeros_get_page`, `routeros_command_tree`)
