---
name: remote-system-maintenance
description: This skill should be used when performing maintenance or diagnostics on remote Linux systems. Triggers on "remote server", "Linux maintenance", "Ubuntu cleanup", "Debian", "disk space", "apt cleanup", "journal vacuum", "snap cleanup", "system diagnostics". Provides structured three-phase checklists with quantification.
---

# Remote System Maintenance

## Purpose

Structured guidance for diagnosing and maintaining remote Linux systems through SSH/tmux sessions, with emphasis on Ubuntu/Debian platforms.

## Applicable Scenarios

- System maintenance tasks
- Disk space recovery
- Package updates
- Health diagnostics
- Cleanup operations on remote servers

## Three-Phase Approach

### Phase 1: Initial Diagnostics

Capture baseline system state:
- Hostname and system identification
- Resource utilization (disk, memory, CPU)
- Process status and load
- Zombie process detection

### Phase 2: System Log Review

Examine system health indicators:
- Recent error messages in system logs
- Journal disk consumption analysis
- Critical service status
- Authentication and security events

### Phase 3: Package Assessment

Identify maintenance opportunities:
- Upgradable packages
- Orphaned configurations
- Unused dependencies
- Package cache size

## Ubuntu/Debian Cleanup Sequence

Execute these seven stages in order:

1. **Package Cache Refresh** - `apt update` to sync package lists
2. **System Upgrades** - `apt upgrade` for security and bug fixes
3. **Orphan Removal** - `apt autoremove` to clean unused dependencies
4. **Cache Purging** - `apt clean` to reclaim package cache space
5. **Journal Pruning** - `journalctl --vacuum-time=7d` to limit log retention
6. **Snap Revision Cleanup** - Remove disabled snap revisions (see below)
7. **Temporary Directory Assessment** - Review `/tmp` and `/var/tmp` for cleanup opportunities

## Snap Revision Cleanup Technique

Snap keeps old revisions by default. To identify and remove:

```bash
# List all disabled snap revisions
snap list --all | awk '/disabled/{print $1, $3}'

# Remove specific revision
snap remove <package-name> --revision=<revision-number>
```

**Important**: Requires explicit removal by revision number, not simple package uninstallation.

## Documentation Requirements

All maintenance sessions must generate structured logs recording:

1. **System Identification**
   - Hostname
   - OS version
   - Kernel information
   - Operator identity

2. **Resource States**
   - Initial disk/memory/CPU usage
   - Final disk/memory/CPU usage
   - Quantified improvements

3. **Actions Taken**
   - Specific commands executed
   - MB/GB freed per category
   - Packages upgraded/removed

4. **Follow-up Recommendations**
   - Remaining issues
   - Future maintenance needs
   - Monitoring suggestions

## Expected Results

Real-world recovery examples:
- **Journal vacuuming**: 300-600 MB
- **Snap revision cleanup**: 500 MB to 2 GB
- **Package cache purging**: 100-500 MB
- **Total potential**: 2+ GB in comprehensive sessions

## Time Commitment

Typical maintenance session: 15-30 minutes including diagnostics, cleanup, and documentation.
