# Common Infrastructure Patterns

Infrastructure-specific patterns and expected behaviors for Accelerated Industries systems and typical homelab/development environments.

## Host Types and Expected Baselines

### Development Workstation (e.g., hyperion)

**Typical configuration:**
- 8-16 cores
- 16-32GB RAM
- NVMe primary storage
- Desktop environment: Hyprland, KDE Plasma, or GNOME
- GPU: NVIDIA or AMD for development/rendering

**Expected baseline:**
- Load: 10-30% of cores (1.6/16 cores for 16-core system)
- Memory: 60-80% usage (lots of caching is normal)
- Memory pressure: < 1%
- Swap usage: 0MB ideally, <500MB acceptable
- Disk I/O: Bursty, 20-100 IOPS typical

**Normal top processes:**
- Firefox/Chrome: 2-4GB RAM, 5-15% CPU during active use
- VSCode/Code: 1-2GB RAM, 10-30% CPU during builds
- Docker daemon: 500MB-1GB RAM
- Terminal multiplexers: tmux, screen
- Development tools: compilers, language servers

**Red flags:**
- Load > 70% sustained without active builds
- Memory pressure > 2% 
- Swap usage > 1GB
- GPU temperature > 85°C sustained

### .local mDNS Hosts

**Examples:** accelerated.local, hyperion.local, etc.

**Naming convention:**
- `.local` suffix indicates mDNS/Avahi resolution
- Typically on local network (192.168.x.x or 10.x.x.x)
- May be physical machines or VMs

**Access pattern:**
- GASP on port 8080 (default)
- SSH usually on port 22
- Local network only (not internet-exposed)

**Expected behavior:**
- Quick response times (<50ms on LAN)
- Consistent availability
- If unreachable, check network/mDNS resolution

### Proxmox Virtualization Hosts

**Typical configuration:**
- 8-32 cores
- 64-256GB RAM
- Multiple disks/RAID
- Multiple VMs and containers running

**Expected baseline:**
- Load: 30-60% of cores (depends on VM density)
- Memory: 70-85% (VMs consume most RAM)
- High process count (100-300+ processes)
- Many QEMU/KVM processes in top list

**Normal top processes:**
- `pve-cluster`: Proxmox cluster daemon
- `pvedaemon`: Proxmox daemon
- Multiple `qemu-system-x86_64`: VM processes
- `pve-ha-lrm`, `pve-ha-crm`: High availability daemons
- `corosync`: Cluster communication

**Proxmox-specific checks:**
- VM count vs expected
- Migration events in recent_changes
- Cluster communication (if clustered)
- Storage pool health

**Red flags:**
- Load > 90% sustained (VMs fighting for CPU)
- Memory pressure on host (VMs overcommitted)
- Failed systemd units for pve-* services
- Storage nearing capacity

### Container Hosts (Docker/LXC)

**Typical configuration:**
- Variable core count
- RAM allocation per container workload
- Often runs on Proxmox or bare metal

**Expected baseline:**
- Load: Proportional to container count and workload
- Memory: 50-80% usage
- High process count (containers contribute many processes)
- dockerd/containerd always in top processes

**Normal patterns:**
- Baseline load higher than bare metal
- Many processes with short uptimes (container churn)
- Network activity elevated (container networking)
- Disk I/O elevated (container layers, logs)

**Container-specific checks:**
- Container resource limits vs usage
- Container restart patterns
- Volume mount performance
- Network bridge overhead

**Red flags:**
- Single container using >50% host resources
- Continuous container restarts
- Docker daemon high CPU (>10% sustained)
- Out of disk space (container logs, images)

## Application-Specific Patterns

### Web Browsers (Firefox, Chrome)

**Expected behavior:**
- High memory usage: 2-6GB normal with many tabs
- Bursty CPU: 10-50% during page loads
- GPU usage: For video playback, WebGL
- Multiple processes (sandboxing)

**When concerning:**
- Memory > 8GB (possible tab leak)
- CPU > 50% when idle
- Continuous high GPU usage when idle

### IDE/Editors (VSCode, JetBrains)

**Expected behavior:**
- Memory: 1-3GB for VSCode, 2-4GB for JetBrains
- CPU: 10-50% during indexing/building
- Disk I/O: High during indexing
- Language server processes

**When concerning:**
- Memory > 6GB
- CPU > 30% when idle
- Continuous high disk I/O when idle

### Database Containers (PostgreSQL, MySQL, etc.)

**Expected behavior:**
- Memory: Grows to configured limits (caching)
- CPU: Bursty during queries
- Steady connections in network stats
- Regular checkpoint I/O

**When concerning:**
- Memory grows beyond configured limits
- High CPU sustained (runaway query?)
- Continuous high disk I/O (missing indexes?)
- Connection count growing unbounded

### Docker Daemon

**Expected behavior:**
- Memory: 500MB-1.5GB depending on container count
- CPU: <5% most of the time, spikes during operations
- Present in top processes on container hosts

**When concerning:**
- Memory > 2GB
- CPU > 10% sustained
- Many restarts in systemd logs

## Desktop Environment Patterns

### Hyprland (Wayland Compositor)

**Expected behavior:**
- Low memory: 50-200MB
- Low CPU: <5% typically
- GPU usage for compositing effects
- Very responsive

