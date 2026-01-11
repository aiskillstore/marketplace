#!/usr/bin/env python3
"""
WordPress Theme Test Analyzer

Analyzes WordPress theme PHP files to extract testable elements
for E2E test generation with Playwright.

Usage:
    python3 analyze.py /path/to/theme [--output json|markdown]
"""

import os
import re
import sys
import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional


@dataclass
class FormField:
    name: str
    type: str
    required: bool = False
    validation: Optional[str] = None


@dataclass
class Form:
    file: str
    line: int
    action: str
    method: str
    fields: List[FormField] = field(default_factory=list)
    nonce_field: Optional[str] = None
    nonce_action: Optional[str] = None
    success_redirect: Optional[str] = None
    error_redirect: Optional[str] = None


@dataclass
class Link:
    file: str
    href: str
    text: Optional[str] = None
    classes: List[str] = field(default_factory=list)


@dataclass
class DynamicContent:
    file: str
    type: str  # wp_query, conditional, meta, loop
    description: str
    line: int


@dataclass
class JSInteraction:
    file: str
    type: str  # onclick, toggle, data-attr
    target: str
    action: str


@dataclass
class PageTemplate:
    file: str
    template_name: Optional[str] = None
    sections: List[str] = field(default_factory=list)
    animations: List[str] = field(default_factory=list)
    has_form: bool = False


@dataclass
class CustomPostType:
    name: str
    slug: str
    supports: List[str] = field(default_factory=list)
    meta_fields: List[str] = field(default_factory=list)


@dataclass
class AnalysisResult:
    theme_path: str
    forms: List[Form] = field(default_factory=list)
    pages: List[PageTemplate] = field(default_factory=list)
    links: List[Link] = field(default_factory=list)
    dynamic_content: List[DynamicContent] = field(default_factory=list)
    js_interactions: List[JSInteraction] = field(default_factory=list)
    custom_post_types: List[CustomPostType] = field(default_factory=list)
    navigation_menus: Dict[str, List[str]] = field(default_factory=dict)
    theme_options: List[str] = field(default_factory=list)


