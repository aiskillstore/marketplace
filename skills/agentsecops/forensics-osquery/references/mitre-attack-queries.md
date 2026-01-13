# MITRE ATT&CK Detection Queries for osquery

Pre-built osquery detection queries mapped to MITRE ATT&CK techniques for threat hunting and incident response.

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

## Initial Access

### T1078 - Valid Accounts

Detect unusual account usage patterns.

```sql
-- Unusual login times or locations
SELECT username, tty, host, time
FROM last
WHERE time > (strftime('%s', 'now') - 86400)
ORDER BY time DESC;

-- Failed authentication attempts (requires auth logs)
SELECT * FROM logged_in_users WHERE user NOT IN (SELECT username FROM users);
```

### T1190 - Exploit Public-Facing Application

Detect web server exploitation indicators.

```sql
-- Web server processes spawning shells
SELECT p1.name AS webserver, p1.cmdline,
       p2.name AS child_process, p2.cmdline AS child_cmdline
FROM processes p1
JOIN processes p2 ON p1.pid = p2.parent
WHERE p1.name IN ('httpd', 'nginx', 'apache2', 'w3wp.exe', 'java')
  AND p2.name IN ('bash', 'sh', 'cmd.exe', 'powershell.exe', 'python', 'perl');
```

## Execution

### T1059.001 - PowerShell

Detect suspicious PowerShell execution.

```sql
SELECT pid, name, path, cmdline, parent
FROM processes
WHERE name LIKE '%powershell%'
  AND (cmdline LIKE '%EncodedCommand%'
       OR cmdline LIKE '%-enc%'
       OR cmdline LIKE '%FromBase64String%'
       OR cmdline LIKE '%Invoke-Expression%'
       OR cmdline LIKE '%IEX%'
       OR cmdline LIKE '%DownloadString%'
       OR cmdline LIKE '%-w hidden%'
       OR cmdline LIKE '%-WindowStyle hidden%');
```

### T1059.003 - Windows Command Shell

Detect suspicious cmd.exe usage.

```sql
SELECT pid, name, path, cmdline, parent
FROM processes
WHERE name = 'cmd.exe'
  AND (cmdline LIKE '%/c%'
       OR cmdline LIKE '%&%'
       OR cmdline LIKE '%|%'
       OR cmdline LIKE '%<%'
       OR cmdline LIKE '%>%');
```

### T1059.004 - Unix Shell

Detect suspicious shell execution.

```sql
SELECT pid, name, path, cmdline, parent, uid
FROM processes
WHERE name IN ('bash', 'sh', 'zsh', 'ksh')
  AND (cmdline LIKE '%curl%http%'
       OR cmdline LIKE '%wget%http%'
       OR cmdline LIKE '%nc%'
       OR cmdline LIKE '%netcat%'
       OR cmdline LIKE '%/dev/tcp%'
       OR cmdline LIKE '%base64%');
```

### T1053 - Scheduled Task/Job

Detect suspicious scheduled tasks.

```sql
-- Suspicious cron jobs (Linux/macOS)
SELECT command, path, minute, hour
FROM crontab
WHERE command LIKE '%curl%'
   OR command LIKE '%wget%'
   OR command LIKE '%/tmp/%'
   OR command LIKE '%bash -i%'
   OR command LIKE '%python -c%';

-- Suspicious scheduled tasks (Windows)
SELECT name, action, path, enabled
FROM scheduled_tasks
WHERE enabled = 1
  AND (action LIKE '%powershell%'
       OR action LIKE '%cmd%'
       OR action LIKE '%wscript%'
       OR action LIKE '%mshta%');
```

## Persistence

### T1547.001 - Registry Run Keys (Windows)

Detect persistence via registry.

```sql
SELECT key, name, path, data
FROM registry
WHERE (key LIKE '%\\Run' OR key LIKE '%\\RunOnce')
  AND (data LIKE '%AppData%'
       OR data LIKE '%Temp%'
       OR data LIKE '%ProgramData%'
       OR data LIKE '%.vbs'
       OR data LIKE '%.js');
```

