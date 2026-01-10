/**
 * [INPUT]: variant, className
 * [OUTPUT]: Badge 徽章组件（渐变背景）
 * [POS]: UI 基础层 - 状态标识原语
 * [PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
 */
import * as React from "react"
import { cva } from "class-variance-authority"
import { cn } from "@/lib/utils"

/* ========================================
   Badge 样式配置 - 渐变 + 光影
   ======================================== */

const BADGE_STYLES = {
  default: {
    background: 'linear-gradient(135deg, var(--color-primary) 0%, color-mix(in srgb, var(--color-primary) 80%, black) 100%)',
    boxShadow: '0 2px 6px color-mix(in srgb, var(--color-primary) 30%, transparent), inset 0 1px 0 rgba(255,255,255,0.15)',
  },
  secondary: {
    background: 'linear-gradient(135deg, var(--color-secondary) 0%, color-mix(in srgb, var(--color-secondary) 85%, black) 100%)',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1), inset 0 1px 0 rgba(255,255,255,0.05)',
  },
  destructive: {
    background: 'linear-gradient(135deg, var(--color-destructive) 0%, color-mix(in srgb, var(--color-destructive) 80%, black) 100%)',
    boxShadow: '0 2px 6px color-mix(in srgb, var(--color-destructive) 30%, transparent), inset 0 1px 0 rgba(255,255,255,0.15)',
  },
  outline: {
    background: 'transparent',
    boxShadow: 'none',
  },
}

const badgeVariants = cva(
  "inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold transition-colors",
  {
    variants: {
      variant: {
        default: "text-primary-foreground",
        secondary: "text-secondary-foreground",
        destructive: "text-destructive-foreground",
        outline: "border border-input text-foreground",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

function Badge({ className, variant = "default", ...props }) {
  const styleConfig = BADGE_STYLES[variant] || BADGE_STYLES.default

  return (
    <div
      className={cn(badgeVariants({ variant }), className)}
      style={{
        background: styleConfig.background,
        boxShadow: styleConfig.boxShadow,
      }}
      {...props}
    />
  )
}

export { Badge, badgeVariants }
