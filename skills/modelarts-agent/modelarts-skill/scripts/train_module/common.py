#!/usr/bin/env python3
"""
训练模块 - 公共函数

功能：训练任务的公共验证、配置构建、响应解析等
"""

import json
import sys
from typing import Dict, Any, List, Optional

sys.path.insert(0, '.')

from common_module.result import format_api_result


def validate_required_params(params: dict, required: list) -> dict:
    missing = [key for key in required if not params.get(key)]
    if missing:
        return format_error_result(error=f"Missing required parameters: {', '.join(missing)}", status_code=400)
    return format_api_result(success=True)


def format_error_result(error: str, status_code: int = 400) -> dict:
    result = format_api_result(success=False, error=error)
    result['status_code'] = status_code
    return result


def format_success_result(data=None, status_code: int = 200, **kwargs) -> dict:
    result = format_api_result(success=True, data=data)
    result['status_code'] = status_code
    for k, v in kwargs.items():
        result[k] = v
    return result


def validate_training_job_params(name: str, command: str = None, train_url: str = None) -> Dict[str, Any]:
    params = {'name': name}
    if command:
        params['command'] = command
    if train_url:
        params['train_url'] = train_url
    
    required = ['name']
    validation = validate_required_params(params, required)
    if not validation['success']:
        return validation
    if command and train_url:
        return format_error_result(
            error="Cannot specify both 'command' and 'train_url'. Choose one execution mode.",
            status_code=400
        )
    
    if not command and not train_url:
        return format_error_result(
            error="Must provide either 'command' or 'train_url' parameter",
            status_code=400
        )

    if not isinstance(name, str) or len(name) == 0:
        return format_error_result(
            error="Parameter 'name' must be a non-empty string",
            status_code=400
        )
    
    if len(name) > 64:
        return format_error_result(
            error="Parameter 'name' must be 1-64 characters",
            status_code=400
        )
    
    return format_success_result()


def _build_metadata(name: str, description: str = None, annotations: Dict[str, str] = None,
                    enable_jupyterlab: bool = False) -> Dict[str, Any]:
    metadata = {
        "name": name,
        "workspace_id": "0",
        "description": description or f"Training job: {name}"
    }
    
    if enable_jupyterlab:
        annotations = annotations or {}
        annotations["jupyter-lab/enable"] = "true"
    
    if annotations:
        metadata["annotations"] = annotations
    
    return metadata


def _build_algorithm_command(command: str, image_url: str = None) -> Dict[str, Any]:
    algorithm = {
        "command": command,
        "working_dir": "/home/ma-user/modelarts/user-job-dir",
        "local_code_dir": "/home/ma-user/modelarts/user-job-dir"
    }
    
    if image_url:
        algorithm["engine"] = {"image_url": image_url}
    else:
        algorithm["engine"] = {"engine_name": "python", "engine_version": "3.8"}
    
    return algorithm


def _parse_train_url(train_url: str) -> tuple:
    if "/" in train_url:
        parts = train_url.rsplit("/", 1)
        return parts[0] + "/", parts[1]
    return "./", train_url


def _build_algorithm_script(train_url: str, image_url: str = None,
                            parameters: Dict[str, Any] = None,
                            dataset_id: str = None, model_url: str = None) -> Dict[str, Any]:
    code_dir, boot_file = _parse_train_url(train_url)
    
    algorithm = {
        "code_dir": code_dir,
        "boot_file": boot_file,
        "working_dir": "/home/ma-user/modelarts/user-job-dir",
        "local_code_dir": "/home/ma-user/modelarts/user-job-dir"
    }
    
    if image_url:
        algorithm["engine"] = {"image_url": image_url}

    if parameters and isinstance(parameters, dict):
        algorithm["parameters"] = [{"name": str(k), "value": str(v)} for k, v in parameters.items()]

    if dataset_id:
        input_spec = {
            "name": "data_url",
            "remote": {"obs": {"obs_url": dataset_id}} if dataset_id.startswith("obs://")
            else {"name": "data_url", "remote": {"dataset": {"id": dataset_id}}}
        }
        algorithm["inputs"] = [input_spec]

    if model_url:
        algorithm["outputs"] = [{"name": "output_dir", "remote": {"obs": {"obs_url": model_url}}}]
    
    return algorithm


