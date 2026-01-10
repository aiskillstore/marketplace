"""
Placement 執行器

提供執行 placement_info.json 的完整流程
"""

import time
from typing import Dict, Any, Optional

from .client import GrasshopperClient
from .component_manager import ComponentManager
from .connection_manager import ConnectionManager
from .utils import load_placement_info


class PlacementExecutor:
    """Placement 執行器，執行完整的 placement_info.json 流程"""
    
    def __init__(
        self,
        client: Optional[GrasshopperClient] = None,
        component_manager: Optional[ComponentManager] = None,
        connection_manager: Optional[ConnectionManager] = None
    ):
        """
        初始化 Placement 執行器
        
        Args:
            client: Grasshopper 客戶端實例
            component_manager: 組件管理器實例
            connection_manager: 連接管理器實例
        """
        self.client = client or GrasshopperClient()
        self.component_manager = component_manager or ComponentManager(self.client)
        self.connection_manager = connection_manager or ConnectionManager(self.client, self.component_manager)
    
    def execute_placement_info(
        self,
        json_path: str,
        max_workers: int = 10,
        save_id_map: bool = True,
        id_map_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        執行 placement_info.json 中的命令
        
        Args:
            json_path: placement_info.json 文件路徑
            max_workers: 最大並行線程數
            save_id_map: 是否保存組件 ID 映射
            id_map_path: 組件 ID 映射保存路徑，如果為 None 則使用默認路徑
        
        Returns:
            執行結果字典，包含：
                - add_success: 組件創建成功數量
                - add_fail: 組件創建失敗數量
                - connect_success: 連接成功數量
                - connect_fail: 連接失敗數量
                - add_time: 組件創建耗時
                - connect_time: 連接耗時
                - total_time: 總耗時
        """
        print("=" * 80)
        print("執行 placement_info.json")
        print("=" * 80)
        
        # 讀取 JSON 文件
        print(f"\n讀取命令文件: {json_path}")
        placement_data = load_placement_info(json_path)
        
        if not placement_data:
            print("\n✗ 無法讀取命令文件，程序退出")
            return {
                "success": False,
                "error": "無法讀取命令文件"
            }
        
        description = placement_data.get("description", "無描述")
        commands = placement_data.get("commands", [])
        
        print(f"描述: {description}")
        print(f"總命令數: {len(commands)}")
        
        # 分離 add_component 和 connect_components 命令
        add_commands = []
        connect_commands = []
        
        for cmd in commands:
            cmd_type = cmd.get("type")
            if cmd_type == "add_component":
                add_commands.append(cmd)
            elif cmd_type == "connect_components":
                connect_commands.append(cmd)
        
        print(f"\n組件創建命令: {len(add_commands)} 個")
        print(f"連接命令: {len(connect_commands)} 個")
        
        # 設置並行工作線程數
        add_max_workers = min(max_workers, max(1, len(add_commands)))
        connect_max_workers = min(max_workers, max(1, len(connect_commands)))
        print(f"並行執行線程數: 組件創建={add_max_workers}, 連接={connect_max_workers}")
        
        # 執行所有 add_component 命令（並行）
        print("\n" + "=" * 80)
        print("階段 1: 創建組件（並行執行）")
        print("=" * 80)
        
        start_time = time.time()
        add_success, add_fail = self.component_manager.add_components_parallel(
            add_commands,
            max_workers=add_max_workers
        )
        add_time = time.time() - start_time
        
        print(f"\n組件創建完成: 成功 {add_success} 個，失敗 {add_fail} 個（耗時 {add_time:.2f} 秒）")
        print(f"組件 ID 映射: {len(self.component_manager.component_id_map)} 個")
        
        if add_fail > 0:
            print("\n⚠️  警告: 有組件創建失敗，連接可能會失敗")
            print("自動繼續執行連接命令...")
        
        # 保存組件 ID 映射
        if save_id_map:
            self.component_manager.save_id_map(id_map_path)
        
        # 執行所有 connect_components 命令（並行）
        print("\n" + "=" * 80)
        print("階段 2: 連接組件（並行執行）")
        print("=" * 80)
        
        start_time = time.time()
        connect_success, connect_fail = self.connection_manager.connect_components_parallel(
            connect_commands,
            max_workers=connect_max_workers
        )
        connect_time = time.time() - start_time
        
        print(f"\n連接完成: 成功 {connect_success} 個，失敗 {connect_fail} 個（耗時 {connect_time:.2f} 秒）")
        
        # 總結
        total_time = add_time + connect_time
        print("\n" + "=" * 80)
        print("執行總結")
        print("=" * 80)
        print(f"組件創建: {add_success}/{len(add_commands)} 成功（耗時 {add_time:.2f} 秒）")
        print(f"組件連接: {connect_success}/{len(connect_commands)} 成功（耗時 {connect_time:.2f} 秒）")
        print(f"總耗時: {total_time:.2f} 秒")
        
        success = (add_success == len(add_commands) and connect_success == len(connect_commands))
        
        if success:
            print("\n✓ 所有命令執行成功！")
        else:
            print("\n⚠️  部分命令執行失敗，請檢查錯誤信息。")
        
        return {
            "success": success,
            "add_success": add_success,
            "add_fail": add_fail,
            "connect_success": connect_success,
            "connect_fail": connect_fail,
            "add_time": add_time,
            "connect_time": connect_time,
            "total_time": total_time,
            "component_id_map_size": len(self.component_manager.component_id_map)
        }