class WordPressThemeAnalyzer:
    def __init__(self, theme_path: str):
        self.theme_path = Path(theme_path)
        self.result = AnalysisResult(theme_path=str(theme_path))

    def analyze(self) -> AnalysisResult:
        """Run full analysis on the theme."""
        php_files = list(self.theme_path.glob("**/*.php"))

        for php_file in php_files:
            self._analyze_file(php_file)

        # Analyze JS files for animation functions
        js_files = list(self.theme_path.glob("**/*.js"))
        for js_file in js_files:
            self._analyze_js_file(js_file)

        return self.result

    def _analyze_file(self, file_path: Path):
        """Analyze a single PHP file."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            relative_path = str(file_path.relative_to(self.theme_path))
        except Exception as e:
            print(f"Error reading {file_path}: {e}", file=sys.stderr)
            return

        # Extract template name
        template_match = re.search(r'Template Name:\s*(.+)', content)
        template_name = template_match.group(1).strip() if template_match else None

        # Create page template entry
        page = PageTemplate(
            file=relative_path,
            template_name=template_name
        )

        # Find forms
        self._extract_forms(content, relative_path)

        # Find links
        self._extract_links(content, relative_path)

        # Find dynamic content
        self._extract_dynamic_content(content, relative_path)

        # Find JS interactions
        self._extract_js_interactions(content, relative_path)

        # Find custom post types
        self._extract_custom_post_types(content, relative_path)

        # Find navigation menus
        self._extract_navigation(content, relative_path)

        # Find theme options
        self._extract_theme_options(content, relative_path)

        # Find sections (HTML comments or section tags)
        sections = re.findall(r'<!--\s*(.+?)\s*-->', content)
        page.sections = [s for s in sections if 'Section' in s or 'section' in s.lower()]

        # Find animation calls
        animations = re.findall(r'CSRAnimations\.(\w+)\(\)', content)
        page.animations = animations

        # Check if page has form
        page.has_form = '<form' in content.lower()

        if template_name or page.sections or page.animations:
            self.result.pages.append(page)

    def _extract_forms(self, content: str, file: str):
        """Extract form elements from PHP content."""
        # Find form tags
        form_pattern = r'<form[^>]*>(.*?)</form>'
        forms = re.findall(form_pattern, content, re.DOTALL | re.IGNORECASE)

        for i, form_content in enumerate(forms):
            form = Form(
                file=file,
                line=content[:content.find(form_content)].count('\n') + 1,
                action='POST to self',  # Default
                method='POST'
            )

            # Extract method
            method_match = re.search(r'method=["\'](\w+)["\']', form_content, re.IGNORECASE)
            if method_match:
                form.method = method_match.group(1).upper()

            # Extract action
            action_match = re.search(r'action=["\']([^"\']+)["\']', form_content, re.IGNORECASE)
            if action_match:
                form.action = action_match.group(1)

            # Extract input fields
            inputs = re.findall(
                r'<input[^>]*name=["\']([^"\']+)["\'][^>]*type=["\']([^"\']+)["\'][^>]*>|'
                r'<input[^>]*type=["\']([^"\']+)["\'][^>]*name=["\']([^"\']+)["\'][^>]*>|'
                r'<textarea[^>]*name=["\']([^"\']+)["\'][^>]*>',
                form_content, re.IGNORECASE
            )

            for match in inputs:
                name = match[0] or match[3] or match[4]
                input_type = match[1] or match[2] or 'textarea'
                if name and not name.startswith('_'):  # Skip hidden/nonce fields
                    required = 'required' in form_content[form_content.find(name):form_content.find(name)+200]
                    form.fields.append(FormField(
                        name=name,
                        type=input_type,
                        required=required
                    ))

            # Extract nonce
            nonce_match = re.search(r"wp_nonce_field\(['\"]([^'\"]+)['\"],\s*['\"]([^'\"]+)['\"]", content)
            if nonce_match:
                form.nonce_action = nonce_match.group(1)
                form.nonce_field = nonce_match.group(2)

            # Find success/error redirects
            success_match = re.search(r'\?[\w]+=success', content)
            error_match = re.search(r'\?[\w]+=error', content)
            if success_match:
                form.success_redirect = success_match.group(0)
            if error_match:
                form.error_redirect = error_match.group(0)

            if form.fields:  # Only add forms with fields
                self.result.forms.append(form)

    def _extract_links(self, content: str, file: str):
        """Extract links from PHP content."""
        # Find anchor tags
        link_pattern = r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>'
        links = re.findall(link_pattern, content, re.DOTALL | re.IGNORECASE)

        for href, text in links:
            # Skip PHP-only hrefs
            if href.startswith('<?php') and '?>' not in href:
                continue

            # Extract classes
            class_match = re.search(rf'<a[^>]*href=["\'{re.escape(href)}["\'][^>]*class=["\']([^"\']+)["\']', content)
            classes = class_match.group(1).split() if class_match else []

            # Clean text
            clean_text = re.sub(r'<[^>]+>', '', text).strip()
            clean_text = re.sub(r'\s+', ' ', clean_text)

            if clean_text:
                self.result.links.append(Link(
                    file=file,
                    href=href[:100],  # Truncate long hrefs
                    text=clean_text[:50],
                    classes=classes[:5]
                ))

    def _extract_dynamic_content(self, content: str, file: str):
        """Extract dynamic content patterns."""
        # WP_Query
        queries = re.finditer(r'new WP_Query\s*\(\s*array\s*\((.*?)\)\s*\)', content, re.DOTALL)
        for match in queries:
            self.result.dynamic_content.append(DynamicContent(
                file=file,
                type='wp_query',
                description=f"WP_Query with params",
                line=content[:match.start()].count('\n') + 1
            ))

        # Conditionals
        conditionals = re.finditer(r'<\?php\s+if\s*\(([^)]+)\)\s*:', content)
        for match in conditionals:
            condition = match.group(1)[:50]
            self.result.dynamic_content.append(DynamicContent(
                file=file,
                type='conditional',
                description=f"Conditional: {condition}",
                line=content[:match.start()].count('\n') + 1
            ))

        # Post meta
        meta_calls = re.finditer(r"get_post_meta\s*\([^,]+,\s*['\"]([^'\"]+)['\"]", content)
        for match in meta_calls:
            self.result.dynamic_content.append(DynamicContent(
                file=file,
                type='meta',
                description=f"Post meta: {match.group(1)}",
                line=content[:match.start()].count('\n') + 1
            ))

    def _extract_js_interactions(self, content: str, file: str):
        """Extract JavaScript interactions from PHP content."""
        # onclick handlers
        onclick_matches = re.finditer(r'onclick=["\']([^"\']+)["\']', content)
        for match in onclick_matches:
            self.result.js_interactions.append(JSInteraction(
                file=file,
                type='onclick',
                target='element',
                action=match.group(1)[:50]
            ))

        # ID-based interactions (likely JS targets)
        id_matches = re.finditer(r'id=["\']([^"\']+)["\']', content)
        for match in id_matches:
            id_name = match.group(1)
            if any(keyword in id_name.lower() for keyword in ['btn', 'button', 'toggle', 'menu', 'modal', 'overlay']):
                self.result.js_interactions.append(JSInteraction(
                    file=file,
                    type='id_target',
                    target=f"#{id_name}",
                    action='Interactive element'
                ))

        # Class toggles mentioned
        toggle_matches = re.finditer(r"classList\.(toggle|add|remove)\(['\"]([^'\"]+)['\"]", content)
        for match in toggle_matches:
            self.result.js_interactions.append(JSInteraction(
                file=file,
                type='class_toggle',
                target='element',
                action=f"{match.group(1)}('{match.group(2)}')"
            ))

    def _extract_custom_post_types(self, content: str, file: str):
        """Extract custom post type registrations."""
        cpt_matches = re.finditer(
            r"register_post_type\s*\(\s*['\"]([^'\"]+)['\"]",
            content
        )
        for match in cpt_matches:
            cpt_name = match.group(1)

            # Try to find supports array
            supports = []
            supports_match = re.search(
                rf"register_post_type.*?{cpt_name}.*?'supports'\s*=>\s*array\s*\(([^)]+)\)",
                content, re.DOTALL
            )
            if supports_match:
                supports = re.findall(r"['\"](\w+)['\"]", supports_match.group(1))

            self.result.custom_post_types.append(CustomPostType(
                name=cpt_name,
                slug=cpt_name,
                supports=supports
            ))

    def _extract_navigation(self, content: str, file: str):
        """Extract navigation menu registrations."""
        menu_matches = re.finditer(
            r"['\"](\w+)['\"].*?['\"]([^'\"]+)['\"].*?register_nav_menu",
            content
        )
        for match in menu_matches:
            menu_slug = match.group(1)
            menu_name = match.group(2)
            if menu_slug not in self.result.navigation_menus:
                self.result.navigation_menus[menu_slug] = []

    def _extract_theme_options(self, content: str, file: str):
        """Extract theme options/settings."""
        option_matches = re.finditer(
            r"get_option\s*\(\s*['\"]([^'\"]+)['\"]|"
            r"csr_get_option\s*\(\s*['\"]([^'\"]+)['\"]",
            content
        )
        for match in option_matches:
            option = match.group(1) or match.group(2)
            if option and option not in self.result.theme_options:
                self.result.theme_options.append(option)

    def _analyze_js_file(self, file_path: Path):
        """Analyze JavaScript files for animation functions."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            relative_path = str(file_path.relative_to(self.theme_path))
        except Exception as e:
            return

        # Find function definitions
        func_matches = re.finditer(r'(\w+)\s*[=:]\s*(?:function|async function|\([^)]*\)\s*=>)', content)
        for match in func_matches:
            func_name = match.group(1)
            if func_name.startswith('init') or 'animate' in func_name.lower():
                self.result.js_interactions.append(JSInteraction(
                    file=relative_path,
                    type='animation_function',
                    target='page',
                    action=func_name
                ))


