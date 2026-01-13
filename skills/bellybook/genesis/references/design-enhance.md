# 设计提升：微拟物光影质感

> **前置条件**：必须先完成设计系统初始化，下载主题并安装 shadcn/ui 组件。

---

## 核心设计语言

```
微拟物 = 渐变背景 + 立体阴影 + 微交互

禁止：
- backdrop-blur 毛玻璃
- 0 0 Npx 发光扩散阴影
- 硬编码颜色值

必须：
- 全部使用 CSS 变量 + color-mix
- 三层阴影结构
- 大圆角 (20px+)
```

---

## 设计公式

### 1. 渐变背景

```css
/* 三段式渐变：亮 → 中 → 暗 */
background: linear-gradient(
  135deg,
  var(--primary) 0%,
  color-mix(in srgb, var(--primary) 85%, black) 50%,
  color-mix(in srgb, var(--primary) 70%, black) 100%
);
```

### 2. 立体阴影

```css
/* 三层：外投影 + 顶部高光 + 底部暗边 */
box-shadow:
  0 4px 12px color-mix(in srgb, var(--primary) 35%, transparent),
  inset 0 1px 0 rgba(255,255,255,0.2),
  inset 0 -1px 0 rgba(0,0,0,0.1);
```

### 3. Hover 增强

```css
box-shadow:
  0 6px 20px color-mix(in srgb, var(--primary) 45%, transparent),
  inset 0 1px 0 rgba(255,255,255,0.25),
  inset 0 -1px 0 rgba(0,0,0,0.15);
```

### 4. 微交互

```css
transition: all 0.2s ease;
hover: scale(1.02);
active: scale(0.97);
```

### 5. 圆角规范

```
sm: 16px | default: 20px | lg: 24px | xl: 32px
```

---

## Button 升级范例

以下是 Button 组件的完整升级实现，作为设计语言的参考范例：

