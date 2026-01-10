#!/usr/bin/env python3
"""
Code Readability Analyzer

What: Checks if code is accessible to non-developers
Why: Ensures code can be understood by everyone on the team, not just developers
How: Analyzes naming, comments, jargon, and documentation to score readability

This tool helps teams write code that managers, stakeholders, and new team members
can understand without needing deep programming knowledge.
"""

# Import required libraries
import argparse  # For command-line argument parsing
import os        # For file system operations
import re        # For pattern matching in code
import json      # For JSON output format
from pathlib import Path        # For file path handling
from typing import Dict, List, Tuple  # For type hints

# What: Common technical jargon that needs explanation
# Why: Non-developers won't understand these terms
# How: We flag these in comments unless they're followed by an explanation
TECHNICAL_JARGON = [
    'API', 'REST', 'CRUD', 'DTO', 'JSON', 'XML', 'HTTP', 'SQL',
    'OAuth', 'JWT', 'PKCE', 'async', 'await', 'promise', 'callback',
    'middleware', 'endpoint', 'payload', 'schema', 'ORM', 'migration',
    'refactor', 'deprecated', 'polymorphism', 'inheritance', 'instantiate',
    'serialize', 'deserialize', 'hydrate', 'repository', 'factory',
    'singleton', 'dependency injection', 'IoC', 'webhook', 'CORS'
]

# What: Cryptic abbreviations commonly used in variable names
# Why: These are truly unclear to non-developers and should be spelled out
# How: We check variable names against this list (only the most cryptic ones)
CRYPTIC_ABBREVIATIONS = [
    # User-related abbreviations that should be spelled out
    r'\b(usr)(_|[A-Z])',  # usr - should be "user"

    # Authentication and configuration abbreviations
    r'\b(tkn|tok)(_|[A-Z])',  # tkn, tok - should be "token"
    r'\b(cfg|conf)(_|[A-Z])',  # cfg, conf - should be "config"
    r'\b(ctx)(_|[A-Z])',  # ctx - should be "context"

    # Generic placeholder abbreviations that need better names
    r'\b(tmp|temp)(_|[A-Z])',  # tmp, temp - should be descriptive

    # Counter and iteration abbreviations
    r'\b(idx)(_|[A-Z])',  # idx - should be "index"
    r'\b(cnt)(_|[A-Z])',  # cnt - should be "count"

    # Action and calculation abbreviations
    r'\b(proc)(_|[A-Z])',  # proc - should be "process"
    r'\b(calc)(_|[A-Z])',  # calc - should be "calculate"
]

# Note: Removed common abbreviations that are widely understood:
# - num, str, len (standard and clear in context)
# - msg, req, res, resp (common in web/API contexts, API = Application Programming Interface, how programs talk to each other)
# - arr, obj, val (commonly understood programming terms)

# What: Supported file extensions and their languages
# Why: We need to know which language we're analyzing
# How: Map file extension to language name
SUPPORTED_EXTENSIONS = {
    # Python ecosystem
    '.py': 'python',      # Python files

    # JavaScript ecosystem (includes TypeScript and React)
    '.js': 'javascript',  # JavaScript files
    '.ts': 'typescript',  # TypeScript files
    '.jsx': 'javascript', # React JavaScript files
    '.tsx': 'typescript', # React TypeScript files

    # Other popular languages
    '.java': 'java',      # Java files
    '.go': 'go',          # Go files
    '.rb': 'ruby',        # Ruby files
    '.php': 'php',        # PHP files
}

# ============================================================================
# Core Data Structures
# ============================================================================
# The following classes define how we represent and store readability issues

