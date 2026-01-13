# Common Dependency Vulnerabilities

## Vulnerability Categories

### Code Injection

**Prototype Pollution (JavaScript)**
- **Risk**: High
- **Common in**: lodash, jQuery, minimist
- **Attack**: Modify Object.prototype to inject properties
- **Example**: `merge({}, JSON.parse(userInput))`
- **Fix**: Update to patched versions, use `Object.create(null)`

**SQL Injection**
- **Risk**: Critical
- **Common in**: ORMs with raw query support
- **Attack**: Inject SQL via user input
- **Example**: `db.query('SELECT * FROM users WHERE id = ' + userId)`
- **Fix**: Use parameterized queries, ORM methods

**Command Injection**
- **Risk**: Critical
- **Common in**: child_process, shell execution libraries
- **Attack**: Execute arbitrary commands
- **Example**: `exec('ping ' + userInput)`
- **Fix**: Use spawn with args array, sanitize input

**Path Traversal**
- **Risk**: High
- **Common in**: File serving libraries
- **Attack**: Access files outside intended directory
- **Example**: `fs.readFile(basePath + userInput)`
- **Fix**: Validate and normalize paths, use path.join()

### Cross-Site Scripting (XSS)

**Reflected XSS**
- **Risk**: High
- **Common in**: Template engines, HTML builders
- **Attack**: Inject malicious scripts via URL/forms
- **Fix**: Escape user input, use auto-escaping templates

**Stored XSS**
- **Risk**: High
- **Attack**: Store malicious scripts in database
- **Fix**: Sanitize on input and escape on output

**DOM-based XSS**
- **Risk**: Moderate
- **Common in**: Client-side rendering libraries
- **Fix**: Use framework security features, avoid innerHTML

### Deserialization Vulnerabilities

**Unsafe Deserialization**
- **Risk**: Critical
- **Common in**: pickle (Python), unserialize (PHP), ObjectInputStream (Java)
- **Attack**: Execute code during deserialization
- **Example**: `pickle.loads(untrusted_data)`
- **Fix**: Never deserialize untrusted data, use JSON

**YAML Injection**
- **Risk**: High
- **Common in**: PyYAML, js-yaml
- **Attack**: Execute code via YAML tags
- **Fix**: Use safe loaders (yaml.safe_load)

### Regular Expression Denial of Service (ReDoS)

**Catastrophic Backtracking**
- **Risk**: Moderate
- **Common in**: Validation libraries
- **Attack**: Craft input causing exponential regex time
- **Example**: `/(a+)+b/.test(aaaaa...c)` hangs
- **Fix**: Timeout regexes, avoid nested quantifiers

### Authentication & Authorization

**JWT Vulnerabilities**
- **Risk**: Critical
- **Common issues**: None algorithm, weak secrets, no expiration
- **Attack**: Forge tokens, bypass auth
- **Fix**: Validate algorithm, strong secrets, short expiry

**Session Fixation**
- **Risk**: High
- **Attack**: Force user to use attacker's session ID
- **Fix**: Regenerate session ID on login

**Insecure Defaults**
- **Risk**: Varies
- **Common in**: Many frameworks
- **Attack**: Exploit default credentials/configs
- **Fix**: Change defaults, disable debug in production

### Cryptography Issues

**Weak Hashing**
- **Risk**: High
- **Vulnerable**: MD5, SHA1
- **Attack**: Rainbow tables, collision attacks
- **Fix**: Use bcrypt, scrypt, Argon2 for passwords

**Insufficient Entropy**
- **Risk**: High
- **Common in**: Random number generators
- **Attack**: Predict "random" values
- **Fix**: Use crypto.randomBytes, secrets module

**Hardcoded Secrets**
- **Risk**: Critical
- **Attack**: Extract secrets from code
- **Fix**: Use environment variables, secret managers

### Dependency Chain Attacks

**Typosquatting**
- **Risk**: High
- **Attack**: Register similar package names
- **Example**: `requets` instead of `requests`
- **Fix**: Double-check package names before install

**Dependency Confusion**
- **Risk**: High
- **Attack**: Private package name in public registry
- **Fix**: Use scoped packages, private registries

**Malicious Package Updates**
- **Risk**: Critical
- **Attack**: Hijack maintainer account, publish malicious update
- **Fix**: Use lock files, review updates, SRI for CDN

### Denial of Service

**Billion Laughs (XML)**
- **Risk**: Moderate
- **Attack**: Exponentially expand XML entities
- **Fix**: Disable external entities, limit expansion

**Algorithmic Complexity**
- **Risk**: Moderate
- **Attack**: Trigger O(n²) or worse operations
- **Example**: Hash collision attacks
- **Fix**: Use resistant algorithms, timeouts

