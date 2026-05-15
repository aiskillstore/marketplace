# 视图控制 (View Control)

高德地图 JSAPI v2.0 提供了强大的 3D 视图控制能力，包括缩放、旋转、俯仰和中心点移动。

## 核心属性

在地图初始化或运行时，可以通过以下属性控制视口：

- **zoom**: 缩放级别 (2 - 20)。
- **center**: 地图中心点 `[lng, lat]`。
- **rotation**: 旋转角度 (0 - 360)，顺时针。
- **pitch**: 俯仰角度 (0 - 83)，0 为垂直向下，83 为接近水平。

## 常用方法

### 1. 缩放 (Zoom)

```javascript
map.setZoom(15);           // 设置特定级别
map.zoomIn();              // 放大一级
map.zoomOut();             // 缩小一级
const zoom = map.getZoom(); // 获取当前级别
```

### 2. 移动与平移 (Move/Pan)

```javascript
// 瞬间移动到指定位置
map.setCenter([116.40, 39.90]);

// 平滑移动到指定位置 (带动画)
map.panTo([116.40, 39.90]);

// 同时设置缩放和中心点
map.setZoomAndCenter(14, [116.40, 39.90]);
```

### 3. 3D 控制 (Pitch/Rotation)

```javascript
map.setPitch(45);      // 设置俯仰角
map.setRotation(90);   // 设置旋转角 (正北为0，顺时针)
```

### 4. 限制显示范围 (Bounds)

限制用户只能在特定区域内浏览地图。

```javascript
const bounds = new AMap.Bounds(
    [116.0, 39.0], // 西南角
    [117.0, 40.0]  // 东北角
);
map.setLimitBounds(bounds);

// 清除限制
map.clearLimitBounds();
```

## 视图自适应

让地图自动调整层级和中心，以显示所有指定的覆盖物。

```javascript
// 自动适配视口
map.setFitView(
    [marker1, polygon1], // 覆盖物数组，为空则包含所有
    false,               // 是否立即过渡 (false 为动画)
    [60, 60, 60, 60]     // 上下左右的 padding
);
```
## 注意事项
- 容器高度：确保地图容器 div 在 CSS 中有明确的宽度和高度，否则地图无法显示。
- 坐标系：高德地图使用 GCJ-02 坐标系（火星坐标系）。
- 插件加载：可以在 AMapLoader.load 时一次性引入，也可以在使用时通过 AMap.plugin(['AMap.XX'], callback) 动态引入。
- 性能优化：对于 1000 个以上的点标记，强烈建议使用 AMap.LabelMarker 或 AMap.MassMarks 而非普通 AMap.Marker。
- references/map-init.md
- references/security.md

### 说明：
1. **安全配置模块**：在 v2.0 中，这是最常见的报错来源。我在 `0. 安全配置` 中特别强调了 `window._AMapSecurityConfig`。
2. **Loader 模式**：官方现在推荐使用异步 Loader 模式，示例代码直接给出了 `AMapLoader` 的写法。
3. **高性能组件**：针对 v2.0 增加了 `LabelMarker` 的引用，这是 WebGL 版本相比 v1.4 的核心优势。
4. **结构化引用**：保持了与你提供的百度地图 Skill 一致的 `references/*.md` 结构，方便 LLM 模拟读取详细文档。
