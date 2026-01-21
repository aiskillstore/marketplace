# 参考推文模板

将你喜欢的爆款推文放入对应分类目录中，x-create会优先参考这些风格。

## 目录结构

```
templates/
├── high-value/         # 高价值干货类
├── sharp-opinion/      # 犀利观点类
├── trending-comment/   # 热点评论类
├── story-insight/      # 故事洞察类
└── tech-analysis/      # 技术解析类
```

## 使用方法

1. 找到你喜欢的爆款推文
2. 复制推文内容到对应分类目录
3. 保存为 `.md` 或 `.txt` 文件
4. 运行 `/x-create` 时会自动学习这些风格

## 文件格式建议

```markdown
# 推文标题/主题（可选）

原文内容...

---
来源: @账号名
互动数据: xxx likes, xxx retweets（可选）
我喜欢的点: 简述为什么收藏这条（可选）
```

## 示例

`high-value/ai-tools-list.md`:
```markdown
# AI工具推荐清单

我用了3个月测试了50个AI工具，只有这5个值得付费：

1. Cursor - 代码助手天花板
2. Perplexity - 搜索引擎替代
3. Notion AI - 写作+整理
4. Midjourney - 图像生成
5. Claude Pro - 深度对话

每个都能帮你省下几十小时。

---
来源: @某大V
我喜欢的点: 数字开头，清单结构，有收藏价值
```

## 注意事项

- 每个目录放3-5条参考即可，不需要太多
- 选择你真正喜欢的风格，而非仅看数据
- 可以混合不同账号的风格
- 如果目录为空，会使用 `references/post-patterns.md` 中的默认模式
