---
name: resource-monitor
description: Monitor system resources (CPU, memory, disk, network) during development and production.
---

# Resource Monitor Skill

Monitor system resources (CPU, memory, disk, network) during development and production.

## Instructions

You are a system resource monitoring expert. When invoked:

1. **Monitor Resources**:
   - CPU usage and load average
   - Memory usage (RAM and swap)
   - Disk usage and I/O
   - Network traffic and connections
   - Process-level metrics

2. **Analyze Patterns**:
   - Identify resource-intensive processes
   - Detect memory leaks
   - Find CPU bottlenecks
   - Monitor disk space trends
   - Track network bandwidth usage

3. **Set Alerts**:
   - CPU usage thresholds
   - Memory limits
   - Disk space warnings
   - Unusual network activity

4. **Provide Recommendations**:
   - Resource optimization strategies
   - Scaling recommendations
   - Configuration improvements
   - Performance tuning

## Resource Metrics

### CPU Monitoring
```bash
# Current CPU usage
top -bn1 | grep "Cpu(s)"

# Per-core usage
mpstat -P ALL 1

# Process CPU usage
ps aux --sort=-%cpu | head -10

# Load average
uptime

# Node.js CPU profiling
node --prof app.js
node --prof-process isolate-*.log
```

### Memory Monitoring
```bash
# Memory usage
free -h

# Detailed memory info
cat /proc/meminfo

# Process memory usage
ps aux --sort=-%mem | head -10

# Memory map for specific process
pmap -x <PID>

# Node.js memory usage
node --inspect app.js
# Chrome DevTools -> Memory
```

### Disk Monitoring
```bash
# Disk space
df -h

# Disk I/O
iostat -x 1

# Large files/directories
du -h --max-depth=1 / | sort -hr | head -20

# Disk usage by directory
ncdu /

# Monitor disk writes
iotop
```

### Network Monitoring
```bash
# Network connections
netstat -tunapl

# Active connections
ss -s

# Bandwidth usage
iftop

# Network traffic
nload

# Connection states
netstat -ant | awk '{print $6}' | sort | uniq -c | sort -n
```

## Monitoring Scripts

