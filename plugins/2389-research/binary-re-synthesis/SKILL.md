---
name: binary-re:synthesis
description: Use when ready to document findings, generate a report, or summarize binary analysis results. Compiles analysis findings into structured reports - correlates facts from triage/static/dynamic phases, validates hypotheses, generates documentation with evidence chains. Keywords - "summarize findings", "generate report", "document analysis", "what did we find", "write up results", "export findings"
---

# Analysis Synthesis (Phase 5)

## Purpose

Compile all gathered knowledge into actionable intelligence. Validate hypotheses against evidence. Produce structured reports with traceable findings.

## When to Use

- Sufficient facts gathered from triage + static + dynamic analysis
- Ready to document understanding for handoff or archival
- Need to present findings to stakeholders
- Before closing analysis session

## Synthesis Process

### Step 1: Evidence Review

Gather all recorded knowledge:

```
FACTS collected:
- From triage: arch, ABI, dependencies, capabilities
- From static: functions, xrefs, decompilation
- From dynamic: syscalls, network, file access

HYPOTHESES formed:
- With supporting evidence
- With contradicting evidence
- Unresolved hypotheses

QUESTIONS remaining:
- Blocking questions (prevent conclusion)
- Open questions (future investigation)
```

### Step 2: Hypothesis Validation

For each hypothesis, determine status:

| Evidence State | Status | Action |
|----------------|--------|--------|
| Strong support, no contradictions | **Confirmed** | Include in conclusions |
| Some support, some contradictions | **Uncertain** | Document both sides |
| Strong contradictions | **Refuted** | Explain why wrong |
| No evidence either way | **Unvalidated** | List as unknown |

### Step 3: Correlation Analysis

Connect findings across phases:

```
Static finding: Function at 0x8400 calls socket(), connect(), SSL_read()
Dynamic finding: connect() to 192.168.1.100:8443 observed
Strings found: "api.vendor.com/telemetry"

CORRELATED CONCLUSION:
Function 0x8400 is network initialization for telemetry submission
to api.vendor.com:8443 over TLS.
```

### Step 4: Capability Mapping

Summarize what the binary CAN do:

```markdown
## Capabilities

### Network
- [x] HTTP/HTTPS client (libcurl, libssl imports)
- [x] Custom TCP connections (socket/connect observed)
- [ ] Server functionality (no bind/listen/accept)

### File System
- [x] Read configuration (/etc/config.json accessed)
- [x] Write logs (/var/log/app.log)
- [ ] Execute other programs (no exec* calls)

### Cryptography
- [x] TLS encryption (SSL_* imports)
- [ ] Symmetric encryption (no AES/DES imports)
- [ ] Hashing (no SHA*/MD5 imports)
```

### Step 5: Behavioral Summary

Document observed/inferred behavior:

```markdown
## Behavioral Analysis

### Startup Sequence
1. Load configuration from /etc/config.json
2. Initialize network subsystem (function 0x8400)
3. Establish TLS connection to api.vendor.com:8443
4. Enter main loop (function 0x10800)

### Main Loop Behavior
- Polls sensor data every 30 seconds (timing from sleep() calls)
- Formats data as JSON (jsmn library identified)
- Submits via HTTPS POST
- Logs results to /var/log/app.log

### Error Handling
- Network failures: retry with exponential backoff
- Config errors: exit with code 1
- Unknown errors: continue with default values
```

## Report Template

```markdown
# Binary Analysis Report

## Executive Summary

[2-3 sentence overview of what was found]

## Artifact Information

| Property | Value |
|----------|-------|
| Filename | [name] |
| SHA256 | [hash] |
| Architecture | [arch] |
| Libc | [glibc/musl/uclibc] |
| Stripped | [yes/no] |
| Analysis Date | [date] |
| Analyst | [human + Claude] |

## Identification

**File Type:** ELF [32/64]-bit [LSB/MSB] [executable/shared object]

**Purpose (Hypothesis):** [What we believe this binary does]

**Confidence:** [High/Medium/Low] - [Brief justification]

## Capabilities Summary

### Confirmed Capabilities
- [Capability 1] - Evidence: [source]
- [Capability 2] - Evidence: [source]

### Potential Capabilities (Unverified)
- [Capability] - Reason: [why suspected]

## Technical Findings

### Key Functions

| Address | Inferred Name | Purpose | Confidence |
|---------|---------------|---------|------------|
| 0x8400 | network_init | Initialize network connection | High |
| 0x9200 | parse_config | Parse JSON configuration | Medium |
| 0x10800 | main_loop | Main execution loop | High |

### External Communications

| Destination | Port | Protocol | Purpose |
|-------------|------|----------|---------|
| api.vendor.com | 8443 | HTTPS | Telemetry submission |

### File System Access

| Path | Access | Purpose |
|------|--------|---------|
| /etc/config.json | Read | Configuration |
| /var/log/app.log | Write | Logging |

## Evidence Log

### Confirmed Hypotheses

**H1: Binary is a telemetry client**
- Status: CONFIRMED
- Supporting evidence:
  - Import of libcurl (HTTP client)
  - String "telemetry" found at 0x12340
  - connect() to api.vendor.com:8443 observed
- Contradicting evidence: None

### Refuted Hypotheses

**H2: Binary acts as server**
- Status: REFUTED
- Reason: No bind/listen/accept imports or calls observed

### Unresolved Questions

- Q1: What triggers telemetry submission? (Timing or event-based?)
- Q2: What data is collected? (Need deeper dynamic analysis)

## Recommendations

### For Security Review
- [ ] Verify TLS certificate validation
- [ ] Check for hardcoded credentials
- [ ] Audit data collection scope

### For Further Analysis
- [ ] Capture network traffic during execution
- [ ] Analyze configuration format in detail
- [ ] Test behavior with malformed config

## Appendices

### A. Tool Outputs
[Truncated raw outputs from key analysis steps]

### B. Timeline
[Chronological log of analysis steps taken]

### C. File Hashes
[SHA256 of all analyzed files]
```

