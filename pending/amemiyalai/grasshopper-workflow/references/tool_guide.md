# Grasshopper Tools 工具使用指南

本文檔列出所有可用的工具及其所需的輸入資料。

## 📋 目錄

1. [GrasshopperClient - 通信客戶端](#grasshopperclient)
2. [ComponentManager - 組件管理](#componentmanager)
3. [ConnectionManager - 連接管理](#connectionmanager)
4. [ParameterSetter - 參數設置](#parametersetter)
5. [GroupManager - 群組管理](#groupmanager)
6. [MMDParser - MMD 解析](#mmdparser)
7. [JSONGenerator - JSON 生成](#jsongenerator)
8. [PlacementExecutor - 執行器](#placementexecutor)
9. [工具函數](#工具函數)

---

## 1. GrasshopperClient - 通信客戶端

### 初始化
```python
client = GrasshopperClient(host="localhost", port=8080)
```

**輸入資料：**
- `host` (可選): 服務器地址，默認 "localhost"
- `port` (可選): 服務器端口，默認 8080

### 方法

#### `send_command(command_type, params)`
發送命令到 Grasshopper MCP

**輸入資料：**
- `command_type` (必需): 命令類型字符串，如 "add_component", "connect_components"
- `params` (可選): 命令參數字典

**返回：** 響應字典

#### `extract_component_id(response)`
從響應中提取組件 ID

**輸入資料：**
- `response` (必需): Grasshopper MCP 響應字典

**返回：** 組件 ID 字符串或 None

---

## 2. ComponentManager - 組件管理

### 初始化
```python
comp_mgr = ComponentManager(client=None)
```

**輸入資料：**
- `client` (可選): GrasshopperClient 實例，如果為 None 則創建新實例

### 方法

#### `add_component(guid, x, y, component_id=None)`
創建單個組件

**輸入資料：**
- `guid` (必需): 組件類型 GUID 字符串
- `x` (必需): X 座標 (float)
- `y` (必需): Y 座標 (float)
- `component_id` (可選): 組件 ID 鍵（用於映射）

**返回：** 組件實際 ID 或 None

#### `add_components_parallel(commands, max_workers=10)`
並行創建多個組件

**輸入資料：**
- `commands` (必需): 組件創建命令列表，每個命令為字典：
  ```python
  {
      "guid": "組件類型 GUID",
      "x": 100.0,  # X 座標
      "y": 200.0,  # Y 座標
      "componentId": "SLIDER_WIDTH",  # 可選的組件 ID 鍵
      "comment": "註釋"  # 可選
  }
  ```
- `max_workers` (可選): 最大並行線程數，默認 10

**返回：** (成功數量, 失敗數量) 元組

#### `delete_component(component_id)`
刪除組件

**輸入資料：**
- `component_id` (必需): 組件實際 ID 字符串

**返回：** 是否成功刪除 (bool)

#### `get_component_guid(component_name)`
查詢組件的 GUID

**輸入資料：**
- `component_name` (必需): 組件名稱字符串，如 "Number Slider", "XY Plane"

**返回：** 包含 name, guid, category, isBuiltIn 的字典或 None

#### `get_component_id(component_id_key)`
從映射中獲取實際組件 ID

**輸入資料：**
- `component_id_key` (必需): 組件 ID 鍵字符串

**返回：** 實際組件 ID 或 None

#### `save_id_map(file_path=None)`
保存組件 ID 映射到文件

**輸入資料：**
- `file_path` (可選): 保存路徑，如果為 None 則使用默認路徑

#### `load_id_map(file_path=None)`
從文件加載組件 ID 映射

**輸入資料：**
- `file_path` (可選): 文件路徑，如果為 None 則使用默認路徑

---

## 3. ConnectionManager - 連接管理

### 初始化
```python
conn_mgr = ConnectionManager(client=None, component_manager=None)
```

**輸入資料：**
- `client` (可選): GrasshopperClient 實例
- `component_manager` (可選): ComponentManager 實例

### 方法

#### `connect_components(source_id, target_id, source_param=None, target_param=None, source_id_key=None, target_id_key=None)`
連接兩個組件

**輸入資料：**
- `source_id` (必需): 源組件實際 ID
- `target_id` (必需): 目標組件實際 ID
- `source_param` (可選): 源組件參數名稱
- `target_param` (可選): 目標組件參數名稱
- `source_id_key` (可選): 源組件 ID 鍵（用於從映射中查找）
- `target_id_key` (可選): 目標組件 ID 鍵（用於從映射中查找）

**返回：** 是否成功連接 (bool)

#### `connect_components_parallel(commands, max_workers=10)`
並行連接多個組件

**輸入資料：**
- `commands` (必需): 連接命令列表，每個命令為字典：
  ```python
  {
      "comment": "註釋",
      "parameters": {
          "sourceId": "SLIDER_WIDTH",  # 或實際 ID
          "targetId": "DIVISION_X",    # 或實際 ID
          "sourceParam": "Number",
          "targetParam": "A"
      }
  }
  ```
- `max_workers` (可選): 最大並行線程數，默認 10

**返回：** (成功數量, 失敗數量) 元組

#### `get_document_errors()`
獲取文檔中的所有錯誤

**輸入資料：** 無

**返回：** 錯誤列表

#### `fix_connection(source_id, target_id, source_param, target_param, source_id_key=None, target_id_key=None)`
修正連接

**輸入資料：** 與 `connect_components` 相同

**返回：** 是否成功修正 (bool)

---

## 4. ParameterSetter - 參數設置

### 初始化
```python
param_setter = ParameterSetter(client=None, component_manager=None)
```

**輸入資料：**
- `client` (可選): GrasshopperClient 實例
- `component_manager` (可選): ComponentManager 實例

### 方法

#### `set_slider_properties(component_id, value, min_value=None, max_value=None, rounding=0.1, component_id_key=None)`
設置 Number Slider 的屬性

**輸入資料：**
- `component_id` (必需): 組件實際 ID（如果提供 component_id_key 則可為空字符串）
- `value` (必需): 當前值字符串，如 "120.0"
- `min_value` (可選): 最小值 (float)
- `max_value` (可選): 最大值 (float)
- `rounding` (可選): 精度 (float)，默認 0.1
- `component_id_key` (可選): 組件 ID 鍵（用於從映射中查找）

**返回：** 是否成功設置 (bool)

#### `set_component_value(component_id, value, parameter=None, min_value=None, max_value=None, rounding=None, component_id_key=None)`
設置組件的值（通用方法）

**輸入資料：**
- `component_id` (必需): 組件實際 ID
- `value` (必需): 要設置的值字符串
- `parameter` (可選): 參數名稱，如 "X", "Y", "Z"（用於 Vector XYZ）
- `min_value` (可選): 最小值（僅對 Number Slider 有效）
- `max_value` (可選): 最大值（僅對 Number Slider 有效）
- `rounding` (可選): 精度（僅對 Number Slider 有效）
- `component_id_key` (可選): 組件 ID 鍵

**返回：** 是否成功設置 (bool)

#### `set_slider(component_id_key, value, min_value=None, max_value=None, rounding=0.1, auto_range=True)`
設置 Slider 的值（自動確定範圍）

**輸入資料：**
- `component_id_key` (必需): 組件 ID 鍵
- `value` (必需): 當前值字符串
- `min_value` (可選): 最小值
- `max_value` (可選): 最大值
- `rounding` (可選): 精度，默認 0.1
- `auto_range` (可選): 是否自動確定範圍，默認 True

**返回：** 是否成功設置 (bool)

#### `set_vector_xyz(component_id_key, x, y, z)`
設置 Vector XYZ 組件的 X、Y、Z 值

**輸入資料：**
- `component_id_key` (必需): 組件 ID 鍵
- `x` (必需): X 值 (float)
- `y` (必需): Y 值 (float)
- `z` (必需): Z 值 (float)

**返回：** 是否全部成功設置 (bool)

#### `set_sliders_batch(slider_configs)`
批量設置多個 Slider

**輸入資料：**
- `slider_configs` (必需): Slider 配置列表，每個配置為元組：
  ```python
  (
      "SLIDER_WIDTH",    # component_id_key
      "120.0",           # value
      0.0,               # min_value (可選)
      200.0,             # max_value (可選)
      0.1                # rounding (可選)
  )
  ```

**返回：** (成功數量, 失敗數量) 元組

---

## 5. GroupManager - 群組管理

### 初始化
```python
group_mgr = GroupManager(client=None, component_manager=None)
```

**輸入資料：**
- `client` (可選): GrasshopperClient 實例
- `component_manager` (可選): ComponentManager 實例

### 方法

#### `group_components(component_ids, group_name, color=None, color_hex=None, component_id_keys=None)`
將多個組件群組起來

**輸入資料：**
- `component_ids` (必需): 組件實際 ID 列表
- `group_name` (必需): 群組名稱字符串
- `color` (可選): RGB 顏色元組 (r, g, b)，如 (225, 245, 255)
- `color_hex` (可選): 十六進制顏色字符串，如 "#FF0000"
- `component_id_keys` (可選): 組件 ID 鍵列表（用於從映射中查找）

**返回：** 是否成功創建群組 (bool)

#### `group_components_batch(groups)`
批量創建多個群組

**輸入資料：**
- `groups` (必需): 群組配置列表，每個配置為字典：
  ```python
  {
      "name": "群組名稱",
      "componentIds": ["id1", "id2"],  # 或使用 componentIdKeys
      "componentIdKeys": ["SLIDER_WIDTH", "SLIDER_LENGTH"],  # 或使用 componentIds
      "color": (225, 245, 255),  # 或使用 colorHex
      "colorHex": "#FF0000"  # 或使用 color
  }
  ```

**返回：** (成功數量, 失敗數量) 元組

---

## 6. MMDParser - MMD 解析

### 初始化
```python
parser = MMDParser()
```

**輸入資料：** 無

### 方法

#### `parse_component_info_mmd(file_path)`
解析 component_info.mmd 文件，提取組件和連接信息

**輸入資料：**
- `file_path` (必需): MMD 文件路徑字符串

**返回：** (組件列表, 連接列表) 元組

#### `parse_subgraphs_from_mmd(file_path)`
提取所有 subgraph 及其組件

**輸入資料：**
- `file_path` (必需): MMD 文件路徑字符串

**返回：** subgraph ID 到組件 ID 列表的映射字典

#### `get_subgraph_names(file_path)`
獲取 subgraph ID 到名稱的映射

**輸入資料：**
- `file_path` (必需): MMD 文件路徑字符串

**返回：** subgraph ID 到名稱的映射字典

#### `parse_slider_values(file_path)`
提取所有 Number Slider 的值

**輸入資料：**
- `file_path` (必需): MMD 文件路徑字符串

**返回：** 組件 ID 到 slider 信息的映射字典

---

## 7. JSONGenerator - JSON 生成

### 初始化
```python
generator = JSONGenerator()
```

**輸入資料：** 無

### 方法

#### `generate_placement_info(components, connections, description="自動生成")`
生成 placement_info.json 結構

**輸入資料：**
- `components` (必需): 組件列表（從 MMDParser.parse_component_info_mmd 獲取）
- `connections` (必需): 連接列表（從 MMDParser.parse_component_info_mmd 獲取）
- `description` (可選): 描述信息字符串，默認 "自動生成"

**返回：** placement_info 字典

#### `save_placement_info(placement_info, file_path)`
保存 placement_info 到 JSON 文件

**輸入資料：**
- `placement_info` (必需): placement_info 字典
- `file_path` (必需): 保存路徑字符串

---

## 8. PlacementExecutor - 執行器

### 初始化
```python
executor = PlacementExecutor(client=None, component_manager=None, connection_manager=None)
```

**輸入資料：**
- `client` (可選): GrasshopperClient 實例
- `component_manager` (可選): ComponentManager 實例
- `connection_manager` (可選): ConnectionManager 實例

### 方法

#### `execute_placement_info(json_path, max_workers=10, save_id_map=True, id_map_path=None)`
執行 placement_info.json 中的命令

**輸入資料：**
- `json_path` (必需): placement_info.json 文件路徑字符串
- `max_workers` (可選): 最大並行線程數，默認 10
- `save_id_map` (可選): 是否保存組件 ID 映射，默認 True
- `id_map_path` (可選): 組件 ID 映射保存路徑，如果為 None 則使用默認路徑

**返回：** 執行結果字典，包含：
- `success`: 是否全部成功 (bool)
- `add_success`: 組件創建成功數量 (int)
- `add_fail`: 組件創建失敗數量 (int)
- `connect_success`: 連接成功數量 (int)
- `connect_fail`: 連接失敗數量 (int)
- `add_time`: 組件創建耗時 (float)
- `connect_time`: 連接耗時 (float)
- `total_time`: 總耗時 (float)
- `component_id_map_size`: 組件 ID 映射數量 (int)

---

## 9. 工具函數

### `load_component_id_map(file_path=None)`
從文件加載組件 ID 映射

**輸入資料：**
- `file_path` (可選): 組件 ID 映射文件路徑

**返回：** 組件 ID 映射字典或 None

### `save_component_id_map(component_id_map, file_path=None)`
保存組件 ID 映射到文件

**輸入資料：**
- `component_id_map` (必需): 組件 ID 映射字典
- `file_path` (可選): 保存路徑

### `load_placement_info(json_path)`
讀取 placement_info.json 文件

**輸入資料：**
- `json_path` (必需): JSON 文件路徑字符串

**返回：** placement_info 字典或 None

### `update_guids_in_json(json_path, guid_map)`
更新 JSON 文件中的 GUID

**輸入資料：**
- `json_path` (必需): JSON 文件路徑字符串
- `guid_map` (必需): 舊 GUID 到新 GUID 的映射字典

**返回：** 更新的 GUID 數量 (int)

### `DEFAULT_GUID_MAP`
預設的 GUID 映射字典（可直接使用）

### `hex_to_rgb(hex_color)`
將十六進制顏色轉換為 RGB

**輸入資料：**
- `hex_color` (必需): 十六進制顏色字符串，如 "#FF0000" 或 "FF0000"

**返回：** RGB 元組 (r, g, b)

### `determine_slider_range(slider_name, value)`
根據 slider 名稱和值確定合理的範圍

**輸入資料：**
- `slider_name` (必需): Slider 名稱字符串
- `value` (必需): Slider 值 (float)

**返回：** (最小值, 最大值) 元組

---

## 📝 快速參考

### 最常用的工作流程

#### 1. 從 MMD 文件創建完整的 Grasshopper 定義
```python
from scripts.parser_utils import MMDParser, JSONGenerator, PlacementExecutor

# 解析 MMD
parser = MMDParser()
components, connections = parser.parse_component_info_mmd("component_info.mmd")

# 生成 JSON
generator = JSONGenerator()
placement_info = generator.generate_placement_info(components, connections)
generator.save_placement_info(placement_info, "placement_info.json")

# 執行
executor = PlacementExecutor()
result = executor.execute_placement_info("placement_info.json")
```

#### 2. 設置參數
```python
from scripts.parameter_setter import ParameterSetter
from scripts.component_manager import ComponentManager

comp_mgr = ComponentManager()
param_setter = ParameterSetter(component_manager=comp_mgr)

# 設置單個 slider
param_setter.set_slider("SLIDER_WIDTH", "120.0", 0.0, 200.0)

# 批量設置
configs = [
    ("SLIDER_WIDTH", "120.0", 0.0, 200.0, 0.1),
    ("SLIDER_LENGTH", "80.0", 0.0, 200.0, 0.1),
]
param_setter.set_sliders_batch(configs)
```

#### 3. 創建群組
```python
from scripts.group_manager import GroupManager
from scripts.component_manager import ComponentManager

comp_mgr = ComponentManager()
group_mgr = GroupManager(component_manager=comp_mgr)

# 創建單個群組
group_mgr.group_components(
    component_id_keys=["SLIDER_WIDTH", "SLIDER_LENGTH"],
    group_name="桌面參數",
    color=(225, 245, 255)
)
```

---

## 🔗 相關文檔

- [API 參考](api_reference.md) - 完整的使用說明和範例
- [CLI 使用說明](cli_usage.md) - 命令行工具使用指南
- [工作流程步驟](workflow_steps.md) - 完整的工作流程指南

