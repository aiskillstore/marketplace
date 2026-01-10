# License Compliance Risk Assessment Guide

## Table of Contents
- [License Risk Categories](#license-risk-categories)
- [Common Open Source Licenses](#common-open-source-licenses)
- [License Compatibility](#license-compatibility)
- [Compliance Workflows](#compliance-workflows)
- [Legal Considerations](#legal-considerations)

## License Risk Categories

### High Risk - Copyleft (Strong)

**Licenses**: GPL-2.0, GPL-3.0, AGPL-3.0

**Characteristics**:
- Requires derivative works to be open-sourced under same license
- Source code distribution mandatory
- AGPL extends to network use (SaaS applications)

**Business Impact**: HIGH
- May require releasing proprietary code as open source
- Incompatible with most commercial software
- Legal review required for any usage

**Use Cases Where Allowed**:
- Internal tools (not distributed)
- Separate services with network boundaries
- Dual-licensed components (use commercial license)

**Example Compliance Violation**:
```
Product: Commercial SaaS Application
Dependency: GPL-licensed library linked into application
Issue: AGPL requires source code release for network-accessible software
Risk: Legal liability, forced open-sourcing
```

### Medium Risk - Weak Copyleft

**Licenses**: LGPL-2.1, LGPL-3.0, MPL-2.0, EPL-2.0

**Characteristics**:
- Copyleft applies only to modified library files
- Allows proprietary applications if library used as separate component
- Source modifications must be released

**Business Impact**: MEDIUM
- Safe if used as unmodified library (dynamic linking)
- Modifications require open-sourcing
- License compatibility considerations

**Compliance Requirements**:
- Keep library as separate, unmodified component
- If modified, release modifications under same license
- Attribute properly in documentation

**Example Safe Usage**:
```
Product: Commercial Application
Dependency: LGPL library via dynamic linking
Status: COMPLIANT
Reason: No modifications, used as separate component
```

### Low Risk - Permissive

**Licenses**: MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause

**Characteristics**:
- Minimal restrictions on use and distribution
- No copyleft requirements
- Attribution required
- Apache-2.0 includes patent grant

**Business Impact**: LOW
- Generally safe for commercial use
- Simple compliance requirements
- Industry standard for most projects

**Compliance Requirements**:
- Include license text in distribution
- Preserve copyright notices
- Apache-2.0: Include NOTICE file if present

### Minimal Risk - Public Domain / Unlicense

**Licenses**: CC0-1.0, Unlicense, Public Domain

**Characteristics**:
- No restrictions
- No attribution required (though recommended)

**Business Impact**: MINIMAL
- Safest for commercial use
- No compliance obligations

## Common Open Source Licenses

### Permissive Licenses

#### MIT License

**SPDX**: MIT
**OSI Approved**: Yes
**Risk Level**: LOW

**Permissions**: Commercial use, modification, distribution, private use
**Conditions**: Include license and copyright notice
**Limitations**: No liability, no warranty

**Common in**: JavaScript (React, Angular), Ruby (Rails)

**Compliance Checklist**:
- [ ] Include LICENSE file in distribution
- [ ] Preserve copyright notices in source files
- [ ] Credit in ABOUT/CREDITS file

#### Apache License 2.0

**SPDX**: Apache-2.0
**OSI Approved**: Yes
**Risk Level**: LOW

**Permissions**: Same as MIT, plus explicit patent grant
**Conditions**: Include license, preserve NOTICE file, state changes
**Limitations**: No trademark use, no liability

**Common in**: Java (Spring), Big Data (Hadoop, Kafka)

**Key Difference from MIT**: Patent protection clause

**Compliance Checklist**:
- [ ] Include LICENSE file
- [ ] Include NOTICE file if present
- [ ] Document modifications
- [ ] Don't use project trademarks

#### BSD Licenses (2-Clause and 3-Clause)

**SPDX**: BSD-2-Clause, BSD-3-Clause
**OSI Approved**: Yes
**Risk Level**: LOW

**3-Clause Addition**: No endorsement using project name

**Common in**: Unix utilities, networking libraries

**Compliance Checklist**:
- [ ] Include license text
- [ ] Preserve copyright notices
- [ ] BSD-3: No unauthorized endorsements

### Weak Copyleft Licenses

#### GNU LGPL 2.1 / 3.0

**SPDX**: LGPL-2.1, LGPL-3.0
**OSI Approved**: Yes
**Risk Level**: MEDIUM

**Safe Usage Patterns**:
1. **Dynamic Linking**: Link as shared library without modification
2. **Unmodified Use**: Use library as-is without code changes
3. **Separate Component**: Keep as distinct, replaceable module

**Unsafe Usage Patterns**:
1. **Static Linking**: Compiling LGPL code into proprietary binary
2. **Modifications**: Changing LGPL library code
3. **Intimate Integration**: Tightly coupling with proprietary code

**Common in**: GTK, glibc, Qt (dual-licensed)

**Compliance for Unmodified Use**:
- [ ] Provide library source code or offer to provide
- [ ] Allow users to replace library
- [ ] Include license text

**Compliance for Modifications**:
- [ ] Release modifications under LGPL
- [ ] Provide modified source code
- [ ] Document changes

#### Mozilla Public License 2.0

**SPDX**: MPL-2.0
**OSI Approved**: Yes
**Risk Level**: MEDIUM

**File-Level Copyleft**: Only modified files must remain MPL

**Common in**: Firefox, Rust standard library

**Compliance**:
- [ ] Keep MPL files in separate files
- [ ] Release modifications to MPL files
- [ ] May combine with proprietary code at module level

### Strong Copyleft Licenses

#### GNU GPL 2.0 / 3.0

**SPDX**: GPL-2.0, GPL-3.0
**OSI Approved**: Yes
**Risk Level**: HIGH

**Copyleft Scope**: Entire program must be GPL

**Key Differences**:
- **GPL-3.0**: Added anti-tivoization, patent provisions
- **GPL-2.0**: More permissive for hardware restrictions

**Common in**: Linux kernel (GPL-2.0), many GNU tools

**When GPL is Acceptable**:
1. **Internal Use**: Not distributed outside organization
2. **Network Boundary**: Separate GPL service (API-based)
3. **Dual-Licensed**: Use commercial license option

**Compliance if Using**:
- [ ] Entire program must be GPL-compatible
- [ ] Provide source code to recipients
- [ ] Include license and build instructions

#### GNU AGPL 3.0

**SPDX**: AGPL-3.0
**OSI Approved**: Yes
**Risk Level**: CRITICAL for SaaS

**Network Copyleft**: Source code required even for network use

**Common in**: Some database tools, server software

**Critical for**: SaaS, web applications, APIs

**Avoid Unless**: Prepared to open-source entire application

### Proprietary / Commercial Licenses

**Risk Level**: VARIES (requires legal review)

**Common Scenarios**:
- Evaluation/trial licenses (non-production)
- Dual-licensed (commercial option available)
- Runtime licenses (e.g., database drivers)

**Compliance**: Follow vendor-specific terms

## License Compatibility

### Compatibility Matrix

| Your Project | MIT | Apache-2.0 | LGPL | GPL | AGPL |
|--------------|-----|-----------|------|-----|------|
| Proprietary  | ✅  | ✅        | ⚠️   | ❌  | ❌   |
| MIT          | ✅  | ✅        | ⚠️   | ❌  | ❌   |
| Apache-2.0   | ✅  | ✅        | ⚠️   | ⚠️  | ❌   |
| LGPL         | ✅  | ✅        | ✅   | ⚠️  | ❌   |
| GPL          | ✅  | ⚠️        | ✅   | ✅  | ⚠️   |
| AGPL         | ✅  | ⚠️        | ✅   | ✅  | ✅   |

**Legend**:
- ✅ Compatible
- ⚠️ Compatible with conditions
- ❌ Incompatible

### Common Incompatibilities

**Apache-2.0 with GPL-2.0**:
- Issue: GPL-2.0 doesn't have explicit patent grant
- Solution: Use GPL-3.0 instead (compatible with Apache-2.0)

**GPL with Proprietary**:
- Issue: GPL requires derivative works be GPL
- Solution: Keep as separate program, use network boundary

**AGPL with SaaS**:
- Issue: AGPL triggers on network use
- Solution: Avoid AGPL or use commercial license

## Compliance Workflows

### Initial License Assessment

1. **Scan Dependencies**
   ```bash
   scripts/blackduck_scan.py --project MyApp --version 1.0.0 --report-type license
   ```

2. **Categorize Licenses by Risk**
   - Review all HIGH risk licenses immediately
   - Assess MEDIUM risk licenses for compliance requirements
   - Document LOW risk licenses for attribution

3. **Legal Review**
   - Escalate HIGH risk licenses to legal team
   - Get approval for MEDIUM risk usage patterns
   - Document decisions

### Continuous License Monitoring

**In CI/CD Pipeline**:
```yaml
# GitHub Actions example
- name: License Compliance Check
  run: |
    scripts/blackduck_scan.py \
      --project ${{ github.repository }} \
      --version ${{ github.sha }} \
      --report-type license \
      --fail-on-blocklisted-licenses
```

**Policy Enforcement**:
- Block builds with GPL/AGPL dependencies
- Require approval for new LGPL dependencies
- Auto-approve MIT/Apache-2.0

### License Remediation

**For High-Risk Licenses**:

1. **Replace Component**
   - Find MIT/Apache alternative
   - Example: MySQL (GPL) → PostgreSQL (PostgreSQL License - permissive)

2. **Commercial License**
   - Purchase commercial license if available
   - Example: Qt (LGPL or Commercial)

3. **Separate Service**
   - Run GPL component as separate service
   - Communicate via API/network

4. **Remove Dependency**
   - Implement functionality directly
   - Use different approach

### Attribution and Notices

**Required Artifacts**:

**LICENSES.txt** - All license texts:
```
This software includes the following third-party components:

1. Component Name v1.0.0
   License: MIT
   Copyright (c) 2024 Author
   [Full license text]

2. Another Component v2.0.0
   License: Apache-2.0
   [Full license text]
```

**NOTICE.txt** - Attribution notices (if Apache-2.0 dependencies):
```
This product includes software developed by
The Apache Software Foundation (http://www.apache.org/).

[Additional NOTICE content from Apache-licensed dependencies]
```

**UI/About Screen**:
- List major third-party components
- Link to full license information
- Provide "Open Source Licenses" section

## Legal Considerations

### When to Consult Legal Counsel

**Always Consult for**:
- GPL/AGPL in commercial products
- Dual-licensing decisions
- Patent-related concerns
- Proprietary license negotiations
- M&A due diligence
- License violations/disputes

### Common Legal Questions

**Q: Can I use GPL code in a SaaS application?**
A: GPL-2.0/3.0 yes (no distribution), AGPL-3.0 no (network use triggers copyleft)

**Q: What if I modify an MIT-licensed library?**
A: You can keep modifications proprietary, just preserve MIT license

**Q: Can I remove license headers from code?**
A: No, preserve all copyright and license notices

**Q: What's the difference between "linking" and "use"?**
A: Legal concept varies by jurisdiction; consult attorney for specific cases

### Audit and Compliance Documentation

**Maintain Records**:
- Complete SBOM with license information
- License review approvals
- Component selection rationale
- Exception approvals with expiration dates

**Quarterly Review**:
- Update license inventory
- Review new dependencies
- Renew/revoke exceptions
- Update attribution files

## Tools and Resources

**Black Duck Features**:
- Automated license detection
- License risk categorization
- Policy enforcement
- Bill of Materials with licenses

**Additional Tools**:
- FOSSA - License compliance automation
- WhiteSource - License management
- Snyk - License scanning

**Resources**:
- [SPDX License List](https://spdx.org/licenses/)
- [Choose A License](https://choosealicense.com/)
- [TL;DR Legal](https://tldrlegal.com/)
- [OSI Approved Licenses](https://opensource.org/licenses)

## License Risk Scorecard Template

```markdown
# License Risk Assessment: [Component Name]

**Component**: component-name@version
**License**: [SPDX ID]
**Risk Level**: [HIGH/MEDIUM/LOW]

## Usage Context
- [ ] Used in distributed product
- [ ] Used in SaaS/cloud service
- [ ] Internal tool only
- [ ] Modifications made: [Yes/No]

## Risk Assessment
- **Copyleft Trigger**: [Yes/No/Conditional]
- **Patent Concerns**: [Yes/No]
- **Commercial Use Allowed**: [Yes/No]

## Compliance Requirements
- [ ] Include license text
- [ ] Provide source code
- [ ] Include NOTICE file
- [ ] Preserve copyright notices
- [ ] Other: _______

## Decision
- [X] Approved for use
- [ ] Requires commercial license
- [ ] Find alternative
- [ ] Legal review pending

**Approved By**: [Name, Date]
**Review Date**: [Date]
```

## References

- [Open Source Initiative](https://opensource.org/)
- [Free Software Foundation](https://www.fsf.org/licensing/)
- [Linux Foundation - Open Compliance Program](https://www.linuxfoundation.org/projects/open-compliance)
- [Google Open Source License Guide](https://opensource.google/documentation/reference/thirdparty/licenses)
