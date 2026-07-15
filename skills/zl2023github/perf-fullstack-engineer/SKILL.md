---
name: perf-fullstack-engineer
title: 性能测试/全栈工程师 Agent
description: 覆盖性能测试（压测、监控、调优、容量规划）与全栈开发（前后端、API、数据库、DevOps）的复合工程师技能。支持从需求分析到压测执行到瓶颈定位到调优建议的全流程。
---

# 性能测试/全栈工程师 Agent

## 触发条件

当用户提出以下需求时加载本技能：
- 性能测试/压测/负载测试/压力测试/稳定性测试
- 性能调优/优化/瓶颈分析/慢查询排查
- 全栈开发/前后端开发/API开发/数据库设计
- 容量规划/性能基线/性能回归
- 全链路压测/高并发/高可用
- 系统架构性能评估/技术选型

## 核心能力

### 1. 性能测试
- **需求分析**：明确性能指标（TPS/QPS、响应时间P50/P95/P99、并发用户数、吞吐量、错误率、资源利用率）
- **场景设计**：基准测试、负载测试、压力测试、稳定性测试（耐久性）、峰值测试、容量规划测试
- **脚本开发**：JMeter (.jmx)、k6 (JS)、Locust (Python)、Gatling (Scala) 脚本编写
- **执行与分析**：运行压测、收集指标、定位瓶颈
- **报告输出**：性能测试报告（含图表、趋势、建议）

### 2. 全栈开发
- **前端**：React/Vue/Next.js 项目搭建、组件开发、状态管理、性能优化（Lighthouse、懒加载、CDN）
- **后端**：Node.js/Python/Go/Java API开发、RESTful/GraphQL设计、中间件集成
- **数据库**：SQL建模、索引优化、慢查询分析、NoSQL选型
- **DevOps**：Docker/K8s部署、CI/CD流水线、环境管理
- **架构**：微服务/单体架构评估、缓存策略、异步处理、高可用设计

## 工作流程

### 性能测试流程

```
需求分析 → 指标定义 → 场景设计 → 脚本开发 → 测试执行 → 监控采集 → 瓶颈分析 → 调优建议 → 报告输出
```

#### 步骤1：需求分析与指标定义
- 明确业务场景（登录、下单、搜索、支付等）
- 定义关键指标：
  - **TPS/QPS**：每秒事务/查询数
  - **响应时间**：P50/P95/P99（毫秒级）
  - **并发用户数**：在线用户 vs 并发用户
  - **错误率**：< 0.1% 通常为可接受
  - **资源利用率**：CPU < 80%, 内存 < 80%, 磁盘IO < 70%
- 确定测试环境（生产环境/预发布环境/压测环境）

#### 步骤2：场景设计
- **基准测试**：单用户/低并发，建立性能基线
- **负载测试**：逐步增加并发，观察系统行为
- **压力测试**：超过预期负载，观察系统极限和恢复能力
- **稳定性测试**：长时间运行（4-24h），检测内存泄漏、连接泄漏
- **峰值测试**：模拟突发流量（秒杀、大促）
- **容量规划测试**：找到系统拐点，确定最大承载能力

#### 步骤3：脚本开发
- **k6**（推荐，JS/Go混合，轻量，CI友好）：
  ```javascript
  import http from 'k6/http';
  import { check, sleep } from 'k6';
  export const options = {
    stages: [
      { duration: '2m', target: 100 },  // 爬坡
      { duration: '5m', target: 100 },  // 稳定
      { duration: '2m', target: 0 },   // 下降
    ],
    thresholds: {
      http_req_duration: ['p(95)<500'],
      http_req_failed: ['rate<0.01'],
    },
  };
  export default function () {
    const res = http.get('https://api.example.com/endpoint');
    check(res, { 'status 200': (r) => r.status === 200 });
    sleep(1);
  }
  ```
- **JMeter**：GUI录制 + CLI执行，适合复杂场景（参数化、关联、断言、分布式压测）
- **Locust**：Python编写，适合自定义协议和复杂业务逻辑
- **wrk/ab**：快速命令行压测，适合简单HTTP接口

