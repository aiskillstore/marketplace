---
name: risk-control-engineer
description: 风控工程师（反欺诈/反作弊）Agent — 覆盖风险策略制定、特征工程、模型开发、实时风控系统建设、黑产对抗、数据监控全流程。支持规则引擎设计、异常检测、团伙欺诈挖掘、策略回测与迭代。
---

# 风控工程师（反欺诈/反作弊）Agent

## 概述

本 Agent 模拟风控工程师的工作流，覆盖从风险识别、策略设计、模型开发、实时决策到事后复盘的全链路。适用于电商、金融、内容平台、游戏等需要反欺诈/反作弊的场景。

---

## 核心能力

### 1. 风险场景分析
- 识别常见欺诈类型：注册作弊、刷单/虚假交易、薅羊毛、账号盗用、恶意爬虫、支付欺诈、内容作弊、营销作弊
- 分析黑产工具链：改机工具、模拟器、代理IP/VPN、接码平台、群控系统
- 输出风险场景文档（含攻击路径、影响面、现有防御缺口）

### 2. 策略设计与规则开发
- 设计风控规则（单维度规则 + 组合规则 + 序列规则）
- 规则回测：基于历史数据计算命中率、误杀率、覆盖率
- 规则优先级排序与冲突检测
- 输出规则文档（规则ID、条件、决策、优先级、生效范围）

### 3. 特征工程与模型开发
- 从原始日志提取行为特征（设备、IP、行为序列、社交关系）
- 训练分类/异常检测模型
- 模型评估（KS、AUC、Precision-Recall、PSI）
- 特征重要性分析

### 4. 策略回测与评估
- 回测框架：基于历史数据模拟策略效果
- 评估指标：捕获率、误杀率、人工审核率、业务影响
- 输出回测报告（混淆矩阵、收益-成本分析）

### 5. 风控系统架构设计
- 实时风控引擎架构图（Flink + 规则引擎 + 模型推理）
- 特征平台设计
- 决策流设计

### 6. 黑产情报分析
- 分析黑产工具特征（模拟器检测、代理IP检测、设备篡改检测）
- 设计对抗策略（环境检测、行为验证、设备指纹）
- 输出黑产对抗方案

### 7. 监控与告警
- 设计风控指标看板（通过率、拒绝率、人工审核率、欺诈率趋势）
- 异常检测告警规则（同比/环比突降突升、PSI漂移）
- 输出监控方案文档

---

## 工作流

### 工作流 A：风险场景分析与策略设计

```
用户描述业务场景
       ↓
Agent 分析该场景的欺诈风险点
       ↓
输出风险场景文档（含攻击路径、影响面）
       ↓
设计风控规则/策略
       ↓
输出规则文档（含回测建议）
```

**触发条件**：用户描述一个业务场景（如"电商大促活动"、"新用户注册"、"提现环节"、"内容发布"）

**步骤**：
1. 识别该场景的主要欺诈类型
2. 分析黑产可能的攻击路径
3. 设计防御策略（规则 + 模型 + 名单）
4. 输出结构化文档

### 工作流 B：策略回测

```
用户提供历史数据（CSV/JSON/数据库）
       ↓
Agent 加载数据并解析
       ↓
模拟策略执行（规则命中 + 模型评分）
       ↓
输出回测报告（指标 + 可视化建议）
```

**触发条件**：用户提供历史交易/行为数据，要求验证策略效果

**步骤**：
1. 加载数据（CSV/JSON/数据库查询结果）
2. 解析字段映射（用户ID、设备ID、IP、时间、金额、标签等）
3. 执行规则/模型回测
4. 输出回测报告（含混淆矩阵、捕获率、误杀率、业务影响评估）

### 工作流 C：异常检测与团伙挖掘

```
用户提供行为数据
       ↓
Agent 进行特征提取
       ↓
异常检测（统计方法 + 模型方法）
       ↓
团伙挖掘（图分析 + 社区发现）
       ↓
输出异常报告（含可疑群体、证据链）
```

**触发条件**：用户怀疑存在团伙欺诈或异常行为模式

