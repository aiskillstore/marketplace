# MITRE ATT&CK Technique Detection with Velociraptor

Mapping of MITRE ATT&CK techniques to Velociraptor artifacts and VQL queries.

## Table of Contents
- [Initial Access](#initial-access)
- [Execution](#execution)
- [Persistence](#persistence)
- [Privilege Escalation](#privilege-escalation)
- [Defense Evasion](#defense-evasion)
- [Credential Access](#credential-access)
- [Discovery](#discovery)
- [Lateral Movement](#lateral-movement)
- [Collection](#collection)
- [Exfiltration](#exfiltration)
- [Command and Control](#command-and-control)

## Initial Access

### T1078: Valid Accounts

**Artifacts**:
- `Windows.EventLogs.EvtxHunter` (EventID 4624, 4625)
- `Windows.EventLogs.RDP`

**VQL Query**:
```sql
-- Detect unusual logon patterns
SELECT timestamp(epoch=System.TimeCreated.SystemTime) AS LogonTime,
       EventData.TargetUserName AS Username,
       EventData.IpAddress AS SourceIP,
       EventData.LogonType AS LogonType,
       EventData.WorkstationName AS Workstation
FROM parse_evtx(filename="C:/Windows/System32/winevt/Logs/Security.evtx")
WHERE System.EventID.Value = 4624
  AND (
    EventData.LogonType IN (3, 10)  -- Network or RemoteInteractive
    OR timestamp(epoch=System.TimeCreated.SystemTime).Hour NOT IN (8,9,10,11,12,13,14,15,16,17)  -- Off-hours
  )
ORDER BY LogonTime DESC
```

### T1566: Phishing

**Artifacts**:
- `Windows.Forensics.Lnk`
- `Windows.Applications.Office.Keywords`

**VQL Query**:
```sql
-- Suspicious Office document execution
SELECT FullPath,
       Mtime,
       read_file(filename=FullPath, length=100000) AS Content
FROM glob(globs=[
  "C:/Users/*/Downloads/**/*.doc*",
  "C:/Users/*/Downloads/**/*.xls*"
])
WHERE Content =~ "(?i)(macro|vba|shell|exec|powershell)"
  AND Mtime > timestamp(epoch=now() - 604800)
```

## Execution

### T1059.001: PowerShell

**Artifacts**:
- `Windows.EventLogs.PowershellScriptblock`
- `Windows.System.Powershell.PSReadline`

**VQL Query**:
```sql
-- Malicious PowerShell execution
SELECT timestamp(epoch=System.TimeCreated.SystemTime) AS ExecutionTime,
       EventData.ScriptBlockText AS Command,
       EventData.Path AS ScriptPath
FROM parse_evtx(filename="C:/Windows/System32/winevt/Logs/Microsoft-Windows-PowerShell%4Operational.evtx")
WHERE System.EventID.Value = 4104  -- Script Block Logging
  AND EventData.ScriptBlockText =~ "(?i)(invoke-expression|iex|downloadstring|webclient|bypass|hidden|encodedcommand)"
ORDER BY ExecutionTime DESC
```

### T1059.003: Windows Command Shell

**Artifacts**:
- `Windows.System.Pslist`
- `Windows.EventLogs.ProcessCreation`

**VQL Query**:
```sql
-- Suspicious cmd.exe usage
SELECT Pid, Ppid, Name, CommandLine, Username, CreateTime
FROM pslist()
WHERE Name =~ "(?i)cmd.exe"
  AND CommandLine =~ "(?i)(/c|/k|/r)"
  AND Ppid IN (
    SELECT Pid FROM pslist()
    WHERE Name =~ "(?i)(winword|excel|powerpnt|acrobat|outlook)"
  )
```

### T1053.005: Scheduled Task

**Artifacts**:
- `Windows.System.TaskScheduler`
- `Windows.EventLogs.ScheduledTasks`

**VQL Query**:
```sql
-- Recently created scheduled tasks
SELECT FullPath AS TaskPath,
       parse_xml(file=FullPath).Task.Actions.Exec.Command AS Command,
       parse_xml(file=FullPath).Task.Principals.Principal.UserId AS RunAsUser,
       timestamp(epoch=Mtime) AS Created
FROM glob(globs="C:/Windows/System32/Tasks/**")
WHERE NOT IsDir
  AND Mtime > timestamp(epoch=now() - 86400)
  AND Command != ""
ORDER BY Created DESC
```

## Persistence

### T1547.001: Registry Run Keys

**Artifacts**:
- `Windows.Persistence.PermanentRuns`
- `Windows.System.StartupItems`

**VQL Query**:
```sql
-- Autorun registry entries
SELECT Key.FullPath AS RegistryKey,
       ValueName,
       ValueData.value AS ExecutablePath,
       timestamp(epoch=Key.Mtime) AS LastModified
FROM read_reg_key(globs=[
  "HKEY_LOCAL_MACHINE/SOFTWARE/Microsoft/Windows/CurrentVersion/Run/*",
  "HKEY_LOCAL_MACHINE/SOFTWARE/Microsoft/Windows/CurrentVersion/RunOnce/*",
  "HKEY_CURRENT_USER/SOFTWARE/Microsoft/Windows/CurrentVersion/Run/*",
  "HKEY_LOCAL_MACHINE/SOFTWARE/WOW6432Node/Microsoft/Windows/CurrentVersion/Run/*"
])
WHERE ValueData.value != ""
ORDER BY LastModified DESC
```

### T1543.003: Windows Service

**Artifacts**:
- `Windows.System.Services`
- `Windows.EventLogs.ServiceCreation`

**VQL Query**:
```sql
-- Suspicious services
SELECT Key.Name AS ServiceName,
       ImagePath.value AS ExecutablePath,
       DisplayName.value AS DisplayName,
       Start.value AS StartType,
       timestamp(epoch=Key.Mtime) AS LastModified
FROM read_reg_key(globs="HKEY_LOCAL_MACHINE/SYSTEM/CurrentControlSet/Services/*")
WHERE ImagePath.value != ""
  AND (
    ImagePath.value =~ "(?i)(temp|appdata|users)"
    OR ImagePath.value =~ "(?i)(powershell|cmd|wscript)"
    OR Key.Mtime > timestamp(epoch=now() - 604800)
  )
```

### T1546.003: WMI Event Subscription

**Artifacts**:
- `Windows.Persistence.PermanentWMIEvents`

**VQL Query**:
```sql
-- Malicious WMI event subscriptions
SELECT Namespace,
       FilterName,
       Query,
       ConsumerName,
       ConsumerType,
       ConsumerData
FROM wmi(
  query="SELECT * FROM __FilterToConsumerBinding",
  namespace="ROOT/Subscription"
)
WHERE ConsumerData =~ "(?i)(powershell|cmd|wscript|executable)"
```

## Privilege Escalation

### T1548.002: Bypass User Account Control

**Artifacts**:
- `Windows.EventLogs.EvtxHunter` (EventID 4688 with elevated token)

**VQL Query**:
```sql
-- UAC bypass indicators
SELECT timestamp(epoch=System.TimeCreated.SystemTime) AS EventTime,
       EventData.NewProcessName AS ProcessName,
       EventData.CommandLine AS CommandLine,
       EventData.ParentProcessName AS ParentProcess
FROM parse_evtx(filename="C:/Windows/System32/winevt/Logs/Security.evtx")
WHERE System.EventID.Value = 4688
  AND EventData.TokenElevationType = "%%1937"  -- Full token elevated
  AND (
    EventData.NewProcessName =~ "(?i)(fodhelper|computerdefaults|sdclt)"
    OR EventData.CommandLine =~ "(?i)(eventvwr|ms-settings)"
  )
```

### T1134: Access Token Manipulation

**Artifacts**:
- `Windows.EventLogs.EvtxHunter` (EventID 4672, 4673)

**VQL Query**:
```sql
-- Sensitive privilege use
SELECT timestamp(epoch=System.TimeCreated.SystemTime) AS EventTime,
       EventData.SubjectUserName AS Username,
       EventData.PrivilegeList AS Privileges
FROM parse_evtx(filename="C:/Windows/System32/winevt/Logs/Security.evtx")
WHERE System.EventID.Value = 4672
  AND EventData.PrivilegeList =~ "(SeDebugPrivilege|SeTcbPrivilege|SeLoadDriverPrivilege)"
```

## Defense Evasion

### T1070.001: Clear Windows Event Logs

**Artifacts**:
- `Windows.EventLogs.Cleared`

**VQL Query**:
```sql
-- Event log clearing
SELECT timestamp(epoch=System.TimeCreated.SystemTime) AS ClearedTime,
       System.Channel AS LogName,
       EventData.SubjectUserName AS Username
FROM parse_evtx(filename="C:/Windows/System32/winevt/Logs/Security.evtx")
WHERE System.EventID.Value IN (1102, 104)  -- Audit log cleared
ORDER BY ClearedTime DESC
```

### T1562.001: Disable or Modify Tools

**Artifacts**:
- `Windows.Forensics.Timeline`
- `Windows.Registry.RecentDocs`

**VQL Query**:
```sql
-- Security tool tampering
SELECT Key.FullPath AS RegistryKey,
       ValueName,
       ValueData.value AS Value,
       timestamp(epoch=Key.Mtime) AS Modified
FROM read_reg_key(globs=[
  "HKEY_LOCAL_MACHINE/SOFTWARE/Microsoft/Windows Defender/**",
  "HKEY_LOCAL_MACHINE/SOFTWARE/Policies/Microsoft/Windows Defender/**",
  "HKEY_LOCAL_MACHINE/SYSTEM/CurrentControlSet/Services/WinDefend/**"
])
WHERE (
  ValueName =~ "(?i)(DisableAntiSpyware|DisableRealtimeMonitoring|Start)"
  AND (ValueData.value = 1 OR ValueData.value = 4)
)
```

### T1055: Process Injection

**Artifacts**:
- `Windows.Detection.ProcessInjection`
- `Windows.Memory.Acquisition`

**VQL Query**:
```sql
-- Detect process injection via memory protections
SELECT Pid,
       process_tracker_get(id=Pid).Name AS ProcessName,
       Address,
       Size,
       Protection,
       Type
FROM vad()
WHERE Protection =~ "EXECUTE.*WRITE"  -- RWX memory
  AND Type = "Private"
  AND process_tracker_get(id=Pid).Name NOT IN ("chrome.exe", "firefox.exe")  -- Exclude known JIT
```

## Credential Access

### T1003.001: LSASS Memory

**Artifacts**:
- `Windows.EventLogs.ProcessAccess`
- `Windows.Detection.Mimikatz`

**VQL Query**:
```sql
-- LSASS access attempts
SELECT timestamp(epoch=System.TimeCreated.SystemTime) AS AccessTime,
       EventData.SourceProcessId AS SourcePID,
       EventData.SourceImage AS SourceImage,
       EventData.TargetImage AS TargetImage,
       EventData.GrantedAccess AS AccessRights
FROM parse_evtx(filename="C:/Windows/System32/winevt/Logs/Microsoft-Windows-Sysmon%4Operational.evtx")
WHERE System.EventID.Value = 10  -- ProcessAccess
  AND EventData.TargetImage =~ "(?i)lsass.exe"
  AND EventData.GrantedAccess =~ "(0x1010|0x1410|0x143A)"  -- Suspicious access rights
```

### T1003.002: Security Account Manager

**Artifacts**:
- `Windows.Forensics.SAM`
- `Windows.EventLogs.EvtxHunter`

**VQL Query**:
```sql
-- SAM registry hive access
SELECT FullPath,
       timestamp(epoch=Atime) AS AccessTime,
       timestamp(epoch=Mtime) AS ModifiedTime
FROM glob(globs=[
  "C:/Windows/System32/config/SAM",
  "C:/Windows/System32/config/SYSTEM",
  "C:/Windows/System32/config/SECURITY"
])
WHERE Atime > timestamp(epoch=now() - 86400)
```

### T1555: Credentials from Password Stores

**Artifacts**:
- `Windows.Forensics.DPAPI`
- `Windows.Browsers.ChromeHistory`

**VQL Query**:
```sql
-- Browser credential access
SELECT FullPath,
       timestamp(epoch=Atime) AS AccessTime
FROM glob(globs=[
  "C:/Users/*/AppData/Local/Google/Chrome/User Data/*/Login Data",
  "C:/Users/*/AppData/Roaming/Mozilla/Firefox/Profiles/*/logins.json"
])
WHERE Atime > timestamp(epoch=now() - 86400)
ORDER BY AccessTime DESC
```

## Discovery

### T1082: System Information Discovery

**Artifacts**:
- `Generic.Client.Info`
- `Windows.System.SystemInfo`

**VQL Query**:
```sql
-- System enumeration commands
SELECT Pid, Name, CommandLine, Username, CreateTime
FROM pslist()
WHERE CommandLine =~ "(?i)(systeminfo|whoami|ipconfig|hostname|ver)"
  AND CreateTime > timestamp(epoch=now() - 3600)
ORDER BY CreateTime DESC
```

### T1083: File and Directory Discovery

**Artifacts**:
- `Windows.EventLogs.ProcessCreation`

**VQL Query**:
```sql
-- File system enumeration
SELECT Pid, Name, CommandLine, CreateTime
FROM pslist()
WHERE CommandLine =~ "(?i)(dir|tree|findstr|where)"
  AND CommandLine =~ "(?i)(\\*|recursive|/s|/b)"
ORDER BY CreateTime DESC
```

### T1049: System Network Connections Discovery

**Artifacts**:
- `Windows.Network.Netstat`

**VQL Query**:
```sql
-- Network enumeration commands
SELECT Pid, Name, CommandLine, CreateTime
FROM pslist()
WHERE CommandLine =~ "(?i)(netstat|net use|net view|arp|route print|nslookup)"
ORDER BY CreateTime DESC
```

## Lateral Movement

### T1021.001: Remote Desktop Protocol

**Artifacts**:
- `Windows.EventLogs.RDP`
- `Windows.EventLogs.EvtxHunter`

**VQL Query**:
```sql
-- RDP lateral movement
SELECT timestamp(epoch=System.TimeCreated.SystemTime) AS LogonTime,
       EventData.TargetUserName AS Username,
       EventData.IpAddress AS SourceIP,
       System.Computer AS DestinationHost
FROM parse_evtx(filename="C:/Windows/System32/winevt/Logs/Security.evtx")
WHERE System.EventID.Value = 4624
  AND EventData.LogonType = 10  -- RemoteInteractive
  AND EventData.IpAddress != "127.0.0.1"
ORDER BY LogonTime DESC
```

### T1021.002: SMB/Windows Admin Shares

**Artifacts**:
- `Windows.EventLogs.EvtxHunter` (EventID 5140, 5145)

**VQL Query**:
```sql
-- Admin share access
SELECT timestamp(epoch=System.TimeCreated.SystemTime) AS AccessTime,
       EventData.SubjectUserName AS Username,
       EventData.IpAddress AS SourceIP,
       EventData.ShareName AS Share,
       EventData.RelativeTargetName AS FilePath
FROM parse_evtx(filename="C:/Windows/System32/winevt/Logs/Security.evtx")
WHERE System.EventID.Value = 5140
  AND EventData.ShareName =~ "(?i)(ADMIN\\$|C\\$|IPC\\$)"
```

### T1047: Windows Management Instrumentation

**Artifacts**:
- `Windows.EventLogs.WMIActivity`
- `Windows.System.Pslist`

**VQL Query**:
```sql
-- WMI process creation
SELECT Pid, Name, CommandLine, Username, CreateTime
FROM pslist()
WHERE (
  -- WMI spawned processes
  Ppid IN (SELECT Pid FROM pslist() WHERE Name =~ "(?i)wmiprvse.exe")

  -- Or WMIC usage
  OR (Name =~ "(?i)wmic.exe" AND CommandLine =~ "(?i)(process call create|/node:)")
)
ORDER BY CreateTime DESC
```

## Collection

### T1005: Data from Local System

**Artifacts**:
- `Windows.Forensics.Timeline`
- `Windows.Detection.Yara`

**VQL Query**:
```sql
-- Data staging detection
SELECT FullPath, Size,
       timestamp(epoch=Ctime) AS Created,
       timestamp(epoch=Mtime) AS Modified
FROM glob(globs=[
  "C:/Users/*/AppData/**/*.zip",
  "C:/Users/*/AppData/**/*.rar",
  "C:/Users/*/AppData/**/*.7z",
  "C:/Windows/Temp/**/*.zip"
])
WHERE Size > 10485760  -- > 10MB
  AND Ctime > timestamp(epoch=now() - 86400)
ORDER BY Size DESC
```

### T1119: Automated Collection

**Artifacts**:
- `Windows.System.Pslist`
- `Windows.EventLogs.ProcessCreation`

**VQL Query**:
```sql
-- Automated collection tools
SELECT Pid, Name, CommandLine, Username, CreateTime
FROM pslist()
WHERE CommandLine =~ "(?i)(robocopy|xcopy|tar|7z|winrar)"
  AND CommandLine =~ "(?i)(/s|recursive|mirror)"
```

## Exfiltration

### T1041: Exfiltration Over C2 Channel

**Artifacts**:
- `Windows.Network.NetstatEnriched`
- `Windows.Detection.NetworkAlerts`

**VQL Query**:
```sql
-- Large outbound transfers
SELECT Laddr.Port AS LocalPort,
       Raddr.IP AS RemoteIP,
       Raddr.Port AS RemotePort,
       Pid,
       process_tracker_get(id=Pid).Name AS ProcessName,
       process_tracker_get(id=Pid).CommandLine AS CommandLine
FROM netstat()
WHERE Status = "ESTABLISHED"
  AND Raddr.IP !~ "^(10\\.|172\\.(1[6-9]|2[0-9]|3[01])\\.|192\\.168\\.)"
  AND Raddr.Port NOT IN (80, 443, 22)
```

### T1052: Exfiltration Over Physical Medium

**Artifacts**:
- `Windows.Forensics.USBDevices`
- `Windows.EventLogs.USBActivity`

**VQL Query**:
```sql
-- USB file transfers
SELECT FullPath, Size,
       timestamp(epoch=Mtime) AS Modified
FROM glob(globs=["D:/**", "E:/**", "F:/**"])  -- Removable drives
WHERE Mtime > timestamp(epoch=now() - 86400)
  AND Size > 1048576  -- > 1MB
ORDER BY Mtime DESC, Size DESC
```

## Command and Control

### T1071: Application Layer Protocol

**Artifacts**:
- `Windows.Network.NetstatEnriched`
- `Windows.Detection.Sigma`

**VQL Query**:
```sql
-- Unusual outbound connections
SELECT Raddr.IP AS RemoteIP,
       Raddr.Port AS RemotePort,
       COUNT(*) AS ConnectionCount,
       GROUP_CONCAT(DISTINCT process_tracker_get(id=Pid).Name) AS Processes
FROM netstat()
WHERE Status = "ESTABLISHED"
  AND Raddr.IP !~ "^(10\\.|172\\.(1[6-9]|2[0-9]|3[01])\\.|192\\.168\\.)"
  AND Raddr.Port NOT IN (80, 443, 53, 22, 3389)
GROUP BY Raddr.IP, Raddr.Port
HAVING ConnectionCount > 10
```

### T1095: Non-Application Layer Protocol

**Artifacts**:
- `Windows.Network.RawConnections`

**VQL Query**:
```sql
-- Raw socket usage (ICMP tunneling, etc.)
SELECT Pid,
       process_tracker_get(id=Pid).Name AS ProcessName,
       process_tracker_get(id=Pid).CommandLine AS CommandLine,
       Protocol,
       Laddr.IP AS LocalIP,
       Raddr.IP AS RemoteIP
FROM netstat()
WHERE Protocol NOT IN ("TCP", "UDP")
  AND Raddr.IP != ""
```

### T1219: Remote Access Software

**Artifacts**:
- `Windows.System.Pslist`
- `Windows.Persistence.PermanentRuns`

**VQL Query**:
```sql
-- Remote access tools
SELECT Pid, Name, Exe, CommandLine, Username
FROM pslist()
WHERE Name =~ "(?i)(teamviewer|anydesk|logmein|ammyy|vnc|radmin|screenconnect)"
  OR Exe =~ "(?i)(remote|rdp|desktop|viewer)"
```
