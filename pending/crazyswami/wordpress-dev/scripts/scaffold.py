#!/usr/bin/env python3
"""
WordPress Code Scaffold Generator

Generates boilerplate code for custom post types, taxonomies, meta boxes, and more.

Usage:
    python3 scaffold.py --type cpt --name "Property" --slug property --output /path/to/theme/inc/
    python3 scaffold.py --type taxonomy --name "Property Type" --slug property_type --post-type property
    python3 scaffold.py --type meta-box --name "Property Details" --id property_details --post-type property
    python3 scaffold.py --type rest --namespace "theme/v1" --route properties --post-type property
"""

import argparse
import os
import re
import sys
from pathlib import Path


# Template directory
TEMPLATE_DIR = Path(__file__).parent.parent / "templates"


def to_slug(name: str) -> str:
    """Convert name to slug (lowercase with underscores)."""
    slug = name.lower()
    slug = re.sub(r'[^a-z0-9]+', '_', slug)
    slug = slug.strip('_')
    return slug


def to_function_name(name: str) -> str:
    """Convert name to function name format."""
    return to_slug(name)


def to_class_name(name: str) -> str:
    """Convert name to class name (PascalCase)."""
    words = re.split(r'[^a-zA-Z0-9]+', name)
    return ''.join(word.capitalize() for word in words if word)


def to_constant_name(name: str) -> str:
    """Convert name to constant name (UPPER_SNAKE_CASE)."""
    return to_slug(name).upper()


def pluralize(name: str) -> str:
    """Simple pluralization."""
    if name.endswith('y'):
        return name[:-1] + 'ies'
    elif name.endswith('s') or name.endswith('x') or name.endswith('ch') or name.endswith('sh'):
        return name + 'es'
    else:
        return name + 's'


def load_template(template_name: str) -> str:
    """Load template file content."""
    template_path = TEMPLATE_DIR / template_name
    if not template_path.exists():
        print(f"Error: Template not found: {template_path}", file=sys.stderr)
        sys.exit(1)
    return template_path.read_text()


def replace_placeholders(content: str, replacements: dict) -> str:
    """Replace all placeholders in content."""
    for placeholder, value in replacements.items():
        content = content.replace(f'{{{{{placeholder}}}}}', value)
    return content


def generate_cpt(args) -> str:
    """Generate custom post type code."""
    template = load_template('custom-post-type.php')

    name = args.name
    slug = args.slug or to_slug(name)
    plural = args.plural or pluralize(name)
    text_domain = args.text_domain or 'theme-name'
    menu_icon = args.menu_icon or 'dashicons-admin-post'

    replacements = {
        'POST_TYPE': slug,
        'POST_TYPE_NAME': name,
        'POST_TYPE_NAME_PLURAL': plural,
        'TEXT_DOMAIN': text_domain,
        'MENU_ICON': menu_icon,
    }

    return replace_placeholders(template, replacements)


def generate_taxonomy(args) -> str:
    """Generate custom taxonomy code."""
    template = load_template('taxonomy.php')

    name = args.name
    slug = args.slug or to_slug(name)
    plural = args.plural or pluralize(name)
    text_domain = args.text_domain or 'theme-name'
    post_type = args.post_type or 'post'

    replacements = {
        'TAXONOMY': slug,
        'TAXONOMY_NAME': name,
        'TAXONOMY_NAME_PLURAL': plural,
        'POST_TYPE': post_type,
        'TEXT_DOMAIN': text_domain,
    }

    return replace_placeholders(template, replacements)


def generate_meta_box(args) -> str:
    """Generate meta box code."""
    template = load_template('meta-box.php')

    name = args.name
    meta_id = args.id or to_slug(name)
    post_type = args.post_type or 'post'
    text_domain = args.text_domain or 'theme-name'
    prefix = args.prefix or f'_{post_type}'

    replacements = {
        'META_BOX_ID': meta_id,
        'META_BOX_TITLE': name,
        'POST_TYPE': post_type,
        'TEXT_DOMAIN': text_domain,
        'PREFIX': prefix,
    }

    return replace_placeholders(template, replacements)