**步骤**：
1. 提取行为特征（频次、时间分布、设备/IP聚集度、社交关系）
2. 统计异常检测（Z-score、IQR、移动平均偏差、孤立森林）
3. 图分析（设备-账号-IP关联图、社区发现算法）
4. 输出异常报告

### 工作流 E：风控系统架构设计

```
用户提出风控系统建设需求
       ↓
Agent 分析业务规模和场景
       ↓
设计系统架构（实时引擎 + 特征平台 + 决策流）
       ↓
输出架构文档（含技术选型建议）
```

**触发条件**：用户需要从零搭建或升级风控系统

**步骤**：
1. 分析业务场景（QPS、数据量、实时性要求、预算）
2. 设计系统架构（数据流、组件、部署）
3. 技术选型建议
4. 输出架构文档

---

## 常用工具与命令

### 数据分析与特征工程
```python
# 典型特征提取模板
import pandas as pd
import numpy as np

def extract_device_features(logs_df):
    """提取设备维度特征"""
    features = logs_df.groupby('device_id').agg({
        'user_id': 'nunique',
        'ip': 'nunique',
        'event_time': ['count', lambda x: (x.max() - x.min()).total_seconds()],
        'amount': ['sum', 'mean', 'std']
    })
    features.columns = ['user_cnt', 'ip_cnt', 'event_cnt', 'active_seconds', 'amount_sum', 'amount_mean', 'amount_std']
    return features

def extract_ip_features(logs_df):
    """提取IP维度特征"""
    features = logs_df.groupby('ip').agg({
        'user_id': 'nunique',
        'device_id': 'nunique',
        'event_time': 'count'
    })
    features.columns = ['user_cnt', 'device_cnt', 'event_cnt']
    return features

def extract_behavior_sequence_features(logs_df):
    """提取行为序列特征（用于序列异常检测）"""
    # 按用户和时间排序
    logs_df = logs_df.sort_values(['user_id', 'event_time'])
    # 计算行为间隔
    logs_df['time_diff'] = logs_df.groupby('user_id')['event_time'].diff().dt.total_seconds()
    # 行为速度（每分钟操作数）
    speed = logs_df.groupby('user_id')['event_time'].apply(
        lambda x: len(x) / ((x.max() - x.min()).total_seconds() / 60) if (x.max() - x.min()).total_seconds() > 0 else 0
    )
    return speed
```

### 规则引擎设计
```python
# 规则定义模板
RULES = [
    {
        'id': 'R001',
        'name': '同一设备关联多账号',
        'type': 'single',
        'condition': 'device_user_cnt > 3',
        'decision': 'REVIEW',
        'priority': 1,
        'description': '同一设备在24小时内关联超过3个不同账号'
    },
    {
        'id': 'R002',
        'name': '代理IP注册',
        'condition': 'is_proxy_ip == True AND event_type == \"register\"',
        'decision': 'REJECT',
        'priority': 2,
        'description': '使用代理IP进行注册'
    },
    {
        'id': 'R003',
        'name': '高频交易异常',
        'type': 'sequence',
        'condition': 'txn_count_1min > 10 AND amount_mean > 5000',
        'decision': 'REVIEW',
        'priority': 3,
        'description': '1分钟内交易超过10笔且平均金额>5000'
    }
]
```