### Node.js Resource Monitor
```javascript
// resource-monitor.js
const os = require('os');

class ResourceMonitor {
  constructor(interval = 5000) {
    this.interval = interval;
    this.startTime = Date.now();
  }

  start() {
    console.log('🔍 Resource Monitor Started\n');
    this.logResources();
    setInterval(() => this.logResources(), this.interval);
  }

  logResources() {
    const uptime = Math.floor((Date.now() - this.startTime) / 1000);
    const cpu = this.getCPUUsage();
    const memory = this.getMemoryUsage();
    const load = os.loadavg();

    console.clear();
    console.log('📊 System Resources');
    console.log('='.repeat(50));
    console.log(`Uptime: ${this.formatUptime(uptime)}`);
    console.log('');

    console.log('CPU:');
    console.log(`  Usage: ${cpu.toFixed(2)}%`);
    console.log(`  Load Average: ${load[0].toFixed(2)}, ${load[1].toFixed(2)}, ${load[2].toFixed(2)}`);
    console.log(`  Cores: ${os.cpus().length}`);
    console.log('');

    console.log('Memory:');
    console.log(`  Total: ${this.formatBytes(memory.total)}`);
    console.log(`  Used: ${this.formatBytes(memory.used)} (${memory.percentage.toFixed(2)}%)`);
    console.log(`  Free: ${this.formatBytes(memory.free)}`);
    this.printProgressBar('Memory', memory.percentage);
    console.log('');

    const processMemory = process.memoryUsage();
    console.log('Process Memory:');
    console.log(`  RSS: ${this.formatBytes(processMemory.rss)}`);
    console.log(`  Heap Total: ${this.formatBytes(processMemory.heapTotal)}`);
    console.log(`  Heap Used: ${this.formatBytes(processMemory.heapUsed)}`);
    console.log(`  External: ${this.formatBytes(processMemory.external)}`);
    console.log('');

    this.checkThresholds(cpu, memory);
  }

  getCPUUsage() {
    const cpus = os.cpus();
    let totalIdle = 0;
    let totalTick = 0;

    cpus.forEach(cpu => {
      for (const type in cpu.times) {
        totalTick += cpu.times[type];
      }
      totalIdle += cpu.times.idle;
    });

    const idle = totalIdle / cpus.length;
    const total = totalTick / cpus.length;
    const usage = 100 - ~~(100 * idle / total);

    return usage;
  }

  getMemoryUsage() {
    const total = os.totalmem();
    const free = os.freemem();
    const used = total - free;
    const percentage = (used / total) * 100;

    return { total, free, used, percentage };
  }

  formatBytes(bytes) {
    const units = ['B', 'KB', 'MB', 'GB', 'TB'];
    let size = bytes;
    let unitIndex = 0;

    while (size >= 1024 && unitIndex < units.length - 1) {
      size /= 1024;
      unitIndex++;
    }

    return `${size.toFixed(2)} ${units[unitIndex]}`;
  }

  formatUptime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hours}h ${minutes}m ${secs}s`;
  }

  printProgressBar(label, percentage) {
    const width = 40;
    const filled = Math.floor(width * percentage / 100);
    const empty = width - filled;
    const bar = '█'.repeat(filled) + '░'.repeat(empty);

    let color = '\x1b[32m'; // Green
    if (percentage > 70) color = '\x1b[33m'; // Yellow
    if (percentage > 85) color = '\x1b[31m'; // Red

    console.log(`  ${color}[${bar}] ${percentage.toFixed(1)}%\x1b[0m`);
  }

  checkThresholds(cpu, memory) {
    const warnings = [];

    if (cpu > 80) {
      warnings.push(`⚠️  High CPU usage: ${cpu.toFixed(2)}%`);
    }

    if (memory.percentage > 80) {
      warnings.push(`⚠️  High memory usage: ${memory.percentage.toFixed(2)}%`);
    }

    if (warnings.length > 0) {
      console.log('\nWarnings:');
      warnings.forEach(w => console.log(`  ${w}`));
    }
  }
}

// Start monitoring
const monitor = new ResourceMonitor(5000);
monitor.start();
```

### Python Resource Monitor
```python
# resource_monitor.py
import psutil
import time
from datetime import datetime

class ResourceMonitor:
    def __init__(self, interval=5):
        self.interval = interval

    def start(self):
        print("🔍 Resource Monitor Started\n")
        while True:
            self.log_resources()
            time.sleep(self.interval)

    def log_resources(self):
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        net = psutil.net_io_counters()

        print("\033[2J\033[H")  # Clear screen
        print("📊 System Resources")
        print("=" * 50)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        print("CPU:")
        print(f"  Usage: {cpu_percent}%")
        print(f"  Cores: {psutil.cpu_count()}")
        self.print_progress_bar("CPU", cpu_percent)
        print()

        print("Memory:")
        print(f"  Total: {self.format_bytes(memory.total)}")
        print(f"  Used: {self.format_bytes(memory.used)} ({memory.percent}%)")
        print(f"  Free: {self.format_bytes(memory.available)}")
        self.print_progress_bar("Memory", memory.percent)
        print()

        print("Disk:")
        print(f"  Total: {self.format_bytes(disk.total)}")
        print(f"  Used: {self.format_bytes(disk.used)} ({disk.percent}%)")
        print(f"  Free: {self.format_bytes(disk.free)}")
        self.print_progress_bar("Disk", disk.percent)
        print()

        print("Network:")
        print(f"  Sent: {self.format_bytes(net.bytes_sent)}")
        print(f"  Received: {self.format_bytes(net.bytes_recv)}")
        print()

        self.check_thresholds(cpu_percent, memory.percent, disk.percent)

    def format_bytes(self, bytes):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes < 1024:
                return f"{bytes:.2f} {unit}"
            bytes /= 1024
        return f"{bytes:.2f} PB"

    def print_progress_bar(self, label, percentage):
        width = 40
        filled = int(width * percentage / 100)
        empty = width - filled
        bar = '█' * filled + '░' * empty

        if percentage > 85:
            color = '\033[91m'  # Red
        elif percentage > 70:
            color = '\033[93m'  # Yellow
        else:
            color = '\033[92m'  # Green

        print(f"  {color}[{bar}] {percentage:.1f}%\033[0m")

    def check_thresholds(self, cpu, memory, disk):
        warnings = []

        if cpu > 80:
            warnings.append(f"⚠️  High CPU usage: {cpu}%")
        if memory > 80:
            warnings.append(f"⚠️  High memory usage: {memory}%")
        if disk > 80:
            warnings.append(f"⚠️  Low disk space: {100-disk}% free")

        if warnings:
            print("\nWarnings:")
            for warning in warnings:
                print(f"  {warning}")

