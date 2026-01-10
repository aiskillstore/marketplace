---
name: crack-hashcat
description: >
  Advanced password recovery and hash cracking tool supporting multiple algorithms and attack modes.
  Use when: (1) Performing authorized password auditing and security assessments, (2) Recovering
  passwords from captured hashes in forensic investigations, (3) Testing password policy strength
  and complexity, (4) Validating encryption implementations, (5) Conducting security research on
  cryptographic hash functions, (6) Demonstrating password weakness in penetration testing reports.
version: 0.1.0
maintainer: sirappsec@gmail.com
category: offsec
tags: [password-cracking, hashcat, forensics, password-audit, cryptography]
frameworks: [MITRE-ATT&CK, NIST]
dependencies:
  packages: [hashcat]
  tools: [opencl, cuda]
references:
  - https://hashcat.net/wiki/
  - https://hashcat.net/hashcat/
  - https://attack.mitre.org/techniques/T1110/
---

# Hashcat Password Recovery

## Overview

Hashcat is the world's fastest password recovery tool, supporting over 300 hash algorithms and multiple attack modes. This skill covers authorized password auditing, forensic password recovery, and security research applications.

**IMPORTANT**: Password cracking must only be performed on hashes you are authorized to crack. Unauthorized password cracking is illegal. Always ensure proper authorization and legal compliance.

## Quick Start

Basic password cracking:

```bash
# Identify hash type
hashcat --example-hashes | grep -i md5

# Dictionary attack on MD5 hash
hashcat -m 0 -a 0 hashes.txt wordlist.txt

# Show cracked passwords
hashcat -m 0 hashes.txt --show

# Benchmark system performance
hashcat -b
```

## Core Workflow

### Password Cracking Workflow

Progress:
[ ] 1. Verify authorization for password cracking
[ ] 2. Identify hash algorithm type
[ ] 3. Prepare hash file and wordlists
[ ] 4. Select appropriate attack mode
[ ] 5. Execute cracking operation
[ ] 6. Analyze cracked passwords
[ ] 7. Document password policy weaknesses
[ ] 8. Securely delete hash files and results

Work through each step systematically. Check off completed items.

### 1. Authorization Verification

**CRITICAL**: Before any password cracking:
- Confirm written authorization from data owner
- Verify legal right to crack captured hashes
- Understand data handling and retention requirements
- Document chain of custody for forensic cases
- Ensure secure storage of cracked passwords

### 2. Hash Identification

Identify hash algorithm:

```bash
# Show all supported hash types
hashcat --example-hashes

# Common hash types
hashcat --example-hashes | grep -i "MD5"
hashcat --example-hashes | grep -i "SHA"
hashcat --example-hashes | grep -i "NTLM"

# Use hash-identifier (separate tool)
hash-identifier
# Paste hash when prompted

# Hashcat mode numbers (common)
# 0 = MD5
# 100 = SHA1
# 1000 = NTLM
# 1400 = SHA256
# 1800 = sha512crypt
# 3200 = bcrypt
# 5600 = NetNTLMv2
# 13100 = Kerberos 5 TGS-REP
```

### 3. Hash File Preparation

Prepare hash files:

```bash
# Simple hash file (one hash per line)
echo "5f4dcc3b5aa765d61d8327deb882cf99" > hashes.txt

# Hash with username (username:hash format)
cat > hashes.txt <<EOF
admin:5f4dcc3b5aa765d61d8327deb882cf99
user1:098f6bcd4621d373cade4e832627b4f6
EOF

# Hash with salt (hash:salt format for some algorithms)
echo "hash:salt" > hashes.txt

# From /etc/shadow (Linux)
sudo cat /etc/shadow | grep -v "^#" | grep -v ":\*:" | grep -v ":!:" > shadow_hashes.txt

# From NTDS.dit (Active Directory)
secretsdump.py -ntds ntds.dit -system SYSTEM -hashes lmhash:nthash LOCAL > ad_hashes.txt
```

### 4. Attack Modes

