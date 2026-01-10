---
name: detection-sigma
description: >
  Generic detection rule creation and management using Sigma, the universal SIEM rule format.
  Sigma provides vendor-agnostic detection logic for log analysis across multiple SIEM platforms.
  Use when: (1) Creating detection rules for security monitoring, (2) Converting rules between
  SIEM platforms (Splunk, Elastic, QRadar, Sentinel), (3) Threat hunting with standardized
  detection patterns, (4) Building detection-as-code pipelines, (5) Mapping detections to
  MITRE ATT&CK tactics, (6) Implementing compliance-based monitoring rules.
version: 0.1.0
maintainer: SirAppSec
category: incident-response
tags: [sigma, detection, siem, threat-hunting, mitre-attack, detection-engineering, log-analysis]
frameworks: [MITRE-ATT&CK, NIST, ISO27001]
dependencies:
  python: ">=3.8"
  packages: [pysigma, pysigma-backend-splunk, pysigma-backend-elasticsearch, pyyaml]
references:
  - https://github.com/SigmaHQ/sigma
  - https://github.com/SigmaHQ/pySigma
  - https://sigmahq.io/
---

# Sigma Detection Engineering

## Overview

Sigma is to log detection what Snort is to network traffic and YARA is to files - a universal signature format for describing security-relevant log events. This skill helps create, validate, and convert Sigma rules for deployment across multiple SIEM platforms, enabling detection-as-code workflows.

**Core capabilities**:
- Create detection rules using Sigma format
- Convert rules to 25+ SIEM/EDR backends (Splunk, Elastic, QRadar, Sentinel, etc.)
- Validate rule syntax and logic
- Map detections to MITRE ATT&CK framework
- Build threat hunting queries
- Implement compliance-based monitoring

## Quick Start

### Install Dependencies

```bash
pip install pysigma pysigma-backend-splunk pysigma-backend-elasticsearch pyyaml
```

### Create a Basic Sigma Rule

```yaml
title: Suspicious PowerShell Execution
id: 7d6d30b8-5b91-4b90-a71e-4f5a3f5a3c3f
status: experimental
description: Detects suspicious PowerShell execution with encoded commands
references:
    - https://attack.mitre.org/techniques/T1059/001/
author: Your Name
date: YYYY/MM/DD
modified: YYYY/MM/DD
tags:
    - attack.execution
    - attack.t1059.001
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        Image|endswith: '\powershell.exe'
        CommandLine|contains:
            - '-enc'
            - '-EncodedCommand'
            - 'FromBase64String'
    condition: selection
falsepositives:
    - Legitimate administrative scripts
level: medium
```

### Convert Rule to Target SIEM

```bash
# Convert to Splunk
python scripts/sigma_convert.py rule.yml --backend splunk

# Convert to Elasticsearch
python scripts/sigma_convert.py rule.yml --backend elasticsearch

# Convert to Microsoft Sentinel
python scripts/sigma_convert.py rule.yml --backend sentinel
```

## Core Workflows

### Workflow 1: Detection Rule Development

Progress:
[ ] 1. Identify detection requirement from threat intelligence or compliance
[ ] 2. Research log sources and field mappings for target environment
[ ] 3. Create Sigma rule using standard template
[ ] 4. Validate rule syntax: `python scripts/sigma_validate.py rule.yml`
[ ] 5. Test rule against sample logs or historical data
[ ] 6. Convert to target SIEM format
[ ] 7. Deploy and tune based on false positive rate
[ ] 8. Document rule metadata and MITRE ATT&CK mapping

Work through each step systematically. Check off completed items.

### Workflow 2: Threat Hunting Rule Creation

For proactive threat hunting based on TTPs:

1. **Select MITRE ATT&CK Technique**
   - Review threat intelligence for relevant TTPs
   - Identify technique ID (e.g., T1059.001 - PowerShell)
   - See [references/mitre-attack-mapping.md](references/mitre-attack-mapping.md) for common techniques

2. **Identify Log Sources**
   - Determine which logs capture the technique
   - Map log source categories (process_creation, network_connection, file_event)
   - Verify log source availability in your environment

3. **Define Detection Logic**
   - Create selection criteria matching suspicious patterns
   - Add filters to reduce false positives
   - Use field modifiers for robust matching (endswith, contains, re)

4. **Validate and Test**
   - Run validation: `python scripts/sigma_validate.py hunting-rule.yml`
   - Test against known-good and known-bad samples
   - Tune detection logic based on results

5. **Document and Deploy**
   - Add references to threat reports
   - Document false positive scenarios
   - Convert and deploy to production SIEM

### Workflow 3: Bulk Rule Conversion

When migrating between SIEM platforms:

```bash
# Validate all rules first
python scripts/sigma_validate.py --directory rules/ --report validation-report.json

# Convert entire rule set
python scripts/sigma_convert.py --directory rules/ --backend splunk --output converted/

# Generate deployment report
python scripts/sigma_convert.py --directory rules/ --backend splunk --report conversion-report.md
```

Review conversion report for:
- Successfully converted rules
- Rules requiring manual adjustment
- Unsupported field mappings
- Backend-specific limitations

