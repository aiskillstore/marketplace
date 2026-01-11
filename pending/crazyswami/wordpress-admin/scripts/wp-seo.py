#!/usr/bin/env python3
"""
WordPress SEO Management Script
Sets Yoast SEO fields (focus keyphrase, meta description, SEO title) via WP-CLI
"""

import subprocess
import json
import argparse
import sys

# Site configurations
SITES = {
    "local": {
        "type": "docker",
        "container": "wordpress-local-wordpress-1",
        "url": "https://local2.hustletogether.com"
    },
    "csr": {
        "type": "rest",
        "url": "https://csrdevelopment.com",
        "rest_url": "https://csrdevelopment.com/wp-json/wp/v2"
    }
}

# Yoast meta field keys
YOAST_FIELDS = {
    "focus_kw": "_yoast_wpseo_focuskw",
    "meta_desc": "_yoast_wpseo_metadesc",
    "seo_title": "_yoast_wpseo_title",
    "canonical": "_yoast_wpseo_canonical",
    "meta_robots_noindex": "_yoast_wpseo_meta-robots-noindex",
    "meta_robots_nofollow": "_yoast_wpseo_meta-robots-nofollow",
}

def run_wpcli(container: str, command: str) -> dict:
    """Run WP-CLI command in Docker container"""
    full_cmd = f'docker exec {container} wp {command} --allow-root'
    try:
        result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            return {"error": result.stderr.strip()}
        return {"output": result.stdout.strip(), "success": True}
    except Exception as e:
        return {"error": str(e)}

def set_seo_field(site: str, post_id: str, field: str, value: str) -> dict:
    """Set a single Yoast SEO field"""
    config = SITES.get(site)
    if not config:
        return {"error": f"Unknown site: {site}"}

    meta_key = YOAST_FIELDS.get(field)
    if not meta_key:
        return {"error": f"Unknown SEO field: {field}. Valid: {list(YOAST_FIELDS.keys())}"}

    if config["type"] == "docker":
        # Escape value for shell
        escaped_value = value.replace('"', '\\"').replace("'", "\\'")
        cmd = f'post meta update {post_id} {meta_key} "{escaped_value}"'
        return run_wpcli(config["container"], cmd)

    return {"error": "REST API not implemented yet"}

def set_seo(site: str, post_id: str, focus_kw: str = None,
            meta_desc: str = None, seo_title: str = None) -> dict:
    """Set multiple Yoast SEO fields at once"""
    results = {}

    if focus_kw:
        results["focus_kw"] = set_seo_field(site, post_id, "focus_kw", focus_kw)

    if meta_desc:
        # Validate meta description length
        if len(meta_desc) > 160:
            print(f"Warning: Meta description is {len(meta_desc)} chars (recommended: 150-155)")
        results["meta_desc"] = set_seo_field(site, post_id, "meta_desc", meta_desc)

    if seo_title:
        # Validate SEO title length
        if len(seo_title) > 60:
            print(f"Warning: SEO title is {len(seo_title)} chars (recommended: 50-60)")
        results["seo_title"] = set_seo_field(site, post_id, "seo_title", seo_title)

    # Check if any errors occurred
    errors = [k for k, v in results.items() if "error" in v]
    if errors:
        return {"success": False, "results": results, "errors": errors}

    return {"success": True, "results": results, "post_id": post_id}

def get_seo(site: str, post_id: str) -> dict:
    """Get all Yoast SEO fields for a post"""
    config = SITES.get(site)
    if not config:
        return {"error": f"Unknown site: {site}"}

    if config["type"] == "docker":
        seo_data = {}
        for field_name, meta_key in YOAST_FIELDS.items():
            cmd = f'post meta get {post_id} {meta_key}'
            result = run_wpcli(config["container"], cmd)
            seo_data[field_name] = result.get("output", "")

        return {"post_id": post_id, "seo": seo_data}

    return {"error": "REST API not implemented yet"}

def generate_meta_desc(title: str, focus_kw: str, brand: str = "CSR Real Estate") -> str:
    """Generate a meta description template (user should customize)"""
    templates = [
        f"Learn about {title.lower()} at {brand}. {focus_kw.capitalize()} - your trusted Miami real estate development partner.",
        f"Discover our {title.lower()} page. {brand} provides {focus_kw} with excellence and integrity in Miami.",
        f"{focus_kw.capitalize()} from {brand}. Read our {title.lower()} for complete information about our services.",
    ]

    # Return the first one that's under 155 chars
    for template in templates:
        if len(template) <= 155:
            return template

    # Truncate if needed
    return templates[0][:152] + "..."

def main():
    parser = argparse.ArgumentParser(description='WordPress SEO Management (Yoast)')
    parser.add_argument('--site', default='local', choices=list(SITES.keys()),
                        help='Site to operate on')

    subparsers = parser.add_subparsers(dest='action', help='Action to perform')

    # Set SEO fields
    set_parser = subparsers.add_parser('set', help='Set SEO fields')
    set_parser.add_argument('--post-id', required=True, help='Post/Page ID')
    set_parser.add_argument('--focus-kw', help='Focus keyphrase')
    set_parser.add_argument('--meta-desc', help='Meta description (150-155 chars)')
    set_parser.add_argument('--seo-title', help='SEO title (50-60 chars)')

    # Get SEO fields
    get_parser = subparsers.add_parser('get', help='Get current SEO fields')
    get_parser.add_argument('--post-id', required=True, help='Post/Page ID')

    # Generate meta description
    gen_parser = subparsers.add_parser('generate', help='Generate meta description template')
    gen_parser.add_argument('--title', required=True, help='Page title')
    gen_parser.add_argument('--focus-kw', required=True, help='Focus keyphrase')
    gen_parser.add_argument('--brand', default='CSR Real Estate', help='Brand name')

    args = parser.parse_args()

    if args.action == 'set':
        result = set_seo(args.site, args.post_id, args.focus_kw,
                        args.meta_desc, args.seo_title)
    elif args.action == 'get':
        result = get_seo(args.site, args.post_id)
    elif args.action == 'generate':
        result = {"meta_desc": generate_meta_desc(args.title, args.focus_kw, args.brand)}
    else:
        parser.print_help()
        return

    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
