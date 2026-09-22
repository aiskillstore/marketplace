# DeepSeek Harness example

[中文](deepseek-harness.zh.md)

Source: [DeepSeek Harness architecture documentation](https://github.com/deepseek-ai/deepseek-harness/blob/c291e7961a515f6d7af9304e7fd1d257929aef26/docs/architecture.md), MIT licensed, by DeepSeek AI. This independently authored overview is not an official diagram and does not cover every application or plugin. All module and relationship claims await source verification; evidence paths refer to that repository, not Birdview.

The timeline is a hypothetical change scenario; no feature implementation or tests took place. Render with simulation enabled:

```sh
node scripts/render.mjs examples/deepseek-harness.architecture.json /tmp/deepseek-harness.html examples/session-timeline.activity.jsonl --simulation
```

Choose a writable HTML output path on your platform. The generated view supports architecture, changes and comparison. JSON fixtures remain in the repository; the HTML is also attached to the release.
