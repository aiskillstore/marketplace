#!/usr/bin/env python3
"""
Notebook模块 - image_register函数
功能：注册镜像
"""

from ._bootstrap import ensure_authentication, format_api_result, simple_api_call, Any, Dict


def image_register(swr_path: str, arch: str = "X86_64", description: str = None,
                   origin: str = "CUSTOMIZE", resource_category: list = None,
                   service_type: str = "UNKNOWN", services: list = None,
                   visibility: str = "PRIVATE", workspace_id: str = None,
                   flavor_type: str = None, swr_instance_id: str = None,
                   read_me: str = None) -> Dict[str, Any]:
    """
    注册 SWR 中的自定义镜像到 ModelArts。

    API 路径: POST /v1/{project_id}/images

    Args:
        swr_path: SWR 镜像地址 (必填) - 格式: [仓库地址[:端口]]/[命名空间]/[镜像名称]:[标签]
        arch: 处理器架构，"X86_64" 或 "AARCH64" (可选，默认 "X86_64")
        description: 镜像描述 (可选) - 最大 512 字符
        origin: 镜像来源，"CUSTOMIZE" 或 "IMAGE_SAVE" (可选，默认 "CUSTOMIZE")
        resource_category: 支持的规格列表，如 ["CPU", "GPU", "ASCEND"] (可选)
        service_type: 支持服务类型，"COMMON"/"INFERENCE"/"TRAIN"/"DEV"/"UNKNOWN" (可选，默认 "UNKNOWN")
        services: 支持的服务列表，如 ["NOTEBOOK", "SSH"] (可选)
        visibility: 可见度，"PRIVATE" 或 "PUBLIC" (可选，默认 "PRIVATE")
        workspace_id: 工作空间 ID (可选，默认 "0")
        flavor_type: 资源类型，"ASCEND_SNT9"/"ASCEND_SNT9B"/"ASCEND_SNT3" (可选)
        swr_instance_id: 企业版 SWR 仓库 ID (可选)
        read_me: 镜像指导文档 (可选) - 最大 3000 字符

    Returns:
        注册结果

    示例:
        >>> from notebook_module import image_register
        >>> result = image_register(
        ...     'swr.cn-north-4.myhuaweicloud.com/dev-custom/my-image:v1',
        ...     description='My custom image'
        ... )
        >>> if result['success']:
        ...     print("注册成功，ID:", result['data']['id'])
    """

    auth_result = ensure_authentication()
    if not auth_result["success"]:
        return format_api_result(False, error=auth_result["error"])
    
    try:
        access = auth_result["access"]

        if not swr_path:
            return format_api_result(False, error="swr_path is required")

        body = {"swr_path": swr_path, "arch": arch, "origin": origin,
                "service_type": service_type, "visibility": visibility}
        if description:
            body["description"] = description
        if resource_category:
            body["resource_category"] = resource_category
        if services:
            body["services"] = services
        if workspace_id:
            body["workspace_id"] = workspace_id
        if flavor_type:
            body["flavor_type"] = flavor_type
        if swr_instance_id:
            body["swr_instance_id"] = swr_instance_id
        if read_me:
            body["read_me"] = read_me

        print(f"  注册镜像: {swr_path}")

        result = simple_api_call(
            access,
            'POST',
            '/v1/{project_id}/images',
            body=body
        )

        return format_api_result(True, data=result)
        
    except Exception as e:
        return format_api_result(False, error=f"注册镜像时发生异常: {e}")


__all__ = ['image_register']