/**
 * [INPUT]: React, ReactDOM, App 组件, 全局样式
 * [OUTPUT]: 应用入口，挂载到 #root
 * [POS]: 应用启动入口，职责单一：渲染根组件
 * [PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
 */
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
