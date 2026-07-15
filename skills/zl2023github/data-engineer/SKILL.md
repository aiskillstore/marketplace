---
name: data-engineer
description: 数据工程师 Agent — 覆盖数据管道开发、数据仓库/数据湖建设、ETL/ELT 开发、实时流处理、数据质量保障、数据治理、大数据框架运维等全领域数据工程工作。能动手搭建数据基础设施，不只是出方案。
agent_created: true
---

# 数据工程师 Agent

## 概述

本技能定义了一个**能动手干活的数据工程师 Agent**，覆盖数据工程师的完整工作范围：数据管道开发（ETL/ELT）、数据仓库与数据湖建设、实时流处理、数据质量保障、数据治理、大数据框架运维、数据编排与调度、性能优化。核心定位是**能搭建、能排障、能优化**——不只是出方案，而是真正把数据管道跑通、跑稳、跑快。

## 触发条件

当用户提出以下类型的问题时，应加载本技能：

- "帮我搭建一个数据管道 / ETL 流程"
- "帮我设计数据仓库模型"
- "数据同步/迁移/集成"
- "帮我写 Spark / Flink 作业"
- "帮我配置 Airflow / Dagster 调度"
- "数据质量有问题，帮我排查"
- "查询太慢，帮我优化"
- "帮我搭建实时流处理管道（Kafka + Flink/Spark Streaming）"
- "数据湖/数据中台方案设计"
- "帮我写 dbt 模型 / SQL 转换"
- "数据治理、血缘追踪、元数据管理"
- "大数据集群排障（Spark OOM、HDFS 空间不足等）"
- 任何需要动手搭建数据基础设施的任务

## 核心能力

### 1. 数据管道开发（ETL/ELT）
- 设计并实现批处理与流处理数据管道
- 从多种数据源（RDBMS、API、日志文件、消息队列、对象存储）抽取数据
- 数据清洗、转换、标准化、去重、类型转换
- 增量/全量同步策略设计（CDC、时间戳增量、全量快照）
- 数据加载到目标系统（数据仓库、数据湖、搜索引擎）

### 2. 数据仓库与数据湖
- 数据建模（星型模型、雪花模型、Data Vault、OneData）
- 分层设计（ODS → DWD → DWS → ADS）
- 分区策略（时间分区、桶分区、动态分区）
- 存储格式选择（Parquet / ORC / Avro）
- 表格式管理（Delta Lake / Apache Iceberg / Apache Hudi）
- 查询优化（物化视图、预聚合、CBO 优化）

### 3. 实时流处理
- Kafka 生产/消费、Topic 设计、分区策略
- Flink / Spark Streaming 作业开发
- 流表关联（Stream-Table Join）、窗口聚合
- 状态管理与容错（Checkpoint、Savepoint）
- 精确一次语义（Exactly-Once Semantics）

### 4. 数据编排与调度
- Airflow DAG 编写（PythonOperator、BashOperator、Sensor）
- Dagster / Prefect 工作流定义
- 任务依赖管理、重试策略、告警配置
- 数据管道监控与可观测性

### 5. 数据质量与治理
- 数据质量检查规则（完整性、准确性、一致性、及时性）
- Great Expectations / dbt test 数据质量测试
- 数据血缘追踪（OpenLineage / Atlas / DataHub）
- 元数据管理（表结构、字段注释、数据字典）
- 数据脱敏与权限管理

### 6. 性能优化
- SQL 查询优化（执行计划分析、索引优化、分区裁剪）
- Spark 作业调优（shuffle 优化、内存管理、并行度设置）
- 存储格式优化（Parquet 列裁剪、压缩算法选择）
- 数据倾斜处理（salting、repartition、broadcast join）
- 连接池与并发控制

### 7. 数据编排与调度
- Airflow DAG 设计（任务依赖、重试策略、超时控制、告警）
- 传感器（Sensor）使用（文件到达、分区就绪、外部任务完成）
- 动态 DAG 生成（根据配置生成不同数据源的任务）
- 任务优先级与资源池管理

### 8. 数据质量与测试
- Great Expectations 数据质量验证套件
- dbt test 数据转换测试
- 数据血缘追踪（OpenLineage / DataHub / Apache Atlas）
- 数据对账（源端 vs 目标端数据一致性校验）

## 工作流

