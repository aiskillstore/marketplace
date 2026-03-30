# RouterOS Extra Packages

## Overview

RouterOS ships with a base feature set. Additional functionality is available via **extra packages**
(`.npk` files) that are downloaded separately and installed by uploading + rebooting.

## Package Installation

```routeros
# Via CLI — upload .npk files to root, then reboot
/system/reboot
```

```typescript
// Via REST API + SCP
// 1. Upload .npk files via SCP (or Winbox drag-and-drop, or WebFig file upload)
// scp container-7.22-arm64.npk admin@router:/

// 2. Reboot to activate
await fetch(`${base}/system/reboot`, { method: "POST", ...auth });

// Alternative: online install (requires internet)
// /system/package/update check-for-updates
// /system/package/update install
```

## Key Extra Packages

| Package | CLI Paths Added | Notable Features |
|---|---|---|
| `container` | `/container`, `/app` | Container runtime, /app YAML system |
| `iot` | `/iot` | MQTT, BLE, LoRa, GPS |
| `zerotier` | `/zerotier` | ZeroTier VPN |
| `wifi-qcom` / `wifi-qcom-ac` | `/interface/wifi` | Qualcomm WiFi drivers |
| `rose-storage` | `/disk` | Extended storage management |
| `ups` | `/system/ups` | UPS monitoring |
| `gps` | `/system/gps` | GPS receiver |
| `calea` | `/system/calea` | Lawful intercept |
| `tr069-client` | `/tr069-client` | TR-069/CWMP |
| `user-manager` | `/user-manager` | RADIUS user management |

## Download URL

Extra packages are bundled in a single zip per architecture:

```
https://download.mikrotik.com/routeros/{version}/all_packages-{arch}-{version}.zip
```

Architectures: `x86`, `arm64`, `arm`, `mipsbe`, `mmips`, `smips`, `ppc`, `tile`

**x86 naming exception:** Individual x86 `.npk` files omit the architecture suffix entirely (e.g., `container-7.22.npk` not `container-7.22-x86.npk`). The `all_packages` zip does use `x86` in its name. See [version-parsing reference](./version-parsing.md) for full download URL patterns.

## Impact on Command Tree

Installing extra packages **extends the command tree** — new paths, commands, and arguments
become visible via `/console/inspect`. This is why schema generation runs in two variants:
- **Base**: only built-in RouterOS commands
- **Extra**: all packages installed — captures the full command tree

The `/app` REST endpoint (`GET /rest/app`) specifically requires the `container` package.
Without it, the endpoint returns 404.

## Package Detection

```typescript
// Check installed packages via REST
const packages = await fetch(`${base}/system/package`, auth).then(r => r.json());
// Returns array: [{name: "routeros", version: "7.22", ...}, {name: "container", ...}]

const hasContainer = packages.some(p => p.name === "container" && !p.disabled);
```
