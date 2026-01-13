/**
 * [INPUT]: 依赖 babel-preset-taro 预设
 * [OUTPUT]: 对外提供 Babel 转译配置
 * [POS]: 根目录的 Babel 配置，React + Vite 转译设置
 * [PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
 */

// babel-preset-taro 更多选项和默认值：
// https://docs.taro.zone/docs/next/babel-config
module.exports = {
  presets: [
    ['taro', {
      framework: 'react',
      ts: false,
      compiler: 'vite',
    }]
  ]
}
