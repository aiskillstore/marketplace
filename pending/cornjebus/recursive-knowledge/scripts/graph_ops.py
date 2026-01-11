#!/usr/bin/env python3
"""
Graph Operations for Recursive Knowledge Processing

Core data structures and operations for the knowledge graph.
Used by index_corpus.py and query.py.
"""

import json
from dataclasses import dataclass, field, asdict
from typing import Optional
from pathlib import Path
import hashlib


@dataclass
class Entity:
    """A node in the knowledge graph."""
    id: str
    type: str  # person, organization, concept, date, location, event
    name: str
    aliases: list[str] = field(default_factory=list)
    attributes: dict = field(default_factory=dict)
    source_docs: list[str] = field(default_factory=list)  # document IDs where found
    extraction_confidence: float = 1.0
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, d):
        return cls(**d)


@dataclass  
class Relationship:
    """An edge in the knowledge graph."""
    id: str
    type: str  # references, mentions, supports, contradicts, relates_to, works_with, etc.
    source_entity_id: str
    target_entity_id: str
    attributes: dict = field(default_factory=dict)
    source_docs: list[str] = field(default_factory=list)
    extraction_confidence: float = 1.0
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, d):
        return cls(**d)


@dataclass
class Document:
    """Metadata about an indexed document."""
    id: str
    path: str
    title: str
    content_hash: str
    chunk_count: int
    indexed_at: str
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, d):
        return cls(**d)