### T1547.006 - Kernel Modules and Extensions

Detect unauthorized kernel modules.

```sql
-- Linux kernel modules
SELECT name, size, used_by, status
FROM kernel_modules
WHERE name NOT IN (
  'ip_tables', 'x_tables', 'nf_conntrack', 'nf_defrag_ipv4',
  'iptable_filter', 'iptable_nat', 'ipt_MASQUERADE'
);

-- macOS kernel extensions
SELECT name, version, path
FROM kernel_extensions
WHERE loaded = 1
  AND path NOT LIKE '/System/%'
  AND path NOT LIKE '/Library/Extensions/%';
```

### T1053.003 - Cron (Linux/macOS)

Detect malicious cron jobs.

```sql
SELECT event, command, path, minute, hour, day_of_week
FROM crontab
WHERE command LIKE '%curl%http%'
   OR command LIKE '%wget%http%'
   OR command LIKE '%bash -i%'
   OR command LIKE '%python%socket%'
   OR command LIKE '%nc%'
   OR command LIKE '%/dev/tcp%'
   OR path LIKE '%/tmp/%'
   OR path LIKE '%/var/tmp/%';
```

### T1543.002 - Systemd Service (Linux)

Detect malicious systemd services.

```sql
SELECT name, fragment_path, description, active_state
FROM systemd_units
WHERE active_state = 'active'
  AND fragment_path NOT LIKE '/usr/lib/systemd/system/%'
  AND fragment_path NOT LIKE '/lib/systemd/system/%';
```

## Privilege Escalation

### T1548.003 - Sudo and Sudo Caching

Detect sudo abuse.

```sql
SELECT pid, name, cmdline, uid, euid, parent
FROM processes
WHERE name = 'sudo'
  AND (cmdline LIKE '%-i%'
       OR cmdline LIKE '%-s%'
       OR cmdline LIKE '%-u root%');
```

### T1548.001 - Setuid and Setgid

Find suspicious SUID/SGID binaries.

```sql
SELECT path, filename, mode, uid, gid
FROM file
WHERE (mode LIKE '%4%' OR mode LIKE '%2%')
  AND (path LIKE '/tmp/%'
       OR path LIKE '/var/tmp/%'
       OR path LIKE '/home/%'
       OR path LIKE '/dev/shm/%');
```

### T1543.001 - Launch Agent (macOS)

Detect malicious launch agents.

```sql
SELECT name, path, program, program_arguments, run_at_load
FROM launchd
WHERE run_at_load = 1
  AND (path LIKE '%/tmp/%'
       OR path LIKE '%/Users/%/Library/LaunchAgents/%'
       OR program LIKE '%curl%'
       OR program LIKE '%bash%');
```

## Defense Evasion

### T1055 - Process Injection

Detect process injection techniques.

```sql
-- Windows process injection indicators
SELECT pid, name, path, cmdline
FROM processes
WHERE cmdline LIKE '%VirtualAllocEx%'
   OR cmdline LIKE '%WriteProcessMemory%'
   OR cmdline LIKE '%CreateRemoteThread%'
   OR cmdline LIKE '%QueueUserAPC%'
   OR cmdline LIKE '%SetThreadContext%';

-- Processes with deleted executables (Linux indicator)
SELECT pid, name, path, cmdline, parent
FROM processes
WHERE on_disk = 0;
```

### T1070.004 - File Deletion

Detect log and evidence deletion.

```sql
SELECT pid, name, cmdline, path
FROM processes
WHERE (cmdline LIKE '%rm%'
       OR cmdline LIKE '%del%'
       OR cmdline LIKE '%shred%'
       OR cmdline LIKE '%wipe%')
  AND (cmdline LIKE '%log%'
       OR cmdline LIKE '%audit%'
       OR cmdline LIKE '%history%'
       OR cmdline LIKE '%bash_history%');
```

