# Grasshopper 工作流程步驟

你是RhinoGrasshopper的參數化建模領域專家

請在GH_WIP創建本次任務所需要的檔案
1.part_info.mmd

請嚴格按照以下任務步驟進行請透過查看GH_WIP資料夾內檔案的狀況來判定目前正在進行那一個階段

任務步驟
task1.釐清設計需求與規格
task2.拆分幾何物件創建part_info.mmd 
task3.規劃電池實際連接圖component_info.mmd
task4.使用get_component_candidates找出所需組件GUID並更新寫入component_info.mmd並規劃電池擺放位置
task5.生程執行序列檔案placement_info.json
task6.清理GH_WIP檔案根據完成時間與任務名稱在GH_PKG創建資料夾ex.202512201344-create_table

## Step 1: 釐清設計需求與規格

進入下一階段條件:已經釐清用戶需求從各個幾何具體的形狀成型方式以及參數需求
如果使用者沒有詳細描述設計規格請先跟使用者釐清設計需求與規格，若以更清晰請進入下一階段
如果使用者沒有提出設計需求的規格請先提出一個建議的規格或者是提供多個方案直接供使用者選擇1 2 3個方案

## Step 2: 拆分幾何物件

進入下一階段條件:完成part_info.mmd檔案創建

先根據用戶提出的目標幾何物件分解成多個子物件並在GH_WIP創建part_info.mmd紀錄各個組件的成形方式以及組件間的依賴關係例如擺在這個組件的參考點哪個位置相對位置要如何取得
若有相同重覆物件例如4之相同桌腳請用orient來複製想同物件到不同參考平面
Ex.桌子->桌面、4支桌腳

描述各個子物件規格part_info.mmd

Ex.草圖類型(2D):polygon,Rectangle,Circle,或是透過"construct point"創建多個點並用polyline連接成一個封閉曲線
在從草圖2D轉換成3D實體前必須先執行boundary surfaces建立面，再進行3D成形
成形方法(3D)extrude,
關鍵參數(Param)vector plane

