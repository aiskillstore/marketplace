---
name: reconnaissance-knowledge
description: Comprehensive knowledge about network reconnaissance and service enumeration. Provides methodologies for port scanning, service fingerprinting, web directory discovery, and vulnerability identification. Includes best practices for structured data collection.
---

# Reconnaissance Knowledge Base

## Purpose
This knowledge base provides comprehensive reconnaissance methodologies and techniques. It covers information gathering about targets without performing exploitation, including discovering services, versions, technologies, and potential attack vectors.

## Tools Available

### Network Scanning
- `nmap` - Port and service discovery
- `masscan` - Fast port scanning (if speed needed)
- `nc` (netcat) - Banner grabbing

### Web Enumeration
- `gobuster` - Directory/file brute forcing
- `dirb` - Alternative directory scanner
- `nikto` - Web vulnerability scanner
- `whatweb` - Technology identification
- `curl`/`wget` - Manual HTTP interaction

### Service Enumeration
- `enum4linux` - SMB/Samba enumeration
- `smbclient` - SMB interaction
- `showmount` - NFS enumeration
- `snmpwalk` - SNMP enumeration

### DNS/Subdomain
- `dig` - DNS queries
- `host` - DNS lookups
- `nslookup` - DNS information

## Layered Reconnaissance Strategy

**Core Principle:** Every reconnaissance task has 3 layers - escalate when previous layer yields insufficient results.

### Layer Framework for Each Task:

```
Layer 1 (Quick & Broad):
  - Fast tools with default parameters
  - Goal: Get initial foothold information
  - Time: 1-5 minutes
  - Example: nmap top 1000 ports, gobuster with small wordlist

Layer 2 (Deep & Intensive):
  - Same tools with aggressive parameters
  - Goal: Extract maximum information from known services
  - Time: 5-30 minutes
  - Example: nmap all ports + version detection, gobuster with large wordlist

Layer 3 (Alternative & Creative):
  - Different tools or manual techniques
  - Goal: Find information that standard tools miss
  - Time: Variable
  - Example: Manual banner grabbing, alternative scanners, custom scripts
```

**Escalation Triggers:**
- Layer 1 returns nothing → Escalate to Layer 2
- Layer 2 returns minimal info → Escalate to Layer 3
- Layer 3 still insufficient → Re-evaluate entire approach

---

## Reconnaissance Phases

### Phase 1: Port Discovery
**Goal**: Find all open ports

```bash
# Quick scan (top 1000 ports)
nmap -p- --min-rate=1000 -T4 TARGET

# Comprehensive scan (all ports)
nmap -p- -T4 TARGET -oN ports.txt
```

**Output Format**:
```json
{
  "ports": [
    {"port": 22, "state": "open", "protocol": "tcp"},
    {"port": 80, "state": "open", "protocol": "tcp"}
  ]
}
```

### Phase 2: Service Detection
**Goal**: Identify services and versions

```bash
# Service version detection
nmap -p22,80,443 -sV -sC -A TARGET -oN services.txt

# Aggressive scan with scripts
nmap -p22,80 -sC -sV --script=default,vuln TARGET
```

**Output Format**:
```json
{
  "services": [
    {
      "port": 22,
      "service": "ssh",
      "version": "OpenSSH 7.6p1",
      "os": "Ubuntu Linux"
    },
    {
      "port": 80,
      "service": "http",
      "version": "Apache httpd 2.4.29",
      "technologies": ["PHP/7.2"]
    }
  ]
}
```

### Phase 3: Web Enumeration (if HTTP/HTTPS found)
**Goal**: Discover hidden files, directories, and web technologies

**Layered Web Scanning:**

```bash
# Layer 1: Quick directory scan
gobuster dir -u http://TARGET -w /usr/share/wordlists/dirb/common.txt -x php,html,txt -t 50

# If Layer 1 finds little/nothing, escalate to Layer 2:
# Layer 2: Deep directory scan with larger wordlist
gobuster dir -u http://TARGET -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x php,html,txt,zip,bak -t 100

# If still insufficient, try Layer 3:
# Layer 3: Alternative tools or techniques
# Option A: Different tool
feroxbuster -u http://TARGET -w /usr/share/wordlists/dirb/common.txt

# Option B: Vulnerability scanner
nikto -h http://TARGET

# Option C: Technology detection
whatweb http://TARGET

# Alternative with larger wordlist
gobuster dir -u http://TARGET -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -t 50

# Technology detection
whatweb http://TARGET

# Vulnerability scan
nikto -h http://TARGET
```

