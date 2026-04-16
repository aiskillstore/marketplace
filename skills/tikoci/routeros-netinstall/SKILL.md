---
name: routeros-netinstall
description: "MikroTik netinstall-cli for automated RouterOS device flashing. Use when: automating netinstall, writing scripts that invoke netinstall-cli, building netinstall tooling, understanding etherboot/BOOTP/TFTP protocols, working with RouterOS package files (.npk), using modescript or configure script, or when the user mentions netinstall, etherboot, or device flashing."
---

# RouterOS Netinstall

## What Netinstall Is

Netinstall is MikroTik's tool for installing and reinstalling RouterOS on hardware devices over a direct Ethernet connection. It uses BOOTP (port 68) and TFTP (port 69) to discover devices in "etherboot" mode and transfer packages to them.

**Two variants:**
- **Netinstall for Windows** — GUI application
- **`netinstall-cli`** — Linux command-line tool (x86 ELF binary only)

Both re-format the device's system drive. The license key and RouterBOOT settings are preserved.

## netinstall-cli Command Syntax

```
netinstall-cli [-r] [-e] [-b] [-m [-o]] [-f] [-v] [-c]
               [-k <keyfile>] [-s <userscript>] [-sm <modescript>]
               [--mac <mac>] {-i <interface> | -a <client-ip>} [PACKAGES...]
```

### Flags

| Flag | Meaning |
|---|---|
| `-r` | Reinstall with default configuration (mutually exclusive with `-e`) |
| `-e` | Reinstall with empty configuration (no defaults applied) |
| `-b` | Discard branding package from device |
| `-m` | Enable multiple device reinstallation (loop). Device will be reinstalled each time it sends BOOTP |
| `-m -o` | Multiple reinstall, but each MAC only once per run |
| `-f` | Ignore storage size constraints |
| `-v` | Verbose output |
| `-c` | Allow concurrent netinstall instances on same host |
| `-k <keyfile>` | Install a license key (.KEY file) |
| `-s <userscript>` | Configure script — custom default config that replaces RouterOS-supplied default. Persists across upgrades until re-netinstalled |
| `-sm <modescript>` | Mode script — one-time first-boot script (7.22+). Runs before configure script. Auto-removed after execution. If it changes device-mode, device reboots immediately |
| `--mac <mac>` | Only serve this specific MAC address |
| `-i <interface>` | Listen on this network interface |
| `-a <client-ip>` | Assign this IP to the device (uses BOOTP server auto-detect for interface) |

### Critical Rules

1. **System package must be listed first** — `routeros-VER-ARCH.npk` must be the first package in the list
2. **Requires root/sudo** — uses privileged BOOTP (port 68) and TFTP (port 69)
3. **Multi-arch support** — provide packages for multiple architectures; netinstall auto-detects the device's architecture and selects matching packages
4. **x86 binary only** — `netinstall-cli` is an i386 Linux ELF; requires QEMU user-mode emulation on ARM/ARM64 hosts
5. **No `-r` and no `-e` = keep old config** — downloads config DB from device, reformats, re-uploads config (does NOT preserve files like Dude/UserManager databases)

### Interface vs Client-IP Mode

| Mode | Flag | How it works |
|---|---|---|
| Interface | `-i <iface>` | Listens on the specified interface, auto-detects server IP |
| Client-IP | `-a <ip>` | Assigns the specified IP to the booting device; netinstall auto-selects the interface |

In containers on RouterOS 7.21+, the VETH interface name matches the configured VETH name (e.g., `veth-netinstall`), so use `-i veth-netinstall`.

## Etherboot Mode

Devices must be in "etherboot" mode for netinstall to discover them. Methods to enter etherboot:

| Method | How |
|---|---|
| Reset button | Power off, hold reset, power on, hold until device appears in netinstall |
| Serial console | Press `Ctrl+E` during boot |
| RouterOS CLI | `/system/routerboard/settings/set boot-device=try-ethernet-once-then-nand` then reboot |
| Protected bootloader | Reset button behavior changes — must remember settings used |

**Etherboot uses BOOTP** (same ports as DHCP). On networks with DHCP servers, conflicts can occur. Best practice: use a dedicated interface/switch with no other DHCP sources.

