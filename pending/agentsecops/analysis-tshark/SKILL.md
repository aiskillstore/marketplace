---
name: analysis-tshark
description: >
  Network protocol analyzer and packet capture tool for traffic analysis, security investigations,
  and forensic examination using Wireshark's command-line interface. Use when: (1) Analyzing network
  traffic for security incidents and malware detection, (2) Capturing and filtering packets for
  forensic analysis, (3) Extracting credentials and sensitive data from network captures, (4)
  Investigating network anomalies and attack patterns, (5) Validating encryption and security
  controls, (6) Performing protocol analysis for vulnerability research.
version: 0.1.0
maintainer: sirappsec@gmail.com
category: offsec
tags: [packet-capture, network-analysis, forensics, tshark, wireshark, traffic-analysis]
frameworks: [MITRE-ATT&CK, NIST]
dependencies:
  packages: [tshark, wireshark]
  tools: [tcpdump, python3]
references:
  - https://www.wireshark.org/docs/man-pages/tshark.html
  - https://wiki.wireshark.org/DisplayFilters
  - https://attack.mitre.org/techniques/T1040/
---

# TShark Network Protocol Analyzer

## Overview

TShark is the command-line network protocol analyzer from the Wireshark project. It provides powerful packet capture and analysis capabilities for security investigations, forensic analysis, and network troubleshooting. This skill covers authorized security operations including traffic analysis, credential extraction, malware detection, and forensic examination.

**IMPORTANT**: Network packet capture may expose sensitive information and must only be conducted with proper authorization. Ensure legal compliance and privacy considerations before capturing network traffic.

## Quick Start

Basic packet capture and analysis:

```bash
# Capture packets on interface
sudo tshark -i eth0

# Capture 100 packets and save to file
sudo tshark -i eth0 -c 100 -w capture.pcap

# Read and analyze capture file
tshark -r capture.pcap

# Apply display filter
tshark -r capture.pcap -Y "http.request.method == GET"

# Extract HTTP objects
tshark -r capture.pcap --export-objects http,extracted_files/
```

## Core Workflow

### Network Analysis Workflow

Progress:
[ ] 1. Verify authorization for packet capture
[ ] 2. Identify target interface and capture requirements
[ ] 3. Capture network traffic with appropriate filters
[ ] 4. Analyze captured packets for security indicators
[ ] 5. Extract artifacts (files, credentials, sessions)
[ ] 6. Document findings and security implications
[ ] 7. Securely handle and store capture files
[ ] 8. Clean up sensitive data per retention policy

Work through each step systematically. Check off completed items.

### 1. Authorization Verification

**CRITICAL**: Before any packet capture:
- Confirm written authorization for network monitoring
- Verify legal compliance (wiretapping laws, privacy regulations)
- Understand data handling and retention requirements
- Document scope of capture (interfaces, duration, filters)
- Ensure secure storage for captured data

### 2. Interface Discovery

Identify available network interfaces:

```bash
# List all interfaces
tshark -D

# List with interface details
sudo tshark -D

# Capture on specific interface
sudo tshark -i eth0
sudo tshark -i wlan0

# Capture on any interface
sudo tshark -i any

# Capture on multiple interfaces
sudo tshark -i eth0 -i wlan0
```

**Interface types**:
- **eth0/ens33**: Ethernet interface
- **wlan0**: Wireless interface
- **lo**: Loopback interface
- **any**: All interfaces (Linux only)
- **mon0**: Monitor mode interface (wireless)

### 3. Basic Packet Capture

Capture network traffic:

```bash
# Capture indefinitely (Ctrl+C to stop)
sudo tshark -i eth0

# Capture specific number of packets
sudo tshark -i eth0 -c 1000

# Capture for specific duration (seconds)
sudo tshark -i eth0 -a duration:60

# Capture to file
sudo tshark -i eth0 -w capture.pcap

# Capture with ring buffer (rotate files)
sudo tshark -i eth0 -w capture.pcap -b filesize:100000 -b files:5
```

**Capture options**:
- `-c <count>`: Capture packet count
- `-a duration:<sec>`: Auto-stop after duration
- `-w <file>`: Write to file
- `-b filesize:<KB>`: Rotate at file size
- `-b files:<num>`: Keep N ring buffer files

### 4. Capture Filters

Apply BPF (Berkeley Packet Filter) during capture for efficiency:

