# OpenAlex API Guide

## Core Concepts
- **Polite Pool**: Add email to User-Agent for 10x rate limits.
- **Inverted Index**: Search uses an inverted index for speed.
- **Concepts**: Hierarchical tagging system.

## Filters
Common filters:
- `is_oa`: "true" or "false" (Open Access)
- `publication_year`: e.g. `>2020`
- `cited_by_count`: e.g. `>100`

## Pagination
The API supports cursor-based pagination for large result sets.
See official documentation for details on cursor implementation.