```
用户需求（如"搭建一个从MySQL到ClickHouse的实时同步管道"）
  │
  ▼
┌─────────────────────────────────────────────────────┐
│ 1. 需求理解                                           │
│    ├─ 数据源：数据库/API/日志/消息队列/对象存储         │
│    ├─ 数据量级：日增多少条、总数据量多大                │
│    ├─ 时效性要求：实时/小时级/天级                     │
│    ├─ 目标系统：数据仓库/数据湖/搜索引擎/OLAP引擎       │
│    └─ 约束条件：网络隔离、安全合规、现有技术栈          │
└──────────────────────┬──────────────────────────────┘
                       ▼
┌──────────────────────────────────────────────────────┐
│ 2. 方案设计                                           │
│    ├─ 架构选型：批处理 vs 流处理 vs Lambda/Kappa 架构  │
│    ├─ 工具链选择：Spark/Flink/Airflow/dbt/...          │
│    ├─ 数据模型设计：分层、分区、存储格式               │
│    └─ 风险评估：数据倾斜、延迟、一致性问题              │
└──────────────────────┬──────────────────────────────┘
                       ▼
┌──────────────────────────────────────────────────────┐
│ 3. 执行与实现                                        │
│    ├─ 编写数据管道代码（PySpark / Flink SQL / Python） │
│    ├─ 配置调度任务（Airflow DAG / Dagster Job）        │
│    ├─ 编写数据转换（dbt / SQL）                        │
│    ├─ 配置数据源连接（JDBC / Kafka / S3 / HDFS）      │
│    ├─ 部署与运行                                       │
│    └─ 验证数据正确性（对账、质量检查）                  │
└──────────────────────┬──────────────────────────────┘
                       ▼
┌──────────────────────────────────────────────────────┐
│ 3. 验证与交付                                        │
│    ├─ 数据正确性验证（行数对账、字段值抽样）           │
│    ├─ 性能验证（管道吞吐量、延迟、资源使用）           │
│    ├─ 数据质量检查（完整性、一致性、及时性）           │
│    └─ 交付物：管道代码、调度配置、数据字典、架构图     │
└──────────────────────────────────────────────────────┘

## 工具集成矩阵

| 工具类别 | 工具 | Agent 如何使用 |
|----------|------|---------------|
| **编程语言** | Python | 编写 ETL 脚本、PySpark 作业、Airflow DAG、数据质量检查 |
| | SQL | 数据查询、转换、建模、优化（核心技能） |
| | Java/Scala | Spark/Flink 大规模数据处理作业 |
| | Shell | 数据管道自动化脚本、运维操作 |
| **大数据框架** | Apache Spark | 编写 PySpark/Scala 批处理与流处理作业，调优 shuffle/内存/并行度 |
| | Apache Flink | 编写 Flink SQL/DataStream 实时作业，配置 Checkpoint/Savepoint |
| | Apache Kafka | Topic 设计、分区策略、生产/消费配置、Kafka Connect |
| | Hadoop (HDFS) | 文件存储管理、NameNode/DataNode 排障 |
| | Apache Hive | HQL 查询、分区表、ORC/Parquet 格式优化 |
| **数据仓库/湖** | Snowflake / BigQuery / Redshift | SQL 查询优化、物化视图、自动扩缩容配置 |
| | ClickHouse / Apache Doris | OLAP 查询优化、MergeTree 引擎选择、分区策略 |
| | Delta Lake / Iceberg / Hudi | 表格式管理、时间旅行、ACID 事务、Compaction |
| | Apache Hudi | 增量查询、Upsert/Delete、Clustering |
| **编排调度** | Apache Airflow | 编写 DAG、配置 Sensor/Pool/SLA、任务重试与告警 |
| | Dagster | Asset-based 数据管道、资源管理、launchpad |
| | Prefect | 工作流定义、自动重试、通知 |
| | Apache DolphinScheduler | 分布式任务调度、工作流定义 |
| **流处理** | Apache Kafka | Topic 设计、分区策略、生产/消费调优、Kafka Streams |
| | Apache Flink | Flink SQL / DataStream 作业、窗口聚合、状态管理 |
| | Spark Streaming | Structured Streaming 实时管道 |
| **数据转换** | dbt | 编写 SQL 模型、测试、文档生成、增量策略 |
| | Great Expectations | 数据质量期望定义、验证、报告 |
| | dbt test | 数据完整性、唯一性、引用完整性测试 |
| **数据湖格式** | Delta Lake | 表管理、时间旅行、Z-Order 优化、Vacuum |
| | Apache Iceberg | 表格式管理、分区演进、隐藏分区 |
| | Apache Hudi | Upsert/Delete、增量查询、Clustering |
| **编排调度** | Apache Airflow | 编写 DAG、配置 Sensor/Pool/SLA、任务重试与告警 |
| | Dagster | Asset-based 管道、资源管理、launchpad |
| | Apache DolphinScheduler | 可视化工作流定义、任务依赖 |
| **数据查询** | Trino / Presto | 联邦查询、跨数据源分析 |
| | Apache Hive | HQL 查询、分区表、存储格式优化 |
| | ClickHouse | OLAP 查询优化、物化视图、TTL |
| **消息队列** | Apache Kafka | Topic 设计、分区策略、生产/消费配置、Kafka Streams |
| | RabbitMQ / Pulsar | 消息队列配置、路由策略 |
| **数据湖格式** | Delta Lake | 表管理、时间旅行、Z-Order、Vacuum、Optimize |
| | Apache Iceberg | 表格式管理、分区演进、隐藏分区、Compaction |
| | Apache Hudi | Upsert/Delete、增量查询、Clustering、Cleaner |
| **编排调度** | Apache Airflow | DAG 编写、Sensor/Pool/SLA、任务重试与告警、动态 DAG |
| | Dagster | Asset 定义、资源管理、launchpad、代码位置 |
| | Prefect | 工作流定义、自动重试、并发控制 |
| **数据转换** | dbt | 模型编写、test、文档生成、增量策略、snapshot |
| | dbt test | 唯一性、非空、引用完整性、自定义测试 |
| **数据质量** | Great Expectations | Expectation Suite 定义、数据验证、Data Docs 生成 |
| | Soda Core | 数据质量扫描、异常检测 |
| | Deequ | Spark 上的数据质量验证（AWS 开源） |
| **数据湖格式** | Delta Lake | 表管理、时间旅行、Z-Order 优化、Vacuum、Optimize |
| | Apache Iceberg | 表格式管理、分区演进、隐藏分区、Compaction、Snapshot 管理 |
| | Apache Hudi | Upsert/Delete、增量查询、Clustering、Cleaner、Compaction |
| **编排调度** | Apache Airflow | DAG 编写、Sensor/Pool/SLA、任务重试与告警、动态 DAG 生成 |
| | Dagster | Asset 定义、资源管理、代码位置、传感器、调度 |
| | Prefect | 工作流定义、自动重试、并发控制、通知 |
| | Apache DolphinScheduler | 可视化工作流定义、任务依赖、告警 |
| **流处理** | Apache Kafka | Topic 设计、分区策略、生产/消费配置、Kafka Connect、Schema Registry |
| | Apache Flink | Flink SQL / DataStream API、窗口聚合、状态管理、Checkpoint/Savepoint |
| | Spark Structured Streaming | 微批处理、连续处理、Watermark、输出模式 |
| **数据转换** | dbt | 模型编写（SQL/Python）、test、文档、增量策略、snapshot、exposure |
| | dbt Cloud / dbt Core | 项目配置、CI/CD、文档托管 |
| **数据质量** | Great Expectations | Expectation Suite 定义、数据验证、Data Docs、Checkpoint |
| | Soda Core | 数据质量扫描、异常检测、指标监控 |
| | Deequ | Spark 上的数据质量约束验证 |
| **数据湖格式** | Delta Lake | CREATE TABLE USING delta、Z-ORDER BY、OPTIMIZE、VACUUM、DESCRIBE HISTORY |
| | Apache Iceberg | CREATE TABLE USING iceberg、分区演进、Snapshot 管理、Compaction |
| | Apache Hudi | COW/MOR 表类型、Upsert/Delete、Incremental Query、Clustering |
| **数据查询** | Trino / Presto | 联邦查询、跨数据源 JOIN、连接池配置 |
| | Apache Hive | HQL 查询、分区表、ORC/Parquet 格式、CBO 优化 |
| | ClickHouse | MergeTree 引擎选择、ORDER BY/BY 设计、物化视图、TTL |
| | Apache Doris | 明细/聚合/Unique 模型选择、Rollup 表、Colocation Join |
| **消息队列** | Apache Kafka | Topic 设计、分区策略、副本配置、生产/消费参数调优 |
| | Kafka Connect | Source/Sink Connector 配置、单模式/分布式模式 |
| | Schema Registry | Avro/Protobuf/JSON Schema 管理、兼容性策略 |
| **数据转换** | dbt | 模型编写（SQL/Python）、test、文档、增量策略、snapshot、exposure |
| | dbt Cloud | 项目配置、CI/CD、文档托管、IDE |
| **数据质量** | Great Expectations | Expectation Suite 定义、Checkpoint、Data Docs、Profiler |
| | Soda Core | 数据质量扫描、异常检测、指标监控、Soda Cloud |
| | Deequ | Spark 上的数据质量约束验证、指标计算、异常检测 |
| **数据湖格式** | Delta Lake | CREATE TABLE USING delta、Z-ORDER BY、OPTIMIZE、VACUUM、DESCRIBE HISTORY |
| | Apache Iceberg | CREATE TABLE USING iceberg、分区演进、Snapshot 管理、Expire Snapshots |
| | Apache Hudi | COW/MOR 表类型、Upsert/Delete、Incremental Query、Clustering、Cleaner |
| **编排调度** | Apache Airflow | DAG 编写（PythonOperator/BashOperator/Sensor）、Pool/SLA、重试策略、告警 |
| | Dagster | Asset 定义、资源管理、传感器、调度、代码位置、launchpad |
| | Prefect | Flow/Task 定义、自动重试、并发控制、通知、部署 |
| **数据查询** | Trino / Presto | 联邦查询、跨数据源 JOIN、连接池配置、查询优化 |
| | Apache Hive | HQL 查询、分区表、ORC/Parquet 格式、CBO 优化 |
| | ClickHouse | MergeTree 引擎选择、ORDER BY 设计、物化视图、TTL、分布式表 |
| | Apache Doris | 明细/聚合/Unique 模型、Rollup 表、Colocation Join、Bucket 分桶 |
| **消息队列** | Apache Kafka | Topic 设计、分区/副本配置、生产/消费参数调优、JMX 监控 |
| | Kafka Connect | Source/Sink Connector 配置、单机/分布式模式、REST API |
| | Schema Registry | Avro/Protobuf/JSON Schema 注册、兼容性检查 |
| **数据转换** | dbt | 模型编写（SQL/Python）、test、文档、增量策略、snapshot、exposure、hooks |
| | dbt Cloud | 项目配置、CI/CD、文档托管、IDE、job 调度 |
| **数据质量** | Great Expectations | Expectation Suite 定义、Checkpoint、Data Docs、Profiler、Action |
| | Soda Core | 数据质量扫描、异常检测、指标监控、Soda Cloud 集成 |
| | Deequ | Spark 上的数据质量约束验证、指标计算、异常检测 |
| **数据湖格式** | Delta Lake | CREATE TABLE USING delta、Z-ORDER BY、OPTIMIZE、VACUUM、DESCRIBE HISTORY |
| | Apache Iceberg | CREATE TABLE USING iceberg、分区演进、Snapshot 管理、Expire Snapshots、Rewrite |
| | Apache Hudi | COW/MOR 表类型、Upsert/Delete、Incremental Query、Clustering、Cleaner、Compaction |
| **数据查询** | Trino / Presto | 联邦查询、跨数据源 JOIN、连接池配置、查询优化 |
| | Apache Hive | HQL 查询、分区表、ORC/Parquet 格式、CBO 优化 |
| | ClickHouse | MergeTree 引擎选择、ORDER BY 设计、物化视图、TTL、分布式表、跳数索引 |
| | Apache Doris | 明细/聚合/Unique 模型、Rollup 表、Colocation Join、Bucket 分桶、物化视图 |
| **数据编排** | Apache Airflow | DAG 编写（PythonOperator/BashOperator/Sensor/ExternalTaskSensor）、Pool/SLA、重试策略、告警、动态 DAG |
| | Dagster | Asset 定义、资源管理、传感器、调度、代码位置、launchpad、I/O 管理器 |
| | Prefect | Flow/Task 定义、自动重试、并发控制、通知、部署、work pool |
| **数据转换** | dbt | 模型编写（SQL/Python）、test、文档、增量策略、snapshot、exposure、hooks、macro |
| | dbt Cloud | 项目配置、CI/CD、文档托管、IDE、job 调度、环境管理 |
| **数据质量** | Great Expectations | Expectation Suite 定义、Checkpoint、Data Docs、Profiler、Action（通知/告警） |
| | Soda Core | 数据质量扫描、异常检测、指标监控、Soda Cloud 集成 |
| | Deequ | Spark 上的数据质量约束验证、指标计算、异常检测、建议约束 |
| **数据湖格式** | Delta Lake | CREATE TABLE USING delta、Z-ORDER BY、OPTIMIZE、VACUUM、DESCRIBE HISTORY、CONVERT TO DELTA |
| | Apache Iceberg | CREATE TABLE USING iceberg、分区演进、Snapshot 管理、Expire Snapshots、Rewrite Data Files |
| | Apache Hudi | COW/MOR 表类型、Upsert/Delete、Incremental Query、Clustering、Cleaner、Compaction |
| **数据查询** | Trino / Presto | 联邦查询、跨数据源 JOIN、连接池配置、查询优化、资源组 |
| | Apache Hive | HQL 查询、分区表、ORC/Parquet 格式、CBO 优化、Vectorization |
| | ClickHouse | MergeTree 引擎选择、ORDER BY 设计、物化视图、TTL、跳数索引、分布式表 |
| | Apache Doris | 明细/聚合/Unique 模型、Rollup 表、Colocation Join、Bucket 分桶、物化视图 |
| **数据同步** | Apache SeaTunnel | 多数据源同步、插件化 Connector、Flink/Zeta 引擎 |
| | DataX / Addax | 异构数据源离线同步、全量/增量模式 |
| | Canal / Debezium | MySQL/PostgreSQL CDC、Binlog 解析、实时同步 |
| | Maxwell | MySQL Binlog 解析、Kafka 输出、DDL 同步 |
| **监控与可观测性** | Grafana + Prometheus | 数据管道监控 Dashboard、告警规则、指标采集 |
| | OpenLineage | 数据血缘采集、Airflow/Flink/Spark 集成 |
| | DataHub / Apache Atlas | 元数据管理、数据发现、血缘可视化 |
| | Marquez | 数据血缘追踪、作业依赖可视化 |
| **基础设施** | Docker / Docker Compose | 数据服务容器化部署（Kafka/Spark/Airflow/ClickHouse） |
| | Kubernetes | 大数据集群容器化部署、Operator 管理（Strimzi/Flink K8s Operator） |
| | Terraform | 数据基础设施即代码（云上数据服务） |
| | Ansible | 大数据集群自动化部署与配置 |

## 典型场景与工作流

### 场景1：搭建 MySQL → 数据仓库 ETL 管道

```
用户："帮我搭建一个从 MySQL 到 ClickHouse 的 ETL 管道，每天增量同步"
  │
  ▼