```bash
# Capture only HTTP traffic
sudo tshark -i eth0 -f "tcp port 80"

# Capture specific host
sudo tshark -i eth0 -f "host 192.168.1.100"

# Capture subnet
sudo tshark -i eth0 -f "net 192.168.1.0/24"

# Capture multiple ports
sudo tshark -i eth0 -f "tcp port 80 or tcp port 443"

# Exclude specific traffic
sudo tshark -i eth0 -f "not port 22"

# Capture SYN packets only
sudo tshark -i eth0 -f "tcp[tcpflags] & tcp-syn != 0"
```

**Common capture filters**:
- `host <ip>`: Traffic to/from IP
- `net <cidr>`: Traffic to/from network
- `port <port>`: Specific port
- `tcp|udp|icmp`: Protocol type
- `src|dst`: Direction filter
- `and|or|not`: Logical operators

### 5. Display Filters

Analyze captured traffic with Wireshark display filters:

```bash
# HTTP requests only
tshark -r capture.pcap -Y "http.request"

# HTTP responses
tshark -r capture.pcap -Y "http.response"

# DNS queries
tshark -r capture.pcap -Y "dns.flags.response == 0"

# TLS handshakes
tshark -r capture.pcap -Y "tls.handshake.type == 1"

# Suspicious traffic patterns
tshark -r capture.pcap -Y "tcp.flags.syn==1 and tcp.flags.ack==0"

# Failed connections
tshark -r capture.pcap -Y "tcp.flags.reset==1"
```

**Advanced display filters**:

```bash
# HTTP POST requests with credentials
tshark -r capture.pcap -Y "http.request.method == POST and (http contains \"password\" or http contains \"username\")"

# SMB file transfers
tshark -r capture.pcap -Y "smb2.cmd == 8 or smb2.cmd == 9"

# Suspicious User-Agents
tshark -r capture.pcap -Y "http.user_agent contains \"python\" or http.user_agent contains \"curl\""

# Large data transfers
tshark -r capture.pcap -Y "tcp.len > 1400"

# Beaconing detection (periodic traffic)
tshark -r capture.pcap -Y "http" -T fields -e frame.time_relative -e ip.dst
```

### 6. Protocol Analysis

Analyze specific protocols:

**HTTP/HTTPS Analysis**:

```bash
# Extract HTTP requests
tshark -r capture.pcap -Y "http.request" -T fields -e ip.src -e http.host -e http.request.uri

# Extract HTTP User-Agents
tshark -r capture.pcap -Y "http.user_agent" -T fields -e ip.src -e http.user_agent

# HTTP status codes
tshark -r capture.pcap -Y "http.response" -T fields -e ip.src -e http.response.code

# Extract HTTP cookies
tshark -r capture.pcap -Y "http.cookie" -T fields -e ip.src -e http.cookie
```

**DNS Analysis**:

```bash
# DNS queries
tshark -r capture.pcap -Y "dns.flags.response == 0" -T fields -e ip.src -e dns.qry.name

# DNS responses
tshark -r capture.pcap -Y "dns.flags.response == 1" -T fields -e dns.qry.name -e dns.a

# DNS tunneling detection (long domain names)
tshark -r capture.pcap -Y "dns" -T fields -e dns.qry.name | awk 'length > 50'

# DNS query types
tshark -r capture.pcap -Y "dns" -T fields -e dns.qry.type -e dns.qry.name
```

**TLS/SSL Analysis**:

```bash
# TLS handshakes
tshark -r capture.pcap -Y "tls.handshake.type == 1" -T fields -e ip.src -e ip.dst -e tls.handshake.extensions_server_name

# TLS certificates
tshark -r capture.pcap -Y "tls.handshake.certificate" -T fields -e tls.handshake.certificate

# SSL/TLS versions
tshark -r capture.pcap -Y "tls" -T fields -e tls.record.version

# Weak cipher suites
tshark -r capture.pcap -Y "tls.handshake.ciphersuite" -T fields -e tls.handshake.ciphersuite
```

**SMB/CIFS Analysis**:

```bash
# SMB file access
tshark -r capture.pcap -Y "smb2" -T fields -e ip.src -e smb2.filename

# SMB authentication
tshark -r capture.pcap -Y "ntlmssp" -T fields -e ip.src -e ntlmssp.auth.username

# SMB commands
tshark -r capture.pcap -Y "smb2" -T fields -e smb2.cmd
```

