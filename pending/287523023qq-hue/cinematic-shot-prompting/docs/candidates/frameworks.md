# Framework Candidates

提取方式：独立子代理，仅查看 `BOOK_OVERVIEW.md`、转写稿和原视频；未查看其他候选结论。

```yaml
- id: f01
  title: 叙事任务到运镜选择
  type: framework
  epistemic_status: 蒸馏解释
  source_locator: 00:06-00:31; 02:07-02:41; 11:26-12:31
  evidence_summary: 不同示例反复采用“先说用途，再给运动，最后指出前提和风险”的结构。
  summary: 先确定镜头要让观众看见、感到或理解什么，再选择能完成该任务的最少运动机制。

- id: f02
  title: 固定项与变化项消歧
  type: framework
  epistemic_status: 蒸馏解释
  source_locator: 04:13-04:25; 06:17-06:25; 08:03-08:16
  evidence_summary: 视频通过“机位固定只摇”“相机整体下降”“机位不动只改变景别”等表述区分相似运动。
  summary: 写提示词时显式说明相机位置、朝向、焦距、焦点、主体尺度中哪些变化、哪些保持不变。

- id: f03
  title: 三层提示词顺序
  type: framework
  epistemic_status: 来源陈述
  source_locator: 13:20-13:36
  evidence_summary: 视频画面和讲解明确给出“镜头指令放最前 + 画面主体具体描述 + 环境背景细节补充”。
  summary: 先让生成系统解析运动，再解析运动中的主体与环境信息。

- id: f04
  title: 参考图与提示词职责分离
  type: framework
  epistemic_status: 来源陈述
  source_locator: 14:06-14:20; 14:30-14:52
  evidence_summary: 有参考图时，外观和场景一致性交给图像，文字集中描述镜头怎样运动；图像构图必须支持该运动。
  summary: 避免在运动提示中重复视觉外观；先检查参考图能否提供运动所需的前景、空间和落点。

- id: f05
  title: 状态-路径-约束运动合同
  type: framework
  epistemic_status: 迁移推断
  source_locator: 05:16-05:39; 07:38-07:56; 10:45-11:03; 11:28-11:48
  evidence_summary: 多个镜头都可还原为起始状态、运动路径、方向速度、主体固定项、环境响应和终止状态。
  summary: 不停留在“慢推、环绕、跟拍”等名称，而把镜头展开为可观察、可判定是否完成的运动合同。

- id: f06
  title: 按风险分解关键路径
  type: framework
  epistemic_status: 来源陈述
  source_locator: 14:24-14:30; 14:53-15:30; 15:33-16:06
  evidence_summary: 穿越、转场和尺度变化被视为高风险镜头；先约束首尾，再在模型容易跳步的位置增加中间帧。
  summary: 模型需要凭空补足的空间跨度越大，越应该将连续路径拆成关键状态。

- id: f07
  title: 可见失败驱动的修改闭环
  type: framework
  epistemic_status: 来源陈述与蒸馏解释
  source_locator: 13:42-13:58; 15:33-16:06; 16:36-16:41
  evidence_summary: 视频明确要求试跑和修改，并展示逻辑错误通过增加中间图改善的过程。
  summary: 根据可见失败定位运动机制、主体稳定、背景连续、落点或路径缺失，只改对应槽位后重测。
```
