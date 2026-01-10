---
name: ir-velociraptor
description: >
  Endpoint visibility, digital forensics, and incident response using Velociraptor
  Query Language (VQL) for evidence collection and threat hunting at scale. Use when:
  (1) Conducting forensic investigations across multiple endpoints, (2) Hunting for
  indicators of compromise or suspicious activities, (3) Collecting endpoint telemetry
  and artifacts for incident analysis, (4) Performing live response and evidence
  preservation, (5) Monitoring endpoints for security events, (6) Creating custom
  forensic artifacts for specific threat scenarios.
version: 0.1.0
maintainer: SirAppSec
category: incident-response
tags: [forensics, incident-response, endpoint-detection, threat-hunting, vql, dfir, live-response, evidence-collection]
frameworks: [MITRE-ATT&CK, NIST]
dependencies:
  tools: [velociraptor]
references:
  - https://docs.velociraptor.app/
  - https://github.com/Velocidex/velociraptor
  - https://docs.velociraptor.app/artifact_references/
---

# Velociraptor Incident Response

## Overview

Velociraptor is an endpoint visibility and forensics platform for collecting host-based state information using Velociraptor Query Language (VQL). It operates in three core modes: **Collect** (targeted evidence gathering), **Monitor** (continuous event capture), and **Hunt** (proactive threat hunting).

**When to use this skill**:
- Active incident response requiring endpoint evidence collection
- Threat hunting across enterprise infrastructure
- Digital forensics investigations and timeline analysis
- Endpoint monitoring and anomaly detection
- Custom forensic artifact development for specific threats

## Quick Start

### Local Forensic Triage (Standalone Mode)

```bash
# Download Velociraptor binary for your platform
# https://github.com/Velocidex/velociraptor/releases

# Run GUI mode for interactive investigation
velociraptor gui

# Access web interface at https://127.0.0.1:8889/
# Default admin credentials shown in console output
```

### Enterprise Server Deployment

```bash
# Generate server configuration
velociraptor config generate > server.config.yaml

# Start server
velociraptor --config server.config.yaml frontend

# Generate client configuration
velociraptor --config server.config.yaml config client > client.config.yaml

# Deploy clients across endpoints
velociraptor --config client.config.yaml client
```

## Core Incident Response Workflows

### Workflow 1: Initial Compromise Investigation

Progress:
[ ] 1. Identify affected endpoints and timeframe
[ ] 2. Collect authentication logs and suspicious logins
[ ] 3. Gather process execution history and command lines
[ ] 4. Extract network connection artifacts
[ ] 5. Collect persistence mechanisms (scheduled tasks, autoruns, services)
[ ] 6. Analyze file system modifications and suspicious files
[ ] 7. Extract memory artifacts if needed
[ ] 8. Build timeline and document IOCs

Work through each step systematically. Check off completed items.

**Key VQL Artifacts**:
- `Windows.EventLogs.RDP` - Remote desktop authentication events
- `Windows.System.Pslist` - Running processes with details
- `Windows.Network.NetstatEnriched` - Network connections with process context
- `Windows.Persistence.PermanentWMIEvents` - WMI-based persistence
- `Windows.Timeline.Prefetch` - Program execution timeline
- `Windows.Forensics.Timeline` - Comprehensive filesystem timeline

### Workflow 2: Threat Hunting Campaign

Progress:
[ ] 1. Define threat hypothesis and IOCs
[ ] 2. Select or create custom VQL artifacts for detection
[ ] 3. Create hunt targeting relevant endpoint groups
[ ] 4. Execute hunt across infrastructure
[ ] 5. Monitor collection progress and errors
[ ] 6. Analyze results and identify positive matches
[ ] 7. Triage findings and escalate confirmed threats
[ ] 8. Document TTPs and update detections

Work through each step systematically. Check off completed items.

**Common Hunt Scenarios**:
- Lateral movement detection (PsExec, WMI, remote services)
- Webshell identification on web servers
- Suspicious scheduled task discovery
- Credential dumping tool artifacts
- Malicious PowerShell execution patterns

### Workflow 3: Evidence Collection for Forensics

