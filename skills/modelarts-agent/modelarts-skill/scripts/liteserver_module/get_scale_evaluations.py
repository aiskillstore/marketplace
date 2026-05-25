#!/usr/bin/env python3
"""
Lite Server 模块 - get_scale_evaluations 函数
功能：查询超节点扩缩容支持规格列表及容量测算
说明: 仅限超节点(Hyperinstance)，返回扩缩容规格列表和容量保有情况
重要说明:
  hyperinstance_id 不能使用 list_all_hyperinstances 返回的顶层 id（那是集群ID），
  必须使用 server_hps.id（真正的超节点实例ID）。
  例如 list_all_hyperinstances 返回结构为：
  {
    "id": "9cee8e1c-...",       <- 这是 CLUSTER ID，不可直接使用
    "server_hps": {
      "id": "5ba58f1d-...",     <- 这才是真正的 HYPERINSTANCE ID，用于此接口
      "name": "sp22v-xxx"
    }
  }
"""

from ._bootstrap import authenticated_api_call, Dict, Any
from .common import execute_hyperinstance_operation

@authenticated_api_call
def ma_liteserver_get_scale_evaluations(
    access,
    hyperinstance_id: str
) -> Dict[str, Any]:
    """
    Get scale evaluations for a Lite Server hyperinstance.
    Args:
        hyperinstance_id: The hyperinstance ID (required)
    Returns:
        {
            "evaluations": [
                {
                    "is_sold_out": false,
                    "flavor": "physical.xx.8765",
                    "resource_flavor": "modelarts.bm.abc.arm.ei.d"
                },
                ...
            ]
        }
    """
    return execute_hyperinstance_operation(
        access,
        hyperinstance_id,
        'GET',
        '/v1/{project_id}/dev-servers/hyperinstance/{hyperinstance_id}/scale-evaluations',
        "GetScaleEvaluationsDevServer"
    )

from common_module.api_helper import make_api_call
__all__ = ['ma_liteserver_get_scale_evaluations']
