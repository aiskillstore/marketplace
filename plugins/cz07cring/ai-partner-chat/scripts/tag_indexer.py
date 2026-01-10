"""
Tag Indexer - Manage tag index for fast lookups

Maintains a separate index for tags to enable:
- Fast tag-based queries
- Tag statistics and analytics
- Tag suggestions

Version: 2.0
"""

import json
from pathlib import Path
from typing import List, Dict, Set
from collections import defaultdict, Counter
from datetime import datetime


class TagIndexer:
    """Manage tag index for efficient tag-based operations."""

    def __init__(self, index_dir: str = "./indexes"):
        """
        Initialize tag indexer.

        Args:
            index_dir: Path to index directory
        """
        index_path = Path(index_dir) / "tags_index.json"
        self.index_path = Path(index_path)
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.index = self._load_index()

    def _load_index(self) -> Dict:
        """Load tag index from file."""
        if self.index_path.exists():
            with open(self.index_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {
                'tags': {},  # tag -> {count, files, last_used}
                'files': {},  # filepath -> [tags]
                'last_updated': None
            }

    def _save_index(self):
        """Save tag index to file."""
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.index['last_updated'] = datetime.now().isoformat()

        with open(self.index_path, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, ensure_ascii=False, indent=2)

    def add_tags(self, filepath: str, tags: List[str]):
        """
        Add tags for a file.

        Args:
            filepath: Path to the file
            tags: List of tags to add
        """
        # Update file -> tags mapping
        self.index['files'][filepath] = tags

        # Update tag -> files mapping
        for tag in tags:
            if tag not in self.index['tags']:
                self.index['tags'][tag] = {
                    'count': 0,
                    'files': [],
                    'last_used': None
                }

            tag_info = self.index['tags'][tag]

            # Add file if not already there
            if filepath not in tag_info['files']:
                tag_info['files'].append(filepath)

            tag_info['count'] = len(tag_info['files'])
            tag_info['last_used'] = datetime.now().isoformat()

        self._save_index()

    def remove_file(self, filepath: str):
        """
        Remove a file and its tags from the index.

        Args:
            filepath: Path to the file to remove
        """
        if filepath not in self.index['files']:
            return

        # Get tags for this file
        tags = self.index['files'][filepath]

        # Remove file from each tag
        for tag in tags:
            if tag in self.index['tags']:
                tag_info = self.index['tags'][tag]
                if filepath in tag_info['files']:
                    tag_info['files'].remove(filepath)
                tag_info['count'] = len(tag_info['files'])

                # Remove tag if no files use it
                if tag_info['count'] == 0:
                    del self.index['tags'][tag]

        # Remove file entry
        del self.index['files'][filepath]

        self._save_index()

    def get_files_by_tag(self, tag: str) -> List[str]:
        """
        Get all files with a specific tag.

        Args:
            tag: Tag to search for

        Returns:
            List of file paths
        """
        if tag in self.index['tags']:
            return self.index['tags'][tag]['files'].copy()
        return []

    def get_files_by_tags(
        self,
        tags: List[str],
        match_all: bool = False
    ) -> List[str]:
        """
        Get files matching tags.

        Args:
            tags: List of tags to search for
            match_all: If True, files must have ALL tags. If False, ANY tag.

        Returns:
            List of matching file paths
        """
        if not tags:
            return []

        if match_all:
            # Files must have ALL tags
            file_sets = [set(self.get_files_by_tag(tag)) for tag in tags]
            if file_sets:
                return list(set.intersection(*file_sets))
            return []
        else:
            # Files with ANY tag
            files = set()
            for tag in tags:
                files.update(self.get_files_by_tag(tag))
            return list(files)

    def get_tags_for_file(self, filepath: str) -> List[str]:
        """
        Get all tags for a file.

        Args:
            filepath: Path to the file

        Returns:
            List of tags
        """
        return self.index['files'].get(filepath, []).copy()

    def get_tag_statistics(self) -> Dict:
        """
        Get statistics about tags.

        Returns:
            Dictionary with tag statistics
        """
        total_tags = len(self.index['tags'])
        total_files = len(self.index['files'])

        # Top tags by count
        tag_counts = {
            tag: info['count']
            for tag, info in self.index['tags'].items()
        }

        top_tags = sorted(
            tag_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:20]

        return {
            'total_tags': total_tags,
            'total_files': total_files,
            'top_tags': top_tags,
            'last_updated': self.index.get('last_updated')
        }

    def get_related_tags(self, tag: str, top_k: int = 5) -> List[str]:
        """
        Get tags that often appear together with the given tag.

        Args:
            tag: Tag to find related tags for
            top_k: Number of related tags to return

        Returns:
            List of related tags
        """
        if tag not in self.index['tags']:
            return []

        # Get files with this tag
        files = set(self.get_files_by_tag(tag))

        # Count co-occurring tags
        co_occurrence = Counter()

        for filepath in files:
            file_tags = self.get_tags_for_file(filepath)
            for other_tag in file_tags:
                if other_tag != tag:
                    co_occurrence[other_tag] += 1

        # Return top related tags
        return [tag for tag, count in co_occurrence.most_common(top_k)]

    def suggest_tags(self, content: str, existing_tags: List[str] = None) -> List[str]:
        """
        Suggest tags based on content and existing tags.

        Args:
            content: Content to analyze
            existing_tags: Tags already assigned

        Returns:
            List of suggested tags
        """
        existing_tags = existing_tags or []
        suggestions = set()

        # Get related tags for existing tags
        for tag in existing_tags:
            related = self.get_related_tags(tag, top_k=3)
            suggestions.update(related)

        # Remove already assigned tags
        suggestions = suggestions - set(existing_tags)

        return list(suggestions)[:5]

    def cleanup_unused_tags(self, min_count: int = 1):
        """
        Remove tags with usage count below threshold.

        Args:
            min_count: Minimum count to keep a tag
        """
        tags_to_remove = []

        for tag, info in self.index['tags'].items():
            if info['count'] < min_count:
                tags_to_remove.append(tag)

        for tag in tags_to_remove:
            del self.index['tags'][tag]

        self._save_index()

        return len(tags_to_remove)


# Convenience functions

def add_tags_to_index(filepath: str, tags: List[str], index_path: str = "./indexes/tags_index.json"):
    """
    Add tags for a file to the index.

    Args:
        filepath: File path
        tags: Tags to add
        index_path: Path to index file
    """
    indexer = TagIndexer(index_path)
    indexer.add_tags(filepath, tags)


def get_tag_stats(index_path: str = "./indexes/tags_index.json") -> Dict:
    """
    Get tag statistics.

    Args:
        index_path: Path to index file

    Returns:
        Statistics dictionary
    """
    indexer = TagIndexer(index_path)
    return indexer.get_tag_statistics()
