"""
Chunk data format specification - Version 2.0

This module defines the unified format for all document chunks in AI Partner Chat 2.0.
Supports: Notes, Conversations, Code snippets, with rich metadata for all features.

All chunking strategies (whether rule-based or AI-generated) must
produce chunks conforming to this schema.
"""

from typing import TypedDict, Optional, Dict, List, Any


class EmotionData(TypedDict, total=False):
    """
    Emotion and cognitive state data.

    Fields:
        state: Cognitive state (exploration/confusion/breakthrough/consolidation/burnout)
        excitement: Excitement level 0-10
        confidence: Confidence level 0-10
        confusion: Confusion level 0-10
        fatigue: Fatigue level 0-10
    """
    state: str
    excitement: int
    confidence: int
    confusion: int
    fatigue: int


class TagLayers(TypedDict, total=False):
    """
    Hierarchical tag structure.

    Fields:
        topic: Topic tags (e.g., ['performance', 'optimization'])
        tech: Technology tags (e.g., ['react', 'hooks'])
        custom: User-defined tags (e.g., ['important', 'review'])
    """
    topic: List[str]
    tech: List[str]
    custom: List[str]


class ChunkMetadata(TypedDict, total=False):
    """
    Unified metadata for all chunk types - supports all AI Partner Chat 2.0 features.

    ============ REQUIRED FIELDS (all chunks) ============
    filename: Name of source file
    filepath: Full path to source file
    chunk_id: Sequential ID within the file (starting from 0)
    chunk_type: Type of chunk - 'note', 'conversation', 'code', 'summary'

    ============ BASIC FIELDS (original) ============
    date: Date associated with chunk (YYYY-MM-DD format)
    title: Section or entry title
    sub_chunk_id: ID for sub-chunks when further splitting is needed

    ============ TAG SYSTEM ============
    tags: List of tags ['react', 'hooks', 'performance']
    tag_layers: Hierarchical tag structure (TagLayers)

    ============ CONVERSATION MEMORY ============
    conversation_id: Unique conversation identifier
    importance: Importance score 1-5 (5=critical, 1=trivial)
    participants: List of participants ['user', 'ai']

    ============ CODE MANAGEMENT ============
    language: Programming language (e.g., 'python', 'javascript')
    function_name: Function or class name
    purpose: Brief description of what the code does
    parameters: List of parameter names
    complexity: Complexity level - 'simple', 'medium', 'complex'
    dependencies: List of dependencies/imports

    ============ STATE TRACKING ============
    emotion: Emotion and cognitive state data (EmotionData)

    ============ THINKING ANALYSIS ============
    thinking_level: Thinking level 1-4
        1: Recording facts
        2: Understanding principles
        3: Forming insights
        4: Innovative application
    learning_phase: Learning phase (exploration/learning/mastery)
    knowledge_domain: Knowledge domain (frontend/backend/algorithms/etc)

    ============ GENERAL FIELDS ============
    created_at: Creation timestamp (ISO format)
    updated_at: Last update timestamp (ISO format)
    quality_score: Content quality score 0-10
    """
    # Required fields
    filename: str
    filepath: str
    chunk_id: int
    chunk_type: str

    # Basic fields
    date: Optional[str]
    title: Optional[str]
    sub_chunk_id: Optional[int]

    # Tag system
    tags: Optional[List[str]]
    tag_layers: Optional[TagLayers]

    # Conversation memory
    conversation_id: Optional[str]
    importance: Optional[int]
    participants: Optional[List[str]]

    # Code management
    language: Optional[str]
    function_name: Optional[str]
    purpose: Optional[str]
    parameters: Optional[List[str]]
    complexity: Optional[str]
    dependencies: Optional[List[str]]

    # State tracking
    emotion: Optional[EmotionData]

    # Thinking analysis
    thinking_level: Optional[int]
    learning_phase: Optional[str]
    knowledge_domain: Optional[str]

    # General fields
    created_at: Optional[str]
    updated_at: Optional[str]
    quality_score: Optional[float]


class Chunk(TypedDict):
    """
    Document chunk format.

    All chunks must have:
        content: The actual text content of the chunk
        metadata: ChunkMetadata with required fields
    """
    content: str
    metadata: ChunkMetadata


def validate_chunk(chunk: dict) -> bool:
    """
    Validate if a chunk conforms to the schema.

    Args:
        chunk: Chunk dictionary to validate

    Returns:
        True if valid, False otherwise
    """
    if not isinstance(chunk, dict):
        return False

    if 'content' not in chunk or 'metadata' not in chunk:
        return False

    if not isinstance(chunk['content'], str):
        return False

    metadata = chunk['metadata']
    required_fields = ['filename', 'filepath', 'chunk_id', 'chunk_type']

    for field in required_fields:
        if field not in metadata:
            return False

    return True


