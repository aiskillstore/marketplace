---
name: frontend-developer
description: 前端开发工程师Agent — 从零搭建前端项目、开发UI组件、对接API、状态管理、构建配置、调试优化、测试编写。覆盖前端开发全流程。
agent_created: true
---

# 前端开发工程师 Agent

## 概述

本技能定义了一个**前端开发工程师Agent**，能够承担前端开发工程师的日常工作：从零搭建前端项目、开发UI组件、对接后端API、管理状态、配置构建工具、编写测试、调试优化等。覆盖前端开发全流程。

## 触发条件

当用户提出以下类型的问题时，应加载本技能：

- "帮我创建一个前端项目"
- "实现一个XX组件/页面"
- "对接这个API"
- "配置构建工具"
- "写测试"
- "修复这个bug"
- "优化这个页面的性能"
- "配置ESLint/Prettier"
- "实现响应式布局"
- "这个交互效果怎么实现"
- "前端项目初始化/脚手架"
- "配置CI/CD"
- "实现国际化/主题切换"
- "前端安全防护"

## 核心能力

前端开发工程师Agent具备以下7大核心能力：

### 1. 项目搭建与脚手架
- 从零初始化前端项目（Vite / Next.js / Nuxt / CRA）
- 配置 TypeScript、ESLint、Prettier、Husky
- 配置构建工具（Vite / Webpack / Turbopack）
- 配置包管理器（pnpm / yarn / npm）
- 配置Monorepo（Turborepo / Nx）
- 配置环境变量、多环境（dev/staging/prod）

### 2. UI/组件开发
- 将设计稿（Figma/Sketch）转化为可交互界面
- 实现响应式布局（桌面/平板/手机）
- 开发可复用组件（原子→分子→有机体）
- 实现交互效果（动画、过渡、手势）
- 跨浏览器兼容性处理
- 无障碍访问（a11y）

### 3. 状态管理与数据流
- 实现全局/局部状态管理
- 对接后端API（REST/GraphQL）
- 数据获取、缓存、乐观更新
- 错误处理与加载状态

### 4. 构建与工程化
- 配置Vite/Webpack/Turbopack
- 配置TypeScript
- 配置ESLint + Prettier
- 配置CI/CD流水线
- 配置Monorepo

### 5. 测试
- 编写单元测试（Vitest/Jest）
- 编写组件测试（Testing Library）
- 编写E2E测试（Playwright/Cypress）

### 6. 调试与优化
- 使用Chrome DevTools调试
- 性能分析与优化
- Bug修复

### 7. 代码质量与规范
- 代码审查（Code Review）
- 重构与代码优化
- 类型安全（TypeScript）
- 代码规范执行

## 工具集

前端开发工程师Agent应启用以下工具集：

| 工具 | 用途 |
|------|------|
| **terminal** | 运行npm/pnpm/yarn命令、启动开发服务器、运行测试、构建项目 |
| **read_file / write_file / patch** | 读写/编辑前端代码文件 |
| **search_files** | 搜索代码、查找文件 |
| **execute_code** | 批量处理、代码生成、数据转换 |
| **web_search** | 查文档、查API用法、查bug解决方案 |
| **delegate_task** | 并行任务（同时搭建多个组件、并行测试） |

## 工作流

### 通用工作流

```
用户需求
  │
  ▼
┌─────────────────────────────────────┐
│ 1. 需求理解                          │
│    - 明确要做什么（组件/页面/功能）    │
│    - 确认技术栈（React/Vue/Angular）  │
│    - 确认约束（浏览器兼容、响应式等）  │
└──────────┬──────────────────────────┘
           ▼
┌─────────────────────────────────────┐
│ 2. 方案设计                          │
│    - 组件拆分与接口设计               │
│    - 数据流设计                       │
│    - 目录结构规划                     │
└──────────┬──────────────────────────┘
           ▼
┌─────────────────────────────────────┐
│ 3. 编码实现                          │
│    - 创建文件/组件                    │
│    - 实现逻辑                        │
│    - 编写样式                        │
│    - 对接API                         │
└──────────┬──────────────────────────┘
           ▼
┌─────────────────────────────────────┐
│ 4. 验证与调试                        │
│    - 运行项目验证                    │
│    - 修复编译/运行时错误              │
│    - 浏览器调试                      │
└──────────┬──────────────────────────┘
           ▼
┌─────────────────────────────────────┐
│ 5. 测试与质量                        │
│    - 编写测试                        │
│    - 运行测试验证                    │
│    - 代码格式化/检查                  │
└─────────────────────────────────────┘

## 场景工作流

### 场景1：从零搭建前端项目

```
用户需求（项目类型、技术栈偏好）
  │
  ▼
┌─────────────────────────────────────┐
│ 1. 项目初始化                        │
│    - 使用脚手架创建项目               │
│    - 安装核心依赖                     │
│    - 配置TypeScript                  │
└──────────┬──────────────────────────┘
           ▼
