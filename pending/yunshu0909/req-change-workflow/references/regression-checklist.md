# Regression Checklist (Chrome Extension / promptV2.0)

目标：把“改需求”变成固定回归路径，避免凭感觉点一遍。

## 0. 必要提醒（改了这些一定要重载）

- 如果改了 `prompt/manifest.json` 或 `prompt/service_worker.js`：到 `chrome://extensions` 重载扩展后再测。
- 日志查看：
  - Service Worker：扩展详情页 → “Service worker” → Inspect
  - 侧边栏：打开侧边栏后 → DevTools

## 1. 基础冒烟（每次必做）

- [ ] 扩展能正常加载，无报错（Console/Service Worker）
- [ ] 侧边栏能打开，关键 UI 不空白/不闪退
- [ ] Options 页能打开（如本次涉及）

## 2. OAuth / 飞书（仅当本次涉及 auth/feishu）

- [ ] `chrome-extension://<EXT_ID>/tests/auth_test.html` 覆盖：首次登录、同步续期、添加流程
- [ ] 检查重定向 URI / Scope 变化（如有），并在 Service Worker 日志确认

## 3. 导入导出（仅当本次涉及数据结构/导入导出）

- [ ] `chrome-extension://<EXT_ID>/tests/export_api_test.html`
- [ ] `chrome-extension://<EXT_ID>/tests/import-test.html`
- [ ] `chrome-extension://<EXT_ID>/tests/unified-system-test.html`

## 4. 关键边界（按本次变更选择）

- [ ] 并发：重复点击/重复触发是否会并发执行导致重复写入/重复请求
- [ ] 失败兜底：网络失败、鉴权失败、存储读写失败时是否有可执行的中文提示
- [ ] 兼容：旧数据是否还能读；是否需要迁移（如需要，明确迁移策略与回滚）

## 5. 记录（别省略）

- 变更点：……
- 测过的清单项：……
- 关键日志/截图：……
