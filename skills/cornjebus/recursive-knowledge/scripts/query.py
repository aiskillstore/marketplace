#!/usr/bin/env python3
"""
Query Engine with Stateful Traversal

This is the key improvement over naive RLM approaches.

Features:
- State tracking: visited nodes, edges, findings
- Confidence scoring: know when answer is good enough
- Termination logic: stop when criteria met
- Provenance: track where findings came from
- Multi-hop: traverse paths between entry points

Usage:
    python3 query.py --graph graph.json --query "your question here"
    python3 query.py --graph graph.json --query "question" --max-depth 5 --confidence 0.9
"""

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from graph_ops import KnowledgeGraph, Entity, Relationship


# =============================================================================
# STATE MANAGEMENT - The key innovation
# =============================================================================

@dataclass
class Finding:
    """A piece of evidence found during traversal."""
    content: str
    entity_ids: list[str]
    relationship_ids: list[str]
    source_docs: list[str]
    confidence: float
    path: list[str]  # How we got here


@dataclass
class TraversalState:
    """
    Tracks everything during query execution.
    
    This is what RLM lacks - persistent state that prevents
    redundant exploration and knows when to stop.
    """
    # What we've explored
    visited_nodes: set[str] = field(default_factory=set)
    visited_edges: set[str] = field(default_factory=set)
    
    # What we've found
    findings: list[Finding] = field(default_factory=list)
    
    # Confidence tracking
    confidence: float = 0.0
    corroborating_sources: set[str] = field(default_factory=set)
    
    # Depth tracking
    current_depth: int = 0
    max_depth: int = 5
    
    # Termination config
    confidence_threshold: float = 0.85
    min_corroborating_sources: int = 3
    
    def should_stop(self) -> tuple[bool, str]:
        """
        Determine if we should stop traversing.
        
        Returns (should_stop, reason)
        """
        if self.confidence >= self.confidence_threshold:
            return True, f"Confidence threshold met: {self.confidence:.2f}"
        
        if len(self.corroborating_sources) >= self.min_corroborating_sources:
            return True, f"Sufficient corroboration: {len(self.corroborating_sources)} sources"
        
        if self.current_depth >= self.max_depth:
            return True, f"Max depth reached: {self.current_depth}"
        
        return False, ""
    
    def already_visited_node(self, node_id: str) -> bool:
        """Check if node already explored."""
        return node_id in self.visited_nodes
    
    def already_visited_edge(self, edge_id: str) -> bool:
        """Check if edge already traversed."""
        return edge_id in self.visited_edges
    
    def record_visit(self, node_id: str = None, edge_id: str = None):
        """Record that we've visited a node or edge."""
        if node_id:
            self.visited_nodes.add(node_id)
        if edge_id:
            self.visited_edges.add(edge_id)
    
    def add_finding(self, finding: Finding):
        """Add a finding and update confidence."""
        self.findings.append(finding)
        
        # Update corroborating sources
        for doc_id in finding.source_docs:
            self.corroborating_sources.add(doc_id)
        
        # Update confidence based on findings
        self._update_confidence()
    
    def _update_confidence(self):
        """Recalculate confidence based on findings."""
        if not self.findings:
            self.confidence = 0.0
            return
        
        # Factors that increase confidence:
        # - More findings
        # - Higher individual finding confidence
        # - More corroborating sources
        # - Consistent findings (not contradictory)
        
        avg_finding_confidence = sum(f.confidence for f in self.findings) / len(self.findings)
        source_factor = min(1.0, len(self.corroborating_sources) / self.min_corroborating_sources)
        count_factor = min(1.0, len(self.findings) / 5)  # Cap at 5 findings
        
        self.confidence = (avg_finding_confidence * 0.4 + 
                          source_factor * 0.4 + 
                          count_factor * 0.2)


# =============================================================================
# QUERY PARSING
# =============================================================================

