# ECharts 适配器

> 仅在项目已引用 ECharts，或用户要求快速开箱时使用；Web 默认 D3.js。

## 用途
- 已有 ECharts、快速开发、<10 万点、需内置缩放/悬停/图例交互。

## 映射

### 颜色
```javascript
// 直接使用 categorical 色板
const colorPalette = ['#4269d0', '#3ca951', '#ff725c', '#a463f2', '#efb118',
                       '#6cc5b0', '#9696a0', '#f5a623', '#ca5bb8', '#ff8ab7'];

// ECharts option
option = {
  color: colorPalette,
  // ...
};
```

### 排版
```javascript
const typography = {
  title: {
    left: 'center',
    top: 12,
    textAlign: 'center',
    textStyle: {
      fontSize: 16,        // h1
      fontWeight: 600,     // h1 weight
      color: '#1A1A1A',   // text.primary
      fontFamily: "'Helvetica Neue', Helvetica, Arial, 'PingFang SC', 'Microsoft YaHei', sans-serif"
    },
    subtextStyle: {
      fontSize: 13,        // h2
      fontWeight: 400,
      color: '#555555'     // text.secondary
    }
  },
  legend: {
    top: 44,
    left: 'center',
    orient: 'horizontal',
    textStyle: {
      fontSize: 10,        // h5
      fontWeight: 400,
      color: '#555555'
    }
  },
  xAxis: {
    nameTextStyle: {
      fontSize: 11,        // h3
      color: '#333333'
    },
    axisLabel: {
      fontSize: 10,        // h4
      color: '#666666'
    }
  },
  yAxis: {
    nameTextStyle: { fontSize: 11, color: '#333333' },
    axisLabel: { fontSize: 10, color: '#666666' }
  }
};
```

### 间距
```javascript
const spacing = {
  grid: {
    top: 96,      // title + legend band + legend-to-plot gap
    right: 36,
    bottom: 56,
    left: 56,
    containLabel: true
  }
};
```

顶部图例独占区域；`grid.top` 预留标题与图例。距绘图区 ≥20px，出版 ≥24px。

### 线条样式
```javascript
// 折线图系列
series: [{
  type: 'line',
  lineStyle: { width: 2, cap: 'round', join: 'round' },
  symbol: 'circle',
  symbolSize: 4,           // line_data_point radius * 2
  itemStyle: { borderWidth: 0 }
}]

// 网格线
xAxis: {
  splitLine: {
    show: true,
    lineStyle: {
      color: '#E0E0E0',
      width: 0.5,
      type: 'dashed'       // dash [2,2] → dashed
    }
  }
}
```

## ECharts 初始化模板

```javascript
// 使用前必须设置默认字体和色板
const chart = echarts.init(container, null, {
  renderer: 'canvas'
});

const baseOption = {
  color: colorPalette,
  textStyle: {
    fontFamily: "'Helvetica Neue', Helvetica, Arial, 'PingFang SC', 'Microsoft YaHei', sans-serif"
  },
  backgroundColor: '#FFFFFF',
  animation: true,
  animationDuration: 800,
  animationEasing: 'cubicOut',
  tooltip: {
    backgroundColor: '#FFFFFF',
    borderColor: '#D0D0D0',
    textStyle: { fontSize: 11, color: '#1A1A1A' },
    extraCssText: 'box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-radius: 4px;'
  }
};
```

## 默认

- 动画：800ms `cubicOut`；低动态模式关闭。
- Tooltip：白底、阴影；键盘/点击也可获取。
- 图例：顶部水平；工具栏隐藏，保留 `saveAsImage`。
- 数据点 >50：启用 `dataZoom`。

## 不适用

- >10 万点且需流畅交互：WebGL 或降采样。
- 像素级定制：D3.js。3D 地球：Three.js。