### 7. Credential Extraction

Extract credentials from network traffic (authorized forensics only):

**HTTP Basic Authentication**:

```bash
# Extract HTTP Basic Auth credentials
tshark -r capture.pcap -Y "http.authbasic" -T fields -e ip.src -e http.authbasic

# Decode Base64 credentials
tshark -r capture.pcap -Y "http.authorization" -T fields -e http.authorization | base64 -d
```

**FTP Credentials**:

```bash
# Extract FTP usernames
tshark -r capture.pcap -Y "ftp.request.command == USER" -T fields -e ip.src -e ftp.request.arg

# Extract FTP passwords
tshark -r capture.pcap -Y "ftp.request.command == PASS" -T fields -e ip.src -e ftp.request.arg
```

**NTLM/Kerberos**:

```bash
# Extract NTLM hashes
tshark -r capture.pcap -Y "ntlmssp.auth.ntlmv2response" -T fields -e ntlmssp.auth.username -e ntlmssp.auth.domain -e ntlmssp.auth.ntlmv2response

# Kerberos tickets
tshark -r capture.pcap -Y "kerberos.CNameString" -T fields -e kerberos.CNameString -e kerberos.realm
```

**Email Credentials**:

```bash
# SMTP authentication
tshark -r capture.pcap -Y "smtp.req.command == AUTH" -T fields -e ip.src

# POP3 credentials
tshark -r capture.pcap -Y "pop.request.command == USER or pop.request.command == PASS" -T fields -e pop.request.parameter

# IMAP credentials
tshark -r capture.pcap -Y "imap.request contains \"LOGIN\"" -T fields -e imap.request
```

### 8. File Extraction

Extract files from packet captures:

```bash
# Export HTTP objects
tshark -r capture.pcap --export-objects http,extracted_http/

# Export SMB objects
tshark -r capture.pcap --export-objects smb,extracted_smb/

# Export DICOM objects
tshark -r capture.pcap --export-objects dicom,extracted_dicom/

# Export IMF (email) objects
tshark -r capture.pcap --export-objects imf,extracted_email/
```

**Manual file reconstruction**:

```bash
# Extract file data from HTTP response
tshark -r capture.pcap -Y "http.response and http.content_type contains \"application/pdf\"" -T fields -e data.data | xxd -r -p > extracted_file.pdf

# Reassemble TCP stream
tshark -r capture.pcap -q -z follow,tcp,ascii,<stream-number>
```

### 9. Malware Detection

Identify malicious network activity:

```bash
# Detect common C2 beaconing patterns
tshark -r capture.pcap -Y "http" -T fields -e frame.time_relative -e ip.dst -e http.host | sort | uniq -c | sort -rn

# Suspicious DNS queries (DGA domains)
tshark -r capture.pcap -Y "dns.qry.name" -T fields -e dns.qry.name | awk -F'.' '{print $(NF-1)"."$NF}' | sort | uniq -c | sort -rn

# Detect port scanning
tshark -r capture.pcap -Y "tcp.flags.syn==1 and tcp.flags.ack==0" -T fields -e ip.src -e ip.dst -e tcp.dstport | sort | uniq -c | sort -rn

# Detect data exfiltration (large uploads)
tshark -r capture.pcap -Y "http.request.method == POST" -T fields -e ip.src -e http.content_length | awk '$2 > 1000000'

# Suspicious executable downloads
tshark -r capture.pcap -Y "http.response and (http.content_type contains \"application/exe\" or http.content_type contains \"application/x-dosexec\")"
```

### 10. Statistics and Reporting

Generate traffic statistics:

```bash
# Protocol hierarchy
tshark -r capture.pcap -q -z io,phs

# Conversation statistics
tshark -r capture.pcap -q -z conv,tcp
tshark -r capture.pcap -q -z conv,udp
tshark -r capture.pcap -q -z conv,ip

# HTTP statistics
tshark -r capture.pcap -q -z http,tree

# DNS statistics
tshark -r capture.pcap -q -z dns,tree

# Endpoints
tshark -r capture.pcap -q -z endpoints,tcp
tshark -r capture.pcap -q -z endpoints,udp

# Expert info (warnings/errors)
tshark -r capture.pcap -q -z expert
```

## Security Considerations

### Authorization & Legal Compliance

