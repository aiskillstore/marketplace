#!/usr/bin/env python3
"""
公共模块 - 认证函数文件
功能：认证相关公共函数
"""

import sys
from typing import Any, Dict

sys.path.insert(0, '.')


def ensure_authentication() -> Dict[str, Any]:
    try:
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        
        from auth_manager import get_secure_sdk, check_auth_status, create_session

        auth_status = check_auth_status()
        if not auth_status.get("authenticated"):
            success, session_or_error = create_session()
            if not success:
                return {
                    "success": False,
                    "error": f"认证初始化失败: {session_or_error}"
                }

        access = get_secure_sdk()
        return {
            "success": True,
            "access": access
        }
        
    except ImportError as e:
        return {
            "success": False,
            "error": f"导入认证模块失败: {e}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"认证过程异常: {e}"
        }


__all__ = ['ensure_authentication']