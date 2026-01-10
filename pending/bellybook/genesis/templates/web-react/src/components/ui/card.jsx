/**
 * [INPUT]: className, variant (elevated/inset)
 * [OUTPUT]: Card 卡片组件（凸起/内凹变体）
 * [POS]: UI 基础层 - 容器原语
 * [PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
 */
import * as React from "react"
import { cn } from "@/lib/utils"

/* ========================================
   Card 样式配置 - 微拟物光影
   ======================================== */

const CARD_STYLES = {
  elevated: {
    boxShadow: '0 4px 16px rgba(0,0,0,0.25), inset 0 1px 0 rgba(255,255,255,0.08), inset 0 -1px 0 rgba(0,0,0,0.1)',
    hoverBoxShadow: '0 8px 24px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.1), inset 0 -1px 0 rgba(0,0,0,0.12)',
  },
  inset: {
    boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.2), inset 0 -1px 0 rgba(255,255,255,0.05)',
    hoverBoxShadow: 'inset 0 2px 4px rgba(0,0,0,0.2), inset 0 -1px 0 rgba(255,255,255,0.05)',
  },
}

const Card = React.forwardRef(({ className, variant = "elevated", ...props }, ref) => {
  const [isHovered, setIsHovered] = React.useState(false)
  const styleConfig = CARD_STYLES[variant] || CARD_STYLES.elevated

  return (
    <div
      ref={ref}
      className={cn(
        "rounded-2xl bg-card text-card-foreground transition-all duration-200",
        variant === "elevated" && "hover:scale-[1.01]",
        className
      )}
      style={{
        boxShadow: isHovered ? styleConfig.hoverBoxShadow : styleConfig.boxShadow,
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      {...props}
    />
  )
})
Card.displayName = "Card"

const CardHeader = React.forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex flex-col space-y-1.5 p-6", className)}
    {...props}
  />
))
CardHeader.displayName = "CardHeader"

const CardTitle = React.forwardRef(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn("text-2xl font-semibold leading-none tracking-tight", className)}
    {...props}
  />
))
CardTitle.displayName = "CardTitle"

const CardDescription = React.forwardRef(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn("text-sm text-muted-foreground", className)}
    {...props}
  />
))
CardDescription.displayName = "CardDescription"

const CardContent = React.forwardRef(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("p-6 pt-0", className)} {...props} />
))
CardContent.displayName = "CardContent"

const CardFooter = React.forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex items-center p-6 pt-0", className)}
    {...props}
  />
))
CardFooter.displayName = "CardFooter"

export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent }
