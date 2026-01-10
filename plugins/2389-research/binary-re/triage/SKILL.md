---
name: binary-re:triage
description: Use when first encountering an unknown binary, ELF file, executable, or firmware blob. Fast fingerprinting via rabin2 - architecture detection (ARM, x86, MIPS), ABI identification, dependency mapping, string extraction. Keywords - "what is this binary", "identify architecture", "check file type", "rabin2", "file analysis", "quick scan"
---

# Binary Triage (Phase 1)

## Purpose

Quick fingerprinting to establish baseline facts before deeper analysis. Runs in seconds, not minutes.

## When to Use

- First contact with an unknown binary
- Need architecture/ABI info for tool selection
- Quick capability assessment
- Before committing to expensive analysis

## Key Principle

**Gather facts fast, defer analysis.**

This phase identifies WHAT the binary is, not HOW it works.

## Triage Sequence

### Step 1: File Identification

```bash
# Basic identification
file binary

# Expected output patterns:
# ELF 32-bit LSB executable, ARM, EABI5 version 1 (SYSV), dynamically linked, interpreter /lib/ld-linux-armhf.so.3
# ELF 64-bit LSB pie executable, ARM aarch64, version 1 (SYSV), dynamically linked, interpreter /lib/ld-linux-aarch64.so.1
```

**Extract:**
- Architecture (ARM, ARM64, x86_64, MIPS)
- Bit width (32/64)
- Endianness (LSB/MSB)
- Link type (static/dynamic)
- Interpreter path (libc indicator)

### Step 2: Structured Metadata (rabin2)

```bash
# All metadata as JSON
rabin2 -q -j -I binary | jq .

# Key fields:
# .arch     - "arm", "x86", "mips"
# .bits     - 32 or 64
# .endian   - "little" or "big"
# .os       - "linux", "none"
# .machine  - "ARM", "AARCH64"
# .stripped - true/false
# .static   - true/false
```

### Step 3: ABI Detection

```bash
# Interpreter detection
readelf -p .interp binary 2>/dev/null

# Or via rabin2
rabin2 -I binary | grep interp

# ARM-specific: float ABI
readelf -A binary | grep "Tag_ABI_VFP_args"
# hard-float: "VFP registers"
# soft-float: missing or "compatible"
```

**Interpreter → Libc mapping:**

| Interpreter | Libc | Notes |
|-------------|------|-------|
| `/lib/ld-linux-armhf.so.3` | glibc | ARM hard-float |
| `/lib/ld-linux.so.3` | glibc | ARM soft-float |
| `/lib/ld-musl-arm.so.1` | musl | ARM 32-bit |
| `/lib/ld-musl-aarch64.so.1` | musl | ARM 64-bit |
| `/lib/ld-uClibc.so.0` | uClibc | Embedded |
| `/lib64/ld-linux-x86-64.so.2` | glibc | x86_64 |

### Step 4: Dependencies

```bash
# Library dependencies
rabin2 -q -j -l binary | jq '.libs[]'

# Common patterns:
# libcurl.so.* → HTTP client
# libssl.so.* → TLS/crypto
# libpthread.so.* → Threading
# libz.so.* → Compression
# libsqlite3.so.* → Local database
```

### Step 5: Entry Points & Exports

```bash
# Entry points
rabin2 -q -j -e binary | jq .

# Exports (for shared libraries)
rabin2 -q -j -E binary | jq '.exports[] | {name, vaddr}'
```

### Step 6: Quick String Scan

```bash
# All strings with metadata
rabin2 -q -j -zz binary | jq '.strings | length'  # Count first

# Filter interesting strings (URLs, paths, errors)
rabin2 -q -j -zz binary | jq '
  .strings[] |
  select(.length > 8) |
  select(.string | test("http|ftp|/etc|/var|error|fail|pass|key|token"; "i"))
'
```

### Step 7: Import Analysis

