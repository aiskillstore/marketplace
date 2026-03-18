---
name: looker-studio-bigquery
description: Design and configure Looker Studio dashboards with BigQuery data sources. Use when creating analytics dashboards, connecting BigQuery to visualization tools, or optimizing data pipeline performance. Handles BigQuery connections, custom SQL queries, scheduled queries, dashboard design, and performance optimization.
metadata:
  tags: Looker-Studio, BigQuery, dashboard, analytics, visualization, GCP, data-studio, SQL
  platforms: Claude, ChatGPT, Gemini
---


# Looker Studio BigQuery Integration

## When to use this skill

- **Analytics dashboard creation**: Visualizing BigQuery data to derive business insights
- **Real-time reporting**: Building auto-refreshing dashboards
- **Performance optimization**: Optimizing query costs and loading time for large datasets
- **Data pipeline**: Automating ETL processes with scheduled queries
- **Team collaboration**: Building shareable interactive dashboards

## Instructions

### Step 1: Prepare GCP BigQuery Environment

**Project creation and activation**

Create a new project in Google Cloud Console and enable the BigQuery API.

```bash
# Create project using gcloud CLI
gcloud projects create my-analytics-project
gcloud config set project my-analytics-project
gcloud services enable bigquery.googleapis.com
```

**Create dataset and table**

```sql
-- Create dataset
CREATE SCHEMA `my-project.analytics_dataset`
  OPTIONS(
    description="Analytics dataset",
    location="US"
  );

-- Create example table (GA4 data)
CREATE TABLE `my-project.analytics_dataset.events` (
  event_date DATE,
  event_name STRING,
  user_id INT64,
  event_value FLOAT64,
  event_timestamp TIMESTAMP,
  geo_country STRING,
  device_category STRING
);
```

**IAM permission configuration**

Grant IAM permissions so Looker Studio can access BigQuery:

| Role | Description |
|------|------|
| `BigQuery Data Viewer` | Table read permission |
| `BigQuery User` | Query execution permission |
| `BigQuery Job User` | Job execution permission |

### Step 2: Connecting BigQuery in Looker Studio

**Using native BigQuery connector (recommended)**

1. On Looker Studio homepage, click **+ Create** → **Data Source**
2. Search for "BigQuery" and select Google BigQuery connector
3. Authenticate with Google account
4. Select project, dataset, and table
5. Click **Connect** to create data source

**Custom SQL query approach**

Write SQL directly when complex data transformation is needed:

```sql
SELECT
  event_date,
  event_name,
  COUNT(DISTINCT user_id) as unique_users,
  SUM(event_value) as total_revenue,
  AVG(event_value) as avg_revenue_per_event
FROM `my-project.analytics_dataset.events`
WHERE event_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
GROUP BY event_date, event_name
ORDER BY event_date DESC
```

**Advantages:**
- Handle complex data transformations in SQL
- Pre-aggregate data in BigQuery to reduce query costs
- Improved performance by not loading all data every time

**Multiple table join approach**

```sql
SELECT
  e.event_date,
  e.event_name,
  u.user_country,
  u.user_tier,
  COUNT(DISTINCT e.user_id) as unique_users,
  SUM(e.event_value) as revenue
FROM `my-project.analytics_dataset.events` e
LEFT JOIN `my-project.analytics_dataset.users` u
  ON e.user_id = u.user_id
WHERE e.event_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
GROUP BY e.event_date, e.event_name, u.user_country, u.user_tier
```

### Step 3: Performance Optimization with Scheduled Queries

Use **scheduled queries** instead of live queries to periodically pre-compute data:

```sql
-- Calculate and store aggregated data daily in BigQuery
CREATE OR REPLACE TABLE `my-project.analytics_dataset.daily_summary` AS
SELECT
  CURRENT_DATE() as report_date,
  event_name,
  user_country,
  COUNT(DISTINCT user_id) as daily_users,
  SUM(event_value) as daily_revenue,
  AVG(event_value) as avg_event_value,
  MAX(event_timestamp) as last_event_time
FROM `my-project.analytics_dataset.events`
WHERE event_date = CURRENT_DATE() - 1
GROUP BY event_name, user_country
```

Configure as **scheduled query** in BigQuery UI:
- Runs automatically daily
- Saves results to a new table
- Looker Studio connects to the pre-computed table

**Advantages:**
- Reduce Looker Studio loading time (50-80%)
- Reduce BigQuery costs (less data scanned)
- Improved dashboard refresh speed

### Step 4: Dashboard Layout Design

**F-pattern layout**

Use the F-pattern that follows the natural reading flow of users:

```
┌─────────────────────────────────────┐
│ Header: Logo | Filters/Date Picker  │  ← Users see this first
├─────────────────────────────────────┤
│ KPI 1  │ KPI 2  │ KPI 3  │ KPI 4   │  ← Key metrics (3-4)
├─────────────────────────────────────┤
│                                     │
│ Main Chart (time series/comparison) │  ← Deep insights
│                                     │
├─────────────────────────────────────┤
│ Concrete data table                 │  ← Detailed analysis
│ (Drilldown enabled)                 │
├─────────────────────────────────────┤
│ Additional Insights / Map / Heatmap │
└─────────────────────────────────────┘
```

**Dashboard components**

| Element | Purpose | Example |
|---------|------|------|
| **Header** | Dashboard title, logo, filter placement | "2026 Q1 Sales Analysis" |
| **KPI tiles** | Display key metrics at a glance | Total revenue, MoM growth rate, active users |
| **Trend charts** | Changes over time | Line chart showing daily/weekly revenue trend |
| **Comparison charts** | Compare across categories | Bar chart comparing sales by region/product |
| **Distribution charts** | Visualize data distribution | Heatmap, scatter plot, bubble chart |
| **Detail tables** | Provide exact figures | Conditional formatting to highlight thresholds |
| **Map** | Geographic data | Revenue distribution by country/region |

**Real example: E-commerce dashboard**

```
┌──────────────────────────────────────────────────┐
│ 📊 Jan 2026 Sales Analysis | 🔽 Country | 📅 Date │
├──────────────────────────────────────────────────┤
│ Total Revenue: $125,000  │ Orders: 3,200   │ Conversion: 3.5% │
├──────────────────────────────────────────────────┤
│         Daily Revenue Trend (Line Chart)          │
│    ↗ Upward trend: +15% vs last month             │
├──────────────────────────────────────────────────┤
│ Sales by Category  │  Top 10 Products             │
│ (Bar chart)        │  (Table, sortable)           │
├──────────────────────────────────────────────────┤
│        Revenue Distribution by Region (Map)       │
└──────────────────────────────────────────────────┘
```

### Step 5: Interactive Filters and Controls

**Filter types**

**1. Date range filter** (required)
- Select specific period via calendar
- Pre-defined options like "Last 7 days", "This month"
- Connected to dataset, auto-applied to all charts

**2. Dropdown filter**
```
Example: Country selection filter
- All countries
- South Korea
- Japan
- United States
Shows only data for the selected country
```

**3. Advanced filter** (SQL-based)
```sql
-- Show only customers with revenue >= $10,000
WHERE customer_revenue >= 10000
```

**Filter implementation example**

```sql
-- 1. Date filter
event_date >= DATE_SUB(CURRENT_DATE(), INTERVAL @date_range_days DAY)

-- 2. Dropdown filter (user input)
WHERE country = @selected_country

-- 3. Composite filter
WHERE event_date >= @start_date
  AND event_date <= @end_date
  AND country IN (@country_list)
  AND revenue >= @min_revenue
```

### Step 6: Query Performance Optimization

**1. Using partition keys**

```sql
-- ❌ Inefficient query
SELECT * FROM events
WHERE DATE(event_timestamp) >= '2026-01-01'

-- ✅ Optimized query (using partition)
SELECT * FROM events
WHERE event_date >= '2026-01-01'  -- use partition key directly
```

**2. Data extraction (Extract and Load)**

Extract data to a Looker Studio-dedicated table each night:

```sql
-- Scheduled query running at midnight every day
CREATE OR REPLACE TABLE `my-project.looker_studio_data.dashboard_snapshot` AS
SELECT
  event_date,
  event_name,
  country,
  device_category,
  COUNT(DISTINCT user_id) as users,
  SUM(event_value) as revenue,
  COUNT(*) as events
FROM `my-project.analytics_dataset.events`
WHERE event_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
GROUP BY event_date, event_name, country, device_category;
```

**3. Caching strategy**

- **Looker Studio default caching**: Automatically caches for 3 hours
- **BigQuery caching**: Identical queries reuse previous results (6 hours)
- **Utilizing scheduled queries**: Pre-compute at night

**4. Dashboard complexity management**

- Use a maximum of 20-25 charts per dashboard
- Distribute across multiple tabs (pages) if many charts
- Do not group unrelated metrics together

### Step 7: Community Connector Development (Advanced)

Develop a Community Connector for more complex requirements:

```javascript
// Community Connector example (Apps Script)
function getConfig() {
  return {
    configParams: [
      {
        name: 'project_id',
        displayName: 'BigQuery Project ID',
        helpText: 'Your GCP Project ID',
        placeholder: 'my-project-id'
      },
      {
        name: 'dataset_id',
        displayName: 'Dataset ID'
      }
    ]
  };
}

function getData(request) {
  const projectId = request.configParams.project_id;
  const datasetId = request.configParams.dataset_id;

  // Load data from BigQuery
  const bq = BigQuery.newDataset(projectId, datasetId);
  // ... Data processing logic

  return { rows: data };
}
```

**Community Connector advantages:**
- Centralized billing (using service account)
- Custom caching logic
- Pre-defined query templates
- Parameterized user settings