Choose appropriate attack mode:

**Dictionary Attack (Mode 0)**:
```bash
# Basic dictionary attack
hashcat -m 0 -a 0 hashes.txt rockyou.txt

# Multiple wordlists
hashcat -m 0 -a 0 hashes.txt wordlist1.txt wordlist2.txt

# With rules
hashcat -m 0 -a 0 hashes.txt rockyou.txt -r rules/best64.rule
```

**Combinator Attack (Mode 1)**:
```bash
# Combine words from two wordlists
hashcat -m 0 -a 1 hashes.txt wordlist1.txt wordlist2.txt
```

**Brute-Force Attack (Mode 3)**:
```bash
# All lowercase letters, 8 characters
hashcat -m 0 -a 3 hashes.txt ?l?l?l?l?l?l?l?l

# Mixed case and numbers, 6 characters
hashcat -m 0 -a 3 hashes.txt ?1?1?1?1?1?1 -1 ?l?u?d

# Custom charset
hashcat -m 0 -a 3 hashes.txt ?1?1?1?1?1?1?1?1 -1 abc123
```

**Mask Attack (Mode 3 with patterns)**:
```bash
# Password format: Uppercase + 6 lowercase + 2 digits
hashcat -m 0 -a 3 hashes.txt ?u?l?l?l?l?l?l?d?d

# Year pattern: word + 4 digits (2019-2024)
hashcat -m 0 -a 3 hashes.txt password?d?d?d?d

# Common patterns
hashcat -m 0 -a 3 hashes.txt ?u?l?l?l?l?l?d?d?s  # Capital + word + numbers + special
```

**Hybrid Attacks (Modes 6 & 7)**:
```bash
# Wordlist + mask (append)
hashcat -m 0 -a 6 hashes.txt wordlist.txt ?d?d?d?d

# Mask + wordlist (prepend)
hashcat -m 0 -a 7 hashes.txt ?d?d?d?d wordlist.txt
```