# Start monitoring
monitor = ResourceMonitor(interval=5)
monitor.start()
```

## Usage Examples

```
@resource-monitor
@resource-monitor --interval 5
@resource-monitor --alert
@resource-monitor --process node
@resource-monitor --export-metrics
```

## Monitoring Report

```markdown
# Resource Monitoring Report

**Period**: 2024-01-15 00:00 - 23:59
**Server**: web-server-01
**Environment**: Production

---

## Executive Summary

**Overall Health**: 🟢 Good
**Critical Alerts**: 0
**Warnings**: 3
**Average CPU**: 45%
**Average Memory**: 62%
**Disk Usage**: 58%

---

## CPU Metrics

**Average**: 45%
**Peak**: 87% (at 14:30)
**Minimum**: 12% (at 03:00)

**Load Average**:
- 1 min: 2.34
- 5 min: 2.12
- 15 min: 1.98

**Top CPU Processes**:
1. node (PID 1234): 34%
2. postgres (PID 5678): 12%
3. redis (PID 9012): 5%

**Timeline**:
```
00:00 ████░░░░░░  12%
06:00 ████████░░  35%
12:00 ███████████ 52%
14:30 █████████████████ 87% ⚠️ PEAK
18:00 ████████░░  38%
23:00 █████░░░░░  18%
```

---

## Memory Metrics

**Total**: 16 GB
**Average Used**: 9.92 GB (62%)
**Peak**: 13.6 GB (85%) ⚠️
**Swap Used**: 0 GB

**Memory Breakdown**:
- Application: 6.4 GB (40%)
- Database: 2.4 GB (15%)
- Cache: 1.12 GB (7%)
- System: 0.8 GB (5%)
- Free: 5.28 GB (33%)

**Top Memory Processes**:
1. node (PID 1234): 6.4 GB
2. postgres (PID 5678): 2.4 GB
3. redis (PID 9012): 1.12 GB

**Memory Timeline**:
```
00:00 ████████░░  58%
06:00 ████████░░  62%
12:00 █████████░  68%
14:30 █████████████ 85% ⚠️ PEAK
18:00 ████████░░  65%
23:00 ████████░░  60%
```

---

## Disk Metrics

**Total**: 500 GB
**Used**: 290 GB (58%)
**Free**: 210 GB (42%)

**Disk I/O**:
- Read: 12.3 GB/day
- Write: 8.7 GB/day
- Average IOPS: 234

**Largest Directories**:
1. /var/log: 45 GB (15.5%)
2. /var/lib/postgresql: 89 GB (30.7%)
3. /app/uploads: 67 GB (23.1%)
4. /var/lib/redis: 23 GB (7.9%)

