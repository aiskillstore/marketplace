from modelarts.session import Session

def desensitize_data(data):
    """自动脱敏敏感信息：密钥、网络、凭证"""
    if not data:
        return data

    if isinstance(data, str):
        sensitive = ["access", "secret", "ak", "sk", "endpoint",
                     "subnet", "security_group", "vpc", "token", "password"]
        for kw in sensitive:
            if kw in data.lower():
                return "***脱敏***"
        return data

    if isinstance(data, dict):
        fields = ["access_key", "secret_key", "ak", "sk", "endpoint",
                  "subnet_id", "security_group_id", "vpc_id", "credential", "token"]
        out = {}
        for k, v in data.items():
            if k.lower() in [f.lower() for f in fields]:
                out[k] = "***脱敏***"
            else:
                out[k] = desensitize_data(v)
        return out

    if isinstance(data, list):
        return [desensitize_data(item) for item in data]

    return data

def get_session():
    """无缓存认证：仅使用运行时临时凭证"""
    try:
        return Session()
    except Exception:
        raise Exception("认证失败：无法获取临时安全凭证")