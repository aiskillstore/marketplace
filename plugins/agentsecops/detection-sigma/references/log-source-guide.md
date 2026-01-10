# Sigma Log Source Reference

## Log Source Categories

### process_creation

**Description**: Process creation/execution events

**Common Products**: Windows (Sysmon Event ID 1), Linux (auditd), EDR platforms

**Key Fields**:
- `Image` - Full path to executable
- `CommandLine` - Full command line with arguments
- `ParentImage` - Parent process executable path
- `ParentCommandLine` - Parent process command line
- `User` - User account that created process
- `IntegrityLevel` - Process integrity level (Windows)
- `Hashes` - File hashes (MD5, SHA256)

**Example**:
```yaml
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        Image|endswith: '\powershell.exe'
        CommandLine|contains: '-enc'
```

### network_connection

**Description**: Network connection events

**Common Products**: Sysmon Event ID 3, Firewall logs, EDR

**Key Fields**:
- `Image` - Process making connection
- `DestinationIp` - Remote IP address
- `DestinationPort` - Remote port
- `DestinationHostname` - Remote hostname
- `SourceIp` - Local IP address
- `SourcePort` - Local port
- `Initiated` - Connection initiated (true/false)

**Example**:
```yaml
logsource:
    category: network_connection
    product: windows
detection:
    selection:
        Initiated: 'true'
        DestinationPort: 4444
```

### file_event

**Description**: File creation, modification, deletion

**Common Products**: Sysmon Events 11/23, File integrity monitoring

**Key Fields**:
- `Image` - Process creating/modifying file
- `TargetFilename` - File path
- `CreationUtcTime` - File creation time

**Example**:
```yaml
logsource:
    category: file_event
    product: windows
detection:
    selection:
        TargetFilename|contains: '\Windows\Temp\'
        TargetFilename|endswith: '.exe'
```

### registry_event

**Description**: Registry key/value modifications

**Common Products**: Sysmon Events 12/13/14, Windows Event Logs

**Key Fields**:
- `TargetObject` - Registry key path
- `Details` - Registry value data
- `EventType` - SetValue, CreateKey, DeleteKey

**Example**:
```yaml
logsource:
    category: registry_event
    product: windows
detection:
    selection:
        TargetObject|contains: '\CurrentVersion\Run'
```

### image_load

**Description**: DLL/image load events

**Common Products**: Sysmon Event ID 7

**Key Fields**:
- `Image` - Process loading the image
- `ImageLoaded` - Path to loaded DLL/image
- `Signed` - Digital signature status

**Example**:
```yaml
logsource:
    category: image_load
    product: windows
detection:
    selection:
        ImageLoaded|endswith: '\evil.dll'
        Signed: 'false'
```

### dns_query

**Description**: DNS query events

**Common Products**: Sysmon Event ID 22, DNS server logs, proxy logs

**Key Fields**:
- `QueryName` - DNS name queried
- `QueryResults` - DNS response IPs
- `Image` - Process making query

**Example**:
```yaml
logsource:
    category: dns_query
    product: windows
detection:
    selection:
        QueryName|endswith: '.onion'
```

### web_request

**Description**: HTTP/HTTPS requests

**Common Products**: Proxy logs, web server logs, WAF

**Key Fields**:
- `c-uri` - Requested URI
- `c-useragent` - User agent string
- `cs-method` - HTTP method
- `sc-status` - HTTP status code

### authentication

**Description**: Authentication events (success/failure)

**Common Products**: Windows Security Events 4624/4625, Linux auth.log

**Key Fields**:
- `EventID` - 4624 (success), 4625 (failure), 4768 (Kerberos)
- `LogonType` - Type of logon (2=Interactive, 3=Network, 10=RemoteInteractive)
- `TargetUserName` - Account being authenticated
- `WorkstationName` - Source workstation
- `IpAddress` - Source IP

**Example**:
```yaml
logsource:
    category: authentication
    product: windows
detection:
    selection:
        EventID: 4625  # Failed logon
```

## Products

Common product values:

- `windows` - Windows OS
- `linux` - Linux OS
- `macos` - macOS
- `azure` - Microsoft Azure
- `aws` - Amazon Web Services
- `gcp` - Google Cloud Platform
- `m365` - Microsoft 365
- `okta` - Okta identity platform
- `firewall` - Generic firewall
- `proxy` - Web proxy

## Service Definitions

For cloud services, use service field:

```yaml
logsource:
    product: azure
    service: azuread
```

Common services:
- `azuread` - Azure Active Directory
- `azureactivity` - Azure Activity Logs
- `cloudtrail` - AWS CloudTrail
- `cloudwatch` - AWS CloudWatch
- `gcp.audit` - GCP Audit Logs

## Field Naming Conventions

Sigma uses normalized field names:

### Process Fields
- `Image` - Full executable path
- `CommandLine` - Command line arguments
- `ParentImage` - Parent process path
- `User` - Username
- `ProcessId` - Process ID

### Network Fields
- `SourceIp` / `DestinationIp`
- `SourcePort` / `DestinationPort`
- `Protocol` - Network protocol

### File Fields
- `TargetFilename` - File path
- `SourceFilename` - Original file location (for copies/moves)

### Registry Fields
- `TargetObject` - Registry key path
- `Details` - Registry value data

## Backend-Specific Mappings

Each backend maps these generic fields to product-specific field names:

**Sigma Generic** → **Splunk Sysmon**:
- `Image` → `Image`
- `CommandLine` → `CommandLine`
- `ParentImage` → `ParentImage`

**Sigma Generic** → **Elasticsearch ECS**:
- `Image` → `process.executable`
- `CommandLine` → `process.command_line`
- `ParentImage` → `process.parent.executable`

## Log Source Discovery

To identify available log sources:

1. **Review SIEM data sources**: Check what logs are ingested
2. **Verify field mappings**: Ensure Sigma fields map correctly
3. **Test conversions**: Convert sample rules and validate output
4. **Check coverage**: Ensure critical log sources are available

## Resources

- [Sigma Log Sources](https://github.com/SigmaHQ/sigma/wiki/Log-Sources)
- [Sysmon Event IDs](https://docs.microsoft.com/en-us/sysinternals/downloads/sysmon)
- [Windows Security Events](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/)
