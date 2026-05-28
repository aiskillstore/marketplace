# BioRxiv API Reference

## Overview
This skill interacts with the bioRxiv API to retrieve metadata about preprints.

## Endpoints

### Collection Details
**URL**: `https://api.biorxiv.org/details/biorxiv/{start_date}/{end_date}/{cursor}`

- **Method**: GET
- **Parameters**:
  - `start_date`: YYYY-MM-DD
  - `end_date`: YYYY-MM-DD
  - `cursor`: Integer (start at 0)
- **Response**: JSON object containing a `collection` list of paper metadata.

### Content Access (PDF)
**URL**: `https://www.biorxiv.org/content/{doi}v{version}.full.pdf`

- **Method**: GET
- **Description**: Direct link to the full-text PDF.
- **Note**: Requires valid DOI and version number (usually v1, v2, etc.).

## Limitations
- The API is primarily for metadata retrieval, not full-text search.
- Keyword filtering is performed client-side after fetching the collection.
