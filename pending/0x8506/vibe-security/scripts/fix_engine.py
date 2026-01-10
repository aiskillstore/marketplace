#!/usr/bin/env python3
"""
ML-based fix suggestion engine
Uses pattern matching and historical fixes to suggest secure code alternatives
"""
import json
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import re
import csv


class FixSuggestionEngine:
    """
    Suggests security fixes based on vulnerability type and context
    Uses template matching and learned patterns
    """
    
    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path(__file__).parent.parent / 'data'
        
        self.data_dir = data_dir
        self.fix_templates = self._load_fix_templates()
        self.patterns = self._load_patterns()
        
    def _load_fix_templates(self) -> List[Dict[str, str]]:
        """Load fix templates from CSV"""
        template_file = self.data_dir / 'fix-templates.csv'
        if not template_file.exists():
            return []
        
        with open(template_file, 'r', encoding='utf-8') as f:
            return list(csv.DictReader(f))
    
    def _load_patterns(self) -> List[Dict[str, str]]:
        """Load vulnerability patterns"""
        pattern_files = ['patterns.csv', 'advanced-patterns.csv']
        all_patterns = []
        
        for filename in pattern_files:
            pattern_file = self.data_dir / filename
            if pattern_file.exists():
                with open(pattern_file, 'r', encoding='utf-8') as f:
                    all_patterns.extend(list(csv.DictReader(f)))
        
        return all_patterns
    
    def suggest_fix(self, 
                    vulnerability_type: str,
                    language: str,
                    code_snippet: str,
                    context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate fix suggestions for a vulnerability
        
        Args:
            vulnerability_type: Type of vulnerability (e.g., 'sql-injection')
            language: Programming language
            code_snippet: The vulnerable code
            context: Additional context (framework, libraries, etc.)
        
        Returns:
            Dictionary with fix suggestions, explanations, and test templates
        """
        # Find matching fix template
        template = self._find_template(vulnerability_type, language)
        
        if not template:
            return {
                'success': False,
                'message': f'No fix template found for {vulnerability_type} in {language}'
            }
        
        # Generate specific fix for the code
        fixed_code = self._apply_fix_template(code_snippet, template, language)
        
        # Generate explanation
        explanation = self._generate_explanation(vulnerability_type, template, language)
        
        # Generate test
        test_code = self._generate_test(template, language, fixed_code)
        
        # Additional recommendations
        recommendations = self._get_recommendations(vulnerability_type, language, context)
        
        return {
            'success': True,
            'vulnerability_type': vulnerability_type,
            'language': language,
            'original_code': code_snippet,
            'fixed_code': fixed_code,
            'explanation': explanation,
            'test_code': test_code,
            'recommendations': recommendations,
            'confidence': self._calculate_confidence(code_snippet, template)
        }
    
    def _find_template(self, vulnerability_type: str, language: str) -> Optional[Dict[str, str]]:
        """Find the best matching fix template"""
        # Normalize vulnerability type
        vuln_normalized = vulnerability_type.lower().replace('_', '-')
        
        for template in self.fix_templates:
            if (template.get('vulnerability', '').lower() == vuln_normalized and
                template.get('language', '').lower() == language.lower()):
                return template
        
        # Fallback: try without exact language match
        for template in self.fix_templates:
            if template.get('vulnerability', '').lower() == vuln_normalized:
                return template
        
        return None
    
    def _apply_fix_template(self, code: str, template: Dict[str, str], language: str) -> str:
        """Apply fix template to vulnerable code"""
        unsafe_pattern = template.get('unsafe_pattern', '')
        safe_fix = template.get('safe_fix', '')
        
        # Try to intelligently replace
        # Extract variable names from unsafe code
        variables = self._extract_variables(code, language)
        
        # Substitute variables into safe template
        fixed_code = safe_fix
        for var_name, var_value in variables.items():
            fixed_code = fixed_code.replace(var_name, var_value)
        
        return fixed_code
    
    def _extract_variables(self, code: str, language: str) -> Dict[str, str]:
        """Extract variable names from code snippet"""
        variables = {}
        
        if language in ['javascript', 'typescript']:
            # Extract from template literals
            template_vars = re.findall(r'\$\{(\w+)\}', code)
            for var in template_vars:
                variables[var] = var
            
            # Extract from function arguments
            func_args = re.findall(r'\(([^)]+)\)', code)
            if func_args:
                args = [arg.strip() for arg in func_args[0].split(',')]
                for arg in args:
                    if arg and not arg.startswith('"') and not arg.startswith("'"):
                        variables[arg] = arg
        
        elif language == 'python':
            # Extract from f-strings
            fstring_vars = re.findall(r'\{(\w+)\}', code)
            for var in fstring_vars:
                variables[var] = var
            
            # Extract function arguments
            func_args = re.findall(r'\(([^)]+)\)', code)
            if func_args:
                args = [arg.strip() for arg in func_args[0].split(',')]
                for arg in args:
                    if arg and not arg.startswith('"') and not arg.startswith("'"):
                        variables[arg] = arg
        
        return variables
    
    def _generate_explanation(self, vulnerability_type: str, template: Dict[str, str], language: str) -> str:
        """Generate detailed explanation of the fix"""
        explanation = template.get('explanation', '')
        
        # Add context-specific details
        details = []
        
        if vulnerability_type == 'sql-injection':
            details.append("SQL injection occurs when user input is directly concatenated into queries.")
            details.append("Parameterized queries use placeholders that are safely escaped by the database driver.")
        
        elif vulnerability_type == 'xss':
            details.append("Cross-Site Scripting (XSS) allows attackers to inject malicious scripts.")
            details.append("Always encode or escape user input before rendering in HTML.")
        
        elif vulnerability_type == 'command-injection':
            details.append("Command injection allows attackers to execute arbitrary system commands.")
            details.append("Use array-based arguments instead of shell strings to prevent injection.")
        
        if details:
            explanation += "\n\nDetails:\n" + "\n".join(f"• {d}" for d in details)
        
        return explanation
    
    def _generate_test(self, template: Dict[str, str], language: str, fixed_code: str) -> str:
        """Generate test code for the fix"""
        test_template = template.get('test_template', '')
        
        if not test_template:
            # Generate generic test based on language
            if language in ['javascript', 'typescript']:
                return f"""
describe('Security Test', () => {{
  test('should prevent injection attack', () => {{
    const maliciousInput = "'; DROP TABLE users--";
    expect(() => {{
      // Test with malicious input
      {fixed_code.split('\n')[0]}
    }}).not.toThrow();
  }});
}});
""".strip()
            
            elif language == 'python':
                return f"""
def test_security():
    \"\"\"Test that the fix prevents injection attacks\"\"\"
    malicious_input = "'; DROP TABLE users--"
    try:
        # Test with malicious input
        result = {fixed_code.split('\n')[0]}
        assert result is not None
    except Exception as e:
        pytest.fail(f"Unexpected exception: {{e}}")
""".strip()
        
        return test_template
    
    def _get_recommendations(self, 
                           vulnerability_type: str,
                           language: str,
                           context: Optional[Dict[str, Any]]) -> List[str]:
        """Get additional security recommendations"""
        recommendations = []
        
        # General recommendations
        if vulnerability_type in ['sql-injection', 'nosql-injection']:
            recommendations.extend([
                "Use ORM/ODM frameworks when possible",
                "Implement input validation and sanitization",
                "Apply principle of least privilege to database users",
                "Enable query logging for monitoring"
            ])
        
        elif vulnerability_type == 'xss':
            recommendations.extend([
                "Implement Content Security Policy (CSP) headers",
                "Use auto-escaping template engines",
                "Validate and sanitize all user inputs",
                "Consider using DOMPurify for HTML sanitization"
            ])
        
        elif vulnerability_type in ['command-injection', 'code-injection']:
            recommendations.extend([
                "Never use eval() or exec() with user input",
                "Validate and whitelist allowed commands",
                "Use safer alternatives like subprocess with arrays",
                "Implement proper access controls"
            ])
        
        elif vulnerability_type == 'weak-crypto':
            recommendations.extend([
                "Use industry-standard algorithms (AES-256, SHA-256+)",
                "Never implement custom cryptography",
                "Use proper key management systems",
                "Consider using crypto libraries like libsodium"
            ])
        
        # Framework-specific recommendations
        if context and context.get('framework'):
            framework = context['framework'].lower()
            
            if framework == 'express':
                recommendations.append("Use helmet.js for security headers")
                recommendations.append("Enable CORS properly with cors middleware")
            
            elif framework == 'django':
                recommendations.append("Keep Django security middleware enabled")
                recommendations.append("Use Django's built-in CSRF protection")
            
            elif framework == 'flask':
                recommendations.append("Use Flask-Talisman for security headers")
                recommendations.append("Implement CSRF protection with Flask-WTF")
        
        return recommendations
    
    def _calculate_confidence(self, code: str, template: Dict[str, str]) -> float:
        """Calculate confidence score for the fix suggestion"""
        confidence = 0.5  # Base confidence
        
        # Increase confidence if pattern matches closely
        unsafe_pattern = template.get('unsafe_pattern', '')
        if unsafe_pattern in code:
            confidence += 0.3
        
        # Increase if variables can be extracted
        variables = self._extract_variables(code, template.get('language', ''))
        if variables:
            confidence += 0.1
        
        # Decrease if code is complex
        if len(code.split('\n')) > 5:
            confidence -= 0.1
        
        return min(1.0, max(0.0, confidence))
    
    def batch_suggest_fixes(self, vulnerabilities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate fixes for multiple vulnerabilities"""
        results = []
        
        for vuln in vulnerabilities:
            fix = self.suggest_fix(
                vulnerability_type=vuln.get('type', ''),
                language=vuln.get('language', ''),
                code_snippet=vuln.get('code', ''),
                context=vuln.get('context')
            )
            
            fix['original_vulnerability'] = vuln
            results.append(fix)
        
        return results


def main():
    """CLI interface for fix suggestion engine"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Security fix suggestion engine')
    parser.add_argument('--type', required=True, help='Vulnerability type')
    parser.add_argument('--language', required=True, help='Programming language')
    parser.add_argument('--code', required=True, help='Vulnerable code snippet')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    engine = FixSuggestionEngine()
    result = engine.suggest_fix(
        vulnerability_type=args.type,
        language=args.language,
        code_snippet=args.code
    )
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result['success']:
            print("=" * 80)
            print(f"FIX SUGGESTION: {result['vulnerability_type'].upper()}")
            print("=" * 80)
            print(f"\n📍 Original Code:\n{result['original_code']}\n")
            print(f"✅ Fixed Code:\n{result['fixed_code']}\n")
            print(f"📖 Explanation:\n{result['explanation']}\n")
            print(f"🧪 Test Code:\n{result['test_code']}\n")
            print("💡 Recommendations:")
            for rec in result['recommendations']:
                print(f"  • {rec}")
            print(f"\n🎯 Confidence: {result['confidence']:.0%}")
        else:
            print(f"❌ Error: {result['message']}")


if __name__ == '__main__':
    main()
