---
name: routeros-netinstall
description: "MikroTik netinstall-cli for automated RouterOS device flashing. Use when: automating netinstall, writing scripts that invoke netinstall-cli, building netinstall tooling, understanding etherboot/BOOTP/TFTP protocols, working with RouterOS package files (.npk), using modescript or configure script, or when the user mentions netinstall, etherboot, or device flashing."
---

# RouterOS Netinstall

This skill focuses on **official Netinstall / `netinstall-cli` behavior**. `tikoci/netinstall` is a useful wrapper and source of grounded examples, but it is only one way to drive the tool.

## What `netinstall-cli` Does

Netinstall reinstalls RouterOS onto a device that has booted into **etherboot** mode. The Linux tool, `netinstall-cli`, listens for BOOTP requests and then sends the RouterOS boot image and selected `.npk` packages.

Grounded behavior from MikroTik docs:

- Netinstall **re-formats the system drive**
- It **does not erase the RouterOS license key**
- It **does not reset RouterBOOT settings**
- It works over a direct **Layer 2** path using **BOOTP/DHCP ports** and **TFTP**
- It requires **root / sudo**

`netinstall-cli` is the Linux command-line variant. The Windows GUI exposes nearly the same core options.

## Command Syntax

```text
netinstall-cli [-r] [-e] [-b] [-m [-o]] [-f] [-v] [-c]
               [-k <keyfile>] [-s <userscript>] [-sm <modescript>]
               [--mac <mac>] {-i <interface> | -a <client-ip>} [PACKAGES...]
```

## Flags

| Flag | Meaning |
|---|---|
| `-r` | Reinstall and apply the default-configuration stage |
| `-e` | Reinstall with empty configuration |
| `-b` | Discard the currently installed branding package |
| `-m` | Enable repeated installs in one run |
| `-o` | With `-m`, only reinstall a given MAC once per run; by itself it behaves like a normal single install |
| `-f` | Ignore storage-size checks |
| `-v` | Verbose output |
| `-c` | Allow multiple netinstall instances on the same host |
| `-k <keyfile>` | Install a license key (`.KEY`) |
| `-s <userscript>` | Install a persistent **configure script** that replaces the RouterOS-supplied default configuration script |
| `-sm <modescript>` | Install a one-time **mode script** for the first boot after install |
| `--mac <mac>` | Only respond to this MAC address |
| `-i <interface>` | Bind to a specific interface |
| `-a <client-ip>` | Assign a specific client IP; if `-i` is used, server IP is auto-detected |

## Hard Rules

1. **The system package must be listed first.** Put `routeros-...npk` first in the package list.
2. **Root privileges are required.** Netinstall uses privileged BOOTP/TFTP ports.
3. **Multi-arch package sets are allowed.** Netinstall detects the device architecture and only uses matching packages.
4. **No `-r` and no `-e` means "keep old configuration".** Netinstall downloads the current configuration database, reformats the device, and uploads that configuration back. This does **not** preserve user files or databases such as Dude or User Manager.

## Install Workflow and Script Order

The official workflow is:

1. Put the device into **etherboot**
2. Run Netinstall with the desired packages and optional scripts
3. On the next boot, RouterOS runs the initial-configuration steps

For Linux `netinstall-cli`, the important first-boot order is:

1. **Mode script (`-sm`) runs first**
2. **Custom/default configuration runs after that**
3. If the mode script changes **device-mode**, the device **reboots immediately** after the mode script completes

That ordering matters: use `-sm` for first-boot state that must happen **before** default or custom configuration, especially **`/system/device-mode`** and **protected-routerboot**.

## Configure Script vs Mode Script

The docs use several names for the persistent `-s` script: **configure script**, **initial configuration**, and the custom default configuration script visible at:

```routeros
/system/default-configuration/custom-script/print
```

These two script types are different:

| Feature | Configure script (`-s`) | Mode script (`-sm`) |
|---|---|---|
| Purpose | Replace RouterOS-supplied default config script | One-time first-boot actions before config scripts |
| When it runs | As the device's default-configuration stage | On first boot after install, before custom/default config |
| Persistence | Stored on device | Auto-removed after execution |
| Survives upgrades | Yes | No |
| Later `/system reset-configuration` | Runs again after reset | Does not persist for later resets |
| Version requirement | Available in RouterOS 7.x docs | Requires **RouterOS 7.22+** and **netinstall-cli 7.22+** |
| Timeout | 120 seconds | 120 seconds |
| File format | Regular RouterOS import file (`.rsc`) | Regular RouterOS import file (`.rsc`) |

