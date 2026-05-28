# API Endpoints

## Base URL
https://rest.ensembl.org

## Key Endpoints

### Lookup
- `GET /lookup/symbol/{species}/{symbol}`: Find objects by symbol.

### Sequence
- `GET /sequence/id/{id}`: Request sequence by stable identifier.

### VEP (Variant Effect Predictor)
- `GET /vep/{species}/hgvs/{hgvs}`: Fetch variant consequences.

## Rate Limiting
- Limit: 15 requests per second.
- The client handles HTTP 429 (Too Many Requests) retries automatically.