def validate_chunk_type(chunk: dict, expected_type: str) -> bool:
    """
    Validate if a chunk is of a specific type.

    Args:
        chunk: Chunk dictionary
        expected_type: Expected chunk_type ('note', 'conversation', 'code', etc.)

    Returns:
        True if chunk is of expected type
    """
    if not validate_chunk(chunk):
        return False
    return chunk['metadata'].get('chunk_type') == expected_type


def get_chunk_type(chunk: dict) -> Optional[str]:
    """Get the type of a chunk."""
    if not validate_chunk(chunk):
        return None
    return chunk['metadata'].get('chunk_type')


# Chunk type constants
CHUNK_TYPE_NOTE = 'note'
CHUNK_TYPE_CONVERSATION = 'conversation'
CHUNK_TYPE_CODE = 'code'
CHUNK_TYPE_SUMMARY = 'summary'

# Cognitive state constants
STATE_EXPLORATION = 'exploration'
STATE_CONFUSION = 'confusion'
STATE_BREAKTHROUGH = 'breakthrough'
STATE_CONSOLIDATION = 'consolidation'
STATE_BURNOUT = 'burnout'
STATE_STAGNATION = 'stagnation'

# Thinking level constants
THINKING_LEVEL_FACTS = 1        # Recording facts
THINKING_LEVEL_PRINCIPLES = 2   # Understanding principles
THINKING_LEVEL_INSIGHTS = 3     # Forming insights
THINKING_LEVEL_INNOVATION = 4   # Innovative application

# Complexity level constants
COMPLEXITY_SIMPLE = 'simple'
COMPLEXITY_MEDIUM = 'medium'
COMPLEXITY_COMPLEX = 'complex'

# Importance score constants
IMPORTANCE_TRIVIAL = 1      # Trivial content, greetings
IMPORTANCE_LOW = 2          # Simple Q&A, facts
IMPORTANCE_MEDIUM = 3       # Useful info, regular learning
IMPORTANCE_HIGH = 4         # Deep discussion, problem solving
IMPORTANCE_CRITICAL = 5     # Major decisions, breakthroughs

# Recommended chunk size constraints
MIN_CHUNK_SIZE = 50      # Minimum characters
MAX_CHUNK_SIZE = 2000    # Maximum characters (can be exceeded for semantic integrity)
TARGET_CHUNK_SIZE = 500  # Target size for optimal retrieval


# Helper functions for creating specific chunk types

def create_note_metadata(filename: str, filepath: str, chunk_id: int, **kwargs) -> ChunkMetadata:
    """
    Create metadata for a note chunk.

    Args:
        filename: Source file name
        filepath: Full file path
        chunk_id: Chunk ID
        **kwargs: Additional metadata fields

    Returns:
        ChunkMetadata dictionary
    """
    metadata: ChunkMetadata = {
        'filename': filename,
        'filepath': filepath,
        'chunk_id': chunk_id,
        'chunk_type': CHUNK_TYPE_NOTE,
    }
    metadata.update(kwargs)  # type: ignore
    return metadata


def create_conversation_metadata(conversation_id: str, importance: int, **kwargs) -> ChunkMetadata:
    """
    Create metadata for a conversation chunk.

    Args:
        conversation_id: Unique conversation ID
        importance: Importance score 1-5
        **kwargs: Additional metadata fields

    Returns:
        ChunkMetadata dictionary
    """
    metadata: ChunkMetadata = {
        'filename': f'conversation_{conversation_id}',
        'filepath': f'conversations/{conversation_id}',
        'chunk_id': 0,
        'chunk_type': CHUNK_TYPE_CONVERSATION,
        'conversation_id': conversation_id,
        'importance': importance,
        'participants': ['user', 'ai'],
    }
    metadata.update(kwargs)  # type: ignore
    return metadata


def create_code_metadata(filename: str, filepath: str, chunk_id: int,
                        language: str, **kwargs) -> ChunkMetadata:
    """
    Create metadata for a code chunk.

    Args:
        filename: Source file name
        filepath: Full file path
        chunk_id: Chunk ID
        language: Programming language
        **kwargs: Additional metadata fields

    Returns:
        ChunkMetadata dictionary
    """
    metadata: ChunkMetadata = {
        'filename': filename,
        'filepath': filepath,
        'chunk_id': chunk_id,
        'chunk_type': CHUNK_TYPE_CODE,
        'language': language,
    }
    metadata.update(kwargs)  # type: ignore
    return metadata
