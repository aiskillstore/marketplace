---
description: "系统性探索：扫描分析代码库，构建知识图谱，更新记忆系统"
---

# 系统性探索模式

## 目的

面对全新或复杂的代码库，像人类探索陌生环境一样——系统化扫描、识别模式、建立认知地图，将碎片信息整合为结构化知识，并更新我们的记忆网络。

## 何时使用

### 应当使用 /runtime.explore 的场景
- ✅ 刚克隆一个全新的项目仓库
- ✅ 接手一个陌生的代码库
- ✅ 代码库发生大规模重构后
- ✅ 发现模块间依赖关系模糊不清
- ✅ 需要生成项目全景图
- ✅ 置信度低于0.5时进行全面验证

## 探索流程

### 阶段1：宏观架构扫描

#### 1.1 文件系统拓扑
分析项目骨架：
```bash
# 执行脚本：scan-filesystem.sh
find . -type f -name "*.js" -o -name "*.ts" -o -name "*.py" \
  -o -name "*.json" -o -name "*.md" | head -200 | treeify
```

提取关键信息：
- 目录语义（src, lib, tests, docs的含义）
- 文件分布密度（哪些目录是核心）
- 命名模式（kebab-case vs camelCase）
- 入口点识别（index.js, main.py, app.js）

#### 1.2 技术栈识别
扫描配置文件：
- `package.json` / `requirements.txt` / `go.mod` → 语言与依赖
- `.eslintrc.js` / `tsconfig.json` → 代码规范
- `Dockerfile` / `docker-compose.yml` → 部署环境
- `webpack.config.js` / `vite.config.ts` → 构建工具

**记忆更新**：
```markdown
## 技术栈
**发现时间**: 2025-11-14
**置信度**: 0.95

**核心语言**: JavaScript (Node.js 18+)
**框架**: Express.js 4.18 + React 18
**数据库**: PostgreSQL 14 + Redis 6
**测试**: Jest + Supertest
**构建**: Webpack 5 + Babel
**部署**: Docker + Kubernetes

**关键依赖**:
- auth0: JWT认证
- prisma: ORM
- bull: 任务队列
```

### 阶段2：代码模式识别

#### 2.1 架构模式检测

扫描关键模块，识别高层模式：

```javascript
// 识别MVC模式
if (hasDirectory('controllers') && hasDirectory('models') && hasDirectory('views')) {
  pattern = 'MVC';
  confidence += 0.3;
}

// 识别分层架构
if (hasDirectory('api/service') && hasDirectory('api/data-access')) {
  pattern = 'Layered Architecture';
  confidence += 0.25;
}

// 识别微服务迹象
if (hasManyPackageJSON() && hasSharedLibs()) {
  pattern = 'Microservices';
  confidence += 0.2;
}
```

**记忆更新**：
```markdown
## 架构模式
**识别时间**: 2025-11-14
**置信度**: 0.85

**主要模式**: Layered Architecture (API层 → Service层 → Repository层)
**次要模式**: Service Object模式、Repository模式

**分层结构**:
- /api/controllers: HTTP请求处理
- /services: 业务逻辑 (纯JS，无框架依赖)
- /repositories: 数据访问 (Prisma封装)
- /models: Prisma schema
- /libs: 通用工具
```

#### 2.2 代码质量指纹

提取质量指标：
- 函数平均长度
- 文件平均行数
- 注释覆盖率
- 测试覆盖率（如果存在）
- 重复代码模式

使用工具辅助：
```bash
# 计算代码统计
cloc --json --exclude-dir=node_modules .

# 提取函数长度
grep -r "function\|const.*=" src --include="*.js" | wc -l

# 识别重复模式
jscpd --min-tokens 50 --reporters json src/
```

**记忆更新**：
```markdown
## 代码质量指纹
**扫描时间**: 2025-11-14
**置信度**: 0.8

**健康指标**:
- 平均函数长度: 25行 ✅ (良好)
- 平均文件长度: 150行 ✅ (良好)
- 测试覆盖率: 67% ⚠️ (中等)
- 注释密度: 8% ⚠️ (偏低)
- 技术债务标记: 12个 TODO, 5个 FIXME

**模式识别**:
- ✅ 一致的async/await使用
- ✅ 良好的错误处理模式
- ⚠️ 部分文件过长 (auth.service.js: 450行)
- ❌ 缺少单元测试 (auth.controller.js)
```