def to_dict(obj):
    """Convert dataclass to dict, handling nested dataclasses."""
    if hasattr(obj, '__dataclass_fields__'):
        return {k: to_dict(v) for k, v in asdict(obj).items()}
    elif isinstance(obj, list):
        return [to_dict(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: to_dict(v) for k, v in obj.items()}
    else:
        return obj


def generate_markdown_report(result: AnalysisResult) -> str:
    """Generate a markdown report from analysis results."""
    lines = [
        f"# WordPress Theme Analysis Report",
        f"\n**Theme Path:** `{result.theme_path}`\n",
        f"---\n",
        f"## Summary\n",
        f"- **Forms:** {len(result.forms)}",
        f"- **Page Templates:** {len(result.pages)}",
        f"- **Links:** {len(result.links)}",
        f"- **Dynamic Content:** {len(result.dynamic_content)}",
        f"- **JS Interactions:** {len(result.js_interactions)}",
        f"- **Custom Post Types:** {len(result.custom_post_types)}",
        f"- **Theme Options:** {len(result.theme_options)}",
        f"\n---\n",
    ]

    if result.forms:
        lines.append("## Forms\n")
        for form in result.forms:
            lines.append(f"### Form in `{form.file}`")
            lines.append(f"- **Method:** {form.method}")
            lines.append(f"- **Action:** {form.action}")
            if form.nonce_field:
                lines.append(f"- **Nonce:** {form.nonce_field}")
            lines.append(f"- **Fields:**")
            for field in form.fields:
                req = " (required)" if field.required else ""
                lines.append(f"  - `{field.name}` [{field.type}]{req}")
            if form.success_redirect:
                lines.append(f"- **Success redirect:** `{form.success_redirect}`")
            lines.append("")

    if result.pages:
        lines.append("## Page Templates\n")
        for page in result.pages:
            lines.append(f"### `{page.file}`")
            if page.template_name:
                lines.append(f"- **Template:** {page.template_name}")
            if page.sections:
                lines.append(f"- **Sections:** {', '.join(page.sections)}")
            if page.animations:
                lines.append(f"- **Animations:** {', '.join(page.animations)}")
            if page.has_form:
                lines.append(f"- **Has form:** Yes")
            lines.append("")

    if result.custom_post_types:
        lines.append("## Custom Post Types\n")
        for cpt in result.custom_post_types:
            lines.append(f"- **{cpt.name}** (slug: `{cpt.slug}`)")
            if cpt.supports:
                lines.append(f"  - Supports: {', '.join(cpt.supports)}")
            lines.append("")

    if result.theme_options:
        lines.append("## Theme Options\n")
        for opt in result.theme_options:
            lines.append(f"- `{opt}`")
        lines.append("")

    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 analyze.py /path/to/theme [--output json|markdown]")
        sys.exit(1)

    theme_path = sys.argv[1]
    output_format = 'json'

    if '--output' in sys.argv:
        idx = sys.argv.index('--output')
        if idx + 1 < len(sys.argv):
            output_format = sys.argv[idx + 1]

    if not os.path.isdir(theme_path):
        print(f"Error: {theme_path} is not a valid directory")
        sys.exit(1)

    analyzer = WordPressThemeAnalyzer(theme_path)
    result = analyzer.analyze()

    if output_format == 'markdown':
        print(generate_markdown_report(result))
    else:
        print(json.dumps(to_dict(result), indent=2))


if __name__ == '__main__':
    main()