**Growth Trend**: +2.3 GB/day
**Estimated Full**: 91 days

---

## Network Metrics

**Traffic**:
- Sent: 234 GB
- Received: 456 GB
- Total: 690 GB

**Bandwidth**:
- Average: 80 Mbps
- Peak: 450 Mbps (at 15:00)

**Connections**:
- Established: 1,234
- Time Wait: 456
- Close Wait: 23

**Top Talkers**:
1. 192.168.1.100: 45 GB
2. 10.0.0.50: 34 GB
3. 172.16.0.20: 28 GB

---

## Alerts & Warnings

### Critical (0)
None

### Warnings (3)

1. **High CPU at 14:30**
   - Peak: 87%
   - Duration: 15 minutes
   - Cause: Scheduled report generation
   - Action: Consider moving to off-peak hours

2. **High Memory at 14:30**
   - Peak: 85%
   - Duration: 20 minutes
   - Cause: Large dataset processing
   - Action: Implement streaming or pagination

3. **Log Directory Growing**
   - Size: 45 GB
   - Growth: 1.2 GB/day
   - Action: Implement log rotation and archiving

---

## Recommendations

### Immediate Actions
1. ✓ Implement log rotation (reduce from 45 GB to <10 GB)
2. ✓ Schedule resource-intensive tasks during off-peak hours
3. ✓ Add memory limit to application (max 8 GB)

### Short Term
1. Monitor memory usage trend for potential leak
2. Optimize report generation queries
3. Add caching for frequently accessed data
4. Archive old database data

### Long Term
1. Consider vertical scaling (upgrade to 32 GB RAM)
2. Implement horizontal scaling for peak hours
3. Move file uploads to object storage (S3)
4. Set up predictive alerting

---

## Capacity Planning

**Current Capacity**: 🟢 Good

**Projections** (next 3 months):
- CPU: Will remain within acceptable range
- Memory: May need upgrade if trend continues
- Disk: Need to address log growth
- Network: Current capacity sufficient

**Recommended Actions**:
- Monitor memory usage weekly
- Implement log archiving within 1 week
- Plan for storage expansion in 6 months
```

## Alerting Thresholds

### CPU
- **Warning**: > 70% for 5 minutes
- **Critical**: > 85% for 5 minutes

### Memory
- **Warning**: > 80% used
- **Critical**: > 90% used

### Disk
- **Warning**: > 80% used
- **Critical**: > 90% used

### Network
- **Warning**: > 80% bandwidth
- **Critical**: Connection errors > 100/min

## Tools & Integration

### Monitoring Tools
- **Prometheus**: Metrics collection
- **Grafana**: Visualization and dashboards
- **Datadog**: Full-stack monitoring
- **New Relic**: Application performance
- **CloudWatch**: AWS monitoring
- **htop**: Interactive process viewer
- **glances**: System monitoring (CLI)

### Node.js Monitoring
```javascript
// Using prom-client for Prometheus
const client = require('prom-client');

const register = new client.Registry();

// CPU metric
const cpuUsage = new client.Gauge({
  name: 'process_cpu_usage_percent',
  help: 'Process CPU usage percentage',
  registers: [register]
});

// Memory metric
const memoryUsage = new client.Gauge({
  name: 'process_memory_usage_bytes',
  help: 'Process memory usage in bytes',
  registers: [register]
});

// Update metrics every 5 seconds
setInterval(() => {
  const usage = process.cpuUsage();
  cpuUsage.set(usage.user + usage.system);

  const mem = process.memoryUsage();
  memoryUsage.set(mem.heapUsed);
}, 5000);
```

## Notes

- Monitor regularly, not just when issues occur
- Set up automated alerts for critical thresholds
- Keep historical data for trend analysis
- Correlate resource usage with application events
- Use monitoring data for capacity planning
- Establish baselines for normal behavior
- Don't over-alert (alert fatigue)
- Document unusual patterns and their causes
