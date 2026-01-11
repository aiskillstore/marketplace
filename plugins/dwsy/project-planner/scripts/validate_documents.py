#!/usr/bin/env python3
"""
Document Validator
Validates project planning documents for completeness and consistency
"""

import re
import argparse
from typing import List, Dict, Tuple
import os

class DocumentValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        
    def validate_requirements(self, content: str) -> Tuple[List[str], List[str]]:
        """Validate requirements document structure and content"""
        errors = []
        warnings = []
        
        # Check required sections
        required_sections = [
            "## Introduction",
            "## Glossary", 
            "## Requirements"
        ]
        
        for section in required_sections:
            if section not in content:
                errors.append(f"Missing required section: {section}")
        
        # Check for user stories
        user_story_pattern = r"\*\*User Story:\*\*.*As a.*I want.*so that"
        if not re.search(user_story_pattern, content, re.DOTALL):
            warnings.append("No user stories found in requirements")
        
        # Check for acceptance criteria
        if "Acceptance Criteria" not in content:
            errors.append("No acceptance criteria found")
        
        # Check for SHALL statements
        shall_count = content.count("SHALL")
        if shall_count < 5:
            warnings.append(f"Only {shall_count} SHALL statements found (recommend at least 5)")
        
        # Check for requirement numbering
        req_pattern = r"### Requirement \d+|### REQ-\d+"
        req_matches = re.findall(req_pattern, content)
        if len(req_matches) < 3:
            warnings.append(f"Only {len(req_matches)} numbered requirements found")
        
        # Check for placeholders
        placeholder_pattern = r"\[.*?\]"
        placeholders = re.findall(placeholder_pattern, content)
        if len(placeholders) > 10:
            warnings.append(f"Found {len(placeholders)} placeholders - remember to fill them in")
        
        return errors, warnings
    
    def validate_design(self, content: str) -> Tuple[List[str], List[str]]:
        """Validate design document structure and content"""
        errors = []
        warnings = []
        
        # Check required sections
        required_sections = [
            "## Overview",
            "## System Architecture",
            "## Data Flow",
            "## Integration Points",
            "## Components",
            "## Data Models",
            "## Deployment"
        ]
        
        for section in required_sections:
            if section not in content:
                errors.append(f"Missing required section: {section}")
        
        # Check for component map
        if "Component Map" not in content and "| Component ID |" not in content:
            errors.append("Missing Component Map table")
        
        # Check for data flow specifications
        if "Data Flow" not in content:
            errors.append("Missing Data Flow specifications")
        
        # Check for integration points
        if "Integration Points" not in content:
            errors.append("Missing Integration Points section")
        
        # Check for system boundaries
        if "System Boundaries" not in content and "In Scope" not in content:
            warnings.append("Missing System Boundaries definition")
        
        # Check for architecture diagram
        if "```" not in content and "┌" not in content:
            warnings.append("No architecture diagram found")
        
        # Check for interfaces
        if "class" not in content and "interface" not in content.lower():
            warnings.append("No interface definitions found")
        
        # Check for error handling
        if "Error Handling" not in content and "error handling" not in content.lower():
            warnings.append("No error handling section found")
        
        # Check for performance targets
        if "Performance" not in content and "performance" not in content.lower():
            warnings.append("No performance targets specified")
        
        # Check for Docker configuration
        if "Docker" not in content and "docker" not in content:
            warnings.append("No Docker configuration found")
        
        return errors, warnings
    
    def validate_tasks(self, content: str) -> Tuple[List[str], List[str]]:
        """Validate implementation plan structure and content"""
        errors = []
        warnings = []
        
        # Check for project boundaries
        if "## Project Boundaries" not in content:
            errors.append("Missing Project Boundaries section")
        
        if "Must Have" not in content:
            warnings.append("Missing 'Must Have' scope definition")
        
        if "Out of Scope" not in content:
            warnings.append("Missing 'Out of Scope' definition")
        
        # Check for deliverables
        if "## Deliverables" not in content and "Deliverables by Phase" not in content:
            warnings.append("Missing Deliverables section")
        
        # Check for success criteria
        if "Success Criteria" not in content:
            warnings.append("Missing Success Criteria for deliverables")
        
        # Check for task structure
        phase_pattern = r"- \[[ x]\] \d+\."
        phases = re.findall(phase_pattern, content)
        
        if len(phases) == 0:
            errors.append("No phases found in task list")
        elif len(phases) < 3:
            warnings.append(f"Only {len(phases)} phases found (recommend at least 3)")
        
        # Check for subtasks
        task_pattern = r"  - \[[ x]\] \d+\.\d+"
        tasks = re.findall(task_pattern, content)
        
        if len(tasks) == 0:
            errors.append("No tasks found in implementation plan")
        elif len(tasks) < 10:
            warnings.append(f"Only {len(tasks)} tasks found (recommend at least 10)")
        
        # Check for requirement tracing
        req_pattern = r"_Requirements:.*REQ-\d+|_Requirements:.*\d+\.\d+"
        req_traces = re.findall(req_pattern, content)
        
        if len(req_traces) == 0:
            warnings.append("No requirement tracing found in tasks")
        elif len(req_traces) < len(tasks) / 2:
            warnings.append(f"Only {len(req_traces)} tasks have requirement tracing")
        
        # Check for component involvement
        comp_pattern = r"_Components:.*COMP-\d+"
        comp_traces = re.findall(comp_pattern, content)
        
        if len(comp_traces) == 0:
            warnings.append("No component mapping found in tasks")
        
        # Check for dependencies
        dep_pattern = r"_Dependencies:"
        dependencies = re.findall(dep_pattern, content)
        
        if len(dependencies) == 0:
            warnings.append("No task dependencies defined")
        
        # Check completion status
        completed_pattern = r"- \[x\]"
        pending_pattern = r"- \[ \]"
        
        completed = len(re.findall(completed_pattern, content))
        pending = len(re.findall(pending_pattern, content))
        
        if completed + pending > 0:
            completion_rate = (completed / (completed + pending)) * 100
            print(f"Task completion: {completed}/{completed + pending} ({completion_rate:.1f}%)")
        
        return errors, warnings
    
    def validate_consistency(self, req_content: str, design_content: str, 
                           task_content: str) -> Tuple[List[str], List[str]]:
        """Check consistency across documents"""
        errors = []
        warnings = []
        
        # Extract requirement IDs from requirements doc
        req_ids = set()
        req_pattern = r"### Requirement (\d+)|### REQ-(\d+)"
        for match in re.finditer(req_pattern, req_content):
            req_id = match.group(1) or match.group(2)
            req_ids.add(f"REQ-{req_id}")
        
        # Check if requirements are referenced in tasks
        for req_id in req_ids:
            if req_id not in task_content:
                warnings.append(f"{req_id} not referenced in any tasks")
        
        # Extract components from design
        component_pattern = r"### .*(?:Service|Component|Manager|Engine|Handler)"
        components = re.findall(component_pattern, design_content)
        
        # Check if major components have corresponding tasks
        for component in components:
            component_name = component.replace("### ", "").strip()
            if component_name.lower() not in task_content.lower():
                warnings.append(f"Component '{component_name}' not mentioned in tasks")
        
        return errors, warnings
    
    def validate_all(self, req_file: str, design_file: str, 
                     task_file: str) -> Dict[str, Tuple[List[str], List[str]]]:
        """Validate all three documents"""
        results = {}
        
        # Read files
        with open(req_file, 'r') as f:
            req_content = f.read()
        with open(design_file, 'r') as f:
            design_content = f.read()
        with open(task_file, 'r') as f:
            task_content = f.read()
        
        # Validate individual documents
        results['requirements'] = self.validate_requirements(req_content)
        results['design'] = self.validate_design(design_content)
        results['tasks'] = self.validate_tasks(task_content)
        
        # Validate consistency
        results['consistency'] = self.validate_consistency(
            req_content, design_content, task_content
        )
        
        return results

