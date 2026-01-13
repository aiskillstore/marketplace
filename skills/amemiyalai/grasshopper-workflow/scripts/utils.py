"""
通用工具函數
"""

import os
import json
from typing import Dict, Optional, Tuple


def load_component_id_map(file_path: Optional[str] = None) -> Optional[Dict[str, str]]:
    """
    從文件加載組件 ID 映射
    
    Args:
        file_path: 組件 ID 映射文件路徑，如果為 None 則使用默認路徑
    
    Returns:
        組件 ID 映射字典，如果文件不存在則返回 None
    """
    if file_path is None:
        # 默認路徑：當前腳本目錄下的 component_id_map.json
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, "..", "component_id_map.json")
    
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"讀取組件 ID 映射文件失敗: {e}")
            return None
    return None


def save_component_id_map(component_id_map: Dict[str, str], file_path: Optional[str] = None):
    """
    保存組件 ID 映射到文件
    
    Args:
        component_id_map: 組件 ID 映射字典
        file_path: 保存路徑，如果為 None 則使用默認路徑
    """
    if file_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, "..", "component_id_map.json")
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(component_id_map, f, indent=2, ensure_ascii=False)
        print(f"組件 ID 映射已保存到: {file_path}")
    except Exception as e:
        print(f"保存組件 ID 映射失敗: {e}")


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """
    將十六進制顏色轉換為 RGB
    
    Args:
        hex_color: 十六進制顏色字符串（如 "#FF0000" 或 "FF0000"）
    
    Returns:
        RGB 元組 (r, g, b)
    """
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (r, g, b)


def determine_slider_range(slider_name: str, value: float) -> Tuple[float, float]:
    """
    根據 slider 名稱和值確定合理的範圍
    
    Args:
        slider_name: Slider 名稱
        value: Slider 值
    
    Returns:
        (最小值, 最大值) 元組
    """
    value_abs = abs(float(value))
    
    if "WIDTH" in slider_name or "LENGTH" in slider_name:
        return (0.0, max(200.0, value_abs * 2))
    elif "HEIGHT" in slider_name or "TOP_Z" in slider_name:
        return (0.0, max(200.0, value_abs * 2))
    elif "RADIUS" in slider_name:
        return (0.0, max(50.0, value_abs * 2))
    elif "LEG" in slider_name and ("X" in slider_name or "Y" in slider_name or "Z" in slider_name):
        # 桌腳位置 slider
        return (-100.0, 100.0)
    elif "CONSTANT" in slider_name:
        return (0.0, 10.0)
    else:
        # 默認範圍
        return (0.0, max(200.0, value_abs * 2))


def load_placement_info(json_path: str) -> Optional[Dict]:
    """
    讀取 placement_info.json 文件
    
    Args:
        json_path: JSON 文件路徑
    
    Returns:
        placement_info 字典，如果讀取失敗則返回 None
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"✗ 錯誤: 找不到文件 {json_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"✗ 錯誤: JSON 解析失敗: {e}")
        return None
    except Exception as e:
        print(f"✗ 錯誤: 讀取文件失敗: {e}")
        return None


def update_guids_in_json(json_path: str, guid_map: Dict[str, str]) -> int:
    """
    更新 JSON 文件中的 GUID
    
    Args:
        json_path: JSON 文件路徑
        guid_map: 舊 GUID 到新 GUID 的映射字典
    
    Returns:
        更新的 GUID 數量
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"讀取文件失敗: {e}")
        return 0
    
    updated_count = 0
    
    # 更新所有命令中的 GUID
    for command in data.get("commands", []):
        if command.get("type") == "add_component":
            params = command.get("parameters", {})
            old_guid = params.get("guid")
            if old_guid in guid_map:
                new_guid = guid_map[old_guid]
                params["guid"] = new_guid
                updated_count += 1
                comment = command.get("comment", "無註釋")
                print(f"更新: {comment} - {old_guid[:8]}... -> {new_guid[:8]}...")
    
    # 保存更新後的文件
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n總共更新了 {updated_count} 個 GUID")
        return updated_count
    except Exception as e:
        print(f"保存文件失敗: {e}")
        return updated_count


# 預設的 GUID 映射（從 update_guids.py）
DEFAULT_GUID_MAP = {
    # XY Plane
    "6301d658-592f-47d0-ae0d-ad3c183a7ea5": "3b92ebc0-d8e1-425b-9541-a9e635f8521f",
    # Number Slider
    "f9abdb91-05f7-4363-8fd2-174b73a276f3": "8c483c8a-a808-420e-821b-96d5f91acfbc",
    # Rectangle (非廢棄版本)
    "bfc1a6aa-9419-47a1-9f3c-72ead30e5dba": "124e50ef-cb25-40c6-89e4-e89541fddd05",
    # Boundary Surfaces
    "bd99f010-73ab-406c-a31d-06cebf1de76a": "fa6bf1bb-89db-4a81-9941-f842098f6909",
    # Unit Z
    "2f810738-45fb-4180-93d1-2c51159ca73e": "8b54aad7-22c4-4316-9cb1-d5b9a0547f19",
    # Amplitude
    "3dd1c715-c864-44ee-afe2-9a0949093bc4": "9e0f3325-bfdc-4b99-9f63-fb0acac5feb6",
    # Extrude
    "2e85a786-1079-4c66-ab54-c2c349eda72b": "6d3702b6-9353-48e7-85e7-324f902cca6a",
    # Circle
    "d41d8868-cb0c-4cb6-b27e-4ef060d8e0a3": "c2bcb3ce-b7d0-4e1e-a737-a19dc15dc8ef",
    # Move (非廢棄版本)
    "c6141da0-066b-4b4f-8126-6a89f1ee3540": "23d06d72-b526-4384-bdee-8d2b0b3454e6",
    # Orient (非廢棄版本)
    "0a481cb8-e51c-4804-a4a0-78bbbf266c08": "0cbc1505-8788-410a-806c-3ae7a34cbfd1",
    # Boolean Union (Solid Union)
    "3e49ea32-3fae-4cc4-8f85-5233688b7fe6": "3b2a23fe-d1dd-421c-b98f-7a486c504094",
    # Vector XYZ
    "c7871aa7-f30c-4a23-8a34-559b62940c88": "01c5a8b8-bd79-4a45-9ad3-7330b9de1d48",
}

