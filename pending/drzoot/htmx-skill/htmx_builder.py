#!/usr/bin/env python3
"""
htmx Skill Builder

This script processes htmx documentation files:
1. Downloads markdown files from GitHub repository
2. Strips frontmatter from each file (TOML +++ or YAML ---)
3. Copies processed files to references/ folder (maintaining subfolder structure)
4. Extracts title and description from frontmatter
5. Updates SKILL.md with a comprehensive index of all pages
"""

import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
import tomllib
import yaml
import requests
from urllib.parse import urljoin

# Global configuration loaded from config.yaml
CONFIG = None


def load_config(config_path: Path) -> Dict:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Configuration dictionary
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file not found: {config_path}")
        print("Please create a config.yaml file in the same directory as builder.py")
        exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing configuration file: {e}")
        exit(1)


def clean_title(title: str) -> str:
    """
    Clean redundant parts from component titles using patterns from config.
    
    Args:
        title: The original title from frontmatter
        
    Returns:
        Cleaned title string
    """
    cleaned = title
    
    # Apply all cleanup patterns from configuration
    for cleanup_rule in CONFIG['title_cleanup']:
        pattern = cleanup_rule['pattern']
        flags_str = cleanup_rule.get('flags')
        
        # Convert flags string to re flags
        flags = 0
        if flags_str == 'IGNORECASE':
            flags = re.IGNORECASE
        
        cleaned = re.sub(pattern, '', cleaned, flags=flags)
    
    return cleaned.strip()


def extract_frontmatter(content: str) -> Tuple[Dict, str]:
    """
    Extract frontmatter and body content from markdown.

    Supports TOML frontmatter delimited by +++ and YAML frontmatter delimited by ---.
    """
    # TOML frontmatter (Hugo-style)
    toml_pattern = r'^\+\+\+\s*\r?\n(.*?)\r?\n\+\+\+\s*\r?\n(.*)$'
    match = re.match(toml_pattern, content, re.DOTALL)
    if match:
        frontmatter_str = match.group(1)
        body = match.group(2)
        try:
            frontmatter = tomllib.loads(frontmatter_str)
            return frontmatter or {}, body
        except tomllib.TOMLDecodeError as e:
            print(f"Warning: Failed to parse TOML frontmatter: {e}")
            return {}, content

    # YAML frontmatter
    yaml_pattern = r'^---\s*\r?\n(.*?)\r?\n---\s*\r?\n(.*)$'
    match = re.match(yaml_pattern, content, re.DOTALL)
    if match:
        frontmatter_str = match.group(1)
        body = match.group(2)
        try:
            frontmatter = yaml.safe_load(frontmatter_str)
            return frontmatter or {}, body
        except yaml.YAMLError as e:
            print(f"Warning: Failed to parse YAML frontmatter: {e}")
            return {}, content

    return {}, content


def normalize_whitespace(text: str) -> str:
    """Collapse whitespace for clean one-line titles/descriptions."""
    return re.sub(r'\s+', ' ', text or '').strip()


def get_github_directory_contents(path: str) -> List[Dict]:
    """
    Get directory contents from GitHub repository using API.
    
    Args:
        path: Path within the repository
        
    Returns:
        List of file/directory information dictionaries
    """
    github_config = CONFIG['github']
    api_url = f"{github_config['api_base']}/{github_config['repo']}/contents/{path}?ref={github_config['branch']}"
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching directory contents from {api_url}: {e}")
        return []


