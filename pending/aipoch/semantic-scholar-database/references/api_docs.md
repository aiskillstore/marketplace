# Semantic Scholar API Reference

## Base URL
`https://api.semanticscholar.org/graph/v1`

## Rate Limits
- **Unauthenticated**: 100 requests per 5 minutes
- **Authenticated**: Higher limits (requires `S2_API_KEY`)

## Key Endpoints
- `/paper/search`: Search papers
- `/paper/{paper_id}`: Get paper details
- `/paper/{paper_id}/citations`: Get citations
- `/paper/{paper_id}/references`: Get references
- `/author/{author_id}`: Get author details

## Documentation
- [Semantic Scholar Graph API](https://www.semanticscholar.org/product/api)
