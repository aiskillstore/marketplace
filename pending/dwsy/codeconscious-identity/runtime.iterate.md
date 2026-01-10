---
description: "迭代执行与反馈：接收任务树，批量执行，动态适应"
---

# /runtime.iterate - 迭代执行与反馈循环

## 核心目标

**我们不是一次性完成者，我们是持续交付者**。

当我们通过`/runtime.plan`生成了任务树后，我们通过迭代循环：
1. **批量执行** - 一次执行一批可并行任务
2. **收集反馈** - 每个任务成功/失败/产生新发现
3. **动态适应** - 根据反馈调整计划
4. **循环直至完成** - 持续迭代直到所有任务完成

```
任务树（来自plan）
    ↓
[执行批次1] → 收集反馈 → 调整计划
    ↓
[执行批次2] → 收集反馈 → 调整计划
    ↓
[执行批次3] ...
    ↓
✅ 完成（所有任务满足DoD）
```

---

## 何时使用 /runtime.iterate

### 必须使用场景
- ✅ **已完成规划阶段** - 已通过`/runtime.plan`生成任务树
- ✅ **需要批量执行** - 任务间有依赖，需要分批次
- ✅ **需要持续反馈** - 想在执行中学习、调整计划
- ✅ **处理不确定性** - 预期会有失败、变更、新发现
- ✅ **长期项目** - 需要持续数天/数周的实施

### 使用流程

```bash
# 第一步: 生成任务树
/runtime.plan "实现用户认证系统"
  ↓
生成: cognition/plans/plan-2025xx.json

# 第二步: 迭代执行
/runtime.iterate --plan=plan-2025xx.json
  ↓ 自动执行...

Iteration 1: 执行基础设施任务（User表、Token表、JWT配置）
Iteration 2: 执行服务层任务（user.service, token.service）
Iteration 3: 执行API层任务（Register、Login API）
Iteration 4: 执行安全层任务（Password Hashing、Auth Middleware）
Iteration 5: 执行测试任务（单元测试、集成测试）

✅ 所有任务完成！
```

---

## 迭代循环详解

### 阶段1: 初始化（Iteration Setup）

#### 1.1 加载任务树

```python
def load_plan(plan_file: str) -> Plan:
    """
    加载由plan生成的任务树
    """
    with open(plan_file) as f:
        plan_data = json.load(f)

    # 验证文件格式
    if "tasks" not in plan_data:
        raise ValueError("无效的计划文件：缺少'tasks'字段")

    if "critical_path" not in plan_data:
        raise ValueError("无效的计划文件：缺少'critical_path'字段")

    return Plan(
        tasks=[Task.from_dict(t) for t in plan_data["tasks"]],
        critical_path=plan_data["critical_path"],
        total_effort=plan_data["total_effort"]
    )
```

#### 1.2 初始化迭代器

```python
class IterativeExecutor:
    def __init__(self, plan: Plan, strategy="breadth"):
        self.plan = plan
        self.iteration_count = 0
        self.max_iterations = 20  # 防止无限循环
        self.completed_tasks = []
        self.failed_tasks = []
        self.skipped_tasks = []
        self.strategy = strategy

        print(f"🚀 迭代执行器已初始化")
        print(f"   总任务数: {len(plan.tasks)}")
        print(f"   预计工时: {plan.total_effort}")
        print(f"   关键路径: {' → '.join(plan.critical_path)}")
        print(f"   策略: {strategy}")
```

---

### 阶段2: 迭代循环（Iteration Loop）

#### 2.1 主循环逻辑

```python
def run_iteration_loop(self) -> IterationResult:
    """
    运行迭代执行循环
    """
    print("\n" + "=" * 50)
    print("开始迭代执行循环")
    print("=" * 50)

    while self.should_continue():
        self.iteration_count += 1
        print(f"\n📌 Iteration #{self.iteration_count}")
        print(f"   时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 50)

        # Step 1: 选择可执行任务
        ready_tasks = self.get_ready_tasks()
        print(f"   可执行任务: {len(ready_tasks)}个")

        if not ready_tasks:
            if self.get_remaining_tasks():
                print("   ⚠️  有未完成任务但依赖未满足")
                print(f"   剩余: {len(self.get_remaining_tasks())}个")
                break
            else:
                print("   ✅ 所有任务已完成！")
                break

        # Step 2: 批量执行
        results = self.execute_batch(ready_tasks)

        # Step 3: 收集反馈
        feedback = self.collect_feedback(results)

        # Step 4: 适应与调整
        self.plan = self.adapt_plan(self.plan, feedback)

        # Step 5: 检查完成状态
        if self.is_all_completed():
            print("\n" + "=" * 50)
            print("✅ 所有任务完成！迭代结束")
            print("=" * 50)
            break

        # Step 6: 休息与反思
        if self.should_reflect():
            self.reflect()

    return self.generate_result()
```