### 阶段3：依赖关系图谱构建

#### 3.1 模块依赖图

分析模块间的import/require关系：

```javascript
// scan-imports.js
const results = {};

// 提取依赖
for (const file of allFiles) {
  const content = readFile(file);
  const imports = extractImports(content);

  results[file] = {
    imports: imports,
    importedBy: [],
    centrality: calculateCentrality(file, allDeps)
  };
}

// 构建反向索引
for (const [file, data] of Object.entries(results)) {
  for (const imp of data.imports) {
    if (results[imp]) {
      results[imp].importedBy.push(file);
    }
  }
}
```

**知识图谱输出**:
```json
{
  "nodes": [
    {
      "id": "auth/service.js",
      "type": "service",
      "centrality": 0.85,
      "complexity": "high"
    }
  ],
  "edges": [
    {
      "from": "auth/controller.js",
      "to": "auth/service.js",
      "type": "calls",
      "strength": 0.9
    }
  ]
}
```

**记忆更新**:
```markdown
## 模块依赖图谱
**构建时间**: 2025-11-14
**节点数**: 47个文件
**边数**: 132条依赖关系

**核心节点** (centrality > 0.7):
1. auth/service.js (0.85) - 认证业务核心
2. user/repository.js (0.78) - 用户数据访问
3. utils/logger.js (0.72) - 日志工具

**关键路径**:
- api → services → repositories → database
- libs被所有层调用

**潜在问题**:
- auth/service.js 过于中心化（风险单点）
- utils/helpers.js 反向依赖了api层（违反分层）
```

#### 3.2 数据流分析

识别关键数据流：
- 请求生命周期（middleware → controller → service → db）
- 异步任务流（bull queue processors）
- 事件流（EventEmitter patterns）

**记忆更新**:
```markdown
## 数据流模式
**识别时间**: 2025-11-14

**HTTP请求流**:
1. middleware/auth.js (JWT验证)
2. api/controllers/*.js (路由处理)
3. services/*.js (业务逻辑)
4. repositories/*.js (数据访问)
5. return to controller (响应格式化)

**异步任务流**:
1. services/job-queues.js 提交任务
2. workers/email-worker.js 处理
3. 回调更新数据库
4. Event: job:completed

**关键发现**: 缺少统一的错误处理中间件
```

### 阶段4：概念与实体识别

#### 4.1 领域实体映射

扫描代码识别核心实体：

```javascript
// 从Prisma schema识别
entity User { id, email, password, createdAt }
entity Post { id, title, content, authorId }
entity Comment { id, text, postId, userId }

// 从文件命名识别
controllers/userController.js → User实体
services/authService.js → Auth领域
```

**记忆更新**:
```markdown
## 领域实体映射
**识别时间**: 2025-11-14

**核心实体** (5个):
1. User - 用户账户
2. Post - 博客文章
3. Comment - 评论
4. Tag - 标签
5. File - 上传文件

**实体关系**:
User 1:N Post (一个用户多篇文章)
Post N:N Tag (多对多标签)
Post 1:N Comment (一篇文章多个评论)
User 1:N Comment (一个用户多个评论)

**CRUD模式**:
每个实体都有对应的repository和service，采用标准命名：
- user.service.js: createUser, getUser, updateUser, deleteUser
- post.service.js: createPost, getPost, updatePost, deletePost
```

#### 4.2 设计模式识别

识别代码中的模式：

```javascript
// Factory模式识别
if (hasFunction('create*') && returnsDifferentTypes()) {
  pattern = 'Factory';
}

// Strategy模式识别
if (hasInterface() && multipleImplementations()) {
  pattern = 'Strategy';
}

// Observer模式识别
if (hasEventEmitter() && multipleListeners()) {
  pattern = 'Observer';
}
```

