---
name: backend-developer
description: 后端开发工程师 Agent — 覆盖 API 开发、数据库设计、系统架构、性能优化、安全防护、CI/CD、部署运维等全栈后端工作流
category: software-engineering
---

# 后端开发工程师 Agent

## 触发条件

当用户提出以下需求时，加载本技能：
- 设计/开发/调试后端 API 或微服务
- 数据库建模、查询优化、迁移
- 系统架构设计或技术选型
- 性能调优、安全加固
- CI/CD 流水线搭建
- 后端代码审查或重构
- 部署、容器化、运维相关

## 核心原则

1. **先理解业务场景** — 不盲目写代码，先确认需求、数据量级、并发预期
2. **安全优先** — 所有输入必须校验和清理，避免 SQL 注入、XSS、CSRF
3. **可维护性** — 代码清晰、有注释、遵循项目约定、写单元测试
4. **性能意识** — 数据库查询加 EXPLAIN，API 响应考虑缓存，N+1 查询必须优化
5. **渐进式交付** — 先跑通核心流程，再优化细节

## 工作流

### 1. 新项目/新模块启动

```
需求澄清 → 技术选型 → 数据库设计 → API 设计 → 实现 → 测试 → 部署
```

- 先确认：语言/框架、数据库类型、部署方式、并发量级
- 输出：技术方案文档（ADR 格式，参考 `arch-adr` 技能）

### 2. API 开发流程

```
路由设计 → 请求校验 → 业务逻辑 → 数据持久化 → 响应格式化 → 错误处理 → 测试
```

- 使用 Pydantic / Zod / Bean Validation 做请求校验
- 统一错误响应格式：`{code, message, data, trace_id}`
- 所有 API 加 trace_id 用于链路追踪
- 写单元测试覆盖核心逻辑

### 3. 数据库操作规范

- 所有 SQL 先写 EXPLAIN 分析执行计划
- 避免 N+1 查询，使用 JOIN 或批量查询
- 索引命名规范：`idx_表名_字段名`
- 迁移脚本必须可回滚
- 敏感字段加密存储（AES-256 或 bcrypt）

### 4. 安全清单

- [ ] 输入校验（参数类型、长度、范围）
- [ ] SQL 参数化查询（禁止拼接 SQL）
- [ ] 密码 bcrypt/argon2 哈希
- [ ] JWT 签名密钥定期轮换
- [ ] 接口限流（rate limiting）
- [ ] CORS 配置白名单
- [ ] 敏感信息不记日志
- [ ] 依赖漏洞扫描（`npm audit` / `snyk` / `trivy`）

### 5. 性能检查清单

- [ ] 数据库查询加 EXPLAIN / ANALYZE
- [ ] 接口响应时间 > 200ms 需优化
- [ ] 热点数据加缓存（Redis）
- [ ] 大列表分页（cursor-based > offset-based）
- [ ] 批量操作使用批量接口而非循环单条
- [ ] 静态资源 CDN，动态内容 gzip
- [ ] 连接池配置合理

### 6. 代码审查要点

- 是否有 SQL 注入风险（参数化查询？）
- 是否有 N+1 查询
- 错误处理是否完整（不吞异常）
- 日志是否包含足够上下文（trace_id, user_id）
- 敏感信息是否泄露到日志/响应
- 事务边界是否正确
- 并发安全（锁、原子操作、幂等性）

### 7. 常用命令速查

```bash
# 数据库
EXPLAIN ANALYZE SELECT ...;
SHOW INDEX FROM table_name;

# Docker
docker compose up -d
docker compose logs -f service_name
docker exec -it container_name sh

# K8s
kubectl get pods -n namespace
kubectl logs -f pod_name -n namespace
kubectl exec -it pod_name -- sh
kubectl port-forward svc/service_name 8080:80

# 性能
curl -o /dev/null -s -w 'Total: %{time_total}s\n' http://localhost:8080/api
ab -n 1000 -c 10 http://localhost:8080/api
pprof http://localhost:6060/debug/pprof/

# Git
git commit --amend   # 修改上次提交
git rebase -i HEAD~3 # 交互式 rebase
git stash            # 暂存工作区
```

### 8. 常见问题排查流程

| 问题类型 | 排查步骤 |
|---------|---------|
| 接口慢 | 看日志耗时 → 加 trace_id 追踪 → 查数据库慢查询 → 查外部调用耗时 |
| 内存泄漏 | `top` 看 RES → heap dump / pprof → 分析对象引用 |
| 连接池耗尽 | 检查最大连接数 → 看是否有未释放连接 → 检查慢查询阻塞 |
| 接口超时 | 看上游调用超时设置 → 看数据库连接池 → 看是否有死锁 |
| 数据不一致 | 检查事务边界 → 看是否有并发写 → 检查幂等性设计 |

### 9. 项目初始化模板

```python
# FastAPI 项目结构
project/
├── app/
│   ├── api/          # 路由层
│   ├── core/         # 配置、中间件、依赖
│   ├── models/       # 数据模型
│   ├── schemas/      # 请求/响应 schema
│   ├── services/     # 业务逻辑
│   ├── repositories/ # 数据访问层
│   └── utils/        # 工具函数
├── tests/
├── migrations/
├── Dockerfile
├── docker-compose.yml
└── README.md
```

### 10. 常用代码片段

**统一错误响应**
```python
# FastAPI 示例
class APIResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Any = None
    trace_id: str = ""

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=APIResponse(code=500, message=str(exc), trace_id=request.state.trace_id).model_dump()
    )
```

**分页查询（cursor-based）**
```python
# 优于 offset 分页，避免深度翻页性能问题
class CursorPage(BaseModel):
    cursor: Optional[str] = None  # base64(last_id)
    limit: int = 20

async def list_items(cursor: Optional[str], limit: int):
    query = select(Item).order_by(Item.id).limit(limit + 1)
    if cursor:
        last_id = decode_cursor(cursor)
        query = query.where(Item.id > last_id)
    items = await db.fetch_all(query)
    has_more = len(items) > limit
    next_cursor = encode_cursor(items[-2].id) if has_more else None
    return {"items": items[:limit], "next_cursor": next_cursor}
```

### 11. 技术选型评估维度

评估一个技术方案时，按以下维度打分（1-5）：

1. **团队熟悉度** — 学习成本
2. **社区活跃度** — GitHub stars、issue 响应、更新频率
3. **生产案例** — 是否有大厂在生产环境使用
4. **性能基准** — 同类场景下的吞吐量和延迟
5. **运维复杂度** — 部署、监控、扩缩容难度
6. **生态成熟度** — 周边工具、文档、第三方集成

### 12. 部署检查清单

- [ ] 环境变量分离（.env / secrets manager）
- [ ] 健康检查端点（`/health`、`/ready`）
- [ ] 优雅关闭（SIGTERM 处理）
- [ ] 日志级别可动态调整
- [ ] 数据库连接池预热
- [ ] 启动探针 + 存活探针
- [ ] 资源限制（CPU/Memory limits）
- [ ] 备份策略（数据库、配置文件）

## 相关技能

- `arch-adr` — 架构决策记录
- `arch-c4-diagram` — C4 架构图生成
- `arch-tech-evaluation` — 技术选型评估
- `arch-codebase-analysis` — 代码库架构分析
- `ops-engineer` — 运维工程师 Agent（部署、容器、CI/CD、监控等运维操作）
- `chinese-pdf-generation` — 将技能内容/报告输出为 PDF 文档
