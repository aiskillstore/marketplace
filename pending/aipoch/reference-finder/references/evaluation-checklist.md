# Reference Finder Evaluation Checklist

## Functional Testing

### 1. Keyword Extraction
- [ ] Can identify biomedical terms (CRISPR-Cas9, DNA, RNA)
- [ ] Can identify abbreviations (PCR, ELISA)
- [ ] Can identify enzymes (kinase, phosphatase)
- [ ] Uses general vocabulary when no keywords are found

### 2. PubMed Search
- [ ] Can connect to PubMed API
- [ ] Returns valid PMID list
- [ ] Supports multiple result returns
- [ ] Handles cases with no search results

### 3. Literature Detail Retrieval
- [ ] Can parse XML responses
- [ ] Correctly extracts PMID
- [ ] Correctly extracts Title
- [ ] Correctly extracts DOI
- [ ] Correctly extracts Publication Year

### 4. Relevance Ranking
- [ ] Keyword matches receive positive scores
- [ ] Literature from the last 5 years receives bonus points
- [ ] Can sort by score

### 5. Sentence Processing
- [ ] Can split sentences (. ! ?)
- [ ] Can handle multi-line text
- [ ] Can deduplicate references

## Performance Testing

### 1. Response Time
- [ ] API requests < 30 seconds
- [ ] Overall processing < 2 minutes

### 2. Stability
- [ ] Graceful degradation during network errors
- [ ] Handles empty input
- [ ] Can handle special characters

## Security Testing

### 1. Path Access
- [ ] Only accesses pubmed.ncbi.nlm.nih.gov
- [ ] Does not access other URLs
- [ ] Does not write to sensitive files

### 2. Injection Protection
- [ ] Input is escaped/sanitized
- [ ] Secure XML parsing

## Use Case Testing

### Scenario 1: Single Sentence Query
```bash
python scripts/find_refs.py "CRISPR-Cas9 enables precise genome editing."
```
Expectation: Returns 3 relevant references

### Scenario 2: Multi-sentence Query
```bash
python scripts/find_refs.py "CRISPR-Cas9 is powerful. mRNA vaccines are effective."
```
Expectation: Returns 5-6 references (may contain duplicates)

### Scenario 3: Interactive Mode
```bash
python scripts/find_refs.py
```
Expectation: Prompts for input, supports Enter to use example

## Acceptance Criteria

- [ ] All functional tests passed
- [ ] Offline/No-network test passed
- [ ] Performance within acceptable range
- [ ] Security scan passed
- [ ] Consistent code style
- [ ] Complete documentation

## Known Limitations

1. Does not use external libraries (urllib vs requests)
2. Does not support complex Boolean searches
3. Does not access paid databases
4. API has rate limits

## Improvement Suggestions

1. Optional support for the requests library
2. Add citation count retrieval
3. Add abstract extraction
4. Add result export functionality