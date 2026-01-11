#!/usr/bin/env python3
"""
Codebase Mapping Script
Generates structural maps and dependency graphs for repository analysis.
"""

import os
import re
import ast
import json
import argparse
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Optional

# Directories to exclude from analysis
EXCLUDED_DIRS = {
    'node_modules', '__pycache__', '.git', '.venv', 'venv', 
    'dist', 'build', '.mypy_cache', '.pytest_cache', '.tox',
    'htmlcov', '.coverage', 'egg-info', '.eggs', 'site-packages'
}

# File extensions to analyze for dependencies
ANALYZABLE_EXTENSIONS = {'.py', '.ts', '.js', '.tsx', '.jsx'}


def should_exclude(path: Path) -> bool:
    """Check if a path should be excluded from analysis."""
    parts = path.parts
    for part in parts:
        if part in EXCLUDED_DIRS or part.endswith('.egg-info'):
            return True
    return False


def generate_file_tree(root: Path, max_depth: int = 10) -> Dict:
    """Generate a structured file tree."""
    tree = {
        'name': root.name,
        'type': 'directory',
        'path': str(root),
        'children': []
    }
    
    def walk_dir(current: Path, node: Dict, depth: int):
        if depth > max_depth:
            return
        
        try:
            items = sorted(current.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        except PermissionError:
            return
        
        for item in items:
            if should_exclude(item):
                continue
            if item.name.startswith('.') and item.name not in ['.env.example']:
                continue
                
            child = {
                'name': item.name,
                'type': 'directory' if item.is_dir() else 'file',
                'path': str(item.relative_to(root))
            }
            
            if item.is_dir():
                child['children'] = []
                walk_dir(item, child, depth + 1)
                # Only include non-empty directories
                if child['children']:
                    node['children'].append(child)
            else:
                if item.suffix in ANALYZABLE_EXTENSIONS or item.name in ['pyproject.toml', 'setup.py', 'package.json']:
                    node['children'].append(child)
    
    walk_dir(root, tree, 0)
    return tree


def extract_python_imports(file_path: Path) -> List[Dict]:
    """Extract imports from a Python file."""
    imports = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=str(file_path))
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        'module': alias.name,
                        'type': 'import',
                        'line': node.lineno
                    })
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                level = node.level  # Relative import level
                imports.append({
                    'module': module,
                    'names': [a.name for a in node.names],
                    'type': 'from_import',
                    'relative_level': level,
                    'line': node.lineno
                })
    except (SyntaxError, UnicodeDecodeError):
        pass
    
    return imports


def extract_js_imports(file_path: Path) -> List[Dict]:
    """Extract imports from JavaScript/TypeScript files."""
    imports = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Match ES6 imports
        es6_pattern = r"import\s+(?:(?:\{[^}]+\}|\*\s+as\s+\w+|\w+)\s+from\s+)?['\"]([^'\"]+)['\"]"
        for match in re.finditer(es6_pattern, content):
            imports.append({
                'module': match.group(1),
                'type': 'es6_import'
            })
        
        # Match require statements
        require_pattern = r"require\s*\(['\"]([^'\"]+)['\"]\)"
        for match in re.finditer(require_pattern, content):
            imports.append({
                'module': match.group(1),
                'type': 'require'
            })
    except UnicodeDecodeError:
        pass
    
    return imports


def build_dependency_graph(root: Path) -> Dict:
    """Build a dependency graph for the codebase."""
    graph = {
        'nodes': [],
        'edges': [],
        'external_deps': set(),
        'internal_deps': defaultdict(list)
    }
    
    file_to_idx = {}
    idx = 0
    
    for file_path in root.rglob('*'):
        if should_exclude(file_path) or not file_path.is_file():
            continue
        
        if file_path.suffix not in ANALYZABLE_EXTENSIONS:
            continue
        
        rel_path = str(file_path.relative_to(root))
        file_to_idx[rel_path] = idx
        graph['nodes'].append({
            'id': idx,
            'path': rel_path,
            'name': file_path.name
        })
        idx += 1
    
    # Extract dependencies
    for file_path in root.rglob('*'):
        if should_exclude(file_path) or not file_path.is_file():
            continue
        
        rel_path = str(file_path.relative_to(root))
        if rel_path not in file_to_idx:
            continue
        
        source_idx = file_to_idx[rel_path]
        
        if file_path.suffix == '.py':
            imports = extract_python_imports(file_path)
        elif file_path.suffix in {'.js', '.ts', '.jsx', '.tsx'}:
            imports = extract_js_imports(file_path)
        else:
            continue
        
        for imp in imports:
            module = imp['module']
            if module.startswith('.'):
                # Relative import - try to resolve
                graph['internal_deps'][rel_path].append(module)
            elif '/' not in module and not module.startswith('@'):
                # Likely external
                graph['external_deps'].add(module.split('.')[0])
            else:
                graph['internal_deps'][rel_path].append(module)
    
    graph['external_deps'] = sorted(graph['external_deps'])
    graph['internal_deps'] = dict(graph['internal_deps'])
    
    return graph