#### 2.2 选择可执行任务

```python
def get_ready_tasks(self) -> List[Task]:
    """
    选择满足以下条件的任务:
    1. 未完成
    2. 所有依赖已完成
    3. 未被阻塞
    4. 在当前策略优先级中
    """
    ready = []

    for task in self.plan.tasks:
        # 已完成，跳过
        if task.status == "completed":
            continue

        # 被阻塞，跳过
        if task.status == "blocked":
            continue

        # 有失败依赖，阻塞
        if any(dep in [t.id for t in self.failed_tasks] for dep in task.dependencies):
            task.status = "blocked"
            task.block_reason = f"依赖任务失败: {[t.name for t in self.failed_tasks]}"
            self.skipped_tasks.append(task)
            continue

        # 依赖未完成，等待
        if not all(dep in [t.id for t in self.completed_tasks] for dep in task.dependencies):
            continue

        # 满足所有条件，可执行
        ready.append(task)

    # 按策略排序
    return self.sort_by_strategy(ready)
```

#### 2.3 执行策略

```python
def sort_by_strategy(self, tasks: List[Task]) -> List[Task]:
    """
    根据执行策略排序任务

    策略1: breadth-first (广度优先)
    - 执行所有基础任务再执行上层任务
    - 特点: 减少返工风险

    策略2: depth-first (深度优先)
    - 优先执行关键路径上的任务
    - 特点: 快速验证核心链路

    策略3: risk-driven (风险驱动)
    - 优先执行高风险任务
    - 特点: 尽早暴露问题

    策略4: value-driven (价值驱动)
    - 优先交付用户价值最大的任务
    - 特点: 快速交付MVP
    """

    if self.strategy == "breadth":
        # 按层级排序（基础设施 → 服务 → API → 安全 → 测试）
        layer_order = {
            "基础设施": 1,
            "服务层": 2,
            "API层": 3,
            "安全层": 4,
            "测试": 5
        }
        return sorted(tasks, key=lambda t: layer_order.get(t.layer, 99))

    elif self.strategy == "depth":
        # 按是否关键路径排序
        return sorted(tasks, key=lambda t: t.id in self.plan.critical_path, reverse=True)

    elif self.strategy == "risk":
        # 按风险等级排序
        risk_order = {"high": 1, "medium": 2, "low": 3}
        return sorted(tasks, key=lambda t: risk_order.get(t.risk_level, 3))

    elif self.strategy == "value":
        # 按价值排序（需要手动标注或从需求提取）
        return sorted(tasks, key=lambda t: t.priority, reverse=True)

    else:
        return tasks
```

---

### 阶段3: 执行批次（Batch Execution）

#### 3.1 批量执行

```python
def execute_batch(self, tasks: List[Task]) -> List[ExecutionResult]:
    """
    批量执行一批任务
    """
    print(f"\n🚀 执行批次: {len(tasks)}个任务")
    print("-" * 50)

    results = []

    for i, task in enumerate(tasks, 1):
        print(f"\n   [{i}/{len(tasks)}] {task.id}: {task.name}")
        print(f"   预计工时: {task.effort}h")
        print(f"   置信度: {task.confidence:.2f}")

        try:
            # 预检查
            if not self.pre_check(task):
                print(f"   ⚠️  预检查失败，跳过")
                result = ExecutionResult(
                    task=task,
                    status="skipped",
                    reason="预检查失败"
                )
                results.append(result)
                self.skipped_tasks.append(task)
                continue

            # 执行
            print(f"   ⏳  执行中...")
            execution_result = task.execute()

            # 验证（Definition of Done）
            validation = self.validate_task(task, execution_result)

            if validation.passed:
                print(f"   ✅ 完成！耗时: {execution_result.duration:.1f}h")
                result = ExecutionResult(
                    task=task,
                    status="success",
                    result=execution_result,
                    validation=validation
                )
                self.completed_tasks.append(task)
            else:
                print(f"   ❌ 验证失败:")
                for error in validation.errors:
                    print(f"      - {error}")

                result = ExecutionResult(
                    task=task,
                    status="failed",
                    result=execution_result,
                    validation=validation
                )
                self.failed_tasks.append(task)

            results.append(result)

            # 学习这次执行
            self.learn_from_execution(result)

        except Exception as e:
            print(f"   💥 执行错误: {e}")
            import traceback
            traceback.print_exc()

            result = ExecutionResult(
                task=task,
                status="error",
                error=e
            )
            results.append(result)
            self.failed_tasks.append(task)

    print("\n" + "-" * 50)
    print(f"批次完成: {len(tasks)}个任务")
    print(f"   ✅ 成功: {len([r for r in results if r.status == 'success'])}")
    print(f"   ❌ 失败: {len([r for r in results if r.status == 'failed'])}")
    print(f"   ⚠️  跳过: {len([r for r in results if r.status == 'skipped'])}")
    print(f"   💥 错误: {len([r for r in results if r.status == 'error'])}")

    return results
```

