"""
Grasshopper MCP 通信客戶端

提供統一的 Grasshopper MCP 通信接口
"""

import socket
import json
from typing import Dict, Any, Optional
from threading import Lock


class GrasshopperClient:
    """Grasshopper MCP 通信客戶端"""
    
    def __init__(self, host: str = "localhost", port: int = 8080):
        """
        初始化 Grasshopper 客戶端
        
        Args:
            host: Grasshopper MCP 服務器地址
            port: Grasshopper MCP 服務器端口
        """
        self.host = host
        self.port = port
        self._print_lock = Lock()  # 線程安全的打印鎖
    
    def send_command(self, command_type: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        向 Grasshopper MCP 發送命令
        
        Args:
            command_type: 命令類型（如 "add_component", "connect_components"）
            params: 命令參數字典
        
        Returns:
            響應字典，包含 success 和 data/error 字段
        """
        if params is None:
            params = {}
        
        command = {
            "type": command_type,
            "parameters": params
        }
        
        try:
            # 連接到 Grasshopper MCP
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((self.host, self.port))
            
            # 發送命令
            command_json = json.dumps(command, ensure_ascii=False)
            client.sendall((command_json + "\n").encode("utf-8"))
            
            # 接收響應
            response_data = b""
            while True:
                chunk = client.recv(4096)
                if not chunk:
                    break
                response_data += chunk
                if response_data.endswith(b"\n"):
                    break
            
            # 處理可能的 BOM
            response_str = response_data.decode("utf-8-sig").strip()
            response = json.loads(response_str)
            client.close()
            return response
        except Exception as e:
            return {
                "success": False,
                "error": f"與 Grasshopper 通信時出錯: {str(e)}"
            }
    
    def safe_print(self, *args, **kwargs):
        """線程安全的打印函數"""
        with self._print_lock:
            print(*args, **kwargs)
    
    def extract_component_id(self, response: Dict[str, Any]) -> Optional[str]:
        """
        從響應中提取組件 ID
        
        Args:
            response: Grasshopper MCP 響應字典
        
        Returns:
            組件 ID 字符串，如果提取失敗則返回 None
        """
        if not response.get("success"):
            return None
        
        # 格式1: response.data.id
        data = response.get("data")
        if data and isinstance(data, dict):
            comp_id = data.get("id")
            if comp_id:
                return str(comp_id)
        
        # 格式2: response.result.id
        result = response.get("result")
        if result and isinstance(result, dict):
            comp_id = result.get("id")
            if comp_id:
                return str(comp_id)
        
        # 格式3: response.data 直接是 ID
        if data and isinstance(data, str):
            return data
        
        # 格式4: response.result 直接是 ID
        if result and isinstance(result, str):
            return result
        
        return None

