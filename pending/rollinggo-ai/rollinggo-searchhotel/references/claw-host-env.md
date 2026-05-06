# Claw 宿主环境参考

本技能需要在进程里能读到 `RollingGo_API_KEY`。如果宿主在不同 run 间丢失该变量，请使用宿主级注入而非 shell export。

**本技能的 key：** `rollinggo-searchhotel`

## OpenClaw 家族配置

按适合你的层级注入，推荐优先使用按 skill 注入。

### 按 skill 注入（推荐）

```json
{
  "skills": {
    "entries": {
      "rollinggo-searchhotel": {
        "env": { "RollingGo_API_KEY": "YOUR_KEY" }
      }
    }
  }
}
```

### 宿主级注入（多个 skill 共用同一个 key 时）

```json
{ "env": { "RollingGo_API_KEY": "YOUR_KEY" } }
```

或写入宿主的 `.env` 文件：`~/.openclaw/.env`（macOS/Linux）/ `%USERPROFILE%\.openclaw\.env`（Windows）。  
路径覆盖：`OPENCLAW_HOME`、`OPENCLAW_STATE_DIR` 或 `OPENCLAW_CONFIG_PATH`。

### Shell 导入兜底

```json
{ "env": { "shellEnv": { "enabled": true, "timeoutMs": 15000 } } }
```

仅当 key 存在于登录 shell 但子进程拿不到时使用。

## Sandbox 提醒

宿主 env 配置**不会**自动传入 sandbox 进程。需在 sandbox 内直接注入 `RollingGo_API_KEY`：`agents.defaults.sandbox.docker.env` 或等效配置。
