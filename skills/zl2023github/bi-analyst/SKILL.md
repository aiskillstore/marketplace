---
name: bi-analyst
category: software-engineering
description: BI/数据分析工程师 Agent — 覆盖数据采集、ETL、指标体系建设、可视化看板、专题分析、数据产品全流程。支持SQL查询、Python分析、BI工具集成、自动化报表、A/B测试分析。
---

# BI/数据分析工程师 Agent

## 触发条件

当用户提出以下需求时加载此技能：
- "分析XX数据"、"做个报表"、"搭个看板"
- "帮我查一下XX指标"、"做个数据透视"
- "数据清洗"、"ETL"、"数据仓库建模"
- "用户行为分析"、"漏斗分析"、"留存分析"
- "A/B测试分析"、"转化率分析"
- "自动化报表"、"数据可视化"
- 任何涉及SQL查询、数据聚合、图表生成的任务

## 核心工作流

### 1. 需求澄清阶段
先明确以下信息：
- **数据来源**：数据库（MySQL/PostgreSQL/ClickHouse等）、CSV/Excel文件、API、日志文件？
- **业务场景**：用户行为？经营分析？产品效果？渠道获客？
- **时间范围**：日/周/月/年？同比/环比？
- **输出形式**：报表/看板/PPT/PDF报告/临时查询？
- **受众**：业务方/管理层/技术团队？

### 2. 数据获取

**SQL查询（数据库场景）**
```sql
-- 典型查询模板：用户留存分析
SELECT 
    DATE(first_active) AS active_date,
    COUNT(DISTINCT user_id) AS new_users,
    COUNT(DISTINCT CASE WHEN DATEDIFF(login_date, first_active) = 1 THEN user_id END) AS day1_retained,
    COUNT(DISTINCT CASE WHEN DATEDIFF(login_date, first_active) = 7 THEN user_id END) AS day7_retained
FROM (
    SELECT 
        u.user_id,
        MIN(u.login_date) OVER (PARTITION BY u.user_id) AS first_active,
        u.login_date
    FROM user_login u
) t
WHERE login_date >= '2024-01-01'
GROUP BY first_active
ORDER BY first_active;
```

**CSV/Excel文件读取（Python）**
```python
import pandas as pd
df = pd.read_csv('data.csv')
# 或 pd.read_excel('data.xlsx', sheet_name='Sheet1')
```

### 2. 数据清洗与预处理

```python
import pandas as pd
import numpy as np

# 基础清洗
df = df.drop_duplicates()
df = df.dropna(subset=['关键字段'])
df['date'] = pd.to_datetime(df['date'])
df['amount'] = pd.to_numeric(df['amount'], errors='coerce')

# 异常值处理
df = df[df['amount'] > 0]  # 过滤负值
df['amount'].fillna(df['amount'].median(), inplace=True)

# 类型转换
df['category'] = df['category'].astype('category')
```

### 3. 指标计算

```python
# 留存分析
cohort = df.groupby('cohort_date').agg(
    new_users=('user_id', 'nunique'),
    day1_retention=('is_day1_active', 'mean'),
    day7_retention=('is_day7_active', 'mean'),
    day30_retention=('is_day30_active', 'mean')
)

# 漏斗分析
funnel = df.groupby('step').agg(
    users=('user_id', 'nunique'),
    conversion_rate=('converted', 'mean')
)
funnel['step_conversion'] = funnel['users'] / funnel['users'].shift(1)

# 同期群分析（Cohort Analysis）
cohort = df.groupby(['cohort_month', 'period']).agg(
    users=('user_id', 'nunique')
)
cohort['retention_rate'] = cohort.groupby(level=0)['users'].transform(
    lambda x: x / x.iloc[0]
)
```

### 4. 可视化与报表

**Python可视化（matplotlib/seaborn/plotly）**
```python
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# 折线图：趋势分析
plt.figure(figsize=(12, 6))
sns.lineplot(data=df, x='date', y='revenue', hue='channel')
plt.title('各渠道收入趋势')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('revenue_trend.png')

# 热力图：留存矩阵
pivot = df.pivot_table(index='cohort', columns='period', values='retention_rate')
sns.heatmap(pivot, annot=True, fmt='.1%', cmap='YlOrRd')
plt.title('留存热力图')
plt.tight_layout()
plt.savefig('retention_heatmap.png')

# 交互式图表（plotly）
fig = px.line(df, x='date', y='metric', color='dimension', title='指标趋势')
fig.write_html('interactive_chart.html')
```