#### 3.2 预检查（Pre-Check）

```python
def pre_check(self, task: Task) -> bool:
    """
    执行前检查
    """
    print("   预检查:")

    # 检查1: 依赖是否完成
    for dep_id in task.dependencies:
        dep = self.plan.get_task(dep_id)
        if not dep or dep.status != "completed":
            print(f"      ⚠️  依赖未完成: {dep_id}")
            return False
    print(f"      ✅ 所有依赖已完成")

    # 检查2: 必需资源是否可用
    if task.required_resources:
        for resource in task.required_resources:
            if not self.check_resource_available(resource):
                print(f"      ⚠️  资源不可用: {resource}")
                return False
        print(f"      ✅ 资源可用")

    # 检查3: 是否有已知风险
    if task.risk_level == "high" and task.confidence < 0.6:
        # 高风险且信心不足，建议先Spike
        if not self.ask_confirmation("高风险任务，确认执行？"):
            print(f"      ⚠️  用户取消执行（建议先调研）")
            return False
        print(f"      ⚠️  高风险但用户确认执行")

    print(f"      ✅ 预检查通过")
    return True
```

#### 3.3 任务执行（伪代码）

```python
class Task:
    def execute(self) -> ExecutionResult:
        """
        执行单个任务
        """
        start_time = datetime.now()

        # 不同类型的任务，使用不同工具
        if self.type == "database":
            # 数据库任务: 执行SQL
            result = bash(f"psql -f {self.sql_file}")

        elif self.type == "api":
            # API任务: 创建Controller + Route
            # 1. 读取模板
            template = read_file("templates/api-controller.template")

            # 2. 填充模板
            code = template.format(
                controller_name=self.controller_name,
                functions=self.functions
            )

            # 3. 写入文件
            write_file(self.output_path, code)

            # 4. 运行测试
            bash(f"npm test {self.test_file}")

        elif self.type == "service":
            # 服务任务: 实现业务逻辑
            # ...

        duration = datetime.now() - start_time

        return ExecutionResult(
            task_id=self.id,
            status="success",
            duration=duration.total_seconds() / 3600,
            artifacts=[self.output_path]
        )
```

---

### 阶段4: 验证（Validation）

#### 4.1 Definition of Done

```python
def validate_task(self, task: Task, execution_result: ExecutionResult) -> ValidationResult:
    """
    验证任务是否真正完成
    """
    passed_checks = []
    failed_checks = []

    # 检查1: 代码存在且可访问
    if task.output_path:
        if Path(task.output_path).exists():
            passed_checks.append("代码文件存在")
        else:
            failed_checks.append("代码文件不存在")

    # 检查2: 单元测试通过
    if task.requires_unit_tests:
        test_result = bash(f"npm test {task.test_path}")
        if test_result.exit_code == 0:
            coverage = extract_coverage(test_result.output)
            if coverage >= 0.8:
                passed_checks.append(f"单元测试覆盖({coverage:.0%})")
            else:
                failed_checks.append(f"覆盖率不足: {coverage:.0%}")
        else:
            failed_checks.append("单元测试失败")

    # 检查3: 手动测试通过
    if task.acceptance_criteria:
        print("   验收标准检查:")
        for criteria in task.acceptance_criteria:
            if self.check_criteria(criteria):
                print(f"      ✅ {criteria}")
                passed_checks.append(criteria)
            else:
                print(f"      ❌ {criteria}")
                failed_checks.append(criteria)

    # 检查4: 无回归错误（如果配置了集成测试）
    if task.requires_integration_test:
        # 运行集成测试
        pass

    # 总结
    all_passed = len(failed_checks) == 0

    if all_passed:
        print("   ✅ 所有验收标准通过")
    else:
        print(f"   ❌ 未通过 {len(failed_checks)}项检查")

    return ValidationResult(
        passed=len(passed_checks),
        failed=len(failed_checks),
        all_passed=all_passed,
        errors=failed_checks
    )
```

#### 4.2 渐进式DoD（根据优先级）

