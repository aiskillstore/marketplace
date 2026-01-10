"""
Grasshopper Tools 命令行接口 (CLI)

提供命令行方式使用所有工具功能
"""

import argparse
import sys
import os
import json

# 添加當前目錄到路徑，以便導入模組
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# 導入模組（使用相對導入）
try:
    from . import (
        GrasshopperClient,
        ComponentManager,
        ConnectionManager,
        ParameterSetter,
        GroupManager,
        MMDParser,
        JSONGenerator,
        PlacementExecutor,
        load_placement_info,
        update_guids_in_json,
        DEFAULT_GUID_MAP,
    )
except ImportError:
    # 如果相對導入失敗，嘗試絕對導入（當作為腳本直接運行時）
    try:
        from grasshopper_tools import (
            GrasshopperClient,
            ComponentManager,
            ConnectionManager,
            ParameterSetter,
            GroupManager,
            MMDParser,
            JSONGenerator,
            PlacementExecutor,
            load_placement_info,
            update_guids_in_json,
            DEFAULT_GUID_MAP,
        )
    except ImportError:
        # 最後嘗試：添加當前目錄的父目錄到路徑
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "grasshopper_tools",
            os.path.join(current_dir, "__init__.py")
        )
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            sys.modules["grasshopper_tools"] = module
            spec.loader.exec_module(module)
            GrasshopperClient = module.GrasshopperClient
            ComponentManager = module.ComponentManager
            ConnectionManager = module.ConnectionManager
            ParameterSetter = module.ParameterSetter
            GroupManager = module.GroupManager
            MMDParser = module.MMDParser
            JSONGenerator = module.JSONGenerator
            PlacementExecutor = module.PlacementExecutor
            load_placement_info = module.load_placement_info
            update_guids_in_json = module.update_guids_in_json
            DEFAULT_GUID_MAP = module.DEFAULT_GUID_MAP
        else:
            raise ImportError("無法導入 grasshopper_tools 模組")


def cmd_execute_placement(args):
    """執行 placement_info.json"""
    executor = PlacementExecutor()
    result = executor.execute_placement_info(
        json_path=args.json_path,
        max_workers=args.max_workers,
        save_id_map=args.save_id_map
    )
    
    if result["success"]:
        print("\n✓ 所有命令執行成功！")
        sys.exit(0)
    else:
        print("\n⚠️  部分命令失敗")
        sys.exit(1)


def cmd_parse_mmd(args):
    """解析 MMD 文件"""
    parser = MMDParser()
    
    if args.action == "components":
        components, connections = parser.parse_component_info_mmd(args.mmd_path)
        print(f"找到 {len(components)} 個組件")
        print(f"找到 {len(connections)} 個連接")
        
        if args.output:
            data = {
                "components": components,
                "connections": connections
            }
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"已保存到: {args.output}")
    
    elif args.action == "subgraphs":
        subgraphs = parser.parse_subgraphs_from_mmd(args.mmd_path)
        subgraph_names = parser.get_subgraph_names(args.mmd_path)
        
        print(f"找到 {len(subgraphs)} 個 subgraph:")
        for sg_id, comp_ids in subgraphs.items():
            sg_name = subgraph_names.get(sg_id, sg_id)
            print(f"  {sg_name}: {len(comp_ids)} 個組件")
        
        if args.output:
            data = {
                "subgraphs": {sg_id: comp_ids for sg_id, comp_ids in subgraphs.items()},
                "subgraph_names": subgraph_names
            }
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"已保存到: {args.output}")
    
    elif args.action == "sliders":
        sliders = parser.parse_slider_values(args.mmd_path)
        print(f"找到 {len(sliders)} 個 Number Slider:")
        for comp_id, info in sliders.items():
            print(f"  {comp_id}: {info['value']}")
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(sliders, f, indent=2, ensure_ascii=False)
            print(f"已保存到: {args.output}")


def cmd_generate_json(args):
    """生成 placement_info.json"""
    parser = MMDParser()
    components, connections = parser.parse_component_info_mmd(args.mmd_path)
    
    generator = JSONGenerator()
    placement_info = generator.generate_placement_info(
        components,
        connections,
        description=args.description
    )
    
    generator.save_placement_info(placement_info, args.output)
    print(f"已生成 {len(placement_info['commands'])} 個命令")


def cmd_update_guids(args):
    """更新 JSON 文件中的 GUID"""
    guid_map = DEFAULT_GUID_MAP
    if args.guid_map:
        with open(args.guid_map, 'r', encoding='utf-8') as f:
            guid_map = json.load(f)
    
    updated_count = update_guids_in_json(args.json_path, guid_map)
    print(f"總共更新了 {updated_count} 個 GUID")