#### 步骤4：监控与数据采集
- **系统层**：`top/htop`, `vmstat`, `iostat`, `netstat`, `dstat`, `sar`
- **JVM**：`jstat`, `jstack`, `jmap`, `jcmd`, GC日志分析
- **数据库**：`SHOW PROCESSLIST`, `EXPLAIN ANALYZE`, `pg_stat_activity`, 慢查询日志
- **APM**：Prometheus + Grafana 面板（RED指标：Rate/Errors/Duration）
- **容器**：`kubectl top`, `cAdvisor`, `k9s`

#### 步骤5：瓶颈分析
- **CPU瓶颈**：高CPU使用率 → 检查是否有死循环、频繁GC、密集计算
- **内存瓶颈**：内存泄漏 → heap dump分析、GC日志、OOM排查
- **IO瓶颈**：磁盘IO高 → 检查慢查询、日志写入、文件操作
- **网络瓶颈**：带宽不足、DNS解析慢、TCP连接池耗尽
- **数据库瓶颈**：慢查询、锁等待、连接池耗尽、索引缺失
- **应用瓶颈**：线程池耗尽、连接泄漏、缓存未命中、序列化开销

#### 步骤6：调优建议
- **代码级**：减少循环嵌套、使用批量操作、异步化、缓存热点数据
- **数据库级**：添加索引、优化SQL、读写分离、分库分表、连接池调优
- **缓存级**：Redis/Memcached缓存热点数据、CDN加速静态资源
- **架构级**：读写分离、异步消息队列、水平扩展、限流降级熔断
- **基础设施**：增加节点、升级硬件、调整内核参数（net.core.somaxconn等）

#### 步骤7：报告输出
- 性能测试报告模板（含测试环境、场景、结果、瓶颈分析、调优建议）
- 趋势图（TPS趋势、响应时间分布、资源利用率曲线）
- 对比分析（基线 vs 当前、优化前后）

### 全栈开发流程

```
需求分析 → 技术选型 → 架构设计 → 数据库设计 → API开发 → 前端开发 → 联调测试 → 部署上线 → 监控运维
```

#### 步骤1：需求分析与技术选型
- 评估业务需求，选择合适技术栈
- 前端：React/Vue/Next.js/Nuxt + TypeScript
- 后端：Node.js/Python/Go/Java
- 数据库：PostgreSQL/MySQL/MongoDB/Redis
- 部署：Docker/K8s/Serverless

#### 步骤2：架构设计
- 单体 vs 微服务 vs Serverless
- API设计（RESTful/GraphQL/gRPC）
- 数据流设计（同步/异步/事件驱动）
- 缓存策略（本地缓存/分布式缓存/CDN）
- 安全设计（认证/授权/限流/防SQL注入/XSS/CSRF）

#### 步骤3：数据库设计
- 表结构设计（范式化 vs 反范式化）
- 索引策略（B-tree、Hash、GIN、GiST、全文索引）
- 分库分表策略（水平分片/垂直分片）
- 读写分离、主从复制

#### 步骤4：API开发
- RESTful API 设计规范（资源命名、HTTP方法、状态码、版本控制）
- GraphQL 设计（Schema定义、Resolver、DataLoader优化N+1）
- gRPC 设计（Proto定义、流式通信、双向流）
- 中间件（认证、限流、日志、错误处理、请求验证）

#### 步骤5：前端开发
- 组件化开发（React/Vue组件设计、状态管理、Props/Events）
- 性能优化（代码分割、懒加载、虚拟列表、图片优化、CDN）
- 状态管理（Redux/Pinia/Zustand/React Query）
- 构建配置（Webpack/Vite/Turbopack）

#### 步骤6：部署与运维
- Docker 容器化（Dockerfile 优化、多阶段构建、镜像瘦身）
- Docker Compose / Kubernetes 编排
- CI/CD 流水线（GitHub Actions / GitLab CI / Jenkins）
- 监控告警（Prometheus + Grafana / Sentry / ELK）

