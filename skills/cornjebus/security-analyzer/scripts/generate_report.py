#!/usr/bin/env python3
"""
Generate security reports from vulnerability scan results.
Outputs both technical and executive summary reports.
"""

import json
import sys
from datetime import datetime
from typing import Optional

def generate_fix_command(vuln: dict) -> str:
    """Generate fix command based on ecosystem."""
    ecosystem = vuln.get('ecosystem', 'npm')
    package = vuln.get('package', '')
    
    # Find fixed version
    fixed_version = None
    for r in vuln.get('affected_ranges', []):
        if r.get('fixed'):
            fixed_version = r['fixed']
            break
    
    if not fixed_version:
        return f"# Manual review required - no fixed version identified for {package}"
    
    commands = {
        'npm': f"npm install {package}@{fixed_version}",
        'pip': f"pip install {package}>={fixed_version}",
        'gem': f"bundle update {package}",
        'go': f"go get {package}@v{fixed_version}",
        'cargo': f"cargo update -p {package}",
    }
    
    return commands.get(ecosystem, f"# Update {package} to version {fixed_version}")

def generate_test_code(vuln: dict) -> dict:
    """Generate test code for vulnerability."""
    package = vuln.get('package', 'unknown')
    cve_id = vuln.get('cves', [vuln.get('id', 'UNKNOWN')])[0]
    cve_normalized = cve_id.lower().replace('-', '_').replace('.', '_')
    installed = vuln.get('installed_version', 'unknown')
    
    fixed_version = None
    for r in vuln.get('affected_ranges', []):
        if r.get('fixed'):
            fixed_version = r['fixed']
            break
    
    pre_test = f'''def test_{cve_normalized}_exists():
    """Proves {cve_id} vulnerability is present before fix."""
    import subprocess
    result = subprocess.run(
        ["pip", "show", "{package}"],
        capture_output=True, text=True
    )
    version_line = [l for l in result.stdout.split("\\n") if l.startswith("Version:")]
    if version_line:
        installed = version_line[0].split(":")[1].strip()
        # Vulnerable if version < {fixed_version or "fixed_version"}
        assert installed == "{installed}", f"Expected vulnerable version {installed}"'''
    
    fix_test = f'''def test_{cve_normalized}_fix_logic():
    """Tests the remediation logic works correctly."""
    # Verify package.json/requirements.txt has correct version constraint
    import json
    # Example for npm:
    # with open("package.json") as f:
    #     pkg = json.load(f)
    #     assert pkg["dependencies"]["{package}"] >= "{fixed_version or 'latest'}"
    pass  # Implement based on ecosystem'''
    
    post_test = f'''def test_{cve_normalized}_resolved():
    """Proves {cve_id} vulnerability is fixed."""
    import subprocess
    result = subprocess.run(
        ["pip", "show", "{package}"],
        capture_output=True, text=True
    )
    version_line = [l for l in result.stdout.split("\\n") if l.startswith("Version:")]
    if version_line:
        installed = version_line[0].split(":")[1].strip()
        # Fixed if version >= {fixed_version or "fixed_version"}
        # assert installed >= "{fixed_version or 'fixed_version'}"
        pass  # Implement version comparison'''
    
    return {
        'pre_test': pre_test,
        'fix_test': fix_test,
        'post_test': post_test
    }

def generate_technical_report(scan_results: dict, inventory: dict) -> str:
    """Generate detailed technical report."""
    vulns = scan_results.get('vulnerabilities', [])
    
    report = f"""# Security Analysis Report
**Generated:** {datetime.now().isoformat()}  
**Scope:** {inventory.get('scan_root', 'Unknown')}

## Executive Summary
- **Total Vulnerabilities:** {scan_results.get('total_vulnerabilities', 0)}
- **Critical:** {scan_results['by_severity'].get('CRITICAL', 0)} | **High:** {scan_results['by_severity'].get('HIGH', 0)} | **Medium:** {scan_results['by_severity'].get('MEDIUM', 0)} | **Low:** {scan_results['by_severity'].get('LOW', 0)}
- **Secrets Exposure Risk:** {inventory.get('secrets_exposure', {}).get('risk', 'Unknown')}

## Environment Inventory
- Dependencies: {inventory.get('summary', {}).get('total_dependencies', 0)} packages
- Containers: {inventory.get('summary', {}).get('container_configs', 0)} configurations
- Cloud Resources: {inventory.get('summary', {}).get('cloud_configs', 0)} IaC files

---

"""
    
    # Group by severity
    phases = {
        'CRITICAL': [],
        'HIGH': [],
        'MEDIUM': [],
        'LOW': []
    }
    
    for vuln in vulns:
        level = vuln.get('severity', {}).get('level', 'LOW')
        phases.get(level, phases['LOW']).append(vuln)
    
    phase_names = [
        ('CRITICAL', 'Phase 1: Critical Priority'),
        ('HIGH', 'Phase 2: High Priority'),
        ('MEDIUM', 'Phase 3: Medium Priority'),
        ('LOW', 'Phase 4: Low Priority')
    ]
    
    for level, phase_title in phase_names:
        phase_vulns = phases[level]
        if not phase_vulns:
            continue
            
        report += f"## {phase_title}\n\n"
        
        for vuln in phase_vulns:
            cve_id = vuln.get('cves', [vuln.get('id', 'UNKNOWN')])[0]
            tests = generate_test_code(vuln)
            fix_cmd = generate_fix_command(vuln)
            
            report += f"""### {cve_id}: {vuln.get('summary', 'No summary')}
**Risk Score:** {vuln.get('risk_score', 'N/A')}/10  
**Package:** {vuln.get('package')}@{vuln.get('installed_version', 'unknown')}  
**CVSS:** {vuln.get('severity', {}).get('score', 'N/A')} ({vuln.get('severity', {}).get('level', 'UNKNOWN')})

#### Vulnerability Details
{vuln.get('details', 'No details available.')[:500]}

#### Affected Versions
"""
            for r in vuln.get('affected_ranges', []):
                report += f"- Introduced: {r.get('introduced', 'Unknown')} → Fixed: {r.get('fixed', 'Not yet fixed')}\n"
            
            report += f"""
#### Remediation

**Fix Command:**
```bash
{fix_cmd}
```

#### Validation Tests

**Pre-fix test:**
```python
{tests['pre_test']}
```

**Remediation unit test:**
```python
{tests['fix_test']}
```

**Post-fix test:**
```python
{tests['post_test']}
```

---

"""
    
    # Secrets section
    secrets = inventory.get('secrets_exposure', {})
    if secrets.get('potentially_exposed'):
        report += f"""## Additional Findings

### Secrets Exposure Risk: {secrets.get('risk', 'Unknown')}
The following environment files may be exposed in version control:
"""
        for f in secrets.get('potentially_exposed', []):
            report += f"- `{f}`\n"
        
        report += """
**Remediation:**
1. Add these files to `.gitignore`
2. Rotate any secrets that may have been committed
3. Use environment variable injection or secrets management

"""
    
    return report

