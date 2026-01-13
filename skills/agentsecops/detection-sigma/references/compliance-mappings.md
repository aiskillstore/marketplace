# Compliance Framework Mappings for Sigma Detection Rules

## PCI-DSS v3.2.1

### Requirement 10.2 - Implement automated audit trails

#### 10.2.1 - Access to cardholder data

**Detection Requirements**: Monitor all access to cardholder data environments

**Sigma Tags**: `pci-dss.10.2.1`

**Example Rules**:
- File access to cardholder data locations
- Database queries accessing payment card fields
- Application logs showing cardholder data retrieval

```yaml
tags:
    - pci-dss.10.2.1
logsource:
    category: file_event
detection:
    selection:
        TargetFilename|contains: '\cardholder-data\'
```

#### 10.2.2 - All actions taken by any individual with root or administrative privileges

**Sigma Tags**: `pci-dss.10.2.2`

**Example Rules**:
- Privileged account usage
- sudo/runas commands
- Administrative actions on critical systems

```yaml
tags:
    - pci-dss.10.2.2
logsource:
    category: process_creation
detection:
    selection:
        User|contains: 'admin'
```

#### 10.2.4 - Invalid logical access attempts

**Sigma Tags**: `pci-dss.10.2.4`

**Example Rules**:
- Failed authentication attempts
- Account lockouts
- Access denied events

```yaml
tags:
    - pci-dss.10.2.4
logsource:
    category: authentication
detection:
    selection:
        EventID: 4625  # Failed logon
```

#### 10.2.5 - Use of identification and authentication mechanisms

**Sigma Tags**: `pci-dss.10.2.5`

**Example Rules**:
- Account creation/deletion/modification
- Password changes
- Multi-factor authentication events

```yaml
tags:
    - pci-dss.10.2.5
logsource:
    category: authentication
detection:
    selection:
        EventID:
            - 4720  # Account created
            - 4724  # Password reset
```

#### 10.2.7 - Creation and deletion of system-level objects

**Sigma Tags**: `pci-dss.10.2.7`

**Example Rules**:
- System service creation
- Scheduled task creation
- New user account creation

```yaml
tags:
    - pci-dss.10.2.7
logsource:
    category: process_creation
detection:
    selection:
        Image|endswith: '\sc.exe'
        CommandLine|contains: 'create'
```

## NIST SP 800-53 Rev. 5

### AU-2 - Event Logging

**Controls**: Organization defines auditable events

**Sigma Tags**: `nist-800-53.au-2`

**Coverage**:
- Security-relevant events
- Success and failure of events
- Actions by privileged users

### AU-3 - Content of Audit Records

**Controls**: Audit records contain sufficient information

**Sigma Tags**: `nist-800-53.au-3`

**Required Fields**:
- Event type, date/time, outcome
- Subject identity, object identity
- Data source

### AU-6 - Audit Review, Analysis, and Reporting

**Controls**: Review and analyze audit records

**Sigma Tags**: `nist-800-53.au-6`

**Detection Focus**:
- Automated scanning for anomalies
- Correlation of audit records
- Investigation and reporting

### AU-12 - Audit Generation

**Controls**: System provides audit record generation

**Sigma Tags**: `nist-800-53.au-12`

**Coverage**:
- Generate audit records for defined events
- Allow authorized users to select auditable events
- Privileged commands

### SI-4 - System Monitoring

**Controls**: Monitor the system to detect attacks and indicators

**Sigma Tags**: `nist-800-53.si-4`

**Detection Coverage**:
- Unauthorized access attempts
- Unauthorized use of privileges
- Malicious code detection

```yaml
tags:
    - nist-800-53.si-4
    - nist-800-53.au-12
logsource:
    category: process_creation
detection:
    selection:
        CommandLine|contains: 'mimikatz'
```

### AC-2 - Account Management

**Controls**: Account creation, modification, removal

**Sigma Tags**: `nist-800-53.ac-2`

