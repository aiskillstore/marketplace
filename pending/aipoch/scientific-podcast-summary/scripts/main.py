#!/usr/bin/env python3
"""Scientific Podcast Summary - Automatically summarize science podcast content
Support: Huberman Lab, Nature Podcast"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from typing import Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


# ==================== Configuration ====================

DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

PODCAST_SOURCES = {
    "huberman": {
        "name": "Huberman Lab",
        "base_url": "https://hubermanlab.com",
        "latest_url": "https://hubermanlab.com/category/podcast-episodes/",
    },
    "nature": {
        "name": "Nature Podcast",
        "base_url": "https://www.nature.com",
        "latest_url": "https://www.nature.com/nature/articles?type=podcast",
    },
}

SUMMARY_PROMPT = """You are a professional science podcast content summary assistant. Please provide a structured summary of the following podcast content.

Requirements:
1. Extract core scientific themes and key findings
2. Use concise and clear language
3. Keep important technical terms and explain them appropriately
4. Highlight practical suggestions or action guides

Please return in JSON format:
{
    "title": "Podcast title",
    "publish_date": "Publish date",
    "host": "host",
    "guests": ["guests 1", "guests 2"],
    "summary": "Summary of core themes (200-300 words)",
    "key_points": ["Key points 1", "Key points 2", "Key points 3"],
    "actionable_tips": ["Suggestion 1", "Suggestion 2"],
    "resources": [{"title": "Resource name", "url": "Link"}]
}

