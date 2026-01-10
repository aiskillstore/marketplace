# React Hooks 学习笔记

今天深入学习了 useState,终于理解了状态更新的原理!

## 基础用法

```javascript
const [count, setCount] = useState(0);

function handleClick() {
    setCount(count + 1);
}
```

## 核心原理

原来 useState 是通过闭包保存状态的,每次渲染都会调用组件函数,
但是 state 变量的值会被 React 记住。

这太好了! 我理解了为什么 Hooks 必须在顶层调用 - 因为 React
依赖调用顺序来关联每个 Hook 和它的状态。

## 注意事项

- 不要在循环、条件或嵌套函数中调用 Hooks
- state 更新是异步的
- 使用函数式更新避免闭包陷阱

```javascript
// ❌ 错误 - 可能有闭包问题
setCount(count + 1);

// ✅ 正确 - 函数式更新
setCount(prev => prev + 1);
```

## 实践经验

尝试了一个计数器组件,发现直接修改 state 不会触发重新渲染,
必须使用 setState 方法。这和类组件的行为是一致的。

真是太棒了,学会了这个重要的概念!