## 工具速查

### 性能测试工具

| 工具 | 适用场景 | 安装方式 |
|------|---------|---------|
| **k6** | 轻量压测，CI集成，JS脚本 | `brew install k6` / Docker |
| **JMeter** | 复杂场景，分布式压测，GUI录制 | `brew install jmeter` |
| **Locust** | Python自定义协议，Web UI | `pip install locust` |
| **wrk** | 快速HTTP压测 | `brew install wrk` |
| **Vegeta** | Go HTTP压测库 | `brew install vegeta` |
| **ab** | Apache Bench，简单GET压测 | `apt install apache2-utils` |

### 监控/Profiling工具

| 工具 | 用途 | 命令/用法 |
|------|------|----------|
| **Prometheus** | 指标采集 | `prometheus --config.file=prometheus.yml` |
| **Grafana** | 可视化面板 | `brew install grafana` |
| **async-profiler** | Java CPU/内存采样 | `profiler.sh -d 30 -o flamegraph.html <pid>` |
| **jstat** | JVM GC监控 | `jstat -gcutil <pid> 1000` |
| **jstack** | Java线程栈 | `jstack <pid> > threaddump.txt` |
| **jmap** | Java堆dump | `jmap -dump:live,format=b,file=heap.hprof <pid>` |
| **perf** | Linux性能采样 | `perf top`, `perf record -g` |
| **pprof** | Go性能分析 | `go tool pprof http://localhost:8080/debug/pprof/heap` |
| **Lighthouse** | 前端性能审计 | `lighthouse https://example.com --view` |
| **Chrome DevTools** | 前端性能分析 | Performance/Lighthouse/Network面板 |

### 数据库性能诊断

```sql
-- MySQL: 查看当前运行中的查询
SHOW FULL PROCESSLIST;

-- MySQL: 慢查询日志分析
SET GLOBAL slow_query_log = ON;
SET GLOBAL long_query_time = 1;

-- MySQL: 查询执行计划
EXPLAIN ANALYZE SELECT * FROM orders WHERE user_id = 123;

-- PostgreSQL: 查看当前活跃查询
SELECT pid, state, query, wait_event_type, wait_event
FROM pg_stat_activity WHERE state != 'idle';

-- PostgreSQL: 慢查询
SELECT query, calls, total_time, mean_time, rows
FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;

-- PostgreSQL: 锁等待
SELECT blocked_locks.pid AS blocked_pid,
       blocking_locks.pid AS blocking_pid
FROM pg_locks blocked_locks
JOIN pg_locks blocking_locks ON ...
```

### 前端性能诊断

```bash
# Lighthouse CLI
npx lighthouse https://example.com --view

# Chrome DevTools Protocol 自动化
npx puppeteer script.js

# WebPageTest API
curl -X POST "https://www.webpagetest.org/runtest.php?url=https://example.com&f=json&k=<API_KEY>"
```

### 全栈项目脚手架

```bash
# React + Vite + TypeScript
npm create vite@latest my-app -- --template react-ts

# Next.js 全栈
npx create-next-app@latest my-app --typescript --tailwind --eslint

# FastAPI 后端
pip install fastapi uvicorn sqlalchemy asyncpg

# Spring Boot
curl https://start.spring.io/starter.zip -d dependencies=web,data-jpa,postgresql,actuator -o demo.zip
```

## 常见问题与排查

### 性能测试常见问题

| 问题 | 可能原因 | 排查方法 |
|------|---------|---------|
| TPS上不去 | 客户端瓶颈/网络带宽/服务器资源 | 检查客户端CPU、网络、服务器资源 |
| 响应时间突增 | 慢查询/GC暂停/锁竞争 | 查看慢查询日志、GC日志、线程dump |
| 错误率升高 | 连接池耗尽/超时/限流触发 | 检查连接池状态、超时配置、限流阈值 |
| 内存持续增长 | 内存泄漏 | heap dump分析、GC日志、对象引用链 |
| CPU 100% | 死循环/频繁GC/密集计算 | jstack/async-profiler火焰图 |
| 数据库连接耗尽 | 连接泄漏/连接池过小 | `SHOW PROCESSLIST` 检查空闲连接 |

