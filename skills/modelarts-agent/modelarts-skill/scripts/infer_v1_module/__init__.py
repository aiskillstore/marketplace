#!/usr/bin/env python3
"""
infer_v1_module - 推理服务管理模块
"""

import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from .create_service_tags import ma_old_inference_service_create_tags
from .make_token_auth_request import make_token_auth_request
from .stop_service import ma_old_inference_service_stop
from .update_service_property import ma_old_inference_service_update_property
from .delete_service_tags import ma_old_inference_service_delete_tags
from .get_services_count import get_old_service_count
from .full_update_service import ma_old_inference_service_full_update
from .get_service_specifications import ma_old_inference_get_specifications
from .parse_api_response import parse_api_response
from .start_service import ma_old_inference_service_start
from .create_service import ma_old_inference_service_create
from .create_service import quick_create_old_service
from .get_service_tags import ma_old_inference_service_get_tags
from .get_service_events import ma_old_inference_service_get_events
from .get_model import ma_old_inference_list_models
from .delete_service import ma_old_inference_service_delete
from .list_services import ma_old_inference_service_list
from .list_services import quick_list_old_services
from .get_service_internal_channel_info import ma_old_inference_get_internal_channel_info
from .get_service import ma_old_inference_service_get
from .get_service import quick_get_old_service
from .update_service import ma_old_inference_service_update

__all__ = [
    "ma_old_inference_service_create_tags",
    "make_token_auth_request",
    "ma_old_inference_service_stop",
    "ma_old_inference_service_update_property",
    "ma_old_inference_service_delete_tags",
    "get_old_service_count",
    "ma_old_inference_service_full_update",
    "ma_old_inference_get_specifications",
    "ma_old_inference_service_list",
    "ma_old_inference_service_create",
    "ma_old_inference_service_stop",
    "ma_old_inference_service_start",
    "ma_old_inference_service_get",
    "quick_get_old_service",
    "quick_list_old_services",
    "get_old_service_count",
    "quick_create_old_service",
    "ma_old_inference_service_get_events",
    "ma_old_inference_service_create_tags",
    "ma_old_inference_service_get_tags",
    "ma_old_inference_service_delete_tags",
    "ma_old_inference_get_internal_channel_info",
    "ma_old_inference_get_specifications",
    "ma_old_inference_service_update_property",
    "ma_old_inference_service_update",
    "ma_old_inference_service_delete",
    "ma_old_inference_service_full_update",
    "parse_api_response",
    "ma_old_inference_service_start",
    "ma_old_inference_service_create",
    "quick_create_old_service",
    "ma_old_inference_service_get_tags",
    "ma_old_inference_service_get_events",
    "ma_old_inference_list_models",
    "ma_old_inference_service_delete",
    "ma_old_inference_service_list",
    "quick_list_old_services",
    "ma_old_inference_get_internal_channel_info",
    "ma_old_inference_service_get",
    "quick_get_old_service",
    "ma_old_inference_service_update"
]

