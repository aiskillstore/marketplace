# 协议 v2 执行与示例

动作表见 [SKILL.md](../SKILL.md)。以下 JSON 只摘录 `next`，由契约样例同步；示例引用和令牌不可执行，实际只用刚返回的值。

## 参数执行

`command` 是 argv 数组。优先逐参数执行；只有 `ask/login` 中与字段同名的 `{name}` 可替换，用户答案保持一个参数。只有 shell 字符串接口时，使用宿主语言的 shell 转义逐项编码，不能直接用空格拼接或只套双引号；单引号、美元符号与换行也必须作为数据传递。不要修改其他参数或补确认参数。

## 登录后恢复

展示协议卡并收集手机号，再替换 `{phone}`；随后按 CLI 要验证码。登录成功只执行最新 `run` 一次，旧 `resume` 不再另执行。

<!-- contract:login-required#next -->
```json
{"action":"login","confirm":{"title":"登录呼波特","items":[{"label":"隐私协议","value":"https://legal.example/privacy"},{"label":"用户协议","value":"https://legal.example/terms"}],"notes":["继续登录即表示同意以上协议"]},"ask":{"fields":[{"name":"phone","label":"手机号"}]},"command":["whobot","login","--phone","{phone}","--accept-terms"],"resume":["whobot","agents","list","--mine"]}
```

<!-- contract:login-resume#next -->
```json
{"action":"run","command":["whobot","agents","list","--mine"]}
```

## 确认卡

按 `title`、每项 `label：value` 和 `notes` 展示，末尾加“回复确认开始，或告诉我要改什么”。卡片有几项就显示几项；不补费用、方式或完整号码。用户改参数后重新取得对应卡片并确认。

<!-- contract:phone-trial-account-preview#next -->
```json
{"action":"confirm","confirm":{"title":"电话试打","items":[{"label":"数字员工","value":"电话顾问"},{"label":"目标号码","value":"138****8000"},{"label":"费用","value":"免费"}],"expiresAt":"2026-01-01T00:00:00Z"},"command":["whobot","call","start","--via","phone","--confirm","cfm_placeholder"]}
```

`ask` 带选项时，一条消息列出全部字段：选项照 `label` 展示，替换时只用对应 `value`；有 `default` 的字段作推荐预填，用户没改就用它。

<!-- contract:agents-hire-ask#next -->
```json
{"action":"ask","ask":{"fields":[{"name":"pricingMode","label":"计费方式","options":[{"value":"effect","label":"按效果付费 ¥6/意向"},{"value":"seat","label":"按坐席付费 ¥750/坐席/月"}],"default":"effect"},{"name":"brandName","label":"品牌名","default":"小猫猫"},{"name":"agentPosition","label":"岗位名","default":"小猫 · 会员健康关怀","optional":true}]},"command":["whobot","agents","hire","op_hire_placeholder","--pricing","{pricingMode}","--brand","{brandName}","--position","{agentPosition}"]}
```

## 等待与交还

`wait` 继续返回的命令；只读等待被宿主中断可重跑。`handoff` 当场交还，附带命令仅在用户回来问进度时执行；“先别等了”也交还，不挂断。

<!-- contract:web-call-handoff#next -->
```json
{"action":"handoff","command":["whobot","call","show"],"say":"网页通话还没有完成，链接仍然有效；需要时可以再回来查看。"}
```

## 未知结果

`data.state=unknown` 时说“结果还不确定，我不会重复操作”。只运行系统给出的查询，不重拨、不重传、不重建；没有查询命令就交还。不从错误码猜重试策略。未知 action、无有效 JSON 或协议不符时说明异常并停止。

## 线索上传

上传直接提交，须按 leads.md 事前说明并取得明确同意，再执行返回的等待命令；受理不代表导入完成。这里没有二次确认卡。