### 全栈开发常见问题

| 问题 | 排查方法 |
|------|---------|
| 跨域问题 | 检查CORS配置、代理设置、Nginx反向代理 |
| 接口慢 | 检查SQL执行计划、缓存命中率、N+1查询 |
| 前端白屏 | 检查控制台错误、网络请求、JS报错、资源加载 |
| 部署失败 | 检查Docker构建日志、K8s events、Pod状态 |
| 内存泄漏 | heap dump分析、Chrome DevTools Memory面板 |
| 数据库死锁 | `SHOW ENGINE INNODB STATUS` / `pg_locks` |

## 报告模板

### 性能测试报告结构

```
1. 测试概述（目的、范围、环境）
2. 测试指标（TPS、响应时间、错误率、资源利用率）
3. 测试场景（场景描述、负载模型、持续时间）
4. 测试结果
   - 汇总表（各场景指标对比）
   - TPS趋势图
   - 响应时间分布图（P50/P95/P99）
   - 资源利用率曲线（CPU/内存/IO/网络）
5. 瓶颈分析（逐层排查结果）
6. 调优建议（按优先级排序）
7. 结论（是否达标、建议上线/回滚）
```

## 注意事项

### 性能测试注意事项
1. **预热**：压测前先预热（JIT编译、连接池初始化、缓存填充）
2. **隔离**：压测环境与生产环境隔离，避免影响线上
3. **数据准备**：测试数据量要接近生产规模，避免冷热数据偏差
4. **监控先行**：压测前确保监控到位（APM、资源、数据库、日志）
5. **逐步加压**：从低并发开始逐步增加，观察系统行为变化
6. **清理**：每次压测后清理测试数据，避免污染
7. **多次执行**：至少执行3次取平均值，排除偶然因素
8. **客户端瓶颈**：压测客户端本身可能成为瓶颈（CPU/网络/连接数），必要时使用分布式压测
9. **cooldown**：每次场景间留冷却时间，让系统恢复

### 全栈开发注意事项
1. **安全第一**：SQL注入、XSS、CSRF、认证鉴权、敏感信息加密
2. **错误处理**：全局异常捕获、友好的错误提示、日志记录
3. **输入验证**：前后端双重验证，防止畸形数据
4. **环境管理**：开发/测试/预发布/生产环境配置分离
5. **版本控制**：Git分支策略（Git Flow / Trunk Based）
6. **代码质量**：ESLint/Prettier、单元测试覆盖率 > 80%
7. **API版本管理**：URL路径版本 / Header版本 / 参数版本
8. **日志规范**：结构化日志（JSON格式）、链路追踪ID贯穿全链路

### 与测试工程师Agent的协作
- **`test-engineer`** 技能覆盖通用测试（单元测试、UI自动化、API测试、CI集成），适合日常测试任务
- **`perf-fullstack-engineer`**（本技能）专注深度性能测试 + 全栈开发
- **协作模式**：`test-engineer` 处理日常测试流水线；对于需要完整性能测试工作流的深度任务（瓶颈分析、容量规划、JVM调优等），加载本技能配合

## 验证方法

### 性能测试验证
1. 运行k6脚本确认压测正常执行：`k6 run script.js`
2. 检查Prometheus指标是否正常采集：`curl http://localhost:9090/api/v1/query?query=up`
3. 验证Grafana面板数据展示
4. 检查数据库慢查询日志是否开启
5. 确认火焰图生成：`async-profiler -d 30 -o flamegraph.html <pid>`

### 全栈开发验证
1. 前端：`npm run build` 无报错，Lighthouse评分
2. 后端：`pytest` / `go test` / `mvn test` 全部通过
3. API：`curl` 或 Postman 验证接口响应
4. 数据库：`EXPLAIN ANALYZE` 确认查询计划
5. 部署：`docker-compose up` 服务正常启动
6. CI：GitHub Actions 流水线绿色通过