**BI工具集成（Metabase/Superset）**
- 通过API或SQL查询引擎连接数据库
- 创建数据集 → 设计可视化 → 发布看板
- 设置定时刷新和预警规则

### 5. 专题分析模板

**用户留存分析**
```python
# 同期群留存
cohort_data = df.groupby(['cohort_date', 'period']).agg(
    users=('user_id', 'nunique')
).reset_index()
cohort_data['retention'] = cohort_data.groupby('cohort_date')['users'].transform(
    lambda x: x / x.iloc[0]
)
```

**漏斗分析**
```python
funnel_steps = ['曝光', '点击', '注册', '下单', '支付']
funnel_data = []
for step in funnel_steps:
    funnel_data.append({
        'step': step,
        'users': df[df['step_rank'] >= funnel_steps.index(step)]['user_id'].nunique()
    })
funnel_df = pd.DataFrame(funnel_data)
funnel_df['step_conversion'] = funnel_df['users'] / funnel_df['users'].shift(1)
funnel_df['overall_conversion'] = funnel_df['users'] / funnel_df['users'].iloc[0]
```

**A/B测试分析**
```python
from scipy import stats

# 假设检验
control = df[df['group'] == 'control']['conversion']
treatment = df[df['group'] == 'treatment']['conversion']

# Z检验 / t检验
stat, p_value = stats.ttest_ind(treatment, control)
# 或比例检验
from statsmodels.stats.proportion import proportions_ztest

# 效应量
from scipy.stats import chi2_contingency
```

### 5. 自动化报表

**Python脚本生成Excel报表**
```python
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

with pd.ExcelWriter('daily_report.xlsx', engine='openpyxl') as writer:
    summary_df.to_excel(writer, sheet_name='概览', index=False)
    detail_df.to_excel(writer, sheet_name='明细', index=False)
    funnel_df.to_excel(writer, sheet_name='漏斗分析', index=False)
```

**定时任务（cron）**
```bash
# 每天早8点运行报表
0 8 * * * cd /path/to/project && python daily_report.py
```

### 6. 数据仓库建模

**星型模型设计**
```sql
-- 事实表
CREATE TABLE fact_orders (
    order_id BIGINT,
    user_id BIGINT,
    product_id BIGINT,
    date_id INT,
    amount DECIMAL(10,2),
    quantity INT
);

-- 维度表
CREATE TABLE dim_user (
    user_id BIGINT PRIMARY KEY,
    register_date DATE,
    city VARCHAR(50),
    channel VARCHAR(50)
);

CREATE TABLE dim_product (
    product_id BIGINT PRIMARY KEY,
    product_name VARCHAR(100),
    category VARCHAR(50),
    price DECIMAL(10,2)
);

CREATE TABLE dim_date (
    date_id INT PRIMARY KEY,
    date DATE,
    year INT,
    month INT,
    day INT,
    weekday VARCHAR(10),
    is_holiday BOOLEAN
);
```

### 7. 自动化与调度

**Airflow DAG模板**
```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'analyst',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'daily_report',
    default_args=default_args,
    schedule_interval='0 8 * * *',  # 每天8点
    catchup=False
)

def generate_daily_report():
    # 1. 从数据库取数
    # 2. 计算指标
    # 3. 生成图表
    # 4. 发送邮件/推送
    pass

task = PythonOperator(
    task_id='run_daily_report',
    python_callable=generate_daily_report,
    dag=dag
)
```

### 8. 统计分析方法

```python
from scipy import stats
import statsmodels.api as sm

# A/B测试显著性检验
def ab_test_analysis(control_conv, treatment_conv, control_n, treatment_n):
    """两样本比例检验"""
    count = [treatment_conv, control_conv]
    nobs = [treatment_n, control_n]
    z_stat, p_value = statsmodels.stats.proportion.proportions_ztest(count, nobs)
    return z_stat, p_value

# 相关性分析
corr = df[['metric1', 'metric2', 'metric3']].corr()

# 回归分析
X = df[['feature1', 'feature2']]
X = sm.add_constant(X)
y = df['target']
model = sm.OLS(y, X).fit()
print(model.summary())
```

### 9. 报告输出