def print_validation_results(results: Dict[str, Tuple[List[str], List[str]]]):
    """Print validation results in a formatted way"""
    
    total_errors = 0
    total_warnings = 0
    
    for doc_name, (errors, warnings) in results.items():
        print(f"\n{'='*50}")
        print(f"Validation Results: {doc_name.upper()}")
        print('='*50)
        
        if errors:
            print(f"\n❌ Errors ({len(errors)}):")
            for error in errors:
                print(f"  - {error}")
            total_errors += len(errors)
        else:
            print("\n✅ No errors found")
        
        if warnings:
            print(f"\n⚠️  Warnings ({len(warnings)}):")
            for warning in warnings:
                print(f"  - {warning}")
            total_warnings += len(warnings)
        else:
            print("\n✅ No warnings found")
    
    # Summary
    print(f"\n{'='*50}")
    print("SUMMARY")
    print('='*50)
    
    if total_errors == 0 and total_warnings == 0:
        print("✅ All documents are valid and complete!")
    else:
        print(f"Total Errors: {total_errors}")
        print(f"Total Warnings: {total_warnings}")
        
        if total_errors > 0:
            print("\n⚠️  Please fix errors before using these documents")
        else:
            print("\n📝 Review warnings to improve document quality")

def main():
    parser = argparse.ArgumentParser(description="Validate project planning documents")
    parser.add_argument("--requirements", "-r", default="requirements.md",
                      help="Path to requirements document")
    parser.add_argument("--design", "-d", default="design.md",
                      help="Path to design document")
    parser.add_argument("--tasks", "-t", default="tasks.md",
                      help="Path to tasks/implementation plan")
    
    args = parser.parse_args()
    
    # Check if files exist
    for filepath, name in [(args.requirements, "Requirements"),
                          (args.design, "Design"),
                          (args.tasks, "Tasks")]:
        if not os.path.exists(filepath):
            print(f"❌ {name} file not found: {filepath}")
            return 1
    
    # Validate documents
    validator = DocumentValidator()
    results = validator.validate_all(args.requirements, args.design, args.tasks)
    
    # Print results
    print_validation_results(results)
    
    # Return exit code based on errors
    total_errors = sum(len(errors) for errors, _ in results.values())
    return 1 if total_errors > 0 else 0

if __name__ == "__main__":
    exit(main())