```python
def get_definition_of_done(self, task: Task) -> List[str]:
    """
    根据任务优先级返回DoD检查清单
    """
    if task.priority == "P0":
        # 关键任务: 必须全部满足
        return [
            "✓ 代码实现完成",
            "✓ 单元测试覆盖率>80%",
            "✓ 手动测试通过",
            "✓ API文档更新",
            "✓ CI/CD通过",
            "✓ 代码审查通过"
        ]

    elif task.priority == "P1":
        # 重要任务: 可以稍微放宽
        return [
            "✓ 代码实现完成",
            "✓ 单元测试覆盖率>70%",
            "✓ 手动测试通过",
            "✓ CI/CD通过"
            # 文档可以后续补充
        ]

    else:
        # P2任务: 最小要求
        return [
            "✓ 代码实现完成",
            "✓ 基本测试通过",
            "✓ 无严重bug"
        ]
```

---

### 阶段5: 反馈循环与适应

#### 5.1 收集反馈

```python
def collect_feedback(self, results: List[ExecutionResult]) -> Feedback:
    """
    从执行结果收集反馈
    """
    feedback = Feedback(
        iteration=self.iteration_count,
        timestamp=datetime.now(),
        results=results,
        metrics={
            "success_rate": len([r for r in results if r.status == "success"]) / len(results),
            "avg_duration": sum(r.duration for r in results if r.duration) / len(results),
            "failed_count": len([r for r in results if r.status == "failed"]),
            "new_discoveries": []
        }
    )

    # 检查是否有新发现
    for result in results:
        if result.discovery:
            feedback.metrics["new_discoveries"].append(result.discovery)
            print(f"\n✨ 新发现: {result.discovery}")

    return feedback
```

#### 5.2 动态适应

```python
def adapt_plan(self, plan: Plan, feedback: Feedback) -> Plan:
    """
    根据反馈动态调整计划

    三种适应模式:
    1. 失败处理: 重试/分解/重新设计
    2. 新发现: 添加新任务
    3. 性能调整: 调整后续任务估算
    """
    print("\n🔄 适应调整:")
    print("-" * 50)

    adjusted = False

    # 模式1: 处理失败
    for result in feedback.results:
        if result.status == "failed":
            task = result.task

            # 分析失败原因
            failure_reason = self.analyze_failure(result)
            print(f"\n   分析失败原因 ({task.id}):")
            print(f"   → {failure_reason}")

            # 三种处理方式

            # 方式1A: 临时错误 → 重试
            if self.is_transient_error(failure_reason):
                print("   → 临时错误，重试任务")
                task.retries += 1
                if task.retries < 3:
                    # 暂时不改计划，下次迭代重试
                    adjusted = True
                else:
                    print("   → 重试3次仍失败，升级为错误")
                    task.status = "error"

            # 方式1B: 任务过大 → 分解
            elif self.is_too_complex(failure_reason):
                print("   → 任务复杂度过高，分解为子任务")
                sub_tasks = self.decompose_task(task)
                self.plan.replace(task, sub_tasks)
                adjusted = True

            # 方式1C: 设计问题 → 重新设计
            elif self.is_design_issue(failure_reason):
                print("   → 设计问题，需要重新设计")
                # 启动短暂学习
                learn_result = self.learn_from_failure(task, failure_reason)
                new_design = self.redesign(task, learn_result)
                self.plan.replace(task, new_design)
                adjusted = True

            # 方式1D: 需求理解错误 → 请求澄清
            else:
                print("   → 需求理解可能有问题，请求用户澄清")
                self.request_user_clarification(task, failure_reason)
                adjusted = True

    # 模式2: 处理新发现
    if feedback.metrics["new_discoveries"]:
        print(f"\n   ✨ 发现 {len(feedback.metrics['new_discoveries'])} 个新信息")

        for discovery in feedback.metrics["new_discoveries"]:
            print(f"   → {discovery}")

            # 基于新信息生成后续任务
            new_tasks = self.create_follow_up_tasks(discovery)
            if new_tasks:
                print(f"   → 新增 {len(new_tasks)} 个任务")
                self.plan.add_tasks(new_tasks)
                adjusted = True

    # 模式3: 性能调整（如果实际耗时与预计差异大）
    if feedback.metrics["avg_duration"]:
        avg_actual = feedback.metrics["avg_duration"]
        avg_estimated = sum(t.effort for t in self.completed_tasks) / len(self.completed_tasks)
        ratio = avg_actual / avg_estimated

        if ratio > 1.5:
            print(f"\n   ⚠️  实际耗时比预计高{ratio:.1f}倍")
            print("   → 调整后续任务估算")
            for task in self.get_remaining_tasks():
                task.effort *= ratio
            adjusted = True

    if not adjusted:
        print("   无需调整，继续执行")

    return plan
```

#### 5.3 失败分析