- **Written Authorization**: Obtain explicit permission for network monitoring
- **Privacy Laws**: Comply with wiretapping and privacy regulations (GDPR, CCPA, ECPA)
- **Data Minimization**: Capture only necessary traffic for investigation
- **Credential Handling**: Treat extracted credentials as highly sensitive
- **Retention Policy**: Follow data retention and secure deletion requirements

### Operational Security

- **Encrypted Storage**: Encrypt capture files at rest
- **Access Control**: Restrict access to packet captures
- **Secure Transfer**: Use encrypted channels for capture file transfer
- **Anonymization**: Remove or redact PII when sharing captures
- **Chain of Custody**: Maintain forensic integrity for legal proceedings

### Audit Logging

Document all packet capture activities:
- Capture start and end timestamps
- Interface(s) captured
- Capture filters applied
- File names and storage locations
- Personnel who accessed captures
- Purpose of capture and investigation findings
- Secure deletion timestamps

### Compliance

- **MITRE ATT&CK**: T1040 (Network Sniffing)
- **NIST CSF**: DE.AE (Detection Processes - Anomalies and Events)
- **PCI-DSS**: Network security monitoring requirements
- **ISO 27001**: A.12.4 Logging and monitoring
- **GDPR**: Data protection and privacy requirements

## Common Patterns

### Pattern 1: Incident Response Investigation

```bash
# Capture traffic during incident
sudo tshark -i eth0 -w incident_$(date +%Y%m%d_%H%M%S).pcap -a duration:300

# Analyze for lateral movement
tshark -r incident.pcap -Y "smb2 or rdp or ssh" -T fields -e ip.src -e ip.dst

# Identify C2 communication
tshark -r incident.pcap -Y "http or dns" -T fields -e ip.dst -e http.host -e dns.qry.name

# Extract IOCs
tshark -r incident.pcap -Y "ip.dst" -T fields -e ip.dst | sort -u > ioc_ips.txt
tshark -r incident.pcap -Y "dns.qry.name" -T fields -e dns.qry.name | sort -u > ioc_domains.txt
```

### Pattern 2: Malware Traffic Analysis

```bash
# Capture malware sandbox traffic
sudo tshark -i eth0 -w malware_traffic.pcap

# Extract C2 indicators
tshark -r malware_traffic.pcap -Y "http.host" -T fields -e ip.src -e http.host -e http.user_agent

# Identify DNS tunneling
tshark -r malware_traffic.pcap -Y "dns" -T fields -e dns.qry.name | awk 'length > 50'

# Extract downloaded payloads
tshark -r malware_traffic.pcap --export-objects http,malware_artifacts/

# Analyze encryption/encoding
tshark -r malware_traffic.pcap -Y "http.request.method == POST" -T fields -e data.data
```

### Pattern 3: Credential Harvesting Detection

```bash
# Monitor for credential transmission
sudo tshark -i eth0 -Y "(http.authorization or ftp or pop or imap) and not tls" -T fields -e ip.src -e ip.dst

# Extract all HTTP POST data
tshark -r capture.pcap -Y "http.request.method == POST" -T fields -e http.file_data > post_data.txt

# Search for password keywords
tshark -r capture.pcap -Y "http contains \"password\" or http contains \"passwd\"" -T fields -e ip.src -e http.request.uri

# NTLM hash extraction
tshark -r capture.pcap -Y "ntlmssp.auth.ntlmv2response" -T fields -e ntlmssp.auth.username -e ntlmssp.auth.domain -e ntlmssp.auth.ntlmv2response > ntlm_hashes.txt
```

### Pattern 4: Network Forensics

```bash
# Reconstruct HTTP conversation
tshark -r capture.pcap -q -z follow,http,ascii,0

# Timeline analysis
tshark -r capture.pcap -T fields -e frame.time -e ip.src -e ip.dst -e tcp.dstport

# Identify file transfers
tshark -r capture.pcap -Y "http.content_type contains \"application/\" or ftp-data" -T fields -e frame.number -e http.content_type

# Geolocation of connections (requires GeoIP)
tshark -r capture.pcap -T fields -e ip.src -e ip.dst -e ip.geoip.src_country -e ip.geoip.dst_country
```

### Pattern 5: Wireless Security Assessment

