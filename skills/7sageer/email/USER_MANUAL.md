# 邮箱账户配置说明

## 密码管理

密码存储在 macOS Keychain 中，使用以下命令设置：

### 设置 SUSTech 账户密码

```bash
# IMAP 密码
security add-generic-password \
  -a "qihr2022@mail.sustech.edu.cn" \
  -s "email-imap-sustech" \
  -w "your-password" \
  -U

# SMTP 密码（如果与 IMAP 相同，可以使用同一个）
security add-generic-password \
  -a "qihr2022@mail.sustech.edu.cn" \
  -s "email-smtp-sustech" \
  -w "your-password" \
  -U
```

### 读取密码（测试）

```bash
security find-generic-password \
  -a "qihr2022@mail.sustech.edu.cn" \
  -s "email-imap-sustech" \
  -w
```

### 删除密码（如需更新）

```bash
security delete-generic-password \
  -a "qihr2022@mail.sustech.edu.cn" \
  -s "email-imap-sustech"
```

## 腾讯企业邮箱说明

- IMAP 服务器：imap.exmail.qq.com:993 (SSL/TLS)
- SMTP 服务器：smtp.exmail.qq.com:465 (SSL/TLS)
- 需要在企业邮箱设置中开启 IMAP/SMTP 服务
- 建议使用应用专用密码而非主密码

## curl 兼容性

使用 curl 而非 rustls 是因为：
- curl 使用 OpenSSL/LibreSSL，对腾讯企业邮箱兼容性更好
- rustls 在某些 TLS 握手场景下可能失败
