# X-Skills 用户配置

首次使用时通过问答自动填写，后续自动读取。

## 初始化状态

```yaml
initialized: false
```

## 账号定位

```yaml
account:
  domains: []           # 领域：AI/科技, 创业/商业, 个人成长, 投资理财
  target_audience: ""   # 目标受众：中文用户, 英文用户, 双语用户
  persona_style: ""     # 人设风格：专业严肃, 轻松幽默, 犀利观点, 温暖亲和
  language: "zh-CN"     # 创作语言
```

## 打分权重（可自定义）

```yaml
scoring:
  trending: 4           # 热度/趋势权重（满分4）
  controversy: 2        # 争议性权重（满分2）
  value: 3              # 高价值权重（满分3）
  relevance: 1          # 账号相关性权重（满分1）
  threshold: 7          # 进入创作池的分数阈值
```

## 使用说明

1. **首次使用**：运行任意x-skills时，会自动进行问答收集信息
2. **修改配置**：直接编辑此文件中的yaml值
3. **重置配置**：将 `initialized` 改为 `false`，下次使用时重新问答

## 配置示例

已初始化的用户配置示例：

```yaml
initialized: true

account:
  domains:
    - AI/科技
    - 创业
    - 个人成长
  target_audience: "中文用户"
  persona_style: "专业严肃、犀利观点、偶尔小幽默"
  language: "zh-CN"

scoring:
  trending: 4
  controversy: 2
  value: 3
  relevance: 1
  threshold: 7
```