Progress:
[ ] 1. Document collection requirements and scope
[ ] 2. Create offline collector with required artifacts
[ ] 3. Deploy collector to target endpoint(s)
[ ] 4. Execute collection and verify completion
[ ] 5. Retrieve collection archive
[ ] 6. Validate evidence integrity (hashes)
[ ] 7. Import into forensic platform for analysis
[ ] 8. Document chain of custody

Work through each step systematically. Check off completed items.

```bash
# Create offline collector (no server required)
velociraptor --config server.config.yaml artifacts collect \
  Windows.KapeFiles.Targets \
  Windows.EventLogs.Evtx \
  Windows.Registry.Sysinternals.Eulacheck \
  --output /path/to/collection.zip

# For custom artifact collection
velociraptor artifacts collect Custom.Artifact.Name --args param=value
```

## VQL Query Patterns

### Pattern 1: Process Investigation

Search for suspicious process execution patterns:

```sql
-- Find processes with unusual parent-child relationships
SELECT Pid, Ppid, Name, CommandLine, Username, Exe
FROM pslist()
WHERE Name =~ "(?i)(powershell|cmd|wscript|cscript)"
  AND CommandLine =~ "(?i)(invoke|download|iex|bypass|hidden)"
```

### Pattern 2: Network Connection Analysis

Identify suspicious network connections:

```sql
-- Active connections with process context
SELECT Laddr.IP AS LocalIP,
       Laddr.Port AS LocalPort,
       Raddr.IP AS RemoteIP,
       Raddr.Port AS RemotePort,
       Status, Pid,
       process_tracker_get(id=Pid).Name AS ProcessName,
       process_tracker_get(id=Pid).CommandLine AS CommandLine
FROM netstat()
WHERE Status = "ESTABLISHED"
  AND Raddr.IP =~ "^(?!10\\.)" -- External IPs only
```

### Pattern 3: File System Forensics

Timeline suspicious file modifications:

```sql
-- Recent file modifications in suspicious locations
SELECT FullPath, Size, Mtime, Atime, Ctime, Btime
FROM glob(globs="C:/Users/*/AppData/**/*.exe")
WHERE Mtime > timestamp(epoch=now() - 86400) -- Last 24 hours
ORDER BY Mtime DESC
```

### Pattern 4: Registry Persistence

Hunt for registry-based persistence:

```sql
-- Common autorun registry keys
SELECT Key.Name AS RegistryKey,
       ValueName,
       ValueData
FROM read_reg_key(globs="HKEY_LOCAL_MACHINE/SOFTWARE/Microsoft/Windows/CurrentVersion/Run/*")
WHERE ValueData =~ "(?i)(powershell|cmd|wscript|rundll32)"
```

For comprehensive VQL patterns and advanced queries, see [references/vql-patterns.md](references/vql-patterns.md)

## Custom Artifact Development

Create custom VQL artifacts for specific investigation needs:

```yaml
name: Custom.Windows.SuspiciousProcess
description: |
  Detect processes with suspicious characteristics for incident response.

parameters:
  - name: ProcessNameRegex
    default: "(?i)(powershell|cmd|wscript)"
    type: regex
  - name: CommandLineRegex
    default: "(?i)(invoke|download|bypass)"
    type: regex

sources:
  - query: |
      SELECT Pid, Ppid, Name, CommandLine, Username, Exe, CreateTime
      FROM pslist()
      WHERE Name =~ ProcessNameRegex
        AND CommandLine =~ CommandLineRegex
```

Save artifacts in YAML format and import via Velociraptor UI or command line.

**For artifact development guidance**, see [references/artifact-development.md](references/artifact-development.md)

## Security Considerations

- **Sensitive Data Handling**: VQL queries can collect credentials, PII, and sensitive files. Implement data minimization - only collect necessary evidence. Use encryption for evidence transport and storage.

- **Access Control**: Velociraptor server access provides significant endpoint control. Implement RBAC, audit all queries, and restrict administrative access. Use client certificates for authentication.

- **Audit Logging**: All VQL queries, hunts, and collections are logged. Enable audit trail for compliance. Document investigation scope and approvals.

