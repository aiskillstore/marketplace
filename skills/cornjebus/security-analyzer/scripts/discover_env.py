#!/usr/bin/env python3
"""
Discover environment assets for security analysis.
Scans working directory for dependencies, containers, cloud configs, and secrets exposure.
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Any

def find_files(root: str, patterns: list[str]) -> list[Path]:
    """Find files matching glob patterns."""
    root_path = Path(root)
    found = []
    for pattern in patterns:
        found.extend(root_path.rglob(pattern))
    return [f for f in found if f.is_file() and 'node_modules' not in str(f) and '.git' not in str(f)]

def parse_package_json(path: Path) -> list[dict]:
    """Extract dependencies from package.json."""
    deps = []
    try:
        data = json.loads(path.read_text())
        for dep_type in ['dependencies', 'devDependencies']:
            for name, version in data.get(dep_type, {}).items():
                deps.append({
                    'name': name,
                    'version': version.lstrip('^~'),
                    'type': 'npm',
                    'source': str(path)
                })
    except Exception as e:
        print(f"Warning: Could not parse {path}: {e}", file=sys.stderr)
    return deps

def parse_requirements(path: Path) -> list[dict]:
    """Extract dependencies from requirements.txt."""
    deps = []
    try:
        for line in path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith('#'):
                match = re.match(r'^([a-zA-Z0-9_-]+)([=<>!]+)?(.+)?', line)
                if match:
                    deps.append({
                        'name': match.group(1),
                        'version': match.group(3) or 'latest',
                        'type': 'pip',
                        'source': str(path)
                    })
    except Exception as e:
        print(f"Warning: Could not parse {path}: {e}", file=sys.stderr)
    return deps

def parse_gemfile(path: Path) -> list[dict]:
    """Extract dependencies from Gemfile."""
    deps = []
    try:
        for line in path.read_text().splitlines():
            match = re.match(r"gem\s+['\"]([^'\"]+)['\"](?:,\s*['\"]([^'\"]+)['\"])?", line)
            if match:
                deps.append({
                    'name': match.group(1),
                    'version': match.group(2) or 'latest',
                    'type': 'gem',
                    'source': str(path)
                })
    except Exception as e:
        print(f"Warning: Could not parse {path}: {e}", file=sys.stderr)
    return deps

def parse_go_mod(path: Path) -> list[dict]:
    """Extract dependencies from go.mod."""
    deps = []
    try:
        in_require = False
        for line in path.read_text().splitlines():
            if line.strip() == 'require (':
                in_require = True
            elif line.strip() == ')':
                in_require = False
            elif in_require:
                parts = line.strip().split()
                if len(parts) >= 2:
                    deps.append({
                        'name': parts[0],
                        'version': parts[1],
                        'type': 'go',
                        'source': str(path)
                    })
    except Exception as e:
        print(f"Warning: Could not parse {path}: {e}", file=sys.stderr)
    return deps

def check_secrets_exposure(root: str) -> dict:
    """Check for potential secrets exposure."""
    env_files = find_files(root, ['.env', '.env.*', '*.env'])
    gitignore_path = Path(root) / '.gitignore'
    
    gitignore_patterns = []
    if gitignore_path.exists():
        gitignore_patterns = gitignore_path.read_text().splitlines()
    
    exposed = []
    for env_file in env_files:
        rel_path = str(env_file.relative_to(root))
        is_ignored = any(
            rel_path == pattern.strip() or 
            rel_path.startswith(pattern.strip().rstrip('/'))
            for pattern in gitignore_patterns if pattern.strip() and not pattern.startswith('#')
        )
        if not is_ignored:
            exposed.append(rel_path)
    
    return {
        'env_files_found': [str(f) for f in env_files],
        'potentially_exposed': exposed,
        'risk': 'HIGH' if exposed else 'LOW'
    }

def discover_containers(root: str) -> list[dict]:
    """Find container configurations."""
    containers = []
    
    dockerfiles = find_files(root, ['Dockerfile', 'Dockerfile.*', '*.dockerfile'])
    for df in dockerfiles:
        containers.append({
            'type': 'dockerfile',
            'path': str(df),
            'base_images': extract_base_images(df)
        })
    
    compose_files = find_files(root, ['docker-compose.yml', 'docker-compose.yaml', 'compose.yml'])
    for cf in compose_files:
        containers.append({
            'type': 'docker-compose',
            'path': str(cf)
        })
    
    k8s_files = find_files(root, ['*.yaml', '*.yml'])
    for kf in k8s_files:
        if is_k8s_manifest(kf):
            containers.append({
                'type': 'kubernetes',
                'path': str(kf)
            })
    
    return containers

def extract_base_images(dockerfile: Path) -> list[str]:
    """Extract FROM statements from Dockerfile."""
    images = []
    try:
        for line in dockerfile.read_text().splitlines():
            if line.strip().upper().startswith('FROM'):
                parts = line.split()
                if len(parts) >= 2:
                    images.append(parts[1])
    except:
        pass
    return images

def is_k8s_manifest(path: Path) -> bool:
    """Check if YAML is a Kubernetes manifest."""
    try:
        content = path.read_text()
        return 'apiVersion:' in content and 'kind:' in content
    except:
        return False

def discover_cloud_configs(root: str) -> list[dict]:
    """Find cloud infrastructure configurations."""
    configs = []
    
    tf_files = find_files(root, ['*.tf'])
    if tf_files:
        configs.append({
            'type': 'terraform',
            'files': [str(f) for f in tf_files]
        })
    
    cfn_files = find_files(root, ['*.yaml', '*.yml', '*.json'])
    for cf in cfn_files:
        if is_cloudformation(cf):
            configs.append({
                'type': 'cloudformation',
                'path': str(cf)
            })
    
    return configs

def is_cloudformation(path: Path) -> bool:
    """Check if file is CloudFormation template."""
    try:
        content = path.read_text()
        return 'AWSTemplateFormatVersion' in content or 'AWS::' in content
    except:
        return False

def main():
    root = sys.argv[1] if len(sys.argv) > 1 else '.'
    root = os.path.abspath(root)
    
    inventory = {
        'scan_root': root,
        'dependencies': [],
        'containers': [],
        'cloud_configs': [],
        'secrets_exposure': {}
    }
    
    # Dependencies
    for pkg_json in find_files(root, ['package.json']):
        inventory['dependencies'].extend(parse_package_json(pkg_json))
    
    for req in find_files(root, ['requirements.txt', 'requirements*.txt']):
        inventory['dependencies'].extend(parse_requirements(req))
    
    for gemfile in find_files(root, ['Gemfile']):
        inventory['dependencies'].extend(parse_gemfile(gemfile))
    
    for go_mod in find_files(root, ['go.mod']):
        inventory['dependencies'].extend(parse_go_mod(go_mod))
    
    # Containers
    inventory['containers'] = discover_containers(root)
    
    # Cloud configs
    inventory['cloud_configs'] = discover_cloud_configs(root)
    
    # Secrets
    inventory['secrets_exposure'] = check_secrets_exposure(root)
    
    # Summary
    inventory['summary'] = {
        'total_dependencies': len(inventory['dependencies']),
        'container_configs': len(inventory['containers']),
        'cloud_configs': len(inventory['cloud_configs']),
        'secrets_risk': inventory['secrets_exposure']['risk']
    }
    
    print(json.dumps(inventory, indent=2))

if __name__ == '__main__':
    main()
