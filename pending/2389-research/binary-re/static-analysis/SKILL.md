---
name: binary-re:static-analysis
description: Use when analyzing binary structure, disassembling code, or decompiling functions. Deep static analysis via radare2 (r2) and Ghidra headless - function enumeration, cross-references (xrefs), decompilation, control flow graphs. Keywords - "disassemble", "decompile", "what does this function do", "find functions", "analyze code", "r2", "ghidra", "pdg", "afl"
---

# Static Analysis (Phases 2-3)

## Purpose

Understand binary structure and logic without execution. Map functions, trace data flow, decompile critical code.

## When to Use

- After triage has established architecture and ABI
- To understand specific functions identified as interesting
- When dynamic analysis is impractical or risky
- To build hypotheses before dynamic verification

## Pre-Analysis: Compare Known I/O First

**CRITICAL:** Before diving into disassembly, check if known inputs/outputs exist.

⚠️ **REQUIRES HUMAN APPROVAL** - Get explicit approval before any execution, even for I/O comparison.

```bash
# SAFE: Use emulation for cross-arch binaries (after human approval)
# ARM32:
qemu-arm -L /usr/arm-linux-gnueabihf -- ./binary < input.txt > actual.txt

# ARM64:
qemu-aarch64 -L /usr/aarch64-linux-gnu -- ./binary < input.txt > actual.txt

# Docker-based (macOS/cross-arch - see dynamic-analysis Option D):
docker run --rm --platform linux/arm/v7 -v ~/samples:/work:ro \
  arm32v7/debian:bullseye-slim sh -c '/work/binary < /work/input.txt' > actual.txt

# x86-64 native (still requires approval):
./binary < input.txt > actual.txt

# Compare outputs:
diff expected.txt actual.txt
cmp -l expected.txt actual.txt | head -20  # Byte-level differences

# Record findings:
# - Where does output first diverge?
# - Does file size match? (logic bug vs truncation)
# - What pattern appears in corruption?
```

This step often reveals the bug category before any code analysis.

---

## Two-Stage Approach

**Stage 1 (Light):** Function enumeration, strings, imports - fast, broad coverage
**Stage 2 (Deep):** Targeted decompilation, CFG analysis - slow, focused

## Stage 1: Light Analysis (radare2)

### Analysis Depth Selection

| Binary Size | Command | Tradeoff |
|-------------|---------|----------|
| < 500KB | `aaa` | Full analysis, may be slow |
| 500KB - 5MB | `aa; aac` | Functions + all call targets |
| > 5MB | `aa` + targeted `af @addr` | Fast, manual depth control |

### Session Setup

```bash
# Launch r2 with controlled analysis
r2 -q0 -e scr.color=false -e anal.timeout=120 -e anal.maxsize=67108864 binary

# Inside r2 (choose based on binary size):
aa       # Basic analysis
aac      # Also analyze all call targets (recommended for most binaries)
```

**Critical settings:**
- `anal.timeout=120` - Prevent runaway analysis
- `anal.maxsize=67108864` - 64MB max function size
- Use `aa; aac` for medium binaries, `aaa` only for small ones

### Handling Unanalyzed Call Targets

If `axtj` returns empty for known imports:

```bash
# The import may be called indirectly or analysis was too shallow
# Option 1: Deeper analysis
aac   # Analyze all calls

# Option 2: Manually create function at call target
af @0x8048abc

# Option 3: Search for references to import address
axtj @sym.imp.connect
```

### Function Enumeration

```bash
# All functions as JSON
aflj

# Filter by name pattern
aflj~main
aflj~init
aflj~network
aflj~send
aflj~recv

# Function count
afl~?
```

### Cross-Reference Analysis

```bash
# Who calls this function?
axtj @sym.imp.connect

# What does this function call?
axfj @sym.main

# Data references to address
axtj @0x12345
```

### String-Function Correlation

```bash
# Find which function contains a string
izj~api.vendor.com
# Note the vaddr, then find containing function
afi @0xVADDR

# Or search and map
"/j api"    # Search for string
axtj @@hit* # Xrefs to all hits
```

### Import/Export Mapping

```bash
# Imports with addresses
iij

# Exports with addresses
iEj

# Symbols (if not stripped)
isj
```

### Quick Disassembly

```bash
# Disassemble function as JSON
pdfj @sym.main

# Disassemble N instructions from address
pdj 20 @0x8400

# Print function summary
afi @sym.main
```

## Stage 2: Deep Analysis

### r2ghidra Availability Check

**Before attempting decompilation, verify r2ghidra is installed:**

```bash
# Check if r2ghidra is available
r2 -qc 'pdg?' - 2>/dev/null | grep -q Usage && echo "r2ghidra OK" || echo "SKIP: r2ghidra not installed"

# If missing, install with:
r2pm -ci r2ghidra
```

**If r2ghidra unavailable:** Rely on disassembly (`pdf`) and cross-reference analysis (`axt/axf`).

### Targeted Decompilation (r2ghidra)

```bash
# Decompile specific function
pdgj @sym.target_function

# Or named function
pdgj @sym.main
```

### Ghidra Headless (Large Binaries)

For complex functions or when r2ghidra struggles:

```bash
# Create analysis project and run script
analyzeHeadless /tmp/ghidra_proj proj \
  -import binary \
  -overwrite \
  -processor ARM:LE:32:v7 \
  -postScript ExportDecompilation.java sym.target_function \
  -deleteProject
```

