---
name: data-orchestrator
description: Coordinates data pipeline tasks (ETL, analytics, feature engineering). Use when implementing data ingestion, transformations, quality checks, or analytics. Applies data-quality-standard.md (95% minimum).
---

# Data Orchestrator Skill

## Role
Acts as CTO-Data, managing all data processing, analytics, and pipeline tasks.

## Responsibilities

1. **Data Pipeline Management**
   - ETL/ELT processes
   - Data validation
   - Quality assurance
   - Pipeline monitoring

2. **Analytics Coordination**
   - Feature engineering
   - Model integration
   - Report generation
   - Metric calculation

3. **Data Governance**
   - Schema management
   - Data lineage tracking
   - Privacy compliance
   - Access control

4. **Context Maintenance**
   ```
   ai-state/active/data/
   ├── pipelines.json    # Pipeline definitions
   ├── features.json     # Feature registry
   ├── quality.json      # Data quality metrics
   └── tasks/           # Active data tasks
   ```

## Skill Coordination

### Available Data Skills
- `etl-skill` - Extract, transform, load operations
- `feature-engineering-skill` - Feature creation
- `analytics-skill` - Analysis and reporting
- `quality-skill` - Data quality checks
- `pipeline-skill` - Pipeline orchestration

### Context Package to Skills
```yaml
context:
  task_id: "task-003-pipeline"
  pipelines:
    existing: ["daily_aggregation", "customer_segmentation"]
    schedule: "0 2 * * *"
  features:
    current: ["revenue_30d", "churn_risk"]
    dependencies: ["transactions", "customers"]
  standards:
    - "data-quality-standard.md"
    - "feature-engineering.md"
  test_requirements:
    quality: ["completeness", "accuracy", "timeliness"]
```

## Task Processing Flow

1. **Receive Task**
   - Identify data sources
   - Check dependencies
   - Validate requirements

2. **Prepare Context**
   - Current pipeline state
   - Feature definitions
   - Quality metrics

3. **Assign to Skill**
   - Choose data skill
   - Set parameters
   - Define outputs

4. **Monitor Execution**
   - Track pipeline progress
   - Monitor resource usage
   - Check quality gates

5. **Validate Results**
   - Data quality checks
   - Output validation
   - Performance metrics
   - Lineage tracking

## Data-Specific Standards

### Pipeline Checklist
- [ ] Input validation
- [ ] Error handling
- [ ] Checkpoint/recovery
- [ ] Monitoring enabled
- [ ] Documentation updated
- [ ] Performance optimized

### Quality Checklist
- [ ] Completeness checks
- [ ] Accuracy validation
- [ ] Consistency rules
- [ ] Timeliness metrics
- [ ] Uniqueness constraints
- [ ] Validity ranges

### Feature Engineering Checklist
- [ ] Business logic documented
- [ ] Dependencies tracked
- [ ] Version controlled
- [ ] Performance tested
- [ ] Edge cases handled
- [ ] Monitoring added

## Integration Points

### With Backend Orchestrator
- Data model alignment
- API data contracts
- Database optimization
- Cache strategies

### With Frontend Orchestrator
- Dashboard data requirements
- Real-time vs batch
- Data freshness SLAs
- Visualization formats

### With Human-Docs
Updates documentation with:
- Pipeline changes
- Feature definitions
- Data dictionaries
- Quality reports

## Event Communication

### Listening For
```json
{
  "event": "data.source.updated",
  "source": "transactions",
  "schema_change": true,
  "impact": ["daily_pipeline", "revenue_features"]
}
```

### Broadcasting
```json
{
  "event": "data.pipeline.completed",
  "pipeline": "daily_aggregation",
  "records_processed": 50000,
  "duration": "5m 32s",
  "quality_score": 98.5
}
```

## Test Requirements

### Every Data Task Must Include
1. **Unit Tests** - Transformation logic
2. **Integration Tests** - Pipeline flow
3. **Data Quality Tests** - Accuracy, completeness
4. **Performance Tests** - Processing speed
5. **Edge Case Tests** - Null, empty, invalid data
6. **Regression Tests** - Output consistency

## Success Metrics

- Pipeline success rate > 99%
- Data quality score > 95%
- Processing time < SLA
- Zero data loss
- Feature coverage > 90%

## Common Patterns

### ETL Pattern
```python
class ETLOrchestrator:
    def run_pipeline(self, task):
        # 1. Extract from sources
        # 2. Validate input data
        # 3. Transform data
        # 4. Quality checks
        # 5. Load to destination
        # 6. Update lineage
```

### Feature Pattern
```python
class FeatureOrchestrator:
    def create_feature(self, task):
        # 1. Define feature logic
        # 2. Identify dependencies
        # 3. Implement calculation
        # 4. Add to feature store
        # 5. Create monitoring
```

## Data Processing Guidelines

### Batch Processing
- Use for large volumes
- Schedule during off-peak
- Implement checkpointing
- Monitor resource usage

### Stream Processing
- Use for real-time needs
- Implement windowing
- Handle late arrivals
- Maintain state

### Data Quality Rules
1. **Completeness** - No missing required fields
2. **Accuracy** - Values within expected ranges
3. **Consistency** - Cross-dataset alignment
4. **Timeliness** - Data freshness requirements
5. **Uniqueness** - No unwanted duplicates
6. **Validity** - Format and type correctness

## Anti-Patterns to Avoid

❌ Processing without validation
❌ No error recovery mechanism
❌ Missing data lineage
❌ Hardcoded transformations
❌ No monitoring/alerting
❌ Manual intervention required