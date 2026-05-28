# ClinicalTrials.gov API v2 Reference

## Overview
The API v2 replaces the legacy XML API and provides JSON output.
Base URL: `https://clinicaltrials.gov/api/v2/studies`

## Endpoints

### GET /studies
Search for studies.

**Key Parameters:**
- `query.cond`: Search by condition (e.g., "cancer")
- `query.intr`: Search by intervention/drug (e.g., "aspirin")
- `filter.overallStatus`: Filter by status (e.g., "RECRUITING", "COMPLETED")
- `pageSize`: Number of results (default 10)
- `pageToken`: Token for pagination

### GET /studies/{nctId}
Retrieve a specific study.

**Fields:**
- `protocolSection`: Protocol details
- `identificationModule`: NCT ID, titles
- `statusModule`: Recruitment status
- `eligibilityModule`: Inclusion/exclusion criteria

## Rate Limits
- Approximately 50 requests per minute.
