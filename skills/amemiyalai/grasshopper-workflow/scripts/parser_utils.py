"""
MMD/JSON 解析工具

提供從 MMD 文件解析組件和連接信息，以及生成 JSON 格式的功能
"""

import re
import json
from typing import Dict, List, Tuple, Optional, Any


class MMDParser:
    """MMD 文件解析器"""
    
    def __init__(self):
        """初始化 MMD 解析器"""
        # GUID 映射（所有組件的正確 GUID）
        self.guid_map = {
            # 桌面模組
            "AVERAGE_LEG_X": "3e0451ca-da24-452d-a6b1-a6877453d4e4",  # Average
            "AVERAGE_LEG_Y": "3e0451ca-da24-452d-a6b1-a6877453d4e4",  # Average
            "SLIDER_TOP_Z": "e2bb9b8d-0d80-44e7-aa2d-2e446f5c61da",  # Number Slider
            "CONSTRUCT_POINT_CENTER": "9dceff86-6201-4c8e-90b1-706ad5bc3d49",  # Construct Point
            "XY_PLANE_TOP": "a896f6c1-dd6c-4830-88f2-44808c07dc10",  # XY Plane
            "SLIDER_WIDTH": "e2bb9b8d-0d80-44e7-aa2d-2e446f5c61da",  # Number Slider
            "SLIDER_LENGTH": "e2bb9b8d-0d80-44e7-aa2d-2e446f5c61da",  # Number Slider
            "SLIDER_TOP_HEIGHT": "e2bb9b8d-0d80-44e7-aa2d-2e446f5c61da",  # Number Slider
            "CONSTANT_2": "e2bb9b8d-0d80-44e7-aa2d-2e446f5c61da",  # Number Slider
            "DIVISION_X": "7ed9789a-7403-4eeb-9716-d6e5681f4136",  # Division
            "DIVISION_Y": "7ed9789a-7403-4eeb-9716-d6e5681f4136",  # Division
            "DIVISION_Z": "7ed9789a-7403-4eeb-9716-d6e5681f4136",  # Division
            "CENTER_BOX_TOP": "e1f83fb4-efe0-4f10-8c20-4b38df56b36c",  # Center Box
            # 桌腳基礎模組
            "XY_PLANE_LEG_BASE": "a896f6c1-dd6c-4830-88f2-44808c07dc10",  # XY Plane
            "SLIDER_RADIUS_LEG": "e2bb9b8d-0d80-44e7-aa2d-2e446f5c61da",  # Number Slider
            "CIRCLE_LEG_BASE": "40dda121-a31b-421b-94b0-e46f5774f98e",  # Circle
            "BOUNDARY_SURFACES_LEG_BASE": "9ec27fcf-b30f-4ad2-b2d1-c1934c32f855",  # Boundary Surfaces
            "SLIDER_LEG_HEIGHT": "e2bb9b8d-0d80-44e7-aa2d-2e446f5c61da",  # Number Slider
            "UNIT_Z": "9428ce3a-b2a0-4c8f-832a-8ad2b81a9743",  # Unit Z
            "AMPLITUDE_LEG_BASE": "7b93e28d-6191-425a-844e-6e9e4127dd6b",  # Amplitude
            "EXTRUDE_LEG_BASE": "1c5e4c65-5f57-432c-96d3-53563470ab51",  # Extrude
            # 桌腳位置平面模組
            "XY_PLANE_LEG_REF": "a896f6c1-dd6c-4830-88f2-44808c07dc10",  # XY Plane
            "SLIDER_LEG1_X": "e2bb9b8d-0d80-44e7-aa2d-2e446f5c61da",  # Number Slider
            "SLIDER_LEG1_Y": "e2bb9b8d-0d80-44e7-aa2d-2e446f5c61da",  # Number Slider
            "SLIDER_LEG1_Z": "e2bb9b8d-0d80-44e7-aa2d-2e446f5c61da",  # Number Slider
            "SLIDER_LEG2_X": "e2bb9b8d-0d80-44e7-aa2d-2e446f5c61da",  # Number Slider
            "SLIDER_LEG2_Y": "e2bb9b8d-0d80-44e7-aa2d-2e446f5c61da",  # Number Slider
            "SLIDER_LEG2_Z": "e2bb9b8d-0d80-44e7-aa2d-2e446f5c61da",  # Number Slider
            "SLIDER_LEG3_X": "e2bb9b8d-0d80-44e7-aa2d-2e446f5c61da",  # Number Slider
            "SLIDER_LEG3_Y": "e2bb9b8d-0d80-44e7-aa2d-2e446f5c61da",  # Number Slider
            "SLIDER_LEG3_Z": "e2bb9b8d-0d80-44e7-aa2d-2e446f5c61da",  # Number Slider
            "SLIDER_LEG4_X": "e2bb9b8d-0d80-44e7-aa2d-2e446f5c61da",  # Number Slider
            "SLIDER_LEG4_Y": "e2bb9b8d-0d80-44e7-aa2d-2e446f5c61da",  # Number Slider
            "SLIDER_LEG4_Z": "e2bb9b8d-0d80-44e7-aa2d-2e446f5c61da",  # Number Slider
            "VECTOR_LEG1": "d3116726-7a3e-4089-b3e2-216b266a1245",  # Vector XYZ
            "VECTOR_LEG2": "d3116726-7a3e-4089-b3e2-216b266a1245",  # Vector XYZ
            "VECTOR_LEG3": "d3116726-7a3e-4089-b3e2-216b266a1245",  # Vector XYZ
            "VECTOR_LEG4": "d3116726-7a3e-4089-b3e2-216b266a1245",  # Vector XYZ
            "MOVE_PLANE_LEG1": "6af48ec9-decb-4ad7-81ac-cd20452189a2",  # Move
            "MOVE_PLANE_LEG2": "6af48ec9-decb-4ad7-81ac-cd20452189a2",  # Move
            "MOVE_PLANE_LEG3": "6af48ec9-decb-4ad7-81ac-cd20452189a2",  # Move
            "MOVE_PLANE_LEG4": "6af48ec9-decb-4ad7-81ac-cd20452189a2",  # Move
            # Orient 複製組
            "ORIENT_LEG1": "b08eae6f-0030-4f63-be06-9f1c7f89efd1",  # Orient
            "ORIENT_LEG2": "b08eae6f-0030-4f63-be06-9f1c7f89efd1",  # Orient
            "ORIENT_LEG3": "b08eae6f-0030-4f63-be06-9f1c7f89efd1",  # Orient
            "ORIENT_LEG4": "b08eae6f-0030-4f63-be06-9f1c7f89efd1",  # Orient
            # 最終合併
            "BOOLEAN_UNION": "cabe86d9-6ef0-4037-90bd-01a02e0d30f0",  # Solid Union
        }
    
    def parse_component_info_mmd(self, file_path: str) -> Tuple[List[Dict], List[Dict]]:
        """
        解析 component_info.mmd 文件，提取組件和連接信息
        
        Args:
            file_path: MMD 文件路徑
        
        Returns:
            (組件列表, 連接列表) 元組
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        components = []
        connections = []
        
        # 提取組件定義
        # 格式: COMPONENT_NAME["描述<br/>...<br/>GUID: xxx<br/>位置: X=xxx, Y=xxx"]
        component_pattern = r'(\w+)\["([^"]+)"\]'
        
        for match in re.finditer(component_pattern, content):
            component_id = match.group(1)
            component_desc = match.group(2)
            
            # 提取 GUID
            guid_match = re.search(r'GUID:\s*([a-f0-9-]+|需要查詢實際GUID)', component_desc)
            if guid_match:
                guid = guid_match.group(1)
                if guid == "需要查詢實際GUID" or component_id in self.guid_map:
                    guid = self.guid_map.get(component_id, guid)
                    if not guid or guid == "需要查詢實際GUID":
                        print(f"警告: {component_id} 的 GUID 未找到")
                        continue
            else:
                if component_id in self.guid_map:
                    guid = self.guid_map[component_id]
                else:
                    print(f"警告: {component_id} 未找到 GUID")
                    continue
            
            # 提取位置
            pos_match = re.search(r'位置:\s*X=(\d+),\s*Y=(\d+)', component_desc)
            if pos_match:
                x = int(pos_match.group(1))
                y = int(pos_match.group(2))
            else:
                print(f"警告: {component_id} 未找到位置信息")
                continue
            
            components.append({
                "componentId": component_id,
                "guid": guid,
                "x": x,
                "y": y,
                "description": component_desc
            })
        
        # 提取連接關係
        # 格式: SOURCE -->|"ParamName"| TARGET
        connection_pattern = r'(\w+)\s*-->\|"([^"]+)"\|\s*(\w+)'
        
        for match in re.finditer(connection_pattern, content):
            source_id = match.group(1)
            param_name = match.group(2)
            target_id = match.group(3)
            
            # 根據參數名稱確定 sourceParam 和 targetParam
            source_param, target_param = self._determine_params(source_id, target_id, param_name)
            
            connections.append({
                "sourceId": source_id,
                "sourceParam": source_param,
                "targetId": target_id,
                "targetParam": target_param
            })
        
        return components, connections
    
    def _determine_params(self, source_id: str, target_id: str, param_name: str) -> Tuple[str, str]:
        """
        根據組件類型和參數名稱確定 sourceParam 和 targetParam
        
        Args:
            source_id: 源組件 ID
            target_id: 目標組件 ID
            param_name: 參數名稱
        
        Returns:
            (sourceParam, targetParam) 元組
        """
        source_param = param_name
        target_param = param_name
        
        # 特殊處理邏輯（簡化版，完整邏輯可參考 generate_placement_info.py）
        if "Number" in param_name:
            source_param = "Number"
            if "AVERAGE" in target_id:
                target_param = "Input"
            elif "DIVISION" in target_id:
                if "SLIDER" in source_id or "CONSTANT" in source_id:
                    target_param = "A" if "SLIDER" in source_id else "B"
                else:
                    target_param = "Number"
            else:
                target_param = "Number"
        elif "Plane" in param_name:
            source_param = "Plane"
            if "CIRCLE" in target_id:
                target_param = "Plane"
            elif "CENTER_BOX" in target_id:
                target_param = "Base"
            else:
                target_param = "Plane"
        elif "Vector" in param_name:
            source_param = "Vector"
            if "MOVE" in target_id:
                target_param = "Motion"
            elif "EXTRUDE" in target_id:
                target_param = "Direction"
            else:
                target_param = "Vector"
        
        # Division 輸出的特殊處理
        if source_id in ["DIVISION_X", "DIVISION_Y", "DIVISION_Z"]:
            source_param = "Result"
            if target_id == "CENTER_BOX_TOP":
                if source_id == "DIVISION_X":
                    target_param = "X"
                elif source_id == "DIVISION_Y":
                    target_param = "Y"
                elif source_id == "DIVISION_Z":
                    target_param = "Z"
        
        # Circle 輸入的特殊處理
        if target_id == "CIRCLE_LEG_BASE":
            if source_id == "XY_PLANE_LEG_BASE":
                target_param = "Plane"
            elif source_id == "SLIDER_RADIUS_LEG":
                target_param = "Radius"
        
        return source_param, target_param
    
    def parse_subgraphs_from_mmd(self, file_path: str) -> Dict[str, List[str]]:
        """
        解析 component_info.mmd，提取所有 subgraph 及其組件
        
        Args:
            file_path: MMD 文件路徑
        
        Returns:
            subgraph ID 到組件 ID 列表的映射
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        subgraphs: Dict[str, List[str]] = {}
        current_subgraph: Optional[str] = None
        current_components: List[str] = []
        
        lines = content.split('\n')
        in_subgraph = False
        
        for line in lines:
            # 匹配 subgraph 開始：subgraph ID["名稱"]
            subgraph_start = re.match(r'\s*subgraph\s+(\w+)\["([^"]+)"\]', line)
            if subgraph_start:
                # 保存上一個 subgraph
                if current_subgraph:
                    subgraphs[current_subgraph] = current_components.copy()
                
                current_subgraph = subgraph_start.group(1)
                current_components = []
                in_subgraph = True
                continue
            
            # 匹配 subgraph 結束
            if line.strip() == "end" and in_subgraph:
                if current_subgraph:
                    subgraphs[current_subgraph] = current_components.copy()
                current_subgraph = None
                current_components = []
                in_subgraph = False
                continue
            
            # 在 subgraph 內，匹配組件定義：COMPONENT_NAME["描述..."]
            if in_subgraph:
                component_match = re.search(r'(\w+)\["', line)
                if component_match:
                    component_id = component_match.group(1)
                    # 跳過註釋行
                    if not line.strip().startswith("%%"):
                        current_components.append(component_id)
        
        # 處理最後一個 subgraph
        if current_subgraph and current_components:
            subgraphs[current_subgraph] = current_components
        
        return subgraphs
    
    def get_subgraph_names(self, file_path: str) -> Dict[str, str]:
        """
        獲取 subgraph ID 到名稱的映射
        
        Args:
            file_path: MMD 文件路徑
        
        Returns:
            subgraph ID 到名稱的映射
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        subgraph_names = {}
        
        # 匹配 subgraph ID["名稱"]
        pattern = r'subgraph\s+(\w+)\["([^"]+)"\]'
        for match in re.finditer(pattern, content):
            subgraph_id = match.group(1)
            subgraph_name = match.group(2)
            subgraph_names[subgraph_id] = subgraph_name
        
        return subgraph_names
    
    def parse_slider_values(self, file_path: str) -> Dict[str, Dict]:
        """
        解析 component_info.mmd，提取所有 Number Slider 的值
        
        Args:
            file_path: MMD 文件路徑
        
        Returns:
            組件 ID 到 slider 信息的映射
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        sliders = {}
        
        # 匹配組件定義：COMPONENT_NAME["描述<br/>输出: 值<br/>..."]
        pattern = r'(\w+)\["([^"]+)"\]'
        
        for match in re.finditer(pattern, content):
            component_id = match.group(1)
            description = match.group(2)
            
            # 提取輸出值（如果是 Number Slider）
            if "Number Slider" in description:
                # 查找 "输出: 值" 模式
                value_match = re.search(r'输出:\s*([-\d.]+)', description)
                if value_match:
                    value = value_match.group(1)
                    sliders[component_id] = {
                        "type": "Number Slider",
                        "value": value,
                        "description": description
                    }
        
        return sliders


class JSONGenerator:
    """JSON 生成器"""
    
    @staticmethod
    def generate_placement_info(components: List[Dict[str, Any]], connections: List[Dict[str, Any]], description: str = "自動生成") -> Dict[str, Any]:
        """
        生成 placement_info.json 結構
        
        Args:
            components: 組件列表
            connections: 連接列表
            description: 描述信息
        
        Returns:
            placement_info 字典
        """
        commands: List[Dict[str, Any]] = []
        
        # 按模組分組添加組件
        desktop_components = ["AVERAGE_LEG_X", "AVERAGE_LEG_Y", "SLIDER_TOP_Z", "CONSTRUCT_POINT_CENTER", 
                             "XY_PLANE_TOP", "SLIDER_WIDTH", "SLIDER_LENGTH", "SLIDER_TOP_HEIGHT", 
                             "CONSTANT_2", "DIVISION_X", "DIVISION_Y", "DIVISION_Z", "CENTER_BOX_TOP"]
        
        leg_base_components = ["XY_PLANE_LEG_BASE", "SLIDER_RADIUS_LEG", "CIRCLE_LEG_BASE", 
                               "BOUNDARY_SURFACES_LEG_BASE", "SLIDER_LEG_HEIGHT", "UNIT_Z", 
                               "AMPLITUDE_LEG_BASE", "EXTRUDE_LEG_BASE"]
        
        leg_planes_components = ["XY_PLANE_LEG_REF", "SLIDER_LEG1_X", "SLIDER_LEG1_Y", "SLIDER_LEG1_Z",
                                 "SLIDER_LEG2_X", "SLIDER_LEG2_Y", "SLIDER_LEG2_Z",
                                 "SLIDER_LEG3_X", "SLIDER_LEG3_Y", "SLIDER_LEG3_Z",
                                 "SLIDER_LEG4_X", "SLIDER_LEG4_Y", "SLIDER_LEG4_Z",
                                 "VECTOR_LEG1", "VECTOR_LEG2", "VECTOR_LEG3", "VECTOR_LEG4",
                                 "MOVE_PLANE_LEG1", "MOVE_PLANE_LEG2", "MOVE_PLANE_LEG3", "MOVE_PLANE_LEG4"]
        
        orient_components = ["ORIENT_LEG1", "ORIENT_LEG2", "ORIENT_LEG3", "ORIENT_LEG4"]
        
        final_components = ["BOOLEAN_UNION"]
        
        # 創建組件ID到組件信息的映射
        component_map = {comp["componentId"]: comp for comp in components}
        
        # 按順序添加組件
        commands.append({"comment": "=== 桌面模組 ==="})
        for comp_id in desktop_components:
            if comp_id in component_map:
                comp = component_map[comp_id]
                commands.append({
                    "comment": f"{comp_id}",
                    "type": "add_component",
                    "parameters": {
                        "guid": comp["guid"],
                        "x": comp["x"],
                        "y": comp["y"]
                    },
                    "componentId": comp_id
                })
        
        commands.append({"comment": "=== 桌腳基礎模組 ==="})
        for comp_id in leg_base_components:
            if comp_id in component_map:
                comp = component_map[comp_id]
                commands.append({
                    "comment": f"{comp_id}",
                    "type": "add_component",
                    "parameters": {
                        "guid": comp["guid"],
                        "x": comp["x"],
                        "y": comp["y"]
                    },
                    "componentId": comp_id
                })
        
        commands.append({"comment": "=== 桌腳位置平面模組 ==="})
        for comp_id in leg_planes_components:
            if comp_id in component_map:
                comp = component_map[comp_id]
                commands.append({
                    "comment": f"{comp_id}",
                    "type": "add_component",
                    "parameters": {
                        "guid": comp["guid"],
                        "x": comp["x"],
                        "y": comp["y"]
                    },
                    "componentId": comp_id
                })
        
        commands.append({"comment": "=== Orient 複製組 ==="})
        for comp_id in orient_components:
            if comp_id in component_map:
                comp = component_map[comp_id]
                commands.append({
                    "comment": f"{comp_id}",
                    "type": "add_component",
                    "parameters": {
                        "guid": comp["guid"],
                        "x": comp["x"],
                        "y": comp["y"]
                    },
                    "componentId": comp_id
                })
        
        commands.append({"comment": "=== 最終合併 ==="})
        for comp_id in final_components:
            if comp_id in component_map:
                comp = component_map[comp_id]
                commands.append({
                    "comment": f"{comp_id}",
                    "type": "add_component",
                    "parameters": {
                        "guid": comp["guid"],
                        "x": comp["x"],
                        "y": comp["y"]
                    },
                    "componentId": comp_id
                })
        
        # 添加連接命令
        commands.append({"comment": "=== 連接命令 ==="})
        for conn in connections:
            commands.append({
                "comment": f"{conn['sourceId']} -> {conn['targetId']}",
                "type": "connect_components",
                "parameters": {
                    "sourceId": conn["sourceId"],
                    "sourceParam": conn["sourceParam"],
                    "targetId": conn["targetId"],
                    "targetParam": conn["targetParam"]
                }
            })
        
        return {
            "description": description,
            "commands": commands
        }
    
    @staticmethod
    def save_placement_info(placement_info: Dict[str, Any], file_path: str):
        """
        保存 placement_info 到 JSON 文件
        
        Args:
            placement_info: placement_info 字典
            file_path: 保存路徑
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(placement_info, f, indent=2, ensure_ascii=False)
        print(f"已生成 {file_path}")