### Step 8: Security and Access Control

**BigQuery-level security**

```sql
-- Grant table access permission to specific users only
GRANT `roles/bigquery.dataViewer`
ON TABLE `my-project.analytics_dataset.events`
TO "user@example.com";

-- Row-Level Security
CREATE OR REPLACE ROW ACCESS POLICY rls_by_country
ON `my-project.analytics_dataset.events`
GRANT ('editor@company.com') TO ('KR'),
      ('viewer@company.com') TO ('US', 'JP');
```

**Looker Studio-level security**

- Set viewer permissions when sharing dashboards (Viewer/Editor)
- Share with specific users/groups only
- Manage permissions per data source

## Output format

### Dashboard Setup Checklist

```markdown
## Dashboard Setup Checklist

### Data Source Configuration
- [ ] BigQuery project/dataset prepared
- [ ] IAM permissions configured
- [ ] Scheduled queries configured (performance optimization)
- [ ] Data source connection tested

### Dashboard Design
- [ ] F-pattern layout applied
- [ ] KPI tiles placed (3-4)
- [ ] Main charts added (trend/comparison)
- [ ] Detail table included
- [ ] Interactive filters added

### Performance Optimization
- [ ] Partition key usage verified
- [ ] Query cost optimized
- [ ] Caching strategy applied
- [ ] Chart count verified (20-25 or fewer)

### Sharing and Security
- [ ] Access permissions configured
- [ ] Data security reviewed
- [ ] Sharing link created
```

## Constraints

### Mandatory Rules (MUST)

1. **Date filter required**: Include date range filter in all dashboards
2. **Use partitions**: Directly use partition keys in BigQuery queries
3. **Permission separation**: Clearly configure access permissions per data source

### Prohibited (MUST NOT)

1. **Excessive charts**: Do not place more than 25 charts on a single dashboard
2. **SELECT ***: Select only necessary columns instead of all columns
3. **Overusing live queries**: Avoid directly connecting to large tables

## Best practices

| Item | Recommendation |
|------|---------|
| **Data refresh** | Use scheduled queries, run at night |
| **Dashboard size** | Max 25 charts, distribute to multiple pages if needed |
| **Filter configuration** | Date filter required, limit to 3-5 additional filters |
| **Color palette** | Use only 3-4 company brand colors |
| **Title/Labels** | Use clear descriptions for intuitiveness |
| **Chart selection** | Place in order: KPI → Trend → Comparison → Detail |
| **Response speed** | Target average loading within 2-3 seconds |
| **Cost management** | Keep monthly BigQuery scanned data within 5TB |

## References

- [Looker Studio Help](https://support.google.com/looker-studio)
- [BigQuery Documentation](https://cloud.google.com/bigquery/docs)
- [Connect to BigQuery](https://cloud.google.com/looker/docs/studio/connect-to-google-bigquery)
- [Community Connectors](https://developers.google.com/looker-studio/connector)
- [Dashboard Design Best Practices](https://lookercourses.com/dashboard-design-tips-for-looker-studio-how-to-build-clear-effective-reports/)

## Metadata

### Version
- **Current Version**: 1.0.0
- **Last Updated**: 2026-01-14
- **Compatible Platforms**: Claude, ChatGPT, Gemini

### Related Skills
- [monitoring-observability](../monitoring-observability/SKILL.md): Data collection and monitoring
- [database-schema-design](../../backend/database-schema-design/SKILL.md): Data modeling

### Tags
`#Looker-Studio` `#BigQuery` `#dashboard` `#analytics` `#visualization` `#GCP`

## Examples

### Example 1: Creating a Basic Dashboard

```sql
-- 1. Create daily summary table
CREATE OR REPLACE TABLE `my-project.looker_data.daily_metrics` AS
SELECT
  event_date,
  COUNT(DISTINCT user_id) as dau,
  SUM(revenue) as total_revenue,
  COUNT(*) as total_events
FROM `my-project.analytics.events`
WHERE event_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
GROUP BY event_date;

-- 2. Connect to this table in Looker Studio
-- 3. Add KPI scorecards: DAU, total revenue
-- 4. Visualize daily trend with line chart
```

### Example 2: Advanced Analytics Dashboard

```sql
-- Prepare data for cohort analysis
CREATE OR REPLACE TABLE `my-project.looker_data.cohort_analysis` AS
WITH user_cohort AS (
  SELECT
    user_id,
    DATE_TRUNC(MIN(event_date), WEEK) as cohort_week
  FROM `my-project.analytics.events`
  GROUP BY user_id
)
SELECT
  uc.cohort_week,
  DATE_DIFF(e.event_date, uc.cohort_week, WEEK) as week_number,
  COUNT(DISTINCT e.user_id) as active_users
FROM `my-project.analytics.events` e
JOIN user_cohort uc ON e.user_id = uc.user_id
GROUP BY cohort_week, week_number
ORDER BY cohort_week, week_number;
```
