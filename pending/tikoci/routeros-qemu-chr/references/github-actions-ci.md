# RouterOS CHR in GitHub Actions CI

## Overview

Running RouterOS CHR on GitHub Actions runners is the primary CI pattern for projects that need
to query the RouterOS REST API (schema generation, /app validation, integration testing). CHR
runs directly in QEMU on the `ubuntu-latest` runner — no Docker-in-Docker needed.

## Runner Prerequisites

**x86 `ubuntu-latest` runners** have KVM available via `/dev/kvm`. GitHub migrated all Linux
runners to a KVM-capable VM SKU when it doubled public-repo runners to 4-core in January 2024,
and confirmed nested virtualization support across all Linux runners (public and private) by
April 2024.

> **Caution:** GitHub officially describes nested virtualization as "technically possible…
> not officially supported… experimental." It works reliably in practice but is not covered
> by GitHub's SLA. Always use the conditional fallback pattern in the QEMU Launch section
> so builds degrade gracefully to TCG rather than hard-fail if KVM is unavailable.

**ARM64 runners** (`ubuntu-24.04-arm`): use partner images (likely AWS Graviton). KVM
availability is **not confirmed** for these runners. Assume TCG only; always use the
conditional fallback.

**Performance without KVM:** x86 CHR boots in TCG software emulation at roughly 5–6× slower
than KVM (measured: ~5 s with KVM vs ~30 s with TCG to first login prompt). Full boot to a
responsive REST API takes 1–3 minutes with KVM on x86; plan for longer without it.

### Installing QEMU

```yaml
- name: Install QEMU
  run: |
    sudo apt-get update
    sudo apt-get install -y qemu-system-x86 qemu-utils
```

**Important:** The apt package is `qemu-system-x86` (not `qemu-system-x86_64` — that's the
binary name, not the package name). Also install `qemu-utils` for `qemu-img`.

### Enabling KVM

```yaml
- name: Enable KVM
  run: |
    echo 'KERNEL=="kvm", GROUP="kvm", MODE="0666", OPTIONS+="static_node=kvm"' | sudo tee /etc/udev/rules.d/99-kvm4all.rules
    sudo udevadm control --reload-rules
    sudo udevadm trigger --name-match=kvm
```

**What this step does:** `/dev/kvm` already exists on x86 `ubuntu-latest` runners, but its
default permissions restrict it to the `kvm` group. The udev rule changes the mode to `0666`
(world-writable) so the runner user can open it without a `sudo`/re-login dance. Without this
step, `/dev/kvm` exists but QEMU will fail immediately with "permission denied" when
`-enable-kvm` is specified — it does **not** silently fall back to TCG.

**This step is a no-op on ARM64 runners** where `/dev/kvm` likely doesn't exist — the udev
trigger completes without creating the device, so it's safe to include unconditionally. The
real guard is in the QEMU launch (see below).

## CHR Image Download Pattern

Always try `download.mikrotik.com` first, fall back to `cdn.mikrotik.com`:

```yaml
- name: Download CHR image
  run: |
    ROSVER="${{ inputs.rosver }}"
    # download.mikrotik.com serves all versions (stable + beta/rc).
    # cdn.mikrotik.com is a fallback mirror — try if primary is unavailable.
    wget -q "https://download.mikrotik.com/routeros/${ROSVER}/chr-${ROSVER}.vdi.zip" \
      || wget -q "https://cdn.mikrotik.com/routeros/${ROSVER}/chr-${ROSVER}.vdi.zip"
    unzip -o "chr-${ROSVER}.vdi.zip"
```

**Do not change this order.** `download.mikrotik.com` is authoritative for all versions. `cdn.mikrotik.com` is a fallback mirror and may lag on new releases.

## Disk Conversion

Convert VDI to QCOW2 (native QEMU format, supports snapshots):

```yaml
- name: Convert disk image
  run: qemu-img convert -f vdi -O qcow2 chr-${ROSVER}.vdi chr.qcow2
```

## QEMU Launch

```yaml
- name: Start CHR
  run: |
    # Detect KVM — check *writability*, not just existence.
    # /dev/kvm exists on x86 runners but is restricted until the "Enable KVM" udev step runs.
    # On ARM64 runners /dev/kvm likely doesn't exist at all.
    # QEMU does NOT fall back to TCG on -enable-kvm failure; it hard-errors immediately.
    KVM_OPTS=""
    if [ -w /dev/kvm ]; then
      KVM_OPTS="-enable-kvm -cpu host"
      echo "KVM available — using hardware acceleration."
    else
      echo "::warning::KVM not writable — QEMU will run in TCG software emulation (slower)."
    fi
    nohup qemu-system-x86_64 \
      -M q35 -m 256 -smp 1 \
      ${KVM_OPTS} \
      -drive file=chr.qcow2,format=qcow2,if=virtio \
      -netdev user,id=net0,hostfwd=tcp::9180-:80,hostfwd=tcp::9122-:22 \
      -device virtio-net-pci,netdev=net0 \
      -display none -serial none \
      > /tmp/qemu.log 2>&1 &
    echo $! > /tmp/qemu.pid
```

**Notes:**
- Use `exec` in the `sh -c` wrapper so `$!` captures the QEMU PID, not the shell's
- Port 9180→80 for REST API, 9122→22 for SSH/SCP (extra packages upload)
- 256 MB RAM is sufficient for schema generation
- Use VirtIO for disk and network (MikroTik recommended for CHR)
- `-serial none` in CI (no need for console); use `-serial stdio` for interactive debugging