class KnowledgeGraph:
    """
    In-memory knowledge graph with persistence.
    
    Structure:
    - entities: dict[id -> Entity]
    - relationships: dict[id -> Relationship]
    - documents: dict[id -> Document]
    - indexes: various lookup indexes for fast traversal
    """
    
    def __init__(self):
        self.entities: dict[str, Entity] = {}
        self.relationships: dict[str, Relationship] = {}
        self.documents: dict[str, Document] = {}
        
        # Indexes for fast lookup
        self._entity_by_name: dict[str, list[str]] = {}  # name -> [entity_ids]
        self._entity_by_type: dict[str, list[str]] = {}  # type -> [entity_ids]
        self._relationships_from: dict[str, list[str]] = {}  # entity_id -> [rel_ids]
        self._relationships_to: dict[str, list[str]] = {}  # entity_id -> [rel_ids]
    
    def add_entity(self, entity: Entity) -> str:
        """Add entity to graph, return ID."""
        self.entities[entity.id] = entity
        
        # Update indexes
        name_lower = entity.name.lower()
        if name_lower not in self._entity_by_name:
            self._entity_by_name[name_lower] = []
        self._entity_by_name[name_lower].append(entity.id)
        
        if entity.type not in self._entity_by_type:
            self._entity_by_type[entity.type] = []
        self._entity_by_type[entity.type].append(entity.id)
        
        # Index aliases too
        for alias in entity.aliases:
            alias_lower = alias.lower()
            if alias_lower not in self._entity_by_name:
                self._entity_by_name[alias_lower] = []
            self._entity_by_name[alias_lower].append(entity.id)
        
        return entity.id
    
    def add_relationship(self, rel: Relationship) -> str:
        """Add relationship to graph, return ID."""
        self.relationships[rel.id] = rel
        
        # Update indexes
        if rel.source_entity_id not in self._relationships_from:
            self._relationships_from[rel.source_entity_id] = []
        self._relationships_from[rel.source_entity_id].append(rel.id)
        
        if rel.target_entity_id not in self._relationships_to:
            self._relationships_to[rel.target_entity_id] = []
        self._relationships_to[rel.target_entity_id].append(rel.id)
        
        return rel.id
    
    def add_document(self, doc: Document) -> str:
        """Add document metadata to graph."""
        self.documents[doc.id] = doc
        return doc.id
    
    def find_entities_by_name(self, name: str) -> list[Entity]:
        """Find entities matching name (case-insensitive)."""
        entity_ids = self._entity_by_name.get(name.lower(), [])
        return [self.entities[eid] for eid in entity_ids if eid in self.entities]
    
    def find_entities_by_type(self, entity_type: str) -> list[Entity]:
        """Find all entities of a given type."""
        entity_ids = self._entity_by_type.get(entity_type, [])
        return [self.entities[eid] for eid in entity_ids if eid in self.entities]
    
    def get_outgoing_relationships(self, entity_id: str) -> list[Relationship]:
        """Get all relationships where entity is the source."""
        rel_ids = self._relationships_from.get(entity_id, [])
        return [self.relationships[rid] for rid in rel_ids if rid in self.relationships]
    
    def get_incoming_relationships(self, entity_id: str) -> list[Relationship]:
        """Get all relationships where entity is the target."""
        rel_ids = self._relationships_to.get(entity_id, [])
        return [self.relationships[rid] for rid in rel_ids if rid in self.relationships]
    
    def get_neighbors(self, entity_id: str) -> list[tuple[Relationship, Entity]]:
        """Get all connected entities with their relationships."""
        neighbors = []
        
        for rel in self.get_outgoing_relationships(entity_id):
            if rel.target_entity_id in self.entities:
                neighbors.append((rel, self.entities[rel.target_entity_id]))
        
        for rel in self.get_incoming_relationships(entity_id):
            if rel.source_entity_id in self.entities:
                neighbors.append((rel, self.entities[rel.source_entity_id]))
        
        return neighbors
    
    def save(self, path: str):
        """Persist graph to JSON file."""
        data = {
            "entities": {k: v.to_dict() for k, v in self.entities.items()},
            "relationships": {k: v.to_dict() for k, v in self.relationships.items()},
            "documents": {k: v.to_dict() for k, v in self.documents.items()},
        }
        Path(path).write_text(json.dumps(data, indent=2))
    
    @classmethod
    def load(cls, path: str) -> "KnowledgeGraph":
        """Load graph from JSON file."""
        data = json.loads(Path(path).read_text())
        
        graph = cls()
        for entity_dict in data.get("entities", {}).values():
            graph.add_entity(Entity.from_dict(entity_dict))
        
        for rel_dict in data.get("relationships", {}).values():
            graph.add_relationship(Relationship.from_dict(rel_dict))
        
        for doc_dict in data.get("documents", {}).values():
            graph.add_document(Document.from_dict(doc_dict))
        
        return graph
    
    def stats(self) -> dict:
        """Return graph statistics."""
        return {
            "entity_count": len(self.entities),
            "relationship_count": len(self.relationships),
            "document_count": len(self.documents),
            "entity_types": dict(sorted(
                {t: len(ids) for t, ids in self._entity_by_type.items()}.items(),
                key=lambda x: -x[1]
            )),
        }


def generate_id(prefix: str, content: str) -> str:
    """Generate deterministic ID from content."""
    hash_val = hashlib.sha256(content.encode()).hexdigest()[:12]
    return f"{prefix}_{hash_val}"


if __name__ == "__main__":
    # Simple test
    graph = KnowledgeGraph()
    
    e1 = Entity(
        id=generate_id("ent", "Anthropic"),
        type="organization",
        name="Anthropic",
        aliases=["Anthropic AI"],
    )
    e2 = Entity(
        id=generate_id("ent", "Claude"),
        type="concept",
        name="Claude",
        aliases=["Claude AI", "Claude model"],
    )
    
    graph.add_entity(e1)
    graph.add_entity(e2)
    
    r1 = Relationship(
        id=generate_id("rel", f"{e1.id}-created-{e2.id}"),
        type="created",
        source_entity_id=e1.id,
        target_entity_id=e2.id,
    )
    graph.add_relationship(r1)
    
    print("Graph stats:", graph.stats())
    print("Neighbors of Anthropic:", [(r.type, e.name) for r, e in graph.get_neighbors(e1.id)])
