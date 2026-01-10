---
name: binary-re:tool-setup
description: Use when reverse engineering tools are missing, not working, or need configuration. Installation guides for radare2 (r2), Ghidra, GDB, QEMU, Frida, binutils, and cross-compilation toolchains. Keywords - "install radare2", "setup ghidra", "r2 not found", "qemu missing", "tool not installed", "configure gdb", "cross-compiler"
---

# Tool Setup

## Purpose

Ensure required reverse engineering tools are available and properly configured for cross-architecture analysis.

## When to Use

- Before first analysis session
- When tool commands fail
- Setting up new analysis environment
- Updating to newer tool versions

## Required Tools

| Tool | Purpose | Priority |
|------|---------|----------|
| radare2 | Static analysis, disassembly | **Required** |
| rabin2 | Fast binary triage | **Required** (part of r2) |
| qemu-user | Cross-arch emulation | **Required** |
| gdb-multiarch | Cross-arch debugging | **Required** |
| Ghidra | Decompilation | Recommended |
| GEF | GDB enhancements | Recommended |
| Frida | Dynamic instrumentation | Optional |
| Unicorn | Snippet emulation | Optional |
| Angr | Symbolic execution | Optional |

## Installation by Platform

### Ubuntu/Debian

```bash
# Core tools
sudo apt update
sudo apt install -y \
  radare2 \
  qemu-user \
  qemu-user-static \
  gdb-multiarch \
  binutils-multiarch \
  jq                    # Required for JSON parsing in skill commands

# ARM sysroots (for QEMU)
sudo apt install -y \
  libc6-armhf-cross \
  libc6-arm64-cross \
  libc6-dev-armhf-cross \
  libc6-dev-arm64-cross

# Additional utilities
sudo apt install -y \
  file \
  binutils \
  elfutils \
  patchelf
```

### Windows (WSL2)

Windows users should use WSL2 with Ubuntu for full compatibility:

```powershell
# PowerShell (Administrator) - Install WSL2 with Ubuntu
wsl --install -d Ubuntu

# Restart computer when prompted, then open Ubuntu terminal
```

Inside WSL2 Ubuntu:

```bash
# Install all required tools
sudo apt update && sudo apt install -y \
  radare2 \
  qemu-user \
  qemu-user-static \
  gdb-multiarch \
  binutils-multiarch \
  jq \
  file \
  patchelf

# Fix file permissions for Windows-mounted drives
sudo tee -a /etc/wsl.conf > /dev/null << 'EOF'
[automount]
options = "metadata,umask=22,fmask=11"
EOF

# Restart WSL to apply changes
# (In PowerShell: wsl --shutdown)
```

**WSL2 Tips:**
- Copy binaries into `~` rather than using `/mnt/c/...` paths (fewer permission issues)
- Use `wsl --shutdown` in PowerShell to restart WSL after config changes
- Docker Desktop integrates with WSL2 for container-based analysis

### macOS (Homebrew)

```bash
# Core tools
brew install radare2 jq

# NOTE: Homebrew QEMU may lack qemu-user targets
# Verify: qemu-arm --version || echo "qemu-user missing"
# If missing, use Docker for cross-arch execution (see below)

# GDB requires special handling on macOS
brew install gdb
# Note: Code signing required for debugging

# ARM cross tools (optional, for static analysis only)
brew install arm-linux-gnueabihf-binutils
```

### macOS Docker Setup for Dynamic Analysis

Since Homebrew doesn't provide `qemu-user`, use Docker for cross-architecture execution:

```bash
# Install Docker runtime (Colima is lightweight alternative to Docker Desktop)
brew install colima docker

# Start Colima
colima start

# Register multi-architecture emulation handlers
docker run --rm --privileged --platform linux/arm64 \
  tonistiigi/binfmt --install arm

# Verify ARM32 emulation works
docker run --rm --platform linux/arm/v7 arm32v7/debian:bullseye-slim uname -m
# Should output: armv7l

# Verify ARM64 emulation works
docker run --rm --platform linux/arm64 arm64v8/debian:bullseye-slim uname -m
# Should output: aarch64

# Verify x86-32 emulation works
docker run --rm --platform linux/i386 i386/debian:bullseye-slim uname -m
# Should output: i686
```

