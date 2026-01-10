# Genesis

> 太初有道，道生代码

## 能干嘛

**一句话，秒级创建生产级项目：**

| 说这句话 | 得到什么 |
|---------|---------|
| "创建 React 项目" | React 19 + Vite + TailwindCSS V4 + shadcn/ui |
| "创建 Python 后端" | FastAPI + UV + SQLModel + AsyncPG |
| "创建 Go 后端" | Gin + GORM + Viper |
| "新建小程序" | Taro 4.x + React + TailwindCSS V4 + 跨端支持 |
| "生成落地页" | 10 个标准 Section + Framer Motion 动画 |
| "动画提升" | 为现有项目添加 Apple 级动效 |

**不是空壳子**：模板自带完整目录结构、配置文件、示例代码，开箱即用。

---

## 如何安装

### 方式一：让 AI 安装（推荐）

把这段话发给 Claude Code：

```
帮我安装 Genesis Skill：https://github.com/BellyBook/genesis
```

### 方式二：Git Clone

```bash
git clone https://github.com/BellyBook/genesis.git ~/.claude/skills/genesis
```

### 验证安装

```bash
ls ~/.claude/skills/genesis/SKILL.md
```

---

## 使用示例

### 创建 React 前端

```
你：创建一个 React 项目叫 my-app

Claude：请选择初始化模式：
        A 模板复制：秒级启动
        B AI 生成：可深度定制

你：A

Claude：[复制模板 → 安装依赖 → 启动开发服务器]
        项目已创建：~/projects/my-app
        运行 npm run dev 启动
```

### 创建 Python 后端

```
你：用 FastAPI 创建一个后端项目

Claude：请选择初始化模式...

你：A

Claude：[复制模板 → uv sync → 启动服务]
        项目已创建，运行 ./local-run.sh 启动
```

### 创建 Go 后端

```
你：新建 Go Gin 项目

Claude：请选择初始化模式...

你：A

Claude：[复制模板 → go mod tidy → 启动服务]
        项目已创建，运行 go run cmd/api/main.go 启动
```

### 创建 Taro 小程序

```
你：新建一个小程序项目

Claude：请选择初始化模式...

你：A

Claude：[复制模板 → 安装依赖 → 启动开发]
        项目已创建，运行 npm run dev:weapp 启动微信小程序开发
```

### 生成落地页

```
你：给 my-app 生成一个落地页

Claude：[读取设计规范 → 生成 10 个 Section → 添加动画]
        落地页已生成：src/pages/LandingPage.tsx
```

### 动画提升

```
你：给这个项目加点动画

Claude：[分析现有组件 → 添加 Framer Motion → 配置过渡动效]
        已添加入场动画、hover 效果、页面过渡
```

---

## 触发词速查

| 意图 | 说法 |
|-----|------|
| React 前端 | 创建 React 项目、新建前端、Web 应用 |
| Python 后端 | Python 后端、FastAPI、创建 API |
| Go 后端 | Go 后端、Gin 项目、Go API |
| Taro 小程序 | 新建小程序、创建小程序、Taro 项目 |
| 落地页 | 生成落地页、Landing Page、官网首页 |
| 动画 | 动画提升、加动效、Apple 动画 |

---

## 两种模式

| 模式 | 速度 | 适用场景 |
|-----|------|---------|
| **A 模板复制** | 秒级 | 快速启动、标准项目 |
| **B AI 生成** | 分钟级 | 深度定制、学习过程 |

---

## 技术栈详情

### Web 前端
- React 19 + Vite 6
- TailwindCSS V4
- shadcn/ui 组件库
- 微拟物光影设计系统

### Python 后端
- FastAPI + Uvicorn
- UV 包管理器
- SQLModel ORM
- AsyncPG 异步数据库

### Go 后端
- Gin Web 框架
- GORM 数据库
- Viper 配置管理
- 标准目录结构

### Taro 小程序
- Taro 4.x 跨端框架
- React 18 + Hooks
- TailwindCSS V4 原子化样式
- weapp-tailwindcss 小程序适配
- 支持微信/支付宝/抖音/H5 多端

---

## License

MIT

