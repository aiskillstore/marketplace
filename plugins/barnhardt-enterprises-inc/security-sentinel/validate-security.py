#!/usr/bin/env python3
"""
Security Vulnerability Scanner for Quetrex

Scans codebase for common security vulnerabilities.
Run before every commit and deployment.

Usage:
    python validate-security.py [path]

Examples:
    python validate-security.py src/
    python validate-security.py .
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass

@dataclass
class SecurityIssue:
    """Represents a security issue found in the code"""
    file: str
    line: int
    severity: str  # 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'
    category: str
    message: str
    code_snippet: str

class SecurityScanner:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.issues: List[SecurityIssue] = []

    def scan(self) -> List[SecurityIssue]:
        """Run all security checks"""
        print(f"🔍 Scanning {self.root_path} for security vulnerabilities...\n")

        # Get all TypeScript/JavaScript files
        files = list(self.root_path.rglob("*.ts")) + \
                list(self.root_path.rglob("*.tsx")) + \
                list(self.root_path.rglob("*.js")) + \
                list(self.root_path.rglob("*.jsx"))

        # Exclude node_modules and .next
        files = [f for f in files if 'node_modules' not in str(f) and '.next' not in str(f)]

        print(f"📁 Found {len(files)} files to scan\n")

        for file in files:
            self.scan_file(file)

        return self.issues

    def scan_file(self, file_path: Path):
        """Scan a single file for vulnerabilities"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for i, line in enumerate(lines, start=1):
                # Check for various vulnerabilities
                self.check_hardcoded_secrets(file_path, i, line)
                self.check_sql_injection(file_path, i, line)
                self.check_xss(file_path, i, line)
                self.check_eval_usage(file_path, i, line)
                self.check_weak_crypto(file_path, i, line)
                self.check_insecure_randomness(file_path, i, line)
                self.check_command_injection(file_path, i, line)
                self.check_path_traversal(file_path, i, line)
                self.check_weak_password_hash(file_path, i, line)
                self.check_jwt_security(file_path, i, line)
                self.check_missing_auth(file_path, i, line)
                self.check_cors_misconfiguration(file_path, i, line)
                self.check_http_only_cookies(file_path, i, line)
                self.check_ts_ignore(file_path, i, line)
                self.check_any_type(file_path, i, line)
                self.check_console_log(file_path, i, line)

        except Exception as e:
            print(f"⚠️  Error scanning {file_path}: {e}")

    def add_issue(self, file: Path, line: int, severity: str, category: str, message: str, code: str):
        """Add a security issue to the list"""
        self.issues.append(SecurityIssue(
            file=str(file.relative_to(self.root_path)),
            line=line,
            severity=severity,
            category=category,
            message=message,
            code_snippet=code.strip()
        ))

    def check_hardcoded_secrets(self, file: Path, line_num: int, line: str):
        """Check for hardcoded API keys, passwords, tokens"""
        patterns = [
            (r'(?i)(api[_-]?key|apikey|api[_-]?secret)\s*[=:]\s*["\']([a-zA-Z0-9_-]{20,})["\']', 'API Key'),
            (r'(?i)(password|passwd|pwd)\s*[=:]\s*["\'](?!.*process\.env)(.{8,})["\']', 'Password'),
            (r'(?i)(secret[_-]?key|secret)\s*[=:]\s*["\'](?!.*process\.env)(.{16,})["\']', 'Secret Key'),
            (r'sk_live_[a-zA-Z0-9]{20,}', 'Stripe Live Key'),
            (r'sk_test_[a-zA-Z0-9]{20,}', 'Stripe Test Key'),
            (r'AIza[a-zA-Z0-9_-]{35}', 'Google API Key'),
            (r'ghp_[a-zA-Z0-9]{36}', 'GitHub Personal Access Token'),
            (r'gho_[a-zA-Z0-9]{36}', 'GitHub OAuth Token'),
            (r'sk-[a-zA-Z0-9]{48}', 'OpenAI API Key'),
            (r'eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*', 'JWT Token'),
        ]

        for pattern, name in patterns:
            if re.search(pattern, line) and 'process.env' not in line and 'example' not in line.lower():
                self.add_issue(
                    file, line_num, 'CRITICAL', 'Hardcoded Secrets',
                    f'Hardcoded {name} detected. Use environment variables.',
                    line
                )

    def check_sql_injection(self, file: Path, line_num: int, line: str):
        """Check for SQL injection vulnerabilities"""
        # String concatenation in SQL queries
        if re.search(r'(SELECT|INSERT|UPDATE|DELETE|WHERE).*\+.*\$\{', line, re.IGNORECASE):
            self.add_issue(
                file, line_num, 'CRITICAL', 'SQL Injection',
                'Potential SQL injection: String concatenation in SQL query. Use parameterized queries.',
                line
            )

        # Template literals in SQL
        if re.search(r'sql`.*\$\{[^}]+\}', line):
            # Check if it's using Drizzle placeholders correctly
            if 'sql`' in line and '${' in line and not re.search(r'sql\s*`[^`]*\$\{users\.[a-zA-Z]+\}', line):
                self.add_issue(
                    file, line_num, 'HIGH', 'SQL Injection',
                    'Potential SQL injection: Unvalidated template literal in SQL. Use Drizzle placeholders.',
                    line
                )

    def check_xss(self, file: Path, line_num: int, line: str):
        """Check for XSS vulnerabilities"""
        # dangerouslySetInnerHTML without DOMPurify
        if 'dangerouslySetInnerHTML' in line and 'DOMPurify' not in line:
            self.add_issue(
                file, line_num, 'HIGH', 'XSS',
                'dangerouslySetInnerHTML without DOMPurify sanitization. Risk of XSS attack.',
                line
            )

        # innerHTML assignment
        if re.search(r'\.innerHTML\s*=', line):
            self.add_issue(
                file, line_num, 'HIGH', 'XSS',
                'Direct innerHTML assignment. Use textContent or sanitize with DOMPurify.',
                line
            )

    def check_eval_usage(self, file: Path, line_num: int, line: str):
        """Check for eval() or Function() usage"""
        if re.search(r'\beval\s*\(', line):
            self.add_issue(
                file, line_num, 'CRITICAL', 'Code Injection',
                'eval() usage detected. This is extremely dangerous and allows arbitrary code execution.',
                line
            )

        if re.search(r'new\s+Function\s*\(', line):
            self.add_issue(
                file, line_num, 'CRITICAL', 'Code Injection',
                'Function() constructor usage detected. This allows arbitrary code execution.',
                line
            )

    def check_weak_crypto(self, file: Path, line_num: int, line: str):
        """Check for weak cryptographic algorithms"""
        weak_algorithms = ['md5', 'sha1', 'des', 'rc4']

        for algo in weak_algorithms:
            if re.search(rf'\b{algo}\b', line, re.IGNORECASE):
                self.add_issue(
                    file, line_num, 'HIGH', 'Weak Cryptography',
                    f'{algo.upper()} is cryptographically weak. Use SHA-256 or stronger.',
                    line
                )

    def check_insecure_randomness(self, file: Path, line_num: int, line: str):
        """Check for insecure random number generation"""
        if re.search(r'Math\.random\(\)', line) and any(word in line for word in ['token', 'session', 'id', 'key', 'secret']):
            self.add_issue(
                file, line_num, 'MEDIUM', 'Weak Randomness',
                'Math.random() is not cryptographically secure. Use crypto.randomBytes() for security tokens.',
                line
            )

    def check_command_injection(self, file: Path, line_num: int, line: str):
        """Check for command injection vulnerabilities"""
        # exec with template literal
        if re.search(r'exec\s*\(\s*`', line):
            self.add_issue(
                file, line_num, 'CRITICAL', 'Command Injection',
                'exec() with template literal. Use spawn() with array arguments instead.',
                line
            )

        # exec with variable
        if re.search(r'exec\s*\([^\'"]', line):
            self.add_issue(
                file, line_num, 'HIGH', 'Command Injection',
                'exec() with variable input. Use spawn() with array arguments instead.',
                line
            )

        # spawn with shell: true
        if 'spawn(' in line and 'shell: true' in line:
            self.add_issue(
                file, line_num, 'HIGH', 'Command Injection',
                'spawn() with shell: true. Set shell: false to prevent command injection.',
                line
            )

    def check_path_traversal(self, file: Path, line_num: int, line: str):
        """Check for path traversal vulnerabilities"""
        # Direct file path from user input
        if re.search(r'(readFile|writeFile|unlink|rmdir|mkdir)\s*\([^)]*req\.(body|query|params)', line):
            self.add_issue(
                file, line_num, 'HIGH', 'Path Traversal',
                'File operation with user input. Validate and sanitize file paths.',
                line
            )

        # path.join with user input
        if 'path.join' in line and any(word in line for word in ['req.', 'params.', 'query.', 'body.']):
            self.add_issue(
                file, line_num, 'MEDIUM', 'Path Traversal',
                'path.join() with user input. Validate against directory traversal (../).',
                line
            )

    def check_weak_password_hash(self, file: Path, line_num: int, line: str):
        """Check for weak password hashing"""
        # bcrypt with low rounds
        if 'bcrypt.hash' in line:
            match = re.search(r'bcrypt\.hash\([^,]+,\s*(\d+)', line)
            if match and int(match.group(1)) < 10:
                self.add_issue(
                    file, line_num, 'HIGH', 'Weak Password Hash',
                    f'bcrypt rounds too low ({match.group(1)}). Use 12+ rounds.',
                    line
                )

        # Password stored without hashing
        if re.search(r'(password|passwd)\s*:\s*[^b]', line) and 'bcrypt' not in line and 'hash' not in line.lower():
            if 'create' in line.lower() or 'insert' in line.lower() or 'update' in line.lower():
                self.add_issue(
                    file, line_num, 'CRITICAL', 'Plaintext Password',
                    'Password may be stored without hashing. Always hash passwords with bcrypt.',
                    line
                )

    def check_jwt_security(self, file: Path, line_num: int, line: str):
        """Check for JWT security issues"""
        # Weak JWT secret
        if 'jwt.sign' in line and re.search(r'["\'][a-zA-Z0-9]{1,16}["\']', line):
            self.add_issue(
                file, line_num, 'HIGH', 'Weak JWT Secret',
                'JWT secret appears weak. Use a strong random secret from environment variables.',
                line
            )

        # JWT without expiration
        if 'jwt.sign' in line and 'expiresIn' not in line:
            self.add_issue(
                file, line_num, 'MEDIUM', 'JWT No Expiration',
                'JWT token without expiration. Set expiresIn option.',
                line
            )

    def check_missing_auth(self, file: Path, line_num: int, line: str):
        """Check for missing authentication in API routes"""
        # API route handler without auth check
        if 'export async function' in line and any(method in line for method in ['POST', 'PUT', 'PATCH', 'DELETE']):
            # This is a basic check - might have false positives
            # Real implementation should check entire function body
            pass  # Placeholder for more sophisticated check

    def check_cors_misconfiguration(self, file: Path, line_num: int, line: str):
        """Check for CORS misconfigurations"""
        # CORS with wildcard and credentials
        if "Access-Control-Allow-Origin" in line and "*" in line:
            self.add_issue(
                file, line_num, 'HIGH', 'CORS Misconfiguration',
                'CORS allows all origins (*). Use a whitelist of allowed origins.',
                line
            )

        if "Access-Control-Allow-Credentials" in line and "true" in line:
            # Check if origin is wildcard (should check nearby lines)
            self.add_issue(
                file, line_num, 'MEDIUM', 'CORS Misconfiguration',
                'CORS credentials enabled. Ensure Access-Control-Allow-Origin is not wildcard.',
                line
            )

    def check_http_only_cookies(self, file: Path, line_num: int, line: str):
        """Check for missing httpOnly flag on cookies"""
        if 'Set-Cookie' in line or 'setCookie' in line or 'cookies.set' in line:
            if 'httpOnly' not in line and 'HttpOnly' not in line:
                self.add_issue(
                    file, line_num, 'MEDIUM', 'Insecure Cookie',
                    'Cookie without httpOnly flag. Add httpOnly: true to prevent XSS access.',
                    line
                )

            if 'secure' not in line and 'Secure' not in line:
                self.add_issue(
                    file, line_num, 'MEDIUM', 'Insecure Cookie',
                    'Cookie without secure flag. Add secure: true for HTTPS-only.',
                    line
                )

    def check_ts_ignore(self, file: Path, line_num: int, line: str):
        """Check for @ts-ignore comments"""
        if '@ts-ignore' in line:
            self.add_issue(
                file, line_num, 'LOW', 'TypeScript',
                '@ts-ignore suppresses type checking. Fix the underlying type issue instead.',
                line
            )

    def check_any_type(self, file: Path, line_num: int, line: str):
        """Check for 'any' type usage"""
        if re.search(r':\s*any\b', line) and 'eslint-disable' not in line:
            self.add_issue(
                file, line_num, 'LOW', 'TypeScript',
                "'any' type defeats TypeScript's purpose. Use specific types.",
                line
            )

    def check_console_log(self, file: Path, line_num: int, line: str):
        """Check for console.log in production code"""
        if re.search(r'\bconsole\.(log|debug|info)\(', line) and 'src/lib/logger' not in str(file):
            self.add_issue(
                file, line_num, 'LOW', 'Code Quality',
                'console.log() in production code. Use proper logger instead.',
                line
            )

