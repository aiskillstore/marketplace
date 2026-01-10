"""
Tag Generator - AI-powered tag extraction

Automatically extracts and generates tags for notes, conversations, and code.
Uses LLM to analyze content and generate appropriate tags in 3 layers:
- Topic tags (main themes)
- Tech tags (technologies/frameworks)
- Custom tags (user-defined)

Version: 2.0
"""

import json
import re
from typing import List, Dict, Optional
from pathlib import Path


class TagGenerator:
    """Generate tags for content using AI analysis."""

    def __init__(self, taxonomy_path: str = "./config/tags_taxonomy.json"):
        """
        Initialize tag generator.

        Args:
            taxonomy_path: Path to tag taxonomy configuration
        """
        self.taxonomy_path = taxonomy_path
        self.taxonomy = self._load_taxonomy()

    def _load_taxonomy(self) -> Dict:
        """Load tag taxonomy from config file."""
        taxonomy_file = Path(self.taxonomy_path)

        if taxonomy_file.exists():
            with open(taxonomy_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Default taxonomy
            default_taxonomy = {
                "tech_tags": [
                    "python", "javascript", "typescript", "react", "vue", "node.js",
                    "django", "flask", "fastapi", "express",
                    "mongodb", "postgresql", "mysql", "redis",
                    "docker", "kubernetes", "git", "linux"
                ],
                "topic_tags": [
                    "performance", "optimization", "testing", "debugging",
                    "architecture", "design-patterns", "algorithms",
                    "security", "deployment", "monitoring"
                ],
                "domain_tags": [
                    "frontend", "backend", "fullstack", "devops",
                    "database", "networking", "system-design"
                ]
            }

            # Save default taxonomy
            taxonomy_file.parent.mkdir(parents=True, exist_ok=True)
            with open(taxonomy_file, 'w', encoding='utf-8') as f:
                json.dump(default_taxonomy, f, ensure_ascii=False, indent=2)

            return default_taxonomy

    def extract_tags_simple(self, content: str, max_tags: int = 5) -> List[str]:
        """
        Simple rule-based tag extraction (fallback method).

        Args:
            content: Text content to analyze
            max_tags: Maximum number of tags to return

        Returns:
            List of extracted tags
        """
        tags = []
        content_lower = content.lower()

        # Check against known tech tags
        for tag in self.taxonomy.get('tech_tags', []):
            if tag.lower() in content_lower:
                tags.append(tag)

        # Check against topic tags
        for tag in self.taxonomy.get('topic_tags', []):
            if tag.lower() in content_lower:
                tags.append(tag)

        return list(set(tags))[:max_tags]

    def generate_tag_layers(
        self,
        content: str,
        content_type: str = 'note'
    ) -> Dict[str, List[str]]:
        """
        Generate hierarchical tag layers.

        This method should use LLM in production, but here we provide
        a simple implementation that can be enhanced by Claude Code.

        Args:
            content: Content to analyze
            content_type: Type of content ('note', 'conversation', 'code')

        Returns:
            Dictionary with tag layers:
            {
                'topic': ['performance', 'optimization'],
                'tech': ['react', 'hooks'],
                'custom': []
            }
        """
        # Simple implementation - in production, this would call LLM
        all_tags = self.extract_tags_simple(content, max_tags=10)

        tech_tags = []
        topic_tags = []

        for tag in all_tags:
            if tag in self.taxonomy.get('tech_tags', []):
                tech_tags.append(tag)
            elif tag in self.taxonomy.get('topic_tags', []):
                topic_tags.append(tag)

        return {
            'topic': topic_tags[:3],
            'tech': tech_tags[:4],
            'custom': []
        }

    def normalize_tags(self, tags: List[str]) -> List[str]:
        """
        Normalize tags (lowercase, remove duplicates, handle aliases).

        Args:
            tags: Raw tag list

        Returns:
            Normalized tag list
        """
        # Lowercase and deduplicate
        normalized = list(set(tag.lower().strip() for tag in tags))

        # Handle common aliases
        aliases = {
            'js': 'javascript',
            'ts': 'typescript',
            'py': 'python',
            'node': 'node.js',
            'pg': 'postgresql',
            'mongo': 'mongodb'
        }

        result = []
        for tag in normalized:
            result.append(aliases.get(tag, tag))

        return list(set(result))


def extract_tags_from_content(
    content: str,
    content_type: str = 'note',
    max_tags: int = 5
) -> List[str]:
    """
    Convenience function to extract tags from content.

    Args:
        content: Content to analyze
        content_type: Type of content
        max_tags: Maximum tags to return

    Returns:
        List of tags
    """
    generator = TagGenerator()
    return generator.extract_tags_simple(content, max_tags)


def generate_tag_layers_for_content(
    content: str,
    content_type: str = 'note'
) -> Dict[str, List[str]]:
    """
    Generate hierarchical tags for content.

    Args:
        content: Content to analyze
        content_type: Type of content

    Returns:
        Tag layers dictionary
    """
    generator = TagGenerator()
    return generator.generate_tag_layers(content, content_type)


# LLM-based tag extraction prompt template (for Claude Code to use)
TAG_EXTRACTION_PROMPT = """
Analyze the following {content_type} and extract relevant tags.

Content:
```
{content}
```

Please provide tags in 3 categories:

1. **Topic Tags** (3-5 tags): Main themes or subjects discussed
   Examples: performance, debugging, architecture, testing

2. **Tech Tags** (3-5 tags): Technologies, frameworks, or tools mentioned
   Examples: react, python, docker, postgresql

3. **Custom Tags** (0-2 tags): Any special attributes
   Examples: important, needs-review, tutorial, reference

Return as JSON:
{{
  "topic": ["tag1", "tag2"],
  "tech": ["tag1", "tag2"],
  "custom": ["tag1"]
}}

Keep tags concise, lowercase, and use hyphens for multi-word tags.
"""