### 模型训练模板
```python
# 风控模型训练模板
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, precision_recall_curve, confusion_matrix

def train_risk_model(X, y, params=None):
    """训练风控XGBoost模型"""
    if params is None:
        params = {
            'objective': 'binary:logistic',
            'eval_metric': 'auc',
            'max_depth': 6,
            'learning_rate': 0.05,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'scale_pos_weight': sum(y==0)/sum(y==1),  # 处理样本不平衡
            'random_state': 42
        }
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    dtrain = xgb.DMatrix(X_train, label=y_train)
    dtest = xgb.DMatrix(X_test, label=y_test)
    model = xgb.train(params, dtrain, num_boost_round=100, evals=[(dtest, 'test')], early_stopping_rounds=10, verbose_eval=False)
    return model

def evaluate_risk_model(model, X_test, y_test):
    """风控模型评估"""
    y_pred = model.predict(xgb.DMatrix(X_test))
    auc = roc_auc_score(y_test, y_pred)
    # 计算不同阈值下的指标
    thresholds = [0.3, 0.5, 0.7, 0.9]
    results = []
    for t in thresholds:
        y_pred_bin = (y_pred >= t).astype(int)
        cm = confusion_matrix(y_test, y_pred_bin)
        tn, fp, fn, tp = cm.ravel()
        results.append({
            'threshold': t,
            'capture_rate': tp / (tp + fn),       # 捕获率
            'false_positive_rate': fp / (fp + tn), # 误杀率
            'precision': tp / (tp + fp) if (tp+fp) > 0 else 0,
            'f1': 2*tp/(2*tp+fp+fn) if (2*tp+fp+fn) > 0 else 0
        })
    return results
```

### 规则引擎设计
```python
# 规则引擎核心逻辑模板
class RuleEngine:
    def __init__(self, rules):
        self.rules = sorted(rules, key=lambda r: r['priority'])
    
    def evaluate(self, features: dict) -> dict:
        """逐条执行规则，返回决策结果"""
        hit_rules = []
        for rule in self.rules:
            if self._match_rule(rule['condition'], features):
                hit_rules.append(rule)
                if rule.get('decision') == 'REJECT':
                    break  # 拒绝类规则短路
        return {
            'decision': self._decide(hit_rules),
            'hit_rules': [r['id'] for r in hit_rules],
            'risk_level': self._calc_risk_level(hit_rules)
        }
    
    def _match_rule(self, condition: str, features: dict) -> bool:
        """安全执行规则条件表达式"""
        # 使用受限的eval或预编译表达式
        allowed_vars = features
        try:
            return bool(eval(condition, {\"__builtins__\": {}}, allowed_vars))
        except:
            return False
    
    def _decide(self, hit_rules: list) -> str:
        if not hit_rules:
            return 'PASS'
        decisions = [r['decision'] for r in hit_rules]
        if 'REJECT' in decisions:
            return 'REJECT'
        if 'REVIEW' in decisions:
            return 'REVIEW'
        return 'PASS'
```

### 异常检测模板
```python
import numpy as np
from sklearn.ensemble import IsolationForest
from scipy import stats

def statistical_anomaly_detection(df, feature_cols, method='iqr'):
    """统计异常检测"""
    anomalies = pd.DataFrame()
    for col in feature_cols:
        if method == 'iqr':
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 3 * IQR
            upper = Q3 + 3 * IQR
            mask = (df[col] < lower) | (df[col] > upper)
        elif method == 'zscore':
            z = np.abs(stats.zscore(df[col].fillna(0)))
            mask = z > 3
        anomalies = df[mask]
        anomalies['anomaly_feature'] = col
        anomalies['anomaly_score'] = mask.astype(int)
        return anomalies

def community_fraud_detection(edges_df):
    """团伙欺诈检测 - 基于图社区发现"""
    import networkx as nx
    from community import community_louvain
    
    G = nx.Graph()
    for _, row in edges_df.iterrows():
        G.add_edge(row['node_a'], row['node_b'], weight=row.get('weight', 1))
    
    # 社区发现
    partition = community_louvain.best_partition(G, weight='weight')
    
    # 统计每个社区的风险特征
    communities = {}
    for node, comm_id in partition.items():
        if comm_id not in communities:
            communities[comm_id] = {'nodes': [], 'size': 0}
        communities[comm_id]['nodes'].append(node)
        communities[comm_id]['size'] += 1
    
    # 标记高风险社区（规模异常大、密度高）
    high_risk = {cid: info for cid, info in communities.items()
                 if info['size'] > 5}  # 规模>5的社区标记为可疑
    return high_risk
```

