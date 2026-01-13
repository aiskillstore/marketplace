# osquery Table Reference for Forensic Investigations

Comprehensive guide to osquery tables most relevant for incident response and forensic analysis.

## Table of Contents

- [Process Tables](#process-tables)
- [Network Tables](#network-tables)
- [File System Tables](#file-system-tables)
- [User and Authentication Tables](#user-and-authentication-tables)
- [System Information Tables](#system-information-tables)
- [Persistence Mechanism Tables](#persistence-mechanism-tables)
- [Platform-Specific Tables](#platform-specific-tables)

## Process Tables

### processes

Query running processes with detailed information.

**Key columns**: pid, name, path, cmdline, cwd, uid, gid, parent, pgroup, state, on_disk, start_time

```sql
-- Basic process listing
SELECT pid, name, path, cmdline, uid FROM processes;

-- Processes with deleted executables (malware indicator)
SELECT * FROM processes WHERE on_disk = 0;

-- Process tree
SELECT p1.pid, p1.name, p1.cmdline, p2.pid AS parent_pid, p2.name AS parent_name
FROM processes p1
LEFT JOIN processes p2 ON p1.parent = p2.pid;
```

### process_open_sockets

Network sockets opened by processes.

**Key columns**: pid, socket, family, protocol, local_address, local_port, remote_address, remote_port, state

```sql
-- Active external connections
SELECT p.name, ps.remote_address, ps.remote_port, ps.state, p.cmdline
FROM processes p
JOIN process_open_sockets ps ON p.pid = ps.pid
WHERE ps.remote_address NOT IN ('127.0.0.1', '::1', '0.0.0.0');
```

### process_memory_map

Memory regions mapped by processes (useful for detecting injections).

**Key columns**: pid, start, end, permissions, path, pseudo

```sql
-- Detect suspicious memory mappings
SELECT p.name, pm.path, pm.permissions, p.cmdline
FROM process_memory_map pm
JOIN processes p ON pm.pid = p.pid
WHERE pm.path LIKE '%tmp%' OR pm.pseudo = 1;
```

### process_envs

Environment variables for running processes.

**Key columns**: pid, key, value

```sql
-- Check for suspicious environment variables
SELECT p.name, pe.key, pe.value
FROM process_envs pe
JOIN processes p ON pe.pid = p.pid
WHERE pe.key IN ('LD_PRELOAD', 'DYLD_INSERT_LIBRARIES', 'PATH');
```

## Network Tables

### listening_ports

Ports listening for connections.

**Key columns**: pid, port, protocol, family, address

```sql
-- Listening ports mapped to processes
SELECT lp.port, lp.protocol, lp.address, p.name, p.path, p.cmdline
FROM listening_ports lp
LEFT JOIN processes p ON lp.pid = p.pid
WHERE lp.address NOT IN ('127.0.0.1', '::1')
ORDER BY lp.port;
```

### interface_addresses

Network interface IP addresses.

**Key columns**: interface, address, mask, broadcast

```sql
-- List all network interfaces and addresses
SELECT interface, address, mask, type FROM interface_addresses;
```

### routes

System routing table.

**Key columns**: destination, netmask, gateway, source, interface, type

```sql
-- Check routing table
SELECT destination, netmask, gateway, interface FROM routes;
```

### arp_cache

ARP table entries (detect ARP spoofing).

**Key columns**: address, mac, interface, permanent

```sql
-- ARP cache analysis
SELECT address, mac, interface FROM arp_cache ORDER BY address;
```

## File System Tables

### file

Query file system metadata.

**Key columns**: path, directory, filename, size, mtime, atime, ctime, mode, uid, gid, type

```sql
-- Recently modified files in sensitive directories
SELECT path, filename, mtime, uid, gid, mode
FROM file
WHERE path LIKE '/etc/%'
   OR path LIKE '/usr/bin/%'
   OR path LIKE '/usr/sbin/%'
ORDER BY mtime DESC LIMIT 50;

-- SUID/SGID binaries
SELECT path, filename, mode, uid
FROM file
WHERE (mode LIKE '%4%' OR mode LIKE '%2%')
  AND path LIKE '/usr/%';
```

### hash

File cryptographic hashes (MD5, SHA1, SHA256).

**Key columns**: path, directory, filename, md5, sha1, sha256, size

```sql
-- Hash files in suspicious locations
SELECT path, filename, md5, sha256
FROM hash
WHERE path LIKE '/tmp/%'
   OR path LIKE '/var/tmp/%';
```

### file_events

Real-time file system change monitoring (requires file integrity monitoring).

**Key columns**: target_path, action, time, pid, uid, gid

```sql
-- Recent file modifications
SELECT target_path, action, time, pid
FROM file_events
WHERE action IN ('CREATED', 'UPDATED', 'DELETED')
  AND time > strftime('%s', 'now') - 3600;
```

## User and Authentication Tables

### users

System user accounts.

**Key columns**: uid, gid, username, description, directory, shell

```sql
-- Users with login shells
SELECT username, uid, gid, shell, directory
FROM users
WHERE shell NOT LIKE '%nologin%' AND shell NOT LIKE '%false';

-- Recent user additions (requires tracking)
SELECT * FROM users ORDER BY uid DESC LIMIT 10;
```

### logged_in_users

Currently logged-in users.

**Key columns**: user, tty, host, time, pid

```sql
-- Active user sessions
SELECT user, tty, host, time FROM logged_in_users;
```

### last

Login history (last command output).

**Key columns**: username, tty, pid, type, time, host

```sql
-- Recent login history
SELECT username, tty, host, time, type
FROM last
ORDER BY time DESC LIMIT 50;
```

### groups

User groups.

**Key columns**: gid, groupname

```sql
-- List all groups
SELECT gid, groupname FROM groups;
```

### user_groups

User-to-group mappings.

**Key columns**: uid, gid

```sql
-- Users in admin groups
SELECT u.username, g.groupname
FROM users u
JOIN user_groups ug ON u.uid = ug.uid
JOIN groups g ON ug.gid = g.gid
WHERE g.groupname IN ('sudo', 'wheel', 'admin', 'root');
```

## System Information Tables

### system_info

System hardware and OS information.

**Key columns**: hostname, uuid, cpu_type, cpu_brand, physical_memory, hardware_model

```sql
-- System information
SELECT hostname, cpu_brand, physical_memory, hardware_model FROM system_info;
```

### os_version

Operating system version details.

**Key columns**: name, version, major, minor, patch, build, platform

```sql
-- OS version
SELECT name, version, platform, build FROM os_version;
```

### kernel_info

Kernel version and parameters.

**Key columns**: version, arguments, path, device

```sql
-- Kernel information
SELECT version, arguments FROM kernel_info;
```

### uptime

System uptime.

**Key columns**: days, hours, minutes, seconds, total_seconds

```sql
-- System uptime
SELECT days, hours, minutes FROM uptime;
```

## Persistence Mechanism Tables

### crontab

Scheduled cron jobs (Linux/macOS).

**Key columns**: event, minute, hour, day_of_month, month, day_of_week, command, path

```sql
-- All cron jobs
SELECT event, command, path FROM crontab;

-- Suspicious cron commands
SELECT * FROM crontab
WHERE command LIKE '%curl%'
   OR command LIKE '%wget%'
   OR command LIKE '%/tmp/%'
   OR command LIKE '%base64%';
```

### scheduled_tasks (Windows)

Windows scheduled tasks.

**Key columns**: name, action, path, enabled, state

```sql
-- Enabled scheduled tasks
SELECT name, action, path, state FROM scheduled_tasks WHERE enabled = 1;
```

### startup_items (macOS)

macOS startup items.

**Key columns**: name, path, args, type, source, status

```sql
-- macOS startup items
SELECT name, path, type, source FROM startup_items;
```

### launchd (macOS)

macOS launch agents and daemons.

**Key columns**: name, path, program, program_arguments, run_at_load, keep_alive

```sql
-- Launch agents/daemons that run at load
SELECT name, path, program, program_arguments
FROM launchd
WHERE run_at_load = 1;
```

### registry (Windows)

Windows registry access.

**Key columns**: key, name, type, data, path

```sql
-- Registry Run keys
SELECT key, name, path, data
FROM registry
WHERE key LIKE '%Run%' OR key LIKE '%RunOnce%';
```

### services (Windows)

Windows services.

**Key columns**: name, display_name, status, path, start_type, user_account

```sql
-- Auto-start services
SELECT name, display_name, path, user_account
FROM services
WHERE start_type = 'AUTO_START';
```

### systemd_units (Linux)

Linux systemd services.

**Key columns**: id, description, load_state, active_state, sub_state, fragment_path

```sql
-- Active systemd services
SELECT id, description, active_state, fragment_path
FROM systemd_units
WHERE active_state = 'active';

-- Non-default systemd services
SELECT * FROM systemd_units
WHERE fragment_path NOT LIKE '/usr/lib/systemd/system/%'
  AND fragment_path NOT LIKE '/lib/systemd/system/%';
```

## Platform-Specific Tables

### kernel_modules (Linux)

Loaded kernel modules.

**Key columns**: name, size, used_by, status, address

```sql
-- Loaded kernel modules
SELECT name, size, used_by, status FROM kernel_modules;
```

### kernel_extensions (macOS)

macOS kernel extensions (kexts).

**Key columns**: name, version, path, loaded

```sql
-- Loaded kernel extensions
SELECT name, version, path FROM kernel_extensions WHERE loaded = 1;
```

### drivers (Windows)

Windows device drivers.

**Key columns**: device_id, device_name, image, provider, service, service_key

```sql
-- Loaded drivers
SELECT device_name, image, provider, service FROM drivers;
```

### chrome_extensions

Chrome browser extensions.

**Key columns**: name, identifier, version, description, path, author

```sql
-- Installed Chrome extensions
SELECT name, version, description, path FROM chrome_extensions;
```

### firefox_addons

Firefox browser add-ons.

**Key columns**: name, identifier, version, description, source_url, visible

```sql
-- Installed Firefox add-ons
SELECT name, version, description, source_url FROM firefox_addons;
```

## Query Optimization Tips

1. **Use WHERE clauses**: Always filter results to reduce query time
   ```sql
   -- Bad: SELECT * FROM processes;
   -- Good: SELECT * FROM processes WHERE uid = 0;
   ```

2. **Limit results**: Use LIMIT for large result sets
   ```sql
   SELECT * FROM file WHERE path LIKE '/usr/%' LIMIT 100;
   ```

3. **Index columns**: Use indexed columns in WHERE clauses (pid, uid, path)

4. **Join efficiently**: Start with smaller tables when joining
   ```sql
   SELECT * FROM listening_ports lp
   JOIN processes p ON lp.pid = p.pid;  -- listening_ports is usually smaller
   ```

5. **Time filtering**: Use time comparisons for event tables
   ```sql
   WHERE time > (strftime('%s', 'now') - 3600)  -- Last hour
   ```

## Reference

- [osquery Schema Documentation](https://osquery.io/schema/)
- [Table schemas by version](https://osquery.io/schema/)