### T1027 - Obfuscated Files or Information

Detect encoding and obfuscation.

```sql
SELECT pid, name, path, cmdline
FROM processes
WHERE cmdline LIKE '%base64%'
   OR cmdline LIKE '%certutil%decode%'
   OR cmdline LIKE '%[Convert]::FromBase64String%'
   OR cmdline LIKE '%openssl enc%'
   OR cmdline LIKE '%uuencode%';
```

### T1564.001 - Hidden Files and Directories

Find hidden files in unusual locations.

```sql
SELECT path, filename, size, mtime
FROM file
WHERE filename LIKE '.%'
  AND (path LIKE '/tmp/%'
       OR path LIKE '/var/tmp/%'
       OR path LIKE '/dev/shm/%')
  AND size > 0;
```

## Credential Access

### T1003.001 - LSASS Memory (Windows)

Detect LSASS dumping.

```sql
SELECT pid, name, path, cmdline, parent
FROM processes
WHERE name IN ('mimikatz.exe', 'procdump.exe', 'pwdump.exe')
   OR cmdline LIKE '%sekurlsa%'
   OR cmdline LIKE '%lsadump%'
   OR cmdline LIKE '%procdump%lsass%'
   OR cmdline LIKE '%comsvcs.dll%MiniDump%';
```

### T1003.008 - /etc/passwd and /etc/shadow

Detect access to credential files.

```sql
-- Processes accessing password files
SELECT p.name, p.cmdline, pm.path
FROM processes p
JOIN process_memory_map pm ON p.pid = pm.pid
WHERE pm.path IN ('/etc/shadow', '/etc/passwd', '/etc/master.passwd')
  AND p.name NOT IN ('sshd', 'login', 'su', 'sudo');
```

### T1552.001 - Credentials in Files

Search for credential files.

```sql
SELECT path, filename, size
FROM file
WHERE (filename LIKE '%password%'
       OR filename LIKE '%credential%'
       OR filename LIKE '%secret%'
       OR filename LIKE '%.pem'
       OR filename LIKE '%.key'
       OR filename = '.bash_history'
       OR filename = '.zsh_history')
  AND path LIKE '/home/%';
```

## Discovery

### T1057 - Process Discovery

Detect process enumeration.

```sql
SELECT pid, name, cmdline, parent
FROM processes
WHERE cmdline LIKE '%ps aux%'
   OR cmdline LIKE '%tasklist%'
   OR cmdline LIKE '%Get-Process%'
   OR name IN ('ps', 'tasklist.exe');
```

### T1082 - System Information Discovery

Detect system reconnaissance.

```sql
SELECT pid, name, cmdline
FROM processes
WHERE cmdline LIKE '%systeminfo%'
   OR cmdline LIKE '%uname -a%'
   OR cmdline LIKE '%Get-ComputerInfo%'
   OR cmdline LIKE '%hostnamectl%'
   OR cmdline LIKE '%sw_vers%';
```

### T1083 - File and Directory Discovery

Detect file enumeration.

```sql
SELECT pid, name, cmdline
FROM processes
WHERE cmdline LIKE '%find%'
   OR cmdline LIKE '%dir /s%'
   OR cmdline LIKE '%ls -la%'
   OR cmdline LIKE '%Get-ChildItem%';
```

### T1087 - Account Discovery

Detect account enumeration.

```sql
SELECT pid, name, cmdline
FROM processes
WHERE cmdline LIKE '%net user%'
   OR cmdline LIKE '%net group%'
   OR cmdline LIKE '%net localgroup%'
   OR cmdline LIKE '%Get-LocalUser%'
   OR cmdline LIKE '%whoami%'
   OR cmdline LIKE '%id%';
```

### T1046 - Network Service Scanning

Detect network scanning activity.