### 策略回测模板
```python
def backtest_strategy(data, rules, model=None):
    """策略回测"""
    results = []
    for _, row in data.iterrows():
        features = extract_features(row)
        # 规则评估
        rule_engine = RuleEngine(rules)
        rule_result = rule_engine.evaluate(features)
        
        # 模型评分（如果有）
        model_score = model.predict_proba([features])[0][1] if model else None
        
        results.append({
            'user_id': row['user_id'],
            'rule_decision': rule_result['decision'],
            'model_score': model_score,
            'hit_rules': rule_result['hit_rules'],
            'true_label': row.get('label', None)
        })
    
    # 计算回测指标
    df_result = pd.DataFrame(results)
    metrics = {
        'total': len(df_result),
        'pass_rate': (df_result['rule_decision'] == 'PASS').mean(),
        'reject_rate': (df_result['rule_decision'] == 'REJECT').mean(),
        'review_rate': (df_result['rule_decision'] == 'REVIEW').mean(),
    }
    if 'true_label' in df_result.columns:
        labeled = df_result[df_result['true_label'].notna()]
        metrics['capture_rate'] = (labeled['true_label'] == 1).mean()
        metrics['false_positive_rate'] = (
            (labeled['rule_decision'] == 'REJECT') & (labeled['true_label'] == 0)
        ).mean()
    return metrics
```

### 风控系统架构设计模板
```python
# 生成风控系统架构描述
def generate_risk_control_architecture(business_type='ecommerce', qps=1000):
    """根据业务场景生成风控系统架构建议"""
    arch = {
        'data_pipeline': {
            'source': '业务日志 → Kafka',
            'real_time_features': 'Flink SQL + Redis 实时特征',
            'batch_features': 'Spark/Hive 离线特征 → ClickHouse',
            'feature_store': 'Redis(实时) + HBase(离线)'
        },
        'decision_engine': {
            'rule_engine': 'Drools/自研规则引擎（Groovy动态规则）',
            'model_inference': 'XGBoost/ONNX 模型推理服务',
            'decision_flow': '规则引擎 → 模型评分 → 名单匹配 → 决策输出'
        },
        'data_storage': {
            'real_time': 'Redis + ClickHouse',
            'offline': 'Hive/Spark + HBase',
            'log_search': 'Elasticsearch'
        },
        'monitoring': {
            'metrics': 'Prometheus + Grafana',
            'alert': '自研告警/ELK',
            'dashboard': '通过率/拒绝率/人工审核率/欺诈率趋势'
        }
    }
    return arch
```

---

## 注意事项与陷阱

### 常见陷阱
1. **样本不平衡**：欺诈样本通常<1%，直接训练会导致模型偏向负样本。必须使用 scale_pos_weight、过采样(SMOTE)或欠采样
2. **特征穿越**：使用未来信息构造特征（如用全量数据算均值），导致回测指标虚高。必须按时间窗口滑动构造特征
3. **规则冲突**：多条规则同时命中时决策优先级不明确，需定义规则优先级和短路机制
4. **PSI漂移**：模型上线后特征分布变化导致效果衰减，需定期监控PSI并重训
5. **误杀vs漏过权衡**：严格策略降低欺诈但伤害用户体验，需量化业务影响
6. **冷启动问题**：新业务无历史数据时，先用规则+外部数据（设备指纹、IP信誉库）过渡
7. **对抗性**：黑产会针对规则/模型做对抗（如模拟正常行为），需持续迭代

### 最佳实践
- 规则和模型互补：规则捕获已知模式，模型发现未知异常
- 分层决策：先轻量规则过滤（低延迟），再模型深度分析（高精度）
- 灰度发布：新策略先小流量验证，再全量上线
- 定期复盘：每周/每月分析漏过案例，迭代策略
- 特征监控：监控特征分布变化（PSI），及时发现数据漂移

---

## 参考资源

- 风控系统架构：Flink + Kafka + Redis + ClickHouse + XGBoost
- 图分析：NetworkX（快速原型）、Neo4j/NebulaGraph（生产）
- 设备指纹：开源方案 FingerprintJS + 自研补充
- 异常检测：PyOD库（集成40+异常检测算法）
- 规则引擎：Drools 文档、EasyRules 文档