def cmd_add_component(args):
    """創建組件"""
    comp_mgr = ComponentManager()
    component_id = comp_mgr.add_component(
        guid=args.guid,
        x=args.x,
        y=args.y,
        component_id=args.component_id
    )
    
    if component_id:
        print(f"✓ 組件創建成功，ID: {component_id}")
        if args.component_id:
            comp_mgr.save_id_map()
    else:
        print("✗ 組件創建失敗")
        sys.exit(1)


def cmd_delete_component(args):
    """刪除組件"""
    comp_mgr = ComponentManager()
    if comp_mgr.delete_component(args.component_id):
        print("✓ 組件刪除成功")
    else:
        print("✗ 組件刪除失敗")
        sys.exit(1)


def cmd_query_guid(args):
    """查詢組件 GUID"""
    comp_mgr = ComponentManager()
    result = comp_mgr.get_component_guid(args.component_name)
    
    if result:
        print(f"組件名稱: {result['name']}")
        print(f"GUID: {result['guid']}")
        print(f"類別: {result['category']}")
        print(f"內置組件: {result['isBuiltIn']}")
    else:
        print(f"✗ 未找到組件: {args.component_name}")
        sys.exit(1)


def cmd_connect_components(args):
    """連接組件"""
    comp_mgr = ComponentManager()
    conn_mgr = ConnectionManager(component_manager=comp_mgr)
    
    success = conn_mgr.connect_components(
        source_id="",
        target_id="",
        source_param=args.source_param,
        target_param=args.target_param,
        source_id_key=args.source_id,
        target_id_key=args.target_id
    )
    
    if success:
        print("✓ 連接成功")
    else:
        print("✗ 連接失敗")
        sys.exit(1)


def cmd_set_slider(args):
    """設置 Slider"""
    comp_mgr = ComponentManager()
    param_setter = ParameterSetter(component_manager=comp_mgr)
    
    success = param_setter.set_slider(
        component_id_key=args.component_id,
        value=args.value,
        min_value=args.min_value,
        max_value=args.max_value,
        rounding=args.rounding
    )
    
    if success:
        print("✓ Slider 設置成功")
    else:
        print("✗ Slider 設置失敗")
        sys.exit(1)


def cmd_set_vector(args):
    """設置 Vector XYZ"""
    comp_mgr = ComponentManager()
    param_setter = ParameterSetter(component_manager=comp_mgr)
    
    success = param_setter.set_vector_xyz(
        component_id_key=args.component_id,
        x=args.x,
        y=args.y,
        z=args.z
    )
    
    if success:
        print("✓ Vector XYZ 設置成功")
    else:
        print("✗ Vector XYZ 設置失敗")
        sys.exit(1)


def cmd_group_components(args):
    """創建群組"""
    comp_mgr = ComponentManager()
    group_mgr = GroupManager(component_manager=comp_mgr)
    
    # 解析組件 ID 列表
    component_ids = args.component_ids.split(',') if args.component_ids else []
    
    # 處理顏色
    color = None
    if args.color:
        r, g, b = map(int, args.color.split(','))
        color = (r, g, b)
    
    success = group_mgr.group_components(
        component_ids=[],
        group_name=args.group_name,
        color=color,
        color_hex=args.color_hex,
        component_id_keys=component_ids
    )
    
    if success:
        print("✓ 群組創建成功")
    else:
        print("✗ 群組創建失敗")
        sys.exit(1)


def cmd_get_errors(args):
    """獲取文檔錯誤"""
    conn_mgr = ConnectionManager()
    errors = conn_mgr.get_document_errors()
    
    print(f"找到 {len(errors)} 個錯誤:")
    for i, error in enumerate(errors, 1):
        print(f"  {i}. {error}")
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump({"errors": errors}, f, indent=2, ensure_ascii=False)
        print(f"已保存到: {args.output}")


