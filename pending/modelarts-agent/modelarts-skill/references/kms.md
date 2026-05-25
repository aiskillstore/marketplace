# KMS 模块参考

KMS（Key Management Service）密钥对查询功能。

## 功能索引

| 功能描述 | 对应函数 | 位置 |
|---------|---------|------|
| 查询SSH密钥对列表 | `list_keypairs` | `scripts/kms_module/keypairs.py` |

---

## 说明

- 用于查询华为云KMS中的SSH密钥对
- 底层通过华为云KMS原生API调用
- 使用华为云SDK Signer进行AK/SK签名认证
- 支持分页查询（`limit`、`marker`参数）

## API 端点

| 服务 | 端点 |
|------|------|
| KMS | `https://kms.{region}.myhuaweicloud.com` |

## 权限要求

| 操作 | 权限 |
|------|------|
| 查询密钥对列表 | `kps:SSHKeyPair:list` 或 `kps:domainKeypairs:list` |

---

## 使用示例

```python
from kms_module import list_keypairs

result = list_keypairs()
if result['success']:
    for kp in result['data']['keypairs']:
        print(f"名称: {kp['name']}")
        print(f"类型: {kp['type']}")      # ssh 或 x509
        print(f"范围: {kp['scope']}")      # user 或 domain
        print(f"指纹: {kp['fingerprint']}")
        print(f"冻结状态: {kp['frozen_state']}")  # 0=正常
        print(f"托管保护: {kp['is_key_protection']}")
        print("---")
```

---

## 与其他模块的对比

| 对比项 | SWR 模块 | VPC 模块 | KMS 模块 |
|--------|---------|---------|---------|
| API 端点 | `swr-api.{region}.myhuaweicloud.com` | `vpc.{region}.myhuaweicloud.com` | `kms.{region}.myhuaweicloud.com` |
| API 版本 | v2 | v1 | v3 |
| 认证方式 | SDK Signer + BasicCredentials | SDK Signer + BasicCredentials | SDK Signer + BasicCredentials |
| 调用模式 | `access.sdk().execute(_func)` | `access.sdk().execute(_func)` | `access.sdk().execute(_func)` |