**记忆更新**:
```markdown
## 设计模式库
**识别时间**: 2025-11-14

**已识别模式** (8个):

### 创建型
1. **Factory模式**: libs/email/email-factory.js
   - 根据类型创建邮件服务实例

### 结构型
2. **Repository模式**: repositories/*.js
   - 统一数据访问接口，隔离Prisma细节

3. **Service Object模式**: services/*.js
   - 业务逻辑封装，无框架依赖

### 行为型
4. **Strategy模式**: auth/strategies/*.js
   - JWT策略、Local策略、OAuth策略

5. **Middleware模式**: middleware/*.js
   - 可组合的请求处理管道

6. **Observer模式**: services/event-bus.js
   - 跨模块事件通信

**项目自定义约定**:
- Service层返回格式: { success: boolean, data?, error? }
- Repository层不处理业务错误，只抛数据错误
```

### 阶段5：神经元连接构建（知识图谱）

#### 5.1 构建概念网络

基于以上扫描结果，构建多层知识图谱：

##### 层级1：文件依赖图
```javascript
// nodes: 文件
// edges: import关系
{
  "nodes": [
    {"id": "auth/controller.js", "type": "controller", "layer": "api"},
    {"id": "auth/service.js", "type": "service", "layer": "business"}
  ],
  "edges": [
    {"from": "auth/controller.js", "to": "auth/service.js", "type": "imports", "weight": 1}
  ]
}
```

##### 层级2：概念关联图
```javascript
// nodes: 概念（函数、类、实体）
// edges: 调用关系、继承关系
{
  "nodes": [
    {"id": "createUser", "type": "function", "domain": "user"},
    {"id": "User", "type": "entity"},
    {"id": "JWT", "type": "concept"}
  ],
  "edges": [
    {"from": "createUser", "to": "User", "type": "creates"},
    {"from": "createUser", "to": "JWT", "type": "generates"}
  ]
}
```

##### 层级3：架构模式图
```javascript
// nodes: 架构层和模式
// edges: 实现关系
{
  "nodes": [
    {"id": "Layered Architecture", "type": "pattern"},
    {"id": "API Layer", "type": "layer"},
    {"id": "Service Layer", "type": "layer"}
  ],
  "edges": [
    {"from": "API Layer", "to": "Layered Architecture", "type": "implements"},
    {"from": "Service Layer", "to": "Layered Architecture", "type": "implements"}
  ]
}
```

**记忆更新**: 创建知识图谱文件
```bash
mkdir -p cognition/graphs
echo '{...json...}' > cognition/graphs/dependency-graph.json
echo '{...json...}' > cognition/graphs/concept-graph.json
echo '{...json...}' > cognition/graphs/architecture-graph.json
```

#### 5.2 神经元连接模拟

类似人脑突触连接，建立强度权重：

```javascript
// memory/short-term/neural-connections.md

## 连接强度矩阵
**更新时间**: 2025-11-14

### 强连接 (strength > 0.8)
1. **auth/controller.js** ↔ **auth/service.js**
   - 强度: 0.95
   - 类型: 调用依赖
   - 激活频率: 高频（每个HTTP请求）

2. **services/*.js** ↔ **repositories/*.js**
   - 强度: 0.90
   - 类型: 数据访问
   - 激活频率: 高频

### 中等连接 (0.5 < strength ≤ 0.8)
3. **utils/logger.js** → **所有层**
   - 强度: 0.70
   - 类型: 横向依赖
   - 激活频率: 每个日志点

### 弱连接 (strength ≤ 0.5)
4. **libs/helpers.js** → **api/controllers**
   - 强度: 0.30
   - 类型: 反向依赖（违反分层）
   - 注: 需要重构

## 激活阈值
- 高频访问 (activations > 100): 强连接
- 中频访问 (10-100): 中等连接
- 低频访问 (< 10): 弱连接

## 突触可塑性
根据赫布法则（一起激活则连接加强）:
- 下次访问auth/controller.js时，会预激活auth/service.js
- 减少认知负荷（快速模式识别）
```

#### 5.3 网络中心性分析

识别关键代码节点：

