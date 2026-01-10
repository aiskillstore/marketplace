/**
 * [INPUT]: className, type, disabled
 * [OUTPUT]: Input 输入框组件（内凹效果）
 * [POS]: UI 基础层 - 表单原语
 * [PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
 */
import * as React from "react"
import { cn } from "@/lib/utils"

const Input = React.forwardRef(({ className, type, ...props }, ref) => {
  return (
    <input
      type={type}
      className={cn(
        "flex h-10 w-full rounded-xl bg-background px-4 py-2 text-sm",
        "border border-input",
        "transition-all duration-200",
        "file:border-0 file:bg-transparent file:text-sm file:font-medium",
        "placeholder:text-muted-foreground",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
        "disabled:cursor-not-allowed disabled:opacity-50",
        className
      )}
      style={{
        boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.15), inset 0 -1px 0 rgba(255,255,255,0.03)',
      }}
      ref={ref}
      {...props}
    />
  )
})
Input.displayName = "Input"

export { Input }