**Processor strings:**
- ARM 32-bit: `ARM:LE:32:v7` or `ARM:LE:32:Cortex`
- ARM 64-bit: `AARCH64:LE:64:v8A`
- x86_64: `x86:LE:64:default`
- MIPS LE: `MIPS:LE:32:default`
- MIPS BE: `MIPS:BE:32:default`

### Control Flow Analysis

```bash
# Basic blocks in function
afbj @sym.main

# Function call graph (dot format)
agCd @sym.main > callgraph.dot

# Control flow graph
agfd @sym.main > cfg.dot
```

### Data Structure Recovery

```bash
# Analyze local variables
afvj @sym.main

# Stack frame layout
afvd @sym.main

# Global data references
adrj
```

## Analysis Patterns

### Pattern: Network Function Tracing

```bash
# Find all network-related calls
axtj @sym.imp.socket
axtj @sym.imp.connect
axtj @sym.imp.send
axtj @sym.imp.recv
axtj @sym.imp.SSL_read
axtj @sym.imp.SSL_write

# Trace caller chain
for func in $(aflj | jq -r '.[].name'); do
  axfj @$func | grep -q "socket\|connect" && echo $func
done
```

### Pattern: Configuration File Analysis

```bash
# Find file operations
axtj @sym.imp.open
axtj @sym.imp.fopen

# Trace string arguments
"/j /etc"
"/j .conf"
"/j .json"

# Check what functions reference these paths
```

### Pattern: Crypto Identification

```bash
# Common crypto imports
axtj @sym.imp.EVP_EncryptInit
axtj @sym.imp.AES_encrypt
axtj @sym.imp.SHA256

# Hardcoded keys (check strings near crypto calls)
izj | jq '.strings[] | select(.length == 16 or .length == 32)'
```

## r2 JSON Commands Reference

| Command | Output | Use Case |
|---------|--------|----------|
| `aflj` | Functions list | Map code structure |
| `axtj @addr` | Xrefs TO address | Who uses this? |
| `axfj @addr` | Xrefs FROM address | What does it call? |
| `pdfj @addr` | Disassembly | Understand instructions |
| `pdgj @addr` | Decompilation | Pseudo-C output |
| `afbj @addr` | Basic blocks | Control flow |
| `izj` | Data strings | Configuration, URLs |
| `iij` | Imports | External dependencies |
| `iEj` | Exports | Public interface |
| `afvj @addr` | Local variables | Stack analysis |

## Output Format

Record analysis findings as structured facts:

```json
{
  "functions_analyzed": [
    {
      "name": "sub_8400",
      "address": "0x8400",
      "size": 256,
      "calls": ["socket", "connect", "send"],
      "called_by": ["main", "init_network"],
      "strings_referenced": ["api.vendor.com"],
      "hypothesis": "network_initialization"
    }
  ],
  "call_graph": {
    "main": ["init_config", "init_network", "main_loop"],
    "init_network": ["sub_8400", "SSL_CTX_new"]
  },
  "data_flow": [
    {
      "source": "config_file_read",
      "through": ["parse_config", "extract_url"],
      "sink": "connect_to_server"
    }
  ]
}
```

## Knowledge Journaling

After static analysis, record findings for episodic memory:

```
[BINARY-RE:static] {filename} (sha256: {hash})

Functions analyzed: {count}
Decompilation performed: {yes|no}

Key functions:
  FACT: Function at {addr} calls {imports} (source: r2 axfj)
  FACT: Function at {addr} references string "{string}" (source: r2 axtj)
  FACT: Function {name} appears to {purpose} (source: decompilation)

Cross-references:
  FACT: {caller} calls {callee} (source: r2 axtj)

HYPOTHESIS UPDATE: {refined theory} (confidence: {new_value})
  Supporting: {fact_ids}
  Contradicting: {fact_ids}

New questions:
  QUESTION: {discovered unknown}

Answered questions:
  RESOLVED: {question} → {answer}
```

### Example Journal Entry

```
[BINARY-RE:static] thermostat_daemon (sha256: a1b2c3d4...)

Functions analyzed: 47
Decompilation performed: yes (function 0x8400)

Key functions:
  FACT: Function 0x8400 calls curl_easy_perform, curl_easy_setopt (source: r2 axfj)
  FACT: Function 0x8400 references string "api.thermco.com/telemetry" (source: r2 axtj)
  FACT: Function 0x9200 parses JSON using jsmn library (source: decompilation)
  FACT: Function 0x10800 is main loop, calls 0x8400 after sleep(30) (source: r2 pdf)

Cross-references:
  FACT: main calls init_config (0x9000) then main_loop (0x10800) (source: r2 axtj)
  FACT: main_loop calls send_telemetry (0x8400) in loop (source: r2 pdf)

HYPOTHESIS UPDATE: Telemetry client sending to api.thermco.com every 30 seconds (confidence: 0.85)
  Supporting: URL string, curl imports, sleep(30) in loop
  Contradicting: none

New questions:
  QUESTION: What data fields are included in telemetry payload?
  QUESTION: Is there any authentication/API key?

Answered questions:
  RESOLVED: "What endpoint?" → api.thermco.com/telemetry via HTTPS
```

## Decision Points

After static analysis:

1. **Identified critical functions?** → Ready for dynamic verification
2. **Unclear behavior?** → Try dynamic analysis for runtime observation
3. **Crypto detected?** → Document key handling, note for security review
4. **Anti-analysis patterns?** → Consider Unicorn snippet emulation

## Next Steps

→ `binary-re-dynamic-analysis` to verify hypotheses with runtime observation
→ `binary-re-synthesis` if sufficient understanding reached