### Workflow 4: Compliance-Based Detection

For implementing compliance monitoring (PCI-DSS, NIST, ISO 27001):

1. **Map Requirements to Detections**
   - Identify compliance control requirements
   - Determine required log monitoring
   - See [references/compliance-mappings.md](references/compliance-mappings.md)

2. **Create Detection Rules**
   - Use compliance rule templates from `assets/compliance-rules/`
   - Tag rules with compliance framework (e.g., tags: [pci-dss.10.2.5])
   - Set appropriate severity levels

3. **Validate Coverage**
   - Run: `python scripts/compliance_coverage.py --framework pci-dss`
   - Review coverage gaps
   - Create additional rules as needed

4. **Generate Compliance Report**
   - Document detection coverage by control
   - Include sample queries and expected alerts
   - Maintain audit trail for compliance evidence

## Rule Structure Reference

### Required Fields

```yaml
title: Human-readable rule name
id: UUID (generate with: python -c "import uuid; print(uuid.uuid4())")
status: stable|test|experimental|deprecated
description: Detailed description of what this detects
author: Your Name
date: YYYY/MM/DD
modified: YYYY/MM/DD
logsource:
    category: process_creation|network_connection|file_event|...
    product: windows|linux|macos|azure|aws|...
detection:
    selection:
        FieldName: value
    condition: selection
level: informational|low|medium|high|critical
```

### Optional Fields

```yaml
references:
    - https://attack.mitre.org/techniques/T1059/
tags:
    - attack.execution
    - attack.t1059.001
falsepositives:
    - Legitimate use cases
fields:
    - CommandLine
    - User
    - ParentImage
```

### Detection Conditions

```yaml
# Simple selection
detection:
    selection:
        Field: value
    condition: selection

# Multiple conditions (AND)
detection:
    selection:
        Field1: value1
        Field2: value2
    condition: selection

# OR conditions
detection:
    selection1:
        Field: value1
    selection2:
        Field: value2
    condition: selection1 or selection2

# NOT conditions
detection:
    selection:
        Field: suspicious_value
    filter:
        Field: legitimate_value
    condition: selection and not filter

# Complex logic
detection:
    selection:
        EventID: 4688
    suspicious_cmd:
        CommandLine|contains:
            - 'powershell'
            - 'cmd.exe'
    filter_legitimate:
        ParentImage|endswith: '\explorer.exe'
    condition: selection and suspicious_cmd and not filter_legitimate
```

### Field Modifiers

Common modifiers for flexible matching:

- `|contains` - Contains substring (case-insensitive)
- `|endswith` - Ends with string
- `|startswith` - Starts with string
- `|re` - Regular expression match
- `|all` - All values must match
- `|base64` - Base64-encoded value matching
- `|base64offset` - Base64 with offset variations

Example:
```yaml
detection:
    selection:
        CommandLine|contains|all:
            - 'powershell'
            - '-enc'
        Image|endswith: '\powershell.exe'
```

## Security Considerations

- **Sensitive Data Handling**: Sigma rules may reference sensitive field names or patterns. Store rules in version control with appropriate access controls. Avoid including actual sensitive data in example values.

- **Access Control**: Detection rules reveal defensive capabilities to adversaries. Implement role-based access for rule repositories. Limit rule modification to authorized detection engineers.

- **Audit Logging**: Log all rule deployments, modifications, and deletions. Track who deployed which rules to which systems. Maintain change history for compliance auditing.

- **Compliance**: Sigma rules support compliance monitoring (PCI-DSS 10.2, NIST SP 800-53 AU family, ISO 27001 A.12.4). Document rule-to-control mappings for audit evidence.

- **Safe Defaults**: Use conservative false positive filtering in production. Start rules at "experimental" status. Test thoroughly in test environment before production deployment.

## Bundled Resources

### Scripts

- `scripts/sigma_convert.py` - Convert Sigma rules to target SIEM backend formats
- `scripts/sigma_validate.py` - Validate Sigma rule syntax and detect common errors
- `scripts/compliance_coverage.py` - Analyze detection coverage for compliance frameworks
- `scripts/generate_rule_template.py` - Generate Sigma rule template with MITRE ATT&CK tags

### References

- `references/mitre-attack-mapping.md` - Common MITRE ATT&CK techniques and Sigma detection patterns
- `references/log-source-guide.md` - Log source categories, products, and field mappings
- `references/compliance-mappings.md` - Compliance framework to detection rule mappings
- `references/backend-support.md` - Supported SIEM backends and conversion capabilities
- `references/field-modifiers.md` - Comprehensive guide to Sigma field modifiers and regex patterns

### Assets

- `assets/rule-templates/` - Pre-built Sigma rule templates for common attack patterns
  - `lateral-movement.yml` - Lateral movement detection template
  - `privilege-escalation.yml` - Privilege escalation detection template
  - `persistence.yml` - Persistence mechanism detection template
  - `credential-access.yml` - Credential dumping detection template

- `assets/compliance-rules/` - Compliance-focused rule templates
  - `pci-dss-monitoring.yml` - PCI-DSS monitoring requirements
  - `nist-800-53-audit.yml` - NIST 800-53 audit logging requirements
  - `iso27001-logging.yml` - ISO 27001 logging and monitoring

