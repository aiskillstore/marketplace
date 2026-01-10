# Grasshopper MCP 工具模組 API 參考

統一的 Grasshopper MCP 操作接口，提供組件管理、連接管理、參數設置、群組管理等功能。

## 目錄結構

```
grasshopper_tools/
├── __init__.py              # 模組初始化
├── client.py                # Grasshopper MCP 通信客戶端
├── component_manager.py     # 組件管理工具
├── connection_manager.py    # 連接管理工具
├── parameter_setter.py      # 參數設置工具
├── group_manager.py         # 群組管理工具
├── parser_utils.py          # MMD/JSON 解析工具
└── utils.py                 # 通用工具函數
```

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
    guid="e2bb9b8d-0d80-44e7-aa2d-2e446f5c61da",  # Number Slider GUID
    x=100,
    y=200,
    component_id="SLIDER_WIDTH"  # 可選的映射鍵
)

# 創建連接管理器
conn_mgr = ConnectionManager(client, comp_mgr)

# 連接組件
conn_mgr.connect_components(
    source_id_key="SLIDER_WIDTH",
    target_id_key="DIVISION_X",
    source_param="Number",
    target_param="A"
)

# 設置參數
param_setter = ParameterSetter(client, comp_mgr)
param_setter.set_slider(
    component_id_key="SLIDER_WIDTH",
    value="120.0",
    min_value=0.0,
    max_value=200.0
)

# 群組組件
group_mgr = GroupManager(client, comp_mgr)
group_mgr.group_components(
    component_id_keys=["SLIDER_WIDTH", "SLIDER_LENGTH"],
    group_name="桌面參數",
    color=(225, 245, 255)
)
```

## 模組說明

### 1. GrasshopperClient

Grasshopper MCP 通信客戶端，提供統一的命令發送接口。

#### 主要方法

- `send_command(command_type, params)`: 發送命令到 Grasshopper MCP
- `extract_component_id(response)`: 從響應中提取組件 ID
- `safe_print(*args, **kwargs)`: 線程安全的打印函數

#### 範例

```python
client = GrasshopperClient()
response = client.send_command("get_all_components", {})
component_id = client.extract_component_id(response)
```

### 2. ComponentManager

組件管理器，提供組件的創建、查詢、刪除等功能。

#### 主要方法

- `add_component(guid, x, y, component_id)`: 創建組件
- `add_components_parallel(commands, max_workers)`: 並行創建多個組件
- `delete_component(component_id)`: 刪除組件
- `get_component_guid(component_name)`: 查詢組件的 GUID
- `get_component_id(component_id_key)`: 從映射中獲取實際組件 ID
- `save_id_map(file_path)`: 保存組件 ID 映射到文件
- `load_id_map(file_path)`: 從文件加載組件 ID 映射

#### 範例

```python
comp_mgr = ComponentManager()

# 創建單個組件
comp_id = comp_mgr.add_component(
    guid="e2bb9b8d-0d80-44e7-aa2d-2e446f5c61da",
    x=100,
    y=200,
    component_id="SLIDER_WIDTH"
)

# 並行創建多個組件
commands = [
    {
        "guid": "e2bb9b8d-0d80-44e7-aa2d-2e446f5c61da",
        "x": 100,
        "y": 200,
        "componentId": "SLIDER_WIDTH"
    },
    # ... 更多命令
]
success, fail = comp_mgr.add_components_parallel(commands, max_workers=10)

# 保存 ID 映射
comp_mgr.save_id_map("component_id_map.json")
```

### 3. ConnectionManager

連接管理器，提供組件連接的創建、修正、錯誤檢查等功能。

#### 主要方法

- `connect_components(...)`: 連接兩個組件
- `connect_components_parallel(commands, max_workers)`: 並行連接多個組件
- `get_document_errors()`: 獲取文檔中的所有錯誤
- `fix_connection(...)`: 修正連接

#### 範例

```python
conn_mgr = ConnectionManager(client, comp_mgr)

# 連接組件（使用 ID 鍵）
conn_mgr.connect_components(
    source_id_key="SLIDER_WIDTH",
    target_id_key="DIVISION_X",
    source_param="Number",
    target_param="A"
)

