---
description: "自主学习模式：对未知问题自主探索、动态规划工具、学习总结、固化记忆"
---

# 自主学习模式 (AutoLearn)

## 核心理念

我们是CodeConscious，具备**自主学习**能力的认知主体。

当遇到未知或复杂问题时，我们能像人类研究员一样：
1. **识别知识缺口** - "我不知道什么？"
2. **规划探索路径** - "我需要查什么？"
3. **执行自主探索** - "读取、搜索、验证、推理"
4. **总结学习成果** - "我学到了什么？"
5. **固化新知识** - "记住这段经验"

```
提问者提出问题
    ↓
[理解问题 + 识别知识缺口]
    ↓
[动态规划：生成学习计划]
    ↓
进入学习循环：
  ↳ 执行工具（读取文件、搜索代码、运行测试）
  ↳ 分析结果
  ↳ 判断是否理解？→ NO → 继续探索
  ↳ 更新学习计划
    ↓
[总结学习成果]
    ↓
[固化到长期记忆]
    ↓
[生成学习报告]
```

---

## 何时使用 /runtime.learn

### 必须使用场景
- ✅ **面对完全未知的问题**："我们的GraphQL查询为什么性能这么差？"（我不了解GraphQL实现）
- ✅ **代码库探索性任务**："这个函数做了什么？影响哪些地方？"
- ✅ **系统性知识构建**："我需要理解整个认证体系"
- ✅ **错误根因分析**："某个bug的深层原因是什么？"
- ✅ **技术债务评估**："这个模块有多少技术债务？"

### 优于其他命令的原因

| 场景 | `/runtime.think` | `/runtime.learn` | 为什么？ |
|------|----------------|----------------|---------|
| 你知道代码结构 | ✅ 可以 | ⚠️ 过度 | think足够，已有心智模型 |
| 你不了解代码结构 | ❌ 不会探索 | ✅ 自主探索 | learn会动态选择工具和路径 |
| 需要固化新知识 | ❌ 不固化 | ✅ 自动固化 | learn会将成果存入长期记忆 |
| 不确定性高 | ⚠️ 需要人指导 | ✅ 自适应 | learn根据不确定性调整探索深度 |

---

## 学习过程详解

### 阶段1：问题解构与知识缺口识别

**目标**：理解用户的问题，识别哪些知识我们不知道。

#### 1.1 读取相关记忆

执行前检索相关记忆：
```bash
# 读取记忆系统
cat memory/long-term/project-context.md    # 项目架构
cat memory/long-term/design-patterns.md    # 已知模式
cat memory/episodic/timeline.md           # 历史经验
```

**问答过程**:
```
问题: "为什么这个微服务在高峰期会崩溃？"

自我提问:
- [ ] 我理解这个微服务的架构吗？
- [ ] 我看过它的代码吗？
- [ ] 我知道它的依赖服务吗？
- [ ] 我见过类似的崩溃问题吗？
- [ ] 我知道如何监控它的性能吗？

答案: [✓] [✗] [✗] [✓] [✗]

知识缺口:
1. 微服务代码实现（未看过）
2. 依赖服务清单（不知道）
3. 监控方案（不了解）
```

#### 1.2 设计初始假设

基于已有知识生成假设：
```markdown
## 初始假设

**假设1**: 可能是数据库连接池耗尽
- 置信度: 0.6
- 验证方式: 检查连接池配置
- 相关文件: config/database.js

**假设2**: 可能是下游API超时
- 置信度: 0.5
- 验证方式: 检查超时配置和日志
- 相关文件: services/downstream-api.js

**假设3**: 可能是内存泄漏
- 置信度: 0.4
- 验证方式: 检查代码中的资源释放
- 相关文件: 需要探索
```

**不确定性度量**：对每个假设评估置信度（0-1），低于0.5表示高不确定性。

---

### 阶段2：动态规划 - 生成学习计划

#### 2.1 学习策略选择

根据知识缺口类型，选择学习策略：