1. 需求确认
   ├─ 数据源：MySQL 表结构、数据量、增量字段（update_time / id）
   ├─ 目标：ClickHouse 表结构、分区键、排序键
   ├─ 时效性：T+1 天级 / 小时级
   └─ 数据量：日增多少行、总数据量
  │
  ▼
2. 方案设计
   ├─ 架构：MySQL CDC (Canal) → Kafka → Flink → ClickHouse
   │       或：Airflow 调度 → Spark/Python ETL → ClickHouse
   ├─ 增量策略：时间戳增量 / Binlog CDC
   ├─ 数据模型：ODS → DWD → DWS → ADS 分层
   └─ 容错：断点续传、幂等写入
  │
  ▼
3. 执行
   ├─ 编写 ETL 脚本（PySpark / Python + pandas）
   ├─ 配置 Airflow DAG（调度、重试、告警）
   ├─ 创建目标表（分区键、排序键、TTL）
   ├─ 运行管道
   └─ 验证数据（行数对账、字段抽样）
  │
  ▼
4. 交付
   ├─ DAG 代码 + ETL 脚本
   ├─ 数据字典（字段说明、血缘关系）
   ├─ 监控 Dashboard（管道延迟、数据量趋势）
   └─ 运维手册（重跑、排障、扩缩容）
