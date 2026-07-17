#!/usr/bin/env python3
"""
API Helper - Utilities for API Design and Documentation

This script provides tools for generating OpenAPI specifications,
validating schemas, and creating API documentation.

Usage:
    python api_helper.py generate --input api.py --output openapi.yaml
    python api_helper.py validate --spec openapi.yaml
    python api_helper.py docs --spec openapi.yaml --output docs/
"""

import argparse
import json
import yaml
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime


class OpenAPIGenerator:
    """Generate OpenAPI specifications from various sources."""

    def __init__(self):
        self.spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "API",
                "version": "1.0.0",
                "description": "API Documentation"
            },
            "servers": [],
            "paths": {},
            "components": {
                "schemas": {},
                "securitySchemes": {}
            }
        }

    def add_server(self, url: str, description: str = ""):
        """Add a server to the OpenAPI spec."""
        self.spec["servers"].append({
            "url": url,
            "description": description
        })

    def add_path(self, path: str, method: str, operation: Dict[str, Any]):
        """Add an API path to the specification."""
        if path not in self.spec["paths"]:
            self.spec["paths"][path] = {}

        self.spec["paths"][path][method.lower()] = operation

    def add_schema(self, name: str, schema: Dict[str, Any]):
        """Add a schema component."""
        self.spec["components"]["schemas"][name] = schema

    def add_security_scheme(self, name: str, scheme: Dict[str, Any]):
        """Add a security scheme."""
        self.spec["components"]["securitySchemes"][name] = scheme

    def to_yaml(self) -> str:
        """Convert specification to YAML format."""
        return yaml.dump(self.spec, default_flow_style=False, sort_keys=False)

    def to_json(self) -> str:
        """Convert specification to JSON format."""
        return json.dumps(self.spec, indent=2)

    def save(self, filepath: str):
        """Save specification to file."""
        ext = filepath.split('.')[-1].lower()

        with open(filepath, 'w') as f:
            if ext == 'yaml' or ext == 'yml':
                f.write(self.to_yaml())
            elif ext == 'json':
                f.write(self.to_json())
            else:
                raise ValueError(f"Unsupported file format: {ext}")

        print(f"OpenAPI specification saved to {filepath}")


class SchemaValidator:
    """Validate OpenAPI specifications and schemas."""

    def __init__(self, spec_path: str):
        self.spec_path = spec_path
        self.errors = []
        self.warnings = []

    def load_spec(self) -> Dict[str, Any]:
        """Load OpenAPI specification from file."""
        with open(self.spec_path, 'r') as f:
            ext = self.spec_path.split('.')[-1].lower()
            if ext in ['yaml', 'yml']:
                return yaml.safe_load(f)
            elif ext == 'json':
                return json.load(f)
            else:
                raise ValueError(f"Unsupported file format: {ext}")

    def validate(self) -> bool:
        """Validate the OpenAPI specification."""
        try:
            spec = self.load_spec()

            # Check required fields
            self._validate_required_fields(spec)

            # Validate paths
            self._validate_paths(spec.get('paths', {}))

            # Validate components
            self._validate_components(spec.get('components', {}))

            # Validate security
            self._validate_security(spec)

            return len(self.errors) == 0

        except Exception as e:
            self.errors.append(f"Failed to load or parse specification: {str(e)}")
            return False

    def _validate_required_fields(self, spec: Dict[str, Any]):
        """Validate required OpenAPI fields."""
        required = ['openapi', 'info', 'paths']
        for field in required:
            if field not in spec:
                self.errors.append(f"Missing required field: {field}")

        if 'info' in spec:
            info_required = ['title', 'version']
            for field in info_required:
                if field not in spec['info']:
                    self.errors.append(f"Missing required info field: {field}")

    def _validate_paths(self, paths: Dict[str, Any]):
        """Validate API paths."""
        if not paths:
            self.warnings.append("No paths defined in specification")
            return

        for path, methods in paths.items():
            if not path.startswith('/'):
                self.errors.append(f"Path must start with '/': {path}")

            for method, operation in methods.items():
                if method not in ['get', 'post', 'put', 'patch', 'delete', 'options', 'head']:
                    self.errors.append(f"Invalid HTTP method: {method} for path {path}")

                if 'responses' not in operation:
                    self.errors.append(f"Missing responses for {method.upper()} {path}")

    def _validate_components(self, components: Dict[str, Any]):
        """Validate component schemas."""
        schemas = components.get('schemas', {})

        for name, schema in schemas.items():
            if 'type' not in schema and '$ref' not in schema:
                self.warnings.append(f"Schema '{name}' missing type definition")

    def _validate_security(self, spec: Dict[str, Any]):
        """Validate security definitions."""
        schemes = spec.get('components', {}).get('securitySchemes', {})

        if not schemes:
            self.warnings.append("No security schemes defined")
            return

        for name, scheme in schemes.items():
            if 'type' not in scheme:
                self.errors.append(f"Security scheme '{name}' missing type")

    def print_results(self):
        """Print validation results."""
        if self.errors:
            print("\n❌ Errors:")
            for error in self.errors:
                print(f"  - {error}")

        if self.warnings:
            print("\n⚠️  Warnings:")
            for warning in self.warnings:
                print(f"  - {warning}")

        if not self.errors and not self.warnings:
            print("\n✅ Specification is valid!")
        elif not self.errors:
            print(f"\n✅ Specification is valid (with {len(self.warnings)} warnings)")
        else:
            print(f"\n❌ Validation failed with {len(self.errors)} errors")


