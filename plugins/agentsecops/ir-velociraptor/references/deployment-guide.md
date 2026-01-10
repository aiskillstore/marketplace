# Velociraptor Enterprise Deployment Guide

Comprehensive guide for deploying Velociraptor in enterprise environments.

## Table of Contents
- [Architecture Overview](#architecture-overview)
- [Server Deployment](#server-deployment)
- [Client Deployment](#client-deployment)
- [High Availability](#high-availability)
- [Security Hardening](#security-hardening)
- [Monitoring and Maintenance](#monitoring-and-maintenance)
- [Scaling Considerations](#scaling-considerations)

## Architecture Overview

### Components

**Frontend Server**:
- Handles client communication (gRPC)
- Serves web GUI
- Manages TLS connections
- Default port: TCP 8000 (clients), TCP 8889 (GUI)

**Datastore**:
- Filesystem-based by default
- Stores artifacts, collections, and configurations
- Can use external storage (S3, GCS)

**Clients (Agents)**:
- Lightweight endpoint agents
- Execute VQL queries
- Report results to server
- Self-updating capability

### Deployment Models

**Single Server** (< 1000 endpoints):
```
[Clients] ──→ [Frontend + GUI + Datastore]
```

**Multi-Frontend** (1000-10000 endpoints):
```
                  ┌─→ [Frontend 1]
[Clients] ──→ [LB]├─→ [Frontend 2] ──→ [Shared Datastore]
                  └─→ [Frontend 3]
```

**Distributed** (> 10000 endpoints):
```
                      ┌─→ [Frontend Pool 1] ──→ [Datastore Region 1]
[Clients by region]├─→ [Frontend Pool 2] ──→ [Datastore Region 2]
                      └─→ [Frontend Pool 3] ──→ [Datastore Region 3]
```

## Server Deployment

### Prerequisites

**System Requirements**:
- OS: Linux (Ubuntu 20.04+, RHEL 8+), Windows Server 2019+
- RAM: 8GB minimum, 16GB+ recommended for large deployments
- CPU: 4 cores minimum, 8+ for production
- Storage: 100GB+ for datastore (grows with collections)
- Network: Public IP or internal with client access

**Software Requirements**:
- No external dependencies (single binary)
- Optional: MySQL/PostgreSQL for metadata (future enhancement)

### Installation Steps

#### 1. Download Velociraptor

```bash
# Linux
wget https://github.com/Velocidex/velociraptor/releases/download/v0.72/velociraptor-v0.72.3-linux-amd64

# Make executable
chmod +x velociraptor-v0.72.3-linux-amd64
sudo mv velociraptor-v0.72.3-linux-amd64 /usr/local/bin/velociraptor
```

#### 2. Generate Server Configuration

```bash
# Interactive configuration generation
velociraptor config generate -i

# Or automated with defaults
velociraptor config generate \
  --deployment linux \
  --frontend_hostname velociraptor.company.com \
  --frontend_port 8000 \
  --gui_port 8889 \
  --datastore /var/lib/velociraptor \
  > /etc/velociraptor/server.config.yaml
```

**Key Configuration Options**:

```yaml
# server.config.yaml
version:
  name: velociraptor
  version: "0.72"

Client:
  server_urls:
    - https://velociraptor.company.com:8000/
  ca_certificate: |
    -----BEGIN CERTIFICATE-----
    [CA cert]
    -----END CERTIFICATE-----

API:
  bind_address: 0.0.0.0
  bind_port: 8001
  bind_scheme: tcp

GUI:
  bind_address: 0.0.0.0
  bind_port: 8889
  use_plain_http: false
  internal_cidr:
    - 10.0.0.0/8
    - 172.16.0.0/12
    - 192.168.0.0/16

Frontend:
  hostname: velociraptor.company.com
  bind_address: 0.0.0.0
  bind_port: 8000

Datastore:
  implementation: FileBaseDataStore
  location: /var/lib/velociraptor
  filestore_directory: /var/lib/velociraptor
```

#### 3. Setup Systemd Service (Linux)

```bash
# Create service file
sudo cat > /etc/systemd/system/velociraptor.service <<'EOF'
[Unit]
Description=Velociraptor DFIR Agent
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/velociraptor --config /etc/velociraptor/server.config.yaml frontend -v
Restart=on-failure
RestartSec=10
User=velociraptor
Group=velociraptor
StandardOutput=journal
StandardError=journal
SyslogIdentifier=velociraptor

# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=full
ProtectHome=true
ReadWritePaths=/var/lib/velociraptor

[Install]
WantedBy=multi-user.target
EOF

# Create user
sudo useradd -r -s /bin/false velociraptor

# Setup directories
sudo mkdir -p /etc/velociraptor /var/lib/velociraptor
sudo chown -R velociraptor:velociraptor /etc/velociraptor /var/lib/velociraptor

# Start service
sudo systemctl daemon-reload
sudo systemctl enable velociraptor
sudo systemctl start velociraptor
```

#### 4. Create Initial Admin User

```bash
# Create admin user
velociraptor --config /etc/velociraptor/server.config.yaml \
  user add admin --role administrator

# Verify
velociraptor --config /etc/velociraptor/server.config.yaml \
  user show admin
```

#### 5. Access Web Interface

```bash
# Access GUI at: https://velociraptor.company.com:8889/
# Login with admin credentials created above
```

### TLS Certificate Configuration

**Option 1: Self-Signed (Testing)**:
```bash
# Already generated during config creation
# Certificates in server.config.yaml
```

**Option 2: Let's Encrypt**:
```bash
# Install certbot
sudo apt install certbot

# Generate certificate
sudo certbot certonly --standalone \
  -d velociraptor.company.com \
  --non-interactive --agree-tos \
  -m admin@company.com

# Update server.config.yaml with Let's Encrypt certs
```

**Option 3: Corporate CA**:
```yaml
# Update server.config.yaml
Frontend:
  certificate: /path/to/server-cert.pem
  private_key: /path/to/server-key.pem

GUI:
  use_plain_http: false
  certificate: /path/to/gui-cert.pem
  private_key: /path/to/gui-key.pem
```

## Client Deployment

### Generate Client Configuration

```bash
# Generate client config from server config
velociraptor --config /etc/velociraptor/server.config.yaml \
  config client > /tmp/client.config.yaml
```

### Deployment Methods

#### Method 1: MSI Installer (Windows)

```bash
# Generate MSI installer
velociraptor --config /etc/velociraptor/server.config.yaml \
  config msi --binary velociraptor.exe \
  --output VelociraptorClient.msi

# Deploy via GPO, SCCM, or Intune
# Silent install: msiexec /i VelociraptorClient.msi /quiet
```

#### Method 2: DEB/RPM Package (Linux)

```bash
# Generate DEB package
velociraptor --config /etc/velociraptor/server.config.yaml \
  debian client --binary velociraptor-linux-amd64 \
  --output velociraptor-client.deb

# Deploy via Ansible, Puppet, or package manager
# Install: sudo dpkg -i velociraptor-client.deb
```

#### Method 3: Manual Installation

**Windows**:
```powershell
# Copy binary and config
Copy-Item velociraptor.exe C:\Program Files\Velociraptor\
Copy-Item client.config.yaml C:\Program Files\Velociraptor\

# Install as service
& "C:\Program Files\Velociraptor\velociraptor.exe" `
  --config "C:\Program Files\Velociraptor\client.config.yaml" `
  service install

# Start service
Start-Service Velociraptor
```

**Linux**:
```bash
# Copy binary and config
sudo cp velociraptor /usr/local/bin/
sudo cp client.config.yaml /etc/velociraptor/

# Create systemd service
sudo cat > /etc/systemd/system/velociraptor-client.service <<'EOF'
[Unit]
Description=Velociraptor DFIR Client
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/velociraptor --config /etc/velociraptor/client.config.yaml client -v
Restart=on-failure
User=root

[Install]
WantedBy=multi-user.target
EOF

# Start service
sudo systemctl enable velociraptor-client
sudo systemctl start velociraptor-client
```

### Client Configuration Options

```yaml
# client.config.yaml
Client:
  server_urls:
    - https://velociraptor.company.com:8000/

  # Connection tuning
  max_poll: 60        # Max seconds between polls
  max_poll_std: 10    # Jitter to prevent thundering herd

  # Performance
  max_upload_size: 104857600  # 100MB
  cpu_limit: 80                # CPU usage percentage limit
  progress_timeout: 3600       # Query timeout

  # Writeback file (client state)
  writeback_linux: /etc/velociraptor/writeback.yaml
  writeback_windows: C:\Program Files\Velociraptor\writeback.yaml
```

## High Availability

### Load Balancer Configuration

**HAProxy Example**:
```conf
# /etc/haproxy/haproxy.cfg
frontend velociraptor_frontend
    bind *:8000 ssl crt /etc/ssl/certs/velociraptor.pem
    mode tcp
    default_backend velociraptor_servers

backend velociraptor_servers
    mode tcp
    balance leastconn
    option tcp-check
    server velo1 10.0.1.10:8000 check
    server velo2 10.0.1.11:8000 check
    server velo3 10.0.1.12:8000 check

frontend velociraptor_gui
    bind *:8889 ssl crt /etc/ssl/certs/velociraptor.pem
    mode http
    default_backend velociraptor_gui_servers

backend velociraptor_gui_servers
    mode http
    balance roundrobin
    option httpchk GET /
    server velo1 10.0.1.10:8889 check
    server velo2 10.0.1.11:8889 check
    server velo3 10.0.1.12:8889 check
```

### Shared Datastore

**NFS Configuration**:
```bash
# On NFS server
sudo apt install nfs-kernel-server
sudo mkdir -p /export/velociraptor
sudo chown nobody:nogroup /export/velociraptor

# /etc/exports
/export/velociraptor 10.0.1.0/24(rw,sync,no_subtree_check,no_root_squash)

# On Velociraptor servers
sudo mount -t nfs nfs-server:/export/velociraptor /var/lib/velociraptor
```

**S3 Datastore (Future)**:
```yaml
# server.config.yaml
Datastore:
  implementation: S3DataStore
  s3_bucket: velociraptor-datastore
  s3_region: us-east-1
  credentials_file: /etc/velociraptor/aws-credentials
```

## Security Hardening

### Network Security

**Firewall Rules** (iptables):
```bash
# Allow client connections
sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT

# Allow GUI access from management network only
sudo iptables -A INPUT -p tcp --dport 8889 -s 10.0.0.0/8 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8889 -j DROP

# Save rules
sudo iptables-save > /etc/iptables/rules.v4
```

**TLS Configuration**:
```yaml
# Enforce TLS 1.2+
Frontend:
  min_tls_version: "1.2"

GUI:
  min_tls_version: "1.2"
```

### Access Control

**Role-Based Access**:
```bash
# Create read-only analyst role
velociraptor --config server.config.yaml \
  acl grant analyst --role reader

# Create hunt operator role
velociraptor --config server.config.yaml \
  acl grant hunter --role analyst

# Create admin role
velociraptor --config server.config.yaml \
  acl grant admin --role administrator
```

**Permissions Matrix**:
| Role | View Artifacts | Run Collections | Create Hunts | Manage Users | View All Clients |
|------|---------------|-----------------|--------------|--------------|------------------|
| Reader | ✓ | ✗ | ✗ | ✗ | ✗ |
| Analyst | ✓ | ✓ | ✗ | ✗ | ✓ |
| Investigator | ✓ | ✓ | ✓ | ✗ | ✓ |
| Administrator | ✓ | ✓ | ✓ | ✓ | ✓ |

### Audit Logging

**Enable Comprehensive Logging**:
```yaml
# server.config.yaml
Logging:
  output_directory: /var/log/velociraptor
  separate_logs_per_component: true
  max_age: 365

  # Log queries
  log_queries: true

  # Log all API calls
  log_api_calls: true
```

**Audit Log Monitoring**:
```bash
# Monitor authentication events
tail -f /var/log/velociraptor/frontend.log | grep -i "auth"

# Monitor collection starts
tail -f /var/log/velociraptor/frontend.log | grep -i "collection"

# Monitor hunt creation
tail -f /var/log/velociraptor/frontend.log | grep -i "hunt"
```

## Monitoring and Maintenance

### Health Checks

**Server Health**:
```bash
# Check server status
systemctl status velociraptor

# Check connected clients
velociraptor --config server.config.yaml \
  query "SELECT client_id, os_info.hostname, last_seen_at FROM clients()"

# Check resource usage
velociraptor --config server.config.yaml \
  query "SELECT * FROM monitoring()"
```

**Client Health Monitoring**:
```sql
-- Find offline clients (>24 hours)
SELECT client_id,
       os_info.hostname AS Hostname,
       timestamp(epoch=last_seen_at) AS LastSeen
FROM clients()
WHERE last_seen_at < now() - 86400
ORDER BY last_seen_at
```

### Backup and Recovery

**Backup Strategy**:
```bash
#!/bin/bash
# velociraptor-backup.sh

BACKUP_DIR="/backup/velociraptor"
DATASTORE="/var/lib/velociraptor"
DATE=$(date +%Y%m%d-%H%M%S)

# Stop server (optional for consistency)
# systemctl stop velociraptor

# Backup datastore
tar -czf "$BACKUP_DIR/datastore-$DATE.tar.gz" "$DATASTORE"

# Backup configuration
cp /etc/velociraptor/server.config.yaml "$BACKUP_DIR/server.config-$DATE.yaml"

# Restart server
# systemctl start velociraptor

# Rotate old backups (keep 30 days)
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete
```

**Recovery**:
```bash
# Stop server
systemctl stop velociraptor

# Restore datastore
tar -xzf /backup/velociraptor/datastore-20240115.tar.gz -C /var/lib/

# Restore config
cp /backup/velociraptor/server.config-20240115.yaml /etc/velociraptor/server.config.yaml

# Start server
systemctl start velociraptor
```

### Maintenance Tasks

**Database Cleanup**:
```bash
# Delete old collections
velociraptor --config server.config.yaml \
  query "DELETE FROM collections WHERE timestamp < now() - 7776000"  # 90 days

# Vacuum datastore (reclaim space)
velociraptor --config server.config.yaml \
  datastore vacuum
```

**Client Updates**:
```bash
# Update clients via server
# 1. Upload new binary to server
velociraptor --config server.config.yaml \
  tools upload --file velociraptor-v0.72.4.exe --name velociraptor

# 2. Create update hunt
velociraptor --config server.config.yaml \
  query "SELECT * FROM hunt(artifact='Generic.Client.Update')"
```

## Scaling Considerations

### Performance Tuning

**Server Configuration**:
```yaml
# server.config.yaml
Frontend:
  # Increase concurrent connections
  max_connections: 10000

  # Connection timeouts
  keep_alive_timeout: 300

Datastore:
  # Filesystem tuning
  max_dir_size: 10000  # Files per directory

Resources:
  # Increase worker pools
  expected_clients: 10000
  max_poll_threads: 100
```

**System Tuning**:
```bash
# Increase file descriptors
echo "velociraptor soft nofile 65536" >> /etc/security/limits.conf
echo "velociraptor hard nofile 65536" >> /etc/security/limits.conf

# Kernel tuning
cat >> /etc/sysctl.conf <<EOF
net.core.somaxconn = 4096
net.ipv4.tcp_max_syn_backlog = 4096
net.ipv4.ip_local_port_range = 10000 65000
EOF
sysctl -p
```

### Capacity Planning

**Client-to-Server Ratio**:
- Single server: Up to 10,000 clients
- Multi-frontend: Up to 100,000 clients
- Distributed: 100,000+ clients

**Storage Requirements**:
- Base install: ~200MB
- Per-client metadata: ~100KB
- Per-collection: Varies (typically 1-50MB)
- Retention: Plan for 90-180 days of data

**Network Bandwidth**:
- Baseline: ~1KB/client/minute (polling)
- Collection: Depends on artifacts (10MB-1GB)
- Hunt: Multiply collection size by client count

**Formula**:
```
Storage = (Clients × 100KB) + (Collections/day × AvgSize × RetentionDays)
Bandwidth = (Clients × 1KB × 60 × 24) + (Hunts/day × Clients × AvgCollection)
```

### Monitoring Metrics

**Key Performance Indicators**:
- Client check-in rate (target: >99%)
- Average query execution time
- Collection success rate
- Datastore growth rate
- Server CPU/memory usage
- Network throughput

**Prometheus Metrics** (if enabled):
```yaml
# server.config.yaml
Monitoring:
  bind_address: localhost
  bind_port: 9090
```
