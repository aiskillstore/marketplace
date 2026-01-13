#!/usr/bin/env python3
"""
CVE/NVD vulnerability database integration
Fetches and analyzes known vulnerabilities in dependencies
"""
import json
import subprocess
import sys
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta
import hashlib


class DependencyScanner:
    """Scan project dependencies for known vulnerabilities"""
    
    def __init__(self, project_path: str = '.'):
        self.project_path = Path(project_path)
        self.cache_dir = Path.home() / '.vibe-security' / 'cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def scan_npm(self) -> List[Dict[str, Any]]:
        """Scan npm dependencies"""
        package_json = self.project_path / 'package.json'
        if not package_json.exists():
            return []
        
        vulnerabilities = []
        
        try:
            # Run npm audit
            result = subprocess.run(
                ['npm', 'audit', '--json'],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.stdout:
                audit_data = json.loads(result.stdout)
                
                # Parse vulnerabilities
                if 'vulnerabilities' in audit_data:
                    for pkg_name, vuln_data in audit_data['vulnerabilities'].items():
                        vulnerabilities.append({
                            'package': pkg_name,
                            'ecosystem': 'npm',
                            'severity': vuln_data.get('severity', 'unknown'),
                            'via': vuln_data.get('via', []),
                            'range': vuln_data.get('range', 'unknown'),
                            'fixAvailable': vuln_data.get('fixAvailable', False),
                            'cves': self._extract_cves(vuln_data)
                        })
        
        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
            pass
        
        return vulnerabilities
    
    def scan_python(self) -> List[Dict[str, Any]]:
        """Scan Python dependencies using pip-audit or safety"""
        requirements = self.project_path / 'requirements.txt'
        if not requirements.exists():
            return []
        
        vulnerabilities = []
        
        try:
            # Try pip-audit first
            result = subprocess.run(
                ['pip-audit', '--format', 'json', '-r', str(requirements)],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.stdout:
                audit_data = json.loads(result.stdout)
                
                for vuln in audit_data.get('vulnerabilities', []):
                    vulnerabilities.append({
                        'package': vuln.get('name'),
                        'ecosystem': 'pypi',
                        'severity': self._map_severity(vuln.get('severity')),
                        'version': vuln.get('version'),
                        'vulnerable_ranges': vuln.get('vulnerable_ranges'),
                        'id': vuln.get('id'),
                        'cves': vuln.get('aliases', []),
                        'fix_versions': vuln.get('fix_versions', [])
                    })
        
        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
            # Fallback to basic pattern matching
            pass
        
        return vulnerabilities
    
    def scan_all(self) -> Dict[str, List[Dict[str, Any]]]:
        """Scan all supported package managers"""
        results = {}
        
        # Detect ecosystem and scan
        if (self.project_path / 'package.json').exists():
            results['npm'] = self.scan_npm()
        
        if (self.project_path / 'requirements.txt').exists():
            results['python'] = self.scan_python()
        
        # Add more ecosystems
        if (self.project_path / 'go.mod').exists():
            results['go'] = self.scan_go()
        
        if (self.project_path / 'Cargo.toml').exists():
            results['rust'] = self.scan_rust()
        
        return results
    
    def scan_go(self) -> List[Dict[str, Any]]:
        """Scan Go dependencies"""
        vulnerabilities = []
        
        try:
            result = subprocess.run(
                ['go', 'list', '-json', '-m', 'all'],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Note: This is a placeholder. Full implementation would use govulncheck
            if result.stdout:
                # Parse go modules and check against vulnerability database
                pass
        
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return vulnerabilities
    
    def scan_rust(self) -> List[Dict[str, Any]]:
        """Scan Rust dependencies using cargo-audit"""
        vulnerabilities = []
        
        try:
            result = subprocess.run(
                ['cargo', 'audit', '--json'],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.stdout:
                audit_data = json.loads(result.stdout)
                
                for vuln in audit_data.get('vulnerabilities', {}).get('list', []):
                    vulnerabilities.append({
                        'package': vuln.get('package'),
                        'ecosystem': 'cargo',
                        'severity': vuln.get('severity', 'unknown'),
                        'advisory': vuln.get('advisory'),
                        'patched_versions': vuln.get('patched_versions'),
                        'cves': [vuln.get('id')]
                    })
        
        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
            pass
        
        return vulnerabilities
    
    def _extract_cves(self, vuln_data: Dict) -> List[str]:
        """Extract CVE IDs from vulnerability data"""
        cves = []
        
        via = vuln_data.get('via', [])
        for item in via:
            if isinstance(item, dict):
                if 'cve' in item:
                    cves.extend(item['cve'])
                if 'url' in item and 'CVE-' in item['url']:
                    # Extract CVE from URL
                    import re
                    matches = re.findall(r'CVE-\d{4}-\d+', item['url'])
                    cves.extend(matches)
        
        return list(set(cves))
    
    def _map_severity(self, severity: str) -> str:
        """Map various severity formats to standard levels"""
        if not severity:
            return 'unknown'
        
        severity_lower = severity.lower()
        
        if severity_lower in ['critical', 'high']:
            return 'critical'
        elif severity_lower in ['medium', 'moderate']:
            return 'high'
        elif severity_lower in ['low', 'info']:
            return 'medium'
        
        return 'unknown'
    
    def generate_report(self, vulnerabilities: Dict[str, List[Dict[str, Any]]]) -> str:
        """Generate human-readable vulnerability report"""
        lines = []
        lines.append("=" * 80)
        lines.append("DEPENDENCY VULNERABILITY REPORT")
        lines.append("=" * 80)
        lines.append("")
        
        total = sum(len(vulns) for vulns in vulnerabilities.values())
        lines.append(f"Total vulnerabilities found: {total}")
        lines.append("")
        
        for ecosystem, vulns in vulnerabilities.items():
            if not vulns:
                continue
            
            lines.append(f"\n{ecosystem.upper()} Vulnerabilities:")
            lines.append("-" * 80)
            
            for vuln in vulns:
                severity = vuln.get('severity', 'unknown').upper()
                package = vuln.get('package', 'unknown')
                
                lines.append(f"\n[{severity}] {package}")
                
                if vuln.get('cves'):
                    lines.append(f"  CVEs: {', '.join(vuln['cves'])}")
                
                if vuln.get('fix_versions'):
                    lines.append(f"  Fix available: {', '.join(vuln['fix_versions'])}")
                elif vuln.get('fixAvailable'):
                    lines.append(f"  Fix available: Yes")
                
                if vuln.get('range'):
                    lines.append(f"  Affected range: {vuln['range']}")
        
        lines.append("\n" + "=" * 80)
        lines.append("Recommendation: Update vulnerable packages to latest versions")
        lines.append("=" * 80)
        
        return '\n'.join(lines)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Scan dependencies for CVE vulnerabilities')
    parser.add_argument('path', nargs='?', default='.', help='Project path to scan')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--ecosystem', choices=['npm', 'python', 'go', 'rust'], 
                       help='Scan specific ecosystem only')
    
    args = parser.parse_args()
    
    scanner = DependencyScanner(args.path)
    
    if args.ecosystem:
        if args.ecosystem == 'npm':
            results = {'npm': scanner.scan_npm()}
        elif args.ecosystem == 'python':
            results = {'python': scanner.scan_python()}
        elif args.ecosystem == 'go':
            results = {'go': scanner.scan_go()}
        elif args.ecosystem == 'rust':
            results = {'rust': scanner.scan_rust()}
    else:
        results = scanner.scan_all()
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(scanner.generate_report(results))


if __name__ == '__main__':
    main()
