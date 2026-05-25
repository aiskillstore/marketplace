#!/usr/bin/env python3
"""
训练模块 - 任务创建

功能：训练任务的创建功能
"""

import json
import sys
from typing import Dict, Any, Optional

sys.path.insert(0, '.')

from common_module import ensure_authentication, format_api_result
from train_module.common import (
    validate_training_job_params,
    build_training_job_config,
    parse_training_job_response
)


def ma_train_job_create(name: str, 
                       train_url: str = None, job_log_path: str = None, 
                       model_url: str = None, dataset_id: str = None, 
                       pool_id: str = None, pool_name: str = None,
                       flavor_id: str = None, flavor_label: str = None,
                       parameters: Dict[str, Any] = None, description: str = None,
                       command: str = None, image_url: str = None,
                       runtime_type: str = "production", enable_jupyterlab: bool = False,
                       annotations: Dict[str, str] = None) -> Dict[str, Any]:
    """
    创建训练任务。
    
    支持两种执行模式：
    1. **命令执行模式**：直接执行 command 参数中的命令（适用于自定义镜像）
    2. **训练脚本模式**：通过 train_url 指定 OBS 路径的训练脚本（适用于预置框架或自定义镜像）
    
    ═══════════════════════════════════════════════════════════════════════════════
    📋 训练任务创建基本规则（Agent 必读）
    ═══════════════════════════════════════════════════════════════════════════════
    
    🔹 规则1：选择运行模式
    - runtime_type="production" (生产模式): 适合正式训练任务，性能最优
    - runtime_type="debug" (调试模式): 适合开发调试，支持 JupyterLab 和 SSH 远程连接
    - 根据用户场景选择：正式训练用 production，需要交互调试用 debug
    
    🔹 规则2：选择资源池 - 生产模式 (production)
    - 公共资源池: 使用 `train_module.ma_train_job_get_flavors()` 获取支持的公共规格列表
    - 专属资源池: 使用 `pool_module.list_pools()` 获取 scope 包含 "Train" 的专属资源池
    - 根据用户需求选择：公共池无需管理，专属池资源独享
    
    🔹 规则3：选择资源池 - 调试模式 (debug)
    - 仅支持专属资源池: 使用 `pool_module.list_pools()` 获取 scope 包含 "Train" 的专属资源池
    - 不支持公共资源池
    
    🔹 规则4：获取镜像
    - 使用 `swr_module.swr_get_train_image_repos()` 获取可用的 SWR 镜像列表
    
    ═══════════════════════════════════════════════════════════════════════════════
    
    📌 前置依赖：
    - 获取可用镜像：使用 `swr_module.swr_get_train_image_repos()` 获取 SWR 镜像仓库列表
    - 获取资源池：使用 `pool_module.list_pools()` 获取专属资源池列表
    
    Args:
        name (str, 必填): 任务名称。限制为1-64位只含数字、字母、下划线和中划线的名称。
        
        train_url (str, 可选): 训练脚本 OBS 路径。与 command 参数互斥。
        command (str,可选): 命令执行模式下的启动命令。与 train_url 互斥。
        
        image_url (str, 可选): 自定义镜像 URL。格式: `{namespace}/{repository_name}:{tag}`
            示例: `dev-custom/openclaw-fxb-test:latest`
            获取方式: 调用 `swr_module.swr_get_train_image_repos()`
        
        pool_id (str, 可选): 资源池 ID。使用专属资源池时必填。
            获取方式: 调用 `pool_module.list_pools()`
        pool_name (str, 可选): 资源池名称。作为 pool_id 的替代标识。
        
        flavor_id (str, 可选): 计算规格 ID。
            示例: `modelarts.pool.visual.xlarge` (1卡), `modelarts.pool.visual.2xlarge` (2卡)
        
        dataset_id (str, 可选): 训练数据集 ID 或 OBS 路径。
        model_url (str, 可选): 模型输出 OBS 路径。
        job_log_path (str, 可选): 日志输出 OBS 路径。
        
        parameters (Dict, 可选): 训练参数字典。示例: `{"learning_rate": 0.001, "batch_size": 32}`
        
        runtime_type (str, 可选): 运行时类型。
            有效值: "production" (默认, 正式训练), "debug" (调试模式，支持 JupyterLab 和 SSH)
            注意: 不支持 "regular"，API 只接受 production 或 debug
            
            📌 调试模式 (debug) 用途：
            - 支持 JupyterLab 交互式调试
            - 支持 SSH 远程访问容器
            - 适用于代码调试、模型验证等开发场景
        
        enable_jupyterlab (bool, 可选): 启用 JupyterLab 调试。
            默认 False
            注意: 此参数仅在 runtime_type="debug" 时生效
            调试模式任务会自动启用 JupyterLab，无需手动设置
        annotations (Dict, 可选): 附加注解。
        
        description (str, 可选): 任务描述。最大256字符。
    
    Returns:
        Dict[str, Any]: 标准化的响应格式
        {
            "success": bool,
            "data": {作业详情},
            "job_id": str,
            "status_code": int
        }
    
    Example:
        # 1. 获取可用镜像列表
        from swr_module import swr_get_train_image_repos
        image_result = swr_get_train_image_repos(offset=0)
        # 选择镜像: dev-custom/openclaw-fxb-test:latest
        
        # 2. 获取资源池列表（可选）
        from pool_module import list_pools
        pool_result = list_pools(access, limit=50)
        
        # 3. 创建训练任务
        result = ma_train_job_create(
            name="my-training-job",
            command="python train.py --epochs=10",
            image_url="dev-custom/openclaw-fxb-test:latest",
            pool_id="pool-xxx",
            description="训练任务示例"
        )
    """
    try:
        validation = validate_training_job_params(name, command, train_url)
        if not validation['success']:
            return validation
        auth_result = ensure_authentication()
        if not auth_result['success']:
            return format_api_result(False, error=auth_result.get('error', 'Authentication failed'))
        access = auth_result['access']
        request_body = build_training_job_config(
            name=name,
            command=command,
            train_url=train_url,
            image_url=image_url,
            parameters=parameters,
            dataset_id=dataset_id,
            model_url=model_url,
            job_log_path=job_log_path,
            description=description,
            runtime_type=runtime_type,
            enable_jupyterlab=enable_jupyterlab,
            annotations=annotations,
            flavor_id=flavor_id,
            flavor_label=flavor_label,
            pool_id=pool_id,
            pool_name=pool_name
        )

        def _create_job(session):
            from modelarts.config.auth import auth_by_apig

            path = f"/v2/{session.project_id}/training-jobs"
            body_bytes = json.dumps(request_body).encode('utf-8')
            
            headers = {'Content-Type': 'application/json'}
            if hasattr(session, 'user_id') and session.user_id:
                headers['x-modelarts-user-id'] = session.user_id
            
            return auth_by_apig(session, "POST", path, body=body_bytes, headers=headers)
        
        api_result = access.sdk().execute(_create_job)

        # 5. 处理响应
        return parse_training_job_response({
            "success": True,
            "result": api_result,
            "status_code": 200
        })
            
    except Exception as e:
        return format_api_result(False, error=f"Unexpected error: {str(e)}")