```sql
SELECT pid, name, cmdline
FROM processes
WHERE cmdline LIKE '%nmap%'
   OR cmdline LIKE '%masscan%'
   OR cmdline LIKE '%netcat%'
   OR cmdline LIKE '%nc%'
   OR name IN ('nmap', 'masscan', 'nc', 'netcat');
```

## Lateral Movement

### T1021.001 - Remote Desktop Protocol

Detect RDP connections.

```sql
SELECT p.pid, p.name, p.cmdline, ps.remote_address, ps.remote_port
FROM processes p
JOIN process_open_sockets ps ON p.pid = ps.pid
WHERE ps.remote_port = 3389
   OR p.name LIKE '%mstsc%'
   OR p.name LIKE '%rdp%';
```

### T1021.002 - SMB/Windows Admin Shares

Detect SMB lateral movement.

```sql
SELECT pid, name, cmdline
FROM processes
WHERE cmdline LIKE '%\\\\%\\admin$%'
   OR cmdline LIKE '%\\\\%\\c$%'
   OR cmdline LIKE '%net use%'
   OR cmdline LIKE '%PsExec%';
```

### T1021.004 - SSH

Detect SSH lateral movement.

```sql
-- Outbound SSH connections
SELECT p.pid, p.name, p.cmdline, ps.remote_address, ps.remote_port
FROM processes p
JOIN process_open_sockets ps ON p.pid = ps.pid
WHERE ps.remote_port = 22
  AND p.name = 'ssh';

-- Unusual SSH sessions
SELECT user, tty, host, time
FROM logged_in_users
WHERE tty LIKE 'pts/%'
  AND user NOT IN ('root', 'admin');
```

## Collection

### T1560.001 - Archive via Utility

Detect data archiving for staging.

```sql
SELECT pid, name, cmdline, path
FROM processes
WHERE cmdline LIKE '%tar%'
   OR cmdline LIKE '%zip%'
   OR cmdline LIKE '%7z%'
   OR cmdline LIKE '%rar%'
   OR cmdline LIKE '%Compress-Archive%';
```

### T1119 - Automated Collection

Detect automated data collection scripts.

```sql
SELECT pid, name, cmdline
FROM processes
WHERE (cmdline LIKE '%find%'
       OR cmdline LIKE '%grep%'
       OR cmdline LIKE '%Select-String%')
  AND (cmdline LIKE '%password%'
       OR cmdline LIKE '%credential%'
       OR cmdline LIKE '%secret%'
       OR cmdline LIKE '%.doc%'
       OR cmdline LIKE '%.xls%');
```

## Exfiltration

### T1041 - Exfiltration Over C2 Channel

Detect suspicious network connections.

```sql
-- Unusual outbound connections
SELECT p.name, p.cmdline, ps.remote_address, ps.remote_port, ps.protocol
FROM processes p
JOIN process_open_sockets ps ON p.pid = ps.pid
WHERE ps.remote_address NOT IN ('127.0.0.1', '::1')
  AND ps.remote_port NOT IN (80, 443, 22, 53, 3389)
  AND ps.state = 'ESTABLISHED';
```

### T1048.003 - Exfiltration Over Unencrypted/Obfuscated Non-C2 Protocol

Detect data exfiltration via common tools.

```sql
SELECT pid, name, cmdline
FROM processes
WHERE cmdline LIKE '%curl%'
   OR cmdline LIKE '%wget%'
   OR cmdline LIKE '%scp%'
   OR cmdline LIKE '%ftp%'
   OR cmdline LIKE '%rsync%';
```

## Query Usage Notes

1. **Test queries** in a lab environment before production use
2. **Tune for environment** - add whitelist filters for legitimate activity
3. **Combine queries** - join multiple detections for higher confidence
4. **Time window** - add time filters to reduce result sets
5. **Baseline first** - understand normal activity before hunting

## Reference

- [MITRE ATT&CK Framework](https://attack.mitre.org/)
- [MITRE ATT&CK Techniques](https://attack.mitre.org/techniques/enterprise/)
