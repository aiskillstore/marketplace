"""
連接管理工具

提供組件連接的創建、修正、錯誤檢查等功能
"""

from typing import Dict, Any, Optional, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from .client import GrasshopperClient
from .component_manager import ComponentManager


class ConnectionManager:
    """連接管理器"""
    
    def __init__(self, client: Optional[GrasshopperClient] = None, component_manager: Optional[ComponentManager] = None):
        """
        初始化連接管理器
        
        Args:
            client: Grasshopper 客戶端實例
            component_manager: 組件管理器實例（用於獲取組件 ID 映射）
        """
        self.client = client or GrasshopperClient()
        self.component_manager = component_manager or ComponentManager(self.client)
    
    def connect_components(
        self,
        source_id: str,
        target_id: str,
        source_param: Optional[str] = None,
        target_param: Optional[str] = None,
        source_id_key: Optional[str] = None,
        target_id_key: Optional[str] = None
    ) -> bool:
        """
        連接兩個組件
        
        Args:
            source_id: 源組件實際 ID
            target_id: 目標組件實際 ID
            source_param: 源組件參數名稱
            target_param: 目標組件參數名稱
            source_id_key: 源組件 ID 鍵（用於從映射中查找）
            target_id_key: 目標組件 ID 鍵（用於從映射中查找）
        
        Returns:
            是否成功連接
        """
        # 如果提供了 ID 鍵，從映射中查找實際 ID
        if source_id_key:
            actual_source_id = self.component_manager.get_component_id(source_id_key)
            if actual_source_id:
                source_id = actual_source_id
            else:
                self.client.safe_print(f"錯誤: 找不到源組件 ID '{source_id_key}'")
                return False
        
        if target_id_key:
            actual_target_id = self.component_manager.get_component_id(target_id_key)
            if actual_target_id:
                target_id = actual_target_id
            else:
                self.client.safe_print(f"錯誤: 找不到目標組件 ID '{target_id_key}'")
                return False
        
        params = {
            "sourceId": source_id,
            "targetId": target_id
        }
        
        if source_param:
            params["sourceParam"] = source_param
        if target_param:
            params["targetParam"] = target_param
        
        response = self.client.send_command("connect_components", params)
        
        if response.get("success"):
            return True
        else:
            error = response.get("error", "未知錯誤")
            self.client.safe_print(f"連接失敗: {error}")
            return False
    
    def connect_components_parallel(self, commands: List[Dict[str, Any]], max_workers: int = 10) -> Tuple[int, int]:
        """
        並行連接多個組件
        
        Args:
            commands: 連接命令列表，每個命令包含：
                - sourceId 或 sourceIdKey: 源組件 ID
                - targetId 或 targetIdKey: 目標組件 ID
                - sourceParam: 源組件參數名稱
                - targetParam: 目標組件參數名稱
            max_workers: 最大並行線程數
        
        Returns:
            (成功數量, 失敗數量) 元組
        """
        success_count = 0
        fail_count = 0
        
        def execute_connect(cmd: Dict[str, Any], index: int, total: int) -> bool:
            params = cmd.get("parameters", {})
            params.get("sourceId", "")
            params.get("targetId", "")
            source_id_key = params.get("sourceId", "")  # 如果使用映射，這裡應該是鍵
            target_id_key = params.get("targetId", "")
            source_param = params.get("sourceParam")
            target_param = params.get("targetParam")
            
            # 嘗試從映射中獲取實際 ID
            actual_source_id = self.component_manager.get_component_id(source_id_key)
            actual_target_id = self.component_manager.get_component_id(target_id_key)
            
            if not actual_source_id:
                self.client.safe_print(f"  ✗ [{index}/{total}] 錯誤: 找不到源組件 ID '{source_id_key}'")
                return False
            
            if not actual_target_id:
                self.client.safe_print(f"  ✗ [{index}/{total}] 錯誤: 找不到目標組件 ID '{target_id_key}'")
                return False
            
            comment = cmd.get("comment", f"{source_id_key} -> {target_id_key}")
            self.client.safe_print(f"  [{index}/{total}] 連接: {comment}")
            
            success = self.connect_components(
                actual_source_id,
                actual_target_id,
                source_param,
                target_param
            )
            
            if success:
                self.client.safe_print("      ✓ 連接成功")
            else:
                self.client.safe_print("      ✗ 連接失敗")
            
            return success
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_command = {
                executor.submit(execute_connect, cmd, i, len(commands)): (i, cmd)
                for i, cmd in enumerate(commands, 1)
            }
            
            for future in as_completed(future_to_command):
                index, cmd = future_to_command[future]
                try:
                    if future.result():
                        success_count += 1
                    else:
                        fail_count += 1
                except Exception as e:
                    self.client.safe_print(f"  ✗ [{index}/{len(commands)}] 執行時發生異常: {e}")
                    fail_count += 1
        
        return success_count, fail_count
    
    def get_document_errors(self) -> List[Dict[str, Any]]:
        """
        獲取文檔中的所有錯誤
        
        Returns:
            錯誤列表
        """
        response = self.client.send_command("get_document_errors", {})
        
        if response.get("success"):
            data = response.get("data") or response.get("result", {})
            return data.get("errors", [])
        else:
            self.client.safe_print(f"獲取錯誤失敗: {response.get('error', '未知錯誤')}")
            return []
    
    def fix_connection(
        self,
        source_id: str,
        target_id: str,
        source_param: str,
        target_param: str,
        source_id_key: Optional[str] = None,
        target_id_key: Optional[str] = None
    ) -> bool:
        """
        修正連接（先斷開舊連接，再建立新連接）
        
        Args:
            source_id: 源組件實際 ID
            target_id: 目標組件實際 ID
            source_param: 源組件參數名稱
            target_param: 目標組件參數名稱
            source_id_key: 源組件 ID 鍵
            target_id_key: 目標組件 ID 鍵
        
        Returns:
            是否成功修正
        """
        # 這裡可以添加斷開舊連接的邏輯（如果需要的話）
        return self.connect_components(
            source_id,
            target_id,
            source_param,
            target_param,
            source_id_key,
            target_id_key
        )

