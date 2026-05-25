#!/usr/bin/env python3
"""
Notebook模块 - create_image函数
功能：从Notebook创建镜像
"""

from ._bootstrap import ensure_authentication, format_api_result, simple_api_call, Any, Dict


def create_image(notebook_id: str, name: str, namespace: str, description: str = None,
                 tag: str = None, workspace_id: str = None, swr_instance_id: str = None,
                 swr_instance_domain: str = None) -> Dict[str, Any]:
    """
    从运行中的 Notebook 实例创建自定义镜像。

    API 路径: POST /v1/{project_id}/notebooks/{id}/create-image

    Args:
        notebook_id: Notebook 实例 ID (必填)
        name: 镜像名称 (必填) - 支持小写字母、数字、中划线、下划线、点
        namespace: SWR 组织名称 (必填) - 可在 SWR 控制台"组织管理"查看
        description: 镜像描述 (可选) - 最大 512 字符
        tag: 镜像标签 (可选) - 支持大小写字母、数字、中划线、下划线、点
        workspace_id: 工作空间 ID (可选，默认 "0")
        swr_instance_id: 企业版 SWR 仓库 ID (可选)
        swr_instance_domain: 企业版 SWR 仓库域名 (可选)

    Returns:
        创建任务结果

    示例:
        >>> from notebook_module import create_image, image_list
        >>> result = create_image(
        ...     'notebook-id',
        ...     'my-custom-image',
        ...     'my-namespace',
        ...     'custom image for ml'
        ... )
        >>> if result['success']:
        ...     print("创建任务已提交，ID:", result['data'].get('id'))
    """

    auth_result = ensure_authentication()
    if not auth_result["success"]:
        return format_api_result(False, error=auth_result["error"])
    
    try:
        access = auth_result["access"]

        if not notebook_id:
            return format_api_result(False, error="notebook_id is required")
        if not name:
            return format_api_result(False, error="name is required")
        if not namespace:
            return format_api_result(False, error="namespace is required")

        body = {"name": name, "namespace": namespace}
        if description:
            body["description"] = description
        if tag:
            body["tag"] = tag
        if workspace_id:
            body["workspace_id"] = workspace_id
        if swr_instance_id:
            body["swr_instance_id"] = swr_instance_id
        if swr_instance_domain:
            body["swr_instance_domain"] = swr_instance_domain

        print(f"  从Notebook创建镜像: {notebook_id} -> {namespace}/{name}")

        result = simple_api_call(
            access,
            'POST',
            '/v1/{project_id}/notebooks/{notebook_id}/create-image',
            body=body,
            notebook_id=notebook_id
        )

        return format_api_result(True, data=result)
        
    except Exception as e:
        return format_api_result(False, error=f"创建镜像时发生异常: {e}")


__all__ = ['create_image']