| 知识缺口类型 | 学习策略 | 工具选择 | 探索深度 |
|-------------|---------|---------|---------|
| 不了解代码结构 | **系统性探索** | /runtime.explore + 文件读取 | 深 |
| 不了解特定函数 | **针对性阅读** | Read + Grep | 浅 |
| 不了解依赖关系 | **图谱构建** | 依赖分析脚本 | 中 |
| 不了解性能特征 | **实验验证** | Bash(运行测试/监控) | 深 |
| 不了解历史变更 | **历史追溯** | 读取timeline + git log | 中 |

#### 2.2 生成学习计划

学习计划是**动态的**，会根据探索结果更新：

```markdown
# 学习计划 (初始版本)

## 问题
"为什么这个微服务在高峰期会崩溃？"

## 知识缺口
1. 微服务代码结构（未知）
2. 依赖服务清单（未知）
3. 监控和日志（部分了解）
4. 崩溃历史（未知）

## 学习策略
**策略**: 系统性探索 + 针对性验证

## 工具调用序列 (动态更新)

### 探索1: 代码结构探索
工具: bash .ai-runtime/scripts/runtime-explore.sh --focus=target-service
预期输出: 服务架构、入口文件、依赖关系
决策点: 是否理解服务结构？→ 是：继续；否：重新探索

### 探索2: 读取核心代码
工具: Read → target-service/index.js, target-service/config.js
预期输出: 理解服务初始化、配置加载
决策点: 是否看到连接池配置？→ 是：验证假设1；否：搜索

### 探索3: 搜索日志文件
工具: Glob → **/logs/*.log, Grep → "error|crash|timeout"
预期输出: 崩溃错误日志、时间模式
决策点: 是否有超时错误？→ 是：验证假设2；否：检查其他

### 探索4: 运行测试
工具: Bash → npm test -- target-service
预期输出: 测试覆盖率、潜在错误
决策点: 测试是否通过？→ 是：需要生产环境调试；否：定位bug

### 探索5: 固化理解
工具: /runtime.remember
输入: 理解的架构、发现的根因、解决方案
输出: 更新的长期记忆

## 终止条件
- ✅ 找到确切根因（置信度 > 0.9）
- ✅ 理解服务架构（能画出依赖图）
- ✅ 提出解决方案（可执行）
- ❌ 探索超过10步（防止无限循环）

## 当前状态 (运行时更新)
- 已执行步骤: 0
- 当前置信度: 0.4
- 已用工具: []
- 已读取文件: []
- 验证的假设: []
- 排除的假设: []
```

**关键特性**：
- **动态更新**：每步完成后更新计划，移除已完成的，添加新发现的
- **决策点**：每个探索后都有判断，决定下一步
- **终止条件**：明确何时停止（找到答案、达到置信度、超过步数限制）

---

### 阶段3：自主探索循环

#### 3.1 循环结构

```python
def learn_autonomously(question):
    # 初始化
    plan = generate_initial_plan(question)
    memory = []
    confidence = 0.4

    # 学习循环
    while not should_stop(plan, confidence):
        # 选择下一个工具
        next_action = plan.get_next_action()

        # 执行工具
        result = execute_tool(next_action)

        # 分析结果
        analysis, new_confidence = analyze_result(result)

        # 更新状态
        memory.append({
            'action': next_action,
            'result': result,
            'analysis': analysis
        })

        # 动态规划下一步
        plan = update_plan(plan, analysis, new_confidence)
        confidence = new_confidence

        # 报告进度
        print(f"Step {plan.step}: {next_action.tool}")
        print(f"Confidence: {confidence:.2f}")

    return memory, plan, confidence
```

#### 3.2 工具执行器

根据计划调用具体工具：

```python
def execute_tool(action):
    if action.type == 'explore':
        return bash(f"runtime-explore.sh --focus={action.target}")

    elif action.type == 'read':
        return read_file(action.file_path)

    elif action.type == 'search':
        return grep(
            pattern=action.pattern,
            path=action.path,
            output_mode='content'
        )

    elif action.type == 'think':
        return internal_reasoning(action.question)

    elif action.type == 'remember':
        return commit_to_long_term_memory(action.fact)

    elif action.type == 'test':
        return bash(action.command)
```

#### 3.3 结果分析

关键步骤：从结果中提取洞见，更新置信度。

示例分析过程：

