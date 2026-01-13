"""
參數設置工具

提供組件參數設置功能，包括 Number Slider 和 Vector XYZ 等
"""

import time
from typing import Dict, Any, Optional, List, Tuple

from .client import GrasshopperClient
from .component_manager import ComponentManager
from .utils import determine_slider_range


class ParameterSetter:
    """參數設置器"""
    
    def __init__(self, client: Optional[GrasshopperClient] = None, component_manager: Optional[ComponentManager] = None):
        """
        初始化參數設置器
        
        Args:
            client: Grasshopper 客戶端實例
            component_manager: 組件管理器實例（用於獲取組件 ID 映射）
        """
        self.client = client or GrasshopperClient()
        self.component_manager = component_manager or ComponentManager(self.client)
    
    def set_slider_properties(
        self,
        component_id: str,
        value: str,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        rounding: float = 0.1,
        component_id_key: Optional[str] = None
    ) -> bool:
        """
        設置 Number Slider 的屬性
        
        Args:
            component_id: 組件實際 ID
            value: 當前值（字符串）
            min_value: 最小值
            max_value: 最大值
            rounding: 精度（小數點後幾位）
            component_id_key: 組件 ID 鍵（用於從映射中查找）
        
        Returns:
            是否成功設置
        """
        # 如果提供了 ID 鍵，從映射中查找實際 ID
        if component_id_key:
            actual_id = self.component_manager.get_component_id(component_id_key)
            if actual_id:
                component_id = actual_id
            else:
                self.client.safe_print(f"錯誤: 找不到組件 ID '{component_id_key}'")
                return False
        
        params: Dict[str, Any] = {
            "id": component_id,
            "value": value
        }
        
        if min_value is not None:
            params["min"] = min_value
        if max_value is not None:
            params["max"] = max_value
        if rounding is not None:
            params["rounding"] = rounding
        
        response = self.client.send_command("set_slider_properties", params)
        
        if response.get("success"):
            return True
        else:
            error = response.get("error", "未知錯誤")
            self.client.safe_print(f"設置 Slider 屬性失敗: {error}")
            return False
    
    def set_component_value(
        self,
        component_id: str,
        value: str,
        parameter: Optional[str] = None,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        rounding: Optional[float] = None,
        component_id_key: Optional[str] = None
    ) -> bool:
        """
        設置組件的值（通用方法，支持多種組件類型）
        
        Args:
            component_id: 組件實際 ID
            value: 要設置的值（字符串）
            parameter: 參數名稱（可選，用於指定要設置的參數，如 Vector XYZ 的 X、Y、Z）
            min_value: 最小值（僅對 Number Slider 有效）
            max_value: 最大值（僅對 Number Slider 有效）
            rounding: 精度（僅對 Number Slider 有效）
            component_id_key: 組件 ID 鍵（用於從映射中查找）
        
        Returns:
            是否成功設置
        """
        # 如果提供了 ID 鍵，從映射中查找實際 ID
        if component_id_key:
            actual_id = self.component_manager.get_component_id(component_id_key)
            if actual_id:
                component_id = actual_id
            else:
                self.client.safe_print(f"錯誤: 找不到組件 ID '{component_id_key}'")
                return False
        
        params: Dict[str, Any] = {
            "id": component_id,
            "value": value
        }
        
        if parameter:
            params["parameter"] = parameter
        if min_value is not None:
            params["min"] = min_value
        if max_value is not None:
            params["max"] = max_value
        if rounding is not None:
            params["rounding"] = rounding
        
        response = self.client.send_command("set_component_value", params)
        
        if response.get("success"):
            return True
        else:
            error = response.get("error", "未知錯誤")
            self.client.safe_print(f"設置組件值失敗: {error}")
            return False
    
    def set_slider(
        self,
        component_id_key: str,
        value: str,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        rounding: float = 0.1,
        auto_range: bool = True
    ) -> bool:
        """
        設置 Slider 的值（自動確定範圍）
        
        Args:
            component_id_key: 組件 ID 鍵
            value: 當前值（字符串）
            min_value: 最小值（如果為 None 且 auto_range=True，則自動確定）
            max_value: 最大值（如果為 None 且 auto_range=True，則自動確定）
            rounding: 精度
            auto_range: 是否自動確定範圍
        
        Returns:
            是否成功設置
        """
        if auto_range and (min_value is None or max_value is None):
            min_val, max_val = determine_slider_range(component_id_key, float(value))
            if min_value is None:
                min_value = min_val
            if max_value is None:
                max_value = max_val
        
        # 優先使用 set_slider_properties
        return self.set_slider_properties(
            "",
            value,
            min_value,
            max_value,
            rounding,
            component_id_key
        )
    
    def set_vector_xyz(
        self,
        component_id_key: str,
        x: float,
        y: float,
        z: float
    ) -> bool:
        """
        設置 Vector XYZ 組件的 X、Y、Z 值
        
        Args:
            component_id_key: 組件 ID 鍵
            x: X 值
            y: Y 值
            z: Z 值
        
        Returns:
            是否全部成功設置
        """
        success_x = self.set_component_value("", str(x), "X", component_id_key=component_id_key)
        time.sleep(0.05)
        success_y = self.set_component_value("", str(y), "Y", component_id_key=component_id_key)
        time.sleep(0.05)
        success_z = self.set_component_value("", str(z), "Z", component_id_key=component_id_key)
        
        return success_x and success_y and success_z
    
    def set_sliders_batch(self, slider_configs: List[Tuple[str, str, Optional[float], Optional[float], float]]) -> Tuple[int, int]:
        """
        批量設置多個 Slider
        
        Args:
            slider_configs: Slider 配置列表，每個配置為：
                (component_id_key, value, min_value, max_value, rounding)
        
        Returns:
            (成功數量, 失敗數量) 元組
        """
        success_count = 0
        fail_count = 0
        
        for config in slider_configs:
            component_id_key = config[0]
            value = config[1]
            min_value = config[2] if len(config) > 2 else None
            max_value = config[3] if len(config) > 3 else None
            rounding = config[4] if len(config) > 4 else 0.1
            
            self.client.safe_print(f"\n設置 {component_id_key} = {value}")
            
            if self.set_slider(component_id_key, value, min_value, max_value, rounding):
                success_count += 1
            else:
                fail_count += 1
            
            time.sleep(0.1)
        
        return success_count, fail_count