**Character Sets**:
- `?l` = lowercase (abcdefghijklmnopqrstuvwxyz)
- `?u` = uppercase (ABCDEFGHIJKLMNOPQRSTUVWXYZ)
- `?d` = digits (0123456789)
- `?s` = special characters (!@#$%^&*...)
- `?a` = all characters (l+u+d+s)
- `?b` = all printable ASCII

### 5. Performance Optimization

Optimize cracking performance:

```bash
# Use GPU acceleration
hashcat -m 0 -a 0 hashes.txt wordlist.txt -w 3

# Workload profiles
# -w 1 = Low (desktop usable)
# -w 2 = Default
# -w 3 = High (dedicated cracking)
# -w 4 = Nightmare (max performance)

# Specify GPU device
hashcat -m 0 -a 0 hashes.txt wordlist.txt -d 1

# Show performance benchmark
hashcat -b

# Optimize kernel
hashcat -m 0 -a 0 hashes.txt wordlist.txt -O

# Show estimated time
hashcat -m 0 -a 0 hashes.txt wordlist.txt --runtime=3600
```

### 6. Rules and Mutations

Apply password mutation rules:

```bash
# Use rule file
hashcat -m 0 -a 0 hashes.txt wordlist.txt -r rules/best64.rule

# Multiple rule files
hashcat -m 0 -a 0 hashes.txt wordlist.txt -r rules/best64.rule -r rules/leetspeak.rule

# Common Hashcat rules
# best64.rule - Best 64 rules for speed/coverage
# dive.rule - Deep mutations
# toggles1.rule - Case toggles
# generated2.rule - Complex mutations

# Custom rule examples
# : = do nothing
# l = lowercase all
# u = uppercase all
# c = capitalize first, lowercase rest
# $1 = append "1"
# ^2 = prepend "2"
# sa@ = replace 'a' with '@'
```

### 7. Session Management

Manage cracking sessions:

```bash
# Save session
hashcat -m 0 -a 0 hashes.txt wordlist.txt --session=mysession

# Restore session
hashcat --session=mysession --restore

# Show status
hashcat --session=mysession --status

# Remove session
hashcat --session=mysession --remove

# Auto-checkpoint every 60 seconds
hashcat -m 0 -a 0 hashes.txt wordlist.txt --session=mysession --restore-file-path=/path/to/checkpoint
```

### 8. Results and Reporting

View and export results:

```bash
# Show cracked passwords
hashcat -m 0 hashes.txt --show

# Show only usernames and passwords
hashcat -m 0 hashes.txt --show --username

# Export to file
hashcat -m 0 hashes.txt --show > cracked.txt

# Show cracking statistics
hashcat -m 0 hashes.txt --show --status

# Left side (uncracked hashes)
hashcat -m 0 hashes.txt --left
```

## Security Considerations

### Authorization & Legal Compliance

- **Explicit Authorization**: Written permission required for all password cracking
- **Forensic Chain of Custody**: Maintain evidence integrity
- **Data Protection**: Securely handle cracked passwords
- **Scope Limitation**: Only crack specifically authorized hashes
- **Legal Jurisdiction**: Understand applicable laws (CFAA, GDPR, etc.)

### Operational Security

- **Secure Storage**: Encrypt hash files and results
- **Offline Cracking**: Perform on air-gapped systems when possible
- **Resource Management**: Monitor system resources during cracking
- **Temperature**: Ensure adequate cooling for extended GPU usage
- **Power**: Use surge protection for hardware safety

### Audit Logging

Document all password cracking activities:
- Hash source and acquisition method
- Authorization documentation
- Hash algorithm and attack mode used
- Cracking start and end timestamps
- Success rate and crack time
- Wordlists and rules applied
- Password complexity analysis
- Secure deletion of artifacts

### Compliance

- **MITRE ATT&CK**: T1110 (Brute Force)
  - T1110.002 (Password Cracking)
- **NIST SP 800-63B**: Digital Identity Guidelines for passwords
- **PCI-DSS**: Password security requirements
- **ISO 27001**: A.9.4 Secret authentication information management

## Common Patterns

### Pattern 1: Windows Domain Password Audit

```bash
# Extract NTLM hashes from NTDS.dit
secretsdump.py -ntds ntds.dit -system SYSTEM LOCAL > ad_hashes.txt

# Crack NTLM hashes
hashcat -m 1000 -a 0 ad_hashes.txt rockyou.txt -r rules/best64.rule

# Show cracked Domain Admin accounts
hashcat -m 1000 ad_hashes.txt --show | grep -i "domain admins"
```

### Pattern 2: Linux Password Audit

```bash
# Extract hashes from /etc/shadow
sudo unshadow /etc/passwd /etc/shadow > linux_hashes.txt

# Crack SHA-512 crypt hashes
hashcat -m 1800 -a 0 linux_hashes.txt rockyou.txt

# Analyze password complexity
hashcat -m 1800 linux_hashes.txt --show | awk -F: '{print length($2), $2}'
```

### Pattern 3: Wi-Fi WPA2 Cracking

```bash
# Convert pcap to hashcat format (using cap2hccapx)
cap2hccapx capture.cap wpa.hccapx

# Crack WPA2 handshake
hashcat -m 22000 -a 0 wpa.hccapx rockyou.txt

# With mask attack for numeric passwords
hashcat -m 22000 -a 3 wpa.hccapx ?d?d?d?d?d?d?d?d
```

### Pattern 4: Web Application Hash Cracking

```bash
# Crack MD5 hashes (web app database dump)
hashcat -m 0 -a 0 webapp_hashes.txt rockyou.txt -r rules/best64.rule

# Crack bcrypt hashes (slow but secure)
hashcat -m 3200 -a 0 bcrypt_hashes.txt wordlist.txt -w 3

# SHA256 with salt
hashcat -m 1400 -a 0 salted_hashes.txt wordlist.txt
```

### Pattern 5: Kerberos TGT Cracking (Kerberoasting)

```bash
# Crack Kerberos 5 TGS-REP
hashcat -m 13100 -a 0 kerberos_tickets.txt rockyou.txt -r rules/best64.rule

# Focus on service accounts
hashcat -m 13100 -a 0 kerberos_tickets.txt wordlist.txt --username
```

## Integration Points

### Password Policy Analysis

```bash
#!/bin/bash
# analyze_passwords.sh - Password policy compliance check

CRACKED_FILE="$1"

echo "Password Length Distribution:"
awk -F: '{print length($2)}' "$CRACKED_FILE" | sort -n | uniq -c

echo -e "\nPasswords with Dictionary Words:"
grep -f /usr/share/dict/words "$CRACKED_FILE" | wc -l

echo -e "\nPasswords without Special Characters:"
grep -v "[!@#$%^&*]" "$CRACKED_FILE" | wc -l

echo -e "\nCommon Password Patterns:"
grep -E "^password|123456|qwerty" "$CRACKED_FILE" | wc -l
```

### Reporting

```bash
# Generate password audit report
cat > audit_report.sh <<'EOF'
#!/bin/bash
TOTAL=$(wc -l < hashes.txt)
CRACKED=$(hashcat -m 1000 hashes.txt --show | wc -l)
PERCENT=$((CRACKED * 100 / TOTAL))

echo "Password Audit Report"
echo "===================="
echo "Total Hashes: $TOTAL"
echo "Cracked: $CRACKED"
echo "Success Rate: $PERCENT%"
echo ""
echo "Recommendations:"
echo "- Implement minimum password length of 12 characters"
echo "- Require complex passwords (upper, lower, digit, special)"
echo "- Enable multi-factor authentication"
echo "- Implement password history and rotation"
EOF
chmod +x audit_report.sh
```

## Troubleshooting

### Issue: Slow Cracking Speed

**Solutions**:
```bash
# Use optimized kernel
hashcat -m 0 -a 0 hashes.txt wordlist.txt -O

# Increase workload
hashcat -m 0 -a 0 hashes.txt wordlist.txt -w 3

# Check GPU utilization
hashcat -m 0 -a 0 hashes.txt wordlist.txt --status

# Verify GPU drivers
nvidia-smi  # For NVIDIA
rocm-smi    # For AMD
```

### Issue: Out of Memory

**Solutions**:
```bash
# Reduce wordlist size
head -n 1000000 large_wordlist.txt > smaller_wordlist.txt

# Disable optimizations
hashcat -m 0 -a 0 hashes.txt wordlist.txt (remove -O flag)

# Split hash file
split -l 1000 hashes.txt hash_chunk_
```

### Issue: Hash Format Errors

**Solutions**:
- Verify hash mode (-m) matches hash type
- Check hash file format (remove extra spaces, newlines)
- Ensure proper salt format for salted hashes
- Use --username flag if hashes include usernames

## Defensive Considerations

Protect against password cracking:

**Strong Password Policies**:
- Minimum length: 12+ characters
- Complexity requirements (mixed case, numbers, special)
- Prohibit common passwords
- Implement password history
- Regular password rotation for privileged accounts

**Technical Controls**:
- Use strong hashing algorithms (bcrypt, scrypt, Argon2)
- Implement salting and key stretching
- Use adaptive hash functions
- Enable multi-factor authentication
- Implement account lockout policies
- Monitor for brute-force attempts

**Hash Storage Best Practices**:
- Never store plaintext passwords
- Use strong, modern hashing algorithms
- Implement per-password unique salts
- Use appropriate iteration counts (bcrypt cost, PBKDF2 rounds)
- Regularly update hashing parameters

## References

- [Hashcat Official Wiki](https://hashcat.net/wiki/)
- [Hashcat Documentation](https://hashcat.net/hashcat/)
- [MITRE ATT&CK: Brute Force](https://attack.mitre.org/techniques/T1110/)
- [NIST SP 800-63B: Digital Identity Guidelines](https://pages.nist.gov/800-63-3/sp800-63b.html)
- [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
