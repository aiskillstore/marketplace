# Sigma Backend Support Reference

## Supported SIEM/Security Platforms

### Splunk

**Backend**: `splunk`

**Query Language**: SPL (Search Processing Language)

**Installation**:
```bash
pip install pysigma-backend-splunk
```

**Conversion Example**:
```bash
python scripts/sigma_convert.py rule.yml --backend splunk
```

**Output Format**:
```spl
index=windows EventID=4688 Image="*\\powershell.exe" CommandLine IN ("*-enc*", "*-EncodedCommand*", "*FromBase64String*")
```

**Deployment**:
- Save as saved search via Splunk Web UI
- Deploy via REST API: `/servicesNS/-/-/saved/searches`
- Use Splunk Enterprise Security correlation rules

**Field Mappings**:
- Sigma `Image` → Splunk `Image` (Sysmon)
- Sigma `CommandLine` → Splunk `CommandLine`
- Sigma `User` → Splunk `User`

### Elasticsearch

**Backend**: `elasticsearch` or `elastic`

**Query Language**: Elasticsearch Query DSL / Lucene

**Installation**:
```bash
pip install pysigma-backend-elasticsearch
```

**Conversion Example**:
```bash
python scripts/sigma_convert.py rule.yml --backend elasticsearch
```

**Output Format**:
```json
{
  "query": {
    "bool": {
      "must": [
        {"wildcard": {"Image": "*\\powershell.exe"}},
        {"terms": {"CommandLine": ["-enc", "-EncodedCommand"]}}
      ]
    }
  }
}
```

**Deployment**:
- Elastic Security Detection Rules
- Kibana Saved Searches
- ElastAlert rules

**Field Mappings** (ECS - Elastic Common Schema):
- Sigma `Image` → ECS `process.executable`
- Sigma `CommandLine` → ECS `process.command_line`
- Sigma `User` → ECS `user.name`

### Microsoft Sentinel (Azure Sentinel)

**Backend**: `sentinel` or `kusto`

**Query Language**: KQL (Kusto Query Language)

**Installation**:
```bash
pip install pysigma-backend-microsoft365defender
```

**Conversion Example**:
```bash
python scripts/sigma_convert.py rule.yml --backend sentinel
```

**Output Format**:
```kql
SecurityEvent
| where EventID == 4688
| where ProcessName endswith "\\powershell.exe"
| where CommandLine contains "-enc" or CommandLine contains "-EncodedCommand"
```

**Deployment**:
- Azure Sentinel Analytics Rules
- Deploy via ARM templates
- Use Azure Sentinel API

**Field Mappings**:
- Sigma `Image` → Sentinel `ProcessName`
- Sigma `CommandLine` → Sentinel `CommandLine`
- Sigma `User` → Sentinel `AccountName`

### IBM QRadar

**Backend**: `qradar` or `aql`

**Query Language**: AQL (Ariel Query Language)

**Installation**:
```bash
pip install pysigma-backend-qradar
```

**Conversion Example**:
```bash
python scripts/sigma_convert.py rule.yml --backend qradar
```

**Output Format**:
```sql
SELECT * FROM events WHERE LOGSOURCETYPENAME(devicetype) = 'Microsoft Windows Security Event Log'
AND "EventID" = '4688'
AND "Image" ILIKE '%\\powershell.exe'
```

**Deployment**:
- QRadar Custom Rules
- Deploy via QRadar API
- AQL searches

### Elastic Security (EQL)

**Backend**: `eql`

**Query Language**: EQL (Event Query Language)

**Conversion Example**:
```bash
python scripts/sigma_convert.py rule.yml --backend eql
```

**Output Format**:
```eql
process where process.name == "powershell.exe" and
  (process.command_line like~ "*-enc*" or
   process.command_line like~ "*-EncodedCommand*")
```

**Deployment**:
- Elastic Security Detection Rules
- EQL searches in Kibana

### Chronicle (Google)

**Backend**: `chronicle`

**Query Language**: YARA-L

**Conversion Example**:
```bash
python scripts/sigma_convert.py rule.yml --backend chronicle
```

### Others

Additional backends available via pySigma plugins:

- **LimaCharlie**: EDR platform
- **OpenSearch**: Fork of Elasticsearch
- **LogPoint**: SIEM platform
- **ArcSight**: SIEM platform
- **Carbon Black**: EDR platform
- **CrowdStrike**: EDR platform (Falcon)
- **SentinelOne**: EDR platform
- **Datadog**: Cloud monitoring platform
- **Sumo Logic**: Cloud SIEM

## Backend Installation

### Core pySigma

```bash
pip install pysigma
```

### Backend Plugins

