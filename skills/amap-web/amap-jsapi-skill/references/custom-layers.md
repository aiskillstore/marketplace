# 自定义图层 (Custom Layers)

当官方图层无法满足需求时，可以使用自定义图层叠加自己的数据。

## 1. 图片图层 (ImageLayer)

将一张图片映射到地图的指定区域（矩形范围）。

```javascript
const bounds = new AMap.Bounds(
    [116.327911, 39.939229], // 西南角
    [116.342659, 39.946275]  // 东北角
);

const imageLayer = new AMap.ImageLayer({
    url: 'https://amap.com/examples/img/dongwuyuan.jpg',
    bounds: bounds,
    zooms: [12, 20],
    zIndex: 2,
    opacity: 0.8
});

map.add(imageLayer);
```

## 2. 视频图层 (VideoLayer)

将视频流叠加到地图上，支持 HTML5 Video 元素。

```javascript
const videoLayer = new AMap.VideoLayer({
    url: 'https://xxx.mp4', // 视频地址
    bounds: bounds,
    zIndex: 10,
    zooms: [14, 20],
    opacity: 1,
    loop: true, // 是否循环播放
});
map.add(videoLayer);
```

## 3. Canvas 图层 (CanvasLayer)

最灵活的图层，允许通过 Canvas API 自定义绘制内容。

```javascript
const canvas = document.createElement('canvas');
canvas.width = map.getSize().width;
canvas.height = map.getSize().height;

const canvasLayer = new AMap.CanvasLayer({
    canvas: canvas,
    bounds: map.getBounds(),
    zooms: [3, 18],
});

map.add(canvasLayer);

// 自定义绘制逻辑
function draw() {
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    // ... 绘制逻辑 ...
    // 可以使用 AMap.CustomLayer 的 render 方法结合 map.lngLatToContainer 转换坐标
}

draw();
```

## 4. 自定义切片图层 (TileLayer)

加载第三方的 WMTS 或 XYZ 切片服务。

```javascript
const xyzLayer = new AMap.TileLayer({
    // [x], [y], [z] 会自动替换为行列号和缩放级别
    getTileUrl: 'https://tile.openstreetmap.org/[z]/[x]/[y].png',
    zIndex: 100
});
map.add(xyzLayer);
```

## 5. GL 图层 (GLCustomLayer)

结合 Three.js 实现自定义 3D 场景渲染。

```javascript
var map = new AMap.Map('container', {
  center: [116.54, 39.79],
  zooms: [2, 20],
  zoom: 14,
  viewMode: '3D',
  pitch: 50,
});

var camera;
var renderer;
var scene;
var meshes = [];
// 数据转换工具
var customCoords = map.customCoords;
// 数据使用转换工具进行转换，这个操作必须要提前执行（在获取镜头参数 函数之前执行），否则将会获得一个错误信息。
var data = customCoords.lngLatsToCoords([
  [116.52, 39.79],
  [116.54, 39.79],
  [116.56, 39.79],
]);

// 创建 GL 图层
var gllayer = new AMap.GLCustomLayer({
  // 图层的层级
  zIndex: 10,
  // 初始化的操作，创建图层过程中执行一次。
  init: (gl) => {
    // 这里我们的地图模式是 3D，所以创建一个透视相机，相机的参数初始化可以随意设置，因为在 render 函数中，每一帧都需要同步相机参数，因此这里变得不那么重要。
    // 如果你需要 2D 地图（viewMode: '2D'），那么你需要创建一个正交相机
    camera = new THREE.PerspectiveCamera(
      60,
      window.innerWidth / window.innerHeight,
      100,
      1 << 30
    );

    renderer = new THREE.WebGLRenderer({
      context: gl, // 地图的 gl 上下文
      // alpha: true,
      // antialias: true,
      // canvas: gl.canvas,
    });

    // 自动清空画布这里必须设置为 false，否则地图底图将无法显示
    renderer.autoClear = false;
    scene = new THREE.Scene();

    // 环境光照和平行光
    var aLight = new THREE.AmbientLight(0xffffff, 0.3);
    var dLight = new THREE.DirectionalLight(0xffffff, 1);
    dLight.position.set(1000, -100, 900);
    scene.add(dLight);
    scene.add(aLight);

    var texture = new THREE.TextureLoader().load(
      'https://a.amap.com/jsapi_demos/static/demo-center-v2/three.jpeg'
    );
    texture.minFilter = THREE.LinearFilter;
    //  这里可以使用 three 的各种材质
    var mat = new THREE.MeshPhongMaterial({
      color: 0xfff0f0,
      depthTest: true,
      transparent: true,
      map: texture,
    });
    var geo = new THREE.BoxBufferGeometry(1000, 1000, 1000);
    for (let i = 0; i < data.length; i++) {
      const d = data[i];
      var mesh = new THREE.Mesh(geo, mat);
      mesh.position.set(d[0], d[1], 500);
      meshes.push({
        mesh,
        count: i,
      });
      scene.add(mesh);
    }
  },
  render: () => {
    // 这里必须执行！！重新设置 three 的 gl 上下文状态。
    renderer.resetState();
    // 重新设置图层的渲染中心点，将模型等物体的渲染中心点重置
    // 否则和 LOCA 可视化等多个图层能力使用的时候会出现物体位置偏移的问题
    customCoords.setCenter([116.52, 39.79]);
    var { near, far, fov, up, lookAt, position } =
      customCoords.getCameraParams();

    // 2D 地图下使用的正交相机
    // var { near, far, top, bottom, left, right, position, rotation } = customCoords.getCameraParams();

    // 这里的顺序不能颠倒，否则可能会出现绘制卡顿的效果。
    camera.near = near;
    camera.far = far;
    camera.fov = fov;
    camera.position.set(...position);
    camera.up.set(...up);
    camera.lookAt(...lookAt);
    camera.updateProjectionMatrix();

    // 2D 地图使用的正交相机参数赋值
    // camera.top = top;
    // camera.bottom = bottom;
    // camera.left = left;
    // camera.right = right;
    // camera.position.set(...position);
    // camera.updateProjectionMatrix();

    renderer.render(scene, camera);

    // 这里必须执行！！重新设置 three 的 gl 上下文状态。
    renderer.resetState();
  },
});
map.add(gllayer);

// 动画
function animate() {
  for (let i = 0; i < meshes.length; i++) {
    let { mesh, count } = meshes[i];
    count += 1;
    mesh.rotateZ((count / 180) * Math.PI);
  }
  map.render();
  requestAnimationFrame(animate);
}
animate();

function onWindowResize() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}
window.addEventListener('resize', onWindowResize);
```
