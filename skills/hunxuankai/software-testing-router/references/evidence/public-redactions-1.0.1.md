# 1.0.1 公开证据脱敏说明

以下三个文件为历史证据的公开脱敏派生副本。2026-11-07 仅将 `/journal_path_at_execution` 的本机绝对目录替换为 `<TEMP>/software-testing-router/`，保留原日志文件名；占位目录不表示原始执行实际使用了该路径。

| 派生文件 | 唯一替换字段 |
| --- | --- |
| [阻塞动作结果未知](optimization-20261105/test_blocking_invoke_timeout_p0.json) | `/journal_path_at_execution` |
| [硬超时后保留已完成步骤](optimization-20261105/test_completed_steps_survive_h0.json) | `/journal_path_at_execution` |
| [条件满足时的观测](optimization-20261105/test_wait_report_uses_the_sati0.json) | `/journal_path_at_execution` |

替换之外的字节、JSON 格式、步骤、状态、时间与数值保持一致。原件仍保留在本地维护历史及 `v1.0.0` 归档中，未修改旧标签或旧 ZIP；原件中的私人目录不公开分发。

[机器可读清单](public-redactions-1.0.1.json) 记录原始文件 SHA-256、派生文件 SHA-256 和替换字段。该清单用于追溯脱敏，不是一次新测试的结果。