class ReadabilityIssue:
    """
    What: Represents a single readability issue found in code
    Why: We need to track and report each issue with context
    How: Stores line number, type of issue, and suggested fix
    """

    # Constructor method - initializes a new readability issue object
    def __init__(self, line_num: int, issue_type: str, description: str,
                 code_snippet: str = "", suggestion: str = ""):
        """
        What: Initialize a new readability issue
        Why: Set up all the details about what's wrong
        How: Store the line number, issue type, description, and suggestion
        """
        # Store location information - where in the file the issue was found
        self.line_num = line_num

        # Store what kind of issue this is (cryptic_naming, missing_comments, etc.)
        self.issue_type = issue_type

        # Store human-readable description of the problem
        self.description = description

        # Store the code snippet that has the issue (helps user locate it)
        self.code_snippet = code_snippet

        # Store suggested fix to help user resolve the issue
        self.suggestion = suggestion

    def to_dict(self):
        """
        What: Convert issue to dictionary format
        Why: Makes it easy to output as JSON or display in reports
        How: Create dict with all issue details
        """
        # Build a dictionary with all issue information
        # This format is used for JSON output and reporting
        return {
            'line': self.line_num,        # Line number where issue was found
            'type': self.issue_type,       # Type of issue (e.g., "cryptic_naming")
            'description': self.description,  # Human-readable problem description
            'code': self.code_snippet,     # Snippet of code with the issue
            'suggestion': self.suggestion  # Suggested fix for the issue
        }

# ============================================================================
# Main Analyzer Class
# ============================================================================
# This class performs all the readability checks on code files

