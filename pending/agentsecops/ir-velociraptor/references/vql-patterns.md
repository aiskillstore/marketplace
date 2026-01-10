# VQL Query Patterns for Incident Response

Comprehensive VQL query patterns for common incident response and threat hunting scenarios.

## Table of Contents
- [Process Analysis](#process-analysis)
- [Network Forensics](#network-forensics)
- [File System Analysis](#file-system-analysis)
- [Registry Forensics](#registry-forensics)
- [Memory Analysis](#memory-analysis)
- [Event Log Analysis](#event-log-analysis)
- [Persistence Mechanisms](#persistence-mechanisms)
- [Lateral Movement Detection](#lateral-movement-detection)
- [Data Exfiltration](#data-exfiltration)
- [Malware Analysis](#malware-analysis)

## Process Analysis

### Suspicious Process Detection

```sql
-- Processes with suspicious characteristics
SELECT Pid, Ppid, Name, CommandLine, Username, Exe, CreateTime
FROM pslist()
WHERE (
  -- Suspicious parent-child relationships
  (Ppid IN (SELECT Pid FROM pslist() WHERE Name =~ "(?i)(winword|excel|powerpnt|acrobat)")
   AND Name =~ "(?i)(powershell|cmd|wscript|cscript)")

  -- Processes running from temp directories
  OR Exe =~ "(?i)(temp|tmp|appdata)"

  -- Processes with obfuscated command lines
  OR CommandLine =~ "(?i)(iex|invoke-expression|downloadstring|webclient|hidden|bypass)"
)
```

### Living-off-the-Land Binaries (LOLBins)

```sql
-- Detect abuse of legitimate Windows binaries
SELECT Pid, Name, CommandLine, Username, Exe
FROM pslist()
WHERE (
  -- certutil for downloading
  (Name =~ "(?i)certutil" AND CommandLine =~ "(?i)(urlcache|url)")

  -- bitsadmin for downloading
  OR (Name =~ "(?i)bitsadmin" AND CommandLine =~ "(?i)(transfer|download)")

  -- mshta for code execution
  OR (Name =~ "(?i)mshta" AND CommandLine =~ "(?i)(http|javascript|vbscript)")

  -- rundll32 suspicious usage
  OR (Name =~ "(?i)rundll32" AND CommandLine =~ "(?i)(javascript|url)")
)
```

### Process Injection Detection

```sql
-- Identify potential process injection
SELECT Pid, Name,
       AllocatedMemory,
       ProtectionFlags,
       Handles
FROM handles()
WHERE Type = "Section"
  AND ProtectionFlags =~ "EXECUTE"
  AND Name != ""
```

## Network Forensics

### External Connections

```sql
-- All external network connections with process context
SELECT Laddr.IP AS LocalIP,
       Laddr.Port AS LocalPort,
       Raddr.IP AS RemoteIP,
       Raddr.Port AS RemotePort,
       Status, Pid,
       process_tracker_get(id=Pid).Name AS ProcessName,
       process_tracker_get(id=Pid).Exe AS ProcessPath,
       process_tracker_get(id=Pid).CommandLine AS CommandLine
FROM netstat()
WHERE Status = "ESTABLISHED"
  AND Raddr.IP != ""
  AND Raddr.IP !~ "^(10\\.|172\\.(1[6-9]|2[0-9]|3[01])\\.|192\\.168\\.)" -- Exclude RFC1918
  AND Raddr.IP !~ "^(127\\.|169\\.254\\.)" -- Exclude localhost and link-local
```

### Unusual Port Activity

```sql
-- Connections on unusual ports
SELECT Raddr.IP AS RemoteIP,
       Raddr.Port AS RemotePort,
       COUNT(*) AS ConnectionCount,
       GROUP_CONCAT(DISTINCT process_tracker_get(id=Pid).Name) AS Processes
FROM netstat()
WHERE Status = "ESTABLISHED"
  AND Raddr.Port NOT IN (80, 443, 22, 3389, 445, 139, 53)
GROUP BY Raddr.IP, Raddr.Port
HAVING ConnectionCount > 5
```

### DNS Query Analysis

```sql
-- Suspicious DNS queries
SELECT query AS Domain,
       response AS IPAddress,
       timestamp(epoch=Time) AS QueryTime
FROM parse_evtx(filename="C:/Windows/System32/winevt/Logs/Microsoft-Windows-DNS-Client%4Operational.evtx")
WHERE System.EventID.Value = 3008
  AND (
    -- Long domain names (possible DGA)
    length(query) > 50

    -- High entropy domains
    OR query =~ "[a-z0-9]{20,}"

    -- Suspicious TLDs
    OR query =~ "\\.(tk|ml|ga|cf|gq)$"
  )
```

## File System Analysis

### Recently Modified Executables

```sql
-- Executables modified in last 7 days
SELECT FullPath, Size,
       timestamp(epoch=Mtime) AS ModifiedTime,
       timestamp(epoch=Ctime) AS CreatedTime,
       hash(path=FullPath, accessor="file") AS SHA256
FROM glob(globs=[
  "C:/Windows/System32/**/*.exe",
  "C:/Windows/SysWOW64/**/*.exe",
  "C:/Users/*/AppData/**/*.exe",
  "C:/ProgramData/**/*.exe"
])
WHERE Mtime > timestamp(epoch=now() - 604800) -- 7 days
ORDER BY Mtime DESC
```

### Webshell Detection

```sql
-- Potential webshells in web directories
SELECT FullPath, Size,
       timestamp(epoch=Mtime) AS ModifiedTime,
       read_file(filename=FullPath, length=1000) AS Content
FROM glob(globs=[
  "C:/inetpub/wwwroot/**/*.asp",
  "C:/inetpub/wwwroot/**/*.aspx",
  "C:/inetpub/wwwroot/**/*.php",
  "C:/xampp/htdocs/**/*.php"
])
WHERE Content =~ "(?i)(eval|base64_decode|exec|shell_exec|system|passthru|WScript\\.Shell)"
  OR FullPath =~ "(?i)(cmd|shell|upload|backdoor|c99)"
```

### Suspicious File Timestamps

```sql
-- Files with timestamp anomalies (timestomping detection)
SELECT FullPath,
       timestamp(epoch=Mtime) AS ModifiedTime,
       timestamp(epoch=Ctime) AS ChangeTime,
       timestamp(epoch=Btime) AS BornTime
FROM glob(globs="C:/Users/**/*.exe")
WHERE Mtime < Btime  -- Modified time before birth time (anomaly)
   OR Ctime < Btime  -- Change time before birth time
```

## Registry Forensics

### Autorun Locations

```sql
-- Comprehensive autorun registry key enumeration
SELECT Key.FullPath AS RegistryPath,
       ValueName,
       ValueData.value AS Value,
       timestamp(epoch=Key.Mtime) AS LastModified
FROM read_reg_key(globs=[
  "HKEY_LOCAL_MACHINE/SOFTWARE/Microsoft/Windows/CurrentVersion/Run/*",
  "HKEY_LOCAL_MACHINE/SOFTWARE/Microsoft/Windows/CurrentVersion/RunOnce/*",
  "HKEY_CURRENT_USER/SOFTWARE/Microsoft/Windows/CurrentVersion/Run/*",
  "HKEY_LOCAL_MACHINE/SOFTWARE/WOW6432Node/Microsoft/Windows/CurrentVersion/Run/*",
  "HKEY_LOCAL_MACHINE/SYSTEM/CurrentControlSet/Services/*"
])
WHERE ValueData.value != ""
```

### Recent Registry Modifications

```sql
-- Recently modified registry keys in security-sensitive locations
SELECT FullPath,
       timestamp(epoch=Mtime) AS ModifiedTime
FROM glob(globs=[
  "HKEY_LOCAL_MACHINE/SOFTWARE/Microsoft/Windows/CurrentVersion/**",
  "HKEY_LOCAL_MACHINE/SYSTEM/CurrentControlSet/**",
  "HKEY_CURRENT_USER/SOFTWARE/Microsoft/Windows/CurrentVersion/**"
], accessor="registry")
WHERE Mtime > timestamp(epoch=now() - 86400) -- Last 24 hours
ORDER BY Mtime DESC
```

### AppInit DLL Injection

```sql
-- Detect AppInit DLL injection mechanism
SELECT ValueName,
       ValueData.value AS DLLPath,
       timestamp(epoch=Key.Mtime) AS LastModified
FROM read_reg_key(globs=[
  "HKEY_LOCAL_MACHINE/SOFTWARE/Microsoft/Windows NT/CurrentVersion/Windows/AppInit_DLLs",
  "HKEY_LOCAL_MACHINE/SOFTWARE/WOW6432Node/Microsoft/Windows NT/CurrentVersion/Windows/AppInit_DLLs"
])
WHERE ValueData.value != ""
```

## Memory Analysis

### Suspicious Memory Regions

```sql
-- Memory regions with unusual protections
SELECT Pid,
       process_tracker_get(id=Pid).Name AS ProcessName,
       Address,
       Size,
       Protection
FROM vad()
WHERE Protection =~ "EXECUTE.*WRITE" -- RWX memory (suspicious)
  AND Type = "Private"
```

### Injected Code Detection

```sql
-- Detect potentially injected code
SELECT Pid,
       Name AS ProcessName,
       Vad.Address AS MemoryAddress,
       Vad.Protection AS Protection,
       Vad.Type AS MemoryType
FROM pslist()
LET Vad <= SELECT * FROM vad(pid=Pid)
WHERE Vad.Protection =~ "EXECUTE"
  AND Vad.Type = "Private"
  AND Vad.Name = ""
```

## Event Log Analysis

### Failed Logon Attempts

```sql
-- Failed authentication attempts
SELECT timestamp(epoch=System.TimeCreated.SystemTime) AS EventTime,
       EventData.TargetUserName AS Username,
       EventData.IpAddress AS SourceIP,
       EventData.WorkstationName AS Workstation,
       EventData.FailureReason AS Reason
FROM parse_evtx(filename="C:/Windows/System32/winevt/Logs/Security.evtx")
WHERE System.EventID.Value = 4625 -- Failed logon
ORDER BY EventTime DESC
LIMIT 1000
```

### Privilege Escalation Events

```sql
-- Privilege elevation and sensitive privilege use
SELECT timestamp(epoch=System.TimeCreated.SystemTime) AS EventTime,
       System.EventID.Value AS EventID,
       EventData.SubjectUserName AS User,
       EventData.PrivilegeList AS Privileges
FROM parse_evtx(filename="C:/Windows/System32/winevt/Logs/Security.evtx")
WHERE System.EventID.Value IN (4672, 4673, 4674) -- Special privilege events
  AND EventData.PrivilegeList =~ "(SeDebugPrivilege|SeTcbPrivilege|SeLoadDriverPrivilege)"
```

### Scheduled Task Creation

```sql
-- Detect scheduled task creation for persistence
SELECT timestamp(epoch=System.TimeCreated.SystemTime) AS EventTime,
       EventData.TaskName AS TaskName,
       EventData.UserContext AS RunAsUser,
       EventData.TaskContent AS TaskXML
FROM parse_evtx(filename="C:/Windows/System32/winevt/Logs/Microsoft-Windows-TaskScheduler%4Operational.evtx")
WHERE System.EventID.Value = 106 -- Task registered
ORDER BY EventTime DESC
```

## Persistence Mechanisms

### Comprehensive Persistence Hunt

```sql
-- Multi-vector persistence detection
LET RegistryAutoRuns = SELECT "Registry" AS Method, Key.FullPath AS Location, ValueData.value AS Value
FROM read_reg_key(globs="HKEY_LOCAL_MACHINE/SOFTWARE/Microsoft/Windows/CurrentVersion/Run/*")

LET ScheduledTasks = SELECT "Scheduled Task" AS Method, FullPath AS Location, "" AS Value
FROM glob(globs="C:/Windows/System32/Tasks/**")
WHERE NOT IsDir

LET Services = SELECT "Service" AS Method, Key.Name AS Location, ImagePath.value AS Value
FROM read_reg_key(globs="HKEY_LOCAL_MACHINE/SYSTEM/CurrentControlSet/Services/**/ImagePath")

LET StartupFolders = SELECT "Startup Folder" AS Method, FullPath AS Location, "" AS Value
FROM glob(globs=[
  "C:/Users/*/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/*",
  "C:/ProgramData/Microsoft/Windows/Start Menu/Programs/Startup/*"
])

SELECT * FROM chain(
  a=RegistryAutoRuns,
  b=ScheduledTasks,
  c=Services,
  d=StartupFolders
)
```

### WMI Event Subscription Persistence

```sql
-- Detect malicious WMI event subscriptions
SELECT Name,
       EventFilter,
       Consumer,
       timestamp(epoch=CreationDate) AS Created
FROM wmi_persist()
WHERE EventFilter != "" OR Consumer != ""
```

## Lateral Movement Detection

### PsExec Activity

```sql
-- PsExec service creation and execution
SELECT timestamp(epoch=System.TimeCreated.SystemTime) AS EventTime,
       EventData.ServiceName AS ServiceName,
       EventData.ImagePath AS ExecutablePath,
       EventData.AccountName AS Account
FROM parse_evtx(filename="C:/Windows/System32/winevt/Logs/System.evtx")
WHERE System.EventID.Value = 7045 -- Service installed
  AND (
    EventData.ServiceName =~ "(?i)PSEXESVC"
    OR EventData.ImagePath =~ "(?i)(\\\\\\\\.*\\\\.*\\\\|admin\\$|c\\$)"
  )
```

### Remote Desktop Activity

```sql
-- RDP logon activity
SELECT timestamp(epoch=System.TimeCreated.SystemTime) AS LogonTime,
       EventData.TargetUserName AS Username,
       EventData.IpAddress AS SourceIP,
       EventData.LogonType AS LogonType
FROM parse_evtx(filename="C:/Windows/System32/winevt/Logs/Security.evtx")
WHERE System.EventID.Value = 4624 -- Successful logon
  AND EventData.LogonType = 10 -- RemoteInteractive (RDP)
ORDER BY LogonTime DESC
```

### SMB/Admin Share Access

```sql
-- Network share access from remote systems
SELECT timestamp(epoch=System.TimeCreated.SystemTime) AS AccessTime,
       EventData.SubjectUserName AS Username,
       EventData.IpAddress AS SourceIP,
       EventData.ShareName AS ShareAccessed,
       EventData.ObjectName AS FileAccessed
FROM parse_evtx(filename="C:/Windows/System32/winevt/Logs/Security.evtx")
WHERE System.EventID.Value = 5140 -- Network share accessed
  AND EventData.ShareName =~ "(?i)(ADMIN\\$|C\\$|IPC\\$)"
```

## Data Exfiltration

### Large File Transfers

```sql
-- Files copied to removable media or network shares
SELECT FullPath,
       Size,
       timestamp(epoch=Mtime) AS LastModified,
       hash(path=FullPath, accessor="file").SHA256 AS SHA256
FROM glob(globs=[
  "D:/**", -- Removable drive
  "E:/**",
  "\\\\*/**" -- Network paths
])
WHERE Size > 10485760 -- Files larger than 10MB
  AND Mtime > timestamp(epoch=now() - 86400)
ORDER BY Size DESC
```

### USB Device History

```sql
-- USB device connection history
SELECT Key.Name AS DeviceID,
       FriendlyName.value AS DeviceName,
       timestamp(epoch=Key.Mtime) AS LastConnected
FROM read_reg_key(globs="HKEY_LOCAL_MACHINE/SYSTEM/CurrentControlSet/Enum/USBSTOR/**/FriendlyName")
ORDER BY LastConnected DESC
```

### Cloud Storage Activity

```sql
-- Files in cloud sync directories
SELECT FullPath, Size,
       timestamp(epoch=Mtime) AS LastModified
FROM glob(globs=[
  "C:/Users/*/OneDrive/**",
  "C:/Users/*/Dropbox/**",
  "C:/Users/*/Google Drive/**"
])
WHERE Mtime > timestamp(epoch=now() - 86400)
ORDER BY Mtime DESC
```

## Malware Analysis

### Suspicious File Indicators

```sql
-- Files with malware-associated characteristics
SELECT FullPath,
       Size,
       timestamp(epoch=Mtime) AS ModifiedTime,
       hash(path=FullPath, accessor="file") AS Hashes
FROM glob(globs=[
  "C:/Windows/Temp/**/*.exe",
  "C:/Users/*/AppData/Local/Temp/**/*.exe",
  "C:/ProgramData/**/*.exe"
])
WHERE (
  -- Small executables (potential droppers)
  Size < 102400

  -- Or recently created
  OR Mtime > timestamp(epoch=now() - 3600)
)
```

### Packed Executable Detection

```sql
-- Detect potentially packed executables (high entropy)
SELECT FullPath,
       parse_pe(file=FullPath).Entropy AS Entropy,
       parse_pe(file=FullPath).Sections AS Sections
FROM glob(globs="C:/Users/**/*.exe")
WHERE parse_pe(file=FullPath).Entropy > 7.0 -- High entropy suggests packing
```

### Malicious Scripts

```sql
-- Suspicious PowerShell/VBS scripts
SELECT FullPath,
       Size,
       timestamp(epoch=Mtime) AS ModifiedTime,
       read_file(filename=FullPath, length=5000) AS Content
FROM glob(globs=[
  "C:/Users/**/*.ps1",
  "C:/Users/**/*.vbs",
  "C:/Users/**/*.js",
  "C:/Windows/Temp/**/*.ps1"
])
WHERE Content =~ "(?i)(invoke-expression|iex|downloadstring|webclient|bypass|hidden|encodedcommand)"
```

## Advanced Hunting Patterns

### Threat Hunting with Multiple Indicators

```sql
-- Correlate multiple suspicious indicators
LET SuspiciousProcesses = SELECT Pid, Name, CommandLine
FROM pslist()
WHERE CommandLine =~ "(?i)(bypass|hidden|encodedcommand)"

LET SuspiciousConnections = SELECT Pid, Raddr.IP AS RemoteIP
FROM netstat()
WHERE Status = "ESTABLISHED"
  AND Raddr.IP !~ "^(10\\.|172\\.(1[6-9]|2[0-9]|3[01])\\.|192\\.168\\.)"

SELECT sp.Pid,
       sp.Name,
       sp.CommandLine,
       GROUP_CONCAT(sc.RemoteIP) AS ConnectedIPs
FROM SuspiciousProcesses sp
JOIN SuspiciousConnections sc ON sp.Pid = sc.Pid
GROUP BY sp.Pid
```

### Timeline Analysis

```sql
-- Comprehensive timeline of system activity
SELECT timestamp(epoch=Timestamp) AS EventTime,
       Source,
       EventType,
       Details
FROM chain(
  a={SELECT Mtime AS Timestamp, "FileSystem" AS Source, "FileCreated" AS EventType, FullPath AS Details
     FROM glob(globs="C:/Users/**") WHERE Mtime > timestamp(epoch=now() - 86400)},
  b={SELECT System.TimeCreated.SystemTime AS Timestamp, "EventLog" AS Source,
     format(format="EventID:%v", args=System.EventID.Value) AS EventType,
     EventData AS Details
     FROM parse_evtx(filename="C:/Windows/System32/winevt/Logs/Security.evtx")
     WHERE System.TimeCreated.SystemTime > timestamp(epoch=now() - 86400)},
  c={SELECT Key.Mtime AS Timestamp, "Registry" AS Source, "KeyModified" AS EventType, Key.FullPath AS Details
     FROM glob(globs="HKEY_LOCAL_MACHINE/SOFTWARE/**", accessor="registry")
     WHERE Key.Mtime > timestamp(epoch=now() - 86400)}
)
ORDER BY EventTime DESC
```
