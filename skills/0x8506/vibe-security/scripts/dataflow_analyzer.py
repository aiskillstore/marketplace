#!/usr/bin/env python3
"""
Data flow analysis for tracking tainted data from sources to sinks
Detects security vulnerabilities by following data propagation
"""
import ast
from typing import Set, Dict, List, Tuple, Any
from collections import defaultdict
import json


class TaintAnalyzer(ast.NodeVisitor):
    """
    Performs taint analysis to track data flow from sources (user input) 
    to sinks (dangerous operations)
    """
    
    # Define sources of untrusted data
    TAINT_SOURCES = {
        'input', 'raw_input', 'sys.stdin.read', 
        'request.args.get', 'request.form.get', 'request.get_json',
        'flask.request.args', 'flask.request.form',
        'django.request.GET', 'django.request.POST'
    }
    
    # Define dangerous sinks
    TAINT_SINKS = {
        'eval': 'code-injection',
        'exec': 'code-injection',
        'compile': 'code-injection',
        '__import__': 'code-injection',
        'os.system': 'command-injection',
        'subprocess.call': 'command-injection',
        'subprocess.run': 'command-injection',
        'subprocess.Popen': 'command-injection',
        'cursor.execute': 'sql-injection',
        'connection.execute': 'sql-injection',
        'pickle.loads': 'deserialization',
        'yaml.load': 'deserialization',
        'open': 'path-traversal'
    }
    
    def __init__(self):
        self.tainted_vars: Set[str] = set()
        self.var_dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.issues: List[Dict[str, Any]] = []
        self.function_context: List[str] = []
        
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Track function context for better reporting"""
        self.function_context.append(node.name)
        
        # Check if function parameters might be tainted
        for arg in node.args.args:
            if any(keyword in arg.arg.lower() for keyword in ['user', 'input', 'param', 'request']):
                self.tainted_vars.add(arg.arg)
        
        self.generic_visit(node)
        self.function_context.pop()
    
    def visit_Assign(self, node: ast.Assign) -> None:
        """Track variable assignments and taint propagation"""
        # Get all target variable names
        targets = []
        for target in node.targets:
            if isinstance(target, ast.Name):
                targets.append(target.id)
        
        # Check if value is from a taint source
        if self._is_taint_source(node.value):
            for target in targets:
                self.tainted_vars.add(target)
        
        # Check if value depends on tainted variables
        dependencies = self._get_dependencies(node.value)
        for target in targets:
            self.var_dependencies[target] = dependencies
            if any(dep in self.tainted_vars for dep in dependencies):
                self.tainted_vars.add(target)
        
        self.generic_visit(node)
    
    def visit_Call(self, node: ast.Call) -> None:
        """Check if tainted data flows to dangerous sinks"""
        func_name = self._get_function_name(node.func)
        
        if func_name in self.TAINT_SINKS:
            # Check all arguments for tainted data
            for arg in node.args:
                arg_deps = self._get_dependencies(arg)
                tainted_deps = arg_deps & self.tainted_vars
                
                if tainted_deps:
                    vulnerability = self.TAINT_SINKS[func_name]
                    self.issues.append({
                        'type': vulnerability,
                        'severity': 'critical',
                        'line': node.lineno,
                        'function': func_name,
                        'context': '.'.join(self.function_context) if self.function_context else 'global',
                        'tainted_vars': list(tainted_deps),
                        'message': f'Tainted data from {tainted_deps} flows to dangerous sink {func_name}()',
                        'recommendation': self._get_recommendation(vulnerability)
                    })
        
        self.generic_visit(node)
    
    def _is_taint_source(self, node: ast.AST) -> bool:
        """Check if a node represents a taint source"""
        if isinstance(node, ast.Call):
            func_name = self._get_function_name(node.func)
            return func_name in self.TAINT_SOURCES
        return False
    
    def _get_function_name(self, node: ast.AST) -> str:
        """Extract full function name from call node"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            base = self._get_function_name(node.value)
            return f"{base}.{node.attr}" if base else node.attr
        return ""
    
    def _get_dependencies(self, node: ast.AST) -> Set[str]:
        """Get all variable names that a node depends on"""
        deps = set()
        
        if isinstance(node, ast.Name):
            deps.add(node.id)
        elif isinstance(node, ast.Call):
            for arg in node.args:
                deps.update(self._get_dependencies(arg))
        elif isinstance(node, ast.BinOp):
            deps.update(self._get_dependencies(node.left))
            deps.update(self._get_dependencies(node.right))
        elif isinstance(node, ast.JoinedStr):
            for value in node.values:
                if isinstance(value, ast.FormattedValue):
                    deps.update(self._get_dependencies(value.value))
        elif isinstance(node, ast.Subscript):
            deps.update(self._get_dependencies(node.value))
        
        return deps
    
    def _get_recommendation(self, vulnerability: str) -> str:
        """Get remediation recommendation for vulnerability type"""
        recommendations = {
            'code-injection': 'Avoid eval/exec with user input. Use safer alternatives like ast.literal_eval() or configuration files.',
            'command-injection': 'Use subprocess with list arguments instead of shell=True. Validate and sanitize all inputs.',
            'sql-injection': 'Use parameterized queries or ORM methods. Never concatenate SQL with user input.',
            'deserialization': 'Avoid pickle/yaml.load with untrusted data. Use JSON or validate input strictly.',
            'path-traversal': 'Validate file paths, use os.path.join() and check if path is within allowed directory.'
        }
        return recommendations.get(vulnerability, 'Sanitize and validate all user inputs.')