def parse_query(query: str, graph: KnowledgeGraph) -> list[str]:
    """
    Parse query to find entry point entities.
    
    In production, use LLM to extract target entities.
    For now, simple keyword matching.
    """
    entry_points = []
    query_lower = query.lower()
    
    # Find entities mentioned in query
    for entity in graph.entities.values():
        if entity.name.lower() in query_lower:
            entry_points.append(entity.id)
        else:
            for alias in entity.aliases:
                if alias.lower() in query_lower:
                    entry_points.append(entity.id)
                    break
    
    return entry_points


def extract_query_intent(query: str) -> dict:
    """
    Extract what the query is asking for.
    
    In production, use LLM for this.
    """
    intent = {
        "looking_for": [],  # Types of entities we're looking for
        "relationship_types": [],  # Types of relationships to follow
    }
    
    # Simple heuristics
    query_lower = query.lower()
    
    if "who" in query_lower:
        intent["looking_for"].append("person")
    if "where" in query_lower:
        intent["looking_for"].append("location")
    if "when" in query_lower:
        intent["looking_for"].append("date")
    if "what" in query_lower:
        intent["looking_for"].extend(["concept", "organization"])
    
    if "work" in query_lower:
        intent["relationship_types"].extend(["works_with", "works_for"])
    if "create" in query_lower or "made" in query_lower:
        intent["relationship_types"].append("created")
    
    return intent


# =============================================================================
# TRAVERSAL ENGINE
# =============================================================================

def traverse_from_entity(
    graph: KnowledgeGraph,
    entity_id: str,
    state: TraversalState,
    query_intent: dict,
    path: list[str] = None
) -> list[Finding]:
    """
    Traverse graph from an entity, respecting state.
    
    This is where we prevent the RLM infinite loop problem:
    - Check if already visited before exploring
    - Record visits as we go
    - Check termination conditions frequently
    """
    if path is None:
        path = []
    
    findings = []
    
    # Check if we should stop globally
    should_stop, reason = state.should_stop()
    if should_stop:
        return findings
    
    # Check if already visited this node
    if state.already_visited_node(entity_id):
        return findings
    
    # Record visit
    state.record_visit(node_id=entity_id)
    current_path = path + [entity_id]
    
    # Get the entity
    entity = graph.entities.get(entity_id)
    if not entity:
        return findings
    
    # Check if this entity matches what we're looking for
    if not query_intent["looking_for"] or entity.type in query_intent["looking_for"]:
        finding = Finding(
            content=f"Found {entity.type}: {entity.name}",
            entity_ids=[entity_id],
            relationship_ids=[],
            source_docs=entity.source_docs,
            confidence=entity.extraction_confidence,
            path=current_path,
        )
        findings.append(finding)
        state.add_finding(finding)
    
    # Check termination again after adding finding
    should_stop, reason = state.should_stop()
    if should_stop:
        return findings
    
    # Increase depth for recursive calls
    state.current_depth += 1
    
    # Explore neighbors
    for rel, neighbor in graph.get_neighbors(entity_id):
        # Check if we should follow this relationship type
        if query_intent["relationship_types"] and rel.type not in query_intent["relationship_types"]:
            continue
        
        # Check if already traversed this edge
        if state.already_visited_edge(rel.id):
            continue
        
        # Record edge visit
        state.record_visit(edge_id=rel.id)
        
        # Create finding for this relationship
        rel_finding = Finding(
            content=f"{entity.name} --[{rel.type}]--> {neighbor.name}",
            entity_ids=[entity_id, neighbor.id],
            relationship_ids=[rel.id],
            source_docs=rel.source_docs,
            confidence=rel.extraction_confidence,
            path=current_path + [rel.id],
        )
        findings.append(rel_finding)
        state.add_finding(rel_finding)
        
        # Check termination
        should_stop, reason = state.should_stop()
        if should_stop:
            break
        
        # Recurse to neighbor
        neighbor_findings = traverse_from_entity(
            graph, neighbor.id, state, query_intent, current_path
        )
        findings.extend(neighbor_findings)
        
        # Check termination again
        should_stop, reason = state.should_stop()
        if should_stop:
            break
    
    state.current_depth -= 1
    return findings


