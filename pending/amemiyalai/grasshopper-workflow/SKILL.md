---
name: grasshopper-workflow
description: "Grasshopper 參數化建模工作流程工具。當需要通過 MCP 協議與 Grasshopper 交互、創建和管理組件、建立連接、設置參數、執行完整建模工作流程時使用。適用於：(1) 從 MMD 文件創建 Grasshopper 定義, (2) 執行 placement_info.json 工作流程, (3) 批量管理組件和連接, (4) 參數化建模的自動化流程, (5) 解析 component_info.mmd 和 part_info.mmd 文件"
---

# Grasshopper Workflow Skill

## 概述

此技能提供完整的 Grasshopper 參數化建模工作流程，包括組件管理、連接管理、參數設置、群組管理和工作流程執行。整合了從需求分析到最終執行的完整流程。

## 核心功能

### 1. 組件管理
- 創建、查詢、刪除組件
- 並行創建多個組件
- 組件 ID 映射管理
- 組件 GUID 查詢

### 2. 連接管理
- 建立組件之間的連接
- 並行連接多個組件
- 連接錯誤檢查和修正
- 文檔錯誤診斷

### 3. 參數設置
- 設置 Number Slider 屬性
- 設置 Vector XYZ 組件
- 批量參數設置
- 自動範圍確定

### 4. 群組管理
- 創建組件群組
- 批量創建群組
- 自定義群組顏色和名稱

### 5. 工作流程執行
- 解析 MMD 文件（component_info.mmd, part_info.mmd）
- 生成 placement_info.json
- 執行完整建模流程
- 自動化腳本執行

## 快速開始

### 基本使用

```python
from scripts.client import GrasshopperClient
from scripts.component_manager import ComponentManager
from scripts.connection_manager import ConnectionManager
from scripts.parameter_setter import ParameterSetter
from scripts.group_manager import GroupManager

# 創建客戶端
client = GrasshopperClient(host="localhost", port=8080)

# 創建組件管理器
comp_mgr = ComponentManager(client)

# 創建組件
component_id = comp_mgr.add_component(
    guid="e2bb9b8d-0d80-44e7-aa2d-2e446f5c61da",
    x=100,
    y=200,
    component_id="SLIDER_WIDTH"
)
```

### 完整工作流程

```python
from scripts.parser_utils import MMDParser, JSONGenerator
from scripts.placement_executor import PlacementExecutor

# 1. 解析 MMD 文件
parser = MMDParser()
components, connections = parser.parse_component_info_mmd("component_info.mmd")

# 2. 生成 placement_info.json
generator = JSONGenerator()
placement_info = generator.generate_placement_info(components, connections)
generator.save_placement_info(placement_info, "placement_info.json")

# 3. 執行
executor = PlacementExecutor()
result = executor.execute_placement_info("placement_info.json")
```

## 工作流程步驟

Grasshopper 建模工作流程包含 6 個主要步驟：

1. **釐清設計需求與規格** - 參見 [references/workflow_steps.md](references/workflow_steps.md#step-1-釐清設計需求與規格)
2. **拆分幾何物件創建 part_info.mmd** - 參見 [references/workflow_steps.md](references/workflow_steps.md#step-2-拆分幾何物件)
3. **規劃電池實際連接圖 component_info.mmd** - 參見 [references/workflow_steps.md](references/workflow_steps.md#step-3-規劃電池實際連接圖)
4. **找出所需組件 GUID 並規劃位置** - 參見 [references/workflow_steps.md](references/workflow_steps.md#step-4-找出id規劃位置)
5. **生成執行序列檔案 placement_info.json** - 參見 [references/workflow_steps.md](references/workflow_steps.md#step-5-生成執行序列檔案)
6. **清理 GH_WIP 檔案** - 參見 [references/workflow_steps.md](references/workflow_steps.md#step-6-清理gh_wip檔案)

## 詳細文檔

- **工作流程步驟**: 參見 [references/workflow_steps.md](references/workflow_steps.md) - 完整的 6 步驟工作流程指南
- **API 參考**: 參見 [references/api_reference.md](references/api_reference.md) - 所有模組和方法的詳細說明
- **CLI 使用說明**: 參見 [references/cli_usage.md](references/cli_usage.md) - 命令行工具使用指南
- **工具使用指南**: 參見 [references/tool_guide.md](references/tool_guide.md) - 所有工具的輸入輸出說明

## 腳本工具

所有 Python 腳本位於 `scripts/` 目錄：

- `client.py` - MCP 通信客戶端
- `component_manager.py` - 組件管理
- `connection_manager.py` - 連接管理
- `parameter_setter.py` - 參數設置
- `group_manager.py` - 群組管理
- `parser_utils.py` - MMD/JSON 解析
- `placement_executor.py` - 執行器
- `utils.py` - 工具函數
- `cli.py` - 命令行接口

## 使用腳本

當需要執行特定操作時，可以調用相應的腳本：

```python
# 執行 placement_info.json
from scripts.placement_executor import PlacementExecutor
executor = PlacementExecutor()
result = executor.execute_placement_info("placement_info.json", max_workers=10)
```

## 命令行工具

使用 CLI 工具執行常見任務：

```bash
# 執行 placement_info.json
python scripts/cli.py execute-placement placement_info.json

# 設置所有 slider
python scripts/cli.py set-sliders component_info.mmd

# 群組組件
python scripts/cli.py group-components component_info.mmd
```

詳細的 CLI 使用說明參見 [references/cli_usage.md](references/cli_usage.md)。

## 注意事項

1. **MCP 服務器**: 確保 Grasshopper MCP 服務器正在運行（localhost:8080）
2. **組件 ID 映射**: 組件創建後會自動保存 ID 映射到 `component_id_map.json`
3. **並行執行**: 支持並行執行以提高效率，建議使用 `max_workers=10` 到 `20`
4. **線程安全**: 所有操作都是線程安全的，可以在多線程環境中使用
5. **文件路徑**: 腳本中的相對路徑需要根據實際使用情況調整

## 常見工作流程

### 從 MMD 到完整定義

1. 解析 `component_info.mmd` 獲取組件和連接信息
2. 生成 `placement_info.json` 執行序列
3. 執行 `placement_info.json` 創建組件和連接
4. 設置所有 slider 參數值
5. 創建組件群組

詳細步驟參見 [references/workflow_steps.md](references/workflow_steps.md)。

