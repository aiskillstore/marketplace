#!/usr/bin/env python3
"""
AST-based semantic analysis for security vulnerabilities
Provides more accurate detection than regex patterns
"""
import ast
import json
from typing import List, Dict, Any, Optional
from pathlib import Path


class SecurityVisitor(ast.NodeVisitor):
    """AST visitor to detect security issues in Python code"""
    
    def __init__(self):
        self.issues = []
        self.tainted_vars = set()
        
    def visit_Call(self, node: ast.Call) -> None:
        """Detect dangerous function calls"""
        if isinstance(node.func, ast.Name):
            # Check for dangerous builtins
            if node.func.id in ['eval', 'exec', '__import__']:
                self.issues.append({
                    'type': 'code-injection',
                    'severity': 'critical',
                    'line': node.lineno,
                    'function': node.func.id,
                    'message': f'Dangerous use of {node.func.id}()'
                })
            
            # Check for pickle
            if node.func.id == 'loads' and len(node.args) > 0:
                self.issues.append({
                    'type': 'deserialization',
                    'severity': 'critical',
                    'line': node.lineno,
                    'message': 'Potentially unsafe deserialization'
                })
        
        elif isinstance(node.func, ast.Attribute):
            # Check for os.system
            if node.func.attr == 'system':
                self.issues.append({
                    'type': 'command-injection',
                    'severity': 'critical',
                    'line': node.lineno,
                    'message': 'Use of os.system() - prefer subprocess'
                })
            
            # Check for SQL execute with f-strings
            if node.func.attr == 'execute' and len(node.args) > 0:
                if isinstance(node.args[0], ast.JoinedStr):
                    self.issues.append({
                        'type': 'sql-injection',
                        'severity': 'critical',
                        'line': node.lineno,
                        'message': 'SQL query uses f-string - use parameterized queries'
                    })
        
        self.generic_visit(node)
    
    def visit_Assign(self, node: ast.Assign) -> None:
        """Track variable assignments for taint analysis"""
        for target in node.targets:
            if isinstance(target, ast.Name):
                # Check if assigned value comes from user input
                if self._is_user_input(node.value):
                    self.tainted_vars.add(target.id)
        
        self.generic_visit(node)
    
    def _is_user_input(self, node: ast.AST) -> bool:
        """Check if a node represents user input"""
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                return node.func.id in ['input', 'raw_input']
            if isinstance(node.func, ast.Attribute):
                return node.func.attr in ['get', 'post', 'request']
        return False


class JavaScriptSecurityAnalyzer:
    """JavaScript/TypeScript security analyzer using regex + heuristics"""
    
    def __init__(self, code: str):
        self.code = code
        self.lines = code.split('\n')
        self.issues = []
    
    def analyze(self) -> List[Dict[str, Any]]:
        """Analyze JavaScript code for security issues"""
        self._check_sql_injection()
        self._check_xss()
        self._check_command_injection()
        self._check_eval()
        self._check_dangerous_functions()
        return self.issues
    
    def _check_sql_injection(self):
        """Detect SQL injection patterns"""
        for i, line in enumerate(self.lines, 1):
            # Template literals in queries
            if 'query' in line.lower() and '${' in line:
                self.issues.append({
                    'type': 'sql-injection',
                    'severity': 'critical',
                    'line': i,
                    'message': 'SQL query uses template literal - use parameterized queries',
                    'code': line.strip()
                })
            # String concatenation in queries
            if 'query' in line.lower() and ('+' in line or 'concat' in line.lower()):
                self.issues.append({
                    'type': 'sql-injection',
                    'severity': 'critical',
                    'line': i,
                    'message': 'SQL query uses string concatenation',
                    'code': line.strip()
                })
    
    def _check_xss(self):
        """Detect XSS vulnerabilities"""
        for i, line in enumerate(self.lines, 1):
            if '.innerHTML' in line and '=' in line:
                self.issues.append({
                    'type': 'xss',
                    'severity': 'high',
                    'line': i,
                    'message': 'Potential XSS via innerHTML - use textContent or sanitize',
                    'code': line.strip()
                })
            if 'dangerouslySetInnerHTML' in line:
                self.issues.append({
                    'type': 'xss',
                    'severity': 'high',
                    'line': i,
                    'message': 'React dangerouslySetInnerHTML detected - ensure sanitization',
                    'code': line.strip()
                })
    
    def _check_command_injection(self):
        """Detect command injection patterns"""
        dangerous_functions = ['exec', 'spawn', 'execSync', 'spawnSync']
        for i, line in enumerate(self.lines, 1):
            for func in dangerous_functions:
                if func in line and ('${' in line or '+' in line):
                    self.issues.append({
                        'type': 'command-injection',
                        'severity': 'critical',
                        'line': i,
                        'message': f'Command execution with {func}() and dynamic input',
                        'code': line.strip()
                    })
    
    def _check_eval(self):
        """Detect use of eval"""
        for i, line in enumerate(self.lines, 1):
            if 'eval(' in line:
                self.issues.append({
                    'type': 'code-injection',
                    'severity': 'critical',
                    'line': i,
                    'message': 'Use of eval() is dangerous - find alternative approach',
                    'code': line.strip()
                })
    
    def _check_dangerous_functions(self):
        """Check for other dangerous patterns"""
        patterns = {
            'new Function(': ('code-injection', 'critical', 'Dynamic function creation'),
            'crypto.createHash(\'md5\')': ('weak-crypto', 'high', 'MD5 is cryptographically broken'),
            'Math.random()': ('weak-random', 'medium', 'Math.random() not suitable for security'),
        }
        
        for i, line in enumerate(self.lines, 1):
            for pattern, (vuln_type, severity, message) in patterns.items():
                if pattern in line:
                    self.issues.append({
                        'type': vuln_type,
                        'severity': severity,
                        'line': i,
                        'message': message,
                        'code': line.strip()
                    })


def analyze_file(filepath: str, language: str = None) -> Dict[str, Any]:
    """
    Analyze a file for security vulnerabilities using AST when possible
    
    Args:
        filepath: Path to the file to analyze
        language: Programming language (auto-detected if None)
    
    Returns:
        Dictionary with analysis results
    """
    path = Path(filepath)
    
    if not path.exists():
        return {'error': 'File not found'}
    
    # Auto-detect language
    if language is None:
        ext = path.suffix.lower()
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript'
        }
        language = language_map.get(ext, 'unknown')
    
    code = path.read_text()
    
    # Use appropriate analyzer
    if language == 'python':
        try:
            tree = ast.parse(code)
            visitor = SecurityVisitor()
            visitor.visit(tree)
            return {
                'file': str(path),
                'language': language,
                'method': 'ast',
                'issues': visitor.issues
            }
        except SyntaxError as e:
            return {
                'error': f'Syntax error: {e}',
                'file': str(path)
            }
    
    elif language in ['javascript', 'typescript']:
        analyzer = JavaScriptSecurityAnalyzer(code)
        issues = analyzer.analyze()
        return {
            'file': str(path),
            'language': language,
            'method': 'heuristic',
            'issues': issues
        }
    
    return {
        'file': str(path),
        'language': language,
        'error': 'Language not supported for AST analysis'
    }


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print('Usage: python ast_analyzer.py <file>')
        sys.exit(1)
    
    result = analyze_file(sys.argv[1])
    print(json.dumps(result, indent=2))
