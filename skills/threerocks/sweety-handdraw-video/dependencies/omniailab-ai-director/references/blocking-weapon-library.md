---
name: omniailab-blocking-weapon-library
description: 站位武器库与动作映射 —— 武器稳定 ID 与适配动作／姿势对照表。
version: 2.3.0
author: OmniAiLab
developer: Mochiball
agent_created: true
开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
---

# 站位武器库与动作映射

配合 `BLOCKING GUIDE.md` 使用：站位数据里的 `weapon` 必须使用下表**稳定 ID**，使同一武器在全部镜头之间保持同一形制与握持方式，避免跨镜换了一把握法不同的同类兵器。

## 武器表

| weapon ID | 中文名 | 适合动作／剧情 | 推荐姿势 | 不适合 |
|---|---|---|---|---|
| `longsword` | 中世纪长剑 | 剑术对决、冲锋、守卫、挥砍 | `fight`、`run`、`stand` | 现代枪战、日常场景 |
| `knife` | 战术匕首 | 潜行、近身格斗、威胁、反握突袭 | `fight`、`crouch`、`run` | 远距离攻击 |
| `parang` | 战术砍刀 | 丛林、重劈、破障、近战追击 | `fight`、`run`、`stand` | 精细剑术、枪械瞄准 |
| `spear` | 战斗长矛 | 刺击、列阵、守门、长兵器对峙 | `fight`、`stand`、`run` | 狭窄室内、贴身缠斗 |
| `baseball-bat` | 棒球棍 | 街头冲突、防身、挥击、追赶 | `fight`、`run`、`stand` | 军事枪战、古典剑术 |
| `g21-pistol` | G21 手枪 | 单手瞄准、室内战术、警戒、近距枪战 | `fight`、`crouch`、`kneel-one` | 长距离精确射击 |
| `ak15k-rifle` | AK-15K 步枪 | 双手持枪、巡逻、突击、压制射击 | `fight`、`crouch`、`kneel-one`、`stand` | 单手挥舞、坐姿日常 |

## 选择优先级

1. 用户明确武器名称时，映射到对应 ID。
2. 剧情明确武器类别时，按时代、距离与动作选择。
3. "持枪"但未说明枪型：室内近距用 `g21-pistol`，军事突击或压制用 `ak15k-rifle`。
4. "持刀"但未说明类型：隐蔽近身用 `knife`，重劈或丛林用 `parang`，古典决斗用 `longsword`。
5. **没有武器语义时省略 `weapon`，不要自动给日常人物或未成年人配武器。**

## 动作约束

- **枪械**：右手握持，右肘指向握把方向；AK-15K 在提示词中明确左手托护木。
- **长矛**：保留前方至少 `1.2 m` 刺击空间，避免矛杆穿过同伴。
- **长剑、砍刀、棒球棍**：挥击侧至少保留 `0.8 m` 空间。
- **匕首**：角色与目标距离通常为 `0.6–1.0 m`。
- 若现有姿势无法自然握持，优先使用 `fight` 并通过肩、肘、手腕 `poseControls` 微调。

## 跨镜一致性要求

- 同一角色在同一场次内**不得更换 weapon ID**；换武器必须写出放下／拾起的时间与位置。
- 武器状态（收起／持握／挥出／脱手／掉落位置）属于 `BLOCKING GUIDE.md` 第 9.3 节「换镜必须继承的十二项」第 8 项，逐镜继承。
- 武器形制与接触一致性另见 `COMBAT GUIDE.md`（打斗镜头的兵器接触与受力闭环）；本表只负责**选型与握持口径**，不负责动作编排。

---

> © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。