```bash
# Splunk
pip install pysigma-backend-splunk

# Elasticsearch
pip install pysigma-backend-elasticsearch

# Microsoft 365 Defender / Sentinel
pip install pysigma-backend-microsoft365defender

# QRadar
pip install pysigma-backend-qradar

# Multiple backends
pip install pysigma-backend-splunk pysigma-backend-elasticsearch
```

## Backend Limitations

### Field Mapping Gaps

Some backends may not support all Sigma field modifiers:

**Issue**: Backend doesn't support regex field modifier `|re`

**Solution**:
- Use alternative field modifiers (`contains`, `endswith`)
- Implement custom pipeline transformations
- Post-process in SIEM after conversion

### Unsupported Features

| Feature | Splunk | Elasticsearch | Sentinel | QRadar |
|---------|--------|---------------|----------|--------|
| Regex | ✓ | ✓ | ✓ | ✓ |
| Base64 decode | Limited | Limited | ✓ | Limited |
| CIDR matching | ✓ | ✓ | ✓ | ✓ |
| Wildcards | ✓ | ✓ | ✓ | ✓ |

### Data Source Availability

Not all log sources may be available in all backends:

**Check availability**:
1. Verify log source is ingested in your SIEM
2. Confirm field mappings match
3. Test converted query with sample data

## Custom Pipelines

pySigma supports custom processing pipelines for field transformations:

```python
from sigma.pipelines.sysmon import sysmon_pipeline
from sigma.backends.splunk import SplunkBackend

# Apply Sysmon field mappings before conversion
backend = SplunkBackend()
pipeline = sysmon_pipeline()
converted = backend.convert_rule(rule, pipeline)
```

## Deployment Automation

### Splunk Deployment

```python
import requests

# Splunk REST API
url = "https://splunk:8089/servicesNS/nobody/search/saved/searches"
auth = ("admin", "password")

data = {
    "name": "Sigma - Suspicious PowerShell",
    "search": converted_query,
    "description": rule.description,
    "cron_schedule": "*/5 * * * *",  # Every 5 minutes
    "actions": "email",
    "action.email.to": "soc@company.com"
}

response = requests.post(url, auth=auth, data=data, verify=False)
```

### Elasticsearch Deployment

```python
from elasticsearch import Elasticsearch

es = Elasticsearch(["https://elasticsearch:9200"])

# Deploy as Elasticsearch detection rule
rule_doc = {
    "name": rule.title,
    "description": rule.description,
    "query": converted_query,
    "severity": rule.level,
    "tags": rule.tags
}

es.index(index="detection-rules", document=rule_doc)
```

### Microsoft Sentinel Deployment

```bash
# ARM template deployment
az sentinel alert-rule create \
  --resource-group myResourceGroup \
  --workspace-name mySentinelWorkspace \
  --rule-name "Sigma - Suspicious PowerShell" \
  --query "$converted_query" \
  --severity Medium \
  --enabled true
```

## Testing Converted Queries

### Splunk

```spl
# Test in Splunk search
index=windows earliest=-24h
| eval match=case(
    Image="*\\powershell.exe" AND (CommandLine LIKE "%enc%" OR CommandLine LIKE "%EncodedCommand%"), "MATCH",
    1=1, "NO MATCH"
  )
| stats count by match
```

### Elasticsearch

```json
POST /winlogbeat-*/_search
{
  "query": {
    "bool": {
      "must": [
        {"wildcard": {"process.executable": "*\\powershell.exe"}},
        {"terms": {"process.command_line": ["-enc", "-EncodedCommand"]}}
      ]
    }
  }
}
```

### Sentinel

```kql
SecurityEvent
| where TimeGenerated > ago(24h)
| where EventID == 4688
| where ProcessName endswith "\\powershell.exe"
| summarize count() by bin(TimeGenerated, 1h)
```

## Troubleshooting

### Conversion Fails

**Error**: `Unsupported field modifier for backend`

**Solution**:
```bash
# Use debug mode to see detailed error
python scripts/sigma_convert.py rule.yml --backend splunk --debug
```

Check `references/field-modifiers.md` for backend compatibility.

### Query Doesn't Return Expected Results

**Steps**:
1. Verify log source is ingested
2. Check field name mappings
3. Test with known-positive sample
4. Validate field value case sensitivity
5. Check time range in query

### Performance Issues

Large, complex queries may impact SIEM performance:

**Optimization**:
- Add index/sourcetype filters early
- Use specific time ranges
- Optimize field modifiers (prefer exact match over regex)
- Test query performance before deployment

## Resources

- [pySigma Documentation](https://github.com/SigmaHQ/pySigma)
- [pySigma Backend Plugins](https://github.com/SigmaHQ/pySigma/blob/main/Backends.md)
- [Sigma Converter Web Tool](https://sigconverter.io/)
- [Sigma GitHub Repository](https://github.com/SigmaHQ/sigma)
