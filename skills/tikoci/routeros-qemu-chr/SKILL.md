---
name: routeros-qemu-chr
description: 'MikroTik RouterOS CHR (Cloud Hosted Router) with QEMU. Use when: running RouterOS in QEMU, booting CHR images, debugging CHR boot failures, setting up VirtIO devices for RouterOS, choosing between SeaBIOS and UEFI boot, configuring QEMU port forwarding for RouterOS REST API, or selecting QEMU acceleration (KVM/HVF/TCG).'
---

# RouterOS CHR with QEMU

## What Is CHR

Cloud Hosted Router (CHR) is MikroTik's x86_64 and aarch64 RouterOS image designed for virtual machines. Free license allows unlimited use with 1 Mbps speed limit — sufficient for development, testing, and API work. Full-speed paid licenses also exist.

## Image Variants

| Image | Architecture | Boot method | Source |
|---|---|---|---|
| `chr-<ver>.img` | x86_64 | SeaBIOS (MBR chain-load) | download.mikrotik.com |
| `chr-<ver>-arm64.img` | aarch64 | UEFI (EDK2 pflash) | download.mikrotik.com |
| `chr-efi.img` (fat-chr) | x86_64 | UEFI (OVMF) | tikoci/fat-chr GitHub |

**Standard x86 image has a proprietary boot partition** — it looks like an EFI System Partition in GPT but is NOT FAT. UEFI firmware (OVMF) cannot read it. Only SeaBIOS can boot it via MBR chain-load.

The `fat-chr` repackaged image converts this to standard FAT16 with `EFI/BOOT/BOOTX64.EFI`, enabling UEFI boot. Required for Apple Virtualization.framework on X86 macOS, optional everywhere else.

**Disk layout** (128 MiB, both architectures): Hybrid GPT+MBR, partition 1 = boot (~33 MiB), partition 2 = ext4 root (~94 MiB).

## Downloading CHR Images

```typescript
// Resolve current version
const channel = "stable"; // or: long-term, testing, development
const version = await fetch(
  `https://upgrade.mikrotik.com/routeros/NEWESTa7.${channel}`
).then(r => r.text()).then(s => s.trim());

// Download x86_64 image
const url = `https://download.mikrotik.com/routeros/${version}/chr-${version}.img.zip`;
// Download aarch64 image
const armUrl = `https://download.mikrotik.com/routeros/${version}/chr-${version}-arm64.img.zip`;
```

Images are distributed as `.img.zip` — unzip to get the raw `.img` disk file.

## Pattern Choices: QEMU Invocation

There are several valid approaches to launching CHR under QEMU. Each has tradeoffs:

### Pattern A: Inline arguments (simplest, good for scripts)

Everything on the command line. Easy for an LLM to construct and debug — all state is visible in one place.

```sh
qemu-system-x86_64 -M q35 -m 256 -smp 1 \
  -drive file=chr.img,format=raw,if=virtio \
  -netdev user,id=net0,hostfwd=tcp::9180-:80 \
  -device virtio-net-pci,netdev=net0 \
  -display none -serial stdio
```

**Pros:** Single command, easy to read, easy to modify.
**Cons:** Long command lines, hard to version-control, no persistence.

### Pattern B: Wrapper script (good for reuse)

A shell script that detects acceleration, handles firmware paths, manages PID files.

```sh
#!/bin/sh
# detect acceleration
if [ "$(uname -s)" = "Linux" ] && [ -w /dev/kvm ]; then
  ACCEL="-accel kvm"
elif [ "$(uname -s)" = "Darwin" ] && [ "$(sysctl -n kern.hv_support 2>/dev/null)" = "1" ]; then
  ACCEL="-accel hvf"
else
  ACCEL="-accel tcg"
fi

qemu-system-x86_64 -M q35 -m 256 -smp 1 \
  $ACCEL \
  -drive file=chr.img,format=raw,if=virtio \
  -netdev user,id=net0,hostfwd=tcp::${PORT:-9180}-:80 \
  -device virtio-net-pci,netdev=net0 \
  -display none -serial stdio
```

**Pros:** Portable, handles platform differences, parameterizable.
**Cons:** Shell scripting limitations, harder to compose from TypeScript.

### Pattern C: Programmatic launch from Bun/TypeScript (good for integration tests)

Launch QEMU as a child process with full control:

```typescript
import { $ } from "bun";