```bash
# Capture wireless traffic (monitor mode required)
sudo tshark -i mon0 -w wireless_capture.pcap

# Identify wireless networks
tshark -r wireless_capture.pcap -Y "wlan.fc.type_subtype == 0x08" -T fields -e wlan.ssid -e wlan.bssid

# Detect deauth attacks
tshark -r wireless_capture.pcap -Y "wlan.fc.type_subtype == 0x0c"

# WPA handshake capture
tshark -r wireless_capture.pcap -Y "eapol"

# Client probing activity
tshark -r wireless_capture.pcap -Y "wlan.fc.type_subtype == 0x04" -T fields -e wlan.sa -e wlan.ssid
```

## Integration Points

### SIEM Integration

Export packet analysis to SIEM platforms:

```bash
# Export to JSON for Splunk/ELK
tshark -r capture.pcap -T ek > packets.json

# Export specific fields in JSON
tshark -r capture.pcap -Y "http" -T json -e ip.src -e ip.dst -e http.host -e http.request.uri

# CSV export for analysis
tshark -r capture.pcap -T fields -E separator=, -e frame.time -e ip.src -e ip.dst -e tcp.dstport > packets.csv
```

### Scripting and Automation

```bash
#!/bin/bash
# continuous_monitor.sh - Continuous network monitoring

INTERFACE="eth0"
ALERT_FILTER="http contains \"cmd.exe\" or dns.qry.name contains \".tk\" or dns.qry.name contains \".xyz\""

sudo tshark -i $INTERFACE -Y "$ALERT_FILTER" -T fields -e frame.time -e ip.src -e ip.dst -e http.host -e dns.qry.name | \
while read line; do
  echo "[ALERT] $(date): $line" | tee -a security_alerts.log
  # Trigger incident response workflow
  echo "$line" | mail -s "Security Alert" soc@company.com
done
```

## Troubleshooting

### Issue: "Permission denied" when capturing

**Solutions**:
```bash
# Run with sudo
sudo tshark -i eth0

# Or add user to wireshark group (Linux)
sudo usermod -a -G wireshark $USER
sudo setcap cap_net_raw,cap_net_admin+eip /usr/bin/tshark

# Logout and login for group changes to take effect
```

### Issue: "No interfaces found"

**Solutions**:
```bash
# Verify tshark installation
tshark --version

# List interfaces with sudo
sudo tshark -D

# Check interface status
ip link show
ifconfig -a
```

### Issue: Capture file is huge

**Solutions**:
```bash
# Use capture filters to reduce size
sudo tshark -i eth0 -f "not port 22" -w capture.pcap

# Use ring buffer
sudo tshark -i eth0 -w capture.pcap -b filesize:100000 -b files:5

# Limit packet size (snaplen)
sudo tshark -i eth0 -s 128 -w capture.pcap
```

### Issue: Cannot decrypt TLS traffic

**Solutions**:
```bash
# Provide SSL key log file (requires SSLKEYLOGFILE environment variable)
tshark -r capture.pcap -o tls.keylog_file:sslkeys.log -Y "http"

# Use pre-master secret
tshark -r capture.pcap -o tls.keys_list:192.168.1.100,443,http,/path/to/server.key
```

## Defensive Considerations

Organizations should protect against unauthorized packet capture:

- **Network Segmentation**: Reduce exposure to packet sniffing
- **Encryption**: Use TLS/SSL to protect sensitive data in transit
- **Switch Security**: Enable port security and DHCP snooping
- **Wireless Security**: Use WPA3, disable broadcast SSID
- **Intrusion Detection**: Monitor for promiscuous mode interfaces
- **Physical Security**: Protect network infrastructure from tap devices

Detect packet capture activity:
- Monitor for promiscuous mode network interfaces
- Detect ARP spoofing and MAC flooding attacks
- Audit administrative access to network devices
- Monitor for unusual outbound data transfers
- Deploy network access control (802.1X)

## References

- [TShark Man Page](https://www.wireshark.org/docs/man-pages/tshark.html)
- [Wireshark Display Filters](https://wiki.wireshark.org/DisplayFilters)
- [MITRE ATT&CK: Network Sniffing](https://attack.mitre.org/techniques/T1040/)
- [NIST SP 800-92: Guide to Computer Security Log Management](https://csrc.nist.gov/publications/detail/sp/800-92/final)
- [Practical Packet Analysis Book](https://nostarch.com/packetanalysis3)