**Markdown报告**
```markdown
# 月度经营分析报告

## 核心指标概览
| 指标 | 本月 | 上月 | 环比 | 同比 |
|------|------|------|------|------|
| GMV | ¥1,200万 | ¥1,050万 | +14.3% | +25.0% |
| 活跃用户 | 85万 | 78万 | +9.0% | +18.1% |
| 转化率 | 3.2% | 3.0% | +0.2pp | +0.5pp |

## 关键发现
1. **增长亮点**：新渠道获客成本下降30%，ROI提升至4.5
2. **风险点**：老用户复购率连续3月下滑，需关注
3. **建议**：优化新用户引导流程，预计可提升次日留存5%
```

**PDF报告（fpdf2）**
- 参考 `chinese-pdf-generation` 技能生成含中文图表的PDF报告

### 10. 数据质量检查

```python
def data_quality_check(df):
    """数据质量检查"""
    report = {
        '行数': len(df),
        '列数': len(df.columns),
        '缺失值': df.isnull().sum().to_dict(),
        '缺失率': (df.isnull().sum() / len(df)).to_dict(),
        '重复行': df.duplicated().sum(),
        '数据类型': df.dtypes.to_dict(),
        '描述统计': df.describe().to_dict()
    }
    return report
```

## 常见场景与应对

### 场景1：临时取数需求
1. 确认业务口径（指标定义、时间范围、维度）
2. 编写SQL查询
3. 导出CSV或直接展示结果
4. 附上数据说明和口径注释

### 场景2：搭建业务看板
1. 梳理核心指标（北极星指标 + 过程指标）
2. 设计看板布局（概览层 → 分析层 → 明细层）
3. 确定刷新频率（实时/小时/天）
4. 设置异常预警阈值

### 场景3：异动归因分析
1. 确认异动指标和时间点
2. 拆解维度（地区/渠道/用户分层/产品线）
3. 计算各维度贡献度（贡献度 = 该维度变化量 / 总变化量）
4. 定位核心原因
5. 输出结论与建议

### 场景4：A/B测试分析
1. 确认实验分组和样本量
2. 计算核心指标（转化率、ARPU等）
3. 假设检验（t检验/Z检验/卡方检验）
4. 效应量评估
5. 结论：是否显著、是否值得全量上线

## 常用命令速查

```bash
# 数据库连接
mysql -h host -u user -p database
psql -h host -U user -d database

# CSV快速查看
head -20 data.csv | column -t -s ','
wc -l data.csv

# Python快速分析
python -c "
import pandas as pd
df = pd.read_csv('data.csv')
print(df.describe())
print(df.isnull().sum())
"
```

## 注意事项

- **数据安全**：永远不要将数据库密码、API密钥硬编码到脚本中；使用环境变量或配置文件
- **口径一致性**：同一指标在不同场景下口径必须一致，建立指标字典
- **数据量级**：大数据量优先在数据库层聚合（GROUP BY），不要全量拉到Python再处理
- **可视化原则**：一图一事，避免信息过载；折线图看趋势、柱状图看对比、饼图看占比（不超过5类）
- **统计陷阱**：注意辛普森悖论、幸存者偏差、对比基数差异
- **结果验证**：关键数据交叉验证（SQL取数结果与BI工具核对）
- **可复现性**：所有分析脚本化，避免手动操作

## 交付物模板

### 分析报告结构
1. **背景与目的** — 为什么要做这个分析
2. **数据说明** — 数据来源、时间范围、口径定义
3. **核心发现** — 3-5个关键结论，用数据说话
4. **详细分析** — 分维度拆解、图表支撑
5. **结论与建议** — 可落地的行动建议
6. **附录** — SQL脚本、数据字典

### 看板设计原则
- **第一屏**：北极星指标 + 核心KPI概览（6-8个关键数字）
- **第二屏**：趋势分析（日/周/月趋势图）
- **第三屏**：维度下钻（地区/渠道/产品线）
- **第四屏**：明细数据表（可搜索、可导出）

## 注意事项

- **数据安全**：永远不要将数据库密码、API密钥硬编码到脚本中；使用环境变量或配置文件
- **口径一致性**：同一指标在不同场景下口径必须一致，建立指标字典文档
- **数据量级**：大数据量优先在数据库层聚合（GROUP BY），不要全量拉到Python再处理
- **可视化原则**：一图一事，避免信息过载；折线图看趋势、柱状图看对比、饼图看占比（不超过5类）
- **统计陷阱**：注意辛普森悖论、幸存者偏差、对比基数差异
- **结果验证**：关键数据交叉验证（SQL取数结果与BI工具核对）
- **可复现性**：所有分析脚本化，避免手动操作
- **性能优化**：SQL查询加索引、避免SELECT *、合理使用分区表
