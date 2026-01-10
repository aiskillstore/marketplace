# 动画提升：Apple 级动效体验

> **前置条件**：必须先完成设计系统初始化和页面内容搭建。
> 本步骤使用 Framer Motion 为所有页面添加 Apple 级动画细节。

---

## 核心哲学

```
Apple 动效 = Spring 弹簧 + 阻尼落定 + 物理惯性

每个动画都要有：
- 自然的起势（不是突然开始）
- 优雅的落定（不是戛然而止）
- 物理的重量感（像真实物体在移动）

禁止：
- 线性动画（linear）
- 无阻尼的弹跳
- 同时触发超过 3 个动画

必须：
- Spring 物理引擎
- 支持 prefers-reduced-motion
- 使用设计系统的缓动曲线
```

---

## Apple 风格 Spring 配置

```javascript
// 标准交互 - 按钮、卡片 hover
const snappy = { type: "spring", stiffness: 400, damping: 30 }

// 柔和过渡 - 面板展开、模态框
const gentle = { type: "spring", stiffness: 300, damping: 35 }

// 弹性强调 - 成功反馈、关键元素
const bouncy = { type: "spring", stiffness: 500, damping: 25, mass: 0.8 }

// 优雅落定 - 页面过渡、大元素移动
const smooth = { type: "spring", stiffness: 200, damping: 40, mass: 1.2 }

// 惯性滑动 - 列表、轮播
const inertia = { type: "spring", stiffness: 150, damping: 20, mass: 0.5 }
```

---

## 动画时长参考

| 场景 | Spring 配置 | 体感时长 |
|------|-------------|----------|
| 微交互 | stiffness: 400, damping: 30 | ~200ms |
| 元素进场 | stiffness: 300, damping: 35 | ~350ms |
| 页面切换 | stiffness: 200, damping: 40 | ~500ms |
| 弹性强调 | stiffness: 500, damping: 25 | ~300ms |

---

## Apple 缓动曲线（非 Spring 场景）

```javascript
// iOS 标准曲线
const appleEase = [0.25, 0.1, 0.25, 1.0]

// iOS 弹出曲线
const appleEaseOut = [0.22, 1, 0.36, 1]

// iOS 减速曲线
const appleDecelerate = [0, 0, 0.2, 1]
```

---

## 动画模式库

### 1. 淡入上移（Spring 版）

```jsx
const fadeInUp = {
  hidden: { opacity: 0, y: 24 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      type: "spring",
      stiffness: 300,
      damping: 30
    }
  }
}
```

### 2. 弹性缩放

```jsx
const scaleIn = {
  hidden: { opacity: 0, scale: 0.9 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: {
      type: "spring",
      stiffness: 400,
      damping: 25
    }
  }
}
```

### 3. 序列进场（带阻尼）

```jsx
const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.06,
      delayChildren: 0.1
    }
  }
}

const staggerItem = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      type: "spring",
      stiffness: 350,
      damping: 30
    }
  }
}
```

### 4. 悬浮提升（Apple Card 效果）

```jsx
const hoverLift = {
  rest: {
    scale: 1,
    y: 0,
    boxShadow: "0 4px 12px rgba(0,0,0,0.1)"
  },
  hover: {
    scale: 1.02,
    y: -4,
    boxShadow: "0 12px 32px rgba(0,0,0,0.15)",
    transition: {
      type: "spring",
      stiffness: 400,
      damping: 25
    }
  }
}
```

### 5. 点击反馈（弹性回弹）

```jsx
const tapScale = {
  rest: { scale: 1 },
  pressed: {
    scale: 0.96,
    transition: {
      type: "spring",
      stiffness: 500,
      damping: 30
    }
  }
}
```

### 6. 模态框（优雅落定）

```jsx
const modalOverlay = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { duration: 0.2 }
  }
}

const modalContent = {
  hidden: { opacity: 0, scale: 0.95, y: 20 },
  visible: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: {
      type: "spring",
      stiffness: 300,
      damping: 35
    }
  },
  exit: {
    opacity: 0,
    scale: 0.95,
    transition: { duration: 0.15 }
  }
}
```

### 7. 页面路由过渡

```jsx
const pageTransition = {
  initial: { opacity: 0, x: 20 },
  animate: {
    opacity: 1,
    x: 0,
    transition: {
      type: "spring",
      stiffness: 260,
      damping: 40
    }
  },
  exit: {
    opacity: 0,
    x: -20,
    transition: { duration: 0.2 }
  }
}
```

---

## 升级任务

理解上述 Apple 动效哲学后，为项目中的所有页面添加动画细节：

**全局层面**
- 页面路由切换（AnimatePresence + pageTransition）
- 滚动触发动画（whileInView + Spring）

**组件层面**
- Card 悬浮提升（hoverLift）
- Button 点击回弹（tapScale）
- Modal 弹性弹出（modalContent）
- 列表 stagger 进场

**细节层面**
- 图标 hover 微动效
- 输入框 focus 反馈
- 加载状态过渡
- 成功/错误状态动画

**联想升级原则**：
1. 所有动画优先使用 Spring 物理引擎
2. 进场用 Spring，退场用短 duration
3. 阻尼值 25-40 之间找平衡
4. 测试真机体感，调整 stiffness

---

## 可访问性要求

```jsx
import { MotionConfig } from "framer-motion"

<MotionConfig reducedMotion="user">
  <App />
</MotionConfig>
```

---

## 最终验收

动画升级完成后，检查以下体验是否达到 Apple 级：

1. 首屏加载 → 元素依次弹入，有落定感
2. 卡片悬浮 → 轻盈提升，阴影加深
3. 按钮点击 → 即时回弹，手感紧致
4. 模态弹出 → 优雅展开，背景柔和淡入
5. 页面跳转 → 丝滑过渡，无突兀感

---

## GEB 分形文档检查

完成动画提升后，**必须执行**以下文档同步：

```
L3 检查 → 新创建的 motion.js 或动画相关文件头部注释是否完整？
L2 检查 → lib/CLAUDE.md 是否记录动画配置模块？
L1 检查 → 项目根目录 CLAUDE.md 是否更新动画系统说明？
```

确保代码与文档同构，完成后等待下一步指令。
