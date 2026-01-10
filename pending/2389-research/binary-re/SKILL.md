---
name: binary-re
description: This skill should be used when analyzing binaries, executables, or bytecode to understand what they do or how they work. Triggers on "binary", "executable", "ELF", "what does this do", "reverse engineer", "disassemble", "decompile", "pyc file", "python bytecode", "analyze binary", "figure out", "marshal". Routes to sub-skills for triage, static analysis, dynamic analysis, synthesis, or tool setup.
---

# Binary Reverse Engineering

## Purpose

Comprehensive guide for binary reverse engineering. This skill provides the overall methodology, philosophy, and reference material. Related skills handle specific phases:

## Related Skills

| Skill | Purpose | Trigger Keywords |
|-------|---------|------------------|
| `binary-re:triage` | Fast fingerprinting | "what is this binary", "identify", "file type" |
| `binary-re:static-analysis` | r2 + Ghidra analysis | "disassemble", "decompile", "functions" |
| `binary-re:dynamic-analysis` | QEMU + GDB + Frida | "run", "execute", "debug", "trace" |
| `binary-re:synthesis` | Report generation | "summarize", "report", "document findings" |
| `binary-re:tool-setup` | Install tools | "install", "setup", "tool not found" |

**Note:** Each skill auto-detects based on keywords. You don't need to explicitly route - just ask what you need.

## Pre-Flight Verification

**Before beginning any analysis, verify tooling availability:**

### Core Tools (Required)
```bash
rabin2 -v  # Should show version
r2 -v      # Should show version
```

### Decompilation (Optional)
```bash
# Check r2ghidra availability
r2 -qc 'pdg?' - 2>/dev/null | grep -q Usage && echo "r2ghidra OK" || echo "r2ghidra missing - install with: r2pm -ci r2ghidra"
```

### Dynamic Analysis Platform Check
| Host Platform | Method | Setup Required |
|---------------|--------|----------------|
| Linux x86_64 | Native QEMU | `apt install qemu-user` |
| macOS (any) | Docker + binfmt | See `binary-re-tool-setup` skill |
| Windows | WSL2 | Use Linux method inside WSL |

**If dynamic tools unavailable:** Proceed with static-only analysis, note reduced confidence in synthesis phase.

### Fallback Tooling (No r2/Ghidra)

When radare2 or Ghidra aren't available, use standard binutils/LLVM tools:

```bash
# Metadata (replaces rabin2 -I)
readelf -h binary              # ELF header
readelf -d binary              # Dynamic section (dependencies)
file binary                    # Quick identification

# Imports/Exports (replaces rabin2 -i/-E)
readelf -Ws binary | grep -E "FUNC|OBJECT" | awk '{print $8}'
nm -D binary 2>/dev/null       # Dynamic symbols

# Strings (replaces rabin2 -zz)
strings -a -n 8 binary | grep -Ei 'http|ftp|/etc|/var|error|pass|key|token|api'

# Disassembly (replaces r2 pdf)
objdump -d -M intel binary | head -500
# Or LLVM (better cross-arch support):
llvm-objdump -d --no-show-raw-insn binary | head -500

# Dependencies (replaces rabin2 -l)
ldd binary 2>/dev/null || readelf -d binary | grep NEEDED
```

**Limitations of fallback approach:**
- No cross-references (axt/axf) - must trace manually
- No decompilation - assembly only
- No function boundary detection - raw disassembly
- Reduced accuracy for stripped binaries

---

## Philosophy

**The LLM drives analysis; the human provides context.**

Human provides:
- Platform info (device type, OS, hardware)
- Suspected purpose (what the binary might do)
- Constraints (no network, isolated env, etc.)

LLM executes:
- Tool selection and invocation
- Hypothesis formation from evidence
- Experiment design
- Knowledge synthesis

## The Agentic Loop

```
┌─────────────────────────────────────────────────┐
│           HYPOTHESIS-DRIVEN ANALYSIS            │
├─────────────────────────────────────────────────┤
│                                                 │
│  0. I/O SANITY → Compare known inputs/outputs   │
│  1. OBSERVE → Gather facts via tools            │
│  2. HYPOTHESIZE → Form theories from facts      │
│  3. PLAN → Design experiments to test theories  │
│  4. EXECUTE → Run tools (gate risky ops)        │
│  5. RECORD → Capture observations               │
│  6. UPDATE → Confirm/refute hypotheses          │
│  7. LOOP → Until understanding sufficient       │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Step 0: Compare Known I/O First (CRITICAL)

**Before diving into code analysis, always check if known inputs/outputs exist.**

This step prevents hours of wasted analysis by establishing ground truth first.

⚠️ **REQUIRES HUMAN APPROVAL** - Even for I/O comparison, get explicit approval before execution.

```bash
# SAFE: Use emulation for cross-arch binaries (after human approval)
# ARM32 example:
qemu-arm -L /usr/arm-linux-gnueabihf -- ./binary input.txt > actual_output.txt

# x86-64 native (still requires approval):
./binary input.txt > actual_output.txt

# Docker-based (macOS - safest option):
docker run --rm --platform linux/arm/v7 -v ~/samples:/work:ro \
  arm32v7/debian:bullseye-slim /work/binary /work/input.txt > actual_output.txt

# Compare outputs:
diff expected_output.txt actual_output.txt
cmp -l expected_output.txt actual_output.txt | head -20  # Byte-level

