# Vulnerability Remediation Strategies

## Table of Contents
- [Remediation Decision Framework](#remediation-decision-framework)
- [Strategy 1: Upgrade to Fixed Version](#strategy-1-upgrade-to-fixed-version)
- [Strategy 2: Apply Security Patch](#strategy-2-apply-security-patch)
- [Strategy 3: Replace Component](#strategy-3-replace-component)
- [Strategy 4: Implement Mitigations](#strategy-4-implement-mitigations)
- [Strategy 5: Risk Acceptance](#strategy-5-risk-acceptance)
- [Language-Specific Guidance](#language-specific-guidance)

## Remediation Decision Framework

```
Is patch/upgrade available?
├─ Yes → Can we upgrade without breaking changes?
│   ├─ Yes → UPGRADE (Strategy 1)
│   └─ No → Are breaking changes acceptable?
│       ├─ Yes → UPGRADE with refactoring (Strategy 1)
│       └─ No → Can we apply patch? (Strategy 2)
│           ├─ Yes → PATCH
│           └─ No → REPLACE or MITIGATE (Strategy 3/4)
│
└─ No → Is vulnerability exploitable in our context?
    ├─ Yes → Can we replace component?
        │   ├─ Yes → REPLACE (Strategy 3)
        │   └─ No → MITIGATE (Strategy 4)
        │
    └─ No → ACCEPT with justification (Strategy 5)
```

## Strategy 1: Upgrade to Fixed Version

**When to use**: Patch available in newer version, upgrade path is clear

**Priority**: HIGHEST - This is the preferred remediation method

### Upgrade Process

1. **Identify Fixed Version**
   ```bash
   # Check Black Duck scan results for fixed version
   # Verify in CVE database or component changelog
   ```

2. **Review Breaking Changes**
   - Read release notes and changelog
   - Check migration guides
   - Review API changes and deprecations

3. **Update Dependency**

   **Node.js/npm**:
   ```bash
   npm install package-name@fixed-version
   npm audit fix  # Auto-fix where possible
   ```

   **Python/pip**:
   ```bash
   pip install package-name==fixed-version
   pip-audit --fix  # Auto-fix vulnerabilities
   ```

   **Java/Maven**:
   ```xml
   <dependency>
       <groupId>org.example</groupId>
       <artifactId>vulnerable-lib</artifactId>
       <version>fixed-version</version>
   </dependency>
   ```

   **Ruby/Bundler**:
   ```bash
   bundle update package-name
   ```

   **.NET/NuGet**:
   ```bash
   dotnet add package PackageName --version fixed-version
   ```

4. **Test Thoroughly**
   - Run existing test suite
   - Test affected functionality
   - Perform integration testing
   - Consider security-specific test cases

5. **Re-scan**
   ```bash
   scripts/blackduck_scan.py --project MyApp --version 1.0.1
   ```

### Handling Breaking Changes

**Minor Breaking Changes**: Acceptable for security fixes
- Update function calls to new API
- Adjust configuration for new defaults
- Update type definitions

**Major Breaking Changes**: Requires planning
- Create feature branch for upgrade
- Refactor code incrementally
- Use adapter pattern for compatibility
- Consider gradual rollout

**Incompatible Changes**: May require alternative strategy
- Evaluate business impact
- Consider Strategy 3 (Replace)
- If critical, implement Strategy 4 (Mitigate) temporarily

## Strategy 2: Apply Security Patch

**When to use**: Vendor provides patch without full version upgrade

**Priority**: HIGH - Use when full upgrade is not feasible

### Patch Types

**Backported Patches**:
- Vendor provides patch for older version
- Common in LTS/enterprise distributions
- Apply using vendor's instructions

**Custom Patches**:
- Create patch from upstream fix
- Test extensively before deployment
- Document patch application process

### Patch Application Process

1. **Obtain Patch**
   - Vendor security advisory
   - GitHub commit/pull request
   - Security mailing list

2. **Validate Patch**
   ```bash
   # Review patch contents
   git diff vulnerable-version..patched-version -- affected-file.js

   # Verify patch signature if available
   gpg --verify patch.sig patch.diff
   ```

3. **Apply Patch**

   **Git-based**:
   ```bash
   # Apply patch from file
   git apply security-patch.diff

   # Or cherry-pick specific commit
   git cherry-pick security-fix-commit-sha
   ```

   **Package manager overlay**:
   ```bash
   # npm patch-package
   npx patch-package package-name

   # pip with local modifications
   pip install -e ./patched-package
   ```

4. **Test and Verify**
   - Verify vulnerability is fixed
   - Run security scan
   - Test functionality

5. **Document Patch**
   - Create internal documentation
   - Add to dependency management notes
   - Set reminder for proper upgrade

## Strategy 3: Replace Component

**When to use**: No fix available, or component is unmaintained

**Priority**: MEDIUM-HIGH - Architectural change required

### Replacement Process

1. **Identify Alternatives**

   **Evaluation Criteria**:
   - Active maintenance (recent commits, releases)
   - Security track record
   - Community size and support
   - Feature parity
   - License compatibility
   - Performance characteristics

   **Research Sources**:
   - Black Duck component quality metrics
   - GitHub stars/forks/issues
   - Security advisories history
   - StackOverflow activity
   - Production usage at scale

2. **Select Replacement**

   **Example Replacements**:

   | Vulnerable Component | Alternative | Reason |
   |---------------------|-------------|--------|
   | moment.js | date-fns, dayjs | No longer maintained |
   | request (npm) | axios, node-fetch | Deprecated |
   | xml2js | fast-xml-parser | XXE vulnerabilities |
   | lodash (full) | lodash-es (specific functions) | Reduce attack surface |

3. **Plan Migration**
   - Map API differences
   - Identify all usage locations
   - Create compatibility layer if needed
   - Plan gradual migration if large codebase

4. **Execute Replacement**
   ```bash
   # Remove vulnerable component
   npm uninstall vulnerable-package

   # Install replacement
   npm install secure-alternative

   # Update imports/requires across codebase
   # Use tools like jscodeshift for automated refactoring
   ```

5. **Verify**
   - Scan for residual references
   - Test all affected code paths
   - Re-scan with Black Duck

## Strategy 4: Implement Mitigations

**When to use**: No fix/replacement available, vulnerability cannot be eliminated

**Priority**: MEDIUM - Compensating controls required

### Mitigation Techniques

#### Input Validation and Sanitization

For injection vulnerabilities:
```javascript
// Before: Vulnerable to injection
const result = eval(userInput);

// Mitigation: Strict validation and safe alternatives
const allowlist = ['option1', 'option2'];
if (!allowlist.includes(userInput)) {
    throw new Error('Invalid input');
}
const result = safeEvaluate(userInput);
```

#### Network Segmentation

For RCE/SSRF vulnerabilities:
- Deploy vulnerable component in isolated network segment
- Restrict outbound network access
- Use Web Application Firewall (WAF) rules
- Implement egress filtering

#### Access Controls

For authentication/authorization bypasses:
```python
# Additional validation layer
@require_additional_auth
def sensitive_operation():
    # Vulnerable library call
    vulnerable_lib.do_operation()
```

#### Runtime Protection

**Application Security Tools**:
- RASP (Runtime Application Self-Protection)
- Virtual patching via WAF
- Container security policies

**Example - WAF Rule**:
```nginx
# ModSecurity rule to block exploitation attempt
SecRule REQUEST_URI "@rx /vulnerable-endpoint" \
    "id:1001,phase:1,deny,status:403,\
    msg:'Blocked access to vulnerable component'"
```

#### Minimize Attack Surface

**Disable Vulnerable Features**:
```xml
<!-- Disable XXE in XML parser -->
<bean class="javax.xml.parsers.DocumentBuilderFactory">
    <property name="features">
        <map>
            <entry key="http://apache.org/xml/features/disallow-doctype-decl" value="true"/>
            <entry key="http://xml.org/sax/features/external-general-entities" value="false"/>
        </map>
    </property>
</bean>
```

**Remove Unused Code**:
```bash
# Remove unused dependencies
npm prune
pip-autoremove

# Tree-shake unused code
webpack --mode production  # Removes unused exports
```

### Monitoring and Detection

Implement enhanced monitoring for vulnerable components:

```python
# Example: Log and alert on vulnerable code path usage
import logging

def wrap_vulnerable_function(original_func):
    def wrapper(*args, **kwargs):
        logging.warning(
            "SECURITY: Vulnerable function called",
            extra={
                "function": original_func.__name__,
                "args": args,
                "caller": inspect.stack()[1]
            }
        )
        # Alert security team
        send_security_alert("Vulnerable code path executed")
        return original_func(*args, **kwargs)
    return wrapper

# Apply wrapper
vulnerable_lib.dangerous_function = wrap_vulnerable_function(
    vulnerable_lib.dangerous_function
)
```

## Strategy 5: Risk Acceptance

**When to use**: Vulnerability is not exploitable in your context, or risk is acceptable

**Priority**: LOWEST - Only after thorough risk analysis

### Risk Acceptance Criteria

**Acceptable when ALL of these are true**:
1. Vulnerability is not exploitable in deployment context
2. Attack requires significant preconditions (e.g., admin access)
3. Vulnerable code path is never executed
4. Impact is negligible even if exploited
5. Mitigation cost exceeds risk

### Risk Acceptance Process

1. **Document Justification**
   ```markdown
   # Risk Acceptance: CVE-2023-XXXXX in component-name

   **Vulnerability**: SQL Injection in admin panel
   **CVSS Score**: 8.5 (HIGH)
   **Component**: admin-dashboard@1.2.3

   **Justification for Acceptance**:
   - Admin panel is only accessible to authenticated administrators
   - Additional authentication layer required (2FA)
   - Network access restricted to internal network only
   - No sensitive data accessible via this component
   - Monitoring in place for suspicious activity

   **Mitigation Controls**:
   - WAF rules blocking SQL injection patterns
   - Enhanced logging on admin endpoints
   - Network segmentation
   - Regular security audits

   **Review Date**: 2024-06-01
   **Approved By**: CISO, Security Team Lead
   **Next Review**: 2024-09-01
   ```

2. **Implement Compensating Controls**
   - Enhanced monitoring
   - Additional authentication layers
   - Network restrictions
   - Regular security reviews

3. **Set Review Schedule**
   - Quarterly reviews for HIGH/CRITICAL
   - Semi-annual for MEDIUM
   - Annual for LOW

4. **Track in Black Duck**
   ```bash
   # Mark as accepted risk in Black Duck with expiration
   # Use Black Duck UI or API to create policy exception
   ```

## Language-Specific Guidance

### JavaScript/Node.js

**Tools**:
- `npm audit` - Built-in vulnerability scanner
- `npm audit fix` - Automatic remediation
- `yarn audit` - Yarn's vulnerability scanner
- `snyk` - Commercial SCA tool

**Best Practices**:
- Lock dependencies with `package-lock.json`
- Use `npm ci` in CI/CD for reproducible builds
- Audit transitive dependencies
- Consider `npm-force-resolutions` for forcing versions

### Python

**Tools**:
- `pip-audit` - Scan for vulnerabilities
- `safety` - Check against vulnerability database
- `pip-check` - Verify package compatibility

**Best Practices**:
- Use `requirements.txt` and `pip freeze`
- Pin exact versions for security-critical deps
- Use virtual environments
- Consider `pip-tools` for dependency management

### Java

**Tools**:
- OWASP Dependency-Check
- Snyk for Java
- Black Duck (commercial)

**Best Practices**:
- Use dependency management (Maven, Gradle)
- Lock versions in `pom.xml` or `build.gradle`
- Scan with `mvn dependency:tree` for transitive deps
- Use Maven Enforcer Plugin for version policies

### .NET

**Tools**:
- `dotnet list package --vulnerable`
- OWASP Dependency-Check
- WhiteSource Bolt

**Best Practices**:
- Use `PackageReference` in project files
- Lock versions with `packages.lock.json`
- Enable NuGet package validation
- Use `dotnet outdated` to track updates

### Ruby

**Tools**:
- `bundle audit` - Check for vulnerabilities
- `bundler-audit` - Automated checking

**Best Practices**:
- Use `Gemfile.lock` for reproducible deps
- Run `bundle audit` in CI/CD
- Update regularly with `bundle update`
- Use pessimistic version constraints

## Remediation Workflow Checklist

For each vulnerability:

- [ ] Identify vulnerability details (CVE, CVSS, affected versions)
- [ ] Determine if vulnerability is exploitable in your context
- [ ] Check for fixed version or patch availability
- [ ] Assess upgrade/patch complexity and breaking changes
- [ ] Select remediation strategy (Upgrade/Patch/Replace/Mitigate/Accept)
- [ ] Create remediation plan with timeline
- [ ] Execute remediation
- [ ] Test thoroughly (functionality + security)
- [ ] Re-scan with Black Duck to confirm fix
- [ ] Document changes and lessons learned
- [ ] Deploy to production with rollback plan
- [ ] Monitor for issues post-deployment

## References

- [NIST Vulnerability Management Guide](https://nvd.nist.gov/)
- [OWASP Dependency Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Vulnerable_Dependency_Management_Cheat_Sheet.html)
- [CISA Known Exploited Vulnerabilities](https://www.cisa.gov/known-exploited-vulnerabilities-catalog)
- [Snyk Vulnerability Database](https://security.snyk.io/)
