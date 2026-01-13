"""
群組管理工具

提供組件群組的創建和管理功能
"""

import time
from typing import Dict, Any, Optional, List, Tuple

from .client import GrasshopperClient
from .component_manager import ComponentManager
from .utils import hex_to_rgb


class GroupManager:
    """群組管理器"""
    
    def __init__(self, client: Optional[GrasshopperClient] = None, component_manager: Optional[ComponentManager] = None):
        """
        初始化群組管理器
        
        Args:
            client: Grasshopper 客戶端實例
            component_manager: 組件管理器實例（用於獲取組件 ID 映射）
        """
        self.client = client or GrasshopperClient()
        self.component_manager = component_manager or ComponentManager(self.client)
    
    def group_components(
        self,
        component_ids: List[str],
        group_name: str,
        color: Optional[Tuple[int, int, int]] = None,
        color_hex: Optional[str] = None,
        component_id_keys: Optional[List[str]] = None
    ) -> bool:
        """
        將多個組件群組起來
        
        Args:
            component_ids: 組件實際 ID 列表
            group_name: 群組名稱
            color: RGB 顏色元組 (r, g, b)
            color_hex: 十六進制顏色字符串（如 "#FF0000"）
            component_id_keys: 組件 ID 鍵列表（用於從映射中查找）
        
        Returns:
            是否成功創建群組
        """
        # 如果提供了 ID 鍵列表，從映射中查找實際 ID
        if component_id_keys:
            actual_ids = []
            missing_components = []
            
            for key in component_id_keys:
                actual_id = self.component_manager.get_component_id(key)
                if actual_id:
                    actual_ids.append(actual_id)
                else:
                    missing_components.append(key)
            
            if missing_components:
                self.client.safe_print(f"警告: 群組中有 {len(missing_components)} 個組件找不到 ID:")
                for comp_id in missing_components[:5]:
                    self.client.safe_print(f"  - {comp_id}")
                if len(missing_components) > 5:
                    self.client.safe_print(f"  ... 還有 {len(missing_components) - 5} 個")
            
            component_ids = actual_ids
        
        if not component_ids:
            self.client.safe_print("錯誤: 沒有可用的組件 ID")
            return False
        
        # 處理顏色
        if color_hex:
            color = hex_to_rgb(color_hex)
        
        if color is None:
            color = (200, 200, 200)  # 默認灰色
        
        r, g, b = color
        
        params = {
            "componentIds": component_ids,
            "groupName": group_name,
            "colorR": r,
            "colorG": g,
            "colorB": b
        }
        
        response = self.client.send_command("group_components", params)
        
        if response.get("success") and response.get("data", {}).get("success"):
            return True
        else:
            error = response.get("error") or response.get("data", {}).get("error", "未知錯誤")
            self.client.safe_print(f"群組失敗: {error}")
            return False
    
    def group_components_batch(self, groups: List[Dict[str, Any]]) -> Tuple[int, int]:
        """
        批量創建多個群組
        
        Args:
            groups: 群組配置列表，每個配置包含：
                - name: 群組名稱
                - componentIds 或 componentIdKeys: 組件 ID 列表或 ID 鍵列表
                - color 或 colorHex: 顏色
        
        Returns:
            (成功數量, 失敗數量) 元組
        """
        success_count = 0
        fail_count = 0
        
        for group in groups:
            group_name = group.get("name", "未命名群組")
            component_ids = group.get("componentIds", [])
            component_id_keys = group.get("componentIdKeys", [])
            color = group.get("color")
            color_hex = group.get("colorHex")
            
            self.client.safe_print(f"\n群組: {group_name} ({len(component_ids) + len(component_id_keys)} 個組件)")
            
            if self.group_components(
                component_ids,
                group_name,
                color,
                color_hex,
                component_id_keys
            ):
                success_count += 1
            else:
                fail_count += 1
            
            time.sleep(0.2)
        
        return success_count, fail_count