使用該格式輸出
erDiagram
    TABLE ||--|| TABLE_TOP : contains
    TABLE ||--o{ TABLE_LEG : contains
    
    TABLE_TOP ||--o{ TABLE_LEG : supports

    TABLE {
        string name "桌子"
        int leg_count "4"
        float total_height "75.0"
    }

    TABLE_TOP {
        string sketch_type "Rectangle"
        string forming_method "Extrude"
        float width "120.0"
        float length "80.0"
        float height "5.0"
        plane base_plane "基準平面"
        vector extrusion_direction "擠出方向"
    }

    TABLE_LEG {
        string sketch_type "Circle"
        string forming_method "Extrude"
        float radius "2.5"
        float height "70.0"
        plane base_plane "基準平面（4個不同位置）"
        vector extrusion_direction "擠出方向"
        int leg_position "1-4"
    }

## Step 3: 規劃電池實際連接圖

根據part_info.mmd
最後完成後檢查有沒有缺少電池之間的連接或者是缺少input輸入
ex.
flowchart LR
    %% 桌面模块
    subgraph TOP["桌面 TABLE_TOP"]
        direction LR
        XY_PLANE_TOP["XY Plane<br/>输出: Plane"]
        SLIDER_WIDTH["Number Slider<br/>输出: 120.0"]
        SLIDER_LENGTH["Number Slider<br/>输出: 80.0"]
        RECTANGLE_TOP["Rectangle<br/>输入: Plane, X Size, Y Size<br/>输出: Rectangle"]
        BOUNDARY_SURFACES_TOP["Boundary Surfaces<br/>输入: Curves<br/>输出: Surface"]
        SLIDER_TOP_HEIGHT["Number Slider<br/>输出: 5.0"]
        UNIT_Z["Unit Z<br/>输出: Vector"]
        AMPLITUDE_TOP["Amplitude<br/>输入: Vector, Amplitude (Number)<br/>输出: Vector"]
        EXTRUDE_TOP["Extrude<br/>输入: Base (Surface), Direction (Vector)<br/>输出: Result"]
        
        XY_PLANE_TOP -->|"Plane"| RECTANGLE_TOP
        SLIDER_WIDTH -->|"Number"| RECTANGLE_TOP
        SLIDER_LENGTH -->|"Number"| RECTANGLE_TOP
        RECTANGLE_TOP -->|"Rectangle"| BOUNDARY_SURFACES_TOP
        BOUNDARY_SURFACES_TOP -->|"Surface"| EXTRUDE_TOP
        UNIT_Z -->|"Vector"| AMPLITUDE_TOP
        SLIDER_TOP_HEIGHT -->|"Number"| AMPLITUDE_TOP
        AMPLITUDE_TOP -->|"Vector"| EXTRUDE_TOP
    end
    
    %% 桌腳1模块
    subgraph LEG1["桌腳1 TABLE_LEG_1"]
        direction LR
        XY_PLANE_LEG1["XY Plane<br/>输出: Plane"]
        VECTOR_LEG1["Vector XYZ<br/>输出: Vector<br/>位置: X=-50, Y=-30"]
        MOVE_PLANE_LEG1["Move<br/>输入: Geometry, Motion<br/>输出: Plane"]
        SLIDER_RADIUS_LEG["Number Slider<br/>输出: 2.5"]
        CIRCLE_LEG1["Circle<br/>输入: Plane, Radius<br/>输出: Circle"]
        BOUNDARY_SURFACES_LEG1["Boundary Surfaces<br/>输入: Curves<br/>输出: Surface"]
        SLIDER_LEG_HEIGHT["Number Slider<br/>输出: 70.0"]
        AMPLITUDE_LEG1["Amplitude<br/>输入: Vector, Amplitude (Number)<br/>输出: Vector"]
        EXTRUDE_LEG1["Extrude<br/>输入: Base (Surface), Direction (Vector)<br/>输出: Result"]
        
        XY_PLANE_LEG1 -->|"Plane"| MOVE_PLANE_LEG1
        VECTOR_LEG1 -->|"Vector"| MOVE_PLANE_LEG1
        MOVE_PLANE_LEG1 -->|"Plane"| CIRCLE_LEG1
        SLIDER_RADIUS_LEG -->|"Number"| CIRCLE_LEG1
        CIRCLE_LEG1 -->|"Circle"| BOUNDARY_SURFACES_LEG1
        BOUNDARY_SURFACES_LEG1 -->|"Surface"| EXTRUDE_LEG1
        UNIT_Z -->|"Vector"| AMPLITUDE_LEG1
        SLIDER_LEG_HEIGHT -->|"Number"| AMPLITUDE_LEG1
    end

## Step 4: 找出ID規劃位置

進入下一階段條件:完成component_info.mmd中所有組件的GUID查詢並更新，且所有組件位置已規劃完成請確實檢查是否有碰撞或是距離過近重疊的問題

步驟:
1. 使用get_component_candidates查詢component_info.mmd中所有需要的組件名稱，獲取正確的GUID並且也獲取正確的input output參數名稱更新到component_info.mmd
2. 將查詢到的GUID更新到component_info.mmd中對應組件的GUID欄位
3. 規劃每個組件在畫布上的擺放位置(X, Y座標)

電池擺放位置規則:
- 同群組或同一個物件的電池應該擺放在附近的位置，保持適當間距(建議200-300單位)
- 如果2個電池都連接到同一顆電池上，那兩顆電池的X位置應該保持相同，Y位置不同，保持垂直間距(建議100-150單位)
- 避免電池過於接近導致碰撞重疊，最小間距建議至少50單位
- 相關的組件應該按照數據流向從左到右排列
- 輸入組件(如Number Slider)通常放在左側，處理組件在中間，輸出組件在右側

component_info.mmd更新格式:
在每個組件的描述中添加以下信息:
- GUID: [查詢到的組件GUID]
- 位置: X=[X座標], Y=[Y座標]

範例:
```
XY_PLANE_TOP["XY Plane<br/>输出: Plane<br/>GUID: 6301d658-592f-47d0-ae0d-ad3c183a7ea5<br/>位置: X=100, Y=100"]
SLIDER_WIDTH["Number Slider<br/>输出: 120.0<br/>GUID: f9abdb91-05f7-4363-8fd2-174b73a276f3<br/>位置: X=100, Y=200"]
```

注意事項:
- 確保使用get_component_candidates查詢到的GUID是組件類型GUID，不是實例GUID
- 如果查詢結果有多個候選項，選擇最符合需求的標準組件
- 位置規劃時要考慮整體布局的美觀性和可讀性

## Step 5: 生成執行序列檔案

進入下一階段條件:完成placement_info.json檔案創建，包含所有組件的add_component命令和所有連接的connect_components命令

步驟:
1. 讀取component_info.mmd文件，提取所有組件信息（GUID、位置、componentId）
2. 按照component_info.mmd中的順序，生成所有add_component命令
3. 按照component_info.mmd中的連接關係，生成所有connect_components命令
4. 將所有命令按照正確的JSON格式組織成placement_info.json文件
5. 根據placement_info.json執行批次創建執行完成后，請確實檢查是否所有的連線到正常完成，
6. 使用get_document_errors檢查是否錯誤訊息，直接使用grasshopper mcp修正不要創建程式碼
7. 請先確認所有slider的數值是否設置正確是否有對齊component_info.mmd規劃的數值，并使用"set_slider_properties"更新
   - 推薦使用 CLI 命令: python -m grasshopper_tools.cli auto-set-sliders GH_WIP/component_info.mmd
   - 命令會自動從component_info.mmd提取所有Number Slider的輸出值並設置
   - 命令會自動從component_id_map.json讀取實際組件ID（由execute-placement自動生成）
   - 命令會根據slider名稱自動確定合理的範圍（min/max）
8.使用"group_components"群組電池可以參考component_info.mmd
   - 推薦使用 CLI 命令: python -m grasshopper_tools.cli auto-group-components GH_WIP/component_info.mmd
   - 命令會自動從component_info.mmd提取所有subgraph定義及其組件列表
   - 命令會根據subgraph類型自動分配顏色（TOP=淺藍色, LEG_BASE=淺橙色, LEG_PLANES=淺綠色, ORIENT_GROUP=淺紅色）
   - 命令會自動從component_id_map.json讀取實際組件ID（由execute-placement自動生成）

執行批次創建命令的方法:

使用 CLI 命令 execute-placement
- 執行命令: python -m grasshopper_tools.cli execute-placement GH_WIP/placement_info.json
- 命令會自動：
  1. 讀取placement_info.json文件
  2. 按照順序執行所有add_component命令
  3. 保存componentId到實際組件ID的映射到component_id_map.json文件
  4. 執行所有connect_components命令
  5. 顯示執行進度和結果統計
  6. 自動保存組件ID映射文件，供後續自動化命令使用

- 確保placement_info.json文件格式正確且完整
- 如果組件創建失敗，後續的連接命令可能會失敗
- 建議在執行前先檢查placement_info.json的完整性
- 執行過程中會顯示進度信息和錯誤提示
- 如果遇到錯誤，檢查GUID是否正確、參數名稱是否匹配

執行結果檢查:
- 檢查所有組件是否成功創建
- 檢查所有連接是否成功建立
- 查看執行統計：成功/失敗數量
- 如有失敗，查看錯誤信息並修正placement_info.json
- 確認component_id_map.json文件已生成（用於後續自動化腳本）

自動化腳本使用說明:

1. auto-set-sliders - 自動設置Slider參數
   - 功能：從component_info.mmd自動提取所有Number Slider的輸出值並設置
   - 執行：python -m grasshopper_tools.cli auto-set-sliders GH_WIP/component_info.mmd
   - 前置條件：需先執行execute_placement.py生成component_id_map.json
   - 工作流程：
     a. 解析component_info.mmd，提取所有Number Slider組件及其輸出值
     b. 從component_id_map.json讀取實際組件ID映射
     c. 根據slider名稱自動確定合理的範圍（min/max）
     d. 使用set_slider_properties命令批量設置所有slider
   - 輸出：顯示設置進度和結果統計

2. auto-group-components - 自動群組組件
   - 功能：從component_info.mmd自動提取subgraph定義並進行群組
   - 執行：python -m grasshopper_tools.cli auto-group-components GH_WIP/component_info.mmd
   - 前置條件：需先執行execute_placement.py生成component_id_map.json
   - 工作流程：
     a. 解析component_info.mmd，提取所有subgraph定義及其組件列表
     b. 從component_id_map.json讀取實際組件ID映射
     c. 根據subgraph類型自動分配顏色：
        - TOP (桌面): 淺藍色 RGB(225, 245, 255)
        - LEG_BASE (桌腳基礎): 淺橙色 RGB(255, 244, 225)
        - LEG_PLANES (桌腳位置平面): 淺綠色 RGB(232, 245, 233)
        - ORIENT_GROUP (Orient複製組): 淺紅色 RGB(255, 235, 238)
     d. 使用group_components命令批量創建群組
   - 輸出：顯示群組進度和結果統計

推薦執行順序:
1. 執行 execute-placement 創建組件和連接（自動生成component_id_map.json）
   python -m grasshopper_tools.cli execute-placement GH_WIP/placement_info.json
2. 使用 get-errors 檢查並修正錯誤
   python -m grasshopper_tools.cli get-errors
3. 執行 auto-set-sliders 自動設置所有slider參數
   python -m grasshopper_tools.cli auto-set-sliders GH_WIP/component_info.mmd
4. 執行 auto-group-components 自動群組所有組件
   python -m grasshopper_tools.cli auto-group-components GH_WIP/component_info.mmd

placement_info.json文件結構:
```json
{
  "description": "描述文字 - 根據 component_info.mmd 生成",
  "commands": [
    // add_component 命令列表
    // connect_components 命令列表
  ]
}
```

add_component命令格式:
```json
{
  "comment": "組件說明（可選）",
  "type": "add_component",
  "parameters": {
    "guid": "組件GUID（從component_info.mmd中獲取）",
    "x": X座標（從component_info.mmd中獲取）,
    "y": Y座標（從component_info.mmd中獲取）
  },
  "componentId": "組件ID（用於後續連接時引用）"
}
```

connect_components命令格式:
```json
{
  "comment": "連接說明（可選）",
  "type": "connect_components",
  "parameters": {
    "sourceId": "源組件的componentId",
    "sourceParam": "源組件的輸出參數名稱",
    "targetId": "目標組件的componentId",
    "targetParam": "目標組件的輸入參數名稱"
  }
}
```

範例:
```json
{
  "description": "桌子創建執行序列 - 根據 component_info.mmd 生成",
  "commands": [
    {
      "comment": "=== 桌面模組 ===",
      "type": "add_component",
      "parameters": {
        "guid": "80c5f8c2-e867-4fc9-9424-76e26cf19dd9",
        "x": 100,
        "y": 100
      },
      "componentId": "XY_PLANE_TOP"
    },
    {
      "comment": "=== 連接命令 - 桌面模組連接 ===",
      "type": "connect_components",
      "parameters": {
        "sourceId": "XY_PLANE_TOP",
        "sourceParam": "Plane",
        "targetId": "RECTANGLE_TOP",
        "targetParam": "Plane"
      }
    }
  ]
}
```

重要規則:
1. 所有add_component命令必須在connect_components命令之前
2. componentId必須與component_info.mmd中的組件標識符一致
3. 參數名稱（sourceParam、targetParam）必須與component_info.mmd中箭頭標示的參數名稱一致
4. GUID必須使用component_info.mmd中查詢到的正確GUID
5. 位置座標（x, y）必須與component_info.mmd中標示的位置一致
6. 連接順序應該按照數據流向，從輸入組件到輸出組件

注意事項:
- 確保所有組件都有唯一的componentId
- 確保所有連接的sourceId和targetId都對應到已定義的componentId
- 參數名稱區分大小寫，必須完全匹配
- 如果component_info.mmd中有註釋說明，應該在對應命令中添加comment字段
- 建議將相關的組件和連接分組，使用comment字段標註模組名稱

## Step 6: 清理GH_WIP檔案

根據完成時間與任務名稱在GH_PKG創建資料夾ex.202512201344-create_table
移動GH_WIP所有檔案到GH_PKG新建的子資料夾
完成任務條件:完成GH_PKG創建資料夾創建並移動本次任務檔案並確認GH_WIP清空