**Example Rules**:
- Account lifecycle events
- Privileged account monitoring
- Account attribute changes

### IA-2 - Identification and Authentication

**Controls**: Uniquely identify and authenticate users

**Sigma Tags**: `nist-800-53.ia-2`

**Example Rules**:
- Multi-factor authentication
- Authentication failures
- Session management

## ISO/IEC 27001:2013

### A.12.4.1 - Event logging

**Control**: Event logs recording user activities, exceptions, and security events

**Sigma Tags**: `iso27001.a.12.4.1`

**Requirements**:
- User IDs
- System activities
- Date, time, and details of key events
- Device identity or location
- Records of successful and rejected system access attempts

```yaml
tags:
    - iso27001.a.12.4.1
logsource:
    category: authentication
detection:
    selection:
        EventID:
            - 4624  # Successful logon
            - 4625  # Failed logon
```

### A.12.4.2 - Protection of log information

**Control**: Logging facilities and log information protected

**Sigma Tags**: `iso27001.a.12.4.2`

**Detection Focus**:
- Unauthorized access to logs
- Log deletion or modification
- Log integrity violations

### A.12.4.3 - Administrator and operator logs

**Control**: System administrator and operator activities logged

**Sigma Tags**: `iso27001.a.12.4.3`

**Example Rules**:
- Privileged command execution
- System configuration changes
- Administrative access

```yaml
tags:
    - iso27001.a.12.4.3
logsource:
    category: process_creation
detection:
    selection:
        User|contains:
            - 'admin'
            - 'root'
```

### A.9.2.1 - User registration and de-registration

**Control**: Account management processes

**Sigma Tags**: `iso27001.a.9.2.1`

**Example Rules**:
- Account creation
- Account deletion
- Account modification

### A.9.4.1 - Information access restriction

**Control**: Access to information and systems restricted

**Sigma Tags**: `iso27001.a.9.4.1`

**Detection Focus**:
- Unauthorized access attempts
- Privilege escalation
- Access control violations

## SOC 2 Trust Service Criteria

### CC6.1 - Logical and Physical Access Controls

**Criteria**: Restrict access to authorized users

**Detection Coverage**:
- Authentication monitoring
- Authorization violations
- Privileged access usage

### CC7.2 - System Monitoring

**Criteria**: Monitor system components

**Detection Coverage**:
- Security event monitoring
- Anomaly detection
- Threat detection

### CC7.3 - Evaluation and Response

**Criteria**: Evaluate events and respond

**Detection Focus**:
- Security incident detection
- Alert generation and escalation
- Response actions

## Tag Format

Use this format for compliance tags:

```yaml
tags:
    - {framework}.{control-id}
```

**Examples**:
```yaml
tags:
    - pci-dss.10.2.5
    - nist-800-53.au-2
    - iso27001.a.12.4.1
```

## Multi-Framework Mapping

Rules can map to multiple frameworks:

```yaml
title: Failed Authentication Monitoring
tags:
    - attack.credential_access
    - attack.t1110
    - pci-dss.10.2.4
    - pci-dss.10.2.5
    - nist-800-53.au-2
    - nist-800-53.au-12
    - nist-800-53.ia-2
    - iso27001.a.12.4.1
    - iso27001.a.9.2.1
```

## Compliance Coverage Analysis

Use `compliance_coverage.py` script to analyze rule coverage:

```bash
# Analyze PCI-DSS coverage
python scripts/compliance_coverage.py --directory rules/ --framework pci-dss

# Generate coverage report
python scripts/compliance_coverage.py --directory rules/ --framework nist-800-53 --report coverage.md
```

## Resources

- [PCI DSS v3.2.1](https://www.pcisecuritystandards.org/)
- [NIST SP 800-53 Rev. 5](https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final)
- [ISO/IEC 27001:2013](https://www.iso.org/standard/54534.html)
- [SOC 2 Trust Service Criteria](https://www.aicpa.org/interestareas/frc/assuranceadvisoryservices/trust-services-criteria)
