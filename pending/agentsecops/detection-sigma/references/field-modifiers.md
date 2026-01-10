# Sigma Field Modifiers Reference

## Overview

Field modifiers transform field values during rule matching. Use pipe `|` syntax to apply modifiers to field names.

**Syntax**: `FieldName|modifier: value`

## String Modifiers

### contains

**Description**: Case-insensitive substring match

**Usage**:
```yaml
detection:
    selection:
        CommandLine|contains: 'powershell'
```

**Matches**:
- `C:\Windows\System32\WindowsPowerShell\powershell.exe -enc`
- `powershell -command "iex"`
- `POWERSHELL.EXE`

**Backend Support**: All backends

### startswith

**Description**: Case-insensitive prefix match

**Usage**:
```yaml
detection:
    selection:
        CommandLine|startswith: 'powershell'
```

**Matches**:
- `powershell -enc AAAA`
- `PowerShell.exe -command`

**Does Not Match**:
- `C:\Windows\System32\powershell.exe`

**Backend Support**: All backends

### endswith

**Description**: Case-insensitive suffix match

**Usage**:
```yaml
detection:
    selection:
        Image|endswith: '\powershell.exe'
```

**Matches**:
- `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe`
- `powershell.exe`

**Backend Support**: All backends

### all

**Description**: All values in list must match

**Usage**:
```yaml
detection:
    selection:
        CommandLine|contains|all:
            - 'powershell'
            - '-enc'
            - 'FromBase64'
```

**Requires**: All three substrings present in CommandLine

**Backend Support**: Most backends (check specific backend documentation)

## Regular Expression Modifiers

### re

**Description**: Regular expression match

**Usage**:
```yaml
detection:
    selection:
        CommandLine|re: 'powershell(.exe)?\s+-enc.*'
```

**Matches**:
- `powershell -enc AAAABBBB`
- `powershell.exe -encodedcommand AAAA`

**Backend Support**: Varies by backend (Splunk ✓, Elasticsearch ✓, Sentinel ✓)

**Performance Note**: Regex can be slow on large datasets

### re (with case-insensitive flag)

**Usage**:
```yaml
detection:
    selection:
        CommandLine|re: '(?i)powershell.*-enc'
```

## Encoding Modifiers

### base64

**Description**: Match base64-encoded value

**Usage**:
```yaml
detection:
    selection:
        CommandLine|base64|contains: 'Invoke-Mimikatz'
```

**How it works**: Encodes search string to base64 before matching

**Encoded Value**: `SW52b2tlLU1pbWlrYXR6`

**Backend Support**: Limited (check backend documentation)

### base64offset

**Description**: Match base64 with offset variations

**Usage**:
```yaml
detection:
    selection:
        CommandLine|base64offset|contains: 'Invoke-Mimikatz'
```

**Why**: Base64 encoding can vary based on string position. This checks all offset variations.

**Generates**:
- `SW52b2tlLU1pbWlrYXR6`
- `ludm9rZS1NaW1pa2F0e`
- `JbnZva2UtTWltaWthdH`

**Backend Support**: Limited

### wide

**Description**: Match UTF-16 wide character encoding

**Usage**:
```yaml
detection:
    selection:
        FileContent|wide|contains: 'malicious'
```

**Encoded**: `m\x00a\x00l\x00i\x00c\x00i\x00o\x00u\x00s\x00`

## Case Modifiers

### (default - case insensitive)

**Description**: By default, Sigma matches are case-insensitive

**Usage**:
```yaml
detection:
    selection:
        CommandLine|contains: 'powershell'  # Matches PowerShell, POWERSHELL, etc.
```

## Type Conversion Modifiers

### lt / lte / gt / gte

**Description**: Numeric comparison (less than, less/equal, greater than, greater/equal)

**Usage**:
```yaml
detection:
    selection:
        EventID|gte: 4624
        EventID|lte: 4634
```

**Backend Support**: Most backends

## Aggregation Modifiers (in condition)

### count

**Description**: Count occurrences

**Usage**:
```yaml
detection:
    selection:
        EventID: 4625  # Failed logon
    condition: selection | count(TargetUserName) by SourceIp > 5
```

**Meaning**: More than 5 failed logons from same IP within timeframe

**Backend Support**: Varies (typically requires SIEM correlation capabilities)

### near

**Description**: Events occur within proximity

**Usage**:
```yaml
condition: selection1 and selection2 | near(timespan=30s)
```

**Meaning**: Both events occur within 30 seconds

**Backend Support**: Limited (backend-dependent)

## Chaining Modifiers

Modifiers can be chained:

```yaml
detection:
    selection:
        CommandLine|base64offset|contains: 'Invoke-Mimikatz'
        Image|endswith: '\powershell.exe'
```

