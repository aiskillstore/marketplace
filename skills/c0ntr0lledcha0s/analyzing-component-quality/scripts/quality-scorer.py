#!/usr/bin/env python3
"""
Quality Scorer for Claude Code Components

Provides automated quality scoring based on heuristics.
Analyzes description clarity, tool permissions, security, and usability.
"""

import sys
import re
import yaml
from pathlib import Path
from typing import Dict, List, Tuple

# Orchestrator agents are permitted to have the Task tool for delegation
# These agents coordinate work across other specialized agents
ORCHESTRATOR_AGENTS = ['project-coordinator', 'investigator', 'workflow-orchestrator']

def extract_frontmatter(file_path: Path) -> Dict:
    """Extract YAML frontmatter from markdown file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract frontmatter between --- markers
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match:
        return {}

    try:
        return yaml.safe_load(match.group(1))
    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}", file=sys.stderr)
        return {}

def score_description_clarity(frontmatter: Dict, content: str, component_type: str) -> Tuple[int, List[str]]:
    """Score description clarity (1-5)."""
    score = 5
    issues = []

    description = frontmatter.get('description', '')

    # Check description length
    if len(description) < 50:
        score -= 2
        issues.append("Description too short (< 50 chars)")
    elif len(description) < 100:
        score -= 1
        issues.append("Description could be more detailed (< 100 chars)")

    # Check for vague words
    vague_words = ['helps', 'manages', 'handles', 'does', 'works with']
    if any(word in description.lower() for word in vague_words):
        score -= 1
        issues.append("Description contains vague words (helps, manages, etc.)")

    # For skills, check for auto-invoke triggers
    if component_type == 'skill':
        trigger_phrases = ['auto-invokes when', 'automatically activated when', 'use when']
        if not any(phrase in description.lower() for phrase in trigger_phrases):
            score -= 1
            issues.append("Skill description missing auto-invoke trigger specification")

    # Check for specific examples or use cases
    if 'e.g.' not in description and 'example' not in description.lower():
        score -= 1
        issues.append("No examples in description")

    return max(1, score), issues

def score_tool_permissions(frontmatter: Dict, component_type: str) -> Tuple[int, List[str]]:
    """Score tool permissions (1-5)."""
    score = 5
    issues = []

    allowed_tools = frontmatter.get('allowed-tools', frontmatter.get('tools', []))

    # Convert to list if string
    if isinstance(allowed_tools, str):
        allowed_tools = [t.strip() for t in allowed_tools.split(',')]

    if not allowed_tools:
        return 5, []  # No tools specified (acceptable for some components)

    # Count dangerous tools
    dangerous_tools = ['Bash', 'Write', 'Edit']
    has_dangerous = [t for t in allowed_tools if t in dangerous_tools]

    if has_dangerous:
        score -= 1
        issues.append(f"Has elevated permissions: {', '.join(has_dangerous)} (ensure justified)")

    # Check for overly permissive (too many tools)
    if len(allowed_tools) > 6:
        score -= 1
        issues.append(f"Many tools specified ({len(allowed_tools)}), ensure all are necessary")

    # Check for Task tool in agents (circular delegation risk)
    # Orchestrator agents are exempt - they need Task tool for delegation
    if component_type == 'agent' and 'Task' in allowed_tools:
        agent_name = frontmatter.get('name', '')
        if agent_name not in ORCHESTRATOR_AGENTS:
            score -= 1
            issues.append("Agent has Task tool (potential circular delegation)")
        else:
            issues.append("✓ Orchestrator agent: Task tool permitted for delegation")

    # Check for unnecessary Write with no Edit
    if 'Write' in allowed_tools and 'Edit' not in allowed_tools:
        issues.append("Has Write but not Edit (intentional? Edit is often better)")

    return max(1, score), issues

def score_auto_invoke_triggers(frontmatter: Dict, content: str) -> Tuple[int, List[str]]:
    """Score auto-invoke trigger quality (1-5) for skills."""
    score = 5
    issues = []

    description = frontmatter.get('description', '')

    # Check if triggers are specified
    trigger_phrases = ['auto-invokes when', 'automatically activated when']
    has_triggers = any(phrase in description.lower() for phrase in trigger_phrases)

    if not has_triggers:
        score -= 2
        issues.append("No clear auto-invoke triggers specified in description")
        return max(1, score), issues

    # Check for specific quoted examples
    if '"' not in description and "'" not in description:
        score -= 1
        issues.append("No specific trigger phrases quoted (e.g., 'how does X work?')")

    # Check for vague triggers
    vague_triggers = ['when user needs help', 'when appropriate', 'when necessary']
    if any(vague in description.lower() for vague in vague_triggers):
        score -= 2
        issues.append("Triggers are too vague")

    return max(1, score), issues

def score_security(frontmatter: Dict, content: str) -> Tuple[int, List[str]]:
    """Score security considerations (1-5)."""
    score = 5
    issues = []

    allowed_tools = frontmatter.get('allowed-tools', frontmatter.get('tools', []))
    if isinstance(allowed_tools, str):
        allowed_tools = [t.strip() for t in allowed_tools.split(',')]

    # High risk: Bash with Write/Edit
    if 'Bash' in allowed_tools and ('Write' in allowed_tools or 'Edit' in allowed_tools):
        score -= 2
        issues.append("SECURITY RISK: Bash + Write/Edit combination (command injection risk)")

    # Medium risk: Bash alone
    elif 'Bash' in allowed_tools:
        score -= 1
        issues.append("Bash tool present (ensure input validation)")

    # Check for input validation mentions in content
    if 'Bash' in allowed_tools:
        if 'validate' not in content.lower() and 'sanitize' not in content.lower():
            score -= 1
            issues.append("Bash tool used but no mention of input validation")

    # Check for security best practices mention
    if 'security' in content.lower() or 'validate' in content.lower():
        issues.append("✓ Security considerations mentioned")

    return max(1, score), issues

def score_usability(frontmatter: Dict, content: str) -> Tuple[int, List[str]]:
    """Score usability and developer experience (1-5)."""
    score = 5
    issues = []

    # Check for examples in content
    if '```' not in content:
        score -= 1
        issues.append("No code examples in documentation")

    # Check for usage section
    if '## usage' not in content.lower() and '## example' not in content.lower():
        score -= 1
        issues.append("No usage or examples section")

    # Check for explanation of capabilities
    if '## capabilities' not in content.lower() and '## features' not in content.lower():
        issues.append("Consider adding capabilities/features section")

    # Check content length (documentation quality)
    lines = content.split('\n')
    doc_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]

    if len(doc_lines) < 20:
        score -= 1
        issues.append("Sparse documentation (< 20 lines of content)")

    return max(1, score), issues

def determine_component_type(file_path: Path) -> str:
    """Determine component type from file path."""
    # Normalize path separators for cross-platform compatibility
    path_str = str(file_path).replace('\\', '/')

    if '/agents/' in path_str:
        return 'agent'
    elif '/skills/' in path_str and file_path.name == 'SKILL.md':
        return 'skill'
    elif '/commands/' in path_str:
        return 'command'
    elif file_path.name == 'hooks.json':
        return 'hook'
    else:
        return 'unknown'

def analyze_component(file_path: Path) -> Dict:
    """Analyze component and return quality scores."""
    component_type = determine_component_type(file_path)

    if component_type == 'hook':
        print("Hook analysis not yet implemented", file=sys.stderr)
        return {}

    frontmatter = extract_frontmatter(file_path)

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Score each dimension
    desc_score, desc_issues = score_description_clarity(frontmatter, content, component_type)
    tool_score, tool_issues = score_tool_permissions(frontmatter, component_type)
    security_score, security_issues = score_security(frontmatter, content)
    usability_score, usability_issues = score_usability(frontmatter, content)

    # Auto-invoke only for skills
    if component_type == 'skill':
        trigger_score, trigger_issues = score_auto_invoke_triggers(frontmatter, content)
    else:
        trigger_score, trigger_issues = None, []

    # Calculate overall score
    scores = [desc_score, tool_score, security_score, usability_score]
    if trigger_score is not None:
        scores.append(trigger_score)

    overall_score = sum(scores) / len(scores)

    return {
        'component_type': component_type,
        'component_name': frontmatter.get('name', file_path.stem),
        'overall_score': overall_score,
        'scores': {
            'description_clarity': desc_score,
            'tool_permissions': tool_score,
            'auto_invoke_triggers': trigger_score,
            'security': security_score,
            'usability': usability_score
        },
        'issues': {
            'description_clarity': desc_issues,
            'tool_permissions': tool_issues,
            'auto_invoke_triggers': trigger_issues,
            'security': security_issues,
            'usability': usability_issues
        }
    }

def format_report(analysis: Dict) -> str:
    """Format analysis results as a readable report."""
    report = []
    report.append("=" * 60)
    report.append(f"Component Quality Analysis")
    report.append("=" * 60)
    report.append(f"Component: {analysis['component_name']}")
    report.append(f"Type: {analysis['component_type']}")
    report.append(f"Overall Quality: {analysis['overall_score']:.1f}/5.0")
    report.append("")

    # Determine quality level
    score = analysis['overall_score']
    if score >= 4.5:
        quality_level = "Excellent ✅"
    elif score >= 4.0:
        quality_level = "Good ✓"
    elif score >= 3.0:
        quality_level = "Adequate ⚠"
    elif score >= 2.0:
        quality_level = "Poor ⚠⚠"
    else:
        quality_level = "Critical ❌"

    report.append(f"Quality Level: {quality_level}")
    report.append("")
    report.append("-" * 60)
    report.append("Quality Scores")
    report.append("-" * 60)

    scores = analysis['scores']
    for dimension, score in scores.items():
        if score is not None:
            dimension_name = dimension.replace('_', ' ').title()
            report.append(f"{dimension_name:.<40} {score}/5")

    report.append("")
    report.append("-" * 60)
    report.append("Issues Identified")
    report.append("-" * 60)

    issues = analysis['issues']
    has_issues = False

    for dimension, issue_list in issues.items():
        if issue_list:
            has_issues = True
            dimension_name = dimension.replace('_', ' ').title()
            report.append(f"\n{dimension_name}:")
            for issue in issue_list:
                if issue.startswith('✓'):
                    report.append(f"  {issue}")
                elif issue.startswith('SECURITY'):
                    report.append(f"  🔴 {issue}")
                else:
                    report.append(f"  • {issue}")

    if not has_issues:
        report.append("\nNo issues identified! ✅")

    report.append("")
    report.append("=" * 60)

    return '\n'.join(report)

def main():
    if len(sys.argv) < 2:
        print("Usage: python quality-scorer.py <component-file>", file=sys.stderr)
        print("  component-file: Path to agent, skill, or command markdown file", file=sys.stderr)
        sys.exit(1)

    file_path = Path(sys.argv[1])

    if not file_path.exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    try:
        analysis = analyze_component(file_path)
        report = format_report(analysis)
        print(report)

        # Exit code based on quality
        if analysis['overall_score'] < 3.0:
            sys.exit(2)  # Quality too low
        elif analysis['overall_score'] < 4.0:
            sys.exit(1)  # Quality adequate but has issues
        else:
            sys.exit(0)  # Quality good

    except Exception as e:
        print(f"Error analyzing component: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(3)

if __name__ == '__main__':
    main()
