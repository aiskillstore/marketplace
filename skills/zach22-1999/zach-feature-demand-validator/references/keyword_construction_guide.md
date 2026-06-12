# 关键词构造指南

在执行 Step 0 时，需要根据用户输入的品类和功能描述，构造 3-5 个英文关键词变体。

## 通用构造模式

| 模式编号 | 格式 | 示例（品类=air fryer, 功能=steam） |
|---------|------|-----|
| P1 | `[品类] with [功能]` | air fryer with steam |
| P2 | `[功能] [品类]` | steam air fryer |
| P3 | `[品类] [功能] combo` 或 `[品类] [功能er] combo` | air fryer steamer combo |
| P4 | `[功能] [品类相邻品类]` | steam oven air fryer |
| P5 | `[品类] [功能形容词]` 或 `[功能ing] [品类]` | steaming air fryer |

**规则**：
- ⛔ 至少构造 **3 个**变体，推荐 **5 个**
- P1 和 P2 是必选，P3-P5 按品类灵活选择
- 与用户确认关键词列表后再执行查询

## 按品类的构造示例

### 厨电类（Air Fryer, Blender, Coffee Maker 等）

| 品类 | 功能 | 关键词变体 |
|------|------|-----------|
| air fryer | steam | air fryer with steam, steam air fryer, air fryer steamer combo, steam oven air fryer |
| blender | self-cleaning | self cleaning blender, blender with self clean, auto clean blender |
| coffee maker | grinder | coffee maker with grinder, grind and brew coffee maker, coffee grinder combo |

### 电子配件类（Charger, Cable, Power Bank 等）

| 品类 | 功能 | 关键词变体 |
|------|------|-----------|
| power bank | wireless charging | power bank wireless charging, wireless power bank, portable charger wireless |
| usb cable | led display | usb cable with display, led usb c cable, charging cable with watt display |

### 家居类（Furniture, Storage, Decor 等）

| 品类 | 功能 | 关键词变体 |
|------|------|-----------|
| desk lamp | wireless charging | desk lamp wireless charger, lamp with charging pad, wireless charging desk light |

## 补充查询策略

构造完初始关键词后，还需要通过以下方式发现用户的真实搜索表达：

1. **keyword_extends**：对搜索量最高的核心词查延伸词，从延伸词中筛选功能相关的
2. **Sorftime 推荐词**：如果 keyword_detail 返回"非热搜词"但推荐了相关词，检查推荐词是否与功能相关
3. **product_search 标题**：从搜索结果的产品标题中提取消费者常见的功能表述方式

## 功能关键词的英文翻译注意事项

| 中文功能 | 推荐英文 | 常见错误 |
|---------|---------|---------|
| 蒸汽功能 | steam, steamer, steaming | 不要用 vapor |
| 自清洁 | self-cleaning, auto clean | 不要用 self wash |
| 快充 | fast charging, quick charge | PD charging 也要查 |
| 静音 | quiet, silent, low noise | 不要只查 mute |
| 防水 | waterproof, water resistant | IP rating 也要查 |
| 可折叠 | foldable, collapsible, portable | 三个都要查 |