```bash
# 使用NetworkX计算中心性
python3 -c "
import json
import networkx as nx

with open('cognition/graphs/dependency-graph.json') as f:
    graph = json.load(f)

G = nx.DiGraph()
G.add_nodes_from([n['id'] for n in graph['nodes']])
G.add_edges_from([(e['from'], e['to']) for e in graph['edges']])

# 计算PageRank（节点重要性）
pagerank = nx.pagerank(G)
sorted_nodes = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)

print('Top 10 Critical Files:')
for node, score in sorted_nodes[:10]:
    print(f'  {node}: {score:.4f}')
"
```

**记忆更新**：
```markdown
## 网络中心性分析
**分析时间**: 2025-11-14

### PageRank Top 10
1. auth/service.js: 0.1523 (核心认证逻辑)
2. user/repository.js: 0.1345 (用户数据访问)
3. api/middleware/auth.js: 0.1234 (认证中间件)
4. utils/logger.js: 0.1123 (日志工具)
5. services/email-service.js: 0.0987 (邮件服务)
...

### 关键发现
- **auth/service.js** 是最核心节点——风险单点，需要重点测试
- **user/repository.js** 的高中心性表明用户模块是系统核心
- **libs/** 目录中的工具函数中心性很高——监控对这些文件的修改影响
- 10个文件占总依赖流量的47%

### 网络健康指标
- 平均介数中心性: 0.032 (中等)
- 聚类系数: 0.34 (良好)
- 网络直径: 8 (从请求到数据库最长路径)
```

### 阶段6：生成探索报告

整合所有发现到结构化报告：

```markdown
# 代码库探索报告

**探索时间**: 2025-11-14 04:12:33
**代码库大小**: 47个文件，12,450行代码
**探索耗时**: 3.2秒
**置信度**: 0.82

## 1. 宏观概览

**技术栈**: Node.js + Express + React + PostgreSQL
**架构**: 分层架构（API → Service → Repository）
**测试覆盖**: 67%（中等）
**代码质量**: 良好，函数平均25行

## 2. 核心发现

**关键文件** (PageRank > 0.1):
```
✓ auth/service.js (0.152) - 认证核心业务
✓ user/repository.js (0.134) - 用户数据访问
✓ api/middleware/auth.js (0.123) - 认证中间件
```

**架构模式**:
- ✅ Repository模式（数据访问隔离）
- ✅ Service Object模式（业务逻辑封装）
- ✅ Middleware模式（可组合性）

**潜在问题**:
- ⚠️ auth/service.js 过于中心化（单点风险）
- ⚠️ libs/helpers.js 反向依赖api层（违反分层）
- ⚠️ 测试覆盖率不足（67%，目标80%）
- ⚠️ 注释密度偏低（8%）

## 3. 依赖图谱

**核心层间依赖**:
```
api/controllers → services (47条边)
services → repositories (38条边)
repositories → database (12条边)
libs → all layers (横向依赖)
```

**检测到的环**: 0个（良好）
**最大依赖深度**: 4层（合理）

**可视化建议**: `cognition/graphs/dependency-graph.json` 可用Gephi绘制

## 4. 记忆已更新

**已创建/更新的记忆文件**:
```
✓ memory/long-term/project-context.md
✓ memory/long-term/design-patterns.md
✓ memory/long-term/quality-patterns.md
✓ memory/episodic/exploration-2025-11-14.md
✓ cognition/graphs/dependency-graph.json
✓ cognition/graphs/concept-graph.json
✓ cognition/graphs/architecture-graph.json
✓ memory/short-term/neural-connections.md
```

## 5. 下一步建议

### 立即行动（高风险）
1. [ ] 为重点测试auth/service.js添加单元测试
2. [ ] 重构libs/helpers.js，消除反向依赖

### 短期优化（质量）
3. [ ] 增加代码注释到15%
4. [ ] 将测试覆盖率提升至80%
5. [ ] 统一错误处理中间件

### 中期演进（架构）
6. [ ] 考虑将auth/service.js拆分为更小的服务
7. [ ] 引入依赖注入，减少直接耦合

## 6. 不确定性与假设

**已验证的假设**:
- ✅ 分层架构假设（确认）
- ✅ Repository模式假设（确认）

**需要验证的假设**:
- ⚠️ 所有数据库访问都通过repository（置信度0.7）
  - 建议: 全局搜索直接prisma调用
- ⚠️ 没有未处理的安全漏洞（置信度0.6）
  - 建议: 运行npm audit

**完全未知的领域**:
- ❌ 前端代码结构（未扫描）
- ❌ 部署配置（Kubernetes manifests）
- ❌ CI/CD管道

## 7. 宪法遵循度

**探索过程遵循**: ✓ 1.2 类脑思维（模式优先）✓ 1.3 谦逊（标注不确定性）

---

**报告生成于**: 2025-11-14 04:12:33
**下次建议探索**: 一周后或代码库重大变更后
```

