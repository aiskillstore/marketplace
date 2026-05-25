#!/usr/bin/env python3
"""
Lite Server 模块 - create_dev_server 函数（增强版）
功能：创建新的 Lite Server 实例，支持自动选择规格和镜像
"""

from ._bootstrap import authenticated_api_call, format_api_result, Dict, Any, List, Optional
from .common import (
    validate_dev_server_params, 
    build_request_body, 
    add_api_reference,
    get_available_flavor,
    get_image_by_flavor
)

def _validate_create_params(name: str, image_id: str, network: Dict[str, Any],
                           admin_pass: Optional[str], key_pair_name: Optional[str],
                           flavor: Optional[str], resource_flavor: Optional[str]) -> tuple[bool, Optional[str]]:
    """创建参数验证 - 分离验证逻辑"""
    # 使用公共验证函数
    valid, error = validate_dev_server_params(
        name=name, image_id=image_id, network=network,
        admin_pass=admin_pass, key_pair_name=key_pair_name,
        flavor=flavor, resource_flavor=resource_flavor
    )
    if not valid:
        return False, error
    return True, None

def _auto_resolve_flavor_and_image(
    access,
    flavor: Optional[str],
    resource_flavor: Optional[str],
    image_id: Optional[str],
    availability_zone: Optional[str],
    arch: Optional[str]
) -> tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
    """
    自动解析并补全 flavor、resource_flavor 和 image_id
    逻辑：
    1. 如果未指定 flavor/resource_flavor，自动查询可用规格
    2. 如果未指定 image_id，根据已选规格自动查询可用镜像
    Args:
        access: 认证后的 access 对象
        flavor: 规格名称（用户指定）
        resource_flavor: 资源规格名称（用户指定）
        image_id: 镜像ID（用户指定）
        availability_zone: 可用区（用于查询过滤）
        arch: 架构类型（用于查询过滤）
    Returns:
        (是否成功, 错误信息, 解析结果字典)
        解析结果包含: flavor, resource_flavor, image_id, auto_selected_flavor, auto_selected_image
    """
    result = {
        "flavor": flavor,
        "resource_flavor": resource_flavor,
        "image_id": image_id,
        "auto_selected_flavor": False,
        "auto_selected_image": False,
        "flavor_info": None,
        "image_info": None
    }
    if not flavor and not resource_flavor:
        # 用户未指定，需要自动选择
        success, error, flavor_info = get_available_flavor(
            access=access,
            availability_zone=availability_zone,
            arch=arch,
            prefer_resource_flavor=True
        )
        if not success or not flavor_info:
            return False, error or "自动选择规格失败", None
        result["flavor"] = flavor_info.get("flavor")
        result["resource_flavor"] = flavor_info.get("resource_flavor")
        result["auto_selected_flavor"] = True
        result["flavor_info"] = flavor_info.get("flavor_info")
        print(f"  [自动选择规格] {result['resource_flavor'] or result['flavor']} "
              f"(类型: {flavor_info.get('flavor_type')})")
    else:
        # 用户已指定，使用用户值
        if resource_flavor:
            result["resource_flavor"] = resource_flavor
        else:
            result["flavor"] = flavor
    if not image_id:
        # 用户未指定，需要自动选择
        success, error, image_info = get_image_by_flavor(
            access=access,
            flavor=result["flavor"],
            resource_flavor=result["resource_flavor"],
            arch=arch
        )
        if not success or not image_info:
            return False, error or "自动选择镜像失败", None
        result["image_id"] = image_info.get("image_id")
        result["auto_selected_image"] = True
        result["image_info"] = image_info.get("image_info")
        print(f"  [自动选择镜像] {result['image_id']} ({image_info.get('image_name', 'N/A')})")
    return True, None, result