## Boot Wait Loop

Wait up to 5 minutes for CHR to respond:

```yaml
- name: Wait for CHR boot
  run: |
    echo "Waiting for RouterOS to boot..."
    for i in $(seq 1 30); do
      if curl -sf --connect-timeout 5 http://127.0.0.1:9180/ > /dev/null 2>&1; then
        echo "RouterOS is ready (attempt $i)"
        exit 0
      fi
      echo "Attempt $i/30 — not ready, waiting 10s..."
      sleep 10
    done
    echo "::error::RouterOS failed to boot within 5 minutes"
    cat /tmp/qemu.log || true
    exit 1
```

**Why this works:** RouterOS WebFig (port 80) returns HTTP 200 **without authentication**.
The REST API (`/rest/`) requires auth, but the root path doesn't. This makes `curl -sf` a
reliable health check.

## Extra Packages Installation

For builds that need container, iot, zerotier, etc.:

```yaml
- name: Install extra packages
  env:
    ROSVER: ${{ inputs.rosver }}
  run: |
    # Download all_packages bundle
    wget -q "https://download.mikrotik.com/routeros/${ROSVER}/all_packages-x86-${ROSVER}.zip" \
      || wget -q "https://cdn.mikrotik.com/routeros/${ROSVER}/all_packages-x86-${ROSVER}.zip"
    unzip -o "all_packages-x86-${ROSVER}.zip"

    # Upload each .npk via SCP (RouterOS SSH on port 9122)
    for pkg in *.npk; do
      sshpass -p '' scp -P 9122 -o StrictHostKeyChecking=no "$pkg" admin@127.0.0.1:/
    done

    # Reboot to activate packages
    curl -sf -u admin: -X POST http://127.0.0.1:9180/rest/system/reboot || true
    sleep 5

    # Wait for reboot completion
    for i in $(seq 1 30); do
      if curl -sf --connect-timeout 5 http://127.0.0.1:9180/ > /dev/null 2>&1; then
        echo "RouterOS rebooted with extra packages"
        exit 0
      fi
      sleep 10
    done
    exit 1
```

## Concurrent Build Push — Retry Pattern

Multiple builds can run in parallel (base + extra, multiple versions). All push to `main`.
Use the retry-with-rebase pattern:

```yaml
- name: Publish schemas
  run: |
    git config user.name "github-actions[bot]"
    git config user.email "github-actions[bot]@users.noreply.github.com"

    git add docs/${ROSVER}/
    git commit -m "Publish ${ROSVER} schemas"

    # Retry up to 5 times with rebase on push rejection
    for attempt in {1..5}; do
      if git push origin main; then
        break
      elif [ $attempt -eq 5 ]; then
        echo "::error::Failed to push after 5 attempts"
        exit 1
      fi
      echo "::warning::Push $attempt/5 failed, rebasing..."
      # Clean bun install/npm install artifacts before rebase
      git checkout -- .
      git clean -fd
      git pull --rebase
      sleep $((RANDOM % 10 + 5))
    done
```

**Why this is safe:** Each build writes to its own `docs/{version}/` directory — no real file
conflicts. The `git checkout -- .` / `git clean -fd` are required because `bun install` /
`npm install` may modify tracked files (`package.json`, `bun.lock`), which would block rebase.

**Do not simplify to `git pull && git push`.** That pattern fails under concurrent builds.

## Cleanup

```yaml
- name: Stop CHR
  if: always()
  run: |
    if [ -f /tmp/qemu.pid ]; then
      kill $(cat /tmp/qemu.pid) 2>/dev/null || true
    fi
```

## Environment Variables

| Variable | Example | Purpose |
|---|---|---|
| `URLBASE` | `http://127.0.0.1:9180/rest` | RouterOS REST API base URL |
| `BASICAUTH` | `admin:` | Credentials (empty password for fresh CHR) |
| `INSPECTFILE` | `./inspect.json` | Skip live router, use cached inspect data |

## Debugging CI Failures

1. **Boot timeout**: Check `/tmp/qemu.log` artifact for QEMU errors
2. **`Permission denied` opening `/dev/kvm`**: The "Enable KVM" udev step ran after QEMU
   launched, or was skipped. Ensure it runs before the QEMU step.
3. **No KVM acceleration warning in logs**: KVM is available but `[ -w /dev/kvm ]` fails —
   the Enable KVM step may have been skipped or the udev rule didn't take effect.
4. **Empty `rosver`**: Check `bun rest2raml.js --version` output parsing (the `xargs` step)
5. **Push rejection after 5 retries**: Too many concurrent builds — increase retry count or add jitter
6. **Download fails**: Check both `download.mikrotik.com` and `cdn.mikrotik.com` for the version
7. **SCP fails**: Ensure sshpass is installed and SSH port forwarding (9122→22) is correct

## Daily Auto-Detection Workflow

The `auto.yaml` pattern:
1. Daily cron checks all 4 channels (`stable`, `testing`, `development`, `long-term`)
2. For each unique version across channels, checks 3 artifacts independently:
   - `docs/{version}/schema.raml` — base schema
   - `docs/{version}/extra/schema.raml` — extra-packages schema
   - `docs/{version}/routeros-app-yaml-schema.json` — /app YAML schemas (7.22+)
3. Dispatches only the builds that are missing
4. Outputs a step summary table showing what was built vs. skipped
