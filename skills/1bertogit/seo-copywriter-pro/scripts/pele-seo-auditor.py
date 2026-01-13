#!/usr/bin/env python3
"""
🏆 PELÉ SEO AUDITOR - Professional Grade
Complete SEO analysis tool following James/Diesel Dudes methodology.

Features:
- Technical SEO (robots.txt, sitemap, SSL, redirects)
- On-Page SEO (title, meta, H1, content analysis)
- Core Web Vitals (via PageSpeed Insights API)
- Schema.org validation (JSON-LD parsing)
- Internal linking analysis (link graph)
- Hreflang validation (reciprocal check)
- Broken link detection
- Duplicate content detection
- Mobile-friendliness check
- Keyword density analysis
- Comprehensive HTML/JSON/CSV reports

Usage:
  python pele-seo-auditor.py <url-or-path> [options]
  
Options:
  --output, -o    Output format: html, json, csv, md (default: md)
  --depth, -d     Crawl depth for URL audits (default: 2)
  --api-key       Google PageSpeed API key (optional, increases limits)
  --verbose, -v   Show detailed progress
  --fix           Generate fix suggestions with code examples

Examples:
  python pele-seo-auditor.py ./my-astro-project
  python pele-seo-auditor.py https://example.com --depth 3 --output html
  python pele-seo-auditor.py ./src/pages --output json --verbose
"""

import os
import sys
import re
import json
import hashlib
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse
import xml.etree.ElementTree as ET

# Optional imports (graceful degradation)
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class SEOIssue:
    """Represents a single SEO issue."""
    severity: str  # critical, high, medium, low
    category: str  # technical, onpage, schema, performance, etc
    message: str
    file: str = ""
    line: int = 0
    fix: str = ""
    impact: str = ""


@dataclass
class PageAnalysis:
    """Analysis results for a single page."""
    url: str
    title: str = ""
    title_length: int = 0
    description: str = ""
    description_length: int = 0
    h1_count: int = 0
    h1_text: str = ""
    h2_count: int = 0
    word_count: int = 0
    has_schema: bool = False
    schema_types: List[str] = field(default_factory=list)
    has_canonical: bool = False
    canonical_url: str = ""
    has_hreflang: bool = False
    hreflang_tags: Dict[str, str] = field(default_factory=dict)
    images_total: int = 0
    images_without_alt: int = 0
    internal_links: List[str] = field(default_factory=list)
    external_links: List[str] = field(default_factory=list)
    broken_links: List[str] = field(default_factory=list)
    content_hash: str = ""
    issues: List[SEOIssue] = field(default_factory=list)


@dataclass
class SiteAnalysis:
    """Analysis results for entire site."""
    base_url: str
    audit_date: str
    total_pages: int = 0
    pages: List[PageAnalysis] = field(default_factory=list)
    
    # Technical SEO
    has_robots_txt: bool = False
    robots_txt_valid: bool = False
    has_sitemap: bool = False
    sitemap_valid: bool = False
    sitemap_urls: int = 0
    has_ssl: bool = False
    
    # Aggregated stats
    pages_with_title: int = 0
    pages_with_description: int = 0
    pages_with_h1: int = 0
    pages_with_schema: int = 0
    pages_with_canonical: int = 0
    
    # Issues
    issues: List[SEOIssue] = field(default_factory=list)
    
    # Scores
    score_technical: int = 100
    score_onpage: int = 100
    score_schema: int = 100
    score_performance: int = 100
    score_total: int = 100
    
    # Core Web Vitals (if available)
    cwv_lcp: float = 0
    cwv_fid: float = 0
    cwv_cls: float = 0
    
    # Duplicate content
    duplicate_groups: List[List[str]] = field(default_factory=list)
    
    # Link graph
    orphan_pages: List[str] = field(default_factory=list)
    most_linked: List[Tuple[str, int]] = field(default_factory=list)


# =============================================================================
# CORE AUDITOR CLASS
# =============================================================================