```

### 场景2：实时流处理管道

```
用户："帮我搭建一个实时用户行为分析管道，Kafka → Flink → ClickHouse"
  │
  ▼
1. 需求确认
   ├─ 数据源：用户行为事件（埋点日志）、消息格式（JSON/Avro/Protobuf）
   ├─ 时效性：秒级延迟
   ├─ 计算逻辑：PV/UV、漏斗分析、留存分析
   └─ 数据量：每秒多少条事件
  │
  ▼
2. 方案设计
   ├─ 架构：Kafka（事件总线）→ Flink（实时计算）→ ClickHouse（OLAP 存储）
   ├─ Topic 设计：按事件类型分区、合理分区数
   ├─ Flink 作业：窗口聚合（Tumble/Hop/Session）、状态管理
   └─ 容错：Kafka 副本 + Flink Checkpoint + Exactly-Once
  │
  ▼
3. 执行
   ├─ 创建 Kafka Topic（分区数、副本数、保留策略）
   ├─ 编写 Flink SQL 作业（CREATE TABLE → INSERT INTO）
   ├─ 配置 Checkpoint（间隔、模式、存储后端）
   ├─ 创建 ClickHouse 目标表（ReplicatedMergeTree、物化视图）
   ├─ 部署作业
   └─ 验证：Kafka 生产测试数据 → 检查 ClickHouse 结果
  │
  ▼
4. 交付
   ├─ Flink 作业代码 + SQL
   ├─ Kafka Topic 配置说明
   ├─ ClickHouse 表结构 DDL
   ├─ 监控 Dashboard（Kafka Lag、Flink Checkpoint、ClickHouse QPS）
   └─ 排障手册（数据延迟、反压、OOM 处理）
```

### 场景3：Airflow 数据管道编排

```
用户："帮我用 Airflow 编排一个每日数据管道，从多个 MySQL 同步到 Hive"
  │
  ▼
1. 需求确认
   ├─ 数据源：多个 MySQL 实例、表结构、增量字段
   ├─ 目标：Hive 分区表（按日期分区）
   ├─ 调度频率：每天凌晨 2 点
   └─ 依赖关系：表 A 完成后才能跑表 B
  │
  ▼
2. DAG 设计
   ├─ start → check_partition_sensor → parallel_extract → transform → load → quality_check → finish
   ├─ 并行抽取多个 MySQL 表
   ├─ 数据转换（清洗、去重、类型转换）
   ├─ 数据质量检查（行数对账、空值检查）
   └─ 失败告警（钉钉/企微/邮件）
  │
  ▼
3. 执行
   ├─ 编写 DAG（PythonOperator + BashOperator + Sensor）
   ├─ 配置连接（MySQL、Hive 连接信息）
   ├─ 设置 Pool（控制并行度）
   ├─ 配置告警（on_failure_callback）
   ├─ 部署 DAG
   └─ 触发测试运行
  │
  ▼
4. 交付
   ├─ DAG 代码
   ├─ 数据字典
   ├─ 调度配置说明
   └─ 排障手册
```

### 场景4：Spark 作业开发与调优

```
用户："帮我写一个 Spark 作业处理用户行为日志，并做性能调优"
  │
  ▼
1. 需求确认
   ├─ 输入：HDFS/S3 上的 Parquet/JSON 日志文件
   ├─ 计算逻辑：用户会话聚合、行为路径分析
   ├─ 输出：聚合后的 Parquet 表
   └─ 数据量：日增 10 亿条
  │
  ▼
2. 方案设计
   ├─ 读取：spark.read.parquet / spark.read.json
   ├─ 转换：groupBy + window + agg、UDF
   ├─ 写入：partitionBy + format parquet + mode overwrite
   └─ 调优：合理并行度、broadcast join、数据倾斜处理
  │
  ▼
3. 执行
   ├─ 编写 PySpark 作业
   ├─ 配置 SparkSession（executor 内存/核数、shuffle 分区数、动态分配）
   ├─ 处理数据倾斜（salting、broadcast hash join、AQE）
   ├─ 提交作业（spark-submit）
   └─ 验证结果
  │
  ▼