**Output Format**:
```json
{
  "web": {
    "url": "http://10.10.10.1",
    "technologies": ["Apache/2.4.29", "PHP/7.2", "WordPress 5.0"],
    "directories": [
      "/admin (Status: 403)",
      "/uploads (Status: 301)",
      "/backup (Status: 200)"
    ],
    "files": [
      "/config.php (Status: 200)",
      "/README.txt (Status: 200)"
    ],
    "vulnerabilities": [
      "Outdated WordPress version",
      "Directory listing enabled on /uploads"
    ]
  }
}
```

### Phase 4: Specific Service Enumeration

#### SMB (Port 139/445)
```bash
# Basic enumeration
enum4linux -a TARGET

# List shares
smbclient -L //TARGET -N

# Check for anonymous access
smbmap -H TARGET
```

#### FTP (Port 21)
```bash
# Check for anonymous login
ftp TARGET
# Try: anonymous / anonymous

# Banner grab
nc TARGET 21
```

#### SSH (Port 22)
```bash
# Get SSH version and algorithms
ssh -v TARGET

# Check for user enumeration
ssh user@TARGET 2>&1 | grep -i "invalid\|denied"
```

#### MySQL/MSSQL (Port 3306/1433)
```bash
# Banner grab
nc TARGET 3306

# Test default credentials
mysql -h TARGET -u root -p
# Try common passwords: root, admin, password, ''
```

## Best Practices

### 1. Structured Output
Always format discoveries in JSON for easy parsing:

```bash
# Example: Parse nmap output to JSON
nmap -p- TARGET -oG - | grep "Ports:" | awk '{print $2, $4}' | sed 's/\/open//' | jq -R -s 'split("\n") | map(select(length > 0) | split(" ") | {port: .[1], service: .[0]})'
```

### 2. Stealth vs Speed
- For playground environments: Use aggressive scans (`-T4`, `--min-rate=1000`)
- For real environments: Use slower, stealthy scans (`-T2`)

### 3. Save All Output
```bash
# Always save raw output
nmap ... -oN nmap-full.txt -oX nmap-full.xml

# Save discoveries to state file
cat discovered.json >> .pentest-state.json
```

### 4. Comprehensive Coverage
Don't miss:
- UDP ports (slower but important): `nmap -sU --top-ports 100 TARGET`
- All TCP ports: `nmap -p- TARGET`
- Web directories with multiple wordlists
- Default credentials for all services found

### 5. Time Management
- Quick initial scan: 5 minutes max
- Comprehensive scan: 15-20 minutes max
- This is a playground, not real-world - speed matters

## Common Wordlists

```bash
# Small (fast)
/usr/share/wordlists/dirb/common.txt

# Medium (balanced)
/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt

# Large (comprehensive)
/usr/share/wordlists/dirbuster/directory-list-2.3-big.txt

# Specific to web apps
/usr/share/wordlists/wfuzz/general/common.txt
```

## Output Template

After completing reconnaissance, provide summary in this format:

```json
{
  "target": "10.10.10.1",
  "scan_date": "2025-01-15",
  "discovered": {
    "ports": [
      {"port": 22, "service": "ssh", "version": "OpenSSH 7.6p1"},
      {"port": 80, "service": "http", "version": "Apache 2.4.29"}
    ],
    "web": {
      "technologies": ["Apache", "PHP", "WordPress"],
      "interesting_paths": ["/admin", "/uploads", "/wp-admin"],
      "vulnerabilities": ["Outdated WordPress", "Directory listing"]
    },
    "potential_vectors": [
      "File upload via /uploads",
      "WordPress plugin vulnerabilities",
      "SSH password authentication enabled"
    ]
  },
  "recommended_actions": [
    "Test file upload functionality on /uploads",
    "Search for WordPress exploits for version detected",
    "Enumerate WordPress users with wpscan"
  ]
}
```

## Key Principles

1. **Thoroughness**: Don't miss services or directories
2. **Structure**: Always output JSON for coordinator to parse
3. **Speed**: Balance between comprehensive and efficient
4. **Context**: Provide next-step recommendations
5. **No Exploitation**: Stay in recon phase, don't test exploits

## Handoff to Next Phase

When reconnaissance is complete, provide:
1. Complete service inventory
2. Identified vulnerabilities
3. Recommended exploitation approaches
4. Any discovered credentials/default logins
5. Updated `.pentest-state.json`

After reconnaissance is sufficient, proceed to the exploitation phase using exploitation knowledge.