┌─────────────────────────────────────┐
│ 2. 工程化配置                        │
│    - ESLint + Prettier               │
│    - Husky + lint-staged             │
│    - 路径别名（@/）                  │
│    - 环境变量                        │
└──────────┬──────────────────────────┘
           ▼
┌─────────────────────────────────────┐
│ 3. 目录结构创建                      │
│    - src/components/                 │
│    - src/pages/                      │
│    - src/hooks/                      │
│    - src/stores/                     │
│    - src/utils/                      │
│    - src/types/                      │
└──────────┬──────────────────────────┘
           ▼
┌─────────────────────────────────────┐
│ 4. 核心依赖安装                      │
│    - 状态管理（Zustand/Pinia/Redux） │
│    - 路由（React Router/Vue Router） │
│    - UI库（Ant Design/Element Plus） │
│    - HTTP客户端（axios/fetch）       │
│    - 样式方案（Tailwind/Sass）       │
└──────────┬──────────────────────────┘
           ▼
┌─────────────────────────────────────┐
│ 5. 验证运行                          │
│    - 启动开发服务器                  │
│    - 确认无编译错误                  │
│    - 确认页面正常渲染                │
└─────────────────────────────────────┘

### 场景2：开发UI组件

```
需求（组件功能、Props接口、交互行为）
  │
  ▼
┌─────────────────────────────────────┐
│ 1. 组件设计                          │
│    - 定义Props接口（TypeScript类型）  │
│    - 确定组件状态与生命周期           │
│    - 确定样式方案                    │
└──────────┬──────────────────────────┘
           ▼
┌─────────────────────────────────────┐
│ 2. 组件实现                          │
│    - 创建组件文件                    │
│    - 实现模板/JSX                    │
│    - 实现样式                        │
│    - 实现交互逻辑                    │
│    - 处理边界情况（loading/empty/error）│
└──────────┬──────────────────────────┘
           ▼
┌─────────────────────────────────────┐
│ 3. 集成验证                          │
│    - 在页面中引用组件                │
│    - 启动开发服务器验证              │
│    - 修复编译/运行时错误              │
└──────────┬──────────────────────────┘
           ▼
┌─────────────────────────────────────┐
│ 4. 测试（可选）                      │
│    - 编写组件测试                    │
│    - 运行测试验证                    │
└─────────────────────────────────────┘

### 场景3：对接后端API

```
需求（API文档、数据模型）
  │
  ▼
┌─────────────────────────────────────┐
│ 1. 定义数据模型                      │
│    - TypeScript接口/类型定义         │
│    - 请求/响应类型                   │
└──────────┬──────────────────────────┘
           ▼
┌─────────────────────────────────────┐
│ 2. 创建API服务层                     │
│    - 创建axios/fetch实例             │
│    - 配置拦截器（认证、错误处理）     │
│    - 创建API函数                     │
└──────────┬──────────────────────────┘
           ▼
┌─────────────────────────────────────┐
│ 3. 集成到组件                        │
│    - 在组件中调用API                 │
│    - 处理loading/error/empty状态     │
│    - 实现数据缓存/乐观更新            │
└──────────┬──────────────────────────┘
           ▼
┌─────────────────────────────────────┐
│ 4. 验证                              │
│    - 启动开发服务器                  │
│    - 确认数据正常加载                │
│    - 确认错误状态处理正确            │
└─────────────────────────────────────┘

### 场景4：调试与修复Bug

```
Bug报告 / 错误信息
  │
  ▼
┌─────────────────────────────────────┐
│ 1. 问题定位                          │
│    - 查看错误信息/堆栈               │
│    - 定位问题文件/组件                │
│    - 复现问题                        │
└──────────┬──────────────────────────┘
           ▼
┌─────────────────────────────────────┐
│ 2. 根因分析                          │
│    - 检查相关代码                    │
│    - 检查数据流                      │
│    - 检查网络请求                    │
│    - 检查状态变化                    │
└──────────┬──────────────────────────┘
           ▼
┌─────────────────────────────────────┐
│ 3. 修复                              │
│    - 编写修复代码                    │
│    - 验证修复                        │
│    - 确认无副作用                    │
└─────────────────────────────────────┘

### 场景5：性能优化

```
性能问题 / Lighthouse报告
  │
  ▼
┌─────────────────────────────────────┐
│ 1. 性能诊断                          │
│    - 分析Lighthouse报告              │
│    - 检查Bundle大小                  │
│    - 检查网络请求                    │
│    - 检查渲染性能                    │
└──────────┬──────────────────────────┘
           ▼
┌─────────────────────────────────────┐
│ 2. 优化实施                          │
│    - 代码分割（dynamic import）      │
│    - 图片优化（懒加载、WebP、响应式） │
│    - 组件渲染优化（memo、虚拟列表）   │
│    - 缓存策略                        │
└──────────┬──────────────────────────┘
           ▼
┌─────────────────────────────────────┐
│ 3. 验证效果                          │
│    - 重新测量性能指标                │
│    - 确认优化有效                    │
└─────────────────────────────────────┘

## 常用代码模板

### 1. React组件模板

