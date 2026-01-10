---
name: memory-management
description: Core workflows for managing persistent context using the knowledge graph
---

# Memory Management Skill

This skill provides comprehensive workflows for managing persistent context across conversations using the memory MCP server's knowledge graph capabilities.

## When to Use This Skill

- Starting new projects that need context preservation
- Resuming work after breaks or session changes
- Tracking user preferences and decisions
- Building relationships between concepts
- Maintaining project knowledge bases
- Cross-referencing technical information
- Preserving important conversation context

## Core Workflows

### Project Initialization

When starting a new project:

1. Create project entity with descriptive name
2. Add observations about goals, scope, timeline
3. Create team member entities if applicable
4. Establish relationships (who works on what)
5. Store technology stack as concept entities
6. Link technologies to project
7. Document initial decisions as observations

Example workflow:

```
1. mcp__memory__create_entities("project-webapp", "project")
2. mcp__memory__add_observations("project-webapp", "React-based todo application with TypeScript")
3. mcp__memory__create_entities("tech-react", "technology")
4. mcp__memory__create_relations("project-webapp", "uses", "tech-react")
```

### Context Preservation

When important information needs to be remembered:

1. Identify key entities mentioned (people, projects, concepts)
2. Check if entities already exist in graph
3. Create new entities or update existing ones
4. Add timestamped observations with context
5. Create relationships to show connections
6. Tag with importance level if critical

Key information types to preserve:

- Architectural decisions
- User preferences
- API endpoints and credentials
- Configuration settings
- Problem solutions
- Team agreements

### Knowledge Building

When accumulating domain knowledge:

1. Create concept entities for important topics
2. Add detailed observations with explanations
3. Link related concepts together
4. Build hierarchy with parent-child relations
5. Add examples as observations
6. Cross-reference with projects using concepts

Example structure:

```
authentication (concept)
├── Observations:
│   ├── "JWT tokens for stateless auth"
│   ├── "Refresh token rotation strategy"
│   └── "OAuth2 integration points"
├── Relations:
│   ├── parent_of → jwt-tokens
│   ├── parent_of → oauth2
│   └── used_by → project-webapp
```

### Session Continuity

When resuming work:

1. Search for relevant project entity
2. Read recent observations for context
3. Check relationships for dependencies
4. Identify last known state
5. Update with new session information
6. Add observation about work resumption

Search pattern:

```
1. mcp__memory__search_nodes("project-name")
2. mcp__memory__open_nodes(["project-id"])
3. Review observations for recent updates
4. Continue from last checkpoint
```

### Preference Management

When tracking user or project preferences:

1. Create preference entities with clear names
2. Add observations about specific preferences
3. Link to relevant projects or users
4. Update when preferences change
5. Check preferences before making decisions

Preference categories:

- Coding style (formatting, patterns)
- Tool preferences (editor, terminal)
- Communication style (formal, casual)
- Technology choices (frameworks, libraries)
- Workflow preferences (TDD, agile)

### Relationship Mapping

When building connections:

1. Identify entities that should be connected
2. Determine relationship type and direction
3. Create meaningful relationship labels
4. Add observations explaining the connection
5. Consider bidirectional relationships
6. Update as relationships evolve

Common relationship patterns:

- Person `works_on` Project
- Project `depends_on` Service
- Concept `related_to` Concept
- Tool `used_by` Project
- Issue `blocks` Feature
- Decision `affects` Component

### Memory Search Strategies

When finding information:

1. **Broad to Specific**: Start with general terms, narrow down
2. **Type Filtering**: Search by entity type when known
3. **Relationship Traversal**: Follow connections from known entities
4. **Keyword Search**: Look for specific terms in observations
5. **Recent Activity**: Check recently modified entities
6. **Pattern Matching**: Find entities with similar structures

### Memory Maintenance

Regular maintenance tasks:

1. **Deduplication**: Merge duplicate entities
2. **Cleanup**: Remove outdated observations
3. **Consolidation**: Combine related observations
4. **Archival**: Move old but valuable info to archive observations
5. **Validation**: Verify relationship accuracy
6. **Optimization**: Remove redundant relationships

### Error Recovery

When memory operations fail:

1. Check entity name format (avoid special characters)
2. Verify entities exist before creating relationships
3. Confirm observation format is valid
4. Try alternative search terms
5. Check for typos in entity names
6. Review error messages for specific issues

## Best Practices

### Entity Naming

- Use descriptive, unique names
- Include type prefix when helpful (project-, user-, tech-)
- Use consistent naming patterns
- Avoid special characters
- Keep names reasonably short

### Observation Quality

- Include timestamps for time-sensitive info
- Add context about source or reliability
- Keep observations focused and specific
- Update rather than duplicate similar info
- Use structured format for complex data

### Relationship Design

- Choose clear, consistent relationship types
- Consider relationship directionality
- Avoid circular dependencies
- Document non-obvious relationships
- Regularly review and update

### Search Optimization

- Index frequently searched terms
- Use consistent vocabulary
- Create search aliases for common queries
- Cache recent search results
- Build search hierarchies

## Integration with Other Tools

### With Code Editors

- Store code snippets as observations
- Link files to project entities
- Track refactoring decisions
- Remember debugging solutions

### With Documentation

- Link docs to relevant entities
- Store API specifications
- Track documentation updates
- Cross-reference with code

### With Communication

- Record meeting decisions
- Track action items
- Store team agreements
- Link discussions to projects

## Advanced Patterns

### Graph Traversal

Navigate complex relationships:

```
1. Start from known entity
2. Get all relationships
3. Follow specific relationship types
4. Collect related entities
5. Recurse to desired depth
```

### Temporal Tracking

Track changes over time:

```
1. Add timestamp to all observations
2. Create version entities for major changes
3. Link versions with "succeeded_by" relations
4. Query by time range
```

### Hierarchical Organization

Build tree structures:

```
1. Create parent entities
2. Create child entities
3. Use "parent_of" relationships
4. Traverse hierarchy as needed
```

## Common Pitfalls to Avoid

- Creating duplicate entities with similar names
- Forgetting to add timestamps to time-sensitive observations
- Creating too many low-value relationships
- Not cleaning up outdated information
- Using inconsistent relationship types
- Storing sensitive information without consideration
- Over-structuring simple information
- Under-structuring complex information

## Troubleshooting

### Entity Not Found

- Check exact spelling and case
- Try searching with partial terms
- Verify entity was created successfully
- Look for similar entities

### Relationship Creation Failed

- Ensure both entities exist
- Check relationship type format
- Verify no duplicate relationship
- Review error message details

### Search Returns Too Many Results

- Add type filter
- Use more specific terms
- Filter by relationships
- Limit to recent entities

### Memory Growing Too Large

- Remove outdated observations
- Delete unused entities
- Consolidate similar entities
- Archive old information