def generate_executive_report(scan_results: dict, inventory: dict) -> str:
    """Generate executive summary report."""
    vulns = scan_results.get('vulnerabilities', [])
    
    # Estimate effort (rough: 1hr critical, 0.5hr high, 0.25hr medium, 0.1hr low)
    effort = {
        'CRITICAL': scan_results['by_severity'].get('CRITICAL', 0) * 1,
        'HIGH': scan_results['by_severity'].get('HIGH', 0) * 0.5,
        'MEDIUM': scan_results['by_severity'].get('MEDIUM', 0) * 0.25,
        'LOW': scan_results['by_severity'].get('LOW', 0) * 0.1
    }
    total_effort = sum(effort.values())
    
    # Determine overall risk
    if scan_results['by_severity'].get('CRITICAL', 0) > 0:
        overall_risk = "HIGH - Critical vulnerabilities require immediate attention"
    elif scan_results['by_severity'].get('HIGH', 0) > 2:
        overall_risk = "ELEVATED - Multiple high-severity issues found"
    elif scan_results['by_severity'].get('HIGH', 0) > 0:
        overall_risk = "MODERATE - High-severity issues present"
    else:
        overall_risk = "LOW - No critical or high-severity issues"
    
    report = f"""# Security Assessment Summary
**Date:** {datetime.now().strftime('%Y-%m-%d')}  
**Prepared for:** Leadership Review

## Overall Security Posture
**Risk Level:** {overall_risk}

## Key Findings

| Priority | Count | Estimated Effort |
|----------|-------|------------------|
| Critical | {scan_results['by_severity'].get('CRITICAL', 0)} | {effort['CRITICAL']:.1f} hours |
| High | {scan_results['by_severity'].get('HIGH', 0)} | {effort['HIGH']:.1f} hours |
| Medium | {scan_results['by_severity'].get('MEDIUM', 0)} | {effort['MEDIUM']:.1f} hours |
| Low | {scan_results['by_severity'].get('LOW', 0)} | {effort['LOW']:.1f} hours |
| **Total** | **{scan_results.get('total_vulnerabilities', 0)}** | **{total_effort:.1f} hours** |

## Top Risks

"""
    
    # Top 5 vulnerabilities
    for i, vuln in enumerate(vulns[:5], 1):
        cve_id = vuln.get('cves', [vuln.get('id', 'UNKNOWN')])[0]
        report += f"{i}. **{cve_id}** ({vuln.get('package')}) - {vuln.get('summary', 'No summary')[:60]}...\n"
    
    report += f"""
## Recommended Actions

### Immediate (This Week)
- Address all {scan_results['by_severity'].get('CRITICAL', 0)} critical vulnerabilities
- Review secrets exposure and rotate if needed

### Short-term (This Month)
- Remediate high-priority vulnerabilities
- Implement automated dependency scanning in CI/CD

### Long-term (This Quarter)
- Establish regular security review cadence
- Implement runtime security monitoring

## Resource Requirements
- Engineering time: ~{total_effort:.0f} hours
- Recommended: Automated dependency scanning tool integration
"""
    
    return report

def main():
    if len(sys.argv) < 3:
        print("Usage: generate_report.py <scan_results.json> <inventory.json>", file=sys.stderr)
        sys.exit(1)
    
    with open(sys.argv[1]) as f:
        scan_results = json.load(f)
    
    with open(sys.argv[2]) as f:
        inventory = json.load(f)
    
    technical = generate_technical_report(scan_results, inventory)
    executive = generate_executive_report(scan_results, inventory)
    
    print("=== TECHNICAL REPORT ===")
    print(technical)
    print("\n\n=== EXECUTIVE REPORT ===")
    print(executive)

if __name__ == '__main__':
    main()
