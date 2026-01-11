---
name: clean-code-reviewer
description: Analyze code quality based on "Clean Code" principles. Identify naming, function size, duplication, over-engineering, and magic number issues with severity ratings and refactoring suggestions. Use when the user requests code review, quality check, refactoring advice, Clean Code analysis, code smell detection, or mentions terms like 代码体检, 代码质量, 重构检查.
---

# Clean Code Review

基于《代码整洁之道》原则，聚焦 7 个高收益检查维度。

## Review Workflow

```
Review Progress:
- [ ] 1. Scan codebase: identify files to review
- [ ] 2. Check each dimension (naming, functions, DRY, YAGNI, magic numbers, clarity, conventions)
- [ ] 3. Rate severity (高/中/低) for each issue
- [ ] 4. Generate report sorted by severity
```

## 核心原则：功能保留

所有建议仅针对**实现方式**优化——绝不建议改变代码的功能、输出或行为。

## Check Dimensions

### 1. 命名问题【有意义的命名】

检查标志：
- `data1`, `temp`, `result`, `info`, `obj` 等无意义命名
- 同一概念多种命名（`get`/`fetch`/`retrieve` 混用）

```typescript
// ❌ 
const d = new Date();
const data1 = fetchUser();

// ✅ 
const currentDate = new Date();
const userProfile = fetchUser();
```

### 2. 函数问题【函数短小 + SRP】

检查标志：
- 函数超过 **100 行**
- 参数超过 **3 个**
- 函数做多件事

```typescript
// ❌ 7 个参数
function processOrder(user, items, address, payment, discount, coupon, notes)

// ✅ 使用参数对象
interface OrderParams { user: User; items: Item[]; shipping: Address; payment: Payment }
function processOrder(params: OrderParams)
```

### 3. 重复问题【DRY】

检查标志：
- 相似的 if-else 结构
- 相似的数据转换/错误处理逻辑
- Copy-paste 痕迹

### 4. 过度设计【YAGNI】

检查标志：
- 从未为 true 的 `if (config.legacyMode)` 分支
- 只有一个实现的接口
- 无用的 try-catch 或 if-else

```typescript
// ❌ YAGNI 违反：从未使用的兼容代码
if (config.legacyMode) {
  // 100 行兼容代码
}
```

### 5. 魔法数字【避免硬编码】

检查标志：
- 裸露数字无解释
- 硬编码字符串

```typescript
// ❌ 
if (retryCount > 3) // 3 是什么？
setTimeout(fn, 86400000) // 这是多久？

// ✅ 
const MAX_RETRY_COUNT = 3;
const ONE_DAY_MS = 24 * 60 * 60 * 1000;
```

### 6. 结构清晰度【可读性优先】

检查标志：
- 嵌套三元运算符
- 过度紧凑的单行代码
- 过深的条件嵌套（> 3 层）

```typescript
// ❌ 嵌套三元
const status = a ? (b ? 'x' : 'y') : (c ? 'z' : 'w');

// ✅ 使用 switch 或 if/else
function getStatus(a, b, c) {
  if (a) return b ? 'x' : 'y';
  return c ? 'z' : 'w';
}
```

### 7. 项目规范【一致性】

检查标志：
- import 顺序混乱（外部库 vs 内部模块）
- 函数声明风格不一致
- 命名规范不统一（camelCase vs snake_case 混用）

```typescript
// ❌ 风格不一致
import { api } from './api'
import axios from 'axios'  // 外部库应在前
const handle_click = () => { ... }  // 命名风格混用

// ✅ 统一风格
import axios from 'axios'
import { api } from './api'
function handleClick(): void { ... }
```

> [!TIP]
> 项目规范应参照 `CLAUDE.md` `AGENTS.md` 或项目约定的编码标准。

## Severity Levels

| 级别 | 标准 |
|------|------|
| 高 | 影响可维护性/可读性，应立即修复 |
| 中 | 有改进空间，建议修复 |
| 低 | 代码气味，可选优化 |

## Output Format

```markdown
### [问题类型]: [简述]

- **原则**: [Clean Code 原则]
- **位置**: `文件:行号`
- **级别**: 高/中/低
- **问题**: [具体描述]
- **建议**: [修复方向]
```

## References

**Detailed examples**: See [references/detailed-examples.md](references/detailed-examples.md)
- 各维度的完整案例（命名、函数、DRY、YAGNI、魔法数字）

**Language patterns**: See [references/language-patterns.md](references/language-patterns.md)
- TypeScript/JavaScript 常见问题
- Python 常见问题
- Go 常见问题

## Multi-Agent Parallel

按以下维度拆分给多 agent 并行：

1. **按检查维度** - 7 维度各一个 agent
2. **按模块/目录** - 不同模块各一个 agent
3. **按语言** - TypeScript、Python、Go 各一个 agent
4. **按文件类型** - 组件、hooks、工具函数、类型定义

示例：`/clean-code-reviewer --scope=components` 或 `--dimension=naming`

汇总时需去重和统一严重程度评定。