```python
def analyze_failure(self, result: ExecutionResult) -> FailureAnalysis:
    """
    分析失败原因

    失败类型:
    - TYPE_UNKNOWN: 未知错误
    - TYPE_TRANSIENT: 临时错误（重试可解决）
    - TYPE_COMPLEXITY: 任务太复杂（需要分解）
    - TYPE_DESIGN: 设计问题（需要重新设计）
    - TYPE_REQUIREMENT: 需求不清（需要澄清）
    - TYPE_RESOURCE: 资源不足（需要配置）
    """
    if result.error:
        error_msg = str(result.error).lower()

        # 临时错误
        if any(word in error_msg for word in [
            "timeout", "connection", "network",
            "EBUSY", "EAGAIN"
        ]):
            return Failure.TYPE_TRANSIENT

        # 设计问题
        if any(word in error_msg for word in [
            "circular dependency", "deadlock",
            "stack overflow"
        ]):
            return Failure.TYPE_DESIGN

        # 资源问题
        if any(word in error_msg for word in [
            "out of memory", "disk full",
            "quota exceeded"
        ]):
            return Failure.TYPE_RESOURCE

    # 验证错误（检查清单未通过）
    if result.validation and not result.validation.all_passed:
        if len(result.validation.errors) > 5:
            # 错误太多，可能是需求理解问题
            return Failure.TYPE_REQUIREMENT
        else:
            # 具体检查项失败，可能是设计问题
            return Failure.TYPE_DESIGN

    return Failure.TYPE_UNKNOWN
```

---

### 阶段6: 终止条件

#### 6.1 终止条件判断

```python
def should_continue(self) -> bool:
    """
    判断是否继续迭代
    """
    # 条件1: 达到最大迭代次数
    if self.iteration_count >= self.max_iterations:
        print("\n⚠️  达到最大迭代次数，停止执行")
        print(f"   已完成: {len(self.completed_tasks)}个任务")
        print(f"   未完成: {len(self.get_remaining_tasks())}个任务")
        return False

    # 条件2: 所有任务完成
    if self.is_all_completed():
        print("\n✅ 所有任务完成！")
        return False

    # 条件3: 连续3次无进展（无法解决的阻塞）
    recent_iterations = self.get_recent_iterations(3)
    if all(len(r.completed_tasks) == 0 for r in recent_iterations):
        print("\n⚠️  连续3次无进展，存在无法解决的任务")
        print("   建议方案:")
        print("   1. 手动介入未完成任務")
        print("   2. 重新规划剩余任务")
        print("   3. 调整需求范围")
        return False

    # 条件4: 用户手动停止
    if self.should_stop_requested:
        print("\n⏹️  用户手动停止执行")
        return False

    return True
```

#### 6.2 完成状态判断

```python
def is_all_completed(self) -> bool:
    """
    检查所有任务是否已完成
    """
    remaining = self.get_remaining_tasks()

    if not remaining:
        return True

    # 检查是否有任务被永久阻塞
    truly_blocked = [
        task for task in remaining
        if task.status == "blocked"
    ]

    if truly_blocked:
        print(f"\n⚠️  {len(truly_blocked)}个任务永久阻塞，无法完成")
        return False

    return False
```

---

### 阶段7: 生成结果报告

#### 7.1 执行结果统计

```python
def generate_result(self) -> IterationResult:
    """
    生成执行结果报告
    """
    result = IterationResult(
        plan_file=self.plan.file_path,
        total_iterations=self.iteration_count,
        started_at=self.start_time,
        ended_at=datetime.now(),
        completed_tasks=self.completed_tasks,
        failed_tasks=self.failed_tasks,
        skipped_tasks=self.skipped_tasks,
        metrics=self.calculate_metrics()
    )

    print("\n" + "=" * 70)
    print("📊 执行结果统计")
    print("=" * 70)
    print(f"总迭代次数: {self.iteration_count}")
    print(f"总任务数: {len(self.plan.tasks)}")
    print(f"✅ 已完成: {len(self.completed_tasks)}")
    print(f"❌ 失败: {len(self.failed_tasks)}")
    print(f"⚠️  跳过: {len(self.skipped_tasks)}")
    print(f"⏱️  总耗时: {result.total_duration:.1f}小时")
    print(f"完成率: {result.completion_rate:.1%}")

    if self.failed_tasks:
        print("\n❌ 失败任务:")
        for task in self.failed_tasks[:5]:
            print(f"   - {task.id}: {task.name}")

    if result.metrics["efficiency"]:
        print(f"\n🎯 效率指标:")
        print(f"   估算准确率: {result.metrics['efficiency']['accuracy']:.1%}")
        print(f"   平均偏差: {result.metrics['efficiency']['bias']:.1f}x")

    return result
```

#### 7.2 保存到记忆