class DocumentationGenerator:
    """Generate human-readable API documentation."""

    def __init__(self, spec_path: str):
        self.spec_path = spec_path
        self.spec = self._load_spec()

    def _load_spec(self) -> Dict[str, Any]:
        """Load OpenAPI specification."""
        with open(self.spec_path, 'r') as f:
            ext = self.spec_path.split('.')[-1].lower()
            if ext in ['yaml', 'yml']:
                return yaml.safe_load(f)
            elif ext == 'json':
                return json.load(f)

    def generate_markdown(self) -> str:
        """Generate Markdown documentation."""
        md = []

        # Title and description
        info = self.spec.get('info', {})
        md.append(f"# {info.get('title', 'API Documentation')}\n")
        md.append(f"Version: {info.get('version', '1.0.0')}\n")

        if 'description' in info:
            md.append(f"{info['description']}\n")

        # Servers
        if 'servers' in self.spec:
            md.append("## Servers\n")
            for server in self.spec['servers']:
                md.append(f"- **{server.get('description', 'Server')}**: `{server['url']}`")
            md.append("")

        # Authentication
        if 'components' in self.spec and 'securitySchemes' in self.spec['components']:
            md.append("## Authentication\n")
            for name, scheme in self.spec['components']['securitySchemes'].items():
                md.append(f"### {name}")
                md.append(f"Type: `{scheme.get('type')}`")
                if 'description' in scheme:
                    md.append(f"{scheme['description']}")
                md.append("")

        # Endpoints
        md.append("## Endpoints\n")

        paths = self.spec.get('paths', {})
        for path, methods in paths.items():
            for method, operation in methods.items():
                md.append(f"### {method.upper()} {path}\n")

                if 'summary' in operation:
                    md.append(f"{operation['summary']}\n")

                if 'description' in operation:
                    md.append(f"{operation['description']}\n")

                # Parameters
                if 'parameters' in operation:
                    md.append("**Parameters:**\n")
                    for param in operation['parameters']:
                        required = "required" if param.get('required') else "optional"
                        md.append(f"- `{param['name']}` ({param['in']}, {required}): {param.get('description', '')}")
                    md.append("")

                # Request body
                if 'requestBody' in operation:
                    md.append("**Request Body:**\n")
                    content = operation['requestBody'].get('content', {})
                    for content_type in content.keys():
                        md.append(f"Content-Type: `{content_type}`")
                    md.append("")

                # Responses
                if 'responses' in operation:
                    md.append("**Responses:**\n")
                    for status, response in operation['responses'].items():
                        md.append(f"- `{status}`: {response.get('description', '')}")
                    md.append("")

                md.append("---\n")

        return "\n".join(md)

    def save_documentation(self, output_path: str):
        """Save generated documentation to file."""
        doc = self.generate_markdown()

        with open(output_path, 'w') as f:
            f.write(doc)

        print(f"Documentation saved to {output_path}")


def create_sample_spec():
    """Create a sample OpenAPI specification."""
    gen = OpenAPIGenerator()

    # Basic info
    gen.spec['info'] = {
        'title': 'Sample API',
        'version': '1.0.0',
        'description': 'A sample API for demonstration purposes'
    }

    # Servers
    gen.add_server('https://api.example.com/v1', 'Production server')
    gen.add_server('https://staging-api.example.com/v1', 'Staging server')

    # Security scheme
    gen.add_security_scheme('bearerAuth', {
        'type': 'http',
        'scheme': 'bearer',
        'bearerFormat': 'JWT'
    })

    # User schema
    gen.add_schema('User', {
        'type': 'object',
        'required': ['username', 'email'],
        'properties': {
            'id': {'type': 'string', 'example': 'usr_123'},
            'username': {'type': 'string', 'example': 'johndoe'},
            'email': {'type': 'string', 'format': 'email', 'example': 'john@example.com'},
            'createdAt': {'type': 'string', 'format': 'date-time'}
        }
    })

    # List users endpoint
    gen.add_path('/users', 'get', {
        'summary': 'List users',
        'description': 'Retrieve a paginated list of users',
        'parameters': [
            {
                'name': 'limit',
                'in': 'query',
                'description': 'Number of users to return',
                'schema': {'type': 'integer', 'default': 10}
            },
            {
                'name': 'offset',
                'in': 'query',
                'description': 'Number of users to skip',
                'schema': {'type': 'integer', 'default': 0}
            }
        ],
        'responses': {
            '200': {
                'description': 'Successful response',
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'array',
                            'items': {'$ref': '#/components/schemas/User'}
                        }
                    }
                }
            }
        },
        'security': [{'bearerAuth': []}]
    })

    return gen


def main():
    parser = argparse.ArgumentParser(description='API Helper - OpenAPI utilities')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate OpenAPI specification')
    gen_parser.add_argument('--sample', action='store_true', help='Generate sample specification')
    gen_parser.add_argument('--output', '-o', required=True, help='Output file path')

    # Validate command
    val_parser = subparsers.add_parser('validate', help='Validate OpenAPI specification')
    val_parser.add_argument('--spec', '-s', required=True, help='Path to OpenAPI specification')

    # Docs command
    docs_parser = subparsers.add_parser('docs', help='Generate documentation')
    docs_parser.add_argument('--spec', '-s', required=True, help='Path to OpenAPI specification')
    docs_parser.add_argument('--output', '-o', required=True, help='Output file path')

    args = parser.parse_args()

    if args.command == 'generate':
        if args.sample:
            gen = create_sample_spec()
            gen.save(args.output)
        else:
            print("Error: Currently only --sample generation is supported")
            sys.exit(1)

    elif args.command == 'validate':
        validator = SchemaValidator(args.spec)
        is_valid = validator.validate()
        validator.print_results()
        sys.exit(0 if is_valid else 1)

    elif args.command == 'docs':
        doc_gen = DocumentationGenerator(args.spec)
        doc_gen.save_documentation(args.output)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
