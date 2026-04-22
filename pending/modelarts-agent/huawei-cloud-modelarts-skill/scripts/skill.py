# -*- coding: utf-8 -*-
"""
ModelArts 资源全功能管理 Skill
覆盖：资源管理、训练、推理、Notebook
认证：临时安全凭证
安全：无缓存、无存储、自动脱敏
"""
from tools.security import get_session, desensitize_data
from modelarts.estimator import Estimator
from modelarts.model import Model
from modelarts.predictor import Predictor
from modelarts.notebook import Notebook

# ==================== Skill 元数据 ====================
SKILL_METADATA = {
    "skill_name": "ModelArts_Resource_Manager",
    "skill_version": "1.0.0",
    "description": "ModelArts 资源/训练/推理/Notebook 统一管理",
    "author": "ModelArts_User",
    "security_level": "high",
    "support_auth_type": "system_token"
}

# ==================== 功能实现 ====================
def list_resource_overview(params):
    try:
        session = get_session()
        obs = session.get_obs_client()
        buckets = obs.list_buckets()
        return {
            "status": "success",
            "data": {
                "obs_bucket_count": len(buckets.get("Buckets", [])),
                "msg": "资源概览查询成功"
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def list_training_jobs(params):
    try:
        limit = params.get("limit", 5)
        jobs = Estimator.list_train_instances(get_session(), limit=limit)
        return {"status": "success", "data": desensitize_data(jobs)}
    except Exception:
        return {"status": "error", "message": "查询训练作业失败"}

def create_training_job(params):
    try:
        est = Estimator(
            session=get_session(),
            source_directory=params["code_dir"],
            boot_file=params["boot_file"],
            flavor=params.get("flavor", "modelarts.vm.cpu.2u")
        )
        job = est.fit(job_name=params["job_name"], wait=False)
        return {"status": "success", "data": desensitize_data(job)}
    except Exception:
        return {"status": "error", "message": "创建训练作业失败"}

def list_models(params):
    try:
        limit = params.get("limit", 5)
        models = Model.list_models(get_session(), limit=limit)
        return {"status": "success", "data": desensitize_data(models)}
    except Exception:
        return {"status": "error", "message": "查询模型失败"}

def list_services(params):
    try:
        limit = params.get("limit", 5)
        services = Predictor.list_services(get_session(), limit=limit)
        return {"status": "success", "data": desensitize_data(services)}
    except Exception:
        return {"status": "error", "message": "查询推理服务失败"}

def list_notebooks(params):
    try:
        limit = params.get("limit", 5)
        notebooks = Notebook.list_notebooks(get_session(), limit=limit)
        return {"status": "success", "data": desensitize_data(notebooks)}
    except Exception:
        return {"status": "error", "message": "查询 Notebook 失败"}

# ==================== Action 路由 ====================
ACTION_MAP = {
    "list_resource_overview": list_resource_overview,
    "list_training_jobs": list_training_jobs,
    "create_training_job": create_training_job,
    "list_models": list_models,
    "list_services": list_services,
    "list_notebooks": list_notebooks
}

# ==================== 标准入口 ====================
def main(params, context={}):
    try:
        action = params.get("action")
        req_params = params.get("params", {})

        if action not in ACTION_MAP:
            return {
                "status": "error",
                "skill_metadata": SKILL_METADATA,
                "message": "不支持的 action"
            }

        result = ACTION_MAP[action](req_params)
        result["skill_metadata"] = SKILL_METADATA
        return result

    except Exception:
        return {
            "status": "error",
            "skill_metadata": SKILL_METADATA,
            "message": "Skill 执行异常"
        }