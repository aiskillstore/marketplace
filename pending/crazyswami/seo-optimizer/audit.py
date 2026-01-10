#!/usr/bin/env python3
"""
SEO Audit Script for WordPress (Yoast/Rank Math)

Audits all pages and posts for:
- Focus keyword presence
- Meta description quality (length, keyword inclusion)
- Featured image presence and metadata

Usage:
    python3 audit.py --base-url https://local2.hustletogether.com
    python3 audit.py --base-url https://local2.hustletogether.com --json
    python3 audit.py --base-url https://local2.hustletogether.com --page about
"""

import argparse
import json
import re
import sys
from typing import Dict, List, Optional
from urllib.parse import urljoin
import subprocess

# Docker database config
DB_CONTAINER = "wordpress-local-db-1"
DB_USER = "wordpress"
DB_PASS = "wordpress"
DB_NAME = "wordpress"


def run_mysql_query(query: str) -> List[Dict]:
    """Run MySQL query against WordPress database"""
    try:
        cmd = [
            'docker', 'exec', DB_CONTAINER,
            'mysql', f'-u{DB_USER}', f'-p{DB_PASS}', DB_NAME,
            '-N', '-e', query
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            rows = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    rows.append(line.split('\t'))
            return rows
    except Exception as e:
        print(f"MySQL Error: {e}", file=sys.stderr)
    return []


def get_yoast_meta(post_id: int) -> Dict:
    """Get Yoast SEO meta from database"""
    query = f"""
        SELECT meta_key, meta_value FROM wp_postmeta
        WHERE post_id = {post_id}
        AND meta_key IN (
            '_yoast_wpseo_focuskw',
            '_yoast_wpseo_metadesc',
            '_yoast_wpseo_title',
            '_thumbnail_id'
        )
    """
    rows = run_mysql_query(query)
    meta = {}
    for row in rows:
        if len(row) >= 2:
            meta[row[0]] = row[1]
    return meta


def get_media_info(media_id: int) -> Dict:
    """Get media attachment info from database"""
    query = f"""
        SELECT p.ID, p.post_title, pm.meta_value as alt_text, pm2.meta_value as file_path
        FROM wp_posts p
        LEFT JOIN wp_postmeta pm ON p.ID = pm.post_id AND pm.meta_key = '_wp_attachment_image_alt'
        LEFT JOIN wp_postmeta pm2 ON p.ID = pm2.post_id AND pm2.meta_key = '_wp_attached_file'
        WHERE p.ID = {media_id}
    """
    rows = run_mysql_query(query)
    if rows and len(rows[0]) >= 4:
        return {
            'id': rows[0][0],
            'title': rows[0][1],
            'alt': rows[0][2] or '',
            'file': rows[0][3] or ''
        }
    return {}


def fetch_json(url: str) -> Optional[Dict]:
    """Fetch JSON from URL using curl"""
    try:
        result = subprocess.run(
            ['curl', '-s', url],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0 and result.stdout:
            return json.loads(result.stdout)
    except Exception as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
    return None


def get_all_pages(base_url: str) -> List[Dict]:
    """Get all pages from WordPress REST API"""
    api_url = f"{base_url}/wp-json/wp/v2/pages?per_page=100"
    pages = fetch_json(api_url)
    return pages if pages else []


def get_all_posts(base_url: str, post_type: str = 'posts') -> List[Dict]:
    """Get all posts of a given type from WordPress REST API"""
    api_url = f"{base_url}/wp-json/wp/v2/{post_type}?per_page=100"
    posts = fetch_json(api_url)
    return posts if posts else []


def audit_page(base_url: str, page: Dict) -> Dict:
    """Audit a single page for SEO issues"""
    page_id = page['id']
    title = page['title']['rendered'] if isinstance(page['title'], dict) else page['title']
    slug = page['slug']
    page_url = f"{base_url}/{slug}/"

    # Get Yoast SEO data from database
    yoast_meta = get_yoast_meta(page_id)

    # Initialize audit result
    audit = {
        'id': page_id,
        'title': title,
        'slug': slug,
        'url': page_url,
        'focus_keyword': {
            'status': 'missing',
            'value': None,
            'in_title': False,
            'in_description': False
        },
        'meta_description': {
            'status': 'missing',
            'length': 0,
            'value': None,
            'has_keyword': False
        },
        'featured_image': {
            'status': 'missing',
            'id': None,
            'url': None,
            'alt': None,
            'title': None,
            'keyword_in_alt': False,
            'keyword_in_title': False
        },
        'seo_title': yoast_meta.get('_yoast_wpseo_title', title),
        'score': 0,
        'issues': [],
        'recommendations': []
    }

    # Check focus keyword
    focus_kw = yoast_meta.get('_yoast_wpseo_focuskw', '')
    if focus_kw:
        audit['focus_keyword']['status'] = 'ok'
        audit['focus_keyword']['value'] = focus_kw
        audit['score'] += 25

        # Check if in title
        seo_title = yoast_meta.get('_yoast_wpseo_title', title)
        if focus_kw.lower() in seo_title.lower():
            audit['focus_keyword']['in_title'] = True
            audit['score'] += 10
        else:
            audit['issues'].append('Focus keyword not in SEO title')
            audit['recommendations'].append(f'Add "{focus_kw}" to SEO title')
    else:
        audit['issues'].append('No focus keyword set')
        audit['recommendations'].append(f'Set a focus keyword (suggested: "{slug.replace("-", " ")}")')

    # Check meta description
    description = yoast_meta.get('_yoast_wpseo_metadesc', '')
    if description:
        audit['meta_description']['status'] = 'ok'
        audit['meta_description']['value'] = description
        audit['meta_description']['length'] = len(description)
        audit['score'] += 20

        # Check length
        if len(description) < 120:
            audit['meta_description']['status'] = 'too_short'
            audit['issues'].append(f'Meta description too short ({len(description)} chars, need 120+)')
            audit['recommendations'].append('Expand meta description to 120-160 characters')
            audit['score'] -= 5
        elif len(description) > 160:
            audit['meta_description']['status'] = 'too_long'
            audit['issues'].append(f'Meta description too long ({len(description)} chars, max 160)')
            audit['recommendations'].append('Shorten meta description to 120-160 characters')
            audit['score'] -= 5

        # Check if focus keyword in description
        if focus_kw and focus_kw.lower() in description.lower():
            audit['meta_description']['has_keyword'] = True
            audit['focus_keyword']['in_description'] = True
            audit['score'] += 15
        elif focus_kw:
            audit['issues'].append('Focus keyword not in meta description')
            audit['recommendations'].append(f'Include "{focus_kw}" in meta description')
    else:
        audit['issues'].append('No meta description set')
        audit['recommendations'].append('Add a meta description (120-160 chars) containing focus keyword')

    # Check featured image
    thumbnail_id = yoast_meta.get('_thumbnail_id', '')
    if thumbnail_id:
        audit['featured_image']['status'] = 'ok'
        audit['featured_image']['id'] = int(thumbnail_id)
        audit['score'] += 15

        # Get image details
        img_info = get_media_info(int(thumbnail_id))
        if img_info:
            audit['featured_image']['title'] = img_info.get('title', '')
            audit['featured_image']['alt'] = img_info.get('alt', '')
            audit['featured_image']['url'] = img_info.get('file', '')

            # Check if focus keyword in ALT
            alt_text = audit['featured_image']['alt'] or ''
            img_title = audit['featured_image']['title'] or ''

            if focus_kw:
                # Check ALT text
                if focus_kw.lower() in alt_text.lower():
                    audit['featured_image']['keyword_in_alt'] = True
                    audit['score'] += 7
                else:
                    audit['issues'].append('Focus keyword not in image ALT text')
                    audit['recommendations'].append(f'Update image ALT to include "{focus_kw}"')

                # Check title - should BE the focus keyword
                if focus_kw.lower() == img_title.lower() or focus_kw.lower() in img_title.lower():
                    audit['featured_image']['keyword_in_title'] = True
                    audit['score'] += 8
                else:
                    audit['issues'].append('Image title should be the focus keyword')
                    audit['recommendations'].append(f'Rename image title to "{focus_kw}"')
    else:
        audit['issues'].append('No featured image set')
        audit['recommendations'].append(f'Add a featured image (search Unsplash for "{focus_kw or slug}")')

    # Cap score at 100
    audit['score'] = min(100, max(0, audit['score']))

    return audit


def print_audit_report(audits: List[Dict], output_json: bool = False):
    """Print audit report in human-readable or JSON format"""
    if output_json:
        print(json.dumps(audits, indent=2))
        return

    print("\n" + "=" * 60)
    print("SEO AUDIT REPORT")
    print("=" * 60)

    total_score = 0
    total_pages = len(audits)

    for audit in audits:
        print(f"\n{'─' * 60}")
        print(f"Page: {audit['title']}")
        print(f"URL: {audit['url']}")
        print(f"{'─' * 60}")

        # Focus Keyword
        fk = audit['focus_keyword']
        fk_icon = '✓' if fk['status'] == 'ok' else '✗'
        print(f"\nFocus Keyword: {fk['value'] or 'NOT SET'} {fk_icon}")
        if fk['value']:
            print(f"  - In SEO title: {'YES ✓' if fk['in_title'] else 'NO ✗'}")
            print(f"  - In meta desc: {'YES ✓' if fk['in_description'] else 'NO ✗'}")

        # Meta Description
        md = audit['meta_description']
        md_icon = '✓' if md['status'] == 'ok' else '✗'
        print(f"\nMeta Description: {md['status'].upper()} {md_icon}")
        if md['value']:
            length_status = ""
            if md['length'] < 120:
                length_status = " (too short)"
            elif md['length'] > 160:
                length_status = " (too long)"
            else:
                length_status = " (optimal)"
            print(f"  - Length: {md['length']} chars{length_status}")
            print(f"  - Has keyword: {'YES ✓' if md['has_keyword'] else 'NO ✗'}")
            # Truncate long descriptions
            desc_preview = md['value'][:80] + '...' if len(md['value']) > 80 else md['value']
            print(f"  - Preview: \"{desc_preview}\"")

        # Featured Image
        fi = audit['featured_image']
        fi_icon = '✓' if fi['status'] == 'ok' else '✗'
        print(f"\nFeatured Image: {fi['status'].upper()} {fi_icon}")
        if fi['id']:
            print(f"  - ID: {fi['id']}")
            print(f"  - Title: {fi['title'] or '(empty)'} {'✓' if fi['keyword_in_title'] else '✗'}")
            print(f"  - ALT: {fi['alt'] or '(empty)'} {'✓' if fi['keyword_in_alt'] else '✗'}")

        # Score
        score = audit['score']
        total_score += score
        score_bar = '█' * (score // 10) + '░' * (10 - score // 10)
        print(f"\nScore: [{score_bar}] {score}/100")

        # Issues & Recommendations
        if audit['issues']:
            print(f"\nIssues ({len(audit['issues'])}):")
            for issue in audit['issues']:
                print(f"  ✗ {issue}")

        if audit['recommendations']:
            print(f"\nFix:")
            for i, rec in enumerate(audit['recommendations'], 1):
                print(f"  {i}. {rec}")

    # Summary
    avg_score = total_score / total_pages if total_pages > 0 else 0
    print(f"\n{'=' * 60}")
    print(f"SUMMARY")
    print(f"{'=' * 60}")
    print(f"Pages Audited: {total_pages}")
    print(f"Average Score: {avg_score:.0f}/100")

    # Count issues by type
    pages_missing_keyword = sum(1 for a in audits if a['focus_keyword']['status'] == 'missing')
    pages_missing_desc = sum(1 for a in audits if a['meta_description']['status'] == 'missing')
    pages_missing_image = sum(1 for a in audits if a['featured_image']['status'] == 'missing')
    pages_keyword_not_in_desc = sum(1 for a in audits if a['focus_keyword']['value'] and not a['meta_description']['has_keyword'])
    pages_keyword_not_in_img = sum(1 for a in audits if a['focus_keyword']['value'] and a['featured_image']['id'] and not a['featured_image']['keyword_in_alt'])

    print(f"\nIssue Breakdown:")
    print(f"  Missing focus keyword: {pages_missing_keyword}")
    print(f"  Missing meta description: {pages_missing_desc}")
    print(f"  Missing featured image: {pages_missing_image}")
    print(f"  Keyword not in description: {pages_keyword_not_in_desc}")
    print(f"  Keyword not in image ALT: {pages_keyword_not_in_img}")


def main():
    parser = argparse.ArgumentParser(description='SEO Audit for WordPress (Yoast/Rank Math)')
    parser.add_argument('--base-url', type=str, default='https://local2.hustletogether.com',
                        help='WordPress site base URL')
    parser.add_argument('--page', type=str, help='Audit specific page by slug')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--include-posts', action='store_true', help='Include posts in audit')
    parser.add_argument('--post-type', type=str, default='property',
                        help='Custom post type to audit (default: property)')

    args = parser.parse_args()

    audits = []

    # Get all pages
    print(f"Fetching pages from {args.base_url}...", file=sys.stderr)
    pages = get_all_pages(args.base_url)

    if args.page:
        # Filter to specific page
        pages = [p for p in pages if p['slug'] == args.page]
        if not pages:
            print(f"Page '{args.page}' not found", file=sys.stderr)
            sys.exit(1)

    print(f"Auditing {len(pages)} pages...", file=sys.stderr)

    for page in pages:
        audit = audit_page(args.base_url, page)
        audits.append(audit)

    # Optionally include posts
    if args.include_posts:
        print(f"Fetching {args.post_type} posts...", file=sys.stderr)
        posts = get_all_posts(args.base_url, args.post_type)
        print(f"Auditing {len(posts)} posts...", file=sys.stderr)

        for post in posts:
            audit = audit_page(args.base_url, post)
            audits.append(audit)

    print_audit_report(audits, args.json)


if __name__ == "__main__":
    main()
