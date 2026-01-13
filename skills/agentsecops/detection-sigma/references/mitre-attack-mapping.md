# MITRE ATT&CK Mapping for Sigma Rules

## Table of Contents
- [Execution](#execution)
- [Persistence](#persistence)
- [Privilege Escalation](#privilege-escalation)
- [Defense Evasion](#defense-evasion)
- [Credential Access](#credential-access)
- [Discovery](#discovery)
- [Lateral Movement](#lateral-movement)
- [Collection](#collection)
- [Command and Control](#command-and-control)
- [Exfiltration](#exfiltration)
- [Impact](#impact)

## Execution

### T1059.001 - PowerShell

**Description**: Adversaries abuse PowerShell for execution

**Log Sources**: process_creation (Windows)

**Detection Pattern**:
```yaml
detection:
    selection:
        Image|endswith: '\powershell.exe'
        CommandLine|contains:
            - '-enc'
            - '-EncodedCommand'
            - 'FromBase64String'
            - 'Invoke-Expression'
            - 'IEX'
```

**Tags**:
```yaml
tags:
    - attack.execution
    - attack.t1059.001
```

### T1059.003 - Windows Command Shell

**Description**: Abuse of cmd.exe for execution

**Detection Pattern**:
```yaml
detection:
    selection:
        Image|endswith: '\cmd.exe'
        CommandLine|contains:
            - '/c'
            - '/k'
            - '&'
            - '|'
```

## Persistence

### T1053.005 - Scheduled Task

**Description**: Adversaries create scheduled tasks for persistence

**Log Sources**: process_creation, registry_event

**Detection Pattern**:
```yaml
detection:
    selection:
        Image|endswith: '\schtasks.exe'
        CommandLine|contains:
            - '/create'
            - '/sc minute'
```

### T1547.001 - Registry Run Keys

**Description**: Persistence via registry run keys

**Log Sources**: registry_event

**Detection Pattern**:
```yaml
logsource:
    category: registry_event
detection:
    selection:
        TargetObject|contains:
            - '\Software\Microsoft\Windows\CurrentVersion\Run'
            - '\Software\Microsoft\Windows\CurrentVersion\RunOnce'
```

## Privilege Escalation

### T1055 - Process Injection

**Description**: Adversaries inject code into processes

**Detection Pattern**:
```yaml
detection:
    selection:
        EventID: 8  # CreateRemoteThread
        TargetImage|endswith:
            - '\lsass.exe'
            - '\explorer.exe'
```

### T1548.002 - Bypass User Account Control

**Description**: UAC bypass techniques

**Detection Pattern**:
```yaml
detection:
    selection:
        CommandLine|contains:
            - 'eventvwr.exe'
            - 'fodhelper.exe'
        IntegrityLevel: 'High'
```

## Defense Evasion

### T1027 - Obfuscated Files or Information

**Description**: Files or information made difficult to discover or analyze

**Detection Pattern**:
```yaml
detection:
    selection:
        CommandLine|contains:
            - '-enc'
            - 'base64'
            - 'FromBase64'
            - 'convert]::FromBase64String'
```

### T1070.001 - Clear Windows Event Logs

**Description**: Clearing Windows event logs

**Detection Pattern**:
```yaml
detection:
    selection:
        EventID: 1102  # Security log cleared
```

## Credential Access

### T1003.001 - LSASS Memory

**Description**: Credential dumping from LSASS memory

**Detection Pattern**:
```yaml
detection:
    selection:
        TargetImage|endswith: '\lsass.exe'
        GrantedAccess:
            - '0x1010'
            - '0x1410'
            - '0x147a'
```

### T1558.003 - Kerberoasting

**Description**: Service principal name abuse for credential theft

**Detection Pattern**:
```yaml
detection:
    selection:
        EventID: 4769
        ServiceName|endswith: '$'
        TicketEncryptionType: '0x17'
```

## Discovery

### T1087 - Account Discovery

**Description**: Adversaries enumerate account information

**Detection Pattern**:
```yaml
detection:
    selection:
        Image|endswith:
            - '\net.exe'
            - '\net1.exe'
        CommandLine|contains:
            - 'user'
            - 'group'
            - 'localgroup administrators'
```

### T1082 - System Information Discovery

**Description**: System and hardware information gathering

**Detection Pattern**:
```yaml
detection:
    selection:
        Image|endswith:
            - '\systeminfo.exe'
            - '\wmic.exe'
        CommandLine|contains:
            - 'os get'
            - 'computersystem'
```

## Lateral Movement

### T1021.001 - Remote Desktop Protocol

**Description**: Remote access via RDP

**Log Sources**: network_connection, authentication

**Detection Pattern**:
```yaml
detection:
    selection:
        EventID: 4624
        LogonType: 10  # RemoteInteractive
```

### T1021.002 - SMB/Windows Admin Shares

**Description**: Lateral movement via SMB

**Detection Pattern**:
```yaml
detection:
    selection:
        EventID: 5140
        ShareName|endswith:
            - 'ADMIN$'
            - 'C$'
            - 'IPC$'
```

## Collection

### T1560 - Archive Collected Data

**Description**: Data archiving before exfiltration

**Detection Pattern**:
```yaml
detection:
    selection:
        Image|endswith:
            - '\rar.exe'
            - '\7z.exe'
        CommandLine|contains:
            - ' a '  # Add to archive
            - '-p'   # Password
```

## Command and Control

### T1071.001 - Web Protocols

**Description**: C2 over HTTP/HTTPS

**Log Sources**: network_connection, proxy

**Detection Pattern**:
```yaml
detection:
    selection:
        DestinationPort:
            - 80
            - 443
        Initiated: 'true'
    filter:
        DestinationIp|startswith:
            - '10.'
            - '172.16.'
            - '192.168.'
    condition: selection and not filter
```

## Exfiltration

### T1041 - Exfiltration Over C2 Channel

**Description**: Data exfiltration via existing C2

**Detection Pattern**:
```yaml
detection:
    selection:
        Initiated: 'true'
        DestinationPort:
            - 4444
            - 8080
            - 8443
```

## Impact

### T1486 - Data Encrypted for Impact

**Description**: Ransomware encryption activity

**Detection Pattern**:
```yaml
detection:
    selection:
        Image|endswith: '.exe'
        TargetFilename|endswith:
            - '.encrypted'
            - '.locked'
            - '.crypto'
    condition: selection
```

## Tag Format

When tagging rules with MITRE ATT&CK, use this format:

```yaml
tags:
    - attack.{tactic}           # Lowercase tactic name
    - attack.{technique_id}     # Technique ID (T####) or sub-technique (T####.###)
```

**Example**:
```yaml
tags:
    - attack.execution
    - attack.t1059.001
    - attack.defense_evasion
    - attack.t1027
```

## Multiple Techniques

Rules can map to multiple tactics and techniques:

```yaml
tags:
    - attack.execution          # Primary tactic
    - attack.t1059.001         # PowerShell
    - attack.defense_evasion   # Secondary tactic
    - attack.t1027             # Obfuscation
    - attack.t1140             # Deobfuscate/Decode Files
```

## Resources

- [MITRE ATT&CK Framework](https://attack.mitre.org/)
- [ATT&CK Navigator](https://mitre-attack.github.io/attack-navigator/)
- [Sigma ATT&CK Correlation](https://github.com/SigmaHQ/sigma/wiki/Tags)