def identify_entry_points(root: Path) -> List[Dict]:
    """Identify likely entry points in the codebase."""
    entry_points = []
    
    # Python entry points
    for pattern, description in [
        ('setup.py', 'Python package setup'),
        ('pyproject.toml', 'Python project configuration'),
        ('main.py', 'Main module'),
        ('app.py', 'Application entry (Flask/FastAPI)'),
        ('manage.py', 'Django management'),
        ('cli.py', 'CLI entry point'),
        ('__main__.py', 'Package main module'),
    ]:
        for match in root.rglob(pattern):
            if should_exclude(match):
                continue
            entry_points.append({
                'path': str(match.relative_to(root)),
                'type': 'python',
                'description': description
            })
    
    # JavaScript/Node entry points
    package_json = root / 'package.json'
    if package_json.exists():
        try:
            with open(package_json) as f:
                pkg = json.load(f)
            if 'main' in pkg:
                entry_points.append({
                    'path': pkg['main'],
                    'type': 'node',
                    'description': 'Package main'
                })
            if 'bin' in pkg:
                for name, path in (pkg['bin'].items() if isinstance(pkg['bin'], dict) else [(pkg['name'], pkg['bin'])]):
                    entry_points.append({
                        'path': path,
                        'type': 'node',
                        'description': f'CLI binary: {name}'
                    })
        except (json.JSONDecodeError, KeyError):
            pass
    
    # Check for if __name__ == "__main__" patterns
    for py_file in root.rglob('*.py'):
        if should_exclude(py_file):
            continue
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            if 'if __name__' in content and '__main__' in content:
                entry_points.append({
                    'path': str(py_file.relative_to(root)),
                    'type': 'python',
                    'description': 'Executable module'
                })
        except UnicodeDecodeError:
            pass
    
    return entry_points


def identify_key_files(root: Path) -> Dict[str, List[str]]:
    """Identify key files for different analysis types."""
    key_files = {
        'types': [],
        'execution': [],
        'tools': [],
        'agents': [],
        'config': []
    }
    
    patterns = {
        'types': ['types.py', 'schema.py', 'models.py', 'schemas.py', 'typing.py'],
        'execution': ['executor.py', 'runner.py', 'engine.py', 'runtime.py', 'loop.py'],
        'tools': ['tool.py', 'tools.py', 'functions.py', 'base_tool.py'],
        'agents': ['agent.py', 'agents.py', 'base_agent.py', 'agent_executor.py'],
        'config': ['config.py', 'settings.py', 'constants.py', 'defaults.py']
    }
    
    for category, file_patterns in patterns.items():
        for pattern in file_patterns:
            for match in root.rglob(pattern):
                if should_exclude(match):
                    continue
                key_files[category].append(str(match.relative_to(root)))
    
    return key_files


def analyze_codebase(repo_path: str, output_path: Optional[str] = None) -> Dict:
    """Main analysis function."""
    root = Path(repo_path).resolve()
    
    if not root.exists():
        raise ValueError(f"Path does not exist: {root}")
    
    print(f"Analyzing codebase: {root}")
    
    result = {
        'repository': root.name,
        'path': str(root),
        'file_tree': generate_file_tree(root),
        'dependencies': build_dependency_graph(root),
        'entry_points': identify_entry_points(root),
        'key_files': identify_key_files(root),
        'stats': {}
    }
    
    # Calculate stats
    file_count = sum(1 for _ in root.rglob('*') if _.is_file() and not should_exclude(_))
    py_count = sum(1 for _ in root.rglob('*.py') if not should_exclude(_))
    result['stats'] = {
        'total_files': file_count,
        'python_files': py_count,
        'external_dependencies': len(result['dependencies']['external_deps'])
    }
    
    if output_path:
        output = Path(output_path)
        with open(output, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        print(f"Output written to: {output}")
    
    return result


def main():
    parser = argparse.ArgumentParser(description='Map codebase structure and dependencies')
    parser.add_argument('path', help='Path to repository')
    parser.add_argument('--output', '-o', help='Output JSON file path')
    
    args = parser.parse_args()
    
    result = analyze_codebase(args.path, args.output)
    
    if not args.output:
        print(json.dumps(result, indent=2, default=str))


if __name__ == '__main__':
    main()
