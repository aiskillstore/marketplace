# Counter-example Candidates

提取方式：子代理因额度限制中断，以下由主流程独立回看原视频和转写稿完成，可信度低于前三组独立提取。

```yaml
- id: ce01
  title: 只有效果词，没有运动机制
  source_locator: 13:14-13:36
  failure_mode: 只写“电影感、紧张、高级”，模型不知道相机具体如何变化。
  mechanism: 视频给出的三层顺序把镜头指令置于最前，说明效果形容不能替代运动动作。
  warning_signs: [没有方向, 没有速度, 没有起点或落点]

- id: ce02
  title: 混淆摇镜、机位移动与变焦
  source_locator: 04:13-04:20; 06:17-06:22; 08:03-08:11
  failure_mode: 把 tilt、pedestal/crane 和 zoom 混写，导致画面同时旋转、平移和放大。
  mechanism: 三种运动改变的变量不同；不声明固定项时，生成系统会自行补全动作。
  warning_signs: [既说机位固定又说相机上升, 把推进和变焦当同义词]

- id: ce03
  title: 主体动作或运动强度过大
  source_locator: 00:06-00:14; 05:41-05:50; 10:31-10:43
  failure_mode: 人脸、肢体或主体边缘在高速运动中模糊、变形或失去可读性。
  mechanism: 相机运动、主体运动和生成形变同时争夺有限的时间连续性。
  warning_signs: [快速运镜同时要求复杂表演, 环绕速度过快, 手持抖动无幅度限制]

- id: ce04
  title: 横移缺少视差证据
  source_locator: 04:44-05:00; 12:04-12:11
  failure_mode: 相机看似没有移动，人物像贴在背景平面上。
  mechanism: 没有近前景时，横向位移缺乏不同深度的相对速度线索。
  warning_signs: [画面只有主体和远背景, 所有图层同速平移]

- id: ce05
  title: 背景与光线在运动中跳变
  source_locator: 00:21-00:30; 05:00-05:14; 08:18-08:30
  failure_mode: 拉远、横移或变焦过程中场景被重绘成另一地点，光向突变。
  mechanism: 提示词没有声明环境连续，或参考图未提供扩展空间。
  warning_signs: [起点周围没有可延展背景, 终点景别远超参考图信息]

- id: ce06
  title: 参考图不支持所选运动
  source_locator: 14:30-14:58
  failure_mode: 门洞太小却要求穿越、无前景却要求强视差、主体贴边却要求对称推进。
  mechanism: 提示词要求的空间信息在起始图像中不存在。
  warning_signs: [运动路径被画面边缘截断, 缺少遮挡物或入口, 主体位置与目标落点冲突]

- id: ce07
  title: 复杂路径只给首尾状态
  source_locator: 15:00-16:06
  failure_mode: 尺度穿越跳过城市、物体从错误方向出现，或中间空间逻辑断裂。
  mechanism: 起点和终点跨度过大，模型必须自行发明中间世界。
  warning_signs: [跨多个数量级, 穿越多个空间, 两次以上转场仍只有两张参考图]

- id: ce08
  title: 参考图模式仍重复堆叠外观词
  source_locator: 14:06-14:20
  failure_mode: 运动指令被冗长风格、服装和场景复述淹没，甚至与参考图冲突。
  mechanism: 视频明确让参考图承担一致性、文字只说明镜头怎样动。
  warning_signs: [提示词大部分是在复述可见内容, 同一属性出现不同描述]

- id: ce09
  title: 把画质好误判为运动逻辑正确
  source_locator: 15:30-16:06
  failure_mode: 画面细节更好，但城市从错误位置出现或过渡缺失。
  mechanism: 视觉质量和空间因果是两个独立维度；前者不能掩盖后者失败。
  warning_signs: [只评价清晰度, 不检查路径, 不检查终点之前发生了什么]
```