const port = 9180;
const accel = await detectAccel();
const proc = Bun.spawn([
  "qemu-system-x86_64", "-M", "q35", "-m", "256",
  "-accel", accel,
  "-drive", `file=chr.img,format=raw,if=virtio`,
  "-netdev", `user,id=net0,hostfwd=tcp::${port}-:80`,
  "-device", "virtio-net-pci,netdev=net0",
  "-display", "none",
  "-chardev", `socket,id=serial0,path=/tmp/chr-serial.sock,server=on,wait=off`,
  "-serial", "chardev:serial0",
  "-monitor", `unix:/tmp/chr-monitor.sock,server,nowait`,
], { stdio: ["ignore", "pipe", "pipe"] });

// Wait for boot
await waitForBoot(`http://127.0.0.1:${port}/`);
```

**Pros:** Full lifecycle control, parallel instance management, TypeScript-native.
**Cons:** More code, QEMU args still need to be correct.

### Pattern D: Config file (`--readconfig`) (declarative, used by mikropkl)

QEMU's `--readconfig` loads an INI-format file for device/machine config. The mikropkl project uses this for its declarative VM packaging.

**Tradeoffs:** Separates concerns (config vs launch), but the INI format is obscure and not all QEMU options can be expressed in it (pflash, `-accel`, `-netdev user,hostfwd` all require command-line args). Best suited for projects that generate configs programmatically.

## Boot Tracks

### x86_64 with SeaBIOS (default, fastest)

No firmware setup needed — QEMU's built-in SeaBIOS handles MikroTik's proprietary boot sector:

```sh
qemu-system-x86_64 -M q35 -m 256 \
  -drive file=chr-7.22.img,format=raw,if=virtio \
  -netdev user,id=net0,hostfwd=tcp::9180-:80 \
  -device virtio-net-pci,netdev=net0 \
  -display none -serial stdio
```

Boot time: ~5s (KVM), ~30s (TCG).

### aarch64 with UEFI (EDK2)

Requires UEFI pflash firmware files. **Both pflash units must be identical size** (typically 64 MiB):

```sh
# Copy vars file (writable) — never modify the original
cp /path/to/edk2-arm-vars.fd /tmp/my-vars.fd

qemu-system-aarch64 -M virt -cpu cortex-a710 -m 256 \
  -drive if=pflash,format=raw,readonly=on,unit=0,file=/path/to/edk2-aarch64-code.fd \
  -drive if=pflash,format=raw,unit=1,file=/tmp/my-vars.fd \
  -drive file=chr-arm64.img,format=raw,if=none,id=drive0 \
  -device virtio-blk-pci,drive=drive0 \
  -netdev user,id=net0,hostfwd=tcp::9180-:80 \
  -device virtio-net-pci,netdev=net0 \
  -display none -serial stdio
```

Boot time: ~10s (KVM), ~20s (TCG native), ~20s (TCG cross-arch on x86 host).

### UEFI Firmware Locations

| Platform | Code ROM | Vars File |
|---|---|---|
| macOS Homebrew (Apple Silicon) | `/opt/homebrew/share/qemu/edk2-aarch64-code.fd` | `edk2-arm-vars.fd` |
| macOS Homebrew (Intel) | `/usr/local/share/qemu/edk2-aarch64-code.fd` | `edk2-arm-vars.fd` |
| Ubuntu/Debian | `/usr/share/AAVMF/AAVMF_CODE.fd` | `AAVMF_VARS.fd` |
| x86 OVMF (Homebrew) | `edk2-x86_64-code.fd` | `edk2-i386-vars.fd` |
| x86 OVMF (Linux) | `/usr/share/OVMF/OVMF_CODE.fd` | `OVMF_VARS.fd` |

## VirtIO — Critical Details

See the [VirtIO driver matrix](./references/virtio-drivers.md) for the full table.

**The one rule:** RouterOS has `virtio_pci` but NOT `virtio_mmio`. This matters on aarch64.

### The `if=virtio` Trap (aarch64)

```
                         x86_64 (q35)              aarch64 (virt)
if=virtio shorthand →    virtio-blk-pci (PCI) ✅    virtio-blk-device (MMIO) ❌
-device virtio-blk-pci → virtio-blk-pci (PCI) ✅    virtio-blk-pci (PCI) ✅
```

On x86_64 `q35`, `if=virtio` resolves to PCI — works fine. On aarch64 `virt`, it resolves to MMIO — **RouterOS kernel stalls silently**. Always use explicit `-device virtio-blk-pci` on aarch64:

```sh
# WRONG on aarch64 — silent boot failure
-drive file=chr.img,format=raw,if=virtio

# CORRECT on aarch64 — explicit PCI device
-drive file=chr.img,format=raw,if=none,id=drive0
-device virtio-blk-pci,drive=drive0
```

On x86_64, both work. The explicit form is always safe on both architectures.

### Network — Universal

All architectures: `virtio-net-pci`. No exceptions:

```sh
-netdev user,id=net0,hostfwd=tcp::9180-:80
-device virtio-net-pci,netdev=net0
```

## Acceleration Detection

```typescript
import { $ } from "bun";

