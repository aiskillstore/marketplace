### Phase 1: Vulnerability Assessment
- [ ] Understand the security issue
- [ ] Assess severity and impact
- [ ] Identify affected versions
- [ ] Check if actively exploited
- [ ] Review security advisories

### Phase 2: Impact Analysis
- [ ] Identify all affected code paths
- [ ] Determine data exposure risk
- [ ] Check for similar issues elsewhere
- [ ] Assess authentication/authorization impact
- [ ] Review compliance implications

### Phase 3: Security Test (TDD)
- [ ] Write test demonstrating vulnerability
- [ ] Test should fail (exploits vulnerability)
- [ ] Test common attack vectors
- [ ] Test boundary conditions
- [ ] Document attack scenarios

### Phase 4: Implement Fix
- [ ] Apply principle of least privilege
- [ ] Use secure coding practices
- [ ] Validate all inputs
- [ ] Sanitize outputs
- [ ] Add rate limiting if applicable

### Phase 5: Security Hardening
- [ ] Add additional security checks
- [ ] Implement defense in depth
- [ ] Add security logging
- [ ] Update authentication/authorization
- [ ] Review encryption/hashing

### Phase 6: Security Testing
- [ ] Run security scan (Bandit)
- [ ] Test with malicious inputs
- [ ] Verify authentication works
- [ ] Test authorization boundaries
- [ ] Check for information disclosure

### Phase 7: Security Review
- [ ] Review with security-focused perspective
- [ ] Check OWASP Top 10 compliance
- [ ] Verify no new vulnerabilities introduced
- [ ] Test error messages don't leak info
- [ ] Document security measures

### Phase 8: Quality & Documentation
- [ ] Run make check
- [ ] Update security documentation
- [ ] Add security comments in code
- [ ] Document security assumptions
- [ ] Plan coordinated disclosure if needed