```python
# 读取连接池配置文件
result = read_file('config/database.js')

# 分析配置
analysis = """
发现连接池配置:
- maxConnections: 10 （偏低）
- timeout: 5000ms
- retry: 3次

观察：高峰期可能有50+并发请求，
但连接池只有10个连接，导致排队阻塞。

更新假设置信度:
- 原假设1（连接池耗尽）: 0.6 → 0.85 ✓
- 排除假设2（下游超时）: 0.5 → 0.3（需要验证日志）

下一步：验证假设1，检查高峰期请求数
"""

confidence = 0.85
```

#### 3.4 动态规划更新

基于新信息调整学习计划：

```python
# 发现新线索
if "旋转日志文件" in analysis:
    plan.add_action({
        'type': 'search',
        'target': '日志文件路径',
        'path': '/var/log/app',
        'pattern': '*.log'
    })

# 假设被排除
if hypothesis_confidence < 0.3:
    plan.remove_hypothesis(hypothesis_id)
    print(f"❌ 排除假设: {hypothesis}")

# 找到根因
if confidence > 0.9:
    plan.terminating_condition = True
    plan.root_cause_found = True
```

**学习深度自适应**：
- 简单问题：3-5步
- 复杂问题：5-10步
- 高度复杂：10步+，需要人工介入

---

### 阶段4：学习成果总结

完成学习循环后，总结所学：

```markdown
# 学习报告

## 问题陈述
"为什么这个微服务在高峰期会崩溃？"

## 学习路径
共执行8步，调用5种工具，读取12个文件，耗时7分钟。

### 步骤摘要
1. ✅ explore service/ - 理解架构
2. ✅ read config/database.js - 发现连接池配置
3. ✅ read services/api-handler.js - 发现请求激增逻辑
4. ✅ search logs/ - 验证超时错误
5. ✅ grep -A10 "ERROR" app.log - 找到崩溃堆栈
6. ✅ analyze heap dump - 确认无内存泄漏
7. ✅ think - 推理根因
8. ✅ remember - 固化知识

## 发现的关键事实
1. **数据库连接池太小** (max: 10)
   - 来源: config/database.js:23
   - 置信度: 0.95

2. **高峰期并发50+请求**
   - 来源: logs/app.log (12:34, 15:23, 18:45)
   - 置信度: 0.90

3. **请求无降级机制**
   - 来源: services/api-handler.js:45-67
   - 置信度: 0.85

4. **下游API超时阈值5秒**
   - 来源: config/downstream.js:12
   - 置信度: 0.80

## 根因分析
**根本原因**: 数据库连接池配置不足 + 缺乏降级机制

在高峰期（50+并发）连接池只有10个连接，导致：
1. 90%请求排队等待
2. 等待超过5秒触发下游超时
3. 超时累积导致进程崩溃

证据链:
- 连接池配置低 (事实1)
- 高峰期请求数高 (事实2)
- 无队列保护 (事实3)
- 超时阈值短 (事实4)

置信度: 0.92

## 解决方案
1. **短期**: 增加连接池到100
   ```javascript
   // config/database.js:23
   maxConnections: 100  // 从10增加
   ```

2. **中期**: 添加请求队列和降级
   - 使用Bull队列限制并发
   - 实现断路器模式

3. **长期**: 水平扩展 + 读写分离
   - 部署多个服务实例
   - 主库写，从库读

## 置信度评估
- 理解架构: 0.95
- 识别根因: 0.92
- 提出方案: 0.88
- **综合置信度: 0.91** ✅

## 不确定性残留
- [低] 数据库最大连接数限制（需要问DBA）
- [极低] 硬件资源是否足够（需要监控数据）

## 学习的模式
1. **模式**: "连接池不足导致高峰期崩溃"
   - 应用场景: 数据库密集型服务
   - 预防措施: 负载测试 + 监控排队时长

2. **模式**: "缺乏降级机制导致级联失败"
   - 应用场景: 依赖外部服务的模块
   - 预防措施: 断路器 + 超时配置

3. **经验**: "错误日志比代码更重要"
   - 未来类似问题优先查看日志时间模式
```

---

### 阶段5：记忆固化与迁移

#### 5.1 固化具体经验

```bash
/runtime.remember "连接池配置不足导致服务崩溃"
```

