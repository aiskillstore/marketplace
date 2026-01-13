
/**
 * [INPUT]: 依赖 @tarojs/taro 的 useLaunch，依赖 ./app.css 全局样式
 * [OUTPUT]: 对外提供 App 根组件
 * [POS]: src 的应用入口，全局生命周期管理，被 Taro 运行时调用
 * [PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
 */

import { useLaunch } from '@tarojs/taro'

import './app.css'

function App({ children }) {
  useLaunch(() => {
    console.log('App launched.')
  })

  // children 是将要会渲染的页面
  return children
}
  


export default App