class JavaScriptDataFlowAnalyzer:
    """JavaScript data flow analyzer using pattern matching"""
    
    def __init__(self, code: str):
        self.code = code
        self.lines = code.split('\n')
        self.issues = []
        self.tainted_vars = set()
        
        # Common sources of user input in JavaScript
        self.sources = [
            'req.body', 'req.query', 'req.params', 'req.cookies',
            'process.argv', 'window.location', 'document.cookie',
            'localStorage.getItem', 'sessionStorage.getItem'
        ]
        
        # Dangerous sinks
        self.sinks = {
            'eval(': 'code-injection',
            'Function(': 'code-injection',
            'setTimeout(': 'code-injection',
            'setInterval(': 'code-injection',
            '.innerHTML': 'xss',
            'document.write(': 'xss',
            'exec(': 'command-injection',
            'execSync(': 'command-injection',
            'query(': 'sql-injection'
        }
    
    def analyze(self) -> List[Dict[str, Any]]:
        """Perform data flow analysis"""
        # First pass: identify tainted variables
        for i, line in enumerate(self.lines, 1):
            for source in self.sources:
                if source in line and '=' in line:
                    # Extract variable name
                    parts = line.split('=')
                    if parts:
                        var_name = parts[0].strip().split()[-1]
                        self.tainted_vars.add(var_name)
        
        # Second pass: check if tainted data reaches sinks
        for i, line in enumerate(self.lines, 1):
            for sink, vuln_type in self.sinks.items():
                if sink in line:
                    # Check if any tainted variable is used
                    for var in self.tainted_vars:
                        if var in line:
                            self.issues.append({
                                'type': vuln_type,
                                'severity': 'critical',
                                'line': i,
                                'sink': sink,
                                'tainted_var': var,
                                'message': f'Tainted variable "{var}" flows to dangerous sink {sink}',
                                'code': line.strip()
                            })
                            break
        
        return self.issues


def analyze_dataflow(filepath: str, language: str = None) -> Dict[str, Any]:
    """
    Perform data flow analysis on a file
    
    Args:
        filepath: Path to file
        language: Programming language (auto-detected if None)
    
    Returns:
        Analysis results with identified vulnerabilities
    """
    from pathlib import Path
    
    path = Path(filepath)
    if not path.exists():
        return {'error': 'File not found'}
    
    # Auto-detect language
    if language is None:
        ext = path.suffix.lower()
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'javascript'
        }
        language = language_map.get(ext, 'unknown')
    
    code = path.read_text()
    
    if language == 'python':
        try:
            tree = ast.parse(code)
            analyzer = TaintAnalyzer()
            analyzer.visit(tree)
            
            return {
                'file': str(path),
                'language': language,
                'tainted_variables': list(analyzer.tainted_vars),
                'issues': analyzer.issues,
                'total_issues': len(analyzer.issues)
            }
        except SyntaxError as e:
            return {'error': f'Syntax error: {e}', 'file': str(path)}
    
    elif language == 'javascript':
        analyzer = JavaScriptDataFlowAnalyzer(code)
        issues = analyzer.analyze()
        
        return {
            'file': str(path),
            'language': language,
            'tainted_variables': list(analyzer.tainted_vars),
            'issues': issues,
            'total_issues': len(issues)
        }
    
    return {'error': 'Language not supported for data flow analysis'}


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print('Usage: python dataflow_analyzer.py <file>')
        sys.exit(1)
    
    result = analyze_dataflow(sys.argv[1])
    print(json.dumps(result, indent=2))