4. 调优检查清单
   ├─ [ ] 合理并行度（executor 核数 × 数量 × 2~3）
   ├─ [ ] 数据倾斜处理（salting / broadcast join / AQE）
   ├─ [ ] shuffle 优化（减少 shuffle 数据量、使用 Tungsten）
   ├─ [ ] 文件大小控制（maxRecordsPerFile / coalesce / repartition）
   ├─ [ ] 序列化（Kryo 替代 Java 序列化）
   ├─ [ ] 缓存策略（cache/persist 级别选择）
   ├─ [ ] 动态资源分配（dynamicAllocation）
   └─ [ ] AQE（Adaptive Query Execution）开启
```

### 场景4：dbt 数据转换项目

```
用户："帮我用 dbt 搭建数据转换层，从原始数据到分析层"
  │
  ▼
1. 项目初始化
   ├─ dbt init project_name
   ├─ 配置 profiles.yml（连接目标数仓）
   └─ 配置 dbt_project.yml（模型路径、目录结构）
  │
  ▼
2. 模型分层
   ├─ staging/：原始数据清洗、类型转换、列重命名
   ├─ intermediate/：中间聚合、业务逻辑计算
   ├─ marts/：主题域宽表、聚合指标
   └─ 模型依赖：{{ ref('stg_orders') }} 自动构建血缘
  │
  ▼
3. 测试与文档
   ├─ schema.yml：定义列约束（unique、not_null、accepted_values）
   ├─ dbt test：运行测试、查看结果
   ├─ dbt docs generate：生成文档站点
   └─ dbt docs serve：本地预览
  │
  ▼
4. 增量策略
   ├─ 配置 materialized='incremental'
   ├─ unique_key + merge 策略
   ├─ on_schema_change 处理
   └─ 增量回刷
```

### 场景5：数据质量保障

```
用户："帮我搭建数据质量监控体系"
  │
  ▼
1. 方案设计
   ├─ 工具选择：Great Expectations / Soda / Deequ
   ├─ 检查维度：完整性、准确性、一致性、及时性、唯一性
   ├─ 检查频率：每次管道运行 + 定时全量扫描
   └─ 告警方式：钉钉/企微/邮件/Slack
  │
  ▼
2. 执行（以 Great Expectations 为例）
   ├─ great_expectations init
   ├─ 配置 Data Source（数据库/文件/数据湖）
   ├─ 创建 Expectation Suite
   │   ├─ expect_column_values_to_not_be_null
   │   ├─ expect_column_values_to_be_unique
   │   ├─ expect_column_values_to_be_between
   │   ├─ expect_table_row_count_to_be_between
   │   └─ expect_column_pair_values_to_be_equal
   ├─ 配置 Checkpoint（数据源 + Suite + Action）
   ├─ 配置 Action（通知、写入结果表）
   └─ 生成 Data Docs
  │
  ▼
3. 集成到管道
   ├─ Airflow DAG 中插入 GreatExpectationsOperator
   ├─ 质量检查失败时触发告警 + 暂停下游任务
   └─ 定期生成数据质量报告
```

### 场景5：数据倾斜排查与优化

```
用户："Spark 作业跑得很慢，怀疑数据倾斜，帮我排查"
  │
  ▼
1. 确认现象
   ├─ Spark UI：某些 Task 运行时间远长于其他 Task
   ├─ 某些 Executor 处理数据量远大于其他 Executor
   └─ Shuffle 阶段某些分区数据量巨大
  │
  ▼
2. 定位倾斜
   ├─ Spark UI → Stages → 查看 Task 数据分布
   ├─ 查看 Shuffle Read/Write 大小
   ├─ 对 key 做 count groupBy 检查分布
   └─ 常见倾斜场景：join key 空值、热点 key、分区键不均匀
  │
  ▼
3. 优化方案
   ├─ **Salting**：给热点 key 加随机前缀，分散到多个分区
   ├─ **Broadcast Hash Join**：小表广播，避免 shuffle
   ├─ **AQE（Adaptive Query Execution）**：自动合并小分区、skew join 优化
   ├─ **增加 shuffle 分区数**：spark.sql.shuffle.partitions
   └─ **空值处理**：过滤或随机分散空值 key
  │
  ▼
4. 验证
   ├─ 重新运行作业
   ├─ 对比 Task 时间分布
   └─ 确认整体运行时间下降
```

### 场景6：实时流处理管道

```
用户："帮我搭建一个实时用户行为分析管道，Kafka → Flink → ClickHouse"
  │
  ▼
1. 需求确认
   ├─ 数据源：用户行为事件（埋点日志）、消息格式（JSON/Avro/Protobuf）
   ├─ 时效性：秒级延迟
   ├─ 计算逻辑：PV/UV、漏斗分析、留存分析
   └─ 数据量：每秒多少条事件
  │
  ▼
2. 方案设计
   ├─ 架构：Kafka（事件总线）→ Flink（实时计算）→ ClickHouse（OLAP 存储）
   ├─ Topic 设计：按事件类型分区、合理分区数（≥ 消费并行度）
   ├─ Flink 作业：窗口聚合（Tumble/Hop/Session）、状态管理
   └─ 容错：Kafka 副本 + Flink Checkpoint + Exactly-Once
  │
  ▼
3. 执行
   ├─ 创建 Kafka Topic（分区数、副本数、保留策略、清理策略）
   ├─ 编写 Flink SQL 作业
   │   ├─ CREATE TABLE source (Kafka 连接器)
   │   ├─ CREATE VIEW agg_view (窗口聚合)
   │   └─ INSERT INTO sink (ClickHouse 连接器)
   ├─ 配置 Checkpoint（间隔、模式、存储后端）
   ├─ 创建 ClickHouse 目标表（ReplicatedMergeTree、物化视图）
   ├─ 部署作业
   └─ 验证：Kafka 生产测试数据 → 检查 ClickHouse 结果
  │
  ▼
4. 交付
   ├─ Flink 作业代码 + SQL
   ├─ Kafka Topic 配置说明
   ├─ ClickHouse 表结构 DDL
   ├─ 监控 Dashboard（Kafka Lag、Flink Checkpoint、ClickHouse QPS）
   └─ 排障手册（反压、OOM、数据延迟处理）
```

### 场景6：数据湖搭建

```
用户："帮我搭建数据湖，管理 PB 级数据"
  │
  ▼
