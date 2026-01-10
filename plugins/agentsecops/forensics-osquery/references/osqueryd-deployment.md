# osqueryd Deployment Guide

Deploy osqueryd for continuous endpoint monitoring, detection, and forensic evidence collection at scale.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Configuration](#configuration)
- [Query Packs](#query-packs)
- [Log Management](#log-management)
- [Fleet Management](#fleet-management)
- [Performance Tuning](#performance-tuning)

## Overview

osqueryd is the daemon component of osquery that enables:
- Scheduled query execution across endpoint fleet
- Real-time event monitoring with event tables
- Centralized log collection and aggregation
- Detection-as-code with versioned query packs

## Installation

### Linux (Ubuntu/Debian)

```bash
# Add osquery repository
export OSQUERY_KEY=1484120AC4E9F8A1A577AEEE97A80C63C9D8B80B
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys $OSQUERY_KEY

# Add repository
sudo add-apt-repository 'deb [arch=amd64] https://pkg.osquery.io/deb deb main'

# Install
sudo apt update
sudo apt install osquery
```

### Linux (RHEL/CentOS)

```bash
# Add osquery repository
curl -L https://pkg.osquery.io/rpm/GPG | sudo tee /etc/pki/rpm-gpg/RPM-GPG-KEY-osquery

# Add repository
sudo yum-config-manager --add-repo https://pkg.osquery.io/rpm/osquery-s3-rpm.repo

# Install
sudo yum install osquery
```

### macOS

```bash
# Using Homebrew
brew install osquery

# Or download official PKG installer
# https://pkg.osquery.io/darwin/osquery-<version>.pkg
```

### Windows

```powershell
# Download MSI installer
# https://pkg.osquery.io/windows/osquery-<version>.msi

# Install via PowerShell
msiexec /i osquery-<version>.msi /quiet
```

## Configuration

### Configuration File Location

- Linux: `/etc/osquery/osquery.conf`
- macOS: `/var/osquery/osquery.conf`
- Windows: `C:\Program Files\osquery\osquery.conf`

### Basic Configuration

```json
{
  "options": {
    "config_plugin": "filesystem",
    "logger_plugin": "filesystem",
    "logger_path": "/var/log/osquery",
    "disable_logging": false,
    "log_result_events": true,
    "schedule_splay_percent": 10,
    "pidfile": "/var/osquery/osquery.pidfile",
    "events_expiry": 3600,
    "database_path": "/var/osquery/osquery.db",
    "verbose": false,
    "worker_threads": 2,
    "enable_monitor": true,
    "disable_events": false,
    "disable_audit": false,
    "audit_allow_config": true,
    "audit_allow_sockets": true,
    "host_identifier": "hostname",
    "enable_syslog": false,
    "syslog_pipe_path": "/var/osquery/syslog_pipe"
  },

  "schedule": {
    "system_info": {
      "query": "SELECT * FROM system_info;",
      "interval": 3600,
      "description": "Collect system information hourly"
    },
    "running_processes": {
      "query": "SELECT pid, name, path, cmdline, uid FROM processes;",
      "interval": 300,
      "description": "Monitor running processes every 5 minutes"
    },
    "network_connections": {
      "query": "SELECT p.name, p.cmdline, ps.remote_address, ps.remote_port FROM processes p JOIN process_open_sockets ps ON p.pid = ps.pid WHERE ps.remote_address NOT IN ('127.0.0.1', '::1');",
      "interval": 600,
      "description": "Monitor network connections every 10 minutes"
    }
  },

  "packs": {
    "incident-response": "/etc/osquery/packs/ir-triage.conf",
    "ossec-rootkit": "/usr/share/osquery/packs/ossec-rootkit.conf"
  }
}
```

### Security-Focused Configuration

```json
{
  "options": {
    "config_plugin": "filesystem",
    "logger_plugin": "filesystem",
    "logger_path": "/var/log/osquery",
    "disable_logging": false,
    "log_result_events": true,
    "schedule_splay_percent": 10,
    "worker_threads": 4,
    "enable_monitor": true,
    "watchdog_level": 1,
    "watchdog_memory_limit": 250,
    "watchdog_utilization_limit": 20
  },

  "schedule": {
    "suspicious_processes": {
      "query": "SELECT * FROM processes WHERE on_disk = 0 OR path LIKE '%tmp%' OR path LIKE '%Temp%';",
      "interval": 300,
      "description": "Detect suspicious processes"
    },
    "unauthorized_suid": {
      "query": "SELECT path, mode, uid FROM file WHERE (mode LIKE '%4%' OR mode LIKE '%2%') AND path NOT IN (SELECT path FROM file WHERE path LIKE '/usr/%' OR path LIKE '/bin/%');",
      "interval": 3600,
      "description": "Find unauthorized SUID binaries",
      "platform": "posix"
    },
    "registry_run_keys": {
      "query": "SELECT key, name, path FROM registry WHERE key LIKE '%Run%' OR key LIKE '%RunOnce%';",
      "interval": 3600,
      "description": "Monitor registry persistence",
      "platform": "windows"
    }
  }
}
```

## Query Packs

### Creating Query Packs

Query packs organize related queries for specific security scenarios.

**Example: `/etc/osquery/packs/ir-triage.conf`**

```json
{
  "platform": "all",
  "version": "1.0.0",
  "queries": {
    "logged_in_users": {
      "query": "SELECT * FROM logged_in_users;",
      "interval": 600,
      "description": "Track logged-in users"
    },
    "listening_ports": {
      "query": "SELECT lp.port, lp.address, p.name, p.path FROM listening_ports lp LEFT JOIN processes p ON lp.pid = p.pid WHERE lp.address NOT IN ('127.0.0.1', '::1');",
      "interval": 300,
      "description": "Monitor listening network ports"
    },
    "kernel_modules": {
      "query": "SELECT name, used_by, status FROM kernel_modules;",
      "interval": 3600,
      "description": "Monitor loaded kernel modules",
      "platform": "linux"
    },
    "scheduled_tasks": {
      "query": "SELECT name, action, path, enabled FROM scheduled_tasks WHERE enabled = 1;",
      "interval": 3600,
      "description": "Monitor Windows scheduled tasks",
      "platform": "windows"
    },
    "launchd_services": {
      "query": "SELECT name, path, program, run_at_load FROM launchd WHERE run_at_load = 1;",
      "interval": 3600,
      "description": "Monitor macOS launch services",
      "platform": "darwin"
    }
  }
}
```

### Platform-Specific Packs

Use `"platform"` field to limit queries:
- `"posix"` - Linux and macOS
- `"linux"` - Linux only
- `"darwin"` - macOS only
- `"windows"` - Windows only
- `"all"` - All platforms

## Log Management

### Log Types

osqueryd generates several log types:

1. **Result logs**: Query results from scheduled queries
2. **Status logs**: osqueryd operational status and errors
3. **Snapshot logs**: Full result sets (vs differential)

### Log Formats

**JSON (recommended):**
```json
{
  "name": "suspicious_processes",
  "hostIdentifier": "web-server-01",
  "calendarTime": "Mon Oct 02 12:34:56 2023 UTC",
  "unixTime": 1696251296,
  "epoch": 0,
  "counter": 1,
  "columns": {
    "pid": "1234",
    "name": "suspicious",
    "path": "/tmp/suspicious"
  },
  "action": "added"
}
```

### Centralized Logging

#### Option 1: Syslog

```json
{
  "options": {
    "logger_plugin": "syslog",
    "syslog_pipe_path": "/var/osquery/syslog_pipe"
  }
}
```

#### Option 2: AWS Kinesis/Firehose

```json
{
  "options": {
    "logger_plugin": "aws_kinesis",
    "aws_kinesis_stream": "osquery-results",
    "aws_region": "us-east-1"
  }
}
```

#### Option 3: TLS Endpoint

```json
{
  "options": {
    "logger_plugin": "tls",
    "logger_tls_endpoint": "/log",
    "logger_tls_period": 60
  }
}
```

#### Option 4: Kafka

```json
{
  "options": {
    "logger_plugin": "kafka_producer",
    "kafka_topic": "osquery-logs",
    "kafka_brokers": "broker1:9092,broker2:9092"
  }
}
```

## Fleet Management

### Fleet Manager Options

1. **osquery Fleet Manager** - Official fleet management tool
2. **Kolide Fleet** - Open-source fleet management (now FleetDM)
3. **Doorman** - Minimal fleet manager
4. **Zentral** - macOS-focused fleet management

### FleetDM Configuration

```yaml
# fleet-config.yml
mysql:
  address: 127.0.0.1:3306
  database: fleet
  username: fleet
  password: fleet_password

redis:
  address: 127.0.0.1:6379

server:
  address: 0.0.0.0:8080
  tls: true
  cert: /path/to/cert.pem
  key: /path/to/key.pem

logging:
  json: true
  debug: false
```

### Enrolling Endpoints

#### TLS Enrollment

```json
{
  "options": {
    "enroll_secret_path": "/etc/osquery/enroll_secret.txt",
    "tls_server_certs": "/etc/osquery/certs/server.pem",
    "tls_hostname": "fleet.example.com",
    "host_identifier": "uuid",
    "enroll_tls_endpoint": "/api/v1/osquery/enroll",
    "config_plugin": "tls",
    "config_tls_endpoint": "/api/v1/osquery/config",
    "config_refresh": 60,
    "logger_plugin": "tls",
    "logger_tls_endpoint": "/api/v1/osquery/log",
    "logger_tls_period": 10,
    "distributed_plugin": "tls",
    "distributed_interval": 60,
    "distributed_tls_read_endpoint": "/api/v1/osquery/distributed/read",
    "distributed_tls_write_endpoint": "/api/v1/osquery/distributed/write"
  }
}
```

## Performance Tuning

### Resource Limits

```json
{
  "options": {
    "watchdog_level": 1,
    "watchdog_memory_limit": 250,
    "watchdog_utilization_limit": 20,
    "worker_threads": 4,
    "schedule_timeout": 60,
    "schedule_max_drift": 60
  }
}
```

### Query Optimization

1. **Use appropriate intervals**: Balance freshness vs performance
   - Critical queries: 60-300 seconds
   - Standard monitoring: 300-900 seconds
   - Inventory queries: 3600+ seconds

2. **Add WHERE clauses**: Reduce result set size
   ```sql
   -- Bad: SELECT * FROM file;
   -- Good: SELECT * FROM file WHERE path LIKE '/etc/%';
   ```

3. **Limit result sets**: Use LIMIT clause
   ```sql
   SELECT * FROM processes ORDER BY start_time DESC LIMIT 100;
   ```

4. **Differential logging**: Only log changes
   ```json
   {
     "options": {
       "log_result_events": true
     }
   }
   ```

### Schedule Splay

Prevent query storms by adding jitter:

```json
{
  "options": {
    "schedule_splay_percent": 10
  }
}
```

## Service Management

### Linux (systemd)

```bash
# Start osqueryd
sudo systemctl start osqueryd

# Enable on boot
sudo systemctl enable osqueryd

# Check status
sudo systemctl status osqueryd

# View logs
sudo journalctl -u osqueryd -f
```

### macOS (launchd)

```bash
# Start osqueryd
sudo launchctl load /Library/LaunchDaemons/com.facebook.osqueryd.plist

# Stop osqueryd
sudo launchctl unload /Library/LaunchDaemons/com.facebook.osqueryd.plist

# Check status
sudo launchctl list | grep osquery
```

### Windows (Service)

```powershell
# Start service
Start-Service osqueryd

# Stop service
Stop-Service osqueryd

# Check status
Get-Service osqueryd

# View logs
Get-Content "C:\ProgramData\osquery\log\osqueryd.results.log" -Wait
```

## Security Best Practices

1. **Limit configuration access**: Restrict `/etc/osquery/` to root only
2. **Use TLS**: Encrypt fleet management communications
3. **Rotate secrets**: Change enrollment secrets regularly
4. **Monitor osqueryd**: Alert on service failures
5. **Version control configs**: Track configuration changes in Git
6. **Test before deploy**: Validate queries in lab first
7. **Implement RBAC**: Use fleet manager role-based access
8. **Audit queries**: Review all scheduled queries for performance impact

## Troubleshooting

### High CPU Usage

Check query performance:
```bash
# Enable verbose logging
sudo osqueryd --verbose --config_path=/etc/osquery/osquery.conf

# Check query times
tail -f /var/log/osquery/osqueryd.INFO | grep "query="
```

### Missing Results

Verify query syntax:
```bash
# Test query interactively
osqueryi "SELECT * FROM processes LIMIT 5;"

# Check for errors
tail -f /var/log/osquery/osqueryd.results.log
```

### Service Crashes

Review watchdog settings:
```json
{
  "options": {
    "watchdog_level": 0,  # Disable for debugging
    "verbose": true
  }
}
```

## Reference

- [osquery Deployment Guide](https://osquery.readthedocs.io/en/stable/deployment/)
- [FleetDM Documentation](https://fleetdm.com/docs)
- [osquery Configuration](https://osquery.readthedocs.io/en/stable/deployment/configuration/)