def download_markdown_file(github_path: str) -> str:
    """
    Download a markdown file from GitHub raw content.
    
    Args:
        github_path: Path to the file in the repository
        
    Returns:
        File content as string
    """
    github_config = CONFIG['github']
    raw_url = f"{github_config['raw_base']}/{github_config['repo']}/{github_config['branch']}/{github_path}"
    
    try:
        response = requests.get(raw_url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error downloading file from {raw_url}: {e}")
        return ""


def should_skip_file(filename: str) -> bool:
    """
    Check if a file should be skipped based on skip patterns in config.
    
    Args:
        filename: Name of the file to check
        
    Returns:
        True if file should be skipped, False otherwise
    """
    for skip_rule in CONFIG['skip_patterns']:
        pattern = skip_rule['pattern']
        if re.search(pattern, filename):
            return True
    return False


def discover_markdown_files(base_path: str = None) -> List[Tuple[str, str]]:
    """
    Recursively discover all markdown files in the GitHub repository.
    
    Args:
        base_path: Starting path in the repository (uses config if None)
        
    Returns:
        List of tuples (github_path, relative_path)
    """
    if base_path is None:
        base_path = CONFIG['github']['content_path']
    
    markdown_files = []
    skipped_files = []
    
    def traverse_directory(path: str, relative_base: str = ""):
        contents = get_github_directory_contents(path)
        
        for item in contents:
            item_path = item['path']
            item_name = item['name']
            item_type = item['type']
            
            # Calculate relative path from content root
            if relative_base:
                relative_path = f"{relative_base}/{item_name}"
            else:
                # Remove the content/ prefix for the first level
                relative_path = item_name if path == base_path else item_name
            
            if item_type == 'file' and item_name.endswith('.md'):
                # Check if file should be skipped
                if should_skip_file(relative_path):
                    skipped_files.append(relative_path)
                    print(f"  Skipped: {relative_path}")
                else:
                    markdown_files.append((item_path, relative_path))
                    print(f"  Found: {relative_path}")
            elif item_type == 'dir':
                # Recursively traverse subdirectories
                traverse_directory(item_path, relative_path)
    
    print("Discovering markdown files in GitHub repository...")
    traverse_directory(base_path)
    print(f"Discovered {len(markdown_files)} markdown files")
    if skipped_files:
        print(f"Skipped {len(skipped_files)} files based on skip patterns")
    print()
    
    return markdown_files


def process_markdown_content(content: str, relative_path: str, references_root: Path) -> Dict:
    """
    Process markdown content: strip frontmatter and save to references folder.
    
    Args:
        content: The markdown file content
        relative_path: Relative path for the output file
        references_root: Root path of references folder
        
    Returns:
        Dictionary with frontmatter data and relative path
    """
    # Extract frontmatter and body
    frontmatter, body = extract_frontmatter(content)
    
    # Create output path
    output_path = references_root / relative_path
    
    # Create output directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write the body content (without frontmatter) to the output file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(body)
    
    # Get and clean the title
    filename = Path(relative_path).stem
    raw_title = frontmatter.get('title', filename.replace('-', ' ').title())
    cleaned_title = normalize_whitespace(clean_title(str(raw_title)))
    
    # Determine category from path
    path_parts = Path(relative_path).parts
    category = path_parts[0] if len(path_parts) > 1 else 'General'
    
    # Return metadata for SKILL.md generation
    return {
        'title': cleaned_title,
        'description': normalize_whitespace(frontmatter.get('description', 'Documentation page')),
        'path': str(relative_path),
        'category': category
    }


def generate_skill_md(components_data: List[Dict], output_path: Path, script_dir: Path):
    """
    Generate or update SKILL.md with component index.
    
    Args:
        components_data: List of component metadata dictionaries
        output_path: Path to SKILL.md file
        script_dir: Path to the script directory (for reading _pre and _post files)
    """
    # Read the pre and post content files from config
    template_config = CONFIG['skill_templates']
    pre_path = script_dir / template_config['pre_file']
    post_path = script_dir / template_config['post_file']
    
    pre_content = ''
    post_content = ''
    
    if pre_path.exists():
        with open(pre_path, 'r', encoding='utf-8') as f:
            pre_content = f.read()
    else:
        print(f"Warning: {pre_path} not found, using empty pre-content")
    
    if post_path.exists():
        with open(post_path, 'r', encoding='utf-8') as f:
            post_content = f.read()
    else:
        print(f"Warning: {post_path} not found, using empty post-content")
    
    # Group components by category
    categories = {}
    for component in components_data:
        category = component['category']
        if category not in categories:
            categories[category] = []
        categories[category].append(component)
    
    # Sort categories and components within each category
    sorted_categories = sorted(categories.items())
    for category, components in sorted_categories:
        components.sort(key=lambda x: x['title'])
    
    # Build the component index content
    index_content = ''
    
    # Add each category section
    for category, components in sorted_categories:
        # Format category name
        category_title = category.replace('-', ' ').title()
        index_content += f"### {category_title}\n\n"
        
        for component in components:
            # Create a bullet point with description and file path
            index_content += f"- **{component['title']}**: {component['description']}\n"
            index_content += f"  - Reference: [{component['path']}](references/{component['path']})\n\n"
    
    # Combine all parts: pre + index + post
    full_content = pre_content + "\n" + index_content + "\n" + post_content
    
    # Write the SKILL.md file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_content)


def main():
    """Main function to download markdown files from GitHub and generate SKILL.md"""
    global CONFIG
    
    # Define paths
    script_dir = Path(__file__).parent
    config_path = script_dir / 'config.yaml'
    references_root = script_dir / 'references'
    skill_md_path = script_dir / 'SKILL.md'
    
    # Load configuration
    print("Loading configuration...")
    CONFIG = load_config(config_path)
    print(f"Configuration loaded from: {config_path}")
    print()
    
    # Clear and recreate references directory for clean build
    if references_root.exists():
        print(f"Clearing existing references directory: {references_root}")
        shutil.rmtree(references_root)
    
    references_root.mkdir(exist_ok=True)
    
    github_config = CONFIG['github']
    
    print("=" * 60)
    print("htmx Skill Builder")
    print("=" * 60)
    print(f"GitHub Repository: {github_config['repo']}")
    print(f"Branch: {github_config['branch']}")
    print(f"Content Path: {github_config['content_path']}")
    print(f"Output directory: {references_root}")
    print()
    
    # Discover all markdown files in the repository
    markdown_files = discover_markdown_files()
    
    if not markdown_files:
        print("Error: No markdown files found in repository")
        return 1
    
    print(f"Downloading and processing {len(markdown_files)} markdown files...")
    print()
    
    # Process each markdown file
    components_data = []
    for github_path, relative_path in sorted(markdown_files):
        print(f"Processing: {relative_path}")
        try:
            # Download the file content
            content = download_markdown_file(github_path)
            if not content:
                print(f"  Warning: Empty content, skipping")
                continue
            
            # Process and save the file
            metadata = process_markdown_content(content, relative_path, references_root)
            components_data.append(metadata)
            print(f"  ✓ Saved to references/{relative_path}")
        except Exception as e:
            print(f"  Error processing file: {e}")
    
    print()
    print(f"Successfully processed {len(components_data)} files")
    print()
    
    # Generate SKILL.md
    print("Generating SKILL.md...")
    generate_skill_md(components_data, skill_md_path, script_dir)
    print(f"SKILL.md generated at: {skill_md_path}")
    print()
    
    # Print summary by category
    categories = {}
    for component in components_data:
        category = component['category']
        categories[category] = categories.get(category, 0) + 1
    
    print("Summary by category:")
    for category, count in sorted(categories.items()):
        print(f"  {category}: {count} components")
    
    print()
    print("=" * 60)
    print("Build complete!")
    print("=" * 60)
    
    return 0


if __name__ == '__main__':
    exit(main())
