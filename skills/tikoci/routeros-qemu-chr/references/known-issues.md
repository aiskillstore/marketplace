# Known Issues — RouterOS CHR with QEMU

## check-installation Fails on aarch64 (All Environments)

**Symptom:** `POST /rest/system/check-installation` returns an error on aarch64 CHR in QEMU.

**Root cause:** RouterOS runs a 32-bit ARM ELF checker binary that looks for capability files (magic `0xbad0f11e`) in `/ram/`. These files are created from hardware DTB info. On QEMU's `virt` machine with ACPI enabled (required for disk access), EDK2 generates an empty DTB — so no capability files exist and the checker returns non-zero.

**Why it can't be fixed:**
- `acpi=on` — disk works (ACPI PCIe), but DTB empty → no capability files → check fails
- `acpi=off` + PCI — DTB present, but no `pci-host-ecam-generic` driver → disk not found
- `acpi=off` + MMIO — DTB present, but no `virtio-mmio` driver → kernel stalls

CPU model is irrelevant — tested cortex-a53, a72, neoverse-n1, all fail identically. RouterOS continues booting normally (HTTP 200 works). **Skip this check on aarch64.**

## Direct `-kernel` Boot Not Viable

QEMU's `-kernel` flag does not work for RouterOS CHR on either architecture:

- **x86_64:** 16-bit real-mode setup code needs BIOS INT services not present in QEMU's Linux boot protocol. Prints "early console in setup code" then hangs.
- **aarch64:** EFI stub requires EFI boot services (memory map, runtime services) that QEMU's direct boot doesn't provide.
- **EFI handover:** Entry point offset 0x190 lands in compressed data → `#UD` crash.

Always boot through firmware (SeaBIOS or UEFI), never with `-kernel`.

## Cross-Architecture TCG: x86_64 on aarch64 Host

**Not viable.** x86 I/O port instructions (`in`/`out`) have no ARM hardware equivalent. Tested over 16 iterations with progressive optimizations:

1. SeaBIOS + q35: 199% CPU, zero serial output, 300s timeout
2. OVMF + q35 + legacy virtio: timeout (I/O port BARs)
3. OVMF + pc + modern virtio: stuck in PIT timer calibration
4. OVMF + pc + modern virtio + HPET: timed out at 300s

The root cause is pervasive: x86 firmware and kernel probe legacy I/O ports during init. No combination of machine type, firmware, or virtio mode can avoid it.

**The reverse works fine:** aarch64 on x86_64 via TCG boots in ~20s (EDK2 UEFI uses 64-bit MMIO throughout).

**Practical CI strategy:**
- x86_64 host: boots ALL machines (x86 native KVM, aarch64 cross-arch TCG)
- aarch64 host: boots only aarch64 machines (x86 skipped)

## UEFI pflash Size Mismatch

Both pflash units (code + vars) must be identical size (typically 64 MiB). On Ubuntu, `AAVMF_CODE.fd` may be a **symlink** — use `stat -Lc%s` (with `-L`) to get the real file size. Without `-L`, `stat` returns the symlink path length.

To pad a vars file to match the code ROM:
```sh
CODE_SIZE=$(stat -Lc%s /usr/share/AAVMF/AAVMF_CODE.fd)
dd if=/dev/zero of=my-vars.fd bs=1 count=0 seek=$CODE_SIZE
```

## Background Mode PID Tracking

When backgrounding QEMU (e.g., `nohup qemu-system-x86_64 ... &`), use `exec` in the shell wrapper to ensure `$!` captures the QEMU PID, not the wrapper shell PID:

```sh
# WRONG — $! is the sh PID, not QEMU
nohup sh -c "qemu-system-x86_64 ..." &

# CORRECT — exec replaces sh with QEMU
nohup sh -c "exec qemu-system-x86_64 ..." &
```

Without `exec`, `kill "$PID"` only kills the wrapper — QEMU becomes orphaned.

## Serial Socket Race with socat

QEMU creates the serial socket file (`bind()`) before it's ready to accept connections (`listen()`). If socat connects too early, it gets "Connection refused." Use retry:

```sh
socat -,rawer UNIX-CONNECT:/tmp/serial.sock,retry=10,interval=1
```

## Temp File Race in Background Mode

`mktemp` + `trap ... EXIT` is standard but breaks when the parent shell exits before the background child (QEMU) reads the temp file. Use deterministic paths without cleanup traps for background mode:

```sh
# Deterministic path — overwritten on re-run, no cleanup needed
VARS_COPY="/tmp/qemu-${VM_NAME}-vars.fd"
cp "$VARS_ORIGINAL" "$VARS_COPY"
```
