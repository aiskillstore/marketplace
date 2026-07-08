#!/usr/bin/env python3
"""
GitHub Label Operations Script
Handles label CRUD, bulk operations, presets, and analytics
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Optional

# Color constants
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color


def error(message: str) -> None:
    """Print error message and exit"""
    print(f"{RED}Error: {message}{NC}", file=sys.stderr)
    sys.exit(1)


def success(message: str) -> None:
    """Print success message"""
    print(f"{GREEN}✓ {message}{NC}")


def warn(message: str) -> None:
    """Print warning message"""
    print(f"{YELLOW}⚠ {message}{NC}")


def info(message: str) -> None:
    """Print info message"""
    print(f"{BLUE}ℹ {message}{NC}")


def run_gh_command(args: List[str]) -> Optional[str]:
    """Execute gh CLI command and return output"""
    try:
        result = subprocess.run(
            ['gh'] + args,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        error(f"gh command failed: {e.stderr}")
        return None


def get_current_labels() -> List[Dict]:
    """Get all labels from current repository"""
    output = run_gh_command(['label', 'list', '--json', 'name,description,color', '--limit', '1000'])
    if output:
        return json.loads(output)
    return []


def create_label(name: str, color: str, description: str = "", force: bool = False) -> bool:
    """Create a single label"""
    existing_labels = {label['name']: label for label in get_current_labels()}

    if name in existing_labels:
        if not force:
            warn(f"Label '{name}' already exists. Use --force to update.")
            return False
        # Update existing label
        run_gh_command(['label', 'edit', name, '--color', color, '--description', description])
        info(f"Updated label: {name}")
        return True

    # Create new label
    run_gh_command(['label', 'create', name, '--color', color, '--description', description])
    success(f"Created label: {name}")
    return True


def delete_label(name: str, confirm: bool = True) -> bool:
    """Delete a single label"""
    if confirm:
        response = input(f"Delete label '{name}'? [y/N]: ")
        if response.lower() != 'y':
            print("Cancelled")
            return False

    run_gh_command(['label', 'delete', name, '--yes'])
    success(f"Deleted label: {name}")
    return True


def load_preset(preset_name: str) -> Dict:
    """Load label preset from assets"""
    # Get script directory and navigate to assets
    script_dir = Path(__file__).parent
    assets_dir = script_dir.parent / 'assets'
    preset_file = assets_dir / 'label-presets.json'

    if not preset_file.exists():
        error(f"Preset file not found: {preset_file}")
        return {}

    with open(preset_file, 'r') as f:
        presets = json.load(f)

    if preset_name not in presets:
        error(f"Preset '{preset_name}' not found. Available: {', '.join(presets.keys())}")
        return {}

    return presets[preset_name]


def apply_preset(preset_name: str, cleanup: bool = False, dry_run: bool = False, force: bool = False) -> None:
    """Apply label preset to repository"""
    preset = load_preset(preset_name)
    if not preset:
        return

    labels_to_create = preset.get('labels', [])

    if dry_run:
        info(f"DRY RUN: Would create {len(labels_to_create)} labels")
        for label in labels_to_create:
            print(f"  - {label['name']} ({label['color']}): {label.get('description', '')}")
        return

    info(f"Applying preset '{preset_name}' ({len(labels_to_create)} labels)...")

    created = 0
    updated = 0

    for label in labels_to_create:
        if create_label(label['name'], label['color'], label.get('description', ''), force=force):
            if force:
                updated += 1
            else:
                created += 1

    success(f"Preset applied: {created} created, {updated} updated")

    if cleanup:
        existing_labels = get_current_labels()
        preset_names = {label['name'] for label in labels_to_create}
        to_delete = [label for label in existing_labels if label['name'] not in preset_names]

        if to_delete:
            warn(f"Cleanup: {len(to_delete)} labels not in preset")
            for label in to_delete:
                print(f"  - {label['name']}")

            if input("Delete these labels? [y/N]: ").lower() == 'y':
                for label in to_delete:
                    delete_label(label['name'], confirm=False)


def bulk_create(file_path: str, force: bool = False) -> None:
    """Bulk create labels from JSON file"""
    path = Path(file_path)
    if not path.exists():
        error(f"File not found: {file_path}")
        return

    with open(path, 'r') as f:
        labels = json.load(f)

    if not isinstance(labels, list):
        error("JSON file must contain an array of label objects")
        return

    info(f"Creating {len(labels)} labels...")

    created = 0
    for label in labels:
        if 'name' not in label or 'color' not in label:
            warn(f"Skipping invalid label: {label}")
            continue

        if create_label(label['name'], label['color'], label.get('description', ''), force=force):
            created += 1

    success(f"Created {created}/{len(labels)} labels")


def bulk_apply(filter_query: str, label_name: str, dry_run: bool = False) -> None:
    """Bulk apply label to issues matching filter"""
    # Search for issues
    output = run_gh_command(['issue', 'list', '--search', filter_query, '--json', 'number,title', '--limit', '1000'])
    if not output:
        warn("No issues found matching filter")
        return

    issues = json.loads(output)

    if dry_run:
        info(f"DRY RUN: Would apply '{label_name}' to {len(issues)} issues")
        for issue in issues[:10]:  # Show first 10
            print(f"  - #{issue['number']}: {issue['title']}")
        if len(issues) > 10:
            print(f"  ... and {len(issues) - 10} more")
        return

    info(f"Applying '{label_name}' to {len(issues)} issues...")

    for i, issue in enumerate(issues, 1):
        run_gh_command(['issue', 'edit', str(issue['number']), '--add-label', label_name])
        print(f"\r{i}/{len(issues)}", end='', flush=True)

    print()  # New line after progress
    success(f"Applied label to {len(issues)} issues")


def infer_labels(issue_number: int) -> None:
    """Infer labels from issue content"""
    # Get issue details
    output = run_gh_command(['issue', 'view', str(issue_number), '--json', 'title,body,labels'])
    if not output:
        error(f"Issue #{issue_number} not found")
        return

    issue = json.loads(output)
    title = issue['title'].lower()
    body = (issue.get('body') or '').lower()
    current_labels = {label['name'] for label in issue.get('labels', [])}

    content = f"{title} {body}"

    # Simple keyword-based inference
    suggestions = []

    # Type inference
    if any(word in content for word in ['bug', 'error', 'crash', 'broken', 'fail']):
        suggestions.append(('bug', 'Issue describes a bug'))
    if any(word in content for word in ['feature', 'add', 'new', 'implement']):
        suggestions.append(('feature', 'Issue requests a feature'))
    if any(word in content for word in ['document', 'docs', 'readme', 'guide']):
        suggestions.append(('documentation', 'Issue mentions documentation'))

    # Priority inference
    if any(word in content for word in ['urgent', 'critical', 'asap', 'immediately', 'blocking']):
        suggestions.append(('priority:high', 'Urgent keywords detected'))
    elif any(word in content for word in ['minor', 'low priority', 'nice to have', 'eventually']):
        suggestions.append(('priority:low', 'Low priority keywords detected'))

    # Scope inference
    if any(word in content for word in ['ui', 'ux', 'frontend', 'interface', 'design', 'css']):
        suggestions.append(('scope:frontend', 'Frontend keywords detected'))
    if any(word in content for word in ['api', 'backend', 'server', 'database', 'endpoint']):
        suggestions.append(('scope:backend', 'Backend keywords detected'))
    if any(word in content for word in ['security', 'vulnerability', 'auth', 'permission']):
        suggestions.append(('security', 'Security keywords detected'))

    # Filter out labels already applied
    suggestions = [(label, reason) for label, reason in suggestions if label not in current_labels]

    if not suggestions:
        info(f"Issue #{issue_number}: No new labels to suggest")
        return

    print(f"\nIssue #{issue_number}: {issue['title']}")
    print(f"\nSuggested labels:")
    for label, reason in suggestions:
        print(f"  ✓ {label} - {reason}")

    if input("\nApply these labels? [y/N]: ").lower() == 'y':
        labels_to_add = ','.join([label for label, _ in suggestions])
        run_gh_command(['issue', 'edit', str(issue_number), '--add-label', labels_to_add])
        success(f"Applied {len(suggestions)} labels to issue #{issue_number}")


def generate_report() -> None:
    """Generate label usage report"""
    labels = get_current_labels()

    # Get issue counts for each label
    label_counts = {}
    for label in labels:
        output = run_gh_command(['issue', 'list', '--label', label['name'], '--json', 'number', '--limit', '1000'])
        if output:
            issues = json.loads(output)
            label_counts[label['name']] = len(issues)
        else:
            label_counts[label['name']] = 0

    # Sort by usage
    sorted_labels = sorted(label_counts.items(), key=lambda x: x[1], reverse=True)

    print("\n=== Label Usage Report ===\n")

    print("Most Used Labels:")
    for label, count in sorted_labels[:10]:
        print(f"  {count:3d} issues: {label}")

    print("\nLeast Used Labels:")
    for label, count in sorted_labels[-5:]:
        print(f"  {count:3d} issues: {label}")

    # Unused labels
    unused = [label for label, count in sorted_labels if count == 0]
    if unused:
        print(f"\nUnused Labels ({len(unused)}):")
        for label in unused:
            print(f"  - {label}")

    print(f"\nTotal: {len(labels)} labels")


def fix_consistency() -> None:
    """Fix label consistency issues"""
    labels = get_current_labels()

    issues = []

    # Check naming conventions
    for label in labels:
        name = label['name']

        # Check for uppercase
        if name != name.lower():
            issues.append(('case', name, name.lower(), 'Should be lowercase'))

        # Check for spaces (should be hyphens)
        if ' ' in name and ':' not in name:  # Allow spaces after colon for readability
            suggested = name.replace(' ', '-').lower()
            issues.append(('spacing', name, suggested, 'Use hyphens instead of spaces'))

        # Check prefix consistency for priority/scope/status
        if name.startswith(('high', 'medium', 'low')) and not name.startswith('priority:'):
            suggested = f"priority:{name}"
            issues.append(('prefix', name, suggested, 'Use priority: prefix'))

        if name.startswith(('frontend', 'backend')) and not name.startswith('scope:'):
            suggested = f"scope:{name}"
            issues.append(('prefix', name, suggested, 'Use scope: prefix'))

    if not issues:
        success("No consistency issues found!")
        return

    print(f"\nFound {len(issues)} consistency issues:\n")
    for issue_type, old_name, new_name, reason in issues:
        print(f"  {old_name} → {new_name}")
        print(f"    Reason: {reason}\n")

    if input("Fix these issues? [y/N]: ").lower() == 'y':
        for issue_type, old_name, new_name, reason in issues:
            # Get label details
            old_label = next((l for l in labels if l['name'] == old_name), None)
            if old_label:
                # Create new label
                create_label(new_name, old_label['color'], old_label.get('description', ''), force=True)

                # Move all issues to new label
                output = run_gh_command(['issue', 'list', '--label', old_name, '--json', 'number', '--limit', '1000'])
                if output:
                    issues_to_move = json.loads(output)
                    for issue in issues_to_move:
                        run_gh_command(['issue', 'edit', str(issue['number']), '--add-label', new_name, '--remove-label', old_name])

                # Delete old label
                delete_label(old_name, confirm=False)

        success(f"Fixed {len(issues)} consistency issues")


def main():
    parser = argparse.ArgumentParser(description='GitHub Label Operations')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # apply-preset
    preset_parser = subparsers.add_parser('apply-preset', help='Apply label preset')
    preset_parser.add_argument('--name', required=True, choices=['standard', 'comprehensive', 'minimal'], help='Preset name')
    preset_parser.add_argument('--cleanup', action='store_true', help='Remove labels not in preset')
    preset_parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
    preset_parser.add_argument('--force', action='store_true', help='Update existing labels')

    # bulk-create
    create_parser = subparsers.add_parser('bulk-create', help='Bulk create labels from JSON')
    create_parser.add_argument('--file', required=True, help='JSON file with labels')
    create_parser.add_argument('--force', action='store_true', help='Update existing labels')

    # bulk-apply
    apply_parser = subparsers.add_parser('bulk-apply', help='Bulk apply label to issues')
    apply_parser.add_argument('--filter', required=True, help='Issue search filter')
    apply_parser.add_argument('--label', required=True, help='Label to apply')
    apply_parser.add_argument('--dry-run', action='store_true', help='Show what would be done')

    # infer-labels
    infer_parser = subparsers.add_parser('infer-labels', help='Infer labels from issue content')
    infer_parser.add_argument('--issue', type=int, required=True, help='Issue number')

    # report
    subparsers.add_parser('report', help='Generate label usage report')

    # fix-consistency
    subparsers.add_parser('fix-consistency', help='Fix label consistency issues')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Execute command
    if args.command == 'apply-preset':
        apply_preset(args.name, args.cleanup, args.dry_run, args.force)
    elif args.command == 'bulk-create':
        bulk_create(args.file, args.force)
    elif args.command == 'bulk-apply':
        bulk_apply(args.filter, args.label, args.dry_run)
    elif args.command == 'infer-labels':
        infer_labels(args.issue)
    elif args.command == 'report':
        generate_report()
    elif args.command == 'fix-consistency':
        fix_consistency()


if __name__ == '__main__':
    main()
