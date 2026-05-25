#!/usr/bin/env python3

"""infer_v2_module 主模块 - 统一导出所有功能"""

from .create_service import ma_inference_service_create, quick_create_v2_service
from .get_service import ma_inference_service_get, quick_get_v2_service
from .list_services import ma_inference_service_list, quick_list_v2_services
from .update_service import ma_inference_service_update, quick_update_v2_service
from .delete_service import ma_inference_service_delete, quick_delete_v2_service

from .batch_delete import ma_inference_service_batch_delete, quick_batch_delete_v2

from .switch_version import ma_inference_service_switch_version, quick_switch_v2_version
from .get_version import ma_inference_service_get_version, quick_get_v2_version

from .start_service import ma_inference_service_start, quick_start_v2_service
from .stop_service import ma_inference_service_stop, quick_stop_v2_service
from .interrupt_service import ma_inference_service_interrupt, quick_interrupt_v2_service

from .health import ma_inference_service_health, quick_health_v2_service
from .get_events import ma_inference_service_get_events, quick_get_v2_events
from .analyze_events import ma_inference_service_analyze_events, quick_analyze_v2_events
from .get_exec import ma_inference_service_get_exec, quick_get_v2_exec

from .detect_region import ma_region_detect_current, quick_detect_v2_region
from .create_with_region import ma_inference_service_create_with_region_consistency, quick_create_v2_with_region
from .get_pool import ma_inference_service_get_pools, quick_get_v2_pools
from .get_flavor import ma_inference_service_get_flavors, quick_get_v2_flavors, suggest_flavor_for_custom_spec

__all__ = [
    'ma_inference_service_create',
    'ma_inference_service_get',
    'ma_inference_service_list',
    'ma_inference_service_update',
    'ma_inference_service_delete',
    'ma_inference_service_batch_delete',
    'ma_inference_service_switch_version',
    'ma_inference_service_get_version',
    'ma_inference_service_start',
    'ma_inference_service_stop',
    'ma_inference_service_interrupt',
    'ma_inference_service_health',
    'ma_inference_service_get_events',
    'ma_inference_service_analyze_events',
    'ma_inference_service_get_exec',
    'ma_region_detect_current',
    'ma_inference_service_create_with_region_consistency',
    'ma_inference_service_get_pools',
    'ma_inference_service_get_flavors',
    'suggest_flavor_for_custom_spec',
    'quick_create_v2_service',
    'quick_get_v2_service',
    'quick_list_v2_services',
    'quick_update_v2_service',
    'quick_delete_v2_service',
    'quick_batch_delete_v2',
    'quick_switch_v2_version',
    'quick_get_v2_version',
    'quick_start_v2_service',
    'quick_stop_v2_service',
    'quick_interrupt_v2_service',
    'quick_health_v2_service',
    'quick_get_v2_events',
    'quick_analyze_v2_events',
    'quick_get_v2_exec',
    'quick_detect_v2_region',
    'quick_create_v2_with_region',
    'quick_get_v2_pools',
    'quick_get_v2_flavors',
]