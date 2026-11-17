# Three.js 适配器

## 用途
- 3D 曲面、散点、地球、VR/AR、数据艺术。

## 映射

### 场景初始化
```javascript
const scene = new THREE.Scene();
scene.background = new THREE.Color('#FFFFFF');

const camera = new THREE.PerspectiveCamera(
  45,                       // FOV
  container.clientWidth / container.clientHeight,
  0.1,
  1000
);
camera.position.set(5, 3, 8);  // 默认等距视角
camera.lookAt(0, 0, 0);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;

// 光照
const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);  // 环境光
const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
directionalLight.position.set(5, 10, 5);  // 左上角 45°
```

### 色板：使用 Viridis 映射
```javascript
// 将 Viridis 色板转为 Three.js Color 数组
const viridisColors = [
  '#440154', '#482878', '#3E4A89', '#31688E', '#26828E',
  '#1F9E89', '#35B779', '#6DCD59', '#B4DE2C', '#FDE725'
].map(c => new THREE.Color(c));
```

### 3D 曲面材质
```javascript
const material = new THREE.MeshPhongMaterial({
  vertexColors: true,       // 逐顶点颜色
  side: THREE.DoubleSide,
  shininess: 30,            // 降低高光
  transparent: true,
  opacity: 0.95
});
```

### 3D 散点
```javascript
const geometry = new THREE.SphereGeometry(0.05, 8, 8);
const material = new THREE.MeshPhongMaterial({
  color: new THREE.Color('#4269d0'),
  opacity: 0.7,
  transparent: true
});
```

### 坐标轴
```javascript
// 使用 CSS2DRenderer 渲染文字标签
const labelDiv = document.createElement('div');
labelDiv.textContent = 'X Axis';
labelDiv.style.fontSize = '10px';  // h4
labelDiv.style.color = '#666666';
labelDiv.style.fontFamily = "'Helvetica Neue', Arial, sans-serif";
```

## 默认

- `WebGLRenderer` 抗锯齿；像素比 ≤2。
- `OrbitControls` 阻尼 0.1。
- 透视相机 FOV 45°，裁面 0.1–1000。
- PNG 截图 2x；交互提供键盘与静态替代。
