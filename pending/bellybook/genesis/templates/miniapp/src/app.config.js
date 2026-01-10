/**
 * [INPUT]: 依赖 Taro 的 defineAppConfig 全局配置函数
 * [OUTPUT]: 对外提供全局应用配置对象
 * [POS]: src 的全局配置，页面路由注册，window 和 tabBar 设置
 * [PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
 */

export default defineAppConfig({
  pages: [
    'pages/index/index'
  ],
  window: {
    backgroundTextStyle: 'light',
    navigationBarBackgroundColor: '#fff',
    navigationBarTitleText: 'WeChat',
    navigationBarTextStyle: 'black'
  }
})