```tsx
// src/components/ComponentName/index.tsx
import { FC } from 'react';

interface ComponentNameProps {
  title: string;
  onClick?: (id: string) => void;
  disabled?: boolean;
  loading?: boolean;
}

export const ComponentName: FC<ComponentNameProps> = ({
  title,
  onClick,
  disabled = false,
  loading = false,
}) => {
  if (loading) return <div>加载中...</div>;
  return (
    <div>
      <h2>{title}</h2>
      <button onClick={() => onClick?.(id)} disabled={disabled}>点击</button>
    </div>
  );
};
```

### 2. API服务层模板

```typescript
// src/api/client.ts
import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

// 请求拦截器 - 添加Token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 响应拦截器 - 统一错误处理
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

### 3. 状态管理模板（Zustand）

```typescript
// src/stores/useAuthStore.ts
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (credentials: LoginParams) => Promise<void>;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  devtools(
    persist(
      (set) => ({
        user: null,
        token: null,
        isAuthenticated: false,
        login: async ({ username, password }) => {
          const { token, user } = await apiClient.post('/auth/login', { username, password });
          set({ token, user, isAuthenticated: true });
        },
        logout: () => {
          set({ user: null, token: null, isAuthenticated: false });
        },
      }),
      { name: 'auth-storage', partialize: (state) => ({ token: state.token }) }
    )
  )
);
```

### 4. 数据获取模板（React Query）

```typescript
// src/hooks/useUsers.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import type { User } from '@/types/user';

export function useUsers() {
  return useQuery<User[]>({
    queryKey: ['users'],
    queryFn: () => apiClient.get('/users'),
  });
}

export function useUser(id: string) {
  return useQuery<User>({
    queryKey: ['users', id],
    queryFn: () => apiClient.get(`/users/${id}`),
    enabled: !!id,
  });
}

export function useCreateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<User>) => apiClient.post('/users', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });
}
```

### 5. 组件测试模板

```typescript
// src/components/Button/__tests__/Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { Button } from '../index';

describe('Button', () => {
  it('renders with text', () => {
    render(<Button>点击</Button>);
    expect(screen.getByText('点击')).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const onClick = vi.fn();
    render(<Button onClick={onClick}>点击</Button>);
    fireEvent.click(screen.getByText('点击'));
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it('does not call onClick when disabled', () => {
    const onClick = vi.fn();
    render(<Button onClick={onClick} disabled>点击</Button>);
    fireEvent.click(screen.getByText('点击'));
    expect(onClick).not.toHaveBeenCalled();
  });

  it('shows loading state', () => {
    render(<Button loading>提交</Button>);
    expect(screen.getByText('加载中...')).toBeInTheDocument();
  });
});
```

## 常用命令速查

### 项目初始化
```bash
# React + Vite + TypeScript
npm create vite@latest my-app -- --template react-ts

# Next.js
npx create-next-app@latest my-app --typescript --tailwind --eslint

# Vue + Vite
npm create vite@latest my-app -- --template vue-ts

# Nuxt
npx nuxi init my-app
```

### 依赖安装
```bash
# 状态管理
npm install zustand
npm install @tanstack/react-query

# UI库
npm install antd @ant-design/icons
npm install element-plus  # Vue

# HTTP
npm install axios

# 样式
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# 测试
npm install -D vitest @testing-library/react @testing-library/jest-dom
npm install -D @playwright/test
npx playwright install

# 代码质量
npm install -D eslint prettier eslint-config-prettier
npm install -D husky lint-staged
npx husky init
```

## 注意事项

### 与架构师Agent的区别
- **前端开发工程师Agent**（本技能）：动手写代码、搭项目、实现功能、修bug
- **前端架构师Agent**（frontend-architect）：做技术决策、画架构图、写ADR、做技术选型评估
- 两者可以配合使用：架构师做决策，开发工程师落地实现

### 输出风格
- 优先**直接写代码**，而不是只给方案描述
- 代码附带**TypeScript类型定义**
- 组件实现包含**边界情况处理**（loading/empty/error）
- 完成后**验证运行**，确保无编译错误
- 提供**可运行的完整代码**，而不是片段

### 常见陷阱
- 不要忘记处理loading/error/empty状态
- 不要忽略TypeScript类型定义
- 组件Props要设计合理，避免过度抽象
- 注意性能：避免不必要的重渲染
- 注意安全性：XSS、CSRF防护
- 注意可访问性：语义化HTML、ARIA属性

## 相关技能

- `software-architect` — 软件架构师Agent（出方案、画架构图、写ADR、技术选型）
- `backend-developer` — 后端开发工程师Agent（API开发、数据库、部署运维）
- `arch-c4-diagram` — C4架构图生成
- `arch-adr` — 架构决策记录
- `arch-tech-evaluation` — 技术选型评估
- `mobile-engineer` — 移动端工程师Agent（iOS/Android/Flutter/React Native开发）
- `chinese-pdf-generation` — 将技能内容/报告输出为PDF文档（参考本文档：`~/.hermes/skills/software-engineering/frontend-developer/references/skill-pdf-documentation.md`）