## Common Detection Patterns

### Pattern 1: Process Execution Monitoring

Detect suspicious process creation with command-line analysis:

```yaml
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        Image|endswith:
            - '\powershell.exe'
            - '\cmd.exe'
        CommandLine|contains:
            - 'Invoke-'
            - 'IEX'
            - 'FromBase64String'
```

### Pattern 2: Network Connection Monitoring

Detect suspicious outbound connections:

```yaml
logsource:
    category: network_connection
    product: windows
detection:
    selection:
        Initiated: 'true'
        DestinationPort:
            - 4444
            - 5555
            - 8080
    filter:
        DestinationIp|startswith:
            - '10.'
            - '172.16.'
            - '192.168.'
    condition: selection and not filter
```

### Pattern 3: File Event Monitoring

Detect file creation in suspicious locations:

```yaml
logsource:
    category: file_event
    product: windows
detection:
    selection:
        TargetFilename|contains:
            - '\Windows\Temp\'
            - '\AppData\Roaming\'
        TargetFilename|endswith:
            - '.exe'
            - '.dll'
            - '.ps1'
```

## Integration Points

### CI/CD Integration

Build detection-as-code pipelines:

```yaml
# .github/workflows/sigma-validation.yml
name: Sigma Rule Validation
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Validate Sigma Rules
        run: |
          pip install pysigma
          python scripts/sigma_validate.py --directory rules/
      - name: Convert to Production Format
        run: |
          python scripts/sigma_convert.py --directory rules/ --backend splunk --output converted/
```

### SIEM Deployment

Automated rule deployment:
- Splunk: Use Splunk REST API or `splunk-sdk` for savedsearches
- Elasticsearch: Convert to EQL and deploy via Kibana API
- Microsoft Sentinel: Convert to KQL and deploy via Azure API
- QRadar: Convert to AQL and deploy via QRadar API

See [references/backend-support.md](references/backend-support.md) for deployment examples.

### Threat Intelligence Integration

Enrich rules with threat intel:
- Tag rules with threat actor TTPs
- Reference threat reports and IOCs
- Map to MITRE ATT&CK techniques
- Track rule effectiveness against known threats

## Troubleshooting

### Issue: Conversion Fails for Specific Backend

**Solution**: Check backend compatibility and field mappings. Some backends have limitations:
- Review `references/backend-support.md` for known limitations
- Use `sigma_convert.py --backend <backend> --debug` for detailed error output
- Check if field names are supported in target backend
- Consider custom pipeline transformations for unsupported fields

### Issue: High False Positive Rate

**Solution**: Refine detection logic with additional filters:
1. Review false positive patterns
2. Add exclusion filters for legitimate use cases
3. Use more specific field modifiers (e.g., `|endswith` vs `|contains`)
4. Consider time-based correlation for behavioral detection
5. Test with historical data to validate tuning

### Issue: Rule Not Triggering in Target SIEM

**Solution**: Verify log source availability and field mappings:
1. Confirm log source is ingested: Check SIEM data sources
2. Verify field names match: Use `sigma_convert.py --show-fields` to see mapping
3. Test converted query directly in SIEM
4. Check for case sensitivity issues in field values
5. Validate time window and search scope in SIEM

## MITRE ATT&CK Integration

Tag rules with ATT&CK tactics and techniques:

```yaml
tags:
    - attack.execution           # Tactic
    - attack.t1059.001          # Technique: PowerShell
    - attack.defense_evasion    # Additional tactic
    - attack.t1027              # Technique: Obfuscated Files
```

Common tactic tags:
- `attack.initial_access`
- `attack.execution`
- `attack.persistence`
- `attack.privilege_escalation`
- `attack.defense_evasion`
- `attack.credential_access`
- `attack.discovery`
- `attack.lateral_movement`
- `attack.collection`
- `attack.exfiltration`
- `attack.command_and_control`
- `attack.impact`

For detailed technique mappings, see [references/mitre-attack-mapping.md](references/mitre-attack-mapping.md).

## Best Practices

1. **Start with Community Rules**: Use SigmaHQ repository (3000+ peer-reviewed rules) as foundation
2. **Version Control**: Store rules in Git with meaningful commit messages
3. **Test Before Deploy**: Validate against historical data in test environment
4. **Document Tuning**: Track false positive patterns and tuning decisions
5. **Map to Frameworks**: Tag all rules with MITRE ATT&CK and compliance mappings
6. **Automate Validation**: Use CI/CD to validate rules on every change
7. **Monitor Effectiveness**: Track rule trigger rates and true positive rates
8. **Regular Updates**: Review and update rules based on new threat intelligence

## References

- [Sigma Specification](https://github.com/SigmaHQ/sigma-specification)
- [SigmaHQ Rule Repository](https://github.com/SigmaHQ/sigma/tree/master/rules)
- [pySigma Documentation](https://github.com/SigmaHQ/pySigma)
- [Sigma Converter Web Tool](https://sigconverter.io/)
- [MITRE ATT&CK Framework](https://attack.mitre.org/)
