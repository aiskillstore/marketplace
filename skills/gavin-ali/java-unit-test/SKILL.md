---
name: java-unit-test
description: 为 Java 项目生成自动化单元测试（JUnit 5 + Mockito）。当用户要求编写单元测试、生成测试用例或提升测试覆盖率时使用。
---

# Java Unit Test Skill

## 触发条件

当用户提出以下需求时激活本技能（包含同义表达）：

- 帮我写单元测试 / 为这个类写测试 / 生成测试用例
- 提升测试覆盖率 / 补齐测试 / 覆盖率不达标
- junit test / mockito test / unit test

## 前置检查清单

在生成测试代码前，必须完成以下检查与信息收集（缺失则先补齐）：

### 1) 识别被测类（SUT）

- 读取被测类源文件与其直接依赖（构造参数、字段注入、静态依赖）
- 记录包名、类名、可见性、构造方法、所有 public 方法签名

### 2) 分析类结构与行为

- 逐个梳理 public 方法：
  - 入参、返回值、抛出异常
  - 分支条件与边界值（null/空集合/0/负数/超长字符串等）
  - 外部交互：数据库/缓存/HTTP/RPC/文件/时间/随机数等

### 3) 识别依赖与可 Mock 点

- 识别可替换依赖（接口/组件/DAO/Client），明确 Mock/Spy 的对象
- 标记不可 Mock 或较难 Mock 的点（static/final/private/new 出来的对象）

### 4) 确认测试工程与框架约束

- 确认项目使用的测试框架与版本（JUnit 4/5，Mockito，Spring Test 等）
- 确认测试源码目录结构（例如：src/test/java 与包路径对齐）
- 确认断言库与风格（JUnit Assertions / AssertJ / Hamcrest 等，优先跟随项目现状）

## 测试代码生成规范

### 1) 测试类命名规范

- 测试类名：{被测类名}Test
- 若存在多实现或多场景拆分：{被测类名}{场景}Test（例如：OrderServiceCreateTest）

### 2) Import 声明规范

- 按以下顺序组织 import：
  1. java.*
  2. javax.*
  3. 第三方库（org.* / com.*）
  4. 项目内部包
  5. static import（断言、Mockito 静态方法）
- 禁止未使用 import

### 3) 测试类结构模板

- 统一结构：
  - Mock 声明区
  - 被测对象构建区（如 @InjectMocks 或手动 new）
  - 通用测试数据构建方法（可选）
  - 用例区：按被测方法分组

推荐的骨架（根据项目框架选择其一）：

1) 纯 Mockito（优先）：
   - @ExtendWith(MockitoExtension.class)
   - @Mock 依赖
   - @InjectMocks 被测对象（或构造注入手动 new）

2) Spring 参与（仅当项目已有此风格且确有必要）：
   - @SpringBootTest / @ExtendWith(SpringExtension.class)
   - @MockBean 替换外部依赖

### 4) Mock 对象配置规范

- Mock 行为遵循 “最小必要” 原则：只 stub 当前用例需要的调用
- 对外部依赖交互必须验证（verify）：
  - 是否被调用
  - 调用次数（times / never）
  - 关键入参（ArgumentCaptor 或 eq）
- 不要过度验证实现细节（避免脆弱测试）

### 5) 测试数据构建规范

- 优先使用 Builder/Factory 方法构建测试数据（若项目已有）
- 没有 Builder 时，使用专用的私有方法构造常见对象：
  - buildValidXxx()
  - buildXxxWithBoundary()
- 避免在单个测试方法内堆叠大量对象构建逻辑

### 6) 断言规范

- 每个测试只断言该场景的关键输出与关键副作用
- 断言优先级：
  - 业务返回值/状态
  - 对外部依赖的交互（verify）
  - 产生的持久化/事件（如有）

### 7) 异常与边界用例规范

- 对非法参数、依赖异常、返回空值/空集合的场景必须覆盖
- 异常断言使用 assertThrows，并校验异常信息或错误码（若稳定）

### 8) 参数化测试（可选）

- 当存在多个等价输入组合且断言相同，优先使用参数化测试
- 仅在项目已使用 JUnit 5 参数化支持时启用

## 测试用例设计原则

### 1) 覆盖策略

- 覆盖 public 方法的：
  - 正常流程（Happy Path）
  - 关键分支（if/else、switch、early return）
  - 边界条件（边界值、空值、极端值）
  - 异常流程（依赖抛错、业务校验失败）

### 2) 测试金字塔

- 单元测试优先覆盖纯业务逻辑与边界条件
- 集成测试只覆盖关键链路与契约（本技能重点在单元测试）

### 3) 覆盖率目标（按团队要求调整）

- 以可维护性优先，覆盖关键逻辑与高风险模块
- 对“薄封装/纯转发”代码不过度追求覆盖率

## 最佳实践清单

### 命名清单

- 测试方法名包含：方法名 + 场景 + 预期结果
- 命名风格统一（可选其一并保持一致）：
  - shouldXxxWhenYyy
  - givenYyyWhenXxxThenZzz

### 结构清单

- Arrange / Act / Assert 三段式清晰
- 单测不依赖执行顺序，可重复执行
- 单测不依赖真实时间/随机数（必要时注入 Clock/Random 或封装）

### 断言清单

- 断言尽量具体，避免 “只 assertNotNull” 的弱断言
- 对集合/对象断言关注关键字段，避免断言全量对象导致脆弱

### Mock 清单

- 避免 deep stubs
- 避免对私有方法做测试（测试对外可观察行为）

### 性能清单

- 单测应快速（通常毫秒级）
- 避免线程 sleep、真实 IO、网络请求

## 常见问题与解决方案

### 1) 静态方法难以 Mock

- 优先重构：用可注入的依赖封装静态调用
- 若项目已启用 Mockito inline 等能力，再考虑静态 Mock（谨慎使用）

### 2) final 类/方法 Mock 问题

- 优先遵循项目现有 Mockito 配置；必要时使用 Mockito inline

### 3) 私有方法怎么测

- 不直接测试私有方法；通过 public 方法的输入输出与副作用覆盖其逻辑