def print_results(issues: List[SecurityIssue]):
    """Print scan results"""
    if not issues:
        print("✅ No security issues found!\n")
        return

    # Group by severity
    critical = [i for i in issues if i.severity == 'CRITICAL']
    high = [i for i in issues if i.severity == 'HIGH']
    medium = [i for i in issues if i.severity == 'MEDIUM']
    low = [i for i in issues if i.severity == 'LOW']

    print(f"⚠️  Found {len(issues)} security issues:\n")
    print(f"  🔴 CRITICAL: {len(critical)}")
    print(f"  🟠 HIGH:     {len(high)}")
    print(f"  🟡 MEDIUM:   {len(medium)}")
    print(f"  🟢 LOW:      {len(low)}")
    print()

    # Print details
    for severity, issues_list, emoji in [
        ('CRITICAL', critical, '🔴'),
        ('HIGH', high, '🟠'),
        ('MEDIUM', medium, '🟡'),
        ('LOW', low, '🟢'),
    ]:
        if not issues_list:
            continue

        print(f"{emoji} {severity} Issues:")
        print("=" * 80)

        for issue in issues_list:
            print(f"\n📁 {issue.file}:{issue.line}")
            print(f"📌 {issue.category}: {issue.message}")
            print(f"💾 {issue.code_snippet}")
            print()

        print()

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = '.'

    if not os.path.exists(path):
        print(f"❌ Path does not exist: {path}")
        sys.exit(1)

    scanner = SecurityScanner(path)
    issues = scanner.scan()
    print_results(issues)

    # Exit with error code if critical or high issues found
    critical_or_high = [i for i in issues if i.severity in ['CRITICAL', 'HIGH']]
    if critical_or_high:
        print(f"❌ Found {len(critical_or_high)} critical/high severity issues.")
        print("   Fix these issues before deployment!")
        sys.exit(1)
    else:
        print("✅ No critical or high severity issues found.")
        sys.exit(0)

if __name__ == '__main__':
    main()
