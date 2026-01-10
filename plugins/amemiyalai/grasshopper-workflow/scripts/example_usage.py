"""
Grasshopper Tools 使用範例

展示如何使用 grasshopper_tools 模組進行常見操作
"""

import sys
import os

# 添加父目錄到路徑，以便導入模組
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from grasshopper_tools import (
    GrasshopperClient,
    ComponentManager,
    ConnectionManager,
    ParameterSetter,
    GroupManager,
    MMDParser,
    JSONGenerator
)


def example_basic_usage():
    """基本使用範例"""
    print("=" * 80)
    print("基本使用範例")
    print("=" * 80)
    
    # 創建客戶端
    client = GrasshopperClient(host="localhost", port=8080)
    
    # 創建組件管理器
    comp_mgr = ComponentManager(client)
    
    # 創建一個 Number Slider
    print("\n1. 創建組件...")
    slider_id = comp_mgr.add_component(
        guid="e2bb9b8d-0d80-44e7-aa2d-2e446f5c61da",  # Number Slider GUID
        x=100,
        y=200,
        component_id="SLIDER_WIDTH"
    )
    
    if slider_id:
        print(f"   ✓ 組件創建成功，ID: {slider_id}")
        
        # 設置參數
        print("\n2. 設置參數...")
        param_setter = ParameterSetter(client, comp_mgr)
        if param_setter.set_slider(
            component_id_key="SLIDER_WIDTH",
            value="120.0",
            min_value=0.0,
            max_value=200.0,
            rounding=0.1
        ):
            print("   ✓ 參數設置成功")
    else:
        print("   ✗ 組件創建失敗")


def example_parse_mmd():
    """解析 MMD 文件範例"""
    print("=" * 80)
    print("解析 MMD 文件範例")
    print("=" * 80)
    
    mmd_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "component_info.mmd")
    
    if not os.path.exists(mmd_path):
        print(f"   ✗ 找不到文件: {mmd_path}")
        return
    
    # 解析 MMD 文件
    parser = MMDParser()
    components, connections = parser.parse_component_info_mmd(mmd_path)
    
    print(f"\n找到 {len(components)} 個組件")
    print(f"找到 {len(connections)} 個連接")
    
    # 提取 subgraph
    subgraphs = parser.parse_subgraphs_from_mmd(mmd_path)
    subgraph_names = parser.get_subgraph_names(mmd_path)
    
    print(f"\n找到 {len(subgraphs)} 個 subgraph:")
    for sg_id, comp_ids in subgraphs.items():
        sg_name = subgraph_names.get(sg_id, sg_id)
        print(f"  {sg_name}: {len(comp_ids)} 個組件")
    
    # 提取 slider 值
    sliders = parser.parse_slider_values(mmd_path)
    print(f"\n找到 {len(sliders)} 個 Number Slider:")
    for comp_id, info in list(sliders.items())[:5]:  # 只顯示前5個
        print(f"  {comp_id}: {info['value']}")


def example_generate_json():
    """生成 JSON 文件範例"""
    print("=" * 80)
    print("生成 JSON 文件範例")
    print("=" * 80)
    
    mmd_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "component_info.mmd")
    
    if not os.path.exists(mmd_path):
        print(f"   ✗ 找不到文件: {mmd_path}")
        return
    
    # 解析 MMD 文件
    parser = MMDParser()
    components, connections = parser.parse_component_info_mmd(mmd_path)
    
    # 生成 JSON
    generator = JSONGenerator()
    placement_info = generator.generate_placement_info(
        components,
        connections,
        description="桌子創建執行序列 - 自動生成"
    )
    
    # 保存到文件
    output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "placement_info_generated.json")
    generator.save_placement_info(placement_info, output_path)
    
    print(f"\n已生成 {len(placement_info['commands'])} 個命令")
    print(f"  組件創建命令: {len([c for c in placement_info['commands'] if c.get('type') == 'add_component'])}")
    print(f"  連接命令: {len([c for c in placement_info['commands'] if c.get('type') == 'connect_components'])}")


def example_full_workflow():
    """完整工作流程範例（需要 Grasshopper MCP 服務器運行）"""
    print("=" * 80)
    print("完整工作流程範例")
    print("=" * 80)
    print("\n注意：此範例需要 Grasshopper MCP 服務器運行")
    print("如果服務器未運行，此範例將失敗\n")
    
    try:
        # 1. 解析 MMD 文件
        mmd_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "component_info.mmd")
        if not os.path.exists(mmd_path):
            print(f"   ✗ 找不到文件: {mmd_path}")
            return
        
        parser = MMDParser()
        components, connections = parser.parse_component_info_mmd(mmd_path)
        
        # 2. 創建客戶端和管理器
        client = GrasshopperClient()
        comp_mgr = ComponentManager(client)
        ConnectionManager(client, comp_mgr)
        ParameterSetter(client, comp_mgr)
        GroupManager(client, comp_mgr)
        
        # 3. 創建組件（只創建前3個作為範例）
        print("\n3. 創建組件（範例：前3個）...")
        add_commands = [
            {
                "guid": comp["guid"],
                "x": comp["x"],
                "y": comp["y"],
                "componentId": comp["componentId"]
            }
            for comp in components[:3]
        ]
        success, fail = comp_mgr.add_components_parallel(add_commands, max_workers=3)
        print(f"   成功: {success}, 失敗: {fail}")
        
        # 4. 保存 ID 映射
        comp_mgr.save_id_map()
        
        print("\n完整工作流程範例完成！")
        print("（實際使用時，請創建所有組件和連接）")
        
    except Exception as e:
        print(f"\n錯誤: {e}")
        print("（可能是 Grasshopper MCP 服務器未運行）")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("Grasshopper Tools 使用範例")
    print("=" * 80)
    
    # 範例 1: 基本使用（需要服務器運行）
    # example_basic_usage()
    
    # 範例 2: 解析 MMD 文件（不需要服務器）
    example_parse_mmd()
    
    # 範例 3: 生成 JSON 文件（不需要服務器）
    example_generate_json()
    
    # 範例 4: 完整工作流程（需要服務器運行）
    # example_full_workflow()
    
    print("\n" + "=" * 80)
    print("範例執行完成")
    print("=" * 80)