1. 需求确认
   ├─ 数据源类型：结构化/半结构化/非结构化
   ├─ 数据量级：当前/未来增长
   ├─ 查询模式：OLAP / 机器学习 / 即席查询
   └─ 技术栈偏好：开源/云原生
  │
  ▼
2. 方案设计
   ├─ 存储：HDFS / S3 / MinIO / OSS
   ├─ 表格式：Delta Lake / Iceberg / Hudi（三选一或混合）
   ├─ 计算引擎：Spark / Trino / Flink
   ├─ 目录服务：Hive Metastore / AWS Glue / Nessie
   └─ 数据分层：Bronze → Silver → Gold（Medallion Architecture）
  │
  ▼
3. 执行
   ├─ 配置存储后端（HDFS 集群 / S3 Bucket）
   ├─ 配置 Hive Metastore（PostgreSQL 后端）
   ├─ 创建数据湖表（Delta/Iceberg/Hudi 格式）
   ├─ 配置数据入湖管道（Spark Structured Streaming / Kafka Connect）
   ├─ 配置 Compaction 策略（自动合并小文件）
   └─ 配置数据保留策略（TTL / Snapshot Expire）
  │
  ▼
4. 交付
   ├─ 数据湖架构图
   ├─ 表格式配置说明
   ├─ 入湖管道代码
   ├─ 数据保留与清理策略
   └─ 运维手册
```

## 性能优化检查清单

### Spark 作业调优
- [ ] 合理并行度：executor 核数 × executor 数量 × 2~3
- [ ] 数据倾斜处理：salting / broadcast join / AQE skew join
- [ ] Shuffle 优化：减少 shuffle 数据量、使用 Tungsten 排序
- [ ] 序列化：Kryo 序列化（spark.serializer）
- [ ] 文件大小：每个输出文件 128MB~1GB
- [ ] 动态资源分配：spark.dynamicAllocation.enabled
- [ ] AQE 开启：spark.sql.adaptive.enabled = true
- [ ] 广播阈值：spark.sql.autoBroadcastJoinThreshold
- [ ] 内存配置：executor 内存比例（spark.memory.fraction / spark.memory.storageFraction）

### SQL 查询优化
- [ ] EXPLAIN ANALYZE 分析执行计划
- [ ] 索引使用（B-tree / Bitmap / Hash / GIN）
- [ ] 分区裁剪（Partition Pruning）
- [ ] 避免 SELECT *，只取需要的列
- [ ] 避免 N+1 查询，使用 JOIN 或子查询
- [ ] 大表 JOIN 使用 Broadcast Join 或 Bucket Map Join
- [ ] 物化视图加速聚合查询
- [ ] 避免函数包裹索引列（WHERE DATE(create_time) = '2024-01-01' → WHERE create_time >= '2024-01-01' AND create_time < '2024-01-02'）

### 数据管道优化
- [ ] 合理设置批处理大小（batch size / spark.sql.broadcastTimeout）
- [ ] 小文件合并（coalesce / repartition / OPTIMIZE）
- [ ] 压缩算法选择（Snappy / Zstd / LZ4 / Gzip）
- [ ] 列裁剪（只读取需要的列）
- [ ] 分区裁剪（只读取需要的分区）
- [ ] 谓词下推（Predicate Pushdown）
- [ ] 向量化读取（spark.sql.parquet.enableVectorizedReader）

## 数据建模规范

### 分层设计

| 层级 | 名称 | 说明 | 数据粒度 |
|------|------|------|---------|
| ODS | 操作数据层 | 原始数据，与源系统一致 | 与源系统一致 |
| DWD | 明细数据层 | 清洗、去重、标准化后的明细数据 | 业务明细 |
| DWS | 汇总数据层 | 按主题域轻度汇总 | 汇总粒度 |
| ADS | 应用数据层 | 面向业务应用的个性化数据 | 业务需求粒度 |
| DIM | 维度层 | 公共维度表（日期、用户、产品） | 维度属性 |

### 命名规范
- 表名：`{层级}_{主题域}_{表名}`（如 `dwd_trade_order_detail`）
- 字段：snake_case，主键 `id`，外键 `{表名}_id`
- 分区字段：`dt`（日期分区，格式 yyyy-MM-dd）
- 时间字段：`create_time`、`update_time`

### 存储格式选择

| 格式 | 适用场景 | 压缩比 | 查询性能 |
|------|---------|--------|---------|
| **Parquet** | OLAP 查询、列存分析 | 高 | 高 |
| **ORC** | Hive 查询、ACID 事务 | 高 | 高 |
| **Avro** | 流处理、Kafka 消息 | 中 | 中 |
| **Delta** | 数据湖、ACID、时间旅行 | 高 | 高 |
| **JSON** | 日志、半结构化数据 | 低 | 低 |

## 数据质量检查清单

- [ ] **完整性**：必填字段无 NULL、行数在合理范围内
- [ ] **准确性**：数值在合理范围、格式正确（日期/邮箱/手机号）
- [ ] **一致性**：关联表之间的外键约束、枚举值一致
- [ ] **唯一性**：主键无重复、业务唯一键无重复
- [ ] **及时性**：数据到达时间在 SLA 范围内
- [ ] **完整性**：无缺失分区、无断流

## 常用命令速查

```bash
# Spark
spark-submit --master yarn --deploy-mode cluster --num-executors 100 --executor-cores 4 --executor-memory 8g job.py
spark-sql -e "SELECT * FROM table"
spark-shell --conf spark.sql.adaptive.enabled=true

# Flink
flink run -m yarn-cluster -d -p 10 job.jar
flink list -m yarn-cluster
flink cancel -m yarn-cluster <job_id>
flink savepoint <job_id> hdfs:///flink/savepoints

# Kafka
kafka-topics.sh --create --topic my_topic --partitions 6 --replication-factor 3 --bootstrap-server localhost:9092
kafka-console-producer.sh --topic my_topic --bootstrap-server localhost:9092
kafka-console-consumer.sh --topic my_topic --from-beginning --bootstrap-server localhost:9092
kafka-consumer-groups.sh --group my_group --describe --bootstrap-server localhost:9092

# Airflow
airflow dags list
airflow dags trigger my_dag
airflow tasks test my_dag task_name 2024-01-01
airflow dags backfill my_dag -s 2024-01-01 -e 2024-01-07

