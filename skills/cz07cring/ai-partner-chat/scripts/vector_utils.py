"""
Vector database utilities for AI Partner Chat 2.0 - Multi-source retrieval

This module provides advanced query capabilities for the vector database:
1. Multi-source retrieval (notes, conversations, code)
2. Filtering by metadata (tags, chunk_type, importance, etc.)
3. Result merging and ranking
4. Support for complex queries

Version: 2.0
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Any
import chromadb
from sentence_transformers import SentenceTransformer


class MultiSourceRetriever:
    """
    Advanced retriever with multi-source and filtering capabilities.

    Supports:
    - Retrieve by chunk type (notes, conversations, code)
    - Filter by tags
    - Filter by importance
    - Filter by date range
    - Complex multi-condition queries
    """

    def __init__(self, db_path: str = "./vector_db"):
        """
        Initialize the retriever.

        Args:
            db_path: Path to ChromaDB database
        """
        self.db_path = db_path
        self.model = None
        self.client = None
        self.collection = None

    def _ensure_initialized(self):
        """Lazy initialization of model and database connection."""
        if self.model is None:
            print("🤖 Loading embedding model...")
            self.model = SentenceTransformer('BAAI/bge-m3')

        if self.client is None:
            try:
                self.client = chromadb.PersistentClient(path=self.db_path)
                self.collection = self.client.get_collection("ai_partner_chunks")
            except Exception as e:
                raise RuntimeError(
                    f"Failed to connect to database at {self.db_path}. "
                    f"Error: {e}"
                )

    def _parse_metadata(self, metadata: Dict[str, str]) -> Dict[str, Any]:
        """
        Parse metadata from ChromaDB (convert JSON strings back to objects).

        Args:
            metadata: Raw metadata from ChromaDB (all strings)

        Returns:
            Parsed metadata with proper types
        """
        parsed = {}
        for key, value in metadata.items():
            if value == "":
                parsed[key] = None
            elif key in ['tags', 'tag_layers', 'emotion', 'parameters', 'dependencies', 'participants']:
                # These fields were stored as JSON strings
                try:
                    parsed[key] = json.loads(value)
                except:
                    parsed[key] = value
            elif key in ['chunk_id', 'importance', 'thinking_level']:
                # Convert to int
                try:
                    parsed[key] = int(value)
                except:
                    parsed[key] = value
            elif key == 'quality_score':
                # Convert to float
                try:
                    parsed[key] = float(value)
                except:
                    parsed[key] = value
            else:
                parsed[key] = value
        return parsed

    def query(
        self,
        query: str,
        top_k: int = 5,
        chunk_types: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        min_importance: Optional[int] = None,
        language: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Advanced query with multiple filtering options.

        Args:
            query: Query text
            top_k: Number of results to return
            chunk_types: Filter by chunk types (e.g., ['note', 'conversation'])
            tags: Filter by tags (results must have ANY of these tags)
            min_importance: Minimum importance score (for conversations)
            language: Filter by programming language (for code chunks)
            **kwargs: Additional filter conditions

        Returns:
            List of results with content and metadata
        """
        self._ensure_initialized()

        # Generate query embedding
        query_embedding = self.model.encode(query).tolist()

        # Build where filter
        where_conditions = {}

        if chunk_types:
            # ChromaDB doesn't support OR for same field, so we'll filter after
            pass

        if language:
            where_conditions['language'] = language

        # Query with larger top_k to allow for filtering
        fetch_k = top_k * 3 if (chunk_types or tags or min_importance) else top_k

        # Query collection
        if where_conditions:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=fetch_k,
                where=where_conditions
            )
        else:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=fetch_k
            )

        # Process and filter results
        processed_results = []
        if results['documents'] and results['documents'][0]:
            for i in range(len(results['documents'][0])):
                metadata = self._parse_metadata(results['metadatas'][0][i])

                # Apply filters
                if chunk_types and metadata.get('chunk_type') not in chunk_types:
                    continue

                if min_importance and metadata.get('importance', 0) < min_importance:
                    continue

                if tags:
                    chunk_tags = metadata.get('tags', [])
                    if not isinstance(chunk_tags, list):
                        continue
                    if not any(tag in chunk_tags for tag in tags):
                        continue

                processed_results.append({
                    'content': results['documents'][0][i],
                    'metadata': metadata,
                    'distance': results['distances'][0][i] if results.get('distances') else None
                })

                if len(processed_results) >= top_k:
                    break

        return processed_results

    def search_notes(self, query: str, top_k: int = 5, tags: Optional[List[str]] = None) -> List[Dict]:
        """
        Search for notes only.

        Args:
            query: Query text
            top_k: Number of results
            tags: Optional tag filter

        Returns:
            List of note results
        """
        return self.query(query, top_k=top_k, chunk_types=['note'], tags=tags)

    def search_conversations(
        self,
        query: str,
        top_k: int = 5,
        min_importance: int = 3
    ) -> List[Dict]:
        """
        Search for conversation history.

        Args:
            query: Query text
            top_k: Number of results
            min_importance: Minimum importance score (default 3 - only important conversations)

        Returns:
            List of conversation results
        """
        return self.query(
            query,
            top_k=top_k,
            chunk_types=['conversation'],
            min_importance=min_importance
        )

    def search_code(
        self,
        query: str,
        top_k: int = 5,
        language: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Search for code snippets.

        Args:
            query: Query text (can describe functionality)
            top_k: Number of results
            language: Filter by programming language
            tags: Optional tag filter

        Returns:
            List of code results
        """
        return self.query(
            query,
            top_k=top_k,
            chunk_types=['code'],
            language=language,
            tags=tags
        )

    def search_all(
        self,
        query: str,
        notes_k: int = 3,
        conversations_k: int = 2,
        code_k: int = 2
    ) -> Dict[str, List[Dict]]:
        """
        Search across all sources in parallel.

        Args:
            query: Query text
            notes_k: Number of notes to retrieve
            conversations_k: Number of conversations to retrieve
            code_k: Number of code snippets to retrieve

        Returns:
            Dictionary with separate results for each type:
            {
                'notes': [...],
                'conversations': [...],
                'code': [...]
            }
        """
        return {
            'notes': self.search_notes(query, top_k=notes_k),
            'conversations': self.search_conversations(query, top_k=conversations_k),
            'code': self.search_code(query, top_k=code_k)
        }

    def get_by_tags(self, tags: List[str], top_k: int = 10) -> List[Dict]:
        """
        Get all chunks with specific tags (no semantic search).

        Args:
            tags: List of tags to filter by
            top_k: Maximum number of results

        Returns:
            List of chunks with any of the specified tags
        """
        self._ensure_initialized()

        # Get all chunks (we'll filter by tags)
        # Note: This is not optimal for large databases
        # Better approach would be to maintain a separate tag index
        results = self.collection.get()

        matching_chunks = []
        for i, metadata in enumerate(results['metadatas']):
            parsed_meta = self._parse_metadata(metadata)
            chunk_tags = parsed_meta.get('tags', [])

            if not isinstance(chunk_tags, list):
                continue

            if any(tag in chunk_tags for tag in tags):
                matching_chunks.append({
                    'content': results['documents'][i],
                    'metadata': parsed_meta
                })

                if len(matching_chunks) >= top_k:
                    break

        return matching_chunks

    def get_recent(
        self,
        days: int = 7,
        chunk_types: Optional[List[str]] = None,
        top_k: int = 10
    ) -> List[Dict]:
        """
        Get recent chunks by date.

        Args:
            days: Number of days to look back
            chunk_types: Filter by chunk types
            top_k: Maximum number of results

        Returns:
            List of recent chunks
        """
        from datetime import datetime, timedelta

        self._ensure_initialized()

        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

        # Get all chunks and filter by date
        results = self.collection.get()

        recent_chunks = []
        for i, metadata in enumerate(results['metadatas']):
            parsed_meta = self._parse_metadata(metadata)

            # Filter by chunk type
            if chunk_types and parsed_meta.get('chunk_type') not in chunk_types:
                continue

            # Filter by date
            chunk_date = parsed_meta.get('date', '')
            if chunk_date >= cutoff_date:
                recent_chunks.append({
                    'content': results['documents'][i],
                    'metadata': parsed_meta
                })

        # Sort by date descending
        recent_chunks.sort(key=lambda x: x['metadata'].get('date', ''), reverse=True)

        return recent_chunks[:top_k]


# Convenience functions for backward compatibility and ease of use

def get_relevant_notes(
    query: str,
    db_path: str = "./vector_db",
    top_k: int = 5,
    tags: Optional[List[str]] = None
) -> List[Dict]:
    """
    Convenience function to retrieve relevant notes.

    Args:
        query: Query text
        db_path: Path to vector database
        top_k: Number of results to return
        tags: Optional tag filter

    Returns:
        List of note results
    """
    retriever = MultiSourceRetriever(db_path)
    return retriever.search_notes(query, top_k=top_k, tags=tags)


def search_all_sources(
    query: str,
    db_path: str = "./vector_db",
    notes_k: int = 3,
    conversations_k: int = 2,
    code_k: int = 2
) -> Dict[str, List[Dict]]:
    """
    Search across all sources (notes, conversations, code).

    Args:
        query: Query text
        db_path: Path to vector database
        notes_k: Number of notes
        conversations_k: Number of conversations
        code_k: Number of code snippets

    Returns:
        Dictionary with results from all sources
    """
    retriever = MultiSourceRetriever(db_path)
    return retriever.search_all(query, notes_k, conversations_k, code_k)


def get_chunks_by_type(
    chunk_type: str,
    db_path: str = "./vector_db",
    limit: int = 10
) -> List[Dict]:
    """
    Get chunks of a specific type.

    Args:
        chunk_type: Type of chunks ('note', 'conversation', 'code', etc.)
        db_path: Path to vector database
        limit: Maximum number of results

    Returns:
        List of chunks of the specified type
    """
    retriever = MultiSourceRetriever(db_path)
    retriever._ensure_initialized()

    results = retriever.collection.get()

    chunks = []
    for i, metadata in enumerate(results['metadatas']):
        parsed_meta = retriever._parse_metadata(metadata)
        if parsed_meta.get('chunk_type') == chunk_type:
            chunks.append({
                'content': results['documents'][i],
                'metadata': parsed_meta
            })
            if len(chunks) >= limit:
                break

    return chunks
