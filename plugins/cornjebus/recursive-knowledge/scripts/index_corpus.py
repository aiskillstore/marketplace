#!/usr/bin/env python3
"""
Index Corpus into Knowledge Graph

Takes a directory of documents and builds a knowledge graph by:
1. Reading each document
2. Chunking into processable pieces
3. Extracting entities via LLM
4. Extracting relationships via LLM
5. Persisting to graph file

Usage:
    python3 index_corpus.py --input /path/to/docs --output graph.json
    python3 index_corpus.py --input /path/to/new_docs --output graph.json --append
"""

import argparse
import json
import hashlib
from pathlib import Path
from datetime import datetime
import sys
import os

# Add scripts dir to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from graph_ops import KnowledgeGraph, Entity, Relationship, Document, generate_id


# Chunk size in characters - tuned for LLM context
CHUNK_SIZE = 8000
CHUNK_OVERLAP = 500


def read_document(path: Path) -> tuple[str, str]:
    """Read document, return (title, content)."""
    content = path.read_text(encoding='utf-8', errors='ignore')
    title = path.stem.replace('_', ' ').replace('-', ' ')
    return title, content


def chunk_document(content: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split document into overlapping chunks."""
    if len(content) <= chunk_size:
        return [content]
    
    chunks = []
    start = 0
    while start < len(content):
        end = start + chunk_size
        chunk = content[start:end]
        
        # Try to break at sentence boundary
        if end < len(content):
            last_period = chunk.rfind('.')
            last_newline = chunk.rfind('\n')
            break_point = max(last_period, last_newline)
            if break_point > chunk_size // 2:
                chunk = chunk[:break_point + 1]
                end = start + break_point + 1
        
        chunks.append(chunk)
        start = end - overlap
    
    return chunks


def extract_entities_prompt(chunk: str, doc_title: str) -> str:
    """Generate prompt for entity extraction."""
    return f"""Extract all named entities from this text chunk.

Document: {doc_title}

Text:
{chunk}

Return JSON array of entities:
[
  {{"name": "Entity Name", "type": "person|organization|concept|date|location|event", "aliases": ["optional", "aliases"]}},
  ...
]

Only include clearly identifiable entities. Use these types:
- person: Individual people
- organization: Companies, agencies, groups
- concept: Ideas, technologies, methods, products
- date: Specific dates or time periods
- location: Places, addresses
- event: Named events, conferences, incidents

Return ONLY valid JSON array, no other text."""


def extract_relationships_prompt(chunk: str, entities: list[dict], doc_title: str) -> str:
    """Generate prompt for relationship extraction."""
    entity_list = "\n".join([f"- {e['name']} ({e['type']})" for e in entities])
    
    return f"""Extract relationships between these entities based on the text.

Document: {doc_title}

Entities found:
{entity_list}

Text:
{chunk}

Return JSON array of relationships:
[
  {{"source": "Entity Name", "target": "Other Entity", "type": "relationship_type", "details": "optional context"}},
  ...
]

Relationship types:
- works_with: Professional collaboration
- works_for: Employment relationship
- created: Made or produced something
- references: Mentions or cites
- supports: Agrees with or backs
- contradicts: Disagrees with
- located_in: Geographic relationship
- part_of: Component or member of
- occurred_at: Event timing/location

Return ONLY valid JSON array, no other text."""


def call_llm(prompt: str) -> str:
    """
    Call LLM for extraction.
    
    Uses heuristic extraction by default.
    Set USE_LLM=1 environment variable to use Claude API.
    """
    if os.environ.get("USE_LLM") == "1":
        try:
            import anthropic
            client = anthropic.Anthropic()
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            print(f"  [LLM call failed: {e}, falling back to heuristic]")
    
    # Heuristic extraction for testing
    return heuristic_extract(prompt)


def heuristic_extract(prompt: str) -> str:
    """
    Simple rule-based entity extraction for testing.
    Not as good as LLM but allows testing the full pipeline.
    """
    import re
    
    # Check if this is entity extraction or relationship extraction
    if "Extract all named entities" in prompt:
        return heuristic_entity_extraction(prompt)
    elif "Extract relationships" in prompt:
        return heuristic_relationship_extraction(prompt)
    return "[]"


def heuristic_entity_extraction(prompt: str) -> str:
    """Extract entities using simple patterns."""
    import re
    
    # Extract the text chunk from prompt
    text_match = re.search(r'Text:\n(.+?)(?:\n\nReturn|$)', prompt, re.DOTALL)
    if not text_match:
        return "[]"
    
    text = text_match.group(1)
    entities = []
    
    # Pattern: Capitalized words (likely proper nouns)
    # Look for sequences of capitalized words
    proper_nouns = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', text)
    
    # Common patterns for entity types
    org_keywords = ['company', 'inc', 'corp', 'founded', 'headquartered', 'agency']
    person_keywords = ['ceo', 'founder', 'serves as', 'developed by']
    location_keywords = ['headquartered in', 'located in', 'based in']
    
    text_lower = text.lower()
    seen = set()
    
    for noun in proper_nouns:
        if noun in seen or len(noun) < 2:
            continue
        seen.add(noun)
        
        # Skip common words
        if noun.lower() in ['the', 'a', 'an', 'is', 'are', 'was', 'were']:
            continue
        
        # Guess entity type based on context
        entity_type = "concept"  # default
        
        # Check context around the noun
        noun_idx = text.find(noun)
        context = text[max(0, noun_idx-50):noun_idx+len(noun)+50].lower()
        
        if any(kw in context for kw in person_keywords):
            entity_type = "person"
        elif any(kw in context for kw in org_keywords):
            entity_type = "organization"
        elif any(kw in context for kw in location_keywords):
            entity_type = "location"
        elif noun.endswith(('AI', 'Miner', 'Platform', 'System')):
            entity_type = "concept"
        
        entities.append({
            "name": noun,
            "type": entity_type,
            "aliases": []
        })
    
    return json.dumps(entities)


def heuristic_relationship_extraction(prompt: str) -> str:
    """Extract relationships using simple patterns."""
    import re
    
    # Extract entities list from prompt
    entities_match = re.search(r'Entities found:\n(.+?)\n\nText:', prompt, re.DOTALL)
    text_match = re.search(r'Text:\n(.+?)(?:\n\nReturn|$)', prompt, re.DOTALL)
    
    if not entities_match or not text_match:
        return "[]"
    
    text = text_match.group(1)
    text_lower = text.lower()
    
    # Parse entity names
    entity_lines = entities_match.group(1).strip().split('\n')
    entity_names = [line.split('(')[0].replace('- ', '').strip() for line in entity_lines]
    
    relationships = []
    
    # Relationship patterns
    patterns = [
        (r'(\w+)\s+(?:is|was)\s+(?:the\s+)?(?:founder|ceo|founder)\s+of\s+(\w+)', 'works_for'),
        (r'(\w+)\s+founded\s+(\w+)', 'created'),
        (r'(\w+)\s+created\s+(\w+)', 'created'),
        (r'(\w+)\s+developed\s+(\w+)', 'created'),
        (r'(\w+)\s+is\s+headquartered\s+in\s+(\w+)', 'located_in'),
        (r'(\w+)\s+(?:works|worked)\s+(?:at|for)\s+(\w+)', 'works_for'),
    ]
    
    for pattern, rel_type in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for source, target in matches:
            # Check if entities are in our list
            source_match = next((e for e in entity_names if source.lower() in e.lower()), None)
            target_match = next((e for e in entity_names if target.lower() in e.lower()), None)
            
            if source_match and target_match:
                relationships.append({
                    "source": source_match,
                    "target": target_match,
                    "type": rel_type,
                    "details": ""
                })
    
    return json.dumps(relationships)


def parse_json_response(response: str) -> list:
    """Safely parse JSON from LLM response."""
    try:
        # Try direct parse
        return json.loads(response)
    except json.JSONDecodeError:
        # Try to extract JSON from response
        import re
        match = re.search(r'\[.*\]', response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    return []


def index_document(
    path: Path,
    graph: KnowledgeGraph,
    verbose: bool = False
) -> tuple[int, int]:
    """
    Index a single document into the graph.
    
    Returns (entity_count, relationship_count) added.
    """
    title, content = read_document(path)
    content_hash = hashlib.sha256(content.encode()).hexdigest()
    
    # Check if already indexed
    doc_id = generate_id("doc", str(path))
    if doc_id in graph.documents:
        existing = graph.documents[doc_id]
        if existing.content_hash == content_hash:
            if verbose:
                print(f"  Skipping {path.name} - already indexed")
            return 0, 0
    
    chunks = chunk_document(content)
    if verbose:
        print(f"  Processing {path.name}: {len(chunks)} chunks")
    
    entity_count = 0
    rel_count = 0
    doc_entities = {}  # Track entities found in this doc
    
    for i, chunk in enumerate(chunks):
        if verbose:
            print(f"    Chunk {i+1}/{len(chunks)}...")
        
        # Extract entities
        entity_prompt = extract_entities_prompt(chunk, title)
        entity_response = call_llm(entity_prompt)
        entities = parse_json_response(entity_response)
        
        for ent_data in entities:
            name = ent_data.get("name", "").strip()
            if not name:
                continue
            
            ent_id = generate_id("ent", name.lower())
            
            if ent_id in graph.entities:
                # Update existing entity with new source
                existing = graph.entities[ent_id]
                if doc_id not in existing.source_docs:
                    existing.source_docs.append(doc_id)
            else:
                # Create new entity
                entity = Entity(
                    id=ent_id,
                    type=ent_data.get("type", "concept"),
                    name=name,
                    aliases=ent_data.get("aliases", []),
                    source_docs=[doc_id],
                )
                graph.add_entity(entity)
                entity_count += 1
            
            doc_entities[name] = ent_id
        
        # Extract relationships
        if entities:
            rel_prompt = extract_relationships_prompt(chunk, entities, title)
            rel_response = call_llm(rel_prompt)
            relationships = parse_json_response(rel_response)
            
            for rel_data in relationships:
                source_name = rel_data.get("source", "").strip()
                target_name = rel_data.get("target", "").strip()
                rel_type = rel_data.get("type", "relates_to")
                
                # Find entity IDs
                source_id = doc_entities.get(source_name) or generate_id("ent", source_name.lower())
                target_id = doc_entities.get(target_name) or generate_id("ent", target_name.lower())
                
                if source_id in graph.entities and target_id in graph.entities:
                    rel_id = generate_id("rel", f"{source_id}-{rel_type}-{target_id}")
                    
                    if rel_id not in graph.relationships:
                        rel = Relationship(
                            id=rel_id,
                            type=rel_type,
                            source_entity_id=source_id,
                            target_entity_id=target_id,
                            attributes={"details": rel_data.get("details", "")},
                            source_docs=[doc_id],
                        )
                        graph.add_relationship(rel)
                        rel_count += 1
                    else:
                        # Update existing relationship with new source
                        existing = graph.relationships[rel_id]
                        if doc_id not in existing.source_docs:
                            existing.source_docs.append(doc_id)
    
    # Record document
    doc = Document(
        id=doc_id,
        path=str(path),
        title=title,
        content_hash=content_hash,
        chunk_count=len(chunks),
        indexed_at=datetime.now().isoformat(),
    )
    graph.add_document(doc)
    
    return entity_count, rel_count


def index_corpus(
    input_path: Path,
    output_path: Path,
    append: bool = False,
    verbose: bool = False
) -> KnowledgeGraph:
    """
    Index entire corpus into knowledge graph.
    """
    # Load existing or create new graph
    if append and output_path.exists():
        if verbose:
            print(f"Loading existing graph from {output_path}")
        graph = KnowledgeGraph.load(str(output_path))
    else:
        graph = KnowledgeGraph()
    
    # Find documents
    if input_path.is_file():
        doc_paths = [input_path]
    else:
        doc_paths = list(input_path.glob("**/*.txt")) + \
                    list(input_path.glob("**/*.md")) + \
                    list(input_path.glob("**/*.json"))
    
    if verbose:
        print(f"Found {len(doc_paths)} documents to index")
    
    total_entities = 0
    total_rels = 0
    
    for doc_path in doc_paths:
        try:
            ent_count, rel_count = index_document(doc_path, graph, verbose)
            total_entities += ent_count
            total_rels += rel_count
        except Exception as e:
            print(f"Error indexing {doc_path}: {e}")
    
    # Save graph
    graph.save(str(output_path))
    
    if verbose:
        print(f"\nIndexing complete:")
        print(f"  New entities: {total_entities}")
        print(f"  New relationships: {total_rels}")
        print(f"  Graph stats: {graph.stats()}")
    
    return graph


def main():
    parser = argparse.ArgumentParser(description="Index documents into knowledge graph")
    parser.add_argument("--input", "-i", required=True, help="Input directory or file")
    parser.add_argument("--output", "-o", required=True, help="Output graph JSON file")
    parser.add_argument("--append", "-a", action="store_true", help="Append to existing graph")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if not input_path.exists():
        print(f"Error: Input path does not exist: {input_path}")
        sys.exit(1)
    
    index_corpus(input_path, output_path, args.append, args.verbose)


if __name__ == "__main__":
    main()
