# Platform-Specific osquery Tables and Queries

Guide to platform-specific tables and query variations across Linux, macOS, and Windows.

## Table of Contents

- [Cross-Platform Tables](#cross-platform-tables)
- [Linux-Specific Tables](#linux-specific-tables)
- [macOS-Specific Tables](#macos-specific-tables)
- [Windows-Specific Tables](#windows-specific-tables)
- [Query Translation Examples](#query-translation-examples)

## Cross-Platform Tables

These tables work across all platforms with consistent schemas:

- `processes` - Running processes
- `users` - User accounts
- `groups` - User groups
- `file` - File system metadata
- `hash` - File hashing
- `system_info` - System information
- `os_version` - OS version details
- `interface_addresses` - Network interfaces
- `routes` - Routing table
- `listening_ports` - Listening network ports

## Linux-Specific Tables

### Process and System

| Table | Description |
|-------|-------------|
| `kernel_modules` | Loaded kernel modules |
| `kernel_info` | Kernel version and boot parameters |
| `memory_info` | System memory information |
| `process_namespaces` | Linux namespace information |
| `seccomp_events` | Seccomp filter events |
| `selinux_events` | SELinux audit events |
| `apparmor_events` | AppArmor audit events |

### Package Management

| Table | Description |
|-------|-------------|
| `deb_packages` | Debian/Ubuntu packages (dpkg) |
| `rpm_packages` | RPM packages (yum/dnf) |
| `portage_packages` | Gentoo Portage packages |
| `pacman_packages` | Arch Linux packages |

### Persistence

| Table | Description |
|-------|-------------|
| `crontab` | Cron scheduled jobs |
| `systemd_units` | Systemd services and units |

### Example Linux Queries

```sql
-- Check kernel modules
SELECT name, size, used_by, status FROM kernel_modules;

-- Active systemd services
SELECT id, description, active_state, fragment_path
FROM systemd_units
WHERE active_state = 'active';

-- Recently installed packages (Debian/Ubuntu)
SELECT name, version, install_time
FROM deb_packages
ORDER BY install_time DESC LIMIT 20;

-- SELinux denials
SELECT * FROM selinux_events WHERE denied = 1;
```

## macOS-Specific Tables

### System and Kernel

| Table | Description |
|-------|-------------|
| `kernel_extensions` | Loaded kernel extensions (kexts) |
| `system_extensions` | macOS system extensions |
| `signature` | Code signature verification |
| `quarantine` | Quarantine database entries |

### Persistence

| Table | Description |
|-------|-------------|
| `launchd` | Launch agents and daemons |
| `startup_items` | Startup items |
| `periodic_items` | Periodic script executions |

### Applications

| Table | Description |
|-------|-------------|
| `apps` | Installed macOS applications |
| `safari_extensions` | Safari browser extensions |
| `authorization_mechanisms` | Authorization plugin mechanisms |

### Security

| Table | Description |
|-------|-------------|
| `extended_attributes` | File extended attributes (xattr) |
| `keychain_items` | macOS Keychain items |
| `firewall` | macOS firewall settings |

### Example macOS Queries

```sql
-- Launch agents that run at load
SELECT name, path, program, program_arguments, run_at_load
FROM launchd
WHERE run_at_load = 1
  AND path NOT LIKE '/System/%';

-- Loaded kernel extensions
SELECT name, version, path, linked_against
FROM kernel_extensions
WHERE loaded = 1;

-- Quarantined files
SELECT path, description, data_url
FROM quarantine
WHERE path LIKE '/Users/%/Downloads/%';

-- Unsigned executables in Applications
SELECT path, signed FROM signature
WHERE path LIKE '/Applications/%' AND signed = 0;

-- Code signing status
SELECT path, authority, signed, identifier
FROM signature
WHERE path = '/Applications/Suspicious.app/Contents/MacOS/Suspicious';
```

## Windows-Specific Tables

### System and Registry

| Table | Description |
|-------|-------------|
| `registry` | Windows registry access |
| `drivers` | Device drivers |
| `services` | Windows services |
| `wmi_cli_event_consumers` | WMI event consumers |
| `wmi_filter_consumer_binding` | WMI filter bindings |

### Persistence

| Table | Description |
|-------|-------------|
| `scheduled_tasks` | Windows scheduled tasks |
| `autoexec` | Auto-execution entries |
| `startup_items` | Startup folder items |

### Security

| Table | Description |
|-------|-------------|
| `windows_eventlog` | Windows Event Log |
| `authenticode` | Authenticode signature verification |
| `windows_security_products` | Installed security products |
| `bitlocker_info` | BitLocker encryption status |

### Processes

| Table | Description |
|-------|-------------|
| `process_memory_map` | Process memory mappings |
| `process_handles` | Open process handles |

### Example Windows Queries

```sql
-- Registry Run keys
SELECT key, name, path, data, mtime
FROM registry
WHERE (key LIKE '%\\Run' OR key LIKE '%\\RunOnce')
  AND key NOT LIKE '%\\RunOnceEx';

-- Scheduled tasks
SELECT name, action, path, enabled, last_run_time, next_run_time
FROM scheduled_tasks
WHERE enabled = 1
ORDER BY next_run_time;

-- WMI persistence
SELECT name, command_line_template, executable_path
FROM wmi_cli_event_consumers;

-- Windows services
SELECT name, display_name, status, path, start_type, user_account
FROM services
WHERE start_type IN ('AUTO_START', 'DEMAND_START')
ORDER BY status;

-- Event log security events
SELECT datetime, eventid, source, data
FROM windows_eventlog
WHERE channel = 'Security'
  AND eventid IN (4624, 4625, 4648, 4672)
ORDER BY datetime DESC LIMIT 100;

-- Authenticode signature verification
SELECT path, result, subject_name, issuer_name
FROM authenticode
WHERE path LIKE 'C:\Users\%'
  AND result != 'trusted';
```

## Query Translation Examples

### Persistence Mechanisms

**Linux:**
```sql
-- Cron jobs
SELECT * FROM crontab;

-- Systemd services
SELECT name, fragment_path, active_state
FROM systemd_units
WHERE active_state = 'active';
```

**macOS:**
```sql
-- Launch agents/daemons
SELECT name, path, program, run_at_load
FROM launchd
WHERE run_at_load = 1;

-- Startup items
SELECT name, path, type, source
FROM startup_items;
```

**Windows:**
```sql
-- Registry Run keys
SELECT key, name, path
FROM registry
WHERE key LIKE '%Run%';

-- Scheduled tasks
SELECT name, action, enabled
FROM scheduled_tasks
WHERE enabled = 1;
```

### Package/Application Inventory

**Linux (Debian/Ubuntu):**
```sql
SELECT name, version, install_time
FROM deb_packages
ORDER BY install_time DESC;
```

**Linux (RHEL/CentOS):**
```sql
SELECT name, version, install_time
FROM rpm_packages
ORDER BY install_time DESC;
```

**macOS:**
```sql
SELECT name, path, bundle_version, last_opened_time
FROM apps
ORDER BY last_opened_time DESC;
```

**Windows:**
```sql
SELECT name, version, install_location, install_date
FROM programs
ORDER BY install_date DESC;
```

### Network Connections

**All Platforms:**
```sql
-- Active connections
SELECT p.name, p.cmdline, ps.remote_address, ps.remote_port, ps.state
FROM processes p
JOIN process_open_sockets ps ON p.pid = ps.pid
WHERE ps.state = 'ESTABLISHED';
```

**Platform-specific filtering:**
```sql
-- Linux: Filter by network namespace
SELECT * FROM process_open_sockets
WHERE pid IN (SELECT pid FROM processes WHERE root != '/');

-- macOS: Include code signature
SELECT p.name, ps.remote_address, s.authority
FROM processes p
JOIN process_open_sockets ps ON p.pid = ps.pid
LEFT JOIN signature s ON p.path = s.path;

-- Windows: Include service name
SELECT p.name, s.name AS service_name, ps.remote_address
FROM processes p
JOIN process_open_sockets ps ON p.pid = ps.pid
LEFT JOIN services s ON p.path = s.path;
```

## Platform Detection in Queries

Use `os_version` table to detect platform:

```sql
-- Get current platform
SELECT platform, name, version FROM os_version;

-- Platform-specific queries
SELECT CASE
  WHEN platform = 'darwin' THEN (SELECT COUNT(*) FROM launchd)
  WHEN platform LIKE '%linux%' THEN (SELECT COUNT(*) FROM systemd_units)
  WHEN platform LIKE '%windows%' THEN (SELECT COUNT(*) FROM services)
  ELSE 0
END AS persistence_count
FROM os_version;
```

## Best Practices for Cross-Platform Queries

1. **Check table availability** before querying:
   ```bash
   osqueryi ".tables" | grep <table_name>
   ```

2. **Use platform detection** for conditional logic

3. **Test queries on each platform** - column names may vary slightly

4. **Document platform requirements** in query comments

5. **Create platform-specific query packs** for osqueryd

## Reference

- [osquery Schema Documentation](https://osquery.io/schema/)
- [Platform-specific table reference](https://osquery.io/schema/)