**When concerning:**
- Memory > 500MB
- CPU > 10%
- Frequent crashes (check recent_restarts)

### KDE Plasma

**Expected behavior:**
- Memory: 500MB-1.5GB (more than Hyprland)
- CPU: 5-15% with effects
- Multiple KDE processes (plasmashell, kwin, etc.)
- GPU usage for effects

**When concerning:**
- Memory > 2GB
- CPU > 20% sustained
- plasmashell crashes frequently

### GNOME

**Expected behavior:**
- Memory: 800MB-2GB (most of the three)
- CPU: 5-15% typical
- gnome-shell process dominant
- Extensions add overhead

**When concerning:**
- Memory > 3GB
- CPU > 25% sustained
- gnome-shell crashes

## GPU Workload Patterns

### NVIDIA GPUs

**Idle state:**
- Utilization: 0-5%
- Memory: <500MB (Xorg/Wayland)
- Temperature: 30-45°C
- Power: 15-30W

**Light use (desktop/browsing):**
- Utilization: 5-15%
- Memory: 500MB-1GB
- Temperature: 45-55°C
- Power: 30-60W

**Heavy use (gaming/rendering/ML):**
- Utilization: 70-100%
- Memory: Up to card limit
- Temperature: 70-85°C
- Power: Near TDP limit

**When concerning:**
- Temperature > 90°C (throttling)
- Memory exhausted (performance cliff)
- Utilization low when expecting high (driver issue?)
- Power draw low when GPU should be busy (power limit throttling)

### AMD GPUs

Similar patterns to NVIDIA but:
- Different monitoring tools (rocm-smi)
- Temperature targets may differ
- Power characteristics different

## Network Patterns

### Normal Development Workstation

**Expected:**
- Rx: 1-10 MB/s typical, spikes to 50-100 MB/s
- Tx: 0.5-5 MB/s typical
- Established connections: 20-60
- Listening ports: 15-30 (various development services)

**When concerning:**
- Continuous high traffic without explanation
- Connection count > 200 sustained
- Packet errors or drops > 0
- Unexpected listening ports

### Container Host

**Expected:**
- Higher baseline traffic (container networking)
- More established connections (containers)
- Bridge interfaces in network stats
- Port forwarding overhead

### Proxmox Host

**Expected:**
- VM networking traffic
- Cluster communication (if clustered)
- Management interface traffic
- Migration bandwidth spikes

## Arch Linux Specific

**Package manager processes:**
- `pacman`: Package installation/updates
- `yay`, `paru`: AUR helpers
- High disk I/O during updates is normal

**Expected services:**
- Minimal systemd services (Arch philosophy)
- User-enabled services vary
- Often no display manager (startx/Wayland session)

**When concerning:**
- Many failed systemd units (Arch can be fragile)
- High CPU from package manager when not updating
- Missing expected services after boot

## Debian/Server Specific

**Package manager processes:**
- `apt`, `dpkg`: Package management
- `unattended-upgrades`: Automatic updates
- More systemd services than Arch

**Expected services:**
- More services enabled by default
- Often runs display manager
- More conservative package versions

**When concerning:**
- apt/dpkg locked (stuck update?)
- unattended-upgrades high CPU
- Many services failed to start

## Time-of-Day Patterns

### Normal working hours (9am-6pm)
- Higher load on workstations
- More active processes
- Higher memory usage (applications open)
- Network traffic elevated

### Off-hours (night/weekend)
- Lower baseline load
- Scheduled tasks may run (backups, updates)
- Some automation/services still active
- Good time for maintenance

### Suspicious off-hours activity
- High load when user should be away
- Unexpected processes running
- High network traffic at night (data exfiltration?)
- New processes not matching automation schedule

## Seasonal/Workload Patterns

### Build times
- High CPU (compilation)
- High disk I/O (reading source, writing objects)
- Temperature elevation
- Memory usage spike (linkers)

### Testing/CI runs
- Bursty resource usage
- Container churn
- Network traffic (pulling dependencies)
- Predictable pattern

### Video editing/rendering
- Very high GPU usage
- High disk I/O (reading/writing video)
- Memory usage elevated (preview buffers)
- Thermal stress

### Machine learning inference
- High GPU usage sustained
- GPU memory near capacity
- CPU relatively low (GPU-bound)
- Predictable pattern per model

## Quick Reference Checklists

### "Is this normal for a dev workstation?"
- [ ] Firefox/Chrome in top 3 memory? → Normal
- [ ] VSCode/JetBrains present? → Normal
- [ ] Docker daemon running? → Normal
- [ ] Load < 50% of cores? → Normal
- [ ] Memory pressure < 2%? → Normal
- [ ] Swap usage minimal? → Normal

### "Is this normal for a Proxmox host?"
- [ ] Multiple qemu processes? → Normal
- [ ] Load 30-60% of cores? → Normal
- [ ] Memory 70-85% used? → Normal
- [ ] pve-* services running? → Normal
- [ ] Many processes (200+)? → Normal

### "Is this normal for a container host?"
- [ ] dockerd/containerd present? → Normal
- [ ] Elevated baseline load? → Normal
- [ ] Many short-lived processes? → Normal
- [ ] Network bridges in stats? → Normal
- [ ] 50-80% memory usage? → Normal
