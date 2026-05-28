# Literature Search Evaluation Checklist

## Functional Testing

### 1. Keyword Extraction
- [ ] Can identify biomedical terms
- [ ] Can identify abbreviations (DNA, RNA, PCR)
- [ ] Stop words correctly filtered (the, and, of, for, with)
- [ ] Extracts 8 high-frequency words by default

### 2. Search Query Construction
- [ ] Title uses field restriction `[Title]`
- [ ] Keywords use `[Title/Abstract]`
- [ ] Multiple keywords connected using `AND`
- [ ] Error prompt on empty input

### 3. PubMed API Calls
- [ ] esearch returns valid PMID list
- [ ] esummary returns complete literature information
- [ ] Supports EMAIL parameter
- [ ] Supports API_KEY parameter

### 4. Result Parsing
- [ ] Correctly extracts PMID
- [ ] Correctly extracts title
- [ ] Correctly extracts journal name
- [ ] Correctly extracts publication year
- [ ] Correctly extracts author list

### 5. File Output
- [ ] JSON file format is correct
- [ ] CSV file format is correct
- [ ] Output directory created automatically
- [ ] File names comply with configuration

## Performance Testing

### 1. Response Time
- [ ] Single API request < 20 seconds
- [ ] Complete process < 1 minute

### 2. Stability
- [ ] Graceful degradation on network errors
- [ ] Handles empty input
- [ ] Handles special characters

## Security Testing

### 1. Path Access
- [ ] Only accesses pubmed.ncbi.nlm.nih.gov
- [ ] Does not access other URLs
- [ ] Does not write files outside the Skill directory

### 2. Credential Management
- [ ] EMAIL is not hard-coded
- [ ] API_KEY is not hard-coded
- [ ] Clear prompts in the configuration file

## Use Case Testing

### Scenario 1: Interactive Input
```bash
python scripts/pubmed_search.py
```
Expectation: Prompt for title and abstract

### Scenario 2: JSON Input
Configure `INPUT_JSON` as the JSON file path
Expectation: Automatically read title and abstract

### Scenario 3: Configuration Validation
- [ ] Prompt when EMAIL is not configured
- [ ] API_KEY is optional, does not affect basic functionality

## Acceptance Criteria

- [ ] All functional tests passed
- [ ] Performance is within acceptable range
- [ ] Security scan passed
- [ ] Consistent code style
- [ ] Complete documentation

## Known Limitations

1. Only supports PubMed database
2. Requires EMAIL for normal use
3. Does not support complex Boolean search queries
4. Does not support batch PMID queries

## Improvement Suggestions

1. Extend support for Scopus, Web of Science
2. Add search history records
3. Add deduplication functionality
4. Add literature filters