- **Compliance**: Ensure evidence collection follows organizational policies and legal requirements. Document chain of custody for forensic investigations. Consider data sovereignty for multi-region deployments.

- **Operational Security**: Velociraptor generates significant endpoint activity. Plan for network bandwidth, endpoint performance impact, and detection by adversaries during covert investigations.

## Common Investigation Patterns

### Pattern: Ransomware Investigation

1. Identify patient zero endpoint
2. Collect: `Windows.Forensics.Timeline` for file modification patterns
3. Collect: `Windows.EventLogs.Evtx` for authentication events
4. Hunt for: Lateral movement artifacts across network
5. Hunt for: Scheduled tasks or services for persistence
6. Extract: Ransomware binary samples for malware analysis
7. Build: Timeline of infection spread and data encryption

### Pattern: Data Exfiltration Detection

1. Collect network connection history: `Windows.Network.NetstatEnriched`
2. Identify large outbound transfers to unusual destinations
3. Correlate with process execution and file access
4. Hunt for: Compression tools or staging directories
5. Examine: Browser downloads and cloud sync activities
6. Review: DNS queries for tunneling or C2 domains
7. Document: Data classification and breach scope

### Pattern: Insider Threat Investigation

1. Collect: User authentication and logon events
2. Track: USB device connections and file transfers
3. Monitor: Sensitive file access patterns
4. Review: Email and browser history (with authorization)
5. Analyze: Print spooler activity for document printing
6. Examine: Cloud storage access and uploads
7. Build: User activity timeline with behavioral anomalies

## Integration Points

- **SIEM Integration**: Export VQL results to Splunk, Elastic, or other SIEM platforms for correlation
- **Threat Intel Platforms**: Enrich IOCs with TIP integrations via VQL plugins
- **SOAR Platforms**: Trigger automated Velociraptor hunts from SOAR playbooks
- **Forensic Suites**: Import Velociraptor collections into X-Ways, Autopsy, or EnCase
- **EDR Interoperability**: Complement EDR with custom VQL detections and forensic depth

## Troubleshooting

### Issue: High CPU Usage During Collection

**Solution**:
- Limit concurrent VQL queries using `rate()` function
- Reduce glob scope to specific directories
- Use `--ops_per_second` limit when creating offline collectors
- Schedule resource-intensive hunts during maintenance windows

### Issue: Client Not Reporting to Server

**Solution**:
- Verify network connectivity and firewall rules (default: TCP 8000)
- Check client logs: `velociraptor --config client.config.yaml logs`
- Validate client certificate and enrollment status
- Ensure server frontend is running and accessible

### Issue: VQL Query Returns No Results

**Solution**:
- Test query in local notebook mode first
- Verify filesystem paths use correct syntax (forward slashes)
- Check plugin availability on target OS
- Use `log()` function to debug query execution
- Review client event logs for permission errors

## Bundled Resources

### Scripts (`scripts/`)

- `vql_query_builder.py` - Generate common VQL queries from templates
- `artifact_validator.py` - Validate custom artifact YAML syntax
- `evidence_collector.sh` - Automate offline collector deployment

### References (`references/`)

- `vql-patterns.md` - Comprehensive VQL query patterns for common IR scenarios
- `artifact-development.md` - Guide to creating custom forensic artifacts
- `mitre-attack-mapping.md` - MITRE ATT&CK technique detection artifacts
- `deployment-guide.md` - Enterprise server deployment and architecture

### Assets (`assets/`)

- `artifact-template.yaml` - Template for custom artifact development
- `hunt-template.yaml` - Hunt configuration template with best practices
- `offline-collector-config.yaml` - Offline collector configuration example

## References

- [Velociraptor Documentation](https://docs.velociraptor.app/)
- [VQL Reference](https://docs.velociraptor.app/vql_reference/)
- [Artifact Exchange](https://docs.velociraptor.app/exchange/)
- [GitHub Repository](https://github.com/Velocidex/velociraptor)
- [MITRE ATT&CK Framework](https://attack.mitre.org/)
