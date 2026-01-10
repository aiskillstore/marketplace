/**
 * [INPUT]: 依赖 Taro 的 definePageConfig 页面配置函数
 * [OUTPUT]: 对外提供首页页面配置对象
 * [POS]: pages/index 的页面配置，navigationBarTitleText 设置
 * [PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
 */

export default definePageConfig({
  navigationBarTitleText: '首页'
})