def _build_resource_spec(flavor_id: str = None, flavor_label: str = None,
                        pool_id: str = None, pool_name: str = None) -> Dict[str, Any]:
    resource = {"node_count": 1}
    
    if flavor_id:
        resource["flavor_id"] = flavor_id
        resource["policy"] = "regular"
    if flavor_label:
        resource["flavor_label"] = flavor_label
    if pool_id:
        resource["pool_id"] = pool_id
    if pool_name:
        resource["pool_name"] = pool_name
    
    return resource


def _build_spec(job_log_path: str = None, runtime_type: str = "production",
                resource: Dict[str, Any] = None) -> Dict[str, Any]:
    spec = {}
    
    if resource:
        spec["resource"] = resource
    
    spec["log_export_path"] = {"obs_url": job_log_path or ""}
    spec["runtime_type"] = "production" if runtime_type not in ["production", "debug"] else runtime_type
    
    return spec


def build_training_job_config(name: str, command: str = None, train_url: str = None,
                             image_url: str = None, parameters: Dict[str, Any] = None,
                             dataset_id: str = None, model_url: str = None,
                             job_log_path: str = None, description: str = None,
                             runtime_type: str = "production", enable_jupyterlab: bool = False,
                             annotations: Dict[str, str] = None, 
                             flavor_id: str = None, flavor_label: str = None,
                             pool_id: str = None, pool_name: str = None) -> Dict[str, Any]:
    """
    构建训练任务配置
    
    Args:
        name: 任务名称
        command: 执行命令（命令模式）
        train_url: 训练脚本路径（脚本模式）
        image_url: 镜像地址
        parameters: 参数
        dataset_id: 数据集ID
        model_url: 模型输出路径
        job_log_path: 日志导出路径
        description: 描述
        runtime_type: 运行时类型 (production/debug)。调试模式(debug)支持JupyterLab和SSH
        enable_jupyterlab: 是否启用JupyterLab (仅debug模式有效)
        annotations: 注解
        flavor_id: 公共池规格ID (用于公共池)
        flavor_label: 公共池规格标签 (用于公共池)
        pool_id: 专属池ID (用于专属池)
        pool_name: 专属池名称 (用于专属池)
    
    Returns:
        任务配置字典
    """
    metadata = _build_metadata(name, description, annotations, enable_jupyterlab)

    algorithm = {}
    if command:
        algorithm = _build_algorithm_command(command, image_url)
    elif train_url:
        algorithm = _build_algorithm_script(train_url, image_url, parameters, dataset_id, model_url)

    resource = _build_resource_spec(flavor_id, flavor_label, pool_id, pool_name)
    spec = _build_spec(job_log_path, runtime_type, resource)

    request_body = {"kind": "job", "metadata": metadata}
    
    if algorithm:
        request_body["algorithm"] = algorithm
    
    if spec:
        request_body["spec"] = spec
    
    return request_body


def parse_training_job_response(api_result: Dict[str, Any]) -> Dict[str, Any]:
    if api_result.get("success"):
        result_data = api_result.get("result", {})
        job_id = result_data.get("job_id", "")
        
        return format_success_result(
            data=result_data,
            job_id=job_id,
            status_code=api_result.get("status_code", 200)
        )
    else:
        error_msg = api_result.get("error", "Unknown API error")
        if isinstance(error_msg, dict):
            error_msg = json.dumps(error_msg, ensure_ascii=False)
        
        return format_error_result(
            error=error_msg,
            status_code=api_result.get("status_code", 500)
        )


def parse_train_url(train_url: str) -> tuple:
    if "/" in train_url:
        parts = train_url.rsplit("/", 1)
        code_dir = parts[0] + "/"
        boot_file = parts[1]
        return code_dir, boot_file
    else:
        return "./", train_url


__all__ = [
    'validate_training_job_params',
    'build_training_job_config',
    'parse_training_job_response',
    'parse_train_url'
]