def create_simple_training_job(name: str, command: str, 
                              image_url: str = None, description: str = None) -> Dict[str, Any]:
    """
    创建简单的命令执行训练任务。
    
    这是 ma_train_job_create 的简化版本，只支持命令执行模式。
    
    Args:
        name: 任务名称
        command: 要执行的命令
        image_url: 自定义镜像 URL (使用 swr_module.swr_get_train_image_repos 获取)
        description: 任务描述
    
    Returns:
        包含成功状态和数据/错误的字典
    """
    return ma_train_job_create(
        name=name,
        command=command,
        image_url=image_url,
        description=description
    )


def create_script_training_job(name: str, train_url: str, 
                              dataset_url: str = None, model_url: str = None, 
                              job_log_path: str = None, parameters: Dict[str, Any] = None, 
                              description: str = None, flavor_id: str = None, 
                              image_url: str = None) -> Dict[str, Any]:
    """
    创建训练脚本模式的任务。
    
    这是 ma_train_job_create 的简化版本，只支持训练脚本模式。
    
    Args:
        name: 任务名称
        train_url: 训练脚本 OBS 路径
        dataset_url: 数据集 OBS 路径
        model_url: 模型输出 OBS 路径
        job_log_path: 日志输出 OBS 路径
        parameters: 训练参数字典
        description: 任务描述
        flavor_id: 计算规格 ID
        image_url: 自定义镜像 URL
    
    Returns:
        包含成功状态和数据/错误的字典
    """
    return ma_train_job_create(
        name=name,
        train_url=train_url,
        dataset_id=dataset_url,
        model_url=model_url,
        job_log_path=job_log_path,
        parameters=parameters,
        description=description,
        flavor_id=flavor_id,
        image_url=image_url
    )


def create_debug_training_job(name: str, command: str, 
                              image_url: str, pool_id: str, 
                              description: str = None) -> Dict[str, Any]:
    """
    创建调试模式训练任务。
    
    调试模式任务支持 JupyterLab 访问。
    
    Args:
        name: 任务名称
        command: 要执行的命令
        image_url: 自定义镜像 URL (使用 swr_module.swr_get_train_image_repos 获取)
        pool_id: 资源池 ID (使用 pool_module.list_pools 获取)
        description: 任务描述
    
    Returns:
        包含成功状态和数据/错误的字典
    """
    return ma_train_job_create(
        name=name,
        command=command,
        image_url=image_url,
        pool_id=pool_id,
        runtime_type="debug",
        enable_jupyterlab=True,
        description=description or f"Debug job: {name}"
    )


__all__ = [
    'ma_train_job_create',
    'create_simple_training_job',
    'create_script_training_job',
    'create_debug_training_job'
]