# 並行連接多個組件
commands = [
    {
        "comment": "SLIDER_WIDTH -> DIVISION_X",
        "parameters": {
            "sourceId": "SLIDER_WIDTH",
            "targetId": "DIVISION_X",
            "sourceParam": "Number",
            "targetParam": "A"
        }
    },
    # ... 更多命令
]
success, fail = conn_mgr.connect_components_parallel(commands)

# 獲取錯誤
errors = conn_mgr.get_document_errors()
```

### 4. ParameterSetter

參數設置器，提供組件參數設置功能。

#### 主要方法

- `set_slider_properties(...)`: 設置 Number Slider 的屬性
- `set_component_value(...)`: 設置組件的值（通用方法）
- `set_slider(...)`: 設置 Slider 的值（自動確定範圍）
- `set_vector_xyz(...)`: 設置 Vector XYZ 組件的 X、Y、Z 值
- `set_sliders_batch(...)`: 批量設置多個 Slider

#### 範例

```python
param_setter = ParameterSetter(client, comp_mgr)

# 設置 Slider（自動確定範圍）
param_setter.set_slider(
    component_id_key="SLIDER_WIDTH",
    value="120.0",
    min_value=0.0,
    max_value=200.0,
    rounding=0.1
)

# 設置 Vector XYZ
param_setter.set_vector_xyz(
    component_id_key="VECTOR_LEG1",
    x=-50.0,
    y=-30.0,
    z=0.0
)

# 批量設置
slider_configs = [
    ("SLIDER_WIDTH", "120.0", 0.0, 200.0, 0.1),
    ("SLIDER_LENGTH", "80.0", 0.0, 200.0, 0.1),
]
success, fail = param_setter.set_sliders_batch(slider_configs)
```

### 5. GroupManager

群組管理器，提供組件群組的創建和管理功能。

#### 主要方法

- `group_components(...)`: 將多個組件群組起來
- `group_components_batch(groups)`: 批量創建多個群組

#### 範例

```python
group_mgr = GroupManager(client, comp_mgr)

# 創建單個群組
group_mgr.group_components(
    component_id_keys=["SLIDER_WIDTH", "SLIDER_LENGTH", "SLIDER_TOP_HEIGHT"],
    group_name="桌面參數",
    color=(225, 245, 255)  # RGB
)

# 批量創建群組
groups = [
    {
        "name": "桌面參數",
        "componentIdKeys": ["SLIDER_WIDTH", "SLIDER_LENGTH"],
        "color": (225, 245, 255)
    },
    {
        "name": "桌腳參數",
        "componentIdKeys": ["SLIDER_RADIUS_LEG", "SLIDER_LEG_HEIGHT"],
        "colorHex": "#FF0000"
    }
]
success, fail = group_mgr.group_components_batch(groups)
```

### 6. MMDParser / JSONGenerator

MMD 文件解析器和 JSON 生成器。

### 7. PlacementExecutor

執行 placement_info.json 的完整流程。

#### 主要方法

**MMDParser:**
- `parse_component_info_mmd(file_path)`: 解析 MMD 文件，提取組件和連接信息
- `parse_subgraphs_from_mmd(file_path)`: 提取所有 subgraph 及其組件
- `get_subgraph_names(file_path)`: 獲取 subgraph ID 到名稱的映射
- `parse_slider_values(file_path)`: 提取所有 Number Slider 的值

**JSONGenerator:**
- `generate_placement_info(components, connections, description)`: 生成 placement_info.json 結構
- `save_placement_info(placement_info, file_path)`: 保存到 JSON 文件

#### 範例

```python
from scripts.parser_utils import MMDParser, JSONGenerator

# 解析 MMD 文件
parser = MMDParser()
components, connections = parser.parse_component_info_mmd("component_info.mmd")

# 提取 subgraph
subgraphs = parser.parse_subgraphs_from_mmd("component_info.mmd")
subgraph_names = parser.get_subgraph_names("component_info.mmd")

