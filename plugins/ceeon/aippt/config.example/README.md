# 配置文件模板

此目录包含配置文件的模板。

## 使用方法

1. 复制整个目录为 `config/`：
   ```bash
   cp -r config.example config
   ```

2. 编辑 `config/secrets.md`，填入你的真实 API 密钥

## 文件说明

| 文件 | 用途 |
|------|------|
| `secrets.md` | 存放 API 密钥，供图片生成等模块使用 |

## 注意

- `config/` 目录已被 `.gitignore` 忽略，不会被提交到 Git
- 请勿将真实密钥提交到代码仓库