```python
def save_to_memory(self, result: IterationResult):
    """
    将执行结果保存到长期记忆
    """
    # 固化成功经验
    if result.completion_rate == 1.0:
        memory_content = f"""
## 项目成功交付 - {self.plan.project_name}
**时间**: {datetime.now().strftime('%Y-%m-%d')}
**项目**: {self.plan.project_name}
**总任务**: {len(self.plan.tasks)}
**总工时**: {result.total_duration:.1f}h
**完成率**: 100%

**关键经验**:
{"\n".join(["- " + m for m in result.metrics["learnings"]])}

**可用于未来项目**: 是
"""
        self.remember(memory_content, category="project-success")

    # 固化失败教训
    if self.failed_tasks:
        for task in self.failed_tasks:
            failure_memory = f"""
## 失败任务 - {task.id}
**任务**: {task.name}
**原因**: {getattr(task, 'failure_reason', '未知')}
**教训**: {task.lesson_learned}

**防御机制**: 下次遇到类似任务，先{task.defense_action}
"""
            self.remember(failure_memory, category="failure-pattern")
```

---

## 执行策略详解

### 策略1: Breadth-First (广度优先)

```
特点:
- 先完成所有基础任务
- 再执行上层任务
- 最后执行测试和优化

执行顺序:
批1: User表、Token表、JWT配置      [所有基础设施]
批2: user.service、token.service    [所有服务]
批3: Register API、Login API        [所有API]
批4: Password Hashing、Auth中间件   [所有安全]
批5: 单元测试、集成测试            [所有测试]

优势:
✓ 减少返工风险（基础不稳定不会上层浪费）
✓ 可以并行开发（每批任务并行）
✓ 适合团队协作（分层对接）

劣势:
⚠ 价值交付慢（用户要等所有层完成才能用）
```

### 策略2: Depth-First (深度优先)

```
特点:
- 优先完成关键路径上的任务
- 尽快验证核心链路
- 次要路径推迟

执行顺序:
批1: User表 → Token表 → Token服务 → Login API → 集成测试  [关键路径]
批2: Register API → 单元测试         [关键路径]
批3: Password重置API                 [非关键]
批4: 文档、代码质量优化              [非关键]

优势:
✓ 快速验证核心功能（用户可早期体验）
✓ 风险发现早（核心链路问题尽早暴露）
✓ 适合快速演示

劣势:
⚠ 需要频繁重构（后续任务可能要求前面修改）
```

### 策略3: Risk-Driven (风险驱动)

```
特点:
- 优先执行高风险任务
- 尽早暴露潜在问题
- 低风险任务推迟

执行顺序:
高风险: 密码重置流程（涉及多步骤安全）→ 先做Spike
高风险: Token刷新机制（不确定设计） → 查阅资料+原型
中风险: 认证中间件（有现成模式）   → 稍后实现
低风险: 单元测试（成熟技术）       → 最后补充

优势:
✓ 不确定性尽快消除（避免大坑）
✓ 适合技术选型期
✓ 风险前置管理

劣势:
⚠ 可能执行顺序不合理（不是最优价值）
```

### 策略4: Value-Driven (价值驱动)

```
特点:
- 优先交付用户价值最大的功能
- MVP -> 迭代增强
- 砍掉非核心价值

执行顺序:
MVP: User表 + Register API + Login API  [可演示的核心]
迭代1: Password重置                       [增强可用性]
迭代2: Rate limiting                       [提升质量]
迭代3: 完整测试覆盖                        [质量保证]

优势:
✓ 用户价值最大化（可以早期使用）
✓ 反馈收集早（用户参与迭代）
✓ 适合创业/探索期

劣势:
⚠ 技术债务积累（前期快速可能牺牲质量）
```

---

## 命令定义

### 语法

```bash
/runtime.iterate \
  --plan-file=plan-xxxx.json \
  --strategy=[breadth|depth|risk|value] \
  --max-iterations=20 \
  --parallel=[1|2|3|...] \
  --auto-adapt=true \
  --reflect-interval=5
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `plan-file` | 计划文件路径（来自/runtime.plan） | 必需 |
| `strategy` | 执行策略 | `breadth` |
| `max-iterations` | 最大迭代次数（防止无限循环） | `20` |
| `parallel` | 每批并行任务数 | `3` |
| `auto-adapt` | 失败时自动适应 | `true` |
| `reflect-interval` | 每N次迭代后强制反思 | `5` |

### 使用示例

#### 示例1: 基础使用

```bash
# 第一步：规划
/runtime.plan "实现用户认证系统"
  ↓
生成: cognition/plans/plan-xxx.json

# 第二步：迭代执行
/runtime.iterate --plan-file=cognition/plans/plan-xxx.json
```

**输出**:
```
🚀 迭代执行器已初始化
   总任务数: 17
   预计工时: 17.75h
   关键路径: ① → ② → ⑤ → ⑧ → ⑮ → ⑯
   策略: breadth