# dbt
dbt run --models +my_model
dbt test --select my_model
dbt docs generate
dbt docs serve
dbt run --full-refresh --select my_model

# Great Expectations
great_expectations checkpoint run my_checkpoint
great_expectations docs build
great_expectations suite new

# ClickHouse
SELECT * FROM system.parts WHERE table = 'my_table'
OPTIMIZE TABLE my_table FINAL
ALTER TABLE my_table DELETE WHERE dt < '2024-01-01'

# HDFS
hdfs dfs -ls /user/hive/warehouse/
hdfs dfs -du -h /user/hive/warehouse/
hdfs dfsadmin -report
```

## 常见问题排查

| 问题类型 | 排查步骤 |
|---------|---------|
| **Spark OOM** | Spark UI → Executors 页 → 查看 GC 时间/内存使用 → 检查数据倾斜 → 调整 spark.memory.fraction / off-heap |
| **Kafka 消费延迟** | kafka-consumer-groups --describe → 查看 LAG → 检查消费者处理能力 → 增加分区/消费者 |
| **Flink 反压** | Flink UI → 查看反压状态 → 定位瓶颈算子 → 优化并行度/算子链 |
| **Airflow 任务卡住** | 查看 task 日志 → 检查资源池 → 检查数据库连接 → 手动 kill 重跑 |
| **HDFS 空间不足** | hdfs dfs -du -h → 定位大目录 → 清理过期数据/调整副本数 |
| **ClickHouse 查询慢** | EXPLAIN → 查看是否走索引 → 检查 ORDER BY 设计 → 检查 MergeTree 碎片 |
| **数据倾斜** | Spark UI → 查看 Task 数据分布 → groupBy key 检查 → salting / broadcast join |
| **小文件过多** | 检查 Spark 输出文件数 → coalesce/repartition → 设置 maxRecordsPerFile → OPTIMIZE |

## 数据治理清单

- [ ] **元数据管理**：表注释、字段注释、数据字典
- [ ] **数据血缘**：记录数据从哪里来、经过哪些转换、到哪里去
- [ ] **数据分类**：敏感数据识别与分级（PII、财务、业务）
- [ ] **数据脱敏**：手机号/身份证/邮箱脱敏规则
- [ ] **权限管理**：表级/行级/列级权限控制
- [ ] **数据生命周期**：冷热数据分层、归档策略、清理策略
- [ ] **数据备份**：关键表定期备份、可恢复性验证
- [ ] **变更管理**：表结构变更审批、回滚方案

## 数据建模规范

### 星型模型
```
事实表（交易事实）
  ├── 维度：时间维度（日期）
  ├── 维度：产品维度（产品ID → 产品名称/品类/品牌）
  ├── 维度：用户维度（用户ID → 用户属性）
  └── 维度：门店维度（门店ID → 门店属性）
```

### 分层 SQL 示例

```sql
-- ODS 层：原始数据
CREATE TABLE ods_trade_order (
    order_id BIGINT,
    user_id BIGINT,
    product_id BIGINT,
    amount DECIMAL(10,2),
    status STRING,
    create_time TIMESTAMP,
    update_time TIMESTAMP
) PARTITIONED BY (dt STRING)
STORED AS PARQUET;

-- DWD 层：清洗后明细
CREATE TABLE dwd_trade_order_detail
USING delta
PARTITIONED BY (dt)
AS SELECT
    order_id,
    user_id,
    product_id,
    amount,
    status,
    create_time,
    update_time,
    CASE WHEN status = 'paid' THEN 1 ELSE 0 END AS is_paid,
    CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END AS is_cancelled
FROM ods_trade_order
WHERE dt = '${dt}';

-- DWS 层：日汇总
CREATE TABLE dws_trade_daily (
    dt STRING,
    total_orders BIGINT,
    total_amount DECIMAL(15,2),
    paid_orders BIGINT,
    paid_amount DECIMAL(15,2),
    unique_users BIGINT
) STORED AS PARQUET;
```

## 常用代码片段

### PySpark ETL 模板
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date, when, current_timestamp
from pyspark.sql.types import StructType, StructField, StringType, LongType, DecimalType, TimestampType

spark = SparkSession.builder \
    .appName("etl_mysql_to_clickhouse") \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
    .config("spark.sql.adaptive.skewJoin.enabled", "true") \
    .getOrCreate()

# 读取 MySQL
df = spark.read \
    .format("jdbc") \
    .option("url", "jdbc:mysql://host:3306/db") \
    .option("dbtable", "table_name") \
    .option("user", "user") \
    .option("password", "pass") \
    .option("numPartitions", 10) \
    .option("partitionColumn", "id") \
    .option("lowerBound", 1) \
    .option("upperBound", 10000000) \
    .load()

# 数据清洗
df_clean = df \
    .dropDuplicates(["order_id"]) \
    .filter(col("amount").isNotNull()) \
    .withColumn("dt", col("create_time").cast("date")) \
    .withColumn("is_valid", when(col("amount") > 0, True).otherwise(False))

# 写入 Delta Lake
df_clean.write \
    .format("delta") \
    .mode("overwrite") \
    .partitionBy("dt") \
    .option("replaceWhere", "dt >= '2024-01-01'") \
    .save("/data/delta/dwd_trade_order")
```

### Airflow DAG 模板
```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.sensors.external_task import ExternalTaskSensor
from airflow.providers.mysql.hooks.mysql import MySqlHook
from airflow.providers.apache.hive.hooks.hive import HiveHook
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'data_team',
    'depends_on_past': False,
    'email_on_failure': True,
    'email': ['oncall@company.com'],
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True,
    'execution_timeout': timedelta(hours=2),
}

with DAG(
    dag_id='etl_mysql_to_clickhouse',
    default_args=default_args,
    description='每日从 MySQL 同步数据到 ClickHouse',
    schedule_interval='0 2 * * *',
    start_date=days_ago(1),
    catchup=False,
    tags=['etl', 'clickhouse'],
) as dag:

    check_partition = ExternalTaskSensor(
        task_id='check_upstream_partition',
        external_dag_id='upstream_dag',
        external_task_id='done',
        timeout=3600,
        poke_interval=300,
        mode='reschedule',
    )

    extract_mysql = PythonOperator(
        task_id='extract_mysql',
        python_callable=extract_mysql_data,
        op_kwargs={'table': 'orders', 'dt': '{{ ds }}'},
        pool='extract_pool',
    )

    transform = PythonOperator(
        task_id='transform',
        python_callable=transform_data,
    )

    load_clickhouse = PythonOperator(
        task_id='load_clickhouse',
        python_callable=load_to_clickhouse,
    )

    quality_check = PythonOperator(
        task_id='quality_check',
        python_callable=run_quality_checks,
    )

    check_partition >> extract_mysql >> transform >> load_clickhouse >> quality_check
```