Additional grounded details:

- Configure scripts can read `$defconfPassword` and `$defconfWifiPassword` starting with **RouterOS 7.10beta8**
- MikroTik docs explicitly suggest introducing a **delay** before configure-script execution
- If a router was netinstalled with a configure script, later `/system reset-configuration` runs that same script again until the device is re-netinstalled without it

## Package URLs and Naming

Use the normal RouterOS download tree:

```text
https://download.mikrotik.com/routeros/{version}/routeros-{version}-{arch}.npk
https://download.mikrotik.com/routeros/{version}/all_packages-{arch}-{version}.zip
https://download.mikrotik.com/routeros/{version}/netinstall-{version}.tar.gz
```

Use `download.mikrotik.com` first for all release channels. Treat `cdn.mikrotik.com` as a fallback mirror/cache, not the primary version rule.

### Architecture suffixes

| Architecture | Package form |
|---|---|
| `arm` | `routeros-7.22-arm.npk` |
| `arm64` | `routeros-7.22-arm64.npk` |
| `mipsbe` | `routeros-7.22-mipsbe.npk` |
| `mmips` | `routeros-7.22-mmips.npk` |
| `smips` | `routeros-7.22-smips.npk` |
| `ppc` | `routeros-7.22-ppc.npk` |
| `tile` | `routeros-7.22-tile.npk` |
| `x86` | `routeros-7.22.npk` |

**x86 is the naming exception:** the package filename omits the architecture suffix, but the all-packages ZIP still uses `x86`, for example `all_packages-x86-7.22.zip`.

## Download and Run

Official Linux quick-start pattern:

```sh
wget https://download.mikrotik.com/routeros/7.22/netinstall-7.22.tar.gz
tar -xzf netinstall-7.22.tar.gz

sudo ./netinstall-cli -r -i eth0 \
  routeros-7.22-arm64.npk \
  container-7.22-arm64.npk
```

Static IP on the netinstall host is strongly recommended, for example:

```sh
sudo ifconfig eth0 192.168.88.2/24
```

## Common Scripted Cases

### Empty config

```sh
sudo ./netinstall-cli -e -b -i eth0 \
  routeros-7.22-arm64.npk
```

### Keep old configuration

```sh
sudo ./netinstall-cli -i eth0 \
  routeros-7.22-arm64.npk
```

This keeps the configuration database only; it does **not** preserve files stored on the device.

### First-boot mode script

```routeros
/system/device-mode update mode=advanced container=yes
```

```sh
sudo ./netinstall-cli -r -sm modescript.rsc -i eth0 \
  routeros-7.22-arm64.npk \
  container-7.22-arm64.npk
```

This is the main documented use for `-sm`: set device mode during the first boot without requiring a later manual confirmation flow.

## Etherboot Notes

Devices must be in **etherboot** mode before Netinstall can see them. Common entry methods:

- reset button
- serial console (`Ctrl+E`)
- RouterOS setting `boot-device=try-ethernet-once-then-nand`

Netinstall uses BOOTP/DHCP ports, so avoid other DHCP sources on the same segment. The docs also call out two common failure cases:

- some USB Ethernet adapters create an extra link flap and the device is missed
- DHCP snooping can block the packets unless the Netinstall-facing port is trusted

## Non-x86 Hosts

`netinstall-cli` is a Linux **i386 ELF** binary.

| Host | Practical approach |
|---|---|
| x86_64 Linux | Run it directly |
| ARM/ARM64 Linux | Use QEMU user-mode (`qemu-i386-static` or `qemu-i386`) |
| macOS | Run Linux in a VM with bridged networking |

This is where `tikoci/netinstall` is useful as a reference wrapper: it automates package download, QEMU-on-ARM, and macOS VM execution, but the underlying Netinstall behavior is still the same `netinstall-cli` flow documented above.

## Related References

- Official docs: <https://help.mikrotik.com/docs/spaces/ROS/pages/24805390/Netinstall>
- Reset behavior for persistent configure scripts: <https://help.mikrotik.com/docs/spaces/ROS/pages/328155/Configuration%2BManagement#ConfigurationManagement-ConfigurationReset>
- Version/channel and URL patterns: `routeros-fundamentals/references/version-parsing.md`
- Wrapper/example project: <https://github.com/tikoci/netinstall>