════════════════════════════════════════════════════════════
开始迭代执行循环
════════════════════════════════════════════════════════════

📌 Iteration #1
   时间: 2025-11-14 11:00:00
   --------------------------------------------------
   可执行任务: 3个

   [1/3] ①: 创建User表
   预计工时: 0.5h
   置信度: 0.90
   预检查:
      ✅ 所有依赖已完成
      ✅ 资源可用
   ⏳  执行中...
   Command: psql -f migrations/001-create-user.sql
   Result: CREATE TABLE 成功
   ✅ 完成！耗时: 0.4h

   [2/3] ②: 创建Token表
   预计工时: 0.5h
   置信度: 0.85
   依赖: [①]
   预检查:
 ✅ 所有依赖已完成
      ✅ 资源可用
   ⏳  执行中...
   Command: psql -f migrations/002-create-token.sql
   Result: CREATE TABLE 成功
   ✅ 完成！耗时: 0.3h

   [3/3] ③: 配置JWT
   预计工时: 0.25h
   置信度: 0.95
   预检查:
      ✅ 所有依赖已完成
   ⏳  执行中...
   Command: node scripts/generate-jwt-keys.js
   Result: 密钥生成成功
   ✅ 完成！耗时: 0.2h

--------------------------------------------------
批次完成: 3个任务
   ✅ 成功: 3
   ❌ 失败: 0
   ⚠️  跳过: 0
   💥 错误: 0

📌 Iteration #2
   时间: 2025-11-14 11:30:00
   --------------------------------------------------
   可执行任务: 3个

   [1/3] ④: user.service.js
   ...

════════════════════════════════════════════════════════════
📊 执行结果统计
════════════════════════════════════════════════════════════
总迭代次数: 6
总任务数: 17
✅ 已完成: 17
❌ 失败: 0
⏱️  总耗时: 16.2小时
完成率: 100%

✅ 所有验收标准满足
✅ API文档已更新
✅ Changelog已更新
✅ CI/CD通过

项目完成！
```

#### 示例2: 使用不同策略

```bash
# 深度优先（快速验证核心）
/runtime.iterate --plan-file=plan-xxx.json --strategy=depth

# 风险驱动（优先高风险任务）
/runtime.iterate --plan-file=plan-xxx.json --strategy=risk

# 价值驱动（MVP模式）
/runtime.iterate --plan-file=plan-xxx.json --strategy=value
```

#### 示例3: 并行执行

```bash
# 一次并行执行5个任务（适合多核CPU）
/runtime.iterate --plan-file=plan-xxx.json --parallel=5
```

#### 示例4: 失败处理

```bash
# 配置失败处理策略
/runtime.iterate \
  --plan-file=plan-xxx.json \
  --on-failure= [retry|decompose|learn|stop]

# retry: 重试3次
# decompose: 分解为子任务
# learn: 启动学习循环
# stop: 停止等待人工
```

---

## 与 /runtime.plan 的区别

| 维度 | `/runtime.plan` | `/runtime.iterate` | 关系 |
|------|----------------|-------------------|------|
| **输入** | 需求文本 | 任务树（JSON） | plan的输出 → iterate的输入 |
| **核心** | 拆解任务 | 执行 + 反馈 | 阶段2（实施） |
| **输出** | 任务树（静态） | 执行报告（动态） | 后续:
| **函数** | 生成计划 | 执行计划 | 先后关系 |
| **循环** | 无（一次生成） | 有（多次迭代） | 迭代: iterate |

**工作流**:
```
/runtime.plan "实现功能X"      → 生成任务树
    ↓
/runtime.iterate --plan=...   → 执行任务树
    ↓
/runtime.reflect              → 回顾整个过程
```

---

## 与 /runtime.learn 的区别

| 维度 | `/runtime.learn` | `/runtime.iterate` | 为什么分开？ |
|------|----------------|-------------------|------------|
| **范围** | 学习 + 规划 + 执行 | 仅执行 | 职责单一 |
| **自治度** | 完全自主（从问题到方案） | 半自主（需plan提供任务树） | 区分认知层次 |
| **输入** | 问题/需求 | 结构化任务 | 抽象层次不同 |
| **复杂度** | 高（需要智能决策） | 中（主要是执行控制） | 便于调试优化 |
| **典型场景** | 探索未知问题 | 执行已知计划 | 解耦关注点 |

**类比**:
- **Learn** = 资深架构师（知道如何学习、规划、实施）
- **Plan** = 项目经理（知道如何拆解任务）
- **Iterate** = 技术主管（知道如何带领团队执行）

---

## 工具与脚本

### 辅助脚本: task-executor.py

```python
#!/usr/bin/env python3
"""
任务执行器 - 执行单个任务并验证
"""