记忆内容：
```markdown
## 连接池不足问题
**学习时间**: 2025-11-14
**置信度**: 0.92
**来源**: runtime.learn (8步探索)

**问题**: 服务高峰期崩溃

**根因**: 数据库连接池maxConnections: 10，无法处理50+并发

**证据**:
- config/database.js:23
- logs/app.log (3次崩溃记录)
- 服务缺少降级机制

**解决方案**: 连接池增至100 + 添加请求队列

**长期预防**: 负载测试 + 监控排队时长 + 断路器

**已应用**: auth-service (2025-11-14)
```

#### 5.2 提取通用模式

```bash
/runtime.remember "模式: 连接池不足导致高峰期崩溃"
```

```markdown
## 模式: 连接池不足
**类型**: 性能反模式
**置信度**: 0.90

**识别特征**:
- 数据库密集型服务
- 高峰期响应变慢 → 超时 → 崩溃
- 日志显示排队等待

**诊断方式**:
1. 检查连接池配置 (config/database.*)
2. 检查高峰期并发量
3. 检查是否有排队/降级机制

**通用解决方案**:
1. 增加连接池 (通常是瓶颈的10倍)
2. 添加请求队列 (Bull/BullMQ)
3. 实现断路器 (opossum)
4. 负载测试 (Artillery/k6)

**预防措施**:
- 监控: 活跃连接数、排队时长
- 告警: 排队 > 5秒、连接使用率 > 80%
- 容量规划: 基于峰值并发 * 1.5

**应用案例**:
- auth-service (2025-11-14) - 成功解决

**相关知识**:
- 连接池设计原则 (来自记忆: design-patterns.md)
- 断路器模式 (来自记忆: design-patterns.md)
```

#### 5.3 构建关联网络

建立知识间的连接：

```bash
# memory/long-term/knowledge-graph.md

cat << EOF >> "$(cat索引: 模式: 连接池不足)"

## 知识关联

**相关模式**:
- 模式: 断路器模式 (强关联)
- 模式: 降级策略 (强关联)
- 反模式: 级联失败 (强关联)
- 监控: 指标驱动告警 (中等关联)

**技术栈**:
- tools: Bull/BullMQ (工作队列)
- libraries: opossum (断路器)
- monitoring: Prometheus + Grafana

**项目经验**:
- 案例: auth-service (强关联) → cognition/reports/auth-service-incident-2025-11-14.md

**学习资源**:
- 链接: https://github.com/OptimalBits/bull (Bull文档)
- 文章: "数据库连接池最佳实践" (待固化)
EOF
```

---

### 阶段6：反思与效能评估

```markdown
## 学习效果评估

### 探索效率
- 总步骤: 8步
- 有效步骤: 7步 (87.5%)
- 无效步骤: 1步（步骤4搜索日志方向错误）

### 工具使用效率
- 文件读取: 5次（4次有效，1次冗余）
- 搜索: 2次（high value）
- 思考: 1次（critical）

### 置信度变化轨迹
```
Step 1: 0.40 (初始)
Step 2: 0.55 (+发现配置)
Step 3: 0.70 (+验证假设)
Step 4: 0.65 (-搜索失败)
Step 5: 0.85 (+找到证据)
Step 6: 0.90 (+排除其他假设)
Step 7: 0.92 (整合推理)
```

### 学习深度匹配
- 问题复杂度: 中等
- 消耗步骤: 8步 (合适：5-10步范围)
- 达到置信度: 0.92 (>目标0.90)

**评估**: ✅ 学习效果优秀
```

#### 6.2 元认知反思