**Order matters**: Apply modifiers left to right

**Example**: `|base64|contains` first encodes to base64, then checks contains

## Common Patterns

### Pattern 1: Flexible PowerShell Detection

```yaml
detection:
    selection:
        Image|endswith:
            - '\powershell.exe'
            - '\pwsh.exe'
        CommandLine|contains:
            - '-enc'
            - '-EncodedCommand'
            - '-e '
```

### Pattern 2: Process Chain Detection

```yaml
detection:
    selection:
        ParentImage|endswith: '\winword.exe'
        Image|endswith:
            - '\powershell.exe'
            - '\cmd.exe'
            - '\wscript.exe'
```

### Pattern 3: File Path Detection

```yaml
detection:
    selection:
        TargetFilename|contains: '\AppData\Roaming\'
        TargetFilename|endswith:
            - '.exe'
            - '.dll'
            - '.ps1'
```

### Pattern 4: Encoded Command Detection

```yaml
detection:
    selection:
        CommandLine|base64offset|contains:
            - 'Invoke-Expression'
            - 'IEX'
            - 'Net.WebClient'
```

## Backend Compatibility Matrix

| Modifier | Splunk | Elasticsearch | Sentinel | QRadar |
|----------|--------|---------------|----------|--------|
| contains | ✓ | ✓ | ✓ | ✓ |
| startswith | ✓ | ✓ | ✓ | ✓ |
| endswith | ✓ | ✓ | ✓ | ✓ |
| all | ✓ | ✓ | ✓ | Partial |
| re | ✓ | ✓ | ✓ | ✓ |
| base64 | Limited | Limited | ✓ | Limited |
| base64offset | Limited | Limited | Limited | No |
| wide | Limited | Limited | Limited | No |
| lt/gt/lte/gte | ✓ | ✓ | ✓ | ✓ |

**Legend**:
- ✓: Full support
- Limited: Partial support, may require workarounds
- No: Not supported

## Best Practices

### 1. Prefer Specific Modifiers

❌ **Don't**:
```yaml
CommandLine|contains: 'powershell'
```

✓ **Do**:
```yaml
Image|endswith: '\powershell.exe'
```

**Why**: More precise, better performance

### 2. Use `all` for Multiple Requirements

❌ **Don't**:
```yaml
CommandLine|contains: 'powershell'
CommandLine|contains: '-enc'
```

✓ **Do**:
```yaml
CommandLine|contains|all:
    - 'powershell'
    - '-enc'
```

**Why**: Clearer intent, single field evaluation

### 3. Avoid Excessive Regex

❌ **Don't**:
```yaml
CommandLine|re: '.*powershell.*-enc.*'
```

✓ **Do**:
```yaml
CommandLine|contains|all:
    - 'powershell'
    - '-enc'
```

**Why**: Regex is slower, harder to tune

### 4. Test Modifiers with Backend

Always test converted queries in target SIEM:

```bash
# Convert rule
python scripts/sigma_convert.py rule.yml --backend splunk

# Test in Splunk search interface
# Verify expected matches/non-matches
```

### 5. Document Complex Modifiers

When using `base64offset` or `wide`, document why:

```yaml
title: Encoded PowerShell Command Detection
description: |
  Detects base64-encoded PowerShell commands with offset variations
  to catch encoding attempts regardless of string position.
detection:
    selection:
        CommandLine|base64offset|contains: 'Invoke-Mimikatz'
```

## Troubleshooting

### Modifier Not Supported in Backend

**Error**: `Field modifier 'base64offset' not supported by backend 'qradar'`

**Solutions**:
1. Use alternative modifier (`contains` instead of `base64offset`)
2. Implement custom pipeline transformation
3. Post-process in SIEM after ingestion

### No Matches Despite Known Positive Data

**Causes**:
- Case sensitivity (shouldn't be issue with Sigma, but check backend)
- Field name mismatch (check field mappings)
- Modifier not applied correctly

**Debug**:
```bash
# Check converted query
python scripts/sigma_convert.py rule.yml --backend splunk --debug

# Test simplified query without modifiers
# Add modifiers incrementally
```

### Performance Issues

**Problem**: Query with `|re` too slow

**Solution**:
- Replace regex with `contains`, `startswith`, `endswith`
- Add more specific filters (EventID, Image path)
- Limit time range

## Resources

- [Sigma Specification - Modifiers](https://github.com/SigmaHQ/sigma-specification/blob/main/Sigma_specification.md#field-modifiers)
- [pySigma Transformations](https://github.com/SigmaHQ/pySigma)
- [Regex Testing Tool](https://regex101.com/)
