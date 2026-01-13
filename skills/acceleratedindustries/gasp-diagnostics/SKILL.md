---
name: gasp-diagnostics
description: System diagnostics using GASP (General AI Specialized Process monitor). Use when user asks about Linux system performance, requests system checks, mentions GASP, asks to diagnose hosts, or says things like "check my system" or "what's wrong with [hostname]". Can actively fetch GASP metrics from hosts via HTTP or interpret provided JSON output.
---

# GASP Diagnostics

Enables comprehensive Linux system diagnostics using GASP's AI-optimized monitoring output. Actively fetches metrics from hosts and provides intelligent analysis with context-aware interpretation.

## Fetching GASP Metrics

When user mentions a host or requests a system check:

1. **Fetch the metrics endpoint**
   ```
   web_fetch("http://{hostname}:8080/metrics")
   ```

2. **Hostname formats supported**
   - mDNS/local: `accelerated.local`, `hyperion.local`
   - DNS names: `proxmox1`, `dev-server`, `workstation`
   - IP addresses: `192.168.1.100`

3. **Default port**: 8080 (unless user specifies otherwise)

4. **Error handling**
   - Host unreachable: Inform user, suggest checking if GASP is running
   - Port closed/refused: Try suggesting `systemctl status gasp` on the host
   - JSON parse error: GASP may not be installed or wrong endpoint
   - Timeout: Network issue or host down

5. **Multi-host queries**: If user mentions multiple hosts, fetch each in sequence and compare

## Quick Diagnosis Workflow

For any system check request:

1. **Fetch** metrics from specified host(s)
2. **Check summary first**: Look at `summary.health` and `summary.concerns[]`
3. **Identify issues** using metric correlations below
4. **Report** findings with severity and specific recommendations

## Trigger Examples

These user messages should trigger this skill and active fetching:

- "Check hyperion for me"
- "What's going on with accelerated.local?"
- "Is proxmox1 having issues?"
- "Compare hyperion and proxmox1"
- "Why is my system slow?" (fetch localhost)
- "Diagnose 192.168.1.50"
- "Check all my proxmox nodes"

## Metric Interpretation

### Health Summary
- `summary.health`: Quick assessment
  - "healthy": No action needed
  - "degraded": Issues present but not critical
  - "critical": Immediate attention required
- `summary.concerns[]`: Pre-analyzed issues to investigate first
- `summary.recent_changes[]`: Context for current state

### CPU Analysis

**Load ratio** = `load_avg_1m / cores`:
- < 0.7: Normal usage
- 0.7-1.0: Busy but healthy
- 1.0-2.0: Saturated (may cause slowness)
- \> 2.0: Severe overload

**Key indicators**:
- `trend`: "increasing" is concerning even if current load is acceptable
- `baseline_load`: Delta from baseline is more important than absolute value
- `top_processes[]`: Check for unexpected CPU hogs

### Memory Analysis

**Red flags** (priority order):
1. `oom_kills_recent > 0`: CRITICAL - system killed processes, find memory hog immediately
2. `swap_used_mb > 0`: Performance degradation in progress
3. `pressure_pct > 5%`: System struggling with memory contention
4. `usage_percent > 90%`: Getting close to limits

**Important**: Linux uses memory for cache, so high `usage_percent` alone is normal. Focus on pressure and swap.

### Disk I/O

**Saturation indicators**:
- `io_wait_ms > 10`: Significant disk bottleneck
- `queue_depth` consistently high: Disk can't keep up
- High `read_iops` or `write_iops` with slow response: Disk performance issue

**Storage capacity**:
- `usage_percent > 90%`: Running out of space
- `usage_percent > 95%`: Critical - will cause failures soon

### Network

- `rx_bytes_per_sec` / `tx_bytes_per_sec`: Check for unexpected traffic spikes
- `errors > 0` or `drops > 0`: Network hardware/configuration issue
- Large number of `time_wait` connections: May indicate connection leak

### Process Intelligence