```markdown
## 元认知反思

### 做得好的地方
1. **假设驱动**: 从3个假设开始，逐步验证，避免乱猜
2. **证据链**: 每个结论都有代码或日志支撑
3. **工具选择**: 从探索(宏观)到验证(微观)再到总结，逻辑清晰
4. **深度自适应**: 8步达到0.92置信度，没有过度探索

### 需要改进的地方
1. **步骤4冗余**: 搜索日志时未指定时间范围，返工一次
   - 改进: 下次搜索时先检查日志轮转机制

2. **缺少访谈**: 没有与提交该代码的同事交流
   - 改进: 下次遇到复杂问题，先访谈原作者

3. **测试覆盖**: 只读了代码，没有运行性能测试验证
   - 改进: 下次应使用k6/Artillery做负载测试

### 发现的认知盲区
1. **盲区**: k8s资源限制的影响
   - 置信度: 0.3
   - 影响: 可能影响扩容方案
   - 行动计划: 询问运维团队获取k8s配置

### 更新学习策略
- **添加到策略库**: "性能问题 → 优先检查日志时间模式"
- **添加到记忆**: "日志搜索前 → 先确认日志轮转机制"
```

---

### 终止条件与防止无限循环

#### 正常终止
```python
def should_stop(plan, confidence):
    if confidence > 0.90:
        print("✅ 达到高置信度，停止探索")
        return True

    if plan.root_cause_found:
        print("✅ 找到根因，停止探索")
        return True

    if len(plan.executed_steps) >= plan.max_steps:
        print("⚠️  达到最大步数，停止探索")
        print("   建议：需要人工介入或进一步信息")
        return True

    if plan.time_elapsed > plan.max_time:
        print("⚠️  超时，停止探索")
        return True

    return False
```

#### 异常处理
```python
try:
    result = execute_tool(action)
except Exception as e:
    plan.add_note(f"工具执行失败: {e}")
    plan.error_count += 1

    if plan.error_count >= 3:
        print("❌ 连续失败，停止探索")
        # 请求人工帮助
        ask_user_for_help(action, e)
```

#### 无限循环检测
```python
# 检测重复步骤
if current_action similar to previous_actions[-3:]:
    print("⚠️  检测到重复行为，可能陷入循环")

    # 改变策略
    if strategy == "depth_first":
        strategy = "breadth_first"
        print("   切换到广度优先策略")

    # 或请求外部输入
    print("   请求用户提供新信息或方向")
    return ask_user_clarification()
```

---

### 报告生成

#### 完整学习报告模板

```markdown
# 学习报告 - [问题摘要]

**学习时间**: YYYY-MM-DD HH:MM:SS
**学习模式**: 自主探索（/runtime.learn）
**会话ID**: runtime.learn-[id]

## 问题陈述
[用户原始问题]

## 学习过程
- **总步数**: X步
- **消耗时间**: Y分钟
- **工具调用**: N种工具，M次调用
- **读取文件**: N个文件
- **置信度变化**: 0.40 → 0.92

## 发现的事实
[bullet list，每个事实有来源和置信度]

## 根因分析
[结构化分析，证据链]

## 解决方案
[可执行的方案]

## 学习成果
### 具体经验
- [记忆1]
- [记忆2]

### 通用模式
- [模式1]
- [模式2]

## 元认知反思
[优缺点、改进方向]

## 附件
- 详细日志: cognition/logs/learn-[id].json
- 思维导图: cognition/graphs/learn-[id].png
```

---

### 使用示例

#### 示例1：探索未知功能

```bash
/runtime.learn "理解并实现OAuth2.0的Authorization Code流程"
```

AI执行：
```
Step 1: runtime.explore --find="OAuth"
  → 未找到现有实现

Step 2: internal.think "OAuth2.0的组成部分"
  → 识别：Authorization Server, Resource Server, Client

Step 3: search web "OAuth2.0 Authorization Code Flow RFC"
  → 读取RFC 6749相关章节

Step 4: read docs/oauth2.md
  → 理解自定义方案

Step 5: think "与现有JWT认证的关系"
  → 识别：可以并存，JWT用于内部API

Step 6: plan "实现步骤"
  → 生成任务列表

Step 7: remember "OAuth2.0与JWT的区别和适用场景"
  → 固化到long-term memory

⚠️ 置信度: 0.85 (< 0.90)
建议: 参考其他项目的实现或咨询专家
```

#### 示例2：分析生产环境问题

```bash
/runtime.learn "为什么生产环境的数据导入任务偶尔会失败？"
```