```bash
# All imports
rabin2 -q -j -i binary | jq '.imports[] | {name, lib}'

# Group by capability
rabin2 -q -j -i binary | jq '
  .imports | group_by(.lib) |
  map({lib: .[0].lib, functions: [.[].name]})
'
```

## Capability Mapping

| Import Pattern | Capability |
|----------------|------------|
| `socket`, `connect`, `send` | Network client |
| `bind`, `listen`, `accept` | Network server |
| `open`, `read`, `write` | File I/O |
| `fork`, `exec*`, `system` | Process spawning |
| `pthread_*` | Multi-threading |
| `SSL_*`, `EVP_*` | Cryptography |
| `dlopen`, `dlsym` | Dynamic loading |
| `mmap`, `mprotect` | Memory manipulation |

## Output Format

After triage, record structured facts:

```json
{
  "artifact": {
    "path": "/path/to/binary",
    "sha256": "abc123...",
    "size_bytes": 245760
  },
  "identification": {
    "arch": "arm",
    "bits": 32,
    "endian": "little",
    "os": "linux",
    "stripped": true,
    "static": false
  },
  "abi": {
    "interpreter": "/lib/ld-musl-arm.so.1",
    "libc": "musl",
    "float_abi": "hard"
  },
  "dependencies": [
    "libcurl.so.4",
    "libssl.so.1.1",
    "libz.so.1"
  ],
  "capabilities_inferred": [
    "network_client",
    "tls_encryption",
    "compression"
  ],
  "strings_of_interest": [
    {"value": "https://api.vendor.com/telemetry", "type": "url"},
    {"value": "/etc/config.json", "type": "path"}
  ],
  "complexity_estimate": {
    "functions": "unknown (stripped)",
    "strings": 847,
    "imports": 156
  }
}
```

## Knowledge Journaling

After triage completes, record findings for episodic memory:

```
[BINARY-RE:triage] {filename} (sha256: {hash})

Identification:
  Architecture: {arch} {bits}-bit {endian}
  Libc: {glibc|musl|uclibc} ({interpreter_path})
  Stripped: {yes|no}
  Size: {bytes}

FACT: Links against {library} (source: rabin2 -l)
FACT: Contains {N} strings of interest (source: rabin2 -zz)
FACT: Imports {function} from {library} (source: rabin2 -i)

Capabilities inferred:
  - {capability_1} (evidence: {import/string})
  - {capability_2} (evidence: {import/string})

HYPOTHESIS: {what binary likely does} (confidence: {0.0-1.0})

QUESTION: {open unknown that needs investigation}

Next phase: {static-analysis|dynamic-analysis}
Sysroot needed: {path or "extract from device"}
```

### Example Journal Entry

```
[BINARY-RE:triage] thermostat_daemon (sha256: a1b2c3d4...)

Identification:
  Architecture: ARM 32-bit LE
  Libc: musl (/lib/ld-musl-arm.so.1)
  Stripped: yes
  Size: 153,600 bytes

FACT: Links against libcurl.so.4 (source: rabin2 -l)
FACT: Links against libssl.so.1.1 (source: rabin2 -l)
FACT: Contains string "api.thermco.com" (source: rabin2 -zz)
FACT: Imports curl_easy_perform (source: rabin2 -i)

Capabilities inferred:
  - HTTP client (evidence: libcurl import)
  - TLS encryption (evidence: libssl import)
  - Network communication (evidence: URL string)

HYPOTHESIS: Telemetry client that reports to api.thermco.com (confidence: 0.6)

QUESTION: What data does it collect and transmit?

Next phase: static-analysis
Sysroot needed: musl ARM (extract from device or Alpine)
```

## Decision Points

After triage, determine:

1. **Sysroot selection** - Based on arch + libc
2. **Analysis tool chain** - r2 vs Ghidra vs both
3. **Dynamic analysis feasibility** - QEMU viability based on arch
4. **Initial hypotheses** - What does this binary likely do?

## Next Steps

→ Proceed to `binary-re-static-analysis` for function enumeration
→ Or `binary-re-dynamic-analysis` if behavior observation is priority