def execute_query(
    graph: KnowledgeGraph,
    query: str,
    max_depth: int = 5,
    confidence_threshold: float = 0.85,
    min_sources: int = 3,
    verbose: bool = False
) -> dict:
    """
    Execute a query against the knowledge graph.
    
    Returns structured result with answer, confidence, and provenance.
    """
    # Initialize state
    state = TraversalState(
        max_depth=max_depth,
        confidence_threshold=confidence_threshold,
        min_corroborating_sources=min_sources,
    )
    
    # Parse query
    entry_points = parse_query(query, graph)
    query_intent = extract_query_intent(query)
    
    if verbose:
        print(f"Query: {query}")
        print(f"Entry points: {[graph.entities[e].name for e in entry_points if e in graph.entities]}")
        print(f"Intent: {query_intent}")
    
    # Traverse from each entry point
    all_findings = []
    for entry_id in entry_points:
        findings = traverse_from_entity(graph, entry_id, state, query_intent)
        all_findings.extend(findings)
        
        should_stop, reason = state.should_stop()
        if should_stop:
            if verbose:
                print(f"Stopping: {reason}")
            break
    
    # Compile result
    result = {
        "query": query,
        "answer": synthesize_answer(all_findings, query),
        "confidence": state.confidence,
        "findings_count": len(state.findings),
        "sources": list(state.corroborating_sources),
        "nodes_visited": len(state.visited_nodes),
        "edges_visited": len(state.visited_edges),
        "termination_reason": state.should_stop()[1] or "All paths exhausted",
        "findings": [
            {
                "content": f.content,
                "confidence": f.confidence,
                "sources": f.source_docs,
            }
            for f in state.findings[:10]  # Top 10 findings
        ],
    }
    
    return result


def synthesize_answer(findings: list[Finding], query: str) -> str:
    """
    Synthesize findings into an answer.
    
    In production, use LLM to generate natural language answer.
    For now, concatenate findings.
    """
    if not findings:
        return "No relevant information found."
    
    # Group by confidence
    high_conf = [f for f in findings if f.confidence >= 0.8]
    
    if high_conf:
        return " | ".join([f.content for f in high_conf[:5]])
    else:
        return " | ".join([f.content for f in findings[:5]])


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Query knowledge graph")
    parser.add_argument("--graph", "-g", required=True, help="Path to graph JSON")
    parser.add_argument("--query", "-q", required=True, help="Query to execute")
    parser.add_argument("--max-depth", "-d", type=int, default=5, help="Max traversal depth")
    parser.add_argument("--confidence", "-c", type=float, default=0.85, help="Confidence threshold")
    parser.add_argument("--min-sources", "-s", type=int, default=3, help="Min corroborating sources")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Load graph
    graph_path = Path(args.graph)
    if not graph_path.exists():
        print(f"Error: Graph file not found: {graph_path}")
        sys.exit(1)
    
    graph = KnowledgeGraph.load(str(graph_path))
    
    if args.verbose:
        print(f"Loaded graph: {graph.stats()}")
    
    # Execute query
    result = execute_query(
        graph,
        args.query,
        max_depth=args.max_depth,
        confidence_threshold=args.confidence,
        min_sources=args.min_sources,
        verbose=args.verbose,
    )
    
    # Output result
    print("\n" + "="*60)
    print(f"Answer: {result['answer']}")
    print(f"Confidence: {result['confidence']:.2%}")
    print(f"Sources: {len(result['sources'])} documents")
    print(f"Exploration: {result['nodes_visited']} nodes, {result['edges_visited']} edges")
    print(f"Termination: {result['termination_reason']}")
    print("="*60)
    
    if args.verbose:
        print("\nFindings:")
        for i, f in enumerate(result['findings'], 1):
            print(f"  {i}. {f['content']} (conf: {f['confidence']:.2f})")


if __name__ == "__main__":
    main()
