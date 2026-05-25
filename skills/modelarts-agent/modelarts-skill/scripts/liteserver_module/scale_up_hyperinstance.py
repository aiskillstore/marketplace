#!/usr/bin/env python3
"""
Lite Server 模块 - scale_up_hyperinstance 函数
功能：扩容超节点实例
"""

from ._bootstrap import authenticated_api_call, format_api_result, Dict, Any, List, Optional
from .common import validate_required_params, build_request_body, add_api_reference

@authenticated_api_call
def ma_liteserver_scale_up_hyperinstance(
    access,
    hyperinstance_id: str,
    flavor: str,
    image_id: str,
    root_volume: Optional[Dict[str, Any]] = None,
    data_volume: Optional[Dict[str, Any]] = None,
    key_pair_name: Optional[str] = None,
    userdata: Optional[str] = None
) -> Dict[str, Any]:
    """
    Scale up a Lite Server hyperinstance (live scale up).
    Args:
        hyperinstance_id: The hyperinstance ID (required)
        flavor: 服务器规格名称 (required) - e.g. "kat3ne-32-800t.192xlarge.8.matrix"
        image_id: 服务器镜像ID (required) - 长度为36个字符，符合UUID格式
        root_volume: 系统盘信息 (optional) - {"type": "GPSSD"|"ESSD"|..., "size": int}
        data_volume: 数据盘信息 (optional) - {"type": str, "size": int, "count": int}
        key_pair_name: 密钥对名称 (optional) - admin_pass和key_pair_name必须二选一
        userdata: 待注入实例自定义数据 (optional) - base64编码，最大长度32K
    Returns:
        Scale up result with hyperinstance details
    """
    valid, error = validate_required_params(
        {"hyperinstance_id": hyperinstance_id, "flavor": flavor, "image_id": image_id},
        ["hyperinstance_id", "flavor", "image_id"]
    )
    if not valid:
        return format_api_result(False, error=error)

    body = {
        "flavor": flavor,
        "image_id": image_id,
    }

    if root_volume:
        body["root_volume"] = root_volume
    if data_volume:
        body["data_volume"] = data_volume
    if key_pair_name:
        body["key_pair_name"] = key_pair_name
    if userdata:
        body["userdata"] = userdata
    result = simple_api_call(
        access,
        'POST',
        '/v1/{project_id}/dev-servers/hyperinstance/{id}/live-scale-up',
        body=body,
        id=hyperinstance_id
    )
    api_result = format_api_result(True, data=result)
    return add_api_reference(api_result, "ScaleUpHyperinstance")

from common_module.api_helper import simple_api_call
__all__ = ['ma_liteserver_scale_up_hyperinstance']
