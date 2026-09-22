# DeepSeek Harness 示例

[English](deepseek-harness.md)

来源：[DeepSeek Harness 架构文档](https://github.com/deepseek-ai/deepseek-harness/blob/c291e7961a515f6d7af9304e7fd1d257929aef26/docs/architecture.md)，作者 DeepSeek AI，采用 MIT 许可证。本概览独立编写，不是官方架构图，也未覆盖所有应用或插件。模块和关系声明均待源码核验；证据路径指向该仓库，不是 Birdview。

时间线是假设的改动场景，没有实施功能或执行测试。渲染时开启模拟标记：

```sh
node scripts/render.mjs examples/deepseek-harness.architecture.json /tmp/deepseek-harness.html examples/session-timeline.activity.jsonl --simulation
```

请为所在平台选择可写的 HTML 输出路径。生成页面支持完整架构、更改视图和并排对照。仓库保留 JSON 样例，HTML 同时作为发布附件提供。
