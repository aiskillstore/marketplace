#!/usr/bin/env python3
"""
Fetch vulnerability data for dependencies.
Queries OSV.dev API for known vulnerabilities.
Use web_search for CISA KEV and NVD data.
"""

import json
import sys
import urllib.request
import urllib.error
from typing import Optional

OSV_API = "https://api.osv.dev/v1/query"

ECOSYSTEM_MAP = {
    'npm': 'npm',
    'pip': 'PyPI',
    'gem': 'RubyGems',
    'go': 'Go',
    'cargo': 'crates.io',
    'maven': 'Maven',
    'nuget': 'NuGet'
}

def query_osv(package: str, version: str, ecosystem: str) -> list[dict]:
    """Query OSV.dev for vulnerabilities."""
    osv_ecosystem = ECOSYSTEM_MAP.get(ecosystem, ecosystem)
    
    payload = {
        "package": {
            "name": package,
            "ecosystem": osv_ecosystem
        }
    }
    
    if version and version != 'latest':
        payload["version"] = version
    
    try:
        req = urllib.request.Request(
            OSV_API,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get('vulns', [])
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return []
        print(f"HTTP error querying OSV for {package}: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"Error querying OSV for {package}: {e}", file=sys.stderr)
        return []

def extract_severity(vuln: dict) -> dict:
    """Extract severity info from OSV vulnerability."""
    severity = {'score': 0, 'level': 'UNKNOWN'}
    
    for s in vuln.get('severity', []):
        if s.get('type') == 'CVSS_V3':
            score_str = s.get('score', '')
            # Parse CVSS vector or score
            if '/' in score_str:
                # It's a vector, extract base score would need parsing
                severity['vector'] = score_str
            else:
                try:
                    severity['score'] = float(score_str)
                except:
                    pass
    
    # Determine level from score
    score = severity['score']
    if score >= 9.0:
        severity['level'] = 'CRITICAL'
    elif score >= 7.0:
        severity['level'] = 'HIGH'
    elif score >= 4.0:
        severity['level'] = 'MEDIUM'
    elif score > 0:
        severity['level'] = 'LOW'
    
    return severity

def format_vulnerability(vuln: dict, package: str, ecosystem: str) -> dict:
    """Format OSV vulnerability for output."""
    severity = extract_severity(vuln)
    
    # Get CVE aliases
    cves = [a for a in vuln.get('aliases', []) if a.startswith('CVE-')]
    
    # Get affected versions
    affected_ranges = []
    for affected in vuln.get('affected', []):
        for r in affected.get('ranges', []):
            events = r.get('events', [])
            introduced = next((e.get('introduced') for e in events if 'introduced' in e), None)
            fixed = next((e.get('fixed') for e in events if 'fixed' in e), None)
            if introduced or fixed:
                affected_ranges.append({
                    'introduced': introduced,
                    'fixed': fixed
                })
    
    return {
        'id': vuln.get('id'),
        'cves': cves,
        'summary': vuln.get('summary', 'No summary available'),
        'details': vuln.get('details', ''),
        'severity': severity,
        'package': package,
        'ecosystem': ecosystem,
        'affected_ranges': affected_ranges,
        'references': [r.get('url') for r in vuln.get('references', [])],
        'published': vuln.get('published'),
        'modified': vuln.get('modified')
    }

def scan_dependencies(inventory: dict) -> list[dict]:
    """Scan all dependencies for vulnerabilities."""
    vulnerabilities = []
    
    for dep in inventory.get('dependencies', []):
        name = dep.get('name')
        version = dep.get('version', '')
        ecosystem = dep.get('type', 'npm')
        
        vulns = query_osv(name, version, ecosystem)
        
        for vuln in vulns:
            formatted = format_vulnerability(vuln, name, ecosystem)
            formatted['source_file'] = dep.get('source')
            formatted['installed_version'] = version
            vulnerabilities.append(formatted)
    
    return vulnerabilities

def calculate_risk_score(vuln: dict, is_in_kev: bool = False) -> float:
    """Calculate risk score based on multiple factors."""
    cvss = vuln.get('severity', {}).get('score', 5.0)
    
    # Exploitability
    if is_in_kev:
        exploitability = 10
    elif any('exploit' in str(r).lower() for r in vuln.get('references', [])):
        exploitability = 7
    else:
        exploitability = 3
    
    # Default criticality and exposure (user should adjust)
    criticality = 5
    exposure = 5
    
    risk = (cvss * 0.3) + (exploitability * 0.3) + (criticality * 0.2) + (exposure * 0.2)
    return round(risk, 2)

def main():
    # Read inventory from stdin or file
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            inventory = json.load(f)
    else:
        inventory = json.load(sys.stdin)
    
    vulnerabilities = scan_dependencies(inventory)
    
    # Add risk scores
    for vuln in vulnerabilities:
        vuln['risk_score'] = calculate_risk_score(vuln)
    
    # Sort by risk score
    vulnerabilities.sort(key=lambda v: v['risk_score'], reverse=True)
    
    output = {
        'total_vulnerabilities': len(vulnerabilities),
        'by_severity': {
            'CRITICAL': len([v for v in vulnerabilities if v['severity']['level'] == 'CRITICAL']),
            'HIGH': len([v for v in vulnerabilities if v['severity']['level'] == 'HIGH']),
            'MEDIUM': len([v for v in vulnerabilities if v['severity']['level'] == 'MEDIUM']),
            'LOW': len([v for v in vulnerabilities if v['severity']['level'] == 'LOW']),
        },
        'vulnerabilities': vulnerabilities
    }
    
    print(json.dumps(output, indent=2))

if __name__ == '__main__':
    main()