- `zombie > 0`: Process management bug (usually benign but indicates issue)
- Processes in `D state`: Stuck in uninterruptible sleep (disk or kernel issue)
- `new_since_last[]`: Check for unexpected process spawning

### Systemd Services

- `units_failed > 0`: Check `failed_units[]` array
- `recent_restarts[]`: May indicate instability

### Log Summary

- `errors_last_interval`: Elevated error rate indicates problems
- `message_rate_per_min`: Spikes suggest logging storm or serious issue
- Review `recent_errors[]` for specific problems

### Desktop Metrics (when present)

- `gpu.utilization_pct` vs CPU: Identify GPU-bound vs CPU-bound workloads
- `gpu.temperature_c > 85`: Thermal throttling likely
- `active_window`: Provides context for resource usage

## Common System Patterns

### Development Workstation (Expected)
- High memory usage from IDEs, browsers
- Firefox/Chrome often in top memory consumers
- Docker daemon using CPU/memory
- VSCode, JetBrains IDEs in top processes
- Baseline load: 10-30% of cores

### Container Host (Expected)
- Elevated baseline load (many processes)
- dockerd/containerd in top processes
- 50-70% memory usage normal
- Many processes in top list

### Proxmox/Virtualization Host (Expected)
- Baseline load proportional to VM count
- Consistent low-level resource usage
- ~2GB overhead for Proxmox itself
- Multiple QEMU/KVM processes

### GPU Workload (Expected)
- High GPU utilization with lower CPU
- Significant GPU memory usage
- Common for: rendering, ML inference, gaming

## Multi-Host Analysis

When checking multiple hosts:

1. **Fetch all hosts first** (parallel thinking)
2. **Compare baselines**: Identify outliers
3. **Look for correlations**: Network event vs individual host issue
4. **Check recent_changes**: Migrations, deployments, package updates
5. **Identify the odd one out**: Which host differs from the pattern?

Example analysis pattern:
```
Host 1: Load 2.1/8 cores (26%), normal
Host 2: Load 7.8/8 cores (97%), ATTENTION NEEDED  ← outlier
Host 3: Load 1.9/8 cores (24%), normal

Focus on Host 2 - investigate top_processes
```

## Diagnosis Strategies

### "System is slow"

1. Check load ratio (CPU saturation?)
2. Check io_wait (disk bottleneck?)
3. Check memory pressure (swapping?)
4. Identify top consumer in relevant category
5. Assess if consumption is expected for that process

### "High memory usage"

1. First: Check pressure_pct (real issue or just cache?)
2. Check swap_used_mb (actual problem?)
3. Find top memory consumers
4. Check process uptime (leak or normal?)
5. Compare to baseline (delta more important than absolute)

### "Unexpected behavior"

1. Check recent_changes for clues
2. Review systemd failed units
3. Check recent_errors in logs
4. Look for new processes since last snapshot
5. Compare current metrics to baseline

## Reporting Guidelines

When reporting findings:

1. **Start with verdict**: "Healthy", "Issue found", "Critical problem"
2. **Be specific**: Name the process/service causing issues
3. **Provide context**: Is this expected for this host type?
4. **Give actionable recommendations**: What should user do?
5. **Include relevant metrics**: Back up findings with data

Good example:
> "Issue found on accelerated.local: Memory pressure at 8.2%. The postgres container started swapping 2 hours ago and is now using 12GB RAM (up from 4GB baseline). This likely indicates a query leak. Recommend checking recent queries and restarting the container."

Bad example:
> "Memory usage is high. You might want to look into it."

## Advanced Diagnostics

For complex issues or when initial analysis is unclear, consult:
- [references/diagnostic-workflows.md](references/diagnostic-workflows.md) - Detailed diagnostic procedures
- [references/common-patterns.md](references/common-patterns.md) - Infrastructure-specific patterns

## Using with Provided JSON

If user pastes GASP JSON instead of requesting a fetch:
1. Analyze the provided JSON using all guidance above
2. Don't attempt to fetch (data already provided)
3. Apply same interpretation and reporting guidelines