@authenticated_api_call
def ma_liteserver_create(
    access,
    name: str,
    network: Dict[str, Any],
    image_id: Optional[str] = None,
    admin_pass: Optional[str] = None,
    arch: Optional[str] = None,
    availability_zone: Optional[str] = None,
    charging_info: Optional[Dict[str, Any]] = None,
    count: Optional[int] = None,
    enterprise_project_id: Optional[str] = None,
    flavor: Optional[str] = None,
    resource_flavor: Optional[str] = None,
    key_pair_name: Optional[str] = None,
    root_volume: Optional[Dict[str, Any]] = None,
    data_volume: Optional[Dict[str, Any]] = None,
    server_type: Optional[str] = None,
    user_data: Optional[str] = None,
    auto_select: bool = True
) -> Dict[str, Any]:
    """
    Create a new Lite Server instance with auto-selection support.
    Args:
        access: ModelArts access object (provided by decorator)
        name: 服务器名称 (required) - 长度为1至64个字符，只能包含字母、数字、中划线、下划线和点
        image_id: 服务器镜像ID (optional if auto_select=True) - 长度为36个字符，符合UUID格式
        network: 服务器的网络信息 (required) - ServerNetwork object
        admin_pass: 用于登录服务器的密码 (optional) - admin_pass和key_pair_name必须二选一
        arch: 服务器规格架构类型 (optional) - X86: CPU架构为X86，ARM: CPU架构为ARM
        availability_zone: 服务器所在的可用区 (optional)
        charging_info: 服务器的计费模式信息 (optional) - ChargingInfo object，结构如下:
                     {
                       "charge_mode": str,  -- 计费模式: PRE_PAID(包周期)/COMMON(按量)
                       "period_type": str,  -- 周期类型: month(月)/year(年)，PRE_PAID时必填
                       "period_num": int    -- 周期数量: 1-9，PRE_PAID时必填
                     }
        count: 单次购买的服务器数量 (optional) - 取值范围：1至10
        enterprise_project_id: 企业ID (optional)
        flavor: 服务器规格名称 (optional) - flavor和resource_flavor二选一
        resource_flavor: 服务器资源规格名称 (optional) - 优先使用此参数
        key_pair_name: 服务器登录密钥对名称 (optional) - admin_pass和key_pair_name必须二选一
        root_volume: 服务器系统盘信息 (optional) - ECS、HPS全部规格该参数为必填项
        data_volume: 服务器数据盘信息 (optional) - ServerDataVolume object
        server_type: 服务器类型 (optional) - BMS: 裸金属服务，ECS: 弹性云服务，HPS: 超节点服务
        user_data: 待注入实例自定义数据 (optional) - base64编码，最大长度32K
        auto_select: 是否自动选择规格和镜像 (default True) - 
                     当为 True 时，如果未指定 flavor/resource_flavor 或 image_id，将自动选择
    Returns:
        Created Lite Server details including server ID

    自动选择逻辑：
        1. 如果未指定 flavor/resource_flavor：
           - 优先查询 resource_flavor（ListDevServerResourceflavors）
           - 回退到查询 flavor（ListDevServerFlavors）
           - 自动过滤售罄状态，选择第一个可用规格
        2. 如果未指定 image_id：
           - 根据已选规格查询 ListDevServerImages
           - 返回支持的第一个可用镜像

    示例:
        >>> # 完全手动指定
        >>> result = ma_liteserver_create(
        ...     name="my-server",
        ...     flavor="snt8c.2xlarge",
        ...     image_id="img-xxx",
        ...     network={"id": "net-xxx"},
        ...     key_pair_name="my-key"
        ... )
        >>>
        >>> # 自动选择规格和镜像（仅指定名称和网络）
        >>> result = ma_liteserver_create(
        ...     name="my-server",
        ...     network={"id": "net-xxx"},
        ...     key_pair_name="my-key",
        ...     arch="X86",
        ...     auto_select=True
        ... )
    """
    if auto_select:
        success, error, resolved = _auto_resolve_flavor_and_image(
            access=access,
            flavor=flavor,
            resource_flavor=resource_flavor,
            image_id=image_id,
            availability_zone=availability_zone,
            arch=arch
        )
        
        if not success:
            return format_api_result(False, error=error)
        # 使用解析后的值
        flavor = resolved.get("flavor")
        resource_flavor = resolved.get("resource_flavor")
        image_id = resolved.get("image_id")
        # 在返回结果中附加自动选择的信息
        auto_info = {
            "auto_selected": {
                "flavor": resolved.get("auto_selected_flavor"),
                "image": resolved.get("auto_selected_image"),
                "flavor_info": resolved.get("flavor_info"),
                "image_info": resolved.get("image_info")
            }
        }
    else:
        # 不自动选择，进行基本验证
        valid, error = _validate_create_params(
            name=name, image_id=image_id, network=network,
            admin_pass=admin_pass, key_pair_name=key_pair_name,
            flavor=flavor, resource_flavor=resource_flavor
        )
        if not valid:
            return format_api_result(False, error=error)
        auto_info = {"auto_selected": {"flavor": False, "image": False}}
    # HPS 类型需要 hps_cluster_id 在 body 顶层，而非 network 内
    # 从 network 中提取（如果用户误将 hps_cluster_id 放在 network 内）
    _hps_cluster_id = None
    if network and isinstance(network, dict):
        _hps_cluster_id = network.pop('hps_cluster_id', None)
    
    required_params = {
        "name": name,
        "image_id": image_id,
        "network": network
    }
    
    optional_params = {
        "admin_pass": admin_pass,
        "arch": arch,
        "availability_zone": availability_zone,
        "charging_info": charging_info,
        "count": count,
        "enterprise_project_id": enterprise_project_id,
        "flavor": flavor,
        "resource_flavor": resource_flavor,
        "key_pair_name": key_pair_name,
        "root_volume": root_volume,
        "data_volume": data_volume,
        "server_type": server_type,
        "user_data": user_data
    }
    
    body = build_request_body(required_params, optional_params)
    # HACK: 如果 hps_cluster_id 被提取出来，手动加到 body 顶层（HPS 专用）
    if _hps_cluster_id:
        body['hps_cluster_id'] = _hps_cluster_id
    result = access.sdk().execute(lambda s: make_api_call(
        s,
        'POST',
        '/v1/{project_id}/dev-servers',
        body=body
    ))
    api_result = format_api_result(True, data=result)
    api_result = add_api_reference(api_result, "22.1 CreateDevServer (Page 1559)")
    # 附加自动选择信息
    if auto_info:
        api_result["auto_selection_details"] = auto_info
    
    return api_result

from common_module.api_helper import make_api_call
__all__ = ['ma_liteserver_create']