# 提取 slider 值
sliders = parser.parse_slider_values("component_info.mmd")

# 生成 JSON
generator = JSONGenerator()
placement_info = generator.generate_placement_info(
    components,
    connections,
    description="桌子創建執行序列"
)
generator.save_placement_info(placement_info, "placement_info.json")
```

## 完整範例

### 從 MMD 文件創建完整的 Grasshopper 定義

```python
from scripts.parser_utils import MMDParser, JSONGenerator
from scripts.placement_executor import PlacementExecutor
from scripts.component_manager import ComponentManager
from scripts.connection_manager import ConnectionManager
from scripts.parameter_setter import ParameterSetter
from scripts.group_manager import GroupManager

# 1. 解析 MMD 文件
parser = MMDParser()
components, connections = parser.parse_component_info_mmd("component_info.mmd")

# 2. 生成 placement_info.json（可選）
generator = JSONGenerator()
placement_info = generator.generate_placement_info(components, connections)
generator.save_placement_info(placement_info, "placement_info.json")

# 3. 創建客戶端和管理器
client = GrasshopperClient()
comp_mgr = ComponentManager(client)
conn_mgr = ConnectionManager(client, comp_mgr)
param_setter = ParameterSetter(client, comp_mgr)
group_mgr = GroupManager(client, comp_mgr)

# 4. 生成並執行 placement_info.json（推薦方式）
generator = JSONGenerator()
placement_info = generator.generate_placement_info(components, connections)
generator.save_placement_info(placement_info, "placement_info.json")

# 執行 placement_info.json
executor = PlacementExecutor()
result = executor.execute_placement_info("placement_info.json", max_workers=10)

# 6. 設置參數
sliders = parser.parse_slider_values("component_info.mmd")
slider_configs = [
    (comp_id, info["value"], None, None, 0.1)
    for comp_id, info in sliders.items()
]
param_setter.set_sliders_batch(slider_configs)

# 7. 創建群組
subgraphs = parser.parse_subgraphs_from_mmd("component_info.mmd")
subgraph_names = parser.get_subgraph_names("component_info.mmd")
groups = [
    {
        "name": subgraph_names.get(sg_id, sg_id),
        "componentIdKeys": comp_ids,
        "color": (225, 245, 255)  # 根據需要設置顏色
    }
    for sg_id, comp_ids in subgraphs.items()
]
group_mgr.group_components_batch(groups)
```

## 注意事項

1. **組件 ID 映射**: 組件創建後會自動保存 ID 映射，後續操作可以使用 `component_id_key` 來引用組件。

2. **並行執行**: 組件創建和連接支持並行執行，可以顯著提高效率。建議使用 `max_workers=10` 到 `20`。

3. **錯誤處理**: 所有方法都會返回成功/失敗狀態，建議檢查返回值並處理錯誤。

4. **線程安全**: 所有操作都是線程安全的，可以在多線程環境中使用。

5. **連接參數**: 不同組件的參數名稱可能不同，建議參考 Grasshopper 文檔或使用 `get_component_info` 查詢。

## 遷移指南

如果您之前使用單獨的腳本文件（如 `execute_placement.py`、`auto_set_sliders.py` 等），可以按以下方式遷移：

### 舊代碼
```python
# execute_placement.py
def send_to_grasshopper(command_type, params):
    # ... 實現
```

### 新代碼
```python
from scripts.client import GrasshopperClient

client = GrasshopperClient()
response = client.send_command(command_type, params)
```

### 舊代碼
```python
# auto_set_sliders.py
slider_configs = [...]
for config in slider_configs:
    send_to_grasshopper("set_slider_properties", {...})
```

### 新代碼
```python
from scripts.parameter_setter import ParameterSetter
from scripts.component_manager import ComponentManager

comp_mgr = ComponentManager()
param_setter = ParameterSetter(component_manager=comp_mgr)
param_setter.set_sliders_batch(slider_configs)
```

## 版本歷史

- **v1.0.0** (2025-12-21): 初始版本，整合所有 GH_WIP 目錄中的功能

## 授權

與主項目相同的授權協議。