async function detectAccel(guestArch: string): Promise<string> {
  const hostOs = process.platform;  // "darwin" | "linux"
  const hostArch = process.arch;    // "x64" | "arm64"

  if (hostOs === "linux") {
    // KVM requires host/guest architecture match
    const kvm = await Bun.file("/dev/kvm").exists();
    const archMatch = (guestArch === "x86_64" && hostArch === "x64")
      || (guestArch === "aarch64" && hostArch === "arm64");
    if (kvm && archMatch) return "kvm";
  }

  if (hostOs === "darwin") {
    // HVF may not be available (e.g., GitHub Actions VMs)
    const hvOk = await $`sysctl -n kern.hv_support`.text().then(s => s.trim() === "1").catch(() => false);
    const archMatch = (guestArch === "aarch64" && hostArch === "arm64")
      || (guestArch === "x86_64" && hostArch === "x64");
    if (hvOk && archMatch) return "hvf";
  }

  return "tcg";  // Software emulation — always available
}
```

**Key rule:** KVM and HVF both require host/guest architecture match. Cross-arch always falls back to TCG. Don't check just for `/dev/kvm` — verify the architecture matches too.

### HVF + CPU Model Gotcha (macOS)

With `-accel hvf`, QEMU exposes the host CPU directly. Specifying a CPU model like `cortex-a710` (ARMv9, requires SVE2) on Apple Silicon (ARMv8.5) crashes QEMU before the VM starts. Use `-cpu host` with HVF:

```sh
# TCG/KVM — specify exact model
CPU_FLAGS="-cpu cortex-a710"

# HVF — passthrough host CPU
if [ "$ACCEL" = "hvf" ]; then
  CPU_FLAGS="-cpu host"
fi
```

## Health Check and Boot Wait

RouterOS WebFig responds with HTTP 200 on port 80 without authentication — ideal for health checks:

```typescript
async function waitForBoot(url: string, timeoutMs = 60_000): Promise<boolean> {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    try {
      const r = await fetch(url, { signal: AbortSignal.timeout(2000) });
      if (r.ok) return true;
    } catch { /* not ready yet */ }
    await Bun.sleep(2000);
  }
  return false;
}

// Usage
const booted = await waitForBoot("http://127.0.0.1:9180/");
if (booted) {
  // RouterOS is ready — can now call REST API
  const info = await fetch("http://127.0.0.1:9180/rest/system/resource", {
    headers: { Authorization: `Basic ${btoa("admin:")}` },
  }).then(r => r.json());
}
```

## Port Forwarding

QEMU user-mode networking (`-netdev user,hostfwd=...`) for typical RouterOS services:

| Service | Guest Port | Example Host Port | hostfwd |
|---|---|---|---|
| WebFig/REST API | 80 | 9180 | `tcp::9180-:80` |
| SSH (RouterOS CLI) | 22 | 9122 | `tcp::9122-:22` |
| API protocol | 8728 | 9728 | `tcp::9728-:8728` |
| API-SSL | 8729 | 9729 | `tcp::9729-:8729` |
| WinBox | 8291 | 9291 | `tcp::9291-:8291` |

Multiple forwards in one netdev:
```sh
-netdev user,id=net0,hostfwd=tcp::9180-:80,hostfwd=tcp::9122-:22,hostfwd=tcp::9728-:8728
```

Use unique host ports per instance when running multiple CHRs (9180, 9181, 9182...).

## Known Limitations

- **`check-installation` fails on aarch64** in all QEMU environments — this is an unresolvable firmware/DTB issue (see [known issues](./references/known-issues.md))
- **Direct `-kernel` boot does not work** for either architecture — RouterOS needs its full firmware boot path
- **Cross-arch TCG: x86_64 on aarch64 host is not viable** — x86 I/O port emulation is too slow (~300s+ timeouts). The reverse (aarch64 on x86_64) works fine (~20s)
- **No `virtio_mmio` driver** — always use explicit `-device virtio-blk-pci`, never rely on `if=virtio` on aarch64

## Additional Resources

- [VirtIO driver matrix](./references/virtio-drivers.md) — full driver support table
- [Known issues](./references/known-issues.md) — boot failures, cross-arch limitations
- [GitHub Actions CI patterns](./references/github-actions-ci.md) — running CHR on GitHub-hosted runners
- For RouterOS CLI/REST once booted: see the `routeros-fundamentals` skill
- For /app YAML container format (requires CHR with container package): see the `routeros-app-yaml` skill