def generate_rest_endpoint(args) -> str:
    """Generate REST API endpoint code."""
    template = load_template('rest-api-endpoint.php')

    namespace = args.namespace or 'theme/v1'
    route = args.route
    post_type = args.post_type or 'post'
    text_domain = args.text_domain or 'theme-name'

    replacements = {
        'NAMESPACE': namespace,
        'ROUTE': route,
        'POST_TYPE': post_type,
        'TEXT_DOMAIN': text_domain,
    }

    return replace_placeholders(template, replacements)


def save_output(content: str, output_path: str, filename: str):
    """Save generated code to file."""
    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    file_path = output_dir / filename
    file_path.write_text(content)
    print(f"Generated: {file_path}")


def main():
    parser = argparse.ArgumentParser(
        description='WordPress Code Scaffold Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Generate a custom post type:
    python3 scaffold.py --type cpt --name "Property" --slug property --output ./inc/

  Generate a taxonomy:
    python3 scaffold.py --type taxonomy --name "Property Type" --slug property_type --post-type property

  Generate a meta box:
    python3 scaffold.py --type meta-box --name "Property Details" --post-type property

  Generate REST API endpoint:
    python3 scaffold.py --type rest --namespace "theme/v1" --route properties --post-type property
        """
    )

    parser.add_argument(
        '--type', '-t',
        required=True,
        choices=['cpt', 'taxonomy', 'meta-box', 'rest'],
        help='Type of code to generate'
    )
    parser.add_argument(
        '--name', '-n',
        required=True,
        help='Name (e.g., "Property", "Property Type")'
    )
    parser.add_argument(
        '--slug', '-s',
        help='Slug (defaults to lowercase name with underscores)'
    )
    parser.add_argument(
        '--plural', '-p',
        help='Plural name (auto-generated if not provided)'
    )
    parser.add_argument(
        '--post-type',
        help='Associated post type (for taxonomy, meta-box, rest)'
    )
    parser.add_argument(
        '--namespace',
        help='REST API namespace (for rest type)'
    )
    parser.add_argument(
        '--route',
        help='REST API route (for rest type)'
    )
    parser.add_argument(
        '--id',
        help='Meta box ID (for meta-box type)'
    )
    parser.add_argument(
        '--prefix',
        help='Meta key prefix (for meta-box type)'
    )
    parser.add_argument(
        '--text-domain',
        default='theme-name',
        help='Text domain for translations (default: theme-name)'
    )
    parser.add_argument(
        '--menu-icon',
        default='dashicons-admin-post',
        help='Dashicon for admin menu (for cpt type)'
    )
    parser.add_argument(
        '--output', '-o',
        default='.',
        help='Output directory (default: current directory)'
    )
    parser.add_argument(
        '--stdout',
        action='store_true',
        help='Print to stdout instead of saving to file'
    )

    args = parser.parse_args()

    # Generate code based on type
    if args.type == 'cpt':
        content = generate_cpt(args)
        filename = f'class-cpt-{args.slug or to_slug(args.name)}.php'
    elif args.type == 'taxonomy':
        content = generate_taxonomy(args)
        filename = f'class-taxonomy-{args.slug or to_slug(args.name)}.php'
    elif args.type == 'meta-box':
        content = generate_meta_box(args)
        filename = f'class-meta-box-{args.id or to_slug(args.name)}.php'
    elif args.type == 'rest':
        if not args.route:
            print("Error: --route is required for REST endpoint generation", file=sys.stderr)
            sys.exit(1)
        content = generate_rest_endpoint(args)
        filename = f'class-rest-{args.route}.php'

    # Output
    if args.stdout:
        print(content)
    else:
        save_output(content, args.output, filename)
        print(f"\nNext steps:")
        print(f"  1. Review the generated file: {args.output}/{filename}")
        print(f"  2. Include it in your theme's functions.php or plugin main file")
        print(f"  3. Flush permalinks: Settings → Permalinks → Save Changes")


if __name__ == '__main__':
    main()
