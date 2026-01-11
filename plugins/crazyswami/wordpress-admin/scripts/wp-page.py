#!/usr/bin/env python3
"""
WordPress Page Management Script
Creates and manages WordPress pages via WP-CLI (Docker) or REST API
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

def run_wpcli(container: str, command: str) -> dict:
    """Run WP-CLI command in Docker container"""
    full_cmd = f'docker exec {container} wp {command} --allow-root --format=json'
    try:
        result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            # Try without --format=json for commands that don't support it
            full_cmd = f'docker exec {container} wp {command} --allow-root'
            result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Error: {result.stderr}", file=sys.stderr)
                return {"error": result.stderr}
            return {"output": result.stdout.strip()}
        return json.loads(result.stdout) if result.stdout.strip() else {"output": "Success"}
    except json.JSONDecodeError:
        return {"output": result.stdout.strip()}
    except Exception as e:
        return {"error": str(e)}

def create_page(site: str, title: str, slug: str = None, template: str = None,
                content: str = "", status: str = "publish") -> dict:
    """Create a new WordPress page"""
    config = SITES.get(site)
    if not config:
        return {"error": f"Unknown site: {site}"}

    if config["type"] == "docker":
        # Build WP-CLI command
        cmd_parts = [
            'post create',
            '--post_type=page',
            f'--post_title="{title}"',
            f'--post_status={status}'
        ]

        if slug:
            cmd_parts.append(f'--post_name="{slug}"')

        if content:
            # Escape content for shell
            escaped_content = content.replace('"', '\\"').replace("'", "\\'")
            cmd_parts.append(f'--post_content="{escaped_content}"')

        cmd_parts.append('--porcelain')  # Return just the post ID

        cmd = ' '.join(cmd_parts)
        result = run_wpcli(config["container"], cmd)

        if "error" in result:
            return result

        # Get the post ID from output
        post_id = result.get("output", "").strip()

        # Set template if provided
        if template and post_id:
            template_cmd = f'post meta update {post_id} _wp_page_template "{template}"'
            run_wpcli(config["container"], template_cmd)

        return {
            "success": True,
            "post_id": post_id,
            "url": f"{config['url']}/{slug or title.lower().replace(' ', '-')}/"
        }

    return {"error": "REST API not implemented yet"}

def list_pages(site: str) -> list:
    """List all pages"""
    config = SITES.get(site)
    if not config:
        return [{"error": f"Unknown site: {site}"}]

    if config["type"] == "docker":
        result = run_wpcli(config["container"], 'post list --post_type=page')
        return result if isinstance(result, list) else [result]

    return [{"error": "REST API not implemented yet"}]

def get_page(site: str, post_id: str = None, slug: str = None) -> dict:
    """Get page details by ID or slug"""
    config = SITES.get(site)
    if not config:
        return {"error": f"Unknown site: {site}"}

    if config["type"] == "docker":
        if post_id:
            cmd = f'post get {post_id}'
        elif slug:
            cmd = f'post list --post_type=page --name="{slug}" --field=ID'
            result = run_wpcli(config["container"], cmd)
            post_id = result.get("output", "").strip()
            if not post_id:
                return {"error": f"Page with slug '{slug}' not found"}
            cmd = f'post get {post_id}'
        else:
            return {"error": "Must provide post_id or slug"}

        return run_wpcli(config["container"], cmd)

    return {"error": "REST API not implemented yet"}

def update_page(site: str, post_id: str, **kwargs) -> dict:
    """Update an existing page"""
    config = SITES.get(site)
    if not config:
        return {"error": f"Unknown site: {site}"}

    if config["type"] == "docker":
        cmd_parts = [f'post update {post_id}']

        if kwargs.get('title'):
            cmd_parts.append(f'--post_title="{kwargs["title"]}"')
        if kwargs.get('slug'):
            cmd_parts.append(f'--post_name="{kwargs["slug"]}"')
        if kwargs.get('content'):
            escaped = kwargs["content"].replace('"', '\\"')
            cmd_parts.append(f'--post_content="{escaped}"')
        if kwargs.get('status'):
            cmd_parts.append(f'--post_status={kwargs["status"]}')

        cmd = ' '.join(cmd_parts)
        result = run_wpcli(config["container"], cmd)

        # Set template if provided
        if kwargs.get('template'):
            template_cmd = f'post meta update {post_id} _wp_page_template "{kwargs["template"]}"'
            run_wpcli(config["container"], template_cmd)

        return {"success": True, "post_id": post_id}

    return {"error": "REST API not implemented yet"}

def delete_page(site: str, post_id: str, force: bool = False) -> dict:
    """Delete a page"""
    config = SITES.get(site)
    if not config:
        return {"error": f"Unknown site: {site}"}

    if config["type"] == "docker":
        cmd = f'post delete {post_id}'
        if force:
            cmd += ' --force'
        return run_wpcli(config["container"], cmd)

    return {"error": "REST API not implemented yet"}

def main():
    parser = argparse.ArgumentParser(description='WordPress Page Management')
    parser.add_argument('--site', default='local', choices=list(SITES.keys()),
                        help='Site to operate on')

    subparsers = parser.add_subparsers(dest='action', help='Action to perform')

    # Create page
    create_parser = subparsers.add_parser('create', help='Create a new page')
    create_parser.add_argument('--title', required=True, help='Page title')
    create_parser.add_argument('--slug', help='URL slug')
    create_parser.add_argument('--template', help='Page template file')
    create_parser.add_argument('--content', default='', help='Page content')
    create_parser.add_argument('--status', default='publish', help='Page status')

    # List pages
    subparsers.add_parser('list', help='List all pages')

    # Get page
    get_parser = subparsers.add_parser('get', help='Get page details')
    get_parser.add_argument('--id', help='Post ID')
    get_parser.add_argument('--slug', help='Page slug')

    # Update page
    update_parser = subparsers.add_parser('update', help='Update a page')
    update_parser.add_argument('--id', required=True, help='Post ID')
    update_parser.add_argument('--title', help='New title')
    update_parser.add_argument('--slug', help='New slug')
    update_parser.add_argument('--template', help='New template')
    update_parser.add_argument('--content', help='New content')
    update_parser.add_argument('--status', help='New status')

    # Delete page
    delete_parser = subparsers.add_parser('delete', help='Delete a page')
    delete_parser.add_argument('--id', required=True, help='Post ID')
    delete_parser.add_argument('--force', action='store_true', help='Skip trash')

    args = parser.parse_args()

    if args.action == 'create':
        result = create_page(args.site, args.title, args.slug, args.template,
                            args.content, args.status)
    elif args.action == 'list':
        result = list_pages(args.site)
    elif args.action == 'get':
        result = get_page(args.site, args.id, args.slug)
    elif args.action == 'update':
        result = update_page(args.site, args.id, title=args.title, slug=args.slug,
                            template=args.template, content=args.content,
                            status=args.status)
    elif args.action == 'delete':
        result = delete_page(args.site, args.id, args.force)
    else:
        parser.print_help()
        return

    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
