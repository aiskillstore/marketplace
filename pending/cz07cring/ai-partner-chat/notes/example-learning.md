# React Hooks 学习笔记

今天深入学习了 React Hooks，终于理解了 useState 和 useEffect 的底层原理！

## useState 原理

```javascript
function useState(initialValue) {
  const [state, setState] = React.useState(initialValue);
  return [state, setState];
}
```

## useEffect 使用场景

- 数据获取
- 订阅管理
- DOM 操作

太棒了！现在可以用 Hooks 重构之前的类组件了。