class CodeReadabilityAnalyzer:
    """
    What: Main analyzer that checks code readability
    Why: Ensures code is accessible to non-developers
    How: Runs multiple checks on code files and generates a report
    """

    # Constructor - sets up a new analyzer with specified strictness level
    def __init__(self, strictness: str = 'standard'):
        # Store strictness setting (lenient, standard, or strict)
        self.strictness = strictness
        # Initialize empty list to store found issues
        self.issues: List[ReadabilityIssue] = []

    # Helper method to clean code lines for analysis
    def _strip_strings_and_comments(self, line: str) -> str:
        """
        What: Remove string literals and comments from a line
        Why: We only want to check actual code, not examples in strings/comments
        How: Use regex to strip quoted strings and comment markers
        """
        # Remove string literals (both single and double quotes)
        # This handles most common cases but not all edge cases
        line_cleaned = re.sub(r'"[^"]*"', '""', line)  # Remove double-quoted strings
        line_cleaned = re.sub(r"'[^']*'", "''", line_cleaned)  # Remove single-quoted strings

        # Remove comments (anything after # or //)
        line_cleaned = re.sub(r'#.*$', '', line_cleaned)
        line_cleaned = re.sub(r'//.*$', '', line_cleaned)

        return line_cleaned

    # Main analysis method - checks a file for readability issues
    def analyze_file(self, file_path: str) -> Dict:
        """
        What: Analyze a single file for readability issues
        Why: Check if non-developers can understand this code
        How: Run all readability checks and collect issues
        """
        # First, verify the file actually exists on disk
        if not os.path.exists(file_path):
            return {'error': f'File not found: {file_path}'}

        # Check if this is a file type we know how to analyze
        # Extract the file extension (e.g., ".py" from "script.py")
        ext = Path(file_path).suffix
        if ext not in SUPPORTED_EXTENSIONS:
            return {'error': f'Unsupported file type: {ext}'}

        # Try to read the entire file into memory
        # We need all lines to perform our analysis
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            return {'error': f'Could not read file: {str(e)}'}

        # Clear any issues from previous file analysis
        # Each file starts with a fresh issue list
        self.issues = []

        # Run all our readability checks on the file
        # Each check adds issues to self.issues if problems are found
        self._check_cryptic_names(lines)
        self._check_comments(lines)
        self._check_jargon_in_comments(lines)
        self._check_section_documentation(lines)

        # Calculate overall readability score based on issues found
        # Score ranges from 0-100, higher is better
        score = self._calculate_readability_score(len(lines))

        # Return comprehensive analysis results
        return {
            'file': file_path,
            'language': SUPPORTED_EXTENSIONS[ext],
            'total_lines': len(lines),
            'issues_found': len(self.issues),
            'readability_score': score,
            'issues': [issue.to_dict() for issue in self.issues],
            'summary': self._generate_summary(score)
        }

    # Check for unclear variable and function names
    def _check_cryptic_names(self, lines: List[str]):
        """
        What: Check for cryptic variable and function names
        Why: Non-developers can't understand abbreviations
        How: Use regex patterns to detect common abbreviations in actual code only
        """
        # State variables to track if we're inside a docstring block
        # Docstrings are multi-line documentation comments in Python
        in_docstring = False
        docstring_marker = None

        # Loop through each line in the file to check for cryptic names
        # enumerate gives us both line number and content
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()

            # Detect docstring boundaries (""" or ''')
            # We skip checking inside docstrings because they often contain
            # code examples that intentionally use abbreviations for teaching
            if '"""' in line or "'''" in line:
                if not in_docstring:
                    # We're entering a docstring block
                    in_docstring = True
                    docstring_marker = '"""' if '"""' in line else "'''"

                    # Handle single-line docstrings (start and end on same line)
                    # If the marker appears twice, it's both opening and closing
                    if line.count(docstring_marker) >= 2:
                        in_docstring = False
                else:
                    # We're exiting a docstring block
                    in_docstring = False
                continue

            # Skip if inside docstring (don't check documentation text)
            if in_docstring:
                continue

            # Skip comment-only lines (already just documentation)
            if stripped.startswith('#') or stripped.startswith('//'):
                continue

            # Clean the line - remove strings and comments before checking
            # This prevents flagging examples like "usr_tkn" in comments
            line_cleaned = self._strip_strings_and_comments(line)

            # Skip if nothing left after cleaning (line was all comments/strings)
            if not line_cleaned.strip():
                continue

            # Check for cryptic abbreviations in the cleaned line
            # These patterns match things like usr_, tkn_, cfg_, etc.
            for pattern in CRYPTIC_ABBREVIATIONS:
                matches = re.finditer(pattern, line_cleaned)
                for match in matches:
                    # Extract the variable name context from the cleaned line
                    start = max(0, match.start() - 10)
                    end = min(len(line_cleaned), match.end() + 20)
                    snippet = line_cleaned[start:end].strip()

                    self.issues.append(ReadabilityIssue(
                        line_num=line_num,
                        issue_type='cryptic_naming',
                        description='Variable name uses unclear abbreviation',
                        code_snippet=snippet,
                        suggestion='Use full, descriptive names like "userToken" instead of "usr_tkn"'
                    ))

            # Check for single-letter variables (except in loops) in cleaned line
            # Single-letter names like "x = 5" are unclear (what does x represent?)
            if not re.search(r'\b(for|while)\b', line_cleaned):
                # Find all single-letter variable assignments (pattern: "a = value")
                single_letters = re.finditer(r'\b([a-z])\s*=', line_cleaned)

                # Loop through each single-letter variable found
                for match in single_letters:
                    # Allow common loop counters i, j, k (universally understood convention)
                    if match.group(1) not in ['i', 'j', 'k']:
                        # Flag this as a readability issue
                        self.issues.append(ReadabilityIssue(
                            line_num=line_num,
                            issue_type='cryptic_naming',
                            description=f'Single-letter variable "{match.group(1)}" is not descriptive',
                            code_snippet=line.strip(),
                            suggestion='Use descriptive names that explain what the variable holds'
                        ))

    # Check if code has adequate explanatory comments
    def _check_comments(self, lines: List[str]):
        """
        What: Check if code has adequate comments
        Why: Comments help non-developers understand what's happening
        How: Count code lines vs comment lines, flag uncommented sections
        """
        # Set up counters to track how many comments we have
        # We'll use these to calculate the comment ratio
        code_line_count = 0
        comment_line_count = 0
        uncommented_code_lines = 0  # Tracks consecutive code lines without comments

        # Process each line of the file to count comments vs code
        # enumerate gives us (line_number, line_content) pairs starting from 1
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()

            # Ignore blank lines - they don't count as code or comments
            if not stripped:
                continue

            # Identify if this line is a comment by checking common markers
            # Different languages use different comment syntax:
            # Python uses #, JavaScript uses //, C uses /* and */
            is_comment = (stripped.startswith('#') or
                         stripped.startswith('//') or
                         stripped.startswith('/*') or
                         stripped.startswith('*'))

            if is_comment:
                # Found a comment line - increment comment counter
                comment_line_count += 1
                # Reset the consecutive uncommented lines counter
                uncommented_code_lines = 0
            elif stripped:
                # Found a code line (not empty, not a comment)
                code_line_count += 1
                uncommented_code_lines += 1

                # Check if we've gone too long without a comment
                # Research shows 10+ lines without explanation is hard to follow
                if uncommented_code_lines > 10 and self.strictness in ['standard', 'strict']:
                    self.issues.append(ReadabilityIssue(
                        line_num=line_num,
                        issue_type='missing_comments',
                        description='Large section of code (10+ lines) without explanatory comments',
                        code_snippet=f'Lines {line_num - 9} to {line_num}',
                        suggestion='Add comments explaining what this section does and why'
                    ))
                    # Reset counter after flagging to avoid duplicate reports
                    uncommented_code_lines = 0

        # Overall comment ratio check
        # We want at least 20% of lines to be comments
        if code_line_count > 0:
            comment_ratio = comment_line_count / code_line_count
            if comment_ratio < 0.2:  # Less than 20% comments
                self.issues.append(ReadabilityIssue(
                    line_num=0,
                    issue_type='insufficient_comments',
                    description=f'Low comment ratio: {comment_ratio:.1%} (aim for at least 20%)',
                    suggestion='Add more comments explaining what the code does, why it exists, and how it works'
                ))

    # Check for unexplained technical terms in comments
    def _check_jargon_in_comments(self, lines: List[str]):
        """
        What: Check if comments contain unexplained technical jargon
        Why: Non-developers won't understand technical terms
        How: Look for jargon words in comments without explanations
        """
        # Scan through all lines to find technical terms in comments
        # We only check comments because code naturally contains technical terms
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()

            # Filter to only comment lines (skip regular code)
            # Comments start with # (Python) or // (JavaScript/C++)
            if not (stripped.startswith('#') or stripped.startswith('//')):
                continue

            # Extract just the comment text, removing the # or // prefix
            # For example: "# API call" becomes "API call"
            comment_text = re.sub(r'^[#/]+\s*', '', stripped)

            # Check each technical term in our jargon list
            # TECHNICAL_JARGON contains terms like API = Application Programming Interface,
            # REST = web service style, JSON = data format, etc.
            for jargon in TECHNICAL_JARGON:
                # Build a regex pattern to match the jargon as a whole word
                # \b = word boundary, ensures we don't match "format" when looking for
                # "ORM = Object-Relational Mapping" (database tool)
                pattern = r'\b' + re.escape(jargon.lower()) + r'\b'

                # Search for the jargon term in the comment (case-insensitive)
                if re.search(pattern, comment_text.lower()):
                    # Look for explanation patterns in the comment
                    # Good: "API = Application Programming Interface"
                    # Good: "API is how programs talk"
                    # Bad: "Call the API" (no explanation)
                    has_explanation = any(marker in comment_text for marker in ['=', ' is ', ' means ', ':'])

                    # If jargon found but no explanation, report it as an issue
                    if not has_explanation:
                        self.issues.append(ReadabilityIssue(
                            line_num=line_num,
                            issue_type='unexplained_jargon',
                            description=f'Technical term "{jargon}" used without explanation',
                            code_snippet=comment_text,
                            suggestion=f'Add explanation like: "{jargon} = [plain English explanation]"'
                        ))

    # Check for What/Why/How documentation in functions and classes
    def _check_section_documentation(self, lines: List[str]):
        """
        What: Check if code sections have What/Why/How documentation
        Why: This format helps non-developers understand purpose and context
        How: Look for function/class definitions and check for proper docs
        """
        # Define regex patterns to identify function and class definitions
        # We support multiple programming languages with different syntax
        definition_patterns = [
            r'^\s*def\s+\w+',  # Python function (e.g., "def my_function()")
            r'^\s*class\s+\w+',  # Python/Java/C++ class (e.g., "class MyClass:")
            r'^\s*function\s+\w+',  # JavaScript function (e.g., "function myFunc()")
            r'^\s*const\s+\w+\s*=\s*\(.*\)\s*=>',  # Modern JavaScript arrow function
        ]

        # Track whether we've found a function definition
        in_function = False
        function_line = 0

        # Scan through all lines looking for function/class definitions
        for line_num, line in enumerate(lines, 1):
            # Try each pattern to see if this line defines a function or class
            for pattern in definition_patterns:
                if re.search(pattern, line):
                    # Found a function/class definition
                    in_function = True
                    function_line = line_num

                    # Initialize flags for What/Why/How documentation
                    # We'll check if the function has proper documentation
                    has_what = False
                    has_why = False
                    has_how = False

                    # Look ahead up to 10 lines for documentation
                    # Docstrings typically appear right after the function definition
                    end = min(len(lines), line_num + 10)
                    for check_line in lines[line_num:end]:
                        # Search for What/Why/How keywords (case-insensitive)
                        if 'what:' in check_line.lower():
                            has_what = True
                        if 'why:' in check_line.lower():
                            has_why = True
                        if 'how:' in check_line.lower():
                            has_how = True

                    # Only flag if missing all three (lenient) or any (strict)
                    # In strict mode, we require all three parts: What, Why, How
                    if self.strictness == 'strict':
                        # Check if "What" documentation is missing
                        # What = describes what the function does
                        if not has_what:
                            # Flag missing "What" as an issue
                            self.issues.append(ReadabilityIssue(
                                line_num=function_line,
                                issue_type='missing_documentation',
                                description='Function/class missing "What" documentation',
                                code_snippet=line.strip(),
                                suggestion='Add comment: "What: [describe what this does]"'
                            ))
                        # Check if "Why" documentation is missing
                        # Why = explains the business reason or purpose
                        if not has_why:
                            # Flag missing "Why" as an issue
                            self.issues.append(ReadabilityIssue(
                                line_num=function_line,
                                issue_type='missing_documentation',
                                description='Function/class missing "Why" documentation',
                                code_snippet=line.strip(),
                                suggestion='Add comment: "Why: [explain the business reason]"'
                            ))
                        # Check if "How" documentation is missing
                        # How = explains how it fits into the larger system
                        if not has_how:
                            # Flag missing "How" as an issue
                            self.issues.append(ReadabilityIssue(
                                line_num=function_line,
                                issue_type='missing_documentation',
                                description='Function/class missing "How" documentation',
                                code_snippet=line.strip(),
                                suggestion='Add comment: "How: [explain how it connects to the system]"'
                            ))
                    elif not (has_what or has_why or has_how):
                        self.issues.append(ReadabilityIssue(
                            line_num=function_line,
                            issue_type='missing_documentation',
                            description='Function/class lacks What/Why/How documentation',
                            code_snippet=line.strip(),
                            suggestion='Add comments explaining: What it does, Why it exists, How it fits in'
                        ))

    # Calculate overall readability score from 0-100
    def _calculate_readability_score(self, total_lines: int) -> int:
        """
        What: Calculate a readability score from 0-100
        Why: Give users a quick sense of how readable their code is
        How: Start at 100, deduct points for each issue type
        """
        # Begin with a perfect score of 100
        # We'll subtract points for each readability issue found
        score = 100

        # Special case: empty files get a score of 0
        # Can't be readable if there's no code
        if total_lines == 0:
            return 0

        # Calculate how many issues per line
        # High density (many issues per line) suggests poor readability
        issue_density = len(self.issues) / total_lines

        # Define penalty weights for each type of issue
        # More serious issues get higher penalties (more points deducted)
        issue_weights = {
            'cryptic_naming': 3,           # Unclear variable names (moderate impact)
            'missing_comments': 5,          # Large uncommented sections (serious impact)
            'insufficient_comments': 10,    # Overall low comment ratio (very serious)
            'unexplained_jargon': 4,        # Technical terms without explanation
            'missing_documentation': 5,     # Missing What/Why/How docs (serious)
        }

        # Subtract points for each issue based on its weight
        # Loop through all issues found in the file
        for issue in self.issues:
            # Get the penalty weight for this issue type (default to 2 if unknown)
            weight = issue_weights.get(issue.issue_type, 2)
            score -= weight

        # Ensure score doesn't go below 0
        # max() returns the larger of score and 0
        return max(0, score)

    # Generate human-readable summary from score
    def _generate_summary(self, score: int) -> str:
        """
        What: Generate a human-readable summary
        Why: Help users understand what the score means
        How: Return plain English assessment based on score
        """
        if score >= 90:
            return "Excellent! This code is very accessible to non-developers."
        elif score >= 75:
            return "Good readability. Minor improvements would help non-developers."
        elif score >= 60:
            return "Moderate readability. Several areas need clearer explanations."
        elif score >= 40:
            return "Below average. Non-developers will struggle with this code."
        else:
            return "Poor readability. Major improvements needed for accessibility."

