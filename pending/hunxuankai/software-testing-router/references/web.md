# 网页 DOM 自动化

优先沿用项目已有的 Playwright、Cypress、WebDriver 等可工作工具。新流程可使用 Playwright 的角色/标签定位、自动等待和断言，将完整流程在同一进程内执行。当前包实际校验的是 **Python Playwright + Chromium**，不是每种浏览器或框架。

## 首次探测

确认 URL、测试服务、可用浏览器与目标页面。先读取 DOM/可访问属性；仅获取需要的子树。用户会话需要现有浏览器状态时使用当前环境允许的连接方式，独立测试则用隔离 context，避免混用用户 profile。

常用定位顺序：可访问角色/标签 + 实际名称，稳定 test ID，再按实际 DOM 建 CSS。重名控件限定到 dialog、form 或 section；iframe 使用 frame locator。不要用 `.first()` 隐藏歧义。

## 真实交互与等待

```python
dialog = page.get_by_role("dialog", name="Export sample", exact=True)
expect(dialog).to_be_visible()
dialog.get_by_label("Item name", exact=True).fill("中文 样例")
with page.expect_response(lambda r: r.url == base + "/api/export") as pending:
    dialog.get_by_role("button", name="Export", exact=True).click()
assert pending.value.status == 200
assert pending.value.json()["code"] == 0  # 本例的业务协议
expect(dialog.get_by_role("status")).to_have_text("Exported")
```

完整可运行版本位于维护仓库 `tests/test_web.py`，执行范围见本包 [验证摘要](validation.md)。本例还有一个同名按钮，定位靠弹窗作用域消除歧义；弹窗异步出现，测试依赖自动等待，不依赖固定睡眠。

网络监听应在触发动作前建立。优先等待目标控件状态、请求或完成标记；有轮询/长连接的网页不适合靠 `networkidle` 代表业务完成。读取属性可以用页面求值；验证按钮接线时不可用求值直接调用业务函数替代点击。

需要排查时保留 trace、必要截图、控制台错误与请求响应。它们可能含用户数据，发布前应按环境要求处理。默认不让模型每一步重新截图识别。

下列复现命令仅在维护仓库根目录、准备测试依赖后执行；安装副本不包含测试样例。

```powershell
.venv/Scripts/python.exe -m pytest tests/test_web.py -q
```

## Electron、CEF 与 WebView

只有确认存在可用调试端点/测试启动能力后，才选 DOM/CDP。可控 Electron 源码可评估它的专用测试入口；HTML 内容和原生文件对话框可能需要两种驱动。UIA 外壳节点少，不代表内部 DOM 已被测；普通 Chromium 测试也不能冒充 Electron、CEF 或 WebView2 兼容验证。

参考：[Playwright 自动等待](https://playwright.dev/python/docs/actionability)、[定位器](https://playwright.dev/python/docs/locators)、[断言](https://playwright.dev/python/docs/test-assertions)。