import subprocess
import time
from pathlib import Path

class TaskExecutor:
    def __init__(self, workspace="."):
        self.workspace = Path(workspace)

    def execute(self, task):
        """
        执行任务

        Returns:
            {
                "status": "success|failed|error",
                "duration": seconds,
                "output": str,
                "error": str (if failed),
                "artifacts": [files created/modified]
            }
        """
        start_time = time.time()
        result = {
            "status": "unknown",
            "duration": 0,
            "output": "",
            "error": None,
            "artifacts": []
        }

        try:
            # 根据任务类型选择执行方式
            if task["type"] == "database":
                exec_result = self._execute_sql(task["sql_file"])

            elif task["type"] == "file_create":
                exec_result = self._create_file(
                    task["file_path"],
                    task["content"]
                )

            elif task["type"] == "command":
                exec_result = self._run_command(task["command"])

            elif task["type"] == "test":
                exec_result = self._run_tests(task["test_files"])

            else:
                exec_result = {
                    "status": "error",
                    "error": f"未知任务类型: {task['type']}"
                }

            # 记录执行结果
            result.update(exec_result)
            result["duration"] = time.time() - start_time

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)

        return result

    def _execute_sql(self, sql_file):
        """执行SQL文件"""
        cmd = f"psql -f {sql_file}"
        return self._run_command(cmd)

    def _create_file(self, file_path, content):
        """创建文件"""
        path = Path(file_path)
        path.write_text(content)
        return {
            "status": "success",
            "artifacts": [str(path)]
        }

    def _run_command(self, command):
        """运行Shell命令"""
        process = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True
        )

        if process.returncode == 0:
            return {
                "status": "success",
                "output": process.stdout
            }
        else:
            return {
                "status": "failed",
                "output": process.stdout,
                "error": process.stderr
            }

    def _run_tests(self, test_files):
        """运行测试"""
        cmd = f"npm test {' '.join(test_files)}"
        return self._run_command(cmd)


# 使用示例
if __name__ == "__main__":
    executor = TaskExecutor(workspace=".")

    # 执行任务: 创建User表
    task = {
        "type": "database",
        "sql_file": "migrations/001-create-user.sql"
    }

    result = executor.execute(task)
    print(json.dumps(result, indent=2))
```

---

## 最佳实践

### 实践1: 先规划，再执行

```bash
# 正确流程
✅ /runtime.plan "需求"  → 生成计划
✅ /runtime.iterate --plan=xxx.json  → 执行计划
✅ /runtime.reflect  → 回顾

# 错误
❌ /runtime.iterate  # 没有提供计划文件
```

### 实践2: 选择合适的策略

```bash
# 不同类型的项目用不同策略
✅ 新功能开发（基础重要）: --strategy=breadth
✅ PoC演示（快速验证）: --strategy=depth
✅ 技术调研（风险消除）: --strategy=risk
✅ MVP产品（价值优先）: --strategy=value
```

### 实践3: 定期检查（Reflect）

```bash
# 每5次迭代后强制检查
/runtime.iterate --plan=xxx.json --reflect-interval=5

# 或在执行后手动
/runtime.reflect
"""
上次5次迭代的模式：
- 估算准确率: 85%
- 常见失败类型: 依赖配置
- 发现的新任务: 平均每次迭代1.2个

改进建议:
- 预检查阶段增强配置验证
- 为配置任务添加专门检查清单
"""
```

### 实践4: 优雅失败与恢复

```python
# 不是暴力失败
try:
    result = execute(task)
except Exception as e:
    # 记录
    log_failure(task, e)

    # 分析
    failure_type = analyze_failure(e)

    # 适应（不是panic）
    if failure_type == FAIL_TRANSIENT:
        retry(task)
    elif failure_type == FAIL_COMPLEX:
        decompose(task)
    elif failure_type == FAIL_DESIGN:
        learn_and_redesign(task)
    elif failure_type == FAIL_REQUIREMENT:
        ask_clarification()

    # 继续（不是所有都停止）
    continue_execution()
```

---

## 宪法遵循

**遵循原则**:
- ✓ 2.2 渐进式实施: 持续交付价值
- ✓ 4.4 规划透明: 执行过程可见
- ✓ 1.3 谦逊与不确定: 失败时承认并学习
- ✓ 4.1 从经验学习: 每次迭代都更新认知
- ✓ 4.3 自我反思: 定期评估执行效果

---

**命令定义**: `.ai-runtime/commands/runtime.iterate.md`
**脚本**: `.ai-runtime/scripts/task-executor.py`
**输出**: `cognition/execution-reports/*.json`
**版本**: 1.0.0
