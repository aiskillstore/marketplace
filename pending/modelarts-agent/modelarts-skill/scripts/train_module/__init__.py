#!/usr/bin/env python3
"""
ModelArts 训练模块

提供训练任务的创建、查询、停止、删除等功能。
"""

from .job_create import (
    ma_train_job_create,
    create_simple_training_job,
    create_script_training_job,
    create_debug_training_job
)

from .job_list import (
    ma_train_job_list,
    list_training_jobs_simple,
    list_debug_training_jobs,
    list_running_training_jobs,
    list_pending_training_jobs,
    list_completed_training_jobs
)

from .job_stop import (
    ma_train_job_stop,
    stop_training_job_simple,
    stop_pending_training_jobs
)

from .job_delete import (
    ma_train_job_delete,
    delete_training_job_simple,
    delete_completed_training_jobs
)

from .common import (
    validate_training_job_params,
    build_training_job_config,
    parse_training_job_response
)

from .job_get_flavors import (
    ma_train_job_get_flavors,
    list_training_job_flavors
)

from .job_update import (
    ma_train_job_update_description
)

from .job_get_details import (
    ma_show_training_job_details
)

__all__ = [
    'ma_train_job_create',
    'create_simple_training_job',
    'create_script_training_job',
    'create_debug_training_job',

    'ma_train_job_list',
    'list_training_jobs_simple',
    'list_debug_training_jobs',
    'list_running_training_jobs',
    'list_pending_training_jobs',
    'list_completed_training_jobs',

    'ma_train_job_stop',
    'stop_training_job_simple',
    'stop_pending_training_jobs',

    'ma_train_job_delete',
    'delete_training_job_simple',
    'delete_completed_training_jobs',

    'ma_train_job_update_description',

    'ma_show_training_job_details',

    'validate_training_job_params',
    'build_training_job_config',
    'parse_training_job_response',

    'ma_train_job_get_flavors',
    'list_training_job_flavors'
]
