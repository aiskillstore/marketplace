---
name: omniailab-blocking-stage-schema
description: 站位数据模型 —— OmniAiLab 导演台 SCENE_JSON 的字段与取值字典。
version: 2.3.0
author: OmniAiLab
developer: Mochiball
agent_created: true
开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
---

# 站位数据模型（OmniAiLab 导演台 SCENE_JSON）

本文件是 `BLOCKING GUIDE.md` 的数据字典，定义**场景数据（`SCENE_JSON`）**的字段与取值。使用无注释的有效 JSON，**坐标与尺寸单位一律为米**。

## 字段映射说明（重要）

`SCENE_JSON` 是 **OmniAiLab 导演台**的结构化输入。字段名以 OmniAiLab 导演台实际上架字段为准；若实际上架字段与本文件的命名不一致，按**语义等价**映射（位置→坐标、朝向→角度、姿势→预设、尺寸→长宽高…），**不得删改语义，也不得把导演台字段写进图像／视频提示词正文**。

`aspectRatio`、`fov`、时长等属于**导演台／平台参数**，只允许出现在本文件或平台 UI 中。

## 完整示例

```json
{
  "version": "1.0",
  "scene": {"name": "仓库对峙", "environment": "废弃仓库", "time": "夜晚", "scale": "meters"},
  "characters": [
    {
      "id": "char_guard",
      "name": "守卫",
      "color": "#d84a3a",
      "position": [0, 0, 0],
      "facing": 0,
      "posePreset": "fight",
      "poseControls": {},
      "bodyType": "standard",
      "weapon": "ak15k-rifle",
      "scale": 1,
      "labels": ["主体"],
      "movementPath": [[0, 0, 0], [1.2, 0, -1.5]]
    }
  ],
  "props": [],
  "camera": {
    "shot": "平视中景",
    "lensMm": 48,
    "fov": 48,
    "position": [5.8, 1.6, 6.6],
    "target": [0, 1.1, 0],
    "movement": "缓慢推近",
    "aspectRatio": "16:9",
    "bodyView": "hands",
    "handView": "both"
  },
  "lighting": {"key": "左后方冷色主光", "fill": "右前方弱补光", "mood": "紧张"},
  "continuity": ["人物与武器身份不变"],
  "characterPathDuration": 4,
  "directorAnnotations": []
}
```

## 顶层键

| 键 | 必需 | 说明 |
|---|---|---|
| `version` | 是 | 数据版本号 |
| `scene` | 是 | 场景元信息（名称、环境、时间、单位） |
| `characters` | 是 | 在场角色数组 |
| `props` | 是 | 道具与建筑构件数组，可为空 |
| `camera` | 是 | 机位与光学参数 |
| `lighting` | 是 | 光线设计（主光／补光／氛围） |
| `continuity` | 是 | 本镜需继承的连续性条目 |
| `characterPathDuration` | 否 | 人物位移总时长 |
| `directorAnnotations` | 否 | 导演标记（俯视图上的笔迹／箭头／文字） |

## 人物字段（`characters[]`）

- **必需**：`id`、`name`、`color`、`position`、`facing`。
- `position`：`[x, y, z]`，地面 `y=0`，`+Y` 向上。
- `facing`：朝向角，`0` 朝 `-Z`，`1.5708` 朝 `-X`，`-1.5708` 朝 `+X`，`3.1416` 朝 `+Z`。
- `posePreset`：使用 `BLOCKING GUIDE.md` 列出的 21 项姿势预设。
- `poseControls`：可选关节对象，支持身体、躯干、头、肩、肘、手、髋、膝、脚的角度控制。
- `bodyType`：`standard`、`slim`、`strong`、`child`、`giant`。
- `weapon`：可选，只能使用 `blocking-weapon-library.md` 中的稳定 ID。
- `scale`：整体缩放，默认 `1`。
- `labels`：画布标签，如"主体""队友""观众"。
- `movementPath`：可选位置点数组，**至少两点**才能预演位移。
- `locked`：可选布尔值；**锁定后禁止移动、旋转、删除与属性修改**。跨镜继承的角色必须置 `true`。

## 道具字段（`props[]`）

- `kind`：`table`、`chair`、`bench`、`cup`、`tree`、`lamp`、`device`、`box`。
- `size`：`[长度X, 高度Y, 宽度Z]`。
- `box.semanticType`：`block`、`wall`、`door`、`window`、`step`、`bed`、`sofa`、`vehicle`。

## 镜头字段（`camera`）

- `shot`：景别与角度的文字描述（语境用，不替代 `position`／`target`）。
- `lensMm` / `fov`：焦距与视场角。
- `position` / `target`：机位坐标与注视点坐标，**与人物共用同一坐标系**。
- `movement`：运镜方式的文字描述。
- `aspectRatio`：`auto`、`1:1`、`2:1`、`3:4`、`4:3`、`16:9`、`21:9`、`9:16`。**仅导演台字段，不进提示词正文**；实际交付比例以 P1 锁定与 P5 参数表为准。
- `bodyView`：仅 `hands` 或 `none`（第一视角）。
- `handView`：`left`、`right`、`both`。
- `keyframes`：可选机位点数组，每点包含 `position`、`target`、`fov`、`time`。
- `motionRegion`：可选，包含 `center`、`radius`、`startDistance`、`endDistance`、`cameraHeight`、`azimuth`、`preset`。

## 光线字段（`lighting`）

- `key`：主光方向与色性。
- `fill`：补光方向与强度。
- `mood`：氛围描述。

> 光线设计须服从 P1 的「全片风格锁定」；本字段只作空间化描述，不改变 P1 的光线口径。

## 连续性字段（`continuity`）

字符串数组，逐条列出本镜必须从上一镜继承的项目。至少覆盖 `BLOCKING GUIDE.md` 第 9.3 节「换镜必须继承的十二项」中本镜涉及的部分。

## 导演标记（`directorAnnotations`）

`tool` 可为 `pen`、`arrow`、`text`；点坐标为画布归一化的 `0–1`。用于在导演台俯视图上标注走位、视线与重点区域。

---

> © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。