```jsx
/**
 * [INPUT]: variant, size, isLoading, leftIcon, rightIcon, asChild, className
 * [OUTPUT]: 统一风格按钮组件（立体渐变效果）
 * [POS]: UI基础层 - 核心交互原语
 */
import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva } from "class-variance-authority"
import { Loader2 } from "lucide-react"
import { cn } from "@/lib/utils"

/* ========================================
   按钮样式配置 - 渐变 + 立体效果
   ======================================== */

const BUTTON_STYLES = {
  default: {
    background: 'linear-gradient(135deg, var(--primary) 0%, color-mix(in srgb, var(--primary) 85%, black) 50%, color-mix(in srgb, var(--primary) 70%, black) 100%)',
    boxShadow: '0 4px 12px color-mix(in srgb, var(--primary) 35%, transparent), inset 0 1px 0 rgba(255,255,255,0.2), inset 0 -1px 0 rgba(0,0,0,0.1)',
    hoverBoxShadow: '0 6px 20px color-mix(in srgb, var(--primary) 45%, transparent), inset 0 1px 0 rgba(255,255,255,0.25), inset 0 -1px 0 rgba(0,0,0,0.15)',
  },
  primary: {
    background: 'linear-gradient(135deg, var(--primary) 0%, color-mix(in srgb, var(--primary) 85%, black) 50%, color-mix(in srgb, var(--primary) 70%, black) 100%)',
    boxShadow: '0 4px 12px color-mix(in srgb, var(--primary) 35%, transparent), inset 0 1px 0 rgba(255,255,255,0.2), inset 0 -1px 0 rgba(0,0,0,0.1)',
    hoverBoxShadow: '0 6px 20px color-mix(in srgb, var(--primary) 45%, transparent), inset 0 1px 0 rgba(255,255,255,0.25), inset 0 -1px 0 rgba(0,0,0,0.15)',
  },
  destructive: {
    background: 'linear-gradient(135deg, var(--destructive) 0%, color-mix(in srgb, var(--destructive) 85%, black) 50%, color-mix(in srgb, var(--destructive) 70%, black) 100%)',
    boxShadow: '0 4px 12px color-mix(in srgb, var(--destructive) 35%, transparent), inset 0 1px 0 rgba(255,255,255,0.2), inset 0 -1px 0 rgba(0,0,0,0.1)',
    hoverBoxShadow: '0 6px 20px color-mix(in srgb, var(--destructive) 45%, transparent), inset 0 1px 0 rgba(255,255,255,0.25), inset 0 -1px 0 rgba(0,0,0,0.15)',
  },
  accent: {
    background: 'linear-gradient(135deg, var(--accent) 0%, color-mix(in srgb, var(--accent) 85%, black) 50%, color-mix(in srgb, var(--accent) 70%, black) 100%)',
    boxShadow: '0 4px 12px color-mix(in srgb, var(--accent) 35%, transparent), inset 0 1px 0 rgba(255,255,255,0.2), inset 0 -1px 0 rgba(0,0,0,0.1)',
    hoverBoxShadow: '0 6px 20px color-mix(in srgb, var(--accent) 45%, transparent), inset 0 1px 0 rgba(255,255,255,0.25), inset 0 -1px 0 rgba(0,0,0,0.15)',
  },
  secondary: {
    background: 'linear-gradient(135deg, var(--secondary) 0%, color-mix(in srgb, var(--secondary) 90%, black) 50%, color-mix(in srgb, var(--secondary) 80%, black) 100%)',
    boxShadow: '0 2px 8px rgba(0,0,0,0.15), inset 0 1px 0 rgba(255,255,255,0.1), inset 0 -1px 0 rgba(0,0,0,0.05)',
    hoverBoxShadow: '0 4px 12px rgba(0,0,0,0.2), inset 0 1px 0 rgba(255,255,255,0.15), inset 0 -1px 0 rgba(0,0,0,0.08)',
  },
  outline: {
    background: 'transparent',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1), inset 0 1px 0 rgba(255,255,255,0.05)',
    hoverBoxShadow: '0 2px 6px rgba(0,0,0,0.15), inset 0 1px 0 rgba(255,255,255,0.08)',
  },
  ghost: {
    background: 'transparent',
    boxShadow: 'none',
    hoverBoxShadow: 'none',
  },
  link: {
    background: 'transparent',
    boxShadow: 'none',
    hoverBoxShadow: 'none',
  },
}

const buttonVariants = cva(
  [
    "inline-flex items-center justify-center gap-2",
    "whitespace-nowrap text-sm font-medium",
    "rounded-2xl",
    "transition-all duration-200",
    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
    "disabled:pointer-events-none disabled:opacity-50",
    "[&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0",
    "active:scale-[0.97] hover:scale-[1.02]",
  ].join(" "),
  {
    variants: {
      variant: {
        default: "text-primary-foreground",
        primary: "text-primary-foreground",
        destructive: "text-destructive-foreground",
        accent: "text-accent-foreground",
        secondary: "text-secondary-foreground",
        outline: "border border-input bg-background hover:bg-accent hover:text-accent-foreground",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "text-primary underline-offset-4 hover:underline",
      },
      size: {
        sm: "h-8 px-4 text-xs rounded-xl",
        default: "h-9 px-5 py-2 rounded-2xl",
        md: "h-10 px-6 py-2.5 rounded-2xl",
        lg: "h-12 px-10 rounded-2xl",
        xl: "h-14 px-12 py-4 text-lg rounded-3xl",
        icon: "h-10 w-10 rounded-2xl",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

const Button = React.forwardRef(({
  className,
  variant = "default",
  size = "default",
  asChild = false,
  isLoading = false,
  leftIcon,
  rightIcon,
  children,
  style,
  ...props
}, ref) => {
  const Comp = asChild ? Slot : "button"
  const [isHovered, setIsHovered] = React.useState(false)

  const styleConfig = BUTTON_STYLES[variant] || BUTTON_STYLES.default
  const needsCustomStyle = !['ghost', 'link'].includes(variant)

  const combinedStyle = needsCustomStyle ? {
    background: styleConfig.background,
    boxShadow: isHovered ? styleConfig.hoverBoxShadow : styleConfig.boxShadow,
    ...style,
  } : style

  return (
    <Comp
      className={cn(buttonVariants({ variant, size, className }))}
      ref={ref}
      disabled={isLoading || props.disabled}
      style={combinedStyle}
      onMouseEnter={(e) => { setIsHovered(true); props.onMouseEnter?.(e) }}
      onMouseLeave={(e) => { setIsHovered(false); props.onMouseLeave?.(e) }}
      {...props}
    >
      {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : leftIcon}
      {children}
      {!isLoading && rightIcon}
    </Comp>
  )
})
Button.displayName = "Button"

export { Button, buttonVariants }
```

---

## 升级任务

理解上述设计语言和 Button 范例后，将同样的微拟物光影质感应用到以下组件：

- Card（凸起/内凹变体）
- Input（内凹效果）
- Badge（渐变背景）
- 其他你认为需要升级的交互组件

**联想升级原则**：
1. 凸起元素用外投影 + 顶部高光
2. 内凹元素用 inset 阴影
3. 所有颜色通过 CSS 变量 + color-mix 派生
4. 保持微交互一致性

---

## 最终验收

升级完成后，在**设计系统展示页面**中新增一个区块，陈列展示所有升级后的组件变体。

---

## GEB 分形文档检查

完成设计提升后，**必须执行**以下文档同步：

```
L3 检查 → 修改的组件文件头部注释是否更新？
L2 检查 → components/ui/CLAUDE.md 是否记录新增的 variant？
L1 检查 → 项目根目录 CLAUDE.md 是否需要更新设计系统说明？
```

确保代码与文档同构，完成后等待下一步指令。
