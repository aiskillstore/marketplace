# Evaluation Checklist

## Functional Testing

### API Query
- [ ] Correctly retrieve facets (filtering criteria)
- [ ] Filter by organism
- [ ] Filter by tissue
- [ ] Filter by disease
- [ ] Filter by cell_type
- [ ] Combined filtering works correctly

### Output Format
- [ ] Correctly display dataset name
- [ ] Correctly display Accession
- [ ] Correctly display cell count
- [ ] Handle empty results

## Security Testing

- [ ] No hardcoded credentials
- [ ] Semantic error messages
- [ ] Access only official API endpoints
- [ ] No path traversal risks

## Performance Testing

- [ ] API response < 10 seconds
- [ ] No long-duration blocking

## Compatibility Testing

- [ ] Runs normally in Windows environment
- [ ] Requires only the requests library
- [ ] SSL certificate issues handled