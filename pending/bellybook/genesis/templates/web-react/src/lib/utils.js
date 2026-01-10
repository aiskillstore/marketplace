/**
 * [INPUT]: clsx, tailwind-merge
 * [OUTPUT]: cn() 样式合并工具函数
 * [POS]: 工具层核心，被所有 UI 组件消费
 * [PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
 */
import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs) {
  return twMerge(clsx(inputs))
}