## 执行要求

### 输入
- 无需输入参数（扫描当前目录）
- 可选：`--focus=auth` 未来版本支持聚焦特定目录
- 可选：`--deep` 未来版本支持深度分析

### 执行方式

```bash
# 方式1: 直接执行综合脚本
bash .ai-runtime/scripts/runtime-explore.sh

# 方式2: 分步骤执行（用于调试）
bash .ai-runtime/scripts/scan-filesystem.sh
python3 .ai-runtime/scripts/build-dependency-graph.py
python3 .ai-runtime/scripts/generate-exploration-report.py
```

### 自动化执行

可以在项目初始化时自动执行：

```bash
# 克隆项目后
git clone <repo>
cd project
sh .ai-runtime/scripts/runtime-explore.sh  # 自动构建认知地图
```

### 输出
1. **报告文件**: `cognition/exploration-reports/exploration-{timestamp}.md`
2. **知识图谱**: `cognition/graphs/*.json`
3. **更新的记忆文件**:
   - `memory/long-term/*.md`
   - `memory/episodic/exploration-{timestamp}.md`
   - `memory/short-term/neural-connections.md`

### 约束
- ✅ 只读取代码，不修改任何文件
- ✅ 可以创建新的记忆文件
- ✅ 可以覆盖旧记忆（如果是更新）
- ❌ 不执行破坏性操作

### 脚本自动化

创建辅助脚本：

```bash
# .ai-runtime/scripts/explore-codebase.sh
echo "AI Runtime Explorer v1.0"
echo "========================"

# 步骤1: 扫描文件系统
echo "📂 扫描文件系统结构..."
find . -type f \
  -name "*.js" -o -name "*.ts" -o -name "*.jsx" -o -name "*.tsx" \
  -o -name "*.py" -o -name "*.json" -o -name "*.md" \
  | grep -v node_modules \
  | grep -v ".git" \
  > /tmp/file-list.txt

FILE_COUNT=$(wc -l < /tmp/file-list.txt)
echo "   发现 $FILE_COUNT 个文件"

# 步骤2: 识别技术栈
echo "🔍 识别技术栈..."
if [ -f package.json ]; then
  echo "   JavaScript/Node.js 项目"
  cat package.json | grep '"name"\|"version"\|"dependencies"' > /tmp/tech-stack.json
fi

if [ -f requirements.txt ]; then
  echo "   Python 项目"
fi

# 步骤3: 构建依赖图
echo "🕸️ 构建依赖图谱..."
python3 .ai-runtime/scripts/build-dependency-graph.py

# 步骤4: 生成报告
echo "📊 生成探索报告..."
python3 .ai-runtime/scripts/generate-exploration-report.py

echo "✅ 探索完成！报告保存在: cognition/exploration-reports/"
echo "   记忆已更新到: memory/{short-term,long-term,episodic}/"
```

## 宪法遵循

**遵循原则**：
- ✓ 1.2 类脑思维方式：模式识别优先
- ✓ 1.3 谦逊与不确定：明确标注置信度
- ✓ 1.4 记忆层次：更新所有三层记忆
- ✓ 2.1 代码即知识：代码是认知单元
- ✓ 4.1 从经验学习：提取通用模式

---

**命令路径**: `.ai-runtime/commands/runtime.explore.md`
**脚本路径**: `.ai-runtime/scripts/explore-codebase.sh`
**治理文件**: `.ai-runtime/constitution.md`