**Memory Exhaustion**
- **Risk**: Moderate
- **Attack**: Allocate unbounded memory
- **Fix**: Limit request sizes, streaming

### Information Disclosure

**Stack Traces in Production**
- **Risk**: Low to Moderate
- **Attack**: Learn about internal structure
- **Fix**: Disable debug mode, custom error pages

**Directory Listing**
- **Risk**: Low
- **Attack**: Browse server files
- **Fix**: Disable directory indexing

**Verbose Errors**
- **Risk**: Low
- **Attack**: Gain insight into system
- **Fix**: Generic error messages to users

## High-Risk Packages (Historical)

### JavaScript/Node.js

**event-stream (2018)**
- Compromised via dependency (flatmap-stream)
- Targeted cryptocurrency wallets
- Lesson: Review all transitive dependencies

**ua-parser-js (2021)**
- Hijacked, published malicious versions
- Cryptominer and password stealer
- Lesson: Monitor for unusual updates

**node-ipc (2022)**
- Maintainer added destructive code
- Deleted files on Russian/Belarusian IPs
- Lesson: Trust but verify maintainer actions

**colors, faker (2022)**
- Maintainer sabotaged own packages
- Infinite loop protest
- Lesson: Pin versions, review updates

### Python

**PyPI typosquatting (ongoing)**
- Packages like `python3-dateutil` (vs `python-dateutil`)
- Various malware campaigns
- Lesson: Verify package names carefully

**ctx (2022)**
- Trojan in popular package
- Exfiltrated environment variables
- Lesson: Audit dependencies

### Ruby

**rest-client (2019)**
- Compromised gem
- Backdoor added
- Lesson: Verify gem signatures

## Severity Assessment

### Critical (Fix Immediately)
- Remote code execution (RCE)
- SQL injection in production dependencies
- Authentication bypass
- Credential theft
- Data exfiltration

### High (Fix Within Days)
- Privilege escalation
- XSS in production
- Path traversal
- Unsafe deserialization
- Known exploits in the wild

### Moderate (Fix Within Weeks)
- Information disclosure
- DoS vulnerabilities
- ReDoS
- Insecure defaults in dev dependencies

### Low (Fix When Convenient)
- Verbose errors
- Minor info leaks
- Issues in development-only dependencies
- Theoretical vulnerabilities with no known exploit

## Mitigation Checklist

### Before Adding Dependencies

- [ ] Check package popularity and maintenance
- [ ] Review recent issues and pull requests
- [ ] Check for known vulnerabilities
- [ ] Verify license compatibility
- [ ] Assess if it's worth the complexity
- [ ] Consider writing it yourself for simple tasks

### Regular Maintenance

- [ ] Run `npm audit` / equivalent weekly
- [ ] Review Dependabot/Renovate PRs
- [ ] Update dependencies quarterly
- [ ] Remove unused dependencies
- [ ] Monitor security advisories
- [ ] Test updates in staging before production

### Security Hardening

- [ ] Use lock files (package-lock.json, etc.)
- [ ] Enable security alerts (GitHub, Snyk, etc.)
- [ ] Audit transitive dependencies
- [ ] Use tools: Snyk, OWASP Dependency Check, npm audit
- [ ] Implement CSP (Content Security Policy)
- [ ] Use SRI for CDN resources
- [ ] Principle of least privilege for dependencies

## Tools for Detection

**JavaScript:**
- `npm audit` - Built-in
- `yarn audit` - Built-in
- Snyk - Commercial/Free
- npm-check-updates - Check for updates

**Python:**
- `pip-audit` - Official auditing tool
- `safety` - Safety DB checking
- Bandit - Security linter

**Ruby:**
- `bundle audit` - Bundler auditing
- Brakeman - Rails security scanner

**Java:**
- OWASP Dependency Check
- Snyk for Java

**Go:**
- `govulncheck` - Official vulnerability checker
- Nancy - Dependency checker

**Multi-language:**
- Snyk
- WhiteSource
- Black Duck
- FOSSA
- Dependabot (GitHub)
- Renovate

## Response Plan

### When Vulnerability Found

1. **Assess severity** using CVSS score and context
2. **Check if exploitable** in your usage
3. **Identify fix** (update version, workaround)
4. **Test fix** in development/staging
5. **Deploy fix** following change management
6. **Document** the incident and response

### When No Fix Available

1. **Search for alternatives** with similar functionality
2. **Implement workarounds** (input validation, sandboxing)
3. **Fork and patch** if critical and no alternative
4. **Accept risk** if impact is low (document decision)
5. **Monitor** for updates and fixes

## References

- [CVE Database](https://cve.mitre.org/)
- [NIST NVD](https://nvd.nist.gov/)
- [Snyk Vulnerability DB](https://snyk.io/vuln)
- [GitHub Advisory Database](https://github.com/advisories)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