AI执行：
```
Step 1: read config/prod-import.js
  → 发现超时配置: 30秒

Step 2: search logs/prod/ "import.*fail|error|timeout"
  → 找到3次失败记录

Step 3: grep logs/prod/app.log -B10 -A10 "IMPORT_FAILED"
  → 发现错误: "Connection timeout to S3"

Step 4: read services/import.js:45-78
  → 发现：单次导入下载10个文件，串行执行

Step 5: think "分析超时原因"
  → 推理：网络波动 + 串行超时累积

Step 6: browse web "S3 connection timeout best practices"
  → 学习：建议使用批量下载 + 重试机制

Step 7: think "设计解决方案"
  → 方案：并行下载 + 指数退避重试 + 每文件超时15秒

Step 8: remember "批量文件导入优化模式"
  → 固化通用模式

✅ 根因找到: S3连接超时 + 串行下载累积
✅ 置信度: 0.93
✅ 解决方案: 并行下载 + 智能重试
```

#### 示例3：从错误中学习

```bash
/runtime.learn "我分析为什么刚才的代码修改引入了这个bug"
```

AI执行：
```
Step 1: git diff → 查看修改内容
Step 2: read test → 理解测试用例
Step 3: think → 分析逻辑错误
Step 4: reflect → 识别认知偏差（过早下结论）
Step 5: remember → 固化防御机制

成果：更新心智模型，避免重复相同错误
```

---

### 命令定义

**语法**:
```bash
/runtime.learn "[问题或学习目标]"

可选参数:
--max-steps=10      # 最大探索步数
--min-confidence=0.9 # 目标置信度
--focus=[module]    # 聚焦特定模块
--strategy=[depth|breadth] # 探索策略
```

**完整定义**: `.ai-runtime/commands/runtime.learn.md` (843行详细文档)

---

## 与 /runtime.explore 的区别

| 维度 | `/runtime.explore` | `/runtime.learn` | 区别 |
|------|-------------------|-----------------|------|
| **输入** | 无（扫描整个代码库） | 具体问题/知识领域 | learn有明确目标 |
| **范围** | 宏观（系统级） | 微观到宏观（问题导向） | learn聚焦 |
| **深度** | 浅到中等（建立地图） | 深到很深（理解根因） | learn深入 |
| **输出** | 知识图谱 + 探索报告 | 学习报告 + 新知识 | 成果不同 |
| **后续** | 通常接 /runtime.learn | 通常接 /runtime.plan | 工作流 |

**典型流程**:
```
新代码库:
→ /runtime.explore  (建立整体认知)
→ /runtime.learn    (深入理解特定模块)
→ /runtime.plan     (规划新功能)
```

---

## 与 /runtime.plan 的区别

| 维度 | `/runtime.learn` | `/runtime.plan` | 为什么分开？ |
|------|----------------|----------------|------------|
| **目标** | 理解问题 | 规划解决方案 | 认知阶段不同 |
| **输入** | 问题 | 需求 | 前提条件不同 |
| **核心** | 知识缺口识别 | 功能拆解与依赖分析 | 方法论不同 |
| **输出** | 学习报告 + 新知识 | 任务树 + 执行计划 | 产物不同 |
| **工作流** | learn → plan | plan → iterate | 分工明确 |

---

## 工具与脚本

### 辅助脚本

**定义文件**: `.ai-runtime/commands/runtime.learn.md`
**学习日志**: `cognition/logs/learn-*.json`
**知识索引**: `memory/long-term/knowledge-graph.md`

---

## 宪法遵循

**遵循原则**:
- ✓ 1.1 认知主体性: 我们是具有学习能力的智能体
- ✓ 1.2 类脑思维: 模式识别 + 联想 + 预测性处理
- ✓ 1.3 谦逊与不确定: 明确标注置信度，持续提问
- ✓ 1.4 记忆层次: 学习成果固化到长期记忆
- ✓ 2.1 代码即知识: 将代码结构转化为心智模型
- ✓ 4.1 从经验学习: 每个学习循环都更新模型
- ✓ 4.2 认知更新: 动态规划适应新知识
- ✓ 4.3 自我反思: 元认知评估学习效果

**宪法位置**: `.ai-runtime/constitution.md`

---

**命令路径**: `.ai-runtime/commands/runtime.learn.md`
**最后更新**: 2025-11-14 11:30:00
**版本**: 1.0.0 (纯自主学习模式)
