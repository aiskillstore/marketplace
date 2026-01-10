# Diagnostic Workflows

Detailed step-by-step procedures for diagnosing complex system issues using GASP output.

## Memory Leak Detection

When suspecting a memory leak:

1. **Identify the suspect**
   - Check `top_processes[]` sorted by `memory_mb`
   - Look for processes with high `uptime_seconds` AND high memory
   - Short uptime + high memory = expected behavior
   - Long uptime + growing memory = possible leak

2. **Compare to baseline**
   - Check `memory.baseline` if available
   - Calculate: `(current - baseline) / baseline * 100` = % growth
   - Growth > 50% over 24h suggests leak

3. **Check system impact**
   - Is `pressure_pct` elevated?
   - Is system swapping? (`swap_used_mb > 0`)
   - Any OOM kills? (`oom_kills_recent > 0`)

4. **Recommendations**
   - Restart the suspect process if safe to do so
   - Monitor memory after restart (does it grow again?)
   - Check application logs for errors
   - Consider memory profiling if problem persists

## Performance Regression Investigation

When "system used to be faster":

1. **Check recent_changes**
   - Look for package updates, service restarts, config changes
   - Correlate timing with user's report

2. **Compare to baseline**
   - CPU: `load_avg_1m` vs `baseline_load`
   - Memory: `usage_percent` vs normal
   - Disk: I/O rates compared to baseline
   - All showing `trend: "increasing"`?

3. **Identify new resource consumers**
   - Check `new_since_last[]` processes
   - Look for unexpected services in `top_processes`
   - Check systemd `recent_restarts[]`

4. **Narrow the timeframe**
   - When did it start? (from user or recent_changes)
   - What changed at that time?
   - Check logs for that timeframe

## Container/VM Performance Issues

When diagnosing containerized or virtualized environments:

1. **Check container metrics** (if present in GASP output)
   - Container resource limits vs actual usage
   - Are containers approaching limits?
   - Check for resource throttling indicators

2. **Host-level analysis**
   - Is the host itself struggling?
   - High baseline load is normal on container hosts
   - Look for noisy neighbor effects (one container starving others)

3. **Network considerations**
   - Check container networking overhead
   - Look for elevated packet errors/drops
   - Inter-container communication issues?

4. **Storage analysis**
   - Container storage driver performance
   - Check for I/O contention between containers
   - Volume mount performance

## GPU Workload Diagnosis

For systems with GPU metrics:

1. **Identify workload type**
   - High GPU + Low CPU = GPU-bound (rendering, ML inference)
   - Low GPU + High CPU = CPU-bound (data prep, preprocessing)
   - High both = Balanced pipeline

2. **Check for GPU bottlenecks**
   - `gpu.utilization_pct > 90%` sustained = GPU-bound
   - Check `gpu.memory_used_mb` vs `gpu.memory_total_mb`
   - GPU memory exhaustion causes severe slowdowns

3. **Temperature and throttling**
   - `gpu.temperature_c > 85°C` = likely thermal throttling
   - Check `gpu.power_watts` vs typical for model
   - Reduced power = throttling active

4. **Per-process analysis**
   - Review `gpu.processes[]` for memory usage
   - Multiple processes competing for GPU?
   - Unexpected GPU usage from background processes?

## Network-Related Issues

When diagnosing network problems:

1. **Check interface statistics**
   - `errors > 0` or `drops > 0` = hardware/driver issue
   - Compare `rx_bytes_per_sec` and `tx_bytes_per_sec` to expected
   - Asymmetric traffic patterns

2. **Connection state analysis**
   - Large number of `time_wait` connections = connection leak
   - Many `established` connections = may be expected or DDoS
   - Review `listening_ports[]` for unexpected services

3. **Recent changes correlation**
   - Did network configuration change?
   - New services started?
   - Firewall rules modified?

4. **Multi-host comparison**
   - Is issue isolated to one host or cluster-wide?
   - Compare connection patterns across hosts
   - Check for network-level issues (switch, router)

## Disk I/O Bottleneck Analysis

When system appears disk-bound:

1. **Confirm disk is the bottleneck**
   - High `io_wait_ms` (>10ms sustained)
   - Low CPU utilization despite high load
   - Elevated `queue_depth`

2. **Identify I/O pattern**
   - High `read_iops` = read-heavy workload
   - High `write_iops` = write-heavy workload
   - Check which processes in `top_processes[]`

3. **Storage capacity check**
   - `usage_percent > 90%` degrades performance
   - Check `inodes_percent` for file count limits
   - Full filesystem causes I/O slowdowns

4. **Recommendations**
   - Move to faster storage (NVMe vs SATA)
   - Adjust application I/O patterns
   - Increase cache sizes if applicable
   - Consider RAID configuration changes

## Systemd Service Failure Investigation

When services are failing:

1. **Review failed_units[]**
   - Note which services are failing
   - Check `recent_restarts[]` for frequency

2. **Correlate with other metrics**
   - Did a service fail due to OOM?
   - Resource exhaustion causing crashes?
   - Dependency failures?

3. **Check log summary**
   - Look in `recent_errors[]` for service-specific errors
   - Elevated error rate around restart time?
   - Specific error patterns?

4. **Follow-up actions**
   - Suggest checking full journal: `journalctl -u service-name`
   - Review service dependencies
   - Check service configuration files
   - Verify resource limits in systemd unit

## Desktop Environment Issues

For desktop workstations with compositor metrics:

1. **Compositor health**
   - Check `desktop.compositor` is running
   - `desktop.session_uptime` vs system uptime
   - Recent compositor crashes?

2. **Resource usage patterns**
   - Browser (Firefox/Chrome) in top memory is expected
   - IDEs (VSCode/JetBrains) high CPU during builds
   - Multiple Electron apps = high memory

3. **GPU desktop acceleration**
   - Check if compositor is using GPU
   - `gpu.utilization_pct` during UI operations
   - GPU memory for desktop compositing

4. **Workspace/window analysis**
   - `desktop.workspaces` count vs normal
   - `desktop.active_window` provides context
   - Too many workspaces/windows = resource pressure

## Cross-Host Issue Correlation

When analyzing multiple hosts simultaneously:

1. **Establish baselines**
   - What's normal for each host type?
   - Workstations vs servers vs container hosts
   - Document expected load ranges

2. **Identify patterns**
   - All hosts affected = infrastructure issue
   - Single host outlier = host-specific problem
   - Subset affected = partial infrastructure issue

3. **Timeline correlation**
   - Check `recent_changes[]` across all hosts
   - Do timing of changes correlate?
   - Cluster-wide updates or migrations?

4. **Resource migration effects**
   - VM migrations in Proxmox clusters
   - Container rebalancing in orchestrated environments
   - Load redistribution after host failures

## Baseline Anomaly Analysis

When metrics significantly differ from baseline:

1. **Calculate deltas**
   - `(current - baseline) / baseline * 100` = % change
   - Changes > 50% warrant investigation
   - Consider time of day/week patterns

2. **Trend analysis**
   - `trend: "increasing"` over time = growing problem
   - `trend: "decreasing"` = resolving or shifting elsewhere
   - `trend: "stable"` at elevated level = new normal?

3. **Determine if new baseline needed**
   - Has workload fundamentally changed?
   - New services/applications deployed?
   - Infrastructure changes (more VMs/containers)?

4. **When to alert**
   - Sudden spike (>100% change) = immediate attention
   - Gradual increase = monitor and plan capacity
   - Decrease = good, but understand why
