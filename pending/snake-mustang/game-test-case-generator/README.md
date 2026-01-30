# 游戏测试用例智能生成器 (Game Test Case Generator)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

一个基于 AI 的游戏测试用例自动生成工具，专为游戏研发团队设计，支持从需求文档（Excel/CSV）自动生成标准化、全场景覆盖的测试用例。

> 🎯 **核心价值**：将测试用例编写效率提升 10 倍，从 1 天人工编写缩短至 10 分钟 AI 生成

## ✨ 功能特性

- 🚀 **双模式生成**
  - **完整模式**：包含详细的前置条件、操作步骤、预期结果、异常分支
  - **快速模式**：简洁的测试点清单，适合快速评审

- 📂 **多格式支持**
  - 输入：Excel (.xls/.xlsx)、CSV、文本描述、原型图片
  - 输出：Markdown、Excel、Xmind（思维导图）

- 🎮 **游戏行业专精**
  - 预置游戏常见测试场景（登录、战斗、商城、社交等）
  - 自动识别功能模块、玩法流程、UI交互
  - 覆盖正常/边界/异常三类场景

- 🔍 **智能分析**
  - 自动标注需求中的模糊点和待确认项
  - 推荐解决方案和备选方案
  - 生成统计分析报告

- 📊 **质量保证**
  - 需求覆盖率 ≥ 95%
  - 每个功能点至少 3 个场景（正常/边界/异常）
  - 无模糊表述，所有预期结果可量化验证

## 🚀 快速开始

### 作为 Cursor/Claude 技能使用

1. **安装到 Cursor**
   ```bash
   # 复制整个目录到 Cursor 技能目录
   cp -r sy-testcase-generator ~/.cursor/skills/
   # 或项目级别
   cp -r sy-testcase-generator .cursor/skills/
   ```

2. **触发使用**
   在 Cursor 中直接说：
   ```
   "根据这个需求文档生成游戏测试用例"
   "用快速模式生成登录模块的测试点"
   "分析 xuqiu.csv 并生成完整测试用例"
   ```

### 作为独立工具使用

1. **安装依赖**
   ```bash
   cd sy-testcase-generator
   pip install -r scripts/requirements.txt
   ```

2. **生成测试用例**
   使用您喜欢的 AI 工具（ChatGPT/Claude/本地模型）配合 `SKILL.md` 中的提示词

3. **格式转换**
   ```bash
   # 转换为 Excel
   python scripts/convert_to_excel.py test_cases.md -o output.xlsx
   
   # 转换为 Xmind 格式
   python scripts/convert_to_xmind.py test_cases.md -o xmind_import.md
   ```

## 📖 使用示例

### 示例 1：从 CSV 需求生成测试用例

**输入文档**：`xuqiu.csv`（探宝轮盘活动需求）

**生成结果**：
- ✅ 103 个测试点
- ✅ 涵盖 4 个功能模块
- ✅ 7 个待确认项标注
- ✅ 包含性能、安全、兼容性测试

查看完整示例：[探宝轮盘测试用例.md](./examples/探宝轮盘测试用例.md)

### 示例 2：登录功能测试用例

**输入**：
```
用户登录功能需求：
1. 支持账号密码登录
2. 账号长度6-20位，密码长度8-32位
3. 连续5次密码错误锁定账号30分钟
4. 登录响应时间不超过2秒
```

**输出**：48 个测试点，涵盖核心、边界、异常、性能、安全、兼容性、UI 测试

查看完整示例：[demo_test_cases.md](./examples/demo_test_cases.md)

## 📁 项目结构

```
sy-testcase-generator/
├── SKILL.md                    # 核心技能文件（AI 使用）
├── README.md                   # 本文件
├── templates/                  # 测试用例模板
│   ├── full-template.md        # 完整用例模板
│   └── quick-template.md       # 快速测试点模板
├── scripts/                    # 格式转换工具
│   ├── convert_to_excel.py     # Markdown → Excel
│   ├── convert_to_xmind.py     # Markdown → Xmind
│   └── requirements.txt        # Python 依赖
└── examples/                   # 示例文件（可选）
```

## 🎯 生成的测试用例包含

### 完整模式
- ✅ 用例编号（模块-功能-场景类型）
- ✅ 测试类型（功能/性能/兼容性/安全）
- ✅ 优先级（高/中/低）
- ✅ 前置条件
- ✅ 详细操作步骤
- ✅ 预期结果（可量化验证）
- ✅ 异常分支处理
- ✅ 测试数据

### 快速模式
- ✅ 核心测试点（正常场景）
- ✅ 边界测试点（极限值、临界值）
- ✅ 异常测试点（错误处理、容错能力）
- ✅ 性能测试点（响应时间、并发）
- ✅ 安全测试点（防刷、防作弊）
- ✅ 兼容性测试点（多平台、多设备）
- ✅ UI 测试点（界面元素验证）
- ✅ 待确认项（需求模糊点标注）

## 🔧 高级配置

### 自定义模板

您可以修改 `templates/` 目录下的模板文件来适配团队规范：

```bash
templates/
├── full-template.md      # 修改完整用例格式
└── quick-template.md     # 修改快速测试点格式
```

### 调整生成策略

在 `SKILL.md` 中可以调整：
- 测试场景覆盖策略（正常/边界/异常比例）
- 用例编号规则
- 优先级定义标准
- 质量检查标准

## 📊 效果对比

| 指标 | 人工编写 | AI 生成 | 提升 |
|------|---------|---------|------|
| **时间** | 1 天 | 10 分钟 | **96% ↓** |
| **覆盖度** | 60-70% | 95%+ | **35% ↑** |
| **一致性** | 中等 | 高 | **标准化** |
| **遗漏率** | 10-20% | <5% | **75% ↓** |

## 🛠️ 产品化方案

本项目可扩展为企业级产品，支持：

### 方案 1：Web 应用
- 前端：React + Ant Design
- 后端：FastAPI + PostgreSQL
- AI：OpenAI API / 本地模型
- 部署：Docker + 云服务

### 方案 2：企业平台集成
- 与 JIRA/Tapd 集成（需求同步）
- 与 TestRail/禅道集成（用例导入）
- 与钉钉/企业微信集成（机器人通知）

### 方案 3：桌面应用
- Electron + Vue（跨平台）
- 本地部署，数据安全
- 支持离线使用

详细方案请参考：[产品化方案文档](./docs/productization.md)（待补充）

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/snake-mustang/sy-testcase-generator.git
cd sy-testcase-generator

# 安装依赖
pip install -r scripts/requirements.txt

# 运行测试
python scripts/convert_to_excel.py examples/demo_test_cases.md -o test_output.xlsx
```

### 提交规范

- feat: 新功能
- fix: 修复问题
- docs: 文档更新
- style: 代码格式调整
- refactor: 重构代码
- test: 测试相关
- chore: 构建/工具链相关

## 📝 许可证

本项目采用 [MIT License](LICENSE)

## 🙏 致谢

- 基于 Claude/GPT 等大语言模型的强大能力
- 感谢游戏测试团队提供的宝贵反馈

## 📧 联系方式

- GitHub: [@snake-mustang](https://github.com/snake-mustang)
- 项目主页: [sy-testcase-generator](https://github.com/snake-mustang/sy-testcase-generator)

---

⭐ 如果这个项目对您有帮助，请给个 Star 支持一下！

**版本**：v1.0.0  
**更新时间**：2026-01-27