Podcast content:
{content}"""


# ==================== Utils ====================

def log(msg: str, level: str = "info"):
    """Print log"""
    prefix = {"info": "ℹ️", "success": "✅", "error": "❌", "warn": "⚠️"}.get(level, "ℹ️")
    print(f"{prefix} {msg}", file=sys.stderr if level == "error" else sys.stdout)


def fetch_url(url: str, headers: Optional[dict] = None) -> Optional[str]:
    """Get URL content"""
    default_headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    if headers:
        default_headers.update(headers)
    
    try:
        resp = requests.get(url, headers=default_headers, timeout=30)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        log(f"getURLfail: {url} - {e}", "error")
        return None


def call_llm(prompt: str) -> Optional[str]:
    """Call LLM API"""
    if not OPENAI_API_KEY:
        log("OPENAI_API_KEY environment variable not set", "error")
        return None
    
    try:
        import openai
        client = openai.OpenAI(
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_BASE_URL,
        )
        
        resp = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are a professional scientific content summary assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )
        return resp.choices[0].message.content
    except Exception as e:
        log(f"LLM APIEnglish: {e}", "error")
        return None


# ==================== Podcast Parsers ====================

def parse_huberman_episode(html: str, url: str) -> dict:
    """Parsing the Huberman Lab page"""
    soup = BeautifulSoup(html, "html.parser")
    
    # Extract title
    title_elem = soup.find("h1", class_=re.compile("entry-title|post-title"))
    title = title_elem.get_text(strip=True) if title_elem else "Unknown"
    
    # Extract release date
    date_elem = soup.find("time", class_="entry-date")
    publish_date = date_elem.get("datetime", "") if date_elem else ""
    
    # Extract content
    content_elem = soup.find("div", class_=re.compile("entry-content|post-content"))
    content = ""
    if content_elem:
        # Remove scripts and styles
        for script in content_elem(["script", "style"]):
            script.decompose()
        content = content_elem.get_text(separator="\n", strip=True)
    
    # Extract guest information (usually in the title or content)
    guests = []
    guest_match = re.search(r"Dr\.\s+([A-Z][a-z]+\s+[A-Z][a-z]+)", title)
    if guest_match:
        guests.append(guest_match.group(0))
    
    return {
        "title": title,
        "publish_date": publish_date,
        "host": "Andrew Huberman",
        "guests": guests,
        "content": content[:15000],  # Limit length
        "source_url": url,
    }


def parse_nature_podcast(html: str, url: str) -> dict:
    """Parsing the Nature Podcast page"""
    soup = BeautifulSoup(html, "html.parser")
    
    # Extract title
    title_elem = soup.find("h1") or soup.find("h2", class_=re.compile("title"))
    title = title_elem.get_text(strip=True) if title_elem else "Unknown"
    
    # Extract release date
    date_elem = soup.find("time") or soup.find("span", class_=re.compile("date"))
    publish_date = date_elem.get_text(strip=True) if date_elem else ""
    
    # Extract content
    content_elem = soup.find("div", class_=re.compile("article-body|content"))
    content = ""
    if content_elem:
        for script in content_elem(["script", "style"]):
            script.decompose()
        content = content_elem.get_text(separator="\n", strip=True)
    
    return {
        "title": title,
        "publish_date": publish_date,
        "host": "Nature Podcast",
        "guests": [],
        "content": content[:15000],
        "source_url": url,
    }


def parse_generic_page(html: str, url: str) -> dict:
    """General page parsing"""
    soup = BeautifulSoup(html, "html.parser")
    
    # Try to extract the title
    title = "Unknown"
    for selector in ["h1", "h2", "title"]:
        elem = soup.find(selector)
        if elem:
            title = elem.get_text(strip=True)
            break
    
    # Extract text content
    content = ""
    for selector in ["article", "main", ".content", "#content", ".post"]:
        elem = soup.find(selector)
        if elem:
            content = elem.get_text(separator="\n", strip=True)
            break
    
    if not content:
        # Go back to extract all paragraphs
        paragraphs = soup.find_all("p")
        content = "\n\n".join(p.get_text(strip=True) for p in paragraphs[:20])
    
    return {
        "title": title,
        "publish_date": "",
        "host": "",
        "guests": [],
        "content": content[:15000],
        "source_url": url,
    }


# ==================== Feed Discovery ====================

def get_latest_huberman_url() -> Optional[str]:
    """Get the latest Huberman Lab episode URL"""
    html = fetch_url(PODCAST_SOURCES["huberman"]["latest_url"])
    if not html:
        return None
    
    soup = BeautifulSoup(html, "html.parser")
    
    # Find links to latest episodes
    link = soup.find("a", href=re.compile(r"/\d{4}/\d{2}/\d{2}/"))
    if link:
        return link.get("href")
    
    # Alternatives
    for article in soup.find_all("article"):
        link = article.find("a", href=True)
        if link:
            href = link.get("href")
            if "/" in href:
                return urljoin(PODCAST_SOURCES["huberman"]["base_url"], href)
    
    return None


def get_latest_nature_url() -> Optional[str]:
    """Get the latest Nature Podcast episode URL"""
    html = fetch_url(PODCAST_SOURCES["nature"]["latest_url"])
    if not html:
        return None
    
    soup = BeautifulSoup(html, "html.parser")
    
    # Find the latest podcast link
    for link in soup.find_all("a", href=True):
        href = link.get("href", "")
        if "/nature/articles/" in href:
            return urljoin(PODCAST_SOURCES["nature"]["base_url"], href)
    
    return None


# ==================== Summary Generation ====================

def generate_summary(episode_data: dict) -> dict:
    """Using LLM to generate summaries"""
    prompt = SUMMARY_PROMPT.format(content=episode_data["content"])
    
    response = call_llm(prompt)
    if not response:
        log("LLM generation failed, using base extraction", "warn")
        return fallback_summary(episode_data)
    
    # Parse JSON response
    try:
        # Try to extract JSON chunks
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            summary_data = json.loads(json_match.group())
            summary_data["source_url"] = episode_data.get("source_url", "")
            return summary_data
    except json.JSONDecodeError:
        pass
    
    # If JSON parsing fails, use the original response
    return {
        "title": episode_data.get("title", "Unknown"),
        "publish_date": episode_data.get("publish_date", ""),
        "host": episode_data.get("host", ""),
        "guests": episode_data.get("guests", []),
        "summary": response[:500],
        "key_points": [],
        "actionable_tips": [],
        "resources": [{"title": "Original link", "url": episode_data.get("source_url", "")}],
        "source_url": episode_data.get("source_url", ""),
    }


def fallback_summary(episode_data: dict) -> dict:
    """Base extraction when LLM fails"""
    content = episode_data.get("content", "")
    
    # Simply extract the first few paragraphs as key takeaways
    paragraphs = [p.strip() for p in content.split("\n\n") if len(p.strip()) > 50][:5]
    
    return {
        "title": episode_data.get("title", "Unknown"),
        "publish_date": episode_data.get("publish_date", ""),
        "host": episode_data.get("host", ""),
        "guests": episode_data.get("guests", []),
        "summary": paragraphs[0] if paragraphs else "",
        "key_points": paragraphs[1:4] if len(paragraphs) > 1 else [],
        "actionable_tips": [],
        "resources": [{"title": "Original link", "url": episode_data.get("source_url", "")}],
        "source_url": episode_data.get("source_url", ""),
    }


# ==================== Output Formatters ====================

def format_markdown(summary: dict) -> str:
    """Formatted as Markdown"""
    lines = [
        f"# 🎙️ {summary['title']}",
        "",
        f"**Release time:** {summary.get('publish_date', 'N/A')}",
        f"**host:** {summary.get('host', 'N/A')}",
    ]
    
    if summary.get('guests'):
        lines.append(f"**Guest:** {', '.join(summary['guests'])}")
    
    lines.extend(["", "---", ""])
    
    # core themes
    lines.extend(["## 📝 Core Theme", ""])
    lines.append(summary.get('summary', 'No overview yet'))
    lines.append("")
    
    # Key takeaways
    if summary.get('key_points'):
        lines.extend(["## 🔬 Key Points", ""])
        for i, point in enumerate(summary['key_points'], 1):
            lines.append(f"{i}. {point}")
        lines.append("")
    
    # Practical advice
    if summary.get('actionable_tips'):
        lines.extend(["## 💡 Practical Advice", ""])
        for tip in summary['actionable_tips']:
            lines.append(f"- {tip}")
        lines.append("")
    
    # Resource links
    if summary.get('resources'):
        lines.extend(["## 📚 Related resources", ""])
        for res in summary['resources']:
            title = res.get('title', 'Link')
            url = res.get('url', '#')
            lines.append(f"- [{title}]({url})")
        lines.append("")
    
    lines.extend(["---", f"\n*Generation time: {datetime.now().strftime('%Y-%m-%d %H:%M')}*"])
    
    return "\n".join(lines)


def format_json(summary: dict) -> str:
    """Format to JSON"""
    summary["generated_at"] = datetime.now().isoformat()
    return json.dumps(summary, ensure_ascii=False, indent=2)


# ==================== Main ====================

def main():
    parser = argparse.ArgumentParser(
        description="Automatically summarize science podcast content (Huberman Lab / Nature Podcast)"
    )
    parser.add_argument(
        "--podcast",
        choices=["huberman", "nature"],
        default="huberman",
        help="Select podcast source (default: huberman)",
    )
    parser.add_argument(
        "--url",
        help="Provide the podcast page URL directly",
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path",
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format (default: markdown)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed log",
    )
    
    args = parser.parse_args()
    
    # Get target URL
    target_url = args.url
    if not target_url:
        log(f"Getting latest {PODCAST_SOURCES[args.podcast]['name']} English...")
        if args.podcast == "huberman":
            target_url = get_latest_huberman_url()
        else:
            target_url = get_latest_nature_url()
    
    if not target_url:
        log("Unable to get podcast URL", "error")
        sys.exit(1)
    
    log(f"parse page: {target_url}")
    
    # Get page content
    html = fetch_url(target_url)
    if not html:
        sys.exit(1)
    
    # parse content
    if args.podcast == "huberman":
        episode_data = parse_huberman_episode(html, target_url)
    elif args.podcast == "nature":
        episode_data = parse_nature_podcast(html, target_url)
    else:
        episode_data = parse_generic_page(html, target_url)
    
    if not episode_data.get("content"):
        log("Unable to extract page content", "error")
        sys.exit(1)
    
    log(f"Extract content length: {len(episode_data['content'])} character")
    
    # Generate summary
    log("Generating AI summary...")
    summary = generate_summary(episode_data)
    
    # Formatted output
    if args.format == "json":
        output = format_json(summary)
    else:
        output = format_markdown(summary)
    
    # Output results
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        log(f"saved to: {args.output}", "success")
    else:
        print(output)


if __name__ == "__main__":
    main()