## Confidence Calibration

Use consistent confidence levels:

| Level | Meaning | Evidence Required |
|-------|---------|-------------------|
| **High** | Near certain | Multiple independent sources confirm |
| **Medium** | Likely correct | Some evidence, no contradictions |
| **Low** | Possible | Limited evidence, some uncertainty |
| **Speculative** | Guess | Based on patterns, not direct evidence |

## Quality Checklist

Before finalizing report:

- [ ] All hypotheses have explicit status (confirmed/refuted/uncertain)
- [ ] Every conclusion has traceable evidence
- [ ] Remaining unknowns are documented
- [ ] Technical details are accurate (addresses, names)
- [ ] No speculation presented as fact
- [ ] Recommendations are actionable

## Knowledge Journaling

After synthesis, record final summary for episodic memory:

```
[BINARY-RE:synthesis] {filename} (sha256: {hash})
Analysis completed: {date}
Phases completed: {triage|static|dynamic|synthesis}

=== FINAL CONCLUSIONS ===

Primary purpose: {what binary does}
Confidence: {HIGH|MEDIUM|LOW}

Confirmed hypotheses:
  CONFIRMED: {hypothesis} (evidence: {facts})

Refuted hypotheses:
  REFUTED: {hypothesis} (reason: {contradicting evidence})

Key capabilities:
  - {capability}: {evidence summary}

Security findings:
  {CRITICAL|HIGH|MEDIUM|LOW}: {finding} (location: {addr/function})

Remaining unknowns:
  UNRESOLVED: {question}

Recommendations:
  - {actionable recommendation}

=== EVIDENCE INDEX ===
Facts: {count} recorded across phases
Hypotheses: {confirmed}/{total}
Questions: {answered}/{total}
```

### Example Final Entry

```
[BINARY-RE:synthesis] thermostat_daemon (sha256: a1b2c3d4...)
Analysis completed: 2024-01-15
Phases completed: triage, static, dynamic, synthesis

=== FINAL CONCLUSIONS ===

Primary purpose: IoT telemetry client that reports temperature/humidity to vendor cloud
Confidence: HIGH

Confirmed hypotheses:
  CONFIRMED: "Telemetry client reporting to api.thermco.com" (evidence: URL string, curl imports, connect() observed)
  CONFIRMED: "30-second reporting interval" (evidence: sleep(30) in main loop, strace timing)

Refuted hypotheses:
  REFUTED: "May have local web server" (reason: no bind/listen/accept imports or calls)

Key capabilities:
  - HTTPS client: libcurl + libssl, connects to api.thermco.com:443
  - Config parsing: reads /etc/thermostat.conf at startup
  - Logging: writes to /var/log/thermostat.log

Security findings:
  LOW: No certificate pinning detected (standard libssl usage)
  INFO: Config file may contain API credentials (needs review)

Remaining unknowns:
  UNRESOLVED: Exact data fields in telemetry payload
  UNRESOLVED: Authentication mechanism (API key location)

Recommendations:
  - Review /etc/thermostat.conf for sensitive data
  - Monitor network traffic to confirm payload contents
  - Consider blocking if telemetry is unwanted

=== EVIDENCE INDEX ===
Facts: 23 recorded across phases
Hypotheses: 2/3 confirmed
Questions: 4/6 answered
```

## Output Formats

### Structured JSON (for tools/databases)

```json
{
  "artifact": { "sha256": "...", "arch": "arm" },
  "conclusions": [
    {
      "statement": "Binary is telemetry client",
      "confidence": 0.9,
      "evidence": ["fact_001", "fact_012", "obs_003"]
    }
  ],
  "capabilities": {
    "network_client": true,
    "network_server": false
  },
  "open_questions": ["Q1: Trigger mechanism"]
}
```

### Markdown (for human readers)

See template above.

### STIX/TAXII (for threat intelligence)

If binary is potentially malicious, format findings for sharing:

```json
{
  "type": "malware",
  "spec_version": "2.1",
  "id": "malware--...",
  "name": "telemetry-client",
  "malware_types": ["spyware"],
  "capabilities": ["exfiltrates-data"],
  "implementation_languages": ["c"]
}
```

## Next Steps

After synthesis:
- Archive analysis artifacts
- Share report with stakeholders
- Document lessons learned
- Update tool configurations if needed