def main():
    """主函數"""
    parser = argparse.ArgumentParser(
        description="Grasshopper Tools 命令行接口",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  # 執行 placement_info.json
  python -m grasshopper_tools.cli execute-placement placement_info.json

  # 解析 MMD 文件
  python -m grasshopper_tools.cli parse-mmd component_info.mmd --action components

  # 生成 placement_info.json
  python -m grasshopper_tools.cli generate-json component_info.mmd -o placement_info.json

  # 創建組件
  python -m grasshopper_tools.cli add-component --guid "xxx" --x 100 --y 200 --component-id SLIDER_WIDTH

  # 設置 Slider
  python -m grasshopper_tools.cli set-slider --component-id SLIDER_WIDTH --value "120.0" --min 0 --max 200

  # 連接組件
  python -m grasshopper_tools.cli connect --source-id SLIDER_WIDTH --target-id DIVISION_X --source-param Number --target-param A
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # execute-placement 命令
    parser_execute = subparsers.add_parser('execute-placement', help='執行 placement_info.json')
    parser_execute.add_argument('json_path', help='placement_info.json 文件路徑')
    parser_execute.add_argument('--max-workers', type=int, default=10, help='最大並行線程數')
    parser_execute.add_argument('--no-save-id-map', dest='save_id_map', action='store_false', help='不保存 ID 映射')
    parser_execute.set_defaults(func=cmd_execute_placement)
    
    # parse-mmd 命令
    parser_parse = subparsers.add_parser('parse-mmd', help='解析 MMD 文件')
    parser_parse.add_argument('mmd_path', help='MMD 文件路徑')
    parser_parse.add_argument('--action', choices=['components', 'subgraphs', 'sliders'], required=True,
                             help='解析動作: components(組件和連接), subgraphs(subgraph), sliders(slider值)')
    parser_parse.add_argument('-o', '--output', help='輸出 JSON 文件路徑')
    parser_parse.set_defaults(func=cmd_parse_mmd)
    
    # generate-json 命令
    parser_gen = subparsers.add_parser('generate-json', help='生成 placement_info.json')
    parser_gen.add_argument('mmd_path', help='MMD 文件路徑')
    parser_gen.add_argument('-o', '--output', default='placement_info.json', help='輸出 JSON 文件路徑')
    parser_gen.add_argument('--description', default='自動生成', help='描述信息')
    parser_gen.set_defaults(func=cmd_generate_json)
    
    # update-guids 命令
    parser_update = subparsers.add_parser('update-guids', help='更新 JSON 文件中的 GUID')
    parser_update.add_argument('json_path', help='JSON 文件路徑')
    parser_update.add_argument('--guid-map', help='自定義 GUID 映射文件（JSON）')
    parser_update.set_defaults(func=cmd_update_guids)
    
    # add-component 命令
    parser_add = subparsers.add_parser('add-component', help='創建組件')
    parser_add.add_argument('--guid', required=True, help='組件類型 GUID')
    parser_add.add_argument('--x', type=float, required=True, help='X 座標')
    parser_add.add_argument('--y', type=float, required=True, help='Y 座標')
    parser_add.add_argument('--component-id', help='組件 ID 鍵（用於映射）')
    parser_add.set_defaults(func=cmd_add_component)
    
    # delete-component 命令
    parser_del = subparsers.add_parser('delete-component', help='刪除組件')
    parser_del.add_argument('component_id', help='組件實際 ID')
    parser_del.set_defaults(func=cmd_delete_component)
    
    # query-guid 命令
    parser_query = subparsers.add_parser('query-guid', help='查詢組件 GUID')
    parser_query.add_argument('component_name', help='組件名稱，如 "Number Slider"')
    parser_query.set_defaults(func=cmd_query_guid)
    
    # connect 命令
    parser_conn = subparsers.add_parser('connect', help='連接組件')
    parser_conn.add_argument('--source-id', required=True, help='源組件 ID 鍵')
    parser_conn.add_argument('--target-id', required=True, help='目標組件 ID 鍵')
    parser_conn.add_argument('--source-param', help='源組件參數名稱')
    parser_conn.add_argument('--target-param', help='目標組件參數名稱')
    parser_conn.set_defaults(func=cmd_connect_components)
    
    # set-slider 命令
    parser_slider = subparsers.add_parser('set-slider', help='設置 Slider')
    parser_slider.add_argument('--component-id', required=True, help='組件 ID 鍵')
    parser_slider.add_argument('--value', required=True, help='當前值')
    parser_slider.add_argument('--min', type=float, dest='min_value', help='最小值')
    parser_slider.add_argument('--max', type=float, dest='max_value', help='最大值')
    parser_slider.add_argument('--rounding', type=float, default=0.1, help='精度')
    parser_slider.set_defaults(func=cmd_set_slider)
    
    # set-vector 命令
    parser_vector = subparsers.add_parser('set-vector', help='設置 Vector XYZ')
    parser_vector.add_argument('--component-id', required=True, help='組件 ID 鍵')
    parser_vector.add_argument('--x', type=float, required=True, help='X 值')
    parser_vector.add_argument('--y', type=float, required=True, help='Y 值')
    parser_vector.add_argument('--z', type=float, required=True, help='Z 值')
    parser_vector.set_defaults(func=cmd_set_vector)
    
    # group 命令
    parser_group = subparsers.add_parser('group', help='創建群組')
    parser_group.add_argument('--component-ids', required=True, help='組件 ID 鍵列表（逗號分隔）')
    parser_group.add_argument('--group-name', required=True, help='群組名稱')
    parser_group.add_argument('--color', help='RGB 顏色（格式: r,g,b）')
    parser_group.add_argument('--color-hex', help='十六進制顏色（格式: #FF0000）')
    parser_group.set_defaults(func=cmd_group_components)
    
    # get-errors 命令
    parser_errors = subparsers.add_parser('get-errors', help='獲取文檔錯誤')
    parser_errors.add_argument('-o', '--output', help='輸出 JSON 文件路徑')
    parser_errors.set_defaults(func=cmd_get_errors)
    
    # 解析參數
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # 執行對應的命令函數
    args.func(args)


if __name__ == '__main__':
    main()

