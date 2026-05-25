#!/usr/bin/env python3
"""
NodePool模块 - create_node_pool函数
功能：创建新的节点池
"""

from ._bootstrap import authenticated_api_call, format_api_result, access_api_call, Dict, Any, Optional


@authenticated_api_call
def create_node_pool(
    access,
    pool_name: str,
    node_pool_name: str,
    flavor: str,
    node_num: int,
    max_node_num: Optional[int] = None,
    az: str = None,
    volume_group: str = None,
    docker_base_size: int = 50,
    kubernetes_lv_size: int = 500,
    post_install: str = "",
    runtime: str = "docker",
    labels: Dict[str, str] = None,
    annotations: Dict[str, str] = None
) -> Dict[str, Any]:
    """
    创建新的节点池

    Args:
        pool_name: 资源池 ID（必填）格式: pool-xxx-xxx-xxx-xxx
        node_pool_name: 节点池名称（必填）
        flavor: 节点规格（必填）如 modelarts.vm.cpu.16u64g.d
        node_num: 节点数量（必填）
        max_node_num: 最大节点数量，默认等于 node_num
        az: 可用区，默认使用资源池所在可用区
        volume_group: 卷组配置，默认 "vgpaas"
        docker_base_size: Docker 基础镜像大小（GB），默认 50
        kubernetes_lv_size: Kubernetes 逻辑卷大小（GB），默认 500
        post_install: 节点启动后执行的脚本
        runtime: 容器运行时，默认 "docker"
        labels: 节点标签
        annotations: 节点注解

    调用经验:
        - 新节点池创建需要 5-10 分钟才能完全就绪
        - 每个节点池使用独立的规格，不能混合规格
        - 创建后可以通过 update_node_pool 进行扩缩容
        - volume_group 配置非常重要，错误可能导致节点创建失败
        - node_pool_name 命名规则: 2-50字符，只能小写字母、数字、连字符(-)
                       必须字母开头，字母或数字结尾，不能以连字符结尾
                       不能包含 . 符号

    常见规格:
        - modelarts.vm.cpu.8u32g.d: 8核32G
        - modelarts.vm.cpu.16u64g.d: 16核64G
        - modelarts.vm.gpu.a100.80g: A100 GPU

    Returns:
        创建结果
    """
    if not pool_name:
        return format_api_result(False, error="pool_name is required")
    if not node_pool_name:
        return format_api_result(False, error="node_pool_name is required")
    if not flavor:
        return format_api_result(False, error="flavor is required")
    if node_num is None or node_num < 0:
        return format_api_result(False, error="node_num is required and must >= 0")

    body = {
        "apiVersion": "v2",
        "kind": "NodePool",
        "metadata": {
            "name": node_pool_name
        },
        "spec": {
            "resources": {
                "nodePool": node_pool_name,
                "flavor": flavor,
                "count": node_num,
                "maxCount": max_node_num if max_node_num is not None else node_num,
                "azs": [{"az": az, "count": node_num}] if az else [],
                "volumeGroupConfigs": [
                    {
                        "volumeGroup": volume_group or "vgpaas",
                        "mode": "share",
                        "lvmConfig": {
                            "lvType": "linear"
                        }
                    }
                ],
                "os": {"name": "EulerOS 2.9"},
                "extendParams": {
                    "dockerBaseSize": str(docker_base_size),
                    "kubernetesLVSize": str(kubernetes_lv_size),
                    "nodePoolName": node_pool_name,
                    "postInstall": post_install or "",
                    "runtime": runtime,
                    "taintPolicyOnExistingNodes": "ignore",
                    "labelPolicyOnExistingNodes": "ignore",
                    "driverPolicyOnExistingNodes": "ignore"
                }
            }
        }
    }

    result = access_api_call(
        access,
        "POST",
        "/v2/{project_id}/pools/{p_id}/nodepools",
        p_id=pool_name, body=body
    )

    return format_api_result(True, data=result)


__all__ = ["create_node_pool"]