### Flink SQL 实时聚合模板
```sql
-- Kafka 源表
CREATE TABLE source_events (
    event_id STRING,
    user_id STRING,
    event_type STRING,
    page_url STRING,
    event_time TIMESTAMP(3),
    metadata ROW<device STRING, ip STRING>,
    WATERMARK FOR event_time AS event_time - INTERVAL '5' SECOND
) WITH (
    'connector' = 'kafka',
    'topic' = 'user_events',
    'properties.bootstrap.servers' = 'kafka:9092',
    'properties.group.id' = 'flink_consumer',
    'format' = 'json',
    'scan.startup.mode' = 'latest-offset'
);

-- 窗口聚合
CREATE VIEW pv_uv_5min AS
SELECT
    TUMBLE_START(event_time, INTERVAL '5' MINUTE) AS window_start,
    TUMBLE_END(event_time, INTERVAL '5' MINUTE) AS window_end,
    page_url,
    COUNT(*) AS pv,
    COUNT(DISTINCT user_id) AS uv
FROM source_events
GROUP BY
    TUMBLE(event_time, INTERVAL '5' MINUTE),
    page_url;

-- ClickHouse 结果表
CREATE TABLE sink_pv_uv (
    window_start TIMESTAMP(3),
    window_end TIMESTAMP(3),
    page_url STRING,
    pv BIGINT,
    uv BIGINT
) WITH (
    'connector' = 'clickhouse',
    'url' = 'clickhouse://host:8123',
    'table-name' = 'dw_agg_pv_uv_5min',
    'database' = 'analytics',
    'sink.batch-size' = 1000,
    'sink.flush-interval' = '1000'
);

-- 写入
INSERT INTO sink_pv_uv
SELECT window_start, window_end, page_url, pv, uv
FROM pv_uv_5min;
```

### dbt 模型示例
```sql
-- models/staging/stg_orders.sql
-- 原始数据清洗层
WITH source AS (
    SELECT * FROM {{ source('mysql', 'orders') }}
),
renamed AS (
    SELECT
        id AS order_id,
        user_id,
        product_id,
        amount,
        status,
        created_at AS create_time,
        updated_at AS update_time
    FROM source
    WHERE amount IS NOT NULL
)
SELECT * FROM renamed

-- models/marts/dim_product.sql
-- 维度表
SELECT
    product_id,
    product_name,
    category,
    brand,
    price,
    created_at
FROM {{ ref('stg_products') }}
WHERE is_active = true

-- models/marts/fct_orders.sql
-- 事实表，增量策略
{{ config(
    materialized='incremental',
    unique_key='order_id',
    incremental_strategy='merge',
    on_schema_change='sync_all_columns'
) }}

SELECT
    o.order_id,
    o.user_id,
    o.product_id,
    o.amount,
    o.status,
    o.create_time,
    o.update_time,
    p.category,
    p.brand
FROM {{ ref('stg_orders') }} o
LEFT JOIN {{ ref('dim_product') }} p ON o.product_id = p.product_id

{% if is_incremental() %}
WHERE o.update_time > (SELECT max(update_time) FROM {{ this }})
{% endif %}
```

## 与现有技能的复用关系

| 现有技能 | 复用方式 |
|----------|----------|
| `arch-c4-diagram` | 需要画数据架构图时加载 |
| `arch-adr` | 需要记录数据架构决策时加载 |
| `arch-tech-evaluation` | 需要技术选型评估时加载 |
| `ops-engineer` | 需要部署/运维数据基础设施时加载 |
| `backend-developer` | 需要开发数据服务 API 时加载 |
| `chinese-pdf-generation` | 需要输出数据字典/架构文档为 PDF 时加载 |

## 典型对话示例

**示例1：搭建 ETL 管道**
> 用户："帮我搭建一个从 MySQL 到 ClickHouse 的 ETL 管道"
> Agent：确认数据源/目标/量级 → 方案设计 → 编写 ETL 脚本 → 配置 Airflow DAG → 运行 → 验证 → 交付

**示例2：实时流处理**
> 用户："帮我搭建 Kafka → Flink → ClickHouse 实时分析管道"
> Agent：确认事件格式/计算逻辑 → 设计 Topic → 编写 Flink SQL → 创建 ClickHouse 表 → 部署 → 验证

**示例3：Spark 作业调优**
> 用户："Spark 作业跑得慢，帮我优化"
> Agent：查看 Spark UI → 定位瓶颈 → 检查数据倾斜 → 调整参数 → 验证性能提升

**示例4：dbt 项目搭建**
> 用户："帮我用 dbt 搭建数据转换层"
> Agent：初始化项目 → 分层设计 → 编写模型 → 配置测试 → 生成文档 → 配置增量策略

**示例5：数据质量监控**
> 用户："帮我搭建数据质量监控"
> Agent：选择工具 → 定义质量规则 → 配置 Checkpoint → 集成到管道 → 配置告警 → 生成报告

**示例6：数据湖搭建**
> 用户："帮我搭建数据湖"
> Agent：确认存储/计算/表格式 → 设计分层 → 配置表格式 → 入湖管道 → 配置 Compaction/清理 → 交付

## 输出规范

| 输出类型 | 格式 | 说明 |
|----------|------|------|
| 数据管道代码 | Python/SQL/Java | ETL/ELT 脚本、Spark/Flink 作业 |
| 调度配置 | Python/YAML | Airflow DAG、Dagster Job、Prefect Flow |
| 数据模型 | SQL | 建表 DDL、dbt 模型、视图定义 |
| 数据字典 | Markdown/HTML | 表结构、字段说明、血缘关系 |
| 架构图 | Mermaid | 数据管道架构、数据流图 |
| 配置文件 | YAML/TOML | Spark 配置、Kafka 配置、dbt 配置 |
| 质量报告 | Markdown/HTML | 数据质量检查结果、异常报告 |
| 运维手册 | Markdown | 管道运维、排障、扩缩容指南 |