**IMPORTANT:** On Colima, always mount from `~/` not `/tmp/`:
```bash
# ✅ Works
docker run -v ~/samples:/work ...

# ❌ May fail silently
docker run -v /tmp/samples:/work ...
```

### Arch Linux

```bash
sudo pacman -S radare2 qemu-user gdb
yay -S arm-linux-gnueabihf-glibc  # From AUR
```

## Tool-Specific Setup

### radare2

```bash
# Verify installation
r2 -v
rabin2 -v

# Install r2ghidra plugin (decompilation)
r2pm init
r2pm update
r2pm -ci r2ghidra  # -ci = clean install

# Verify r2ghidra is working (CRITICAL CHECK)
r2 -qc 'pdg?' - 2>/dev/null | grep -q Usage && echo "r2ghidra OK" || echo "r2ghidra MISSING"

# Alternative verification
r2 -c 'Ld' /bin/ls | grep -i ghidra
```

**Common r2ghidra issues:**

| Symptom | Cause | Fix |
|---------|-------|-----|
| `pdg` unknown command | Plugin not loaded | `r2pm -ci r2ghidra` |
| Plugin loads but crashes | Version mismatch | Update both r2 and plugin |
| Decompilation hangs | Large function | Use `pdf` instead, or Ghidra headless |

**Configuration (~/.radare2rc):**
```
# Disable colors for scripting
e scr.color=false

# Increase analysis limits
e anal.timeout=120
e anal.maxsize=67108864

# JSON output by default for scripts
e cfg.json.num=true
```

### Ghidra (Headless)

```bash
# Download from https://ghidra-sre.org/
# Extract to /opt/ghidra

# Verify headless script
/opt/ghidra/support/analyzeHeadless --help

# Add to PATH
echo 'export PATH=$PATH:/opt/ghidra/support' >> ~/.bashrc
```

**Memory configuration (for large binaries):**
Edit `/opt/ghidra/support/analyzeHeadless`:
```bash
MAXMEM=4G  # Increase from default
```

### GEF (GDB Enhanced Features)

```bash
# Install GEF
bash -c "$(curl -fsSL https://gef.blah.cat/sh)"

# Verify
gdb -q -ex "gef help" -ex "quit"

# For ARM Cortex-M support, also install gef-extras
git clone https://github.com/hugsy/gef-extras.git ~/.gef-extras
echo 'source ~/.gef-extras/scripts/checksec.py' >> ~/.gdbinit
```

### Frida

```bash
# Install Frida tools
pip install frida-tools

# Verify
frida --version

# Install frida-server for device debugging (optional)
# Download from https://github.com/frida/frida/releases
```

### Unicorn (Python bindings)

```bash
pip install unicorn

# Verify
python -c "from unicorn import *; print('OK')"
```

### Angr

```bash
# Create virtual environment (recommended)
python -m venv ~/angr-venv
source ~/angr-venv/bin/activate

# Install angr
pip install angr

# Verify
python -c "import angr; print('OK')"
```

### YARA

```bash
# Ubuntu/Debian
sudo apt install yara

# Or from source for latest
git clone https://github.com/VirusTotal/yara.git
cd yara
./bootstrap.sh
./configure
make && sudo make install

# Python bindings
pip install yara-python
```

## Sysroot Setup

### Standard Debian/Ubuntu Sysroots

Already installed via `libc6-*-cross` packages:

```bash
# Verify paths
ls /usr/arm-linux-gnueabihf/lib/
ls /usr/aarch64-linux-gnu/lib/
```

### Custom Sysroot from Device

```bash
# Pull from device via SSH
mkdir -p ~/sysroots/device
ssh user@device "tar czf - /lib /usr/lib" | tar xzf - -C ~/sysroots/device

# Or minimal extraction
ssh user@device "tar czf - /lib/ld-* /lib/libc.* /lib/libpthread.* /lib/libdl.*" \
  | tar xzf - -C ~/sysroots/device
```

### Musl Sysroot

```bash
# From Alpine Linux
docker run -it --rm -v ~/sysroots:/out alpine:latest sh -c \
  "apk add musl musl-dev && cp -a /lib /usr /out/alpine-musl"
```

## Verification Script

Run this to verify all tools are working:

```bash
#!/bin/bash
set -e

echo "=== Binary RE Tool Verification ==="

# radare2
echo -n "radare2: "
r2 -v | head -1

# rabin2
echo -n "rabin2: "
rabin2 -v | head -1

# QEMU
echo -n "qemu-arm: "
qemu-arm --version | head -1

echo -n "qemu-aarch64: "
qemu-aarch64 --version | head -1

# GDB
echo -n "gdb-multiarch: "
gdb-multiarch --version | head -1

# Ghidra (optional)
if command -v analyzeHeadless &> /dev/null; then
  echo -n "Ghidra: "
  analyzeHeadless 2>&1 | head -1 || echo "available"
else
  echo "Ghidra: not installed (optional)"
fi

# Frida (optional)
if command -v frida &> /dev/null; then
  echo -n "Frida: "
  frida --version
else
  echo "Frida: not installed (optional)"
fi

# Sysroots
echo ""
echo "=== Sysroots ==="
[ -d /usr/arm-linux-gnueabihf ] && echo "ARM hard-float: OK" || echo "ARM hard-float: MISSING"
[ -d /usr/aarch64-linux-gnu ] && echo "ARM64: OK" || echo "ARM64: MISSING"

echo ""
echo "=== Verification Complete ==="
```

## Troubleshooting

### Common Issues Quick Reference

| Symptom | Cause | Fix |
|---------|-------|-----|
| `exec format error` in Docker | binfmt not registered | `docker run --privileged tonistiigi/binfmt --install arm` |
| `ld-linux.so.3 not found` | Linker path mismatch | `ln -sf /lib/ld-linux-armhf.so.3 /lib/ld-linux.so.3` |
| `libXXX.so not found` | Missing dependency | `apt install` in container (check `rabin2 -l`) |
| r2 `pdg` unknown command | r2ghidra not installed | `r2pm -ci r2ghidra` |
| Empty xrefs from `axtj` | Shallow analysis | Use `aa; aac` or manual `af @addr` |
| Empty Docker mount | Colima /tmp issue | Use `~/path` instead of `/tmp/path` |
| strace fails in container | ptrace not implemented | Use `LD_DEBUG=files,libs` |

### r2 "Cannot open file"

```bash
# Check permissions
ls -la binary

# Try with explicit format
r2 -b 32 binary
```

### QEMU "Invalid ELF image"

```bash
# Verify architecture matches
file binary

# Check QEMU variant
qemu-arm --help | grep -i "target"
```

### Docker "exec format error"

```bash
# Register binfmt handlers (one-time setup)
docker run --rm --privileged --platform linux/arm64 \
  tonistiigi/binfmt --install arm

# Verify registration
cat /proc/sys/fs/binfmt_misc/qemu-arm
```

### GDB "Cannot execute binary"

```bash
# Use QEMU as gdbserver
qemu-arm -g 1234 ./binary &
gdb-multiarch -ex "target remote :1234" ./binary
```

### Ghidra "Out of memory"

```bash
# Increase heap in analyzeHeadless script
# Or pass explicitly:
analyzeHeadless ... -max-cpu 4 -analysisTimeoutPerFile 600
```

### Missing ARM libraries in QEMU

```bash
# Set LD_LIBRARY_PATH in QEMU environment
qemu-arm -E LD_LIBRARY_PATH=/lib:/usr/lib -L /sysroot ./binary

# Or use patchelf to modify binary's rpath
patchelf --set-rpath /lib:/usr/lib ./binary
```

### Docker container can't find libraries

```bash
# Inside container, install common dependencies
apt-get update && apt-get install -y libcap2 libacl1

# Check what the binary needs
# (Run rabin2 -l on host before entering container)
```

## Version Recommendations

| Tool | Minimum | Recommended |
|------|---------|-------------|
| radare2 | 5.8.0 | Latest |
| QEMU | 7.0 | 8.0+ |
| GDB | 12.0 | 14.0+ |
| Ghidra | 10.3 | 11.0+ |
| Frida | 16.0 | Latest |

## Environment Variables

Add to `~/.bashrc` or `~/.zshrc`:

```bash
# Ghidra
export GHIDRA_HOME=/opt/ghidra
export PATH=$PATH:$GHIDRA_HOME/support

# Default sysroot for QEMU
export QEMU_LD_PREFIX=/usr/arm-linux-gnueabihf

# Angr virtual environment
alias angr-activate='source ~/angr-venv/bin/activate'
```