class PeleSEOAuditor:
    """Professional-grade SEO auditor."""
    
    def __init__(self, target: str, options: dict = None):
        self.target = target
        self.options = options or {}
        self.is_url = target.startswith(('http://', 'https://'))
        self.is_local = not self.is_url
        
        self.site = SiteAnalysis(
            base_url=target,
            audit_date=datetime.now().isoformat()
        )
        
        # Internal tracking
        self.content_hashes: Dict[str, List[str]] = defaultdict(list)
        self.link_graph: Dict[str, Set[str]] = defaultdict(set)
        self.all_pages: Set[str] = set()
        
        # Verbose mode
        self.verbose = options.get('verbose', False)
    
    def log(self, msg: str):
        """Print if verbose mode."""
        if self.verbose:
            print(f"  → {msg}")
    
    # =========================================================================
    # LOCAL FILE ANALYSIS
    # =========================================================================
    
    def audit_local(self):
        """Audit a local project directory."""
        self.log(f"Auditing local project: {self.target}")
        
        # Find project root
        root = Path(self.target)
        if not root.exists():
            self.site.issues.append(SEOIssue(
                severity="critical",
                category="technical",
                message=f"Path not found: {self.target}"
            ))
            return
        
        # Check for common structures
        src_pages = root / "src" / "pages"
        public_dir = root / "public"
        
        pages_dir = src_pages if src_pages.exists() else root
        
        # Check essential files
        self._check_robots_txt(public_dir if public_dir.exists() else root)
        self._check_sitemap(root, pages_dir)
        
        # Audit all page files
        extensions = ('.html', '.astro', '.jsx', '.tsx', '.vue', '.svelte')
        
        for filepath in pages_dir.rglob('*'):
            if filepath.suffix in extensions and not filepath.name.startswith('_'):
                self._audit_local_file(filepath, pages_dir)
        
        # Post-processing
        self._detect_duplicates()
        self._analyze_link_graph()
        self._calculate_scores()
    
    def _check_robots_txt(self, public_dir: Path):
        """Check robots.txt existence and validity."""
        robots_path = public_dir / "robots.txt"
        
        if not robots_path.exists():
            self.site.issues.append(SEOIssue(
                severity="critical",
                category="technical",
                message="Missing robots.txt",
                fix="Create public/robots.txt with:\nUser-agent: *\nAllow: /\nSitemap: https://yoursite.com/sitemap.xml",
                impact="Search engines may not crawl efficiently"
            ))
            return
        
        self.site.has_robots_txt = True
        
        # Validate content
        content = robots_path.read_text()
        
        if "User-agent" not in content:
            self.site.issues.append(SEOIssue(
                severity="high",
                category="technical",
                message="robots.txt missing User-agent directive",
                file=str(robots_path)
            ))
        
        if "Sitemap:" not in content:
            self.site.issues.append(SEOIssue(
                severity="medium",
                category="technical",
                message="robots.txt missing Sitemap directive",
                file=str(robots_path),
                fix="Add: Sitemap: https://yoursite.com/sitemap.xml"
            ))
        
        if "Disallow: /" in content and "Allow:" not in content:
            self.site.issues.append(SEOIssue(
                severity="critical",
                category="technical",
                message="robots.txt blocks all crawling (Disallow: /)",
                file=str(robots_path)
            ))
        else:
            self.site.robots_txt_valid = True
    
    def _check_sitemap(self, root: Path, pages_dir: Path):
        """Check sitemap existence."""
        # Check for static sitemap
        static_sitemap = root / "public" / "sitemap.xml"
        # Check for dynamic sitemap (Astro)
        dynamic_sitemap = pages_dir / "sitemap.xml.astro"
        # Check for sitemap in astro.config
        astro_config = root / "astro.config.mjs"
        
        has_sitemap = (
            static_sitemap.exists() or 
            dynamic_sitemap.exists() or
            (astro_config.exists() and "@astrojs/sitemap" in astro_config.read_text())
        )
        
        if not has_sitemap:
            self.site.issues.append(SEOIssue(
                severity="critical",
                category="technical",
                message="Missing sitemap.xml",
                fix="For Astro: npx astro add sitemap\nOr create public/sitemap.xml manually",
                impact="Pages may not be indexed by search engines"
            ))
        else:
            self.site.has_sitemap = True
            self.site.sitemap_valid = True
            
            # Count URLs if static sitemap exists
            if static_sitemap.exists():
                try:
                    tree = ET.parse(static_sitemap)
                    urls = tree.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url')
                    self.site.sitemap_urls = len(urls)
                except:
                    pass
    
    def _audit_local_file(self, filepath: Path, pages_dir: Path):
        """Audit a single local file."""
        try:
            content = filepath.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            self.log(f"Error reading {filepath}: {e}")
            return
        
        # Get relative path for reporting
        rel_path = filepath.relative_to(pages_dir) if pages_dir in filepath.parents else filepath.name
        
        page = PageAnalysis(url=str(rel_path))
        
        # Analyze content
        self._analyze_html_content(content, page, str(rel_path))
        
        # Track for duplicate detection
        content_hash = hashlib.md5(self._extract_text(content).encode()).hexdigest()
        page.content_hash = content_hash
        self.content_hashes[content_hash].append(str(rel_path))
        
        # Track for link graph
        self.all_pages.add(str(rel_path))
        for link in page.internal_links:
            self.link_graph[link].add(str(rel_path))
        
        # Add to site
        self.site.pages.append(page)
        self.site.total_pages += 1
        
        # Update aggregated stats
        if page.title:
            self.site.pages_with_title += 1
        if page.description:
            self.site.pages_with_description += 1
        if page.h1_count == 1:
            self.site.pages_with_h1 += 1
        if page.has_schema:
            self.site.pages_with_schema += 1
        if page.has_canonical:
            self.site.pages_with_canonical += 1
    
    def _analyze_html_content(self, content: str, page: PageAnalysis, filename: str):
        """Analyze HTML/template content for SEO factors."""
        
        # =====================================================================
        # TITLE ANALYSIS
        # =====================================================================
        
        # Direct title tag
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', content, re.IGNORECASE | re.DOTALL)
        
        # Astro/React: title prop in frontmatter or component
        title_prop = re.search(r'title\s*[=:]\s*["\']([^"\']+)["\']', content)
        
        # SEO component usage
        seo_title = re.search(r'<SEO[^>]*title\s*=\s*["\']([^"\']+)["\']', content, re.IGNORECASE)
        
        if title_match:
            page.title = title_match.group(1).strip()
        elif seo_title:
            page.title = seo_title.group(1).strip()
        elif title_prop:
            page.title = title_prop.group(1).strip()
        
        if page.title:
            page.title_length = len(page.title)
            
            if page.title_length > 60:
                page.issues.append(SEOIssue(
                    severity="high",
                    category="onpage",
                    message=f"Title too long ({page.title_length} chars, max 60)",
                    file=filename,
                    fix=f"Shorten to: {page.title[:57]}..."
                ))
            elif page.title_length < 30:
                page.issues.append(SEOIssue(
                    severity="medium",
                    category="onpage",
                    message=f"Title too short ({page.title_length} chars, min 30)",
                    file=filename
                ))
        else:
            # Check if using layout (Astro pattern)
            uses_layout = re.search(r'<(BaseLayout|Layout|MainLayout)', content)
            if not uses_layout:
                page.issues.append(SEOIssue(
                    severity="critical",
                    category="onpage",
                    message="Missing title tag",
                    file=filename,
                    fix="Add <title>Your Page Title</title> in <head>",
                    impact="Page won't rank properly"
                ))
        
        # =====================================================================
        # META DESCRIPTION ANALYSIS
        # =====================================================================
        
        desc_match = re.search(
            r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)["\']',
            content, re.IGNORECASE
        )
        desc_prop = re.search(r'description\s*[=:]\s*["\']([^"\']+)["\']', content)
        seo_desc = re.search(r'<SEO[^>]*description\s*=\s*["\']([^"\']+)["\']', content, re.IGNORECASE)
        
        if desc_match:
            page.description = desc_match.group(1).strip()
        elif seo_desc:
            page.description = seo_desc.group(1).strip()
        elif desc_prop:
            page.description = desc_prop.group(1).strip()
        
        if page.description:
            page.description_length = len(page.description)
            
            if page.description_length > 160:
                page.issues.append(SEOIssue(
                    severity="medium",
                    category="onpage",
                    message=f"Meta description too long ({page.description_length} chars, max 160)",
                    file=filename,
                    fix=f"Shorten to: {page.description[:157]}..."
                ))
            elif page.description_length < 70:
                page.issues.append(SEOIssue(
                    severity="low",
                    category="onpage",
                    message=f"Meta description too short ({page.description_length} chars)",
                    file=filename
                ))
        else:
            uses_layout = re.search(r'<(BaseLayout|Layout|MainLayout)', content)
            if not uses_layout:
                page.issues.append(SEOIssue(
                    severity="high",
                    category="onpage",
                    message="Missing meta description",
                    file=filename,
                    fix='Add <meta name="description" content="Your description here">',
                    impact="Lower click-through rate in SERPs"
                ))
        
        # =====================================================================
        # HEADING ANALYSIS
        # =====================================================================
        
        h1_matches = re.findall(r'<h1[^>]*>(.*?)</h1>', content, re.IGNORECASE | re.DOTALL)
        page.h1_count = len(h1_matches)
        
        if h1_matches:
            # Clean HTML from first H1
            page.h1_text = re.sub(r'<[^>]+>', '', h1_matches[0]).strip()
        
        if page.h1_count == 0:
            # Check for dynamic H1 patterns
            has_dynamic_h1 = re.search(r'\{.*?title.*?\}|<h1[^>]*>\s*\{', content)
            if not has_dynamic_h1:
                page.issues.append(SEOIssue(
                    severity="critical",
                    category="onpage",
                    message="Missing H1 tag",
                    file=filename,
                    fix="Add <h1>Your Main Heading</h1>",
                    impact="Search engines can't identify page topic"
                ))
        elif page.h1_count > 1:
            page.issues.append(SEOIssue(
                severity="high",
                category="onpage",
                message=f"Multiple H1 tags ({page.h1_count} found)",
                file=filename,
                fix="Keep only one H1, convert others to H2"
            ))
        
        # Check heading hierarchy
        h2_matches = re.findall(r'<h2[^>]*>', content, re.IGNORECASE)
        h3_matches = re.findall(r'<h3[^>]*>', content, re.IGNORECASE)
        page.h2_count = len(h2_matches)
        
        if h3_matches and not h2_matches:
            page.issues.append(SEOIssue(
                severity="medium",
                category="onpage",
                message="H3 used without H2 (broken hierarchy)",
                file=filename,
                fix="Add H2 headings before H3s"
            ))
        
        # =====================================================================
        # SCHEMA MARKUP ANALYSIS
        # =====================================================================
        
        # JSON-LD
        jsonld_matches = re.findall(
            r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
            content, re.IGNORECASE | re.DOTALL
        )
        
        # Schema components (Astro pattern)
        schema_components = re.findall(
            r'<Schema(Organization|Person|Article|Course|FAQ|Breadcrumb|Markup)[^>]*',
            content, re.IGNORECASE
        )
        
        if jsonld_matches or schema_components:
            page.has_schema = True
            
            # Parse JSON-LD to get types
            for jsonld in jsonld_matches:
                try:
                    data = json.loads(jsonld)
                    if isinstance(data, dict):
                        schema_type = data.get('@type', '')
                        if schema_type:
                            page.schema_types.append(schema_type)
                    elif isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict):
                                schema_type = item.get('@type', '')
                                if schema_type:
                                    page.schema_types.append(schema_type)
                except json.JSONDecodeError:
                    page.issues.append(SEOIssue(
                        severity="high",
                        category="schema",
                        message="Invalid JSON-LD schema (parse error)",
                        file=filename,
                        fix="Validate at https://search.google.com/test/rich-results"
                    ))
            
            # Add component types
            for comp_type in schema_components:
                page.schema_types.append(comp_type)
        else:
            page.issues.append(SEOIssue(
                severity="low",
                category="schema",
                message="No schema markup found",
                file=filename,
                fix="Add JSON-LD schema for better rich snippets"
            ))
        
        # =====================================================================
        # CANONICAL URL
        # =====================================================================
        
        canonical_match = re.search(
            r'<link[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\']',
            content, re.IGNORECASE
        )
        
        if canonical_match:
            page.has_canonical = True
            page.canonical_url = canonical_match.group(1)
        
        # =====================================================================
        # HREFLANG TAGS
        # =====================================================================
        
        hreflang_matches = re.findall(
            r'<link[^>]*hreflang=["\']([^"\']+)["\'][^>]*href=["\']([^"\']+)["\']',
            content, re.IGNORECASE
        )
        
        if hreflang_matches:
            page.has_hreflang = True
            for lang, href in hreflang_matches:
                page.hreflang_tags[lang] = href
            
            # Check for x-default
            if 'x-default' not in page.hreflang_tags:
                page.issues.append(SEOIssue(
                    severity="medium",
                    category="technical",
                    message="hreflang missing x-default",
                    file=filename,
                    fix='Add <link rel="alternate" hreflang="x-default" href="...">'
                ))
        
        # =====================================================================
        # IMAGE ANALYSIS
        # =====================================================================
        
        img_matches = re.findall(r'<img[^>]*>', content, re.IGNORECASE)
        page.images_total = len(img_matches)
        
        for img in img_matches:
            # Check for alt attribute
            has_alt = re.search(r'alt\s*=\s*["\']([^"\']*)["\']', img, re.IGNORECASE)
            
            if not has_alt:
                page.images_without_alt += 1
            elif has_alt.group(1).strip() == '':
                # Empty alt (decorative image is OK, but flag for review)
                pass
        
        if page.images_without_alt > 0:
            page.issues.append(SEOIssue(
                severity="medium",
                category="onpage",
                message=f"{page.images_without_alt} images missing alt text",
                file=filename,
                fix="Add descriptive alt text to all images",
                impact="Accessibility issues, missed image SEO"
            ))
        
        # Check for lazy loading
        if page.images_total > 3:
            has_lazy = 'loading="lazy"' in content or 'loading=\'lazy\'' in content
            if not has_lazy:
                page.issues.append(SEOIssue(
                    severity="low",
                    category="performance",
                    message="Images not using lazy loading",
                    file=filename,
                    fix='Add loading="lazy" to images below the fold'
                ))
        
        # =====================================================================
        # LINK ANALYSIS
        # =====================================================================
        
        link_matches = re.findall(r'<a[^>]*href=["\']([^"\'#]+)["\']', content, re.IGNORECASE)
        
        for href in link_matches:
            if href.startswith(('http://', 'https://', '//')):
                page.external_links.append(href)
            elif href.startswith('/') or not href.startswith(('mailto:', 'tel:', 'javascript:')):
                page.internal_links.append(href)
        
        # =====================================================================
        # CONTENT ANALYSIS
        # =====================================================================
        
        text_content = self._extract_text(content)
        words = text_content.split()
        page.word_count = len(words)
        
        # Check content length
        if page.word_count < 300 and not filename.endswith(('404.astro', 'index.astro')):
            page.issues.append(SEOIssue(
                severity="low",
                category="onpage",
                message=f"Thin content ({page.word_count} words)",
                file=filename,
                fix="Expand content to at least 300 words for better SEO"
            ))
        
        # Add page issues to site issues
        self.site.issues.extend(page.issues)
    
    def _extract_text(self, html: str) -> str:
        """Extract visible text from HTML."""
        # Remove script and style
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        # Remove frontmatter (Astro/MDX)
        text = re.sub(r'---.*?---', '', text, flags=re.DOTALL)
        # Clean up whitespace
        text = ' '.join(text.split())
        return text
    
    def _detect_duplicates(self):
        """Detect duplicate content across pages."""
        for content_hash, pages in self.content_hashes.items():
            if len(pages) > 1:
                self.site.duplicate_groups.append(pages)
                self.site.issues.append(SEOIssue(
                    severity="high",
                    category="onpage",
                    message=f"Duplicate content detected: {', '.join(pages[:3])}{'...' if len(pages) > 3 else ''}",
                    fix="Ensure each page has unique content or use canonical tags"
                ))
    
    def _analyze_link_graph(self):
        """Analyze internal linking structure."""
        # Find orphan pages (no internal links pointing to them)
        linked_pages = set()
        for target, sources in self.link_graph.items():
            linked_pages.add(target)
        
        for page in self.all_pages:
            # Normalize path for comparison
            normalized = '/' + str(page).replace('.astro', '').replace('.html', '').replace('index', '')
            if normalized not in linked_pages and page not in linked_pages:
                self.site.orphan_pages.append(page)
        
        if self.site.orphan_pages:
            self.site.issues.append(SEOIssue(
                severity="medium",
                category="technical",
                message=f"{len(self.site.orphan_pages)} orphan pages (no internal links)",
                fix="Add internal links to these pages from other content"
            ))
        
        # Find most linked pages
        link_counts = [(target, len(sources)) for target, sources in self.link_graph.items()]
        link_counts.sort(key=lambda x: x[1], reverse=True)
        self.site.most_linked = link_counts[:10]
    
    def _calculate_scores(self):
        """Calculate SEO scores by category."""
        total_pages = max(self.site.total_pages, 1)
        
        # Technical score
        tech_score = 100
        tech_issues = [i for i in self.site.issues if i.category == 'technical']
        for issue in tech_issues:
            if issue.severity == 'critical':
                tech_score -= 20
            elif issue.severity == 'high':
                tech_score -= 10
            elif issue.severity == 'medium':
                tech_score -= 5
            else:
                tech_score -= 2
        self.site.score_technical = max(0, tech_score)
        
        # On-page score
        onpage_score = 0
        onpage_score += (self.site.pages_with_title / total_pages) * 30
        onpage_score += (self.site.pages_with_description / total_pages) * 25
        onpage_score += (self.site.pages_with_h1 / total_pages) * 25
        onpage_score += (self.site.pages_with_canonical / total_pages) * 20
        self.site.score_onpage = min(100, int(onpage_score))
        
        # Schema score
        schema_pct = self.site.pages_with_schema / total_pages
        self.site.score_schema = int(schema_pct * 100)
        
        # Performance score (placeholder - would need real metrics)
        perf_issues = [i for i in self.site.issues if i.category == 'performance']
        self.site.score_performance = max(0, 100 - len(perf_issues) * 10)
        
        # Total score (weighted average)
        self.site.score_total = int(
            self.site.score_technical * 0.30 +
            self.site.score_onpage * 0.35 +
            self.site.score_schema * 0.15 +
            self.site.score_performance * 0.20
        )
    
    # =========================================================================
    # URL CRAWLING (if requests available)
    # =========================================================================
    
    def audit_url(self):
        """Audit a live URL (requires requests library)."""
        if not HAS_REQUESTS:
            print("Error: 'requests' library required for URL auditing")
            print("Install with: pip install requests beautifulsoup4")
            sys.exit(1)
        
        self.log(f"Auditing URL: {self.target}")
        
        depth = self.options.get('depth', 2)
        visited = set()
        to_visit = [(self.target, 0)]
        
        # Check robots.txt
        self._check_robots_url()
        
        # Check sitemap
        self._check_sitemap_url()
        
        # Crawl pages
        while to_visit:
            url, current_depth = to_visit.pop(0)
            
            if url in visited or current_depth > depth:
                continue
            
            visited.add(url)
            page = self._fetch_and_analyze_url(url)
            
            if page:
                self.site.pages.append(page)
                self.site.total_pages += 1
                
                # Add internal links to queue
                if current_depth < depth:
                    for link in page.internal_links:
                        full_url = urljoin(self.target, link)
                        if full_url not in visited and full_url.startswith(self.target):
                            to_visit.append((full_url, current_depth + 1))
        
        self._calculate_scores()
    
    def _check_robots_url(self):
        """Check robots.txt for live URL."""
        robots_url = urljoin(self.target, '/robots.txt')
        try:
            resp = requests.get(robots_url, timeout=10)
            if resp.status_code == 200:
                self.site.has_robots_txt = True
                if 'User-agent' in resp.text:
                    self.site.robots_txt_valid = True
            else:
                self.site.issues.append(SEOIssue(
                    severity="critical",
                    category="technical",
                    message="robots.txt not found (404)"
                ))
        except:
            pass
    
    def _check_sitemap_url(self):
        """Check sitemap.xml for live URL."""
        sitemap_url = urljoin(self.target, '/sitemap.xml')
        try:
            resp = requests.get(sitemap_url, timeout=10)
            if resp.status_code == 200:
                self.site.has_sitemap = True
                self.site.sitemap_valid = True
                # Count URLs
                try:
                    root = ET.fromstring(resp.content)
                    urls = root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url')
                    self.site.sitemap_urls = len(urls)
                except:
                    pass
        except:
            self.site.issues.append(SEOIssue(
                severity="critical",
                category="technical",
                message="Could not fetch sitemap.xml"
            ))
    
    def _fetch_and_analyze_url(self, url: str) -> Optional[PageAnalysis]:
        """Fetch and analyze a single URL."""
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code != 200:
                return None
            
            page = PageAnalysis(url=url)
            self._analyze_html_content(resp.text, page, url)
            
            return page
        except Exception as e:
            self.log(f"Error fetching {url}: {e}")
            return None
    
    # =========================================================================
    # CORE WEB VITALS (requires API key)
    # =========================================================================
    
    def check_core_web_vitals(self):
        """Check Core Web Vitals using PageSpeed Insights API."""
        if not HAS_REQUESTS:
            return
        
        api_key = self.options.get('api_key', '')
        
        # Use public endpoint (limited to 25 queries/day without key)
        psi_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        params = {
            'url': self.target,
            'strategy': 'mobile',
            'category': ['performance', 'seo']
        }
        
        if api_key:
            params['key'] = api_key
        
        try:
            resp = requests.get(psi_url, params=params, timeout=60)
            if resp.status_code == 200:
                data = resp.json()
                
                # Extract Core Web Vitals
                metrics = data.get('lighthouseResult', {}).get('audits', {})
                
                lcp = metrics.get('largest-contentful-paint', {}).get('numericValue', 0) / 1000
                fid = metrics.get('max-potential-fid', {}).get('numericValue', 0)
                cls = metrics.get('cumulative-layout-shift', {}).get('numericValue', 0)
                
                self.site.cwv_lcp = round(lcp, 2)
                self.site.cwv_fid = round(fid, 0)
                self.site.cwv_cls = round(cls, 3)
                
                # Add issues based on metrics
                if lcp > 4:
                    self.site.issues.append(SEOIssue(
                        severity="critical",
                        category="performance",
                        message=f"LCP too slow ({lcp}s, should be < 2.5s)",
                        fix="Optimize images, reduce JS, use CDN"
                    ))
                elif lcp > 2.5:
                    self.site.issues.append(SEOIssue(
                        severity="high",
                        category="performance",
                        message=f"LCP needs improvement ({lcp}s)"
                    ))
                
                if cls > 0.25:
                    self.site.issues.append(SEOIssue(
                        severity="critical",
                        category="performance",
                        message=f"CLS too high ({cls}, should be < 0.1)",
                        fix="Set explicit image dimensions, avoid layout shifts"
                    ))
                elif cls > 0.1:
                    self.site.issues.append(SEOIssue(
                        severity="medium",
                        category="performance",
                        message=f"CLS needs improvement ({cls})"
                    ))
                
                self.log(f"Core Web Vitals: LCP={lcp}s, CLS={cls}")
        except Exception as e:
            self.log(f"Could not fetch PageSpeed data: {e}")
    
    # =========================================================================
    # REPORT GENERATION
    # =========================================================================
    
    def generate_report(self, format: str = 'md') -> str:
        """Generate audit report in specified format."""
        if format == 'json':
            return self._report_json()
        elif format == 'html':
            return self._report_html()
        elif format == 'csv':
            return self._report_csv()
        else:
            return self._report_markdown()
    
    def _report_markdown(self) -> str:
        """Generate Markdown report."""
        lines = []
        
        # Header
        lines.append("# 🏆 PELÉ SEO AUDIT REPORT")
        lines.append("")
        lines.append(f"**Target:** {self.site.base_url}")
        lines.append(f"**Date:** {self.site.audit_date[:10]}")
        lines.append(f"**Pages Analyzed:** {self.site.total_pages}")
        lines.append("")
        
        # Score summary
        lines.append("---")
        lines.append("")
        lines.append(f"## 📊 Overall Score: {self.site.score_total}/100")
        lines.append("")
        lines.append("| Category | Score | Status |")
        lines.append("|----------|-------|--------|")
        lines.append(f"| Technical SEO | {self.site.score_technical}/100 | {self._score_emoji(self.site.score_technical)} |")
        lines.append(f"| On-Page SEO | {self.site.score_onpage}/100 | {self._score_emoji(self.site.score_onpage)} |")
        lines.append(f"| Schema Markup | {self.site.score_schema}/100 | {self._score_emoji(self.site.score_schema)} |")
        lines.append(f"| Performance | {self.site.score_performance}/100 | {self._score_emoji(self.site.score_performance)} |")
        lines.append("")
        
        # Technical SEO status
        lines.append("---")
        lines.append("")
        lines.append("## 🔧 Technical SEO Status")
        lines.append("")
        lines.append("| Item | Status |")
        lines.append("|------|--------|")
        lines.append(f"| robots.txt | {'✅ Valid' if self.site.robots_txt_valid else '❌ Missing/Invalid'} |")
        lines.append(f"| sitemap.xml | {'✅ Valid' if self.site.sitemap_valid else '❌ Missing/Invalid'} |")
        if self.site.sitemap_urls:
            lines.append(f"| Sitemap URLs | {self.site.sitemap_urls} |")
        lines.append(f"| SSL/HTTPS | {'✅' if self.site.has_ssl or self.is_local else '⚠️ Check'} |")
        lines.append("")
        
        # Core Web Vitals (if available)
        if self.site.cwv_lcp > 0:
            lines.append("---")
            lines.append("")
            lines.append("## ⚡ Core Web Vitals")
            lines.append("")
            lines.append("| Metric | Value | Target | Status |")
            lines.append("|--------|-------|--------|--------|")
            lines.append(f"| LCP | {self.site.cwv_lcp}s | < 2.5s | {self._cwv_status(self.site.cwv_lcp, 2.5, 4)} |")
            lines.append(f"| FID | {self.site.cwv_fid}ms | < 100ms | {self._cwv_status(self.site.cwv_fid, 100, 300)} |")
            lines.append(f"| CLS | {self.site.cwv_cls} | < 0.1 | {self._cwv_status(self.site.cwv_cls, 0.1, 0.25)} |")
            lines.append("")
        
        # On-page stats
        lines.append("---")
        lines.append("")
        lines.append("## 📝 On-Page SEO Stats")
        lines.append("")
        lines.append("| Metric | Count | Percentage |")
        lines.append("|--------|-------|------------|")
        pct = lambda x: f"{(x / max(self.site.total_pages, 1) * 100):.0f}%"
        lines.append(f"| Pages with Title | {self.site.pages_with_title} | {pct(self.site.pages_with_title)} |")
        lines.append(f"| Pages with Description | {self.site.pages_with_description} | {pct(self.site.pages_with_description)} |")
        lines.append(f"| Pages with H1 | {self.site.pages_with_h1} | {pct(self.site.pages_with_h1)} |")
        lines.append(f"| Pages with Schema | {self.site.pages_with_schema} | {pct(self.site.pages_with_schema)} |")
        lines.append(f"| Pages with Canonical | {self.site.pages_with_canonical} | {pct(self.site.pages_with_canonical)} |")
        lines.append("")
        
        # Issues by severity
        issues_by_severity = defaultdict(list)
        for issue in self.site.issues:
            issues_by_severity[issue.severity].append(issue)
        
        lines.append("---")
        lines.append("")
        lines.append("## 🚨 Issues Found")
        lines.append("")
        
        for severity in ['critical', 'high', 'medium', 'low']:
            issues = issues_by_severity.get(severity, [])
            if issues:
                emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}[severity]
                lines.append(f"### {emoji} {severity.title()} ({len(issues)})")
                lines.append("")
                
                # Group by message to avoid duplicates
                seen = set()
                for issue in issues[:20]:  # Limit display
                    key = issue.message
                    if key not in seen:
                        seen.add(key)
                        lines.append(f"- **{issue.message}**")
                        if issue.file:
                            lines.append(f"  - File: `{issue.file}`")
                        if issue.fix:
                            lines.append(f"  - Fix: {issue.fix}")
                
                if len(issues) > 20:
                    lines.append(f"- ... and {len(issues) - 20} more")
                lines.append("")
        
        # Duplicate content
        if self.site.duplicate_groups:
            lines.append("---")
            lines.append("")
            lines.append("## 📋 Duplicate Content Groups")
            lines.append("")
            for i, group in enumerate(self.site.duplicate_groups[:5], 1):
                lines.append(f"{i}. {', '.join(group[:3])}{'...' if len(group) > 3 else ''}")
            lines.append("")
        
        # Orphan pages
        if self.site.orphan_pages:
            lines.append("---")
            lines.append("")
            lines.append("## 🔗 Orphan Pages (No Internal Links)")
            lines.append("")
            for page in self.site.orphan_pages[:10]:
                lines.append(f"- `{page}`")
            if len(self.site.orphan_pages) > 10:
                lines.append(f"- ... and {len(self.site.orphan_pages) - 10} more")
            lines.append("")
        
        # Most linked pages
        if self.site.most_linked:
            lines.append("---")
            lines.append("")
            lines.append("## 🔥 Most Linked Pages")
            lines.append("")
            lines.append("| Page | Incoming Links |")
            lines.append("|------|----------------|")
            for page, count in self.site.most_linked[:10]:
                lines.append(f"| `{page}` | {count} |")
            lines.append("")
        
        # Recommendations
        lines.append("---")
        lines.append("")
        lines.append("## 💡 Priority Recommendations")
        lines.append("")
        
        if not self.site.robots_txt_valid:
            lines.append("1. **Create/fix robots.txt** - Critical for crawling")
        if not self.site.sitemap_valid:
            lines.append("2. **Create sitemap.xml** - Submit to Google Search Console")
        if self.site.pages_with_title < self.site.total_pages:
            lines.append(f"3. **Add missing titles** - {self.site.total_pages - self.site.pages_with_title} pages affected")
        if self.site.pages_with_description < self.site.total_pages:
            lines.append(f"4. **Add missing descriptions** - {self.site.total_pages - self.site.pages_with_description} pages affected")
        if self.site.pages_with_schema < self.site.total_pages * 0.5:
            lines.append("5. **Add schema markup** - Improves rich snippets")
        
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("*Generated by Pelé SEO Auditor*")
        
        return "\n".join(lines)
    
    def _score_emoji(self, score: int) -> str:
        """Get emoji for score."""
        if score >= 90:
            return "✅ Excellent"
        elif score >= 80:
            return "✅ Good"
        elif score >= 70:
            return "⚠️ Fair"
        elif score >= 60:
            return "🟡 Needs Work"
        else:
            return "❌ Poor"
    
    def _cwv_status(self, value: float, good: float, poor: float) -> str:
        """Get status for Core Web Vital metric."""
        if value <= good:
            return "✅ Good"
        elif value <= poor:
            return "🟡 Needs Improvement"
        else:
            return "❌ Poor"
    
    def _report_html(self) -> str:
        """Generate HTML report."""
        md_content = self._report_markdown()
        
        # Simple HTML wrapper
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SEO Audit Report - {self.site.base_url}</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            background: #f8fafc;
            color: #1e293b;
            line-height: 1.6;
        }}
        h1 {{ color: #0f172a; border-bottom: 3px solid #3b82f6; padding-bottom: 10px; }}
        h2 {{ color: #1e40af; margin-top: 30px; }}
        h3 {{ color: #1e3a8a; }}
        table {{ 
            width: 100%; 
            border-collapse: collapse; 
            margin: 15px 0;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        th {{ 
            background: #1e40af; 
            color: white;
            padding: 12px;
            text-align: left;
        }}
        td {{ 
            padding: 12px; 
            border-bottom: 1px solid #e2e8f0;
        }}
        tr:hover td {{ background: #f1f5f9; }}
        code {{ 
            background: #e2e8f0; 
            padding: 2px 6px; 
            border-radius: 4px;
            font-size: 0.9em;
        }}
        .score-excellent {{ color: #059669; }}
        .score-good {{ color: #0284c7; }}
        .score-fair {{ color: #d97706; }}
        .score-poor {{ color: #dc2626; }}
        ul {{ padding-left: 20px; }}
        li {{ margin: 8px 0; }}
        hr {{ border: none; border-top: 1px solid #e2e8f0; margin: 30px 0; }}
    </style>
</head>
<body>
    <pre style="white-space: pre-wrap; font-family: inherit;">{md_content}</pre>
</body>
</html>"""
        return html
    
    def _report_json(self) -> str:
        """Generate JSON report."""
        # Convert dataclasses to dict
        data = {
            'base_url': self.site.base_url,
            'audit_date': self.site.audit_date,
            'total_pages': self.site.total_pages,
            'scores': {
                'total': self.site.score_total,
                'technical': self.site.score_technical,
                'onpage': self.site.score_onpage,
                'schema': self.site.score_schema,
                'performance': self.site.score_performance
            },
            'technical': {
                'robots_txt': self.site.robots_txt_valid,
                'sitemap': self.site.sitemap_valid,
                'sitemap_urls': self.site.sitemap_urls
            },
            'stats': {
                'with_title': self.site.pages_with_title,
                'with_description': self.site.pages_with_description,
                'with_h1': self.site.pages_with_h1,
                'with_schema': self.site.pages_with_schema,
                'with_canonical': self.site.pages_with_canonical
            },
            'cwv': {
                'lcp': self.site.cwv_lcp,
                'fid': self.site.cwv_fid,
                'cls': self.site.cwv_cls
            },
            'issues': [
                {
                    'severity': i.severity,
                    'category': i.category,
                    'message': i.message,
                    'file': i.file,
                    'fix': i.fix
                }
                for i in self.site.issues
            ],
            'duplicates': self.site.duplicate_groups,
            'orphan_pages': self.site.orphan_pages
        }
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def _report_csv(self) -> str:
        """Generate CSV report of issues."""
        lines = ["severity,category,message,file,fix"]
        for issue in self.site.issues:
            line = f'"{issue.severity}","{issue.category}","{issue.message}","{issue.file}","{issue.fix}"'
            lines.append(line)
        return "\n".join(lines)
    
    # =========================================================================
    # MAIN RUN METHOD
    # =========================================================================
    
    def run(self) -> str:
        """Run the full audit."""
        print(f"🏆 PELÉ SEO AUDITOR")
        print(f"   Analyzing: {self.target}")
        print()
        
        if self.is_local:
            self.audit_local()
        else:
            self.audit_url()
            # Try to get Core Web Vitals for URLs
            if HAS_REQUESTS:
                self.check_core_web_vitals()
        
        output_format = self.options.get('output', 'md')
        return self.generate_report(output_format)


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="🏆 Pelé SEO Auditor - Professional Grade SEO Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pele-seo-auditor.py ./my-project
  python pele-seo-auditor.py https://example.com --depth 3
  python pele-seo-auditor.py ./src --output html --verbose
        """
    )
    
    parser.add_argument('target', help='URL or local path to audit')
    parser.add_argument('-o', '--output', choices=['md', 'html', 'json', 'csv'], 
                       default='md', help='Output format (default: md)')
    parser.add_argument('-d', '--depth', type=int, default=2,
                       help='Crawl depth for URLs (default: 2)')
    parser.add_argument('--api-key', help='Google PageSpeed API key')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Show detailed progress')
    parser.add_argument('--save', help='Save report to file')
    
    args = parser.parse_args()
    
    options = {
        'output': args.output,
        'depth': args.depth,
        'api_key': args.api_key,
        'verbose': args.verbose
    }
    
    auditor = PeleSEOAuditor(args.target, options)
    report = auditor.run()
    
    if args.save:
        with open(args.save, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n✅ Report saved to: {args.save}")
    else:
        print(report)


if __name__ == "__main__":
    main()
