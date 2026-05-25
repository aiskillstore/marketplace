# VPC 模块参考

VPC（虚拟私有云）查询功能，支持查询VPC列表、子网列表、安全组列表。

## 功能索引

| 功能描述 | 对应函数 | 位置 |
|---------|---------|------|
| 查询虚拟私有云列表 | `list_vpcs` | `scripts/vpc_module/vpcs.py` |
| 查询子网列表 | `list_subnets` | `scripts/vpc_module/subnets.py` |
| 查询安全组列表 | `list_security_groups` | `scripts/vpc_module/security_groups.py` |

---

## 说明

- 用于查询华为云VPC服务的虚拟私有云、子网、安全组资源
- 底层通过华为云VPC原生API调用，不走ModelArts API Gateway
- 使用华为云SDK Signer进行AK/SK签名认证
- 支持分页查询（`limit`、`marker`参数）
- 支持按VPC ID、企业项目ID等条件过滤

## API 端点

| 服务 | 端点 |
|------|------|
| VPC | `https://vpc.{region}.myhuaweicloud.com` |

## 权限要求

| 操作 | 权限 |
|------|------|
| 查询VPC列表 | `vpc:vpcs:list` |
| 查询子网列表 | `vpc:subnets:list` |
| 查询安全组列表 | `vpc:securityGroups:list` |

---

## 使用示例

### 查询VPC列表

```python
from vpc_module import list_vpcs

result = list_vpcs(limit=10)
if result['success']:
    for vpc in result['data']['vpcs']:
        print(f"{vpc['name']} ({vpc['id']}): {vpc['cidr']}, status={vpc['status']}")
```

### 查询子网列表

```python
from vpc_module import list_subnets

# 查询所有子网
result = list_subnets()
if result['success']:
    for subnet in result['data']['subnets']:
        print(f"{subnet['name']} ({subnet['vpc_id']}): {subnet['cidr']}, gateway={subnet['gateway_ip']}")

# 查询指定VPC下的子网
result = list_subnets(vpc_id='3ec3b33f-ac1c-4630-ad1c-7dba1ed79d85')
```

### 查询安全组列表

```python
from vpc_module import list_security_groups

result = list_security_groups()
if result['success']:
    for sg in result['data']['security_groups']:
        print(f"{sg['name']} ({sg['id']}): {len(sg['security_group_rules'])} rules")
        for rule in sg.get('security_group_rules', []):
            print(f"  {rule['direction']}: {rule['protocol']} {rule.get('port_range_min', 'all')}->{rule.get('port_range_max', 'all')}")

# 查询指定VPC下的安全组
result = list_security_groups(vpc_id='3ec3b33f-ac1c-4630-ad1c-7dba1ed79d85')
```

### 组合查询示例

```python
from vpc_module import list_vpcs, list_subnets, list_security_groups

# 查询所有VPC
vpcs_result = list_vpcs()
if vpcs_result['success']:
    for vpc in vpcs_result['data']['vpcs']:
        vpc_id = vpc['id']
        print(f"\n=== VPC: {vpc['name']} ({vpc_id}) ===")
        
        # 查询该VPC下的子网
        subnets_result = list_subnets(vpc_id=vpc_id)
        if subnets_result['success']:
            for subnet in subnets_result['data']['subnets']:
                print(f"  Subnet: {subnet['name']} - {subnet['cidr']}")
        
        # 查询该VPC下的安全组
        sgs_result = list_security_groups(vpc_id=vpc_id)
        if sgs_result['success']:
            for sg in sgs_result['data']['security_groups']:
                print(f"  SecurityGroup: {sg['name']} - {len(sg['security_group_rules'])} rules")
```

---

## 与 SWR 模块的对比

| 对比项 | SWR 模块 | VPC 模块 |
|--------|---------|---------|
| API 端点 | `swr-api.{region}.myhuaweicloud.com` | `vpc.{region}.myhuaweicloud.com` |
| API 路径 | `/v2/manage/repos` | `/v1/{project_id}/vpcs`, `/v1/{project_id}/subnets`, `/v1/{project_id}/security-groups` |
| 认证方式 | SDK Signer + BasicCredentials | SDK Signer + BasicCredentials |
| 调用模式 | `access.sdk().execute(_func)` | `access.sdk().execute(_func)` |
| 内部实现 | 直接HTTP请求，不走ModelArts网关 | 直接HTTP请求，不走ModelArts网关 |