## Configure Script vs Mode Script

| Feature | Configure Script (`-s`) | Mode Script (`-sm`) |
|---|---|---|
| When it runs | After default config is applied (on reboot) | First boot, before configure/default scripts |
| Persistence | Kept across upgrades and resets until re-netinstalled | One-time — auto-deleted after execution |
| Min version | Any RouterOS 7.x | RouterOS and netinstall-cli both >= 7.22 |
| Timeout | 120 seconds | 120 seconds |
| Use case | Custom default config replacement | Device-mode setup, protected-routerboot |
| File format | Regular `.rsc` with RouterOS CLI commands | Regular `.rsc` with RouterOS CLI commands |
| Device-mode | If script changes device-mode, reboots immediately | Same |

**Configure script variables (7.10beta8+):**
- `$defconfPassword` — factory-set admin password (read-only)
- `$defconfWifiPassword` — factory-set WiFi password (read-only)

### Mode Script for Device-Mode

The primary use case for `-sm` is enabling device-mode features on first boot without requiring manual power-cycle confirmation:

```routeros
# Enable advanced mode + container support
/system/device-mode update mode=advanced container=yes

# Enable advanced mode + container + zerotier
/system/device-mode update mode=advanced container=yes zerotier=yes
```

When the mode script changes device-mode, the device **automatically reboots** to apply the change. This replaces what would otherwise require a physical power-cycle/reset-button press.

## Package Files (.npk)

### URL Pattern

See the `routeros-fundamentals` skill ([version-parsing reference](../routeros-fundamentals/references/version-parsing.md)) for download URLs, version channels, and pre-release host selection.

```
https://download.mikrotik.com/routeros/{version}/routeros-{version}-{arch}.npk
https://download.mikrotik.com/routeros/{version}/all_packages-{arch}-{version}.zip
https://download.mikrotik.com/routeros/{version}/netinstall-{version}.tar.gz
```

**x86 exception:** x86 packages omit the architecture suffix entirely: `routeros-7.22.npk`, `container-7.22.npk` (not `routeros-7.22-x86.npk`). The `all_packages` zip does use `x86`: `all_packages-x86-7.22.zip`.

Note: Starting sometime around 7.18+, `netinstall-cli` is distributed as a `.tar.gz` containing the `netinstall-cli` binary.

### Architecture Names in Packages

| Architecture | Package suffix | Example |
|---|---|---|
| ARM | `-arm` | `routeros-7.22-arm.npk` |
| ARM64 | `-arm64` | `routeros-7.22-arm64.npk` |
| MIPS big-endian | `-mipsbe` | `routeros-7.22-mipsbe.npk` |
| MIPS multi-core | `-mmips` | `routeros-7.22-mmips.npk` |
| MIPS single-core | `-smips` | `routeros-7.22-smips.npk` |
| PowerPC | `-ppc` | `routeros-7.22-ppc.npk` |
| Tilera | `-tile` | `routeros-7.22-tile.npk` |
| x86 | *(none)* | `routeros-7.22.npk` |

### All-Packages ZIP

The `all_packages-{arch}-{version}.zip` contains all optional packages for a given architecture. Extract to get individual `.npk` files. The system package (routeros-*.npk) is also included.

## Version Resolution

Current version per channel is available as plain text — see the `routeros-fundamentals` skill ([version-parsing reference](../routeros-fundamentals/references/version-parsing.md)) for full details on channels, URL patterns, download host selection (stable vs pre-release), and version comparison logic.

**DNS retry pattern:** When running in a container at boot time, DNS may not be ready. Retry logic (5 attempts, 2s delay) is recommended for any version resolution at startup:

```makefile
# GNU make function with retry (from tikoci/netinstall Makefile)
channel_ver = $(firstword $(shell for _i in 1 2 3 4 5; do \
  _v=$$(wget -q -O - https://upgrade.mikrotik.com/routeros/NEWESTa7.$(1)) && \
  [ -n "$$_v" ] && echo "$$_v" && break; sleep 2; done))
```

## Running on Non-x86 Hosts

`netinstall-cli` is an x86 (i386) Linux ELF binary. On non-x86 hosts:

| Host | Solution |
|---|---|
| x86_64 Linux | Runs natively (kernel supports i386 binaries via `IA32_EMULATION`) |
| ARM/ARM64 Linux | QEMU user-mode emulation — prefix command with `qemu-i386-static` or `qemu-i386` |
| macOS (any arch) | Requires a full QEMU system VM with bridged networking — user-mode QEMU is Linux-only |

### ARM/ARM64 Linux — QEMU User-Mode

Auto-detect the QEMU binary and prefix transparently:

```sh
# Auto-detect: prefer local ./i386, fall back to installed static/dynamic variants
QEMU=""
for q in ./i386 qemu-i386-static qemu-i386; do
  if [ -x "$q" ] || command -v "$q" >/dev/null 2>&1; then
    QEMU="$q"; break
  fi
done
# On x86_64 the loop doesn't matter — QEMU stays empty (native)
if [ "$(uname -m)" = "x86_64" ]; then QEMU=""; fi

# Usage — QEMU prefix is a no-op when empty
${QEMU:+$QEMU} ./netinstall-cli -r -b -i eth0 routeros-7.22-arm64.npk
```

**Package notes:** Debian/Ubuntu install `qemu-user-static` → binary is `qemu-i386-static` (statically linked, safe to copy into containers). Alpine installs `qemu-i386` (dynamically linked). The `tonistiigi/binfmt` OCI image also ships `qemu-i386`.

**`binfmt_misc` alternative:** If the kernel has binfmt handlers registered (e.g., via `docker run --privileged tonistiigi/binfmt --install all`), foreign ELF binaries run transparently without any prefix.

## Network Requirements

- **Privileged ports:** BOOTP uses ports 67/68, TFTP uses port 69 — requires root/sudo
- **Direct L2 connection:** Device must be on the same Layer 2 segment as the netinstall host
- **Static IP recommended:** Configure a static IP on the host interface (e.g., 192.168.88.2/24)
- **Client IP must be unique:** The `-a` IP address must not conflict with any other device on the network
- **Link flaps:** Some USB Ethernet adapters cause link flaps that prevent device detection. Use a switch between adapter and device as workaround
- **DHCP snooping:** If using a managed switch with DHCP snooping, mark the netinstall-facing port as "trusted"

## Automation Patterns

### Single Device Install

```sh
sudo netinstall-cli -r -b -i eth0 \
  routeros-7.22-arm64.npk \
  container-7.22-arm64.npk \
  wifi-qcom-7.22-arm64.npk
```

### Multi-Device Install (Service Loop)

```sh
# Install every device that boots, each MAC once per run
sudo netinstall-cli -r -b -m -o -i eth0 \
  routeros-7.22-arm64.npk \
  container-7.22-arm64.npk
```

### With Mode Script (7.22+)

```sh
# Write modescript
cat > modescript.rsc << 'EOF'
/system/device-mode update mode=advanced container=yes
EOF

sudo netinstall-cli -r -b -sm modescript.rsc -i eth0 \
  routeros-7.22-arm64.npk \
  container-7.22-arm64.npk
```

### Containerized Netinstall on RouterOS

Run netinstall-cli inside a RouterOS container with VETH networking for "self-provisioning" — the router runs a container that can netinstall other devices on the same LAN.

Key environment variables (passed via `/container/envs`):
```routeros
/container envs add key=ARCH     list=NETINSTALL value=arm64
/container envs add key=PKGS     list=NETINSTALL value="container wifi-qcom"
/container envs add key=CHANNEL  list=NETINSTALL value=stable
/container envs add key=OPTS     list=NETINSTALL value="-b -r"
/container envs add key=IFACE    list=NETINSTALL value=veth-netinstall
```

See the `routeros-container` skill for container setup details.

## Additional Resources

**Related skills:**
- For RouterOS CLI/REST basics: see the `routeros-fundamentals` skill
- For device-mode configuration: see the `routeros-container` skill (device-mode section)

**MCP tools:**
- For RouterOS documentation lookups: use the `rosetta` MCP server tools (`routeros_search`, `routeros_get_page`)

**External docs:**
- MikroTik official docs: https://help.mikrotik.com/docs/spaces/ROS/pages/24805390/Netinstall