# ============================================================================
# Command-Line Interface
# ============================================================================
# Main entry point when script is run from command line

def main():
    """
    What: Command-line entry point for the analyzer
    Why: Allow the skill to execute this script from bash
    How: Parse arguments and run the analysis
    """
    # Create the command-line argument parser
    # This tool (argparse) handles --flag arguments from the command line
    parser = argparse.ArgumentParser(
        description='Analyze code readability for non-developers'
    )

    # Configure all available command-line options
    # Each add_argument() defines a flag users can pass

    # Required argument: which file to analyze
    parser.add_argument('--path', required=True, help='Path to file or directory to analyze')

    # Optional: focus on specific aspect (naming, comments, etc.)
    parser.add_argument('--focus', default='all',
                       choices=['naming', 'comments', 'jargon', 'documentation', 'all'],
                       help='Focus area for analysis')

    # Optional: who is the target audience for readability
    parser.add_argument('--audience', default='non-dev',
                       choices=['non-dev', 'new-team-member', 'stakeholder', 'everyone'],
                       help='Target audience for readability')

    # Optional: how strict should the analysis be
    parser.add_argument('--strictness', default='standard',
                       choices=['lenient', 'standard', 'strict'],
                       help='How strict the analysis should be')

    # Optional: output format (human-friendly or machine-readable)
    parser.add_argument('--format', default='human',
                       choices=['human', 'json'],
                       help='Output format')

    # Parse the command-line arguments the user provided
    # This reads sys.argv and converts it to an args object
    args = parser.parse_args()

    # Create an analyzer instance with the requested strictness setting
    # This controls how many issues get flagged
    analyzer = CodeReadabilityAnalyzer(strictness=args.strictness)

    # Run the analysis on the specified file
    # Returns a dictionary with score, issues, and other details
    result = analyzer.analyze_file(args.path)

    # Display results in the format the user requested
    # Can output as JSON = data format for computers, or text for humans
    if args.format == 'json':
        # Machine-readable output format
        # JSON = JavaScript Object Notation, a data format computers can easily read
        # Useful when other tools or scripts need to process the results
        print(json.dumps(result, indent=2))
    else:
        # Human-readable text format with nice formatting
        # This is the default output format that's easy for people to read

        # Print a header section with overall file statistics
        print(f"\n{'='*60}")
        print(f"Code Readability Analysis")
        print(f"{'='*60}\n")

        # Display basic file information
        print(f"File: {result.get('file', 'N/A')}")
        print(f"Language: {result.get('language', 'N/A')}")
        print(f"Total Lines: {result.get('total_lines', 0)}")

        # Show how many issues were found
        print(f"Issues Found: {result.get('issues_found', 0)}")

        # Display the overall readability score (0-100)
        print(f"Readability Score: {result.get('readability_score', 0)}/100")

        # Show plain English summary of what the score means
        print(f"\nSummary: {result.get('summary', 'N/A')}\n")

        # If issues were found, print detailed information about each one
        if result.get('issues'):
            print(f"{'='*60}")
            print("Issues Found:")
            print(f"{'='*60}\n")

            # Display each issue with its details
            for issue in result['issues']:
                # Show which line the issue is on and what the problem is
                print(f"Line {issue['line']}: {issue['description']}")

                # Show the code snippet if available
                if issue.get('code'):
                    print(f"  Code: {issue['code']}")

                # Show the suggestion for fixing the issue
                if issue.get('suggestion'):
                    print(f"  💡 Suggestion: {issue['suggestion']}")

                # Add blank line between issues for readability
                print()


if __name__ == '__main__':
    main()