# Document the delta:
# - Where does output first diverge?
# - What pattern appears in the corruption?
# - Does file size match (logic bug) or differ (truncation)?
```

**Record as FACT:**
```
FACT: Output differs at byte {N}, expected "{X}" got "{Y}" (source: diff/cmp)
FACT: File sizes match/differ by {N} bytes (source: ls -l)
```

This single step often reveals the bug category before any disassembly.

## Knowledge Model

Throughout analysis, maintain structured knowledge via **episodic memory**:

```
FACTS: Verified observations with tool attribution
HYPOTHESES: Theories with confidence and evidence
QUESTIONS: Open unknowns blocking progress
EXPERIMENTS: Planned tool invocations
OBSERVATIONS: Results from experiments
DECISIONS: Human-approved choices with rationale
```

### Episodic Memory Integration

Knowledge persists across sessions via episodic memory. Use consistent tagging:

```
[BINARY-RE:{phase}] {artifact_name} (sha256: {hash})
FACT: {observation} (source: {tool})
HYPOTHESIS: {theory} (confidence: {0.0-1.0})
QUESTION: {unknown}
DECISION: {choice} (rationale: {why})
```

**Starting analysis:** Search episodic memory for artifact hash first
**After each phase:** Findings are automatically captured in conversation
**Resuming:** Search `[BINARY-RE] {artifact_name}` to restore context

## Human-in-the-Loop Triggers

**ALWAYS ask human before:**

1. **Executing the binary** - Even under QEMU, confirm sandbox
2. **Network operations** - Prevent unintended phone-home
3. **Conflicting evidence** - Resolve contradictory findings
4. **Privileged operations** - Device access, root actions
5. **Major direction changes** - Significant analysis pivots

## Session Management

### Starting New Analysis

```
1. Compute artifact hash: sha256sum binary
2. Search episodic memory: "[BINARY-RE] sha256:{hash}"
3. If previous analysis found:
   → "Found previous analysis from {date}. Resume or start fresh?"
4. If resuming: Load facts/hypotheses, continue from last phase
5. If fresh: Begin with triage phase
```

### Resuming Interrupted Analysis

```
User: "Continue analyzing that thermostat binary"

Claude:
1. Invoke episodic-memory:search-conversations
   Query: "[BINARY-RE] thermostat"
2. Retrieve previous session findings
3. Summarize: "Last session identified ARM32/musl, found network
   functions. We were about to run dynamic analysis."
4. Continue from that phase
```

### Searching Past Analyses

```
User: "Have we analyzed any ARM binaries with hardcoded passwords?"

Claude:
1. Search: "[BINARY-RE] FACT: hardcoded" or "[BINARY-RE] ARM"
2. Return matching artifacts and findings
```

## Standard Analysis Flow

For typical unknown binary analysis:

```
1. Triage (binary-re-triage)
   └─ Architecture, ABI, dependencies, capabilities

2. Static Analysis (binary-re-static-analysis)
   └─ Functions, strings, xrefs, decompilation

3. Dynamic Analysis (binary-re-dynamic-analysis) - if safe
   └─ Syscalls, network, file access

4. Synthesis (binary-re-synthesis)
   └─ Structured report with evidence
```

## Quick Reference

### Essential Commands

```bash
# Fast triage
rabin2 -I binary              # Metadata
rabin2 -l binary              # Dependencies
rabin2 -zz binary             # Strings

# Static analysis
r2 -q -c 'aa; aflj' binary    # Functions
r2 -q -c 'izj' binary         # Strings

# Dynamic (ARM example)
qemu-arm -L /usr/arm-linux-gnueabihf -strace ./binary
```

### Architecture Detection

| Indicator | Architecture | QEMU Binary | Ghidra Processor |
|-----------|--------------|-------------|------------------|
| `e_machine=EM_386 (3)` | x86 32-bit | `qemu-i386` or Docker `--platform linux/i386` | `x86:LE:32:default` |
| `e_machine=EM_ARM (40)` | ARM 32-bit | `qemu-arm` or Docker `--platform linux/arm/v7` | `ARM:LE:32:v7` |
| `e_machine=EM_AARCH64 (183)` | ARM 64-bit | `qemu-aarch64` or Docker `--platform linux/arm64` | `AARCH64:LE:64:v8A` |
| `e_machine=EM_X86_64 (62)` | x86-64 | Native or Docker `--platform linux/amd64` | `x86:LE:64:default` |
| `e_machine=EM_MIPS (8)` | MIPS 32 LE | `qemu-mipsel` | `MIPS:LE:32:default` |
| `e_machine=EM_MIPS (8)` BE | MIPS 32 BE | `qemu-mips` | `MIPS:BE:32:default` |
| `e_machine=EM_RISCV (243)` | RISC-V 64 | `qemu-riscv64` | `RISCV:LE:64:RV64I` |
| `e_machine=EM_RISCV (243)` 32 | RISC-V 32 | `qemu-riscv32` | `RISCV:LE:32:RV32I` |

### Libc Detection

| Interpreter | Libc |
|-------------|------|
| `ld-linux-armhf.so.3` | glibc (ARM hard-float) |
| `ld-musl-arm.so.1` | musl |
| `ld-uClibc.so.0` | uClibc |

## Error Recovery

| Situation | Action |
|-----------|--------|
| Tool not found | Use `binary-re-tool-setup` skill |
| Wrong architecture | Re-run triage, verify file output |
| QEMU fails | Try Qiling, Unicorn, or on-device |
| Analysis timeout | Reduce scope, use `aa` not `aaa` |
| Conflicting evidence | Ask human, document both interpretations |

## Documentation

See companion docs:
- `docs/r2-commands.md` - Complete r2 reference for LLMs
- `docs/ghidra-headless.md` - Ghidra scripting guide
- `docs/arch-adapters.md` - Per-architecture quirks
- `docs/python-bytecode-re.md` - Python .pyc/marshal obfuscation patterns

## Integration

Works with other plugins:
- **remote-system-maintenance**: Extract binaries from devices via SSH
- **fresh-eyes-review**: Validate conclusions before documenting
- **scenario-testing**: Create reproducible analysis environments
