#!/usr/bin/env python3
"""
Code Annotator - Adds educational comments to code

This script helps create teaching-friendly code by adding structured
comments that explain what each section does.
"""

import sys
import re
from typing import List, Tuple

def annotate_code(code: str, language: str = "python") -> str:
    """
    Add structured annotation markers to code.
    
    Args:
        code: The source code to annotate
        language: Programming language (python, javascript, typescript)
        
    Returns:
        Code with annotation markers added
    """
    lines = code.split('\n')
    annotated = []
    
    comment_char = get_comment_char(language)
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Add section markers for major code blocks
        if is_function_def(stripped, language):
            annotated.append(f"{comment_char} === FUNCTION: {extract_function_name(stripped, language)} ===")
            annotated.append(f"{comment_char} Purpose: [Explain what this function does]")
            annotated.append(f"{comment_char} Parameters: [Explain parameters]")
            annotated.append(f"{comment_char} Returns: [Explain return value]")
        
        elif is_class_def(stripped, language):
            annotated.append(f"{comment_char} === CLASS: {extract_class_name(stripped)} ===")
            annotated.append(f"{comment_char} Purpose: [Explain what this class represents]")
        
        elif is_loop(stripped, language):
            annotated.append(f"{comment_char} LOOP: [Explain what we're iterating over and why]")
        
        elif is_conditional(stripped, language):
            annotated.append(f"{comment_char} CONDITION: [Explain what we're checking]")
        
        elif is_variable_assignment(stripped, language):
            var_name = extract_variable_name(stripped, language)
            annotated.append(f"{comment_char} Variable '{var_name}': [Explain what this stores]")
        
        # Add the original line
        annotated.append(line)
        
        # Add teaching notes for common patterns
        if is_return_statement(stripped, language):
            annotated.append(f"{comment_char} ^ Returns: [Explain what value is returned]")
    
    return '\n'.join(annotated)

def get_comment_char(language: str) -> str:
    """Get the comment character for a language."""
    if language in ["python"]:
        return "#"
    elif language in ["javascript", "typescript", "java", "c", "cpp"]:
        return "//"
    return "#"

def is_function_def(line: str, language: str) -> bool:
    """Check if line is a function definition."""
    if language == "python":
        return line.startswith("def ") and ":" in line
    elif language in ["javascript", "typescript"]:
        return ("function " in line or "=>" in line) and "{" in line
    return False

def is_class_def(line: str, language: str) -> bool:
    """Check if line is a class definition."""
    return line.startswith("class ")

def is_loop(line: str, language: str) -> bool:
    """Check if line starts a loop."""
    loop_keywords = ["for ", "while "]
    return any(line.startswith(kw) for kw in loop_keywords)

def is_conditional(line: str, language: str) -> bool:
    """Check if line is a conditional statement."""
    return line.startswith("if ") or line.startswith("elif ") or line.startswith("else:")

def is_variable_assignment(line: str, language: str) -> bool:
    """Check if line is variable assignment."""
    if language == "python":
        return "=" in line and not line.startswith(("def ", "class ", "if ", "elif ", "for ", "while "))
    return "=" in line and not any(line.startswith(kw) for kw in ["if", "for", "while", "function"])

def is_return_statement(line: str, language: str) -> bool:
    """Check if line is a return statement."""
    return line.startswith("return ")

def extract_function_name(line: str, language: str) -> str:
    """Extract function name from definition."""
    if language == "python":
        match = re.search(r'def\s+(\w+)', line)
        return match.group(1) if match else "unknown"
    elif language in ["javascript", "typescript"]:
        match = re.search(r'function\s+(\w+)', line)
        if match:
            return match.group(1)
        match = re.search(r'(\w+)\s*=\s*.*=>', line)
        return match.group(1) if match else "anonymous"
    return "unknown"

def extract_class_name(line: str) -> str:
    """Extract class name from definition."""
    match = re.search(r'class\s+(\w+)', line)
    return match.group(1) if match else "unknown"

def extract_variable_name(line: str, language: str) -> str:
    """Extract variable name from assignment."""
    if '=' in line:
        return line.split('=')[0].strip().split()[-1]
    return "unknown"

def create_teaching_template(language: str) -> str:
    """Create a teaching template for explaining code structure."""
    comment = get_comment_char(language)
    
    template = f"""{comment} ========================================
{comment} CODE EXPLANATION TEMPLATE
{comment} ========================================

{comment} 1. OVERVIEW
{comment} What does this code do? (Big picture)

{comment} 2. KEY CONCEPTS USED
{comment} - Concept 1: [Brief explanation]
{comment} - Concept 2: [Brief explanation]

{comment} 3. STEP-BY-STEP EXECUTION
{comment} [Explain how the code runs from top to bottom]

{comment} 4. IMPORTANT DETAILS
{comment} [Highlight tricky parts or common mistakes]

{comment} 5. TRY IT YOURSELF
{comment} [Suggest modifications to experiment with]

{comment} ========================================
"""
    return template

def main():
    """Main entry point for the script."""
    if len(sys.argv) < 2:
        print("Usage: python annotate_code.py <code_file> [language]")
        print("Example: python annotate_code.py script.py python")
        sys.exit(1)
    
    file_path = sys.argv[1]
    language = sys.argv[2] if len(sys.argv) > 2 else "python"
    
    try:
        with open(file_path, 'r') as f:
            code = f.read()
        
        annotated = annotate_code(code, language)
        
        # Write to new file
        output_path = file_path.replace('.', '_annotated.')
        with open(output_path, 'w') as f:
            f.write(annotated)
        
        print(f"✅ Annotated code written to: {output_path}")
        
    except FileNotFoundError:
        print(f"❌ Error: File '{file_path}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
