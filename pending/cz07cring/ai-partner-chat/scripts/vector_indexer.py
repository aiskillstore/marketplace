"""
Vector database utilities for indexing chunks - Version 2.0

This module provides core functionality to:
1. Accept chunks conforming to chunk_schema (v2.0 with rich metadata)
2. Generate embeddings using bge-m3
3. Store in ChromaDB with support for append mode
4. Handle multiple chunk types (notes, conversations, code)

Chunking logic is handled by Claude Code directly, not by pre-written scripts.
"""

import chromadb
import json
import os
from datetime import datetime
from pathlib import Path
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional


class VectorIndexer:
    """Handle vector database indexing operations."""

    def __init__(self, db_path: str = "./vector_db", model_name: str = "BAAI/bge-m3"):
        """
        Initialize indexer.

        Args:
            db_path: Path to ChromaDB database
            model_name: Sentence transformer model name
        """
        self.db_path = db_path
        self.model_name = model_name
        self.model = None
        self.client = None
        self.collection = None

    def _check_model_cached(self) -> bool:
        """检查模型是否已缓存到本地（兼容 macOS/Linux/Windows）"""
        # sentence-transformers 默认缓存路径
        # macOS/Linux: ~/.cache/huggingface/hub/
        # Windows: %USERPROFILE%/.cache/huggingface/hub/ 或 %LOCALAPPDATA%/huggingface/hub/

        cache_dirs = []

        # 标准缓存路径（macOS/Linux）
        cache_dirs.append(Path.home() / '.cache' / 'huggingface' / 'hub')

        # Windows 可能的路径
        if os.name == 'nt':  # Windows
            # Windows 备用路径 1: %LOCALAPPDATA%\huggingface\hub
            if 'LOCALAPPDATA' in os.environ:
                cache_dirs.append(Path(os.environ['LOCALAPPDATA']) / 'huggingface' / 'hub')
            # Windows 备用路径 2: %USERPROFILE%\.cache\huggingface\hub
            cache_dirs.append(Path.home() / '.cache' / 'huggingface' / 'hub')

        # BAAI/bge-m3 的缓存目录格式（大小写变体）
        model_names = ['models--BAAI--bge-m3', 'models--baai--bge-m3']

        # 检查所有可能的路径
        for cache_dir in cache_dirs:
            for model_name in model_names:
                model_path = cache_dir / model_name
                if model_path.exists():
                    return True

        return False

    def _ensure_initialized(self):
        """Lazy initialization of model and database connection."""
        if self.model is None:
            # 检查模型是否已缓存
            is_cached = self._check_model_cached()

            if is_cached:
                print(f"🤖 Loading embedding model ({self.model_name}) from cache...")
            else:
                # 根据操作系统显示不同的缓存路径
                if os.name == 'nt':  # Windows
                    cache_path = "%USERPROFILE%\\.cache\\huggingface\\hub\\"
                else:  # macOS/Linux
                    cache_path = "~/.cache/huggingface/hub/"

                print(f"🤖 Downloading embedding model ({self.model_name})...")
                print(f"   ⚠️  首次下载约 4.3GB，请耐心等待...")
                print(f"   📍 模型会缓存到 {cache_path}")

            # 注意: 使用 transformers<4.50 来避免 torch 2.6 依赖问题
            # transformers 4.50+ 强制要求 torch 2.6 (CVE-2025-32434),
            # 但 torch 2.6 在 macOS 上尚未发布
            self.model = SentenceTransformer(
                self.model_name,
                trust_remote_code=True,
                device='cpu'
            )

            if not is_cached:
                print(f"   ✅ 模型下载完成，已缓存到本地")
                print(f"   💡 下次使用将直接从缓存加载，速度很快")

        if self.client is None:
            print(f"💾 Connecting to vector database at: {self.db_path}")
            self.client = chromadb.PersistentClient(path=self.db_path)

    def initialize_db(self, force_recreate: bool = False):
        """
        Initialize or recreate vector database.

        Args:
            force_recreate: If True, delete and recreate collection
        """
        self._ensure_initialized()

        collection_name = "ai_partner_chunks"  # 更具描述性的名字

        if force_recreate:
            # Delete existing collection
            try:
                self.client.delete_collection(collection_name)
                print("   Deleted existing collection")
            except:
                pass

        # Try to get existing collection, or create new one
        try:
            self.collection = self.client.get_collection(collection_name)
            print(f"   Connected to existing collection: {self.collection.count()} chunks")
        except:
            # Create new collection
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            print("   Created new collection")

    def get_or_create_collection(self):
        """Get existing collection or create if not exists."""
        if self.collection is None:
            self.initialize_db(force_recreate=False)

    def _prepare_metadata(self, metadata: Dict) -> Dict:
        """
        Prepare metadata for ChromaDB (convert complex types to strings).

        Args:
            metadata: Raw metadata dictionary

        Returns:
            Cleaned metadata dictionary suitable for ChromaDB
        """
        clean_metadata = {}
        for key, value in metadata.items():
            if value is None:
                clean_metadata[key] = ""
            elif isinstance(value, (dict, list)):
                # Convert complex types to JSON strings
                clean_metadata[key] = json.dumps(value, ensure_ascii=False)
            else:
                clean_metadata[key] = str(value)
        return clean_metadata

    def index_chunks(self, chunks: List[Dict], start_id: int = 0) -> None:
        """
        Index chunks into vector database (rebuilds from scratch).

        Args:
            chunks: List of chunks conforming to chunk_schema.Chunk format
            start_id: Starting ID for chunks (default 0)
        """
        if not self.collection:
            raise RuntimeError("Database not initialized. Call initialize_db() first")

        print(f"🔄 Indexing {len(chunks)} chunks...")

        for i, chunk in enumerate(chunks):
            try:
                # Validate chunk has required fields
                if 'content' not in chunk or 'metadata' not in chunk:
                    print(f"  ⚠️  Skipping chunk {i}: missing content or metadata")
                    continue

                # Generate embedding
                embedding = self.model.encode(chunk['content']).tolist()

                # Prepare metadata
                metadata = self._prepare_metadata(chunk['metadata'])

                # Add to collection
                self.collection.add(
                    ids=[f"chunk_{start_id + i}"],
                    embeddings=[embedding],
                    documents=[chunk['content']],
                    metadatas=[metadata]
                )

                # Progress indicator
                if (i + 1) % 10 == 0:
                    print(f"  ✓ Indexed {i + 1}/{len(chunks)} chunks")

            except Exception as e:
                print(f"  ✗ Failed to index chunk {i}: {e}")

        print(f"\n✅ Successfully indexed {len(chunks)} chunks")
        print(f"   Database location: {os.path.abspath(self.db_path)}")

    def append_chunks(self, chunks: List[Dict]) -> int:
        """
        Append new chunks to existing vector database (不重建整个库).

        This is the key method for incremental updates!

        Args:
            chunks: List of chunks to append

        Returns:
            Number of successfully indexed chunks
        """
        self.get_or_create_collection()

        # Get current count to generate unique IDs
        current_count = self.collection.count()
        print(f"📝 Appending {len(chunks)} chunks to existing {current_count} chunks...")

        successfully_indexed = 0

        for i, chunk in enumerate(chunks):
            try:
                # Validate chunk
                if 'content' not in chunk or 'metadata' not in chunk:
                    print(f"  ⚠️  Skipping chunk {i}: missing content or metadata")
                    continue

                # Generate embedding
                self._ensure_initialized()
                embedding = self.model.encode(chunk['content']).tolist()

                # Prepare metadata
                metadata = self._prepare_metadata(chunk['metadata'])

                # Generate unique ID
                chunk_id = f"chunk_{current_count + successfully_indexed}_{datetime.now().timestamp()}"

                # Add to collection
                self.collection.add(
                    ids=[chunk_id],
                    embeddings=[embedding],
                    documents=[chunk['content']],
                    metadatas=[metadata]
                )

                successfully_indexed += 1

                # Progress indicator
                if successfully_indexed % 5 == 0:
                    print(f"  ✓ Appended {successfully_indexed}/{len(chunks)} chunks")

            except Exception as e:
                print(f"  ✗ Failed to append chunk {i}: {e}")

        print(f"\n✅ Successfully appended {successfully_indexed} chunks")
        print(f"   Total chunks in database: {self.collection.count()}")

        return successfully_indexed

    def get_stats(self) -> Dict:
        """
        Get statistics about the vector database.

        Returns:
            Dictionary with database statistics
        """
        self.get_or_create_collection()

        total_chunks = self.collection.count()

        # Query all chunks to analyze
        if total_chunks > 0:
            results = self.collection.get()
            metadatas = results['metadatas']

            # Count by chunk type
            chunk_types = {}
            for meta in metadatas:
                chunk_type = meta.get('chunk_type', 'unknown')
                chunk_types[chunk_type] = chunk_types.get(chunk_type, 0) + 1

            return {
                'total_chunks': total_chunks,
                'chunk_types': chunk_types,
                'database_path': os.path.abspath(self.db_path)
            }
        else:
            return {
                'total_chunks': 0,
                'chunk_types': {},
                'database_path': os.path.abspath(self.db_path)
            }


def index_chunks_to_db(chunks: List[Dict], db_path: str = "./vector_db") -> None:
    """
    Convenience function to index chunks.

    Args:
        chunks: List of chunks conforming to chunk_schema.Chunk
        db_path: Path to vector database
    """
    indexer = VectorIndexer(db_path=db_path)
    indexer.initialize_db()
    indexer.index_chunks(chunks)
