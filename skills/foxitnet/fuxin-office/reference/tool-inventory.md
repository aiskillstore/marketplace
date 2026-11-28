# 三产品工具清单（权威快照）

> 来源：`AI-Toolkit/fuxinaiservice/resources/products/{Word,Excel,PowerPoint}/tools.json`——网关工具注册的**唯一事实来源**，网关不硬编码。
> 本文档为人工按功能分组整理，**工具名与数量逐条取自 JSON**，未做任何推测。
> 修改本文件时须重新比对 `tools.json`，避免与权威数据源脱节。

## 一、命名与字段口径

网关对外工具全名 = **产品 ID + 双下划线 + 工具短名**：`{产品ID}__{工具名}`，如 `Word__get_path`。
单下划线（`Word_get_path`）、缺前缀（`get_path`）、应用名作前缀（`FuxinOfficeWord_get_path`）均返回 `tool not found`，**无容错别名**。

`tools.json` 每条工具的结构：

| 字段 | 含义 |
|---|---|
| `name` | 工具**短名**，不含产品前缀 |
| `description` | 中文说明，供 Agent 判断何时调用 |
| `input_schema` | JSON Schema，定义入参 |
| `confirm_required` | `true` 表示执行前须向用户确认 |
| `visibility_level` | 工具暴露层级：`1` 主要（预置在 Agent 工具列表中）／`2` 扩展（按需检索） |
| `timeout_ms` | 超时；`30000` 为默认，`180000` 用于批量/生成类长任务 |

### 三产品**必然不一致**的几个点（易错）

| 意图 | Word | Excel | PowerPoint |
|---|---|---|---|
| 取文档/工作簿/演示稿信息 | `get_doc_info` | **无**，用 `get_sheet_summary` | `get_document_info` |
| 取状态 | `get_doc_status` | **无** | **无** |
| 取路径 | `get_path` | `get_path` | `get_path` |
| 保存 / 另存为 | `save_document` | `save_document` | `save_document` |

> `get_doc_info` 与 `get_document_info` 是**两个不同工具名**，分属不同产品，不能互相替换。
> **`save_document_as` 三产品均不存在**；另存为 = `save_document` 传 `path`（绝对路径）+ 可选 `format`（缺省从扩展名推断）。

### 三产品共同项

| 工具 | 说明 |
|---|---|
| `begin_batch` / `end_batch` | 批次原语，把多次改动合成一次撤销 |
| `save_document` | 保存（需确认）；传 `path` 即另存为 |
| `undo_action` / `redo_action` | 撤销 / 重做（需确认） |
| `trigger_document_proofread` | 触发拼写语法校对 |
| `get_path` / `get_document_text` | 取文件路径 / 取全文 |

---

## 二、Word（60 个工具）

### 文档信息与状态（只读）（6）

| 工具全名 | 确认 | 级别 | 说明 |
|---|---|---|---|
| `Word__get_path` |  | 1 | 获取当前文档本地存储完整路径。 |
| `Word__get_doc_info` |  | 1 | 获取文档基础统计信息（字数、页数、段落数等）。 |
| `Word__get_doc_status` |  | 1 | 获取当前Word文档的状态信息：是否只读、是否为空文档、是否已修改、页数。 |
| `Word__get_document_text` |  | 1 | 获取Word文档的文本内容。默认返回全文；若传入可选的start/end（绝对偏移量，由get_pos获取），则返回该区间内的文本片段。… |
| `Word__get_document_paragraphs` |  | 2 | 获取当前Word文档的段落信息数组，包含大纲、位置、样式、内容、段落索引（0基准）。 |
| `Word__get_outline` |  | 1 | 获取当前Word文档的大纲结构。遍历全文段落，提取所有带大纲级别的标题，返回层级列表。用于快速了解文档结构。 |

### 光标与选区（6）

| 工具全名 | 确认 | 级别 | 说明 |
|---|---|---|---|
| `Word__get_pos` |  | 2 | 获取当前Word文档中光标的位置信息。返回start和end（绝对偏移量），可传给set_pos或insert_text_at_pos来… |
| `Word__set_pos` |  | 2 | 将光标设置到指定位置。传入start和end（由get_pos返回的绝对偏移量）。 |
| `Word__move_pos` |  | 2 | 按规则移动文档光标位置。 |
| `Word__get_selection_text` |  | 1 | 获取当前Word文档中选区（高亮选中）的文本内容。 |
| `Word__select_range` |  | 2 | 按绝对字符位置设置文本选区。all=true 时全选整篇文档，无需传 start/end。 |
| `Word__get_current_paragraph_text` |  | 2 | 获取Word文档中当前光标所在段落的文本内容。 |

### 文本写入与编辑（10）

| 工具全名 | 确认 | 级别 | 说明 |
|---|---|---|---|
| `Word__append_text` |  | 2 | 续写：在选中文本末尾（或当前光标处）纯追加新内容，追加内容自动继承光标处格式。用于「续写接下来的内容/接着写/在末尾追加」等场景。 |
| `Word__insert_text` |  | 2 | 插入文本。默认仅在当前光标位置纯插入；若当前有选区，必须改用 rewrite_selection、append_text 或 inser… |
| `Word__insert_paragraphs` |  | 2 | 在指定位置插入一个或多个新段落（结构化插入：新增一节/插入标题/新增条目）。位置用段落索引（afterParagraph，来自 get_… |
| `Word__insert_page_break` |  | 2 | 在光标处插入分页符。 |
| `Word__replace_text` |  | 2 | 在文档中搜索文本并全部替换为指定文本。 |
| `Word__delete_selection` |  | 2 | 删除当前选中的内容 |
| `Word__rewrite_selection` |  | 2 | 改写当前选中文字的正文内容，并保留原文的字符/段落格式。 |
| `Word__rewrite_paragraphs` |  | 2 | 按段落索引逐段改写并保留格式。每段以 newText（不得含换行，一段对一段）替换原文。传入多个段落时自动从后往前处理，段落总数保持不变… |
| `Word__write_report` |  | 1 | 整篇文档生成场景：生成含标题、多级章节、表格、图片的Word文档，适用于报告、文章、作文、游记、散文等完整内容。支持自定义字体字号、对齐… |
| `Word__clipboard_edit` |  | 2 | 对当前选中内容执行剪贴板操作。cut=剪切（删除并复制到剪贴板）；copy=复制到剪贴板；paste=粘贴剪贴板内容到当前光标。 |

### 查找替换与批量处理（7）

| 工具全名 | 确认 | 级别 | 说明 |
|---|---|---|---|
| `Word__find_text` |  | 2 | 文档内检索文本，匹配成功后光标跳转至首个匹配位置，并返回命中位置（all=false，默认）；all=true 时返回全文所有匹配位置数… |
| `Word__batch_find_replace` |  | 2 | 批量查找替换：在单个事务中执行多组查找替换规则。默认替换全文；也可以用scope限定到选区、指定范围或某一段。每条规则可独立设置匹配选项… |
| `Word__batch_highlight` |  | 2 | 批量高亮：在单个事务中对多组文本规则批量添加荧光高亮。默认作用于全文；也可通过scope限定到选区、指定范围或某一段。 |
| `Word__highlight_and_comment` |  | 1 | 高亮批注场景：查找目标文本并添加高亮和/或批注。支持多组目标，每组可独立设置颜色、批注、匹配选项、加粗。支持处理全部匹配项或仅首个。 |
| `Word__unify_terminology` |  | 1 | 术语统一/排版整理场景：批量查找替换指定术语，可选统一全文格式。内部自动编排替换和格式设置操作。 |
| `Word__begin_batch` |  | 1 | 开启批量操作事务。后续的多个操作将合并为一个事务，一次Ctrl+Z可全部撤销。必须与end_batch配对使用。不支持嵌套。执行批量生成… |
| `Word__end_batch` |  | 1 | 结束批量操作事务，与begin_batch配对使用。结束后可通过一次Ctrl+Z撤销整个批量事务内的全部操作。 |

### 字符与段落格式（9）

| 工具全名 | 确认 | 级别 | 说明 |
|---|---|---|---|
| `Word__apply_style` |  | 2 | 将指定样式应用至光标所在段落。 |
| `Word__set_char_format` |  | 2 | 设置字符格式（加粗/斜体/下划线/着重号/字号/高亮/字色）。默认作用于当前选区/光标处；也可传 paragraphIndexes 把格… |
| `Word__get_char_format` |  | 2 | 读取当前Word文档中光标位置/选区的字符格式信息（字号、加粗、斜体、下划线、着重号、高亮色等）。与 set_char_format 互… |
| `Word__set_para_format` |  | 2 | 设置段落格式（对齐、行距、缩进、段前/段后间距）。默认作用于当前光标所在段落；也可传 paragraphIndexes 批量应用到多段，… |
| `Word__get_para_format` |  | 2 | 读取当前Word文档中光标所在段落的格式信息（对齐方式、行距、缩进等）。与set_para_format互补，用于先读取再修改。 |
| `Word__set_para_outline_level` |  | 2 | 设置段落大纲级别。默认作用于当前光标所在段落；也可传 paragraphIndexes 批量应用到多段，不影响当前光标/选区。 |
| `Word__get_para_outline_level` |  | 2 | 获取段落的大纲级别。默认读取当前光标所在段落；也可传 paragraphIndexes 批量读取多段，不影响当前光标/选区。 |
| `Word__set_document_format` |  | 2 | 全文档排版：按大纲级别为各级标题与正文分别设置段落格式和字符格式（建议先 get_outline 了解文档大纲，再传 levels 数组… |
| `Word__get_style_list` |  | 2 | 返回文档中全部可用样式名称列表。 |

### 页眉页脚与页码（2）

| 工具全名 | 确认 | 级别 | 说明 |
|---|---|---|---|
| `Word__set_header_footer` |  | 2 | 配置页眉/页脚内容与样式。 |
| `Word__set_page_number_options` |  | 2 | 全局配置文档页码参数。 |

### 表格（5）

| 工具全名 | 确认 | 级别 | 说明 |
|---|---|---|---|
| `Word__insert_table` |  | 2 | 在当前光标位置插入空白表格。 |
| `Word__insert_structured_table` |  | 2 | 在当前Word文档光标位置插入结构化表格（含表头和数据）。自动创建表格并尝试填充单元格内容。比insert_table+手动填写更便捷。 |
| `Word__table_edit` |  | 2 | 操作光标所在表格的行、列；insertPicture 时通过 SetCellPos 定位到指定单元格后插入图片。 |
| `Word__get_cell_shape` |  | 2 | 读取当前Word文档中光标所在表格单元格的格式信息（边框、底纹、对齐方式等）。光标必须位于表格单元格内。与set_cell_shape互… |
| `Word__set_cell_shape` |  | 2 | 设置当前Word文档中光标所在表格单元格的格式。光标必须位于表格单元格内。只修改指定的键，未指定的键保持不变。alignment：0=左… |

### 图片与目录（3）

| 工具全名 | 确认 | 级别 | 说明 |
|---|---|---|---|
| `Word__insert_picture` |  | 2 | 在当前光标位置插入图片。 |
| `Word__set_picture_properties` |  | 2 | 修改指定图片布局、尺寸、边框等属性。 |
| `Word__insert_table_of_contents` |  | 2 | 在光标位置自动插入文档目录。 |

### 批注与修订（7）

| 工具全名 | 确认 | 级别 | 说明 |
|---|---|---|---|
| `Word__comment_edit` |  | 2 | 文档批注增删操作。 |
| `Word__batch_add_comment` |  | 2 | 批量加批注：在单个事务中为多组关键词添加批注。默认对全文查找关键词并在每个匹配处加批注；也可通过scope限定到选区、指定范围或某一段。… |
| `Word__get_comment_list` |  | 2 | 获取当前Word文档的批注列表：批注总数、作者列表。可配合get_comment_text按索引读取具体批注内容。 |
| `Word__get_comment_text` |  | 2 | 读取指定索引批注的正文内容。 |
| `Word__revision_action` |  | 2 | 对指定修订记录执行接受或拒绝操作。参数名为 action，可取 accept（接受）或 reject（拒绝）。 |
| `Word__get_revision_list` |  | 2 | 返回文档内所有修订记录列表。 |
| `Word__set_revision_mode` |  | 2 | 开启/关闭文档修订模式。 |

### 校对与检查（2）

| 工具全名 | 确认 | 级别 | 说明 |
|---|---|---|---|
| `Word__trigger_document_proofread` |  | 2 | 触发文档智能校对：显示 AI 助手工作区面板，切换到「智能校对」技能并启动文档校对流程。 |
| `Word__checklist_review` |  | 1 | 清单审查场景：对文档中的清单项逐项添加批注和/或在文档末尾插入审查汇总表。支持自定义汇总表列、高亮命中项、自定义批注作者。 |

### 保存与撤销（3）

| 工具全名 | 确认 | 级别 | 说明 |
|---|---|---|---|
| `Word__save_document` | 确认 | 1 | 保存当前文档。不传path时直接保存当前文档；传入path(绝对路径)则另存为到指定路径，format可选（缺省从扩展名推断）。 |
| `Word__undo_action` | 确认 | 1 | 撤销当前文档的上一步操作，相当于Ctrl+Z。 |
| `Word__redo_action` | 确认 | 2 | 重做当前文档中被撤销的操作，相当于Ctrl+Y。 |

---

## 三、Excel（66 个工具）

### 工作簿与工作表（只读）（7）

| 工具全名 | 确认 | 级别 | 说明 |
|---|---|---|---|
| `Excel__get_path` |  | 1 | 获取当前文档本地存储完整路径。 |
| `Excel__get_sheet_names` |  | 2 | 返回所有工作表名称列表。 |
| `Excel__get_sheet_index` |  | 2 | 返回指定名称工作表的0基索引，不存在返回-1。 |
| `Excel__get_active_sheet_index` |  | 2 | 返回当前活动工作表的0基索引。 |
| `Excel__sheet_exists` |  | 2 | 返回指定名称的工作表是否存在。 |
| `Excel__get_sheet_summary` |  | 1 | 获取工作表数据摘要：非空单元格数、数据边界（起始/最大行列），用于快速了解表格规模。sheetIndex 指定目标表；dataRange… |
| `Excel__get_document_text` |  | 1 | 获取当前Excel工作簿的全文内容。maxLength用于限制返回的最大字符数（小于等于0表示不限制）。 |

### 工作表管理（5）

| 工具全名 | 确认 | 级别 | 说明 |
|---|---|---|---|
| `Excel__activate_sheet` |  | 2 | 激活指定工作表。 |
| `Excel__add_sheet` |  | 2 | 新增一个工作表。 |
| `Excel__delete_sheet` |  | 2 | 删除指定工作表。 |
| `Excel__rename_sheet` |  | 2 | 重命名当前活动工作表。 |
| `Excel__set_sheet_visible` |  | 2 | 设置指定工作表显示或隐藏。 |

### 单元格读取（7）

| 工具全名 | 确认 | 级别 | 说明 |
|---|---|---|---|
| `Excel__get_active_cell` |  | 2 | 返回当前活动单元格位置。 |
| `Excel__get_cell_values` |  | 1 | 读取单元格值。方式①ranges（推荐）：按 A1 记法范围读取，返回二维 data[行][列] 与同形状 addresses[行][列… |
| `Excel__get_cell_value_type` |  | 2 | 返回指定单元格的值类型。返回值：Empty/Number/String/Boolean/Error。 |
| `Excel__get_selection` |  | 2 | 返回当前选区范围。 |
| `Excel__get_selection_values` |  | 1 | 返回当前选区内的单元格值，结果为二维字符串数组（如 [["1","hello"],["2","world"]]）。 |
| `Excel__find_cells_by_value` |  | 2 | 在当前Excel文档中搜索匹配值的单元格，返回匹配的行列坐标列表。支持精确匹配和模糊匹配（包含）。比逐个调用get_cell_value… |
| `Excel__get_outlier_cells` |  | 2 | 返回给定范围内被判定为异常值的单元格地址列表。 |

### 单元格写入与格式（7）

| 工具全名 | 确认 | 级别 | 说明 |
|---|---|---|---|
| `Excel__set_cell_values` |  | 1 | 设置一个或多个单元格的值；sheetIndex 统一作用于全部单元格。 |
| `Excel__set_cell_format` |  | 2 | 设置指定范围单元格格式（字体、颜色、数字/日期格式等）。仅传入需要设置的项，未传入的项保持不变。 |
| `Excel__copy_cell_format` |  | 2 | 格式刷：把源区域（sourceRange）的单元格样式同步到目标区域（targetRange），可携带 set_cell_format … |
| `Excel__set_conditional_format` |  | 2 | 为指定范围应用条件格式规则，每条规则拥有独立的范围、类型和预设。 |
| `Excel__highlight_by_condition` |  | 1 | 按条件高亮单元格场景：对指定范围应用条件格式规则，自动高亮满足条件的单元格。支持数值比较、文本包含、重复值等多种条件类型。色阶/数据条/… |
| `Excel__copy_to_clipboard` |  | 2 | 将给定范围复制到剪贴板。 |
| `Excel__paste_special` |  | 2 | 将剪贴板内容以特殊方式粘贴到指定范围。粘贴方式：All、Values、Formats、ValuesAndFormats、Formulas… |

### 行列操作（6）

| 工具全名 | 确认 | 级别 | 说明 |
|---|---|---|---|
| `Excel__insert_row` |  | 2 | 在指定行插入一行，未指定时使用当前活动单元格所在行。 |
| `Excel__delete_row` |  | 2 | 删除指定行。 |
| `Excel__insert_column` |  | 2 | 在指定列插入一列，未指定时使用当前活动单元格所在列。 |
| `Excel__delete_column` |  | 2 | 删除指定列。 |
| `Excel__get_entire_row_range` |  | 2 | 返回整行范围。 |
| `Excel__get_entire_column_range` |  | 2 | 返回整列范围。 |

### 区域运算（2）

| 工具全名 | 确认 | 级别 | 说明 |
|---|---|---|---|
| `Excel__union_ranges` |  | 2 | 返回多个范围并集组成的单个范围字符串。 |
| `Excel__intersect_ranges` |  | 2 | 返回两个范围的交集范围字符串，若无交集返回空字符串。 |

### 表格对象（7）

| 工具全名 | 确认 | 级别 | 说明 |
|---|---|---|---|
| `Excel__create_table` |  | 2 | 在指定范围上创建SmartTable。 |
| `Excel__set_table_resize` |  | 2 | 将当前表格范围调整为新范围。 |
| `Excel__is_cell_in_table` |  | 2 | 返回指定单元格是否位于表格区域内。 |
| `Excel__get_table_column_count` |  | 2 | 返回当前表格列数。 |
| `Excel__get_table_column_index` |  | 2 | 返回表格中与表头名称匹配的列索引。 |
| `Excel__get_table_column_range` |  | 2 | 返回表格中与列名匹配的列范围。 |
| `Excel__get_table_column_range_by_index` |  | 2 | 返回表格中第idx个列的范围。 |

### 图表（10）

| 工具全名 | 确认 | 级别 | 说明 |
|---|---|---|---|
| `Excel__add_chart` |  | 2 | 添加图表。chartType如Bar2DClusterdCol、LineClusterd、PieNormal、AreaClusterd、… |
| `Excel__batch_create_charts` |  | 1 | 批量创建图表场景：根据数据范围批量创建多个图表，支持设置标题、图例、系列方向等。内部自动编排图表创建、数据源设置、标题配置等操作。 |
| `Excel__get_selected_chart_id` |  | 2 | 返回当前选中的图表ID。 |
| `Excel__set_chart_source_data` |  | 2 | 设置图表源数据范围。 |
| `Excel__set_chart_style` |  | 2 | 更改图表类型。 |
| `Excel__set_chart_title` |  | 2 | 设置图表标题文本。 |
| `Excel__set_chart_axis_config` |  | 2 | 配置图表坐标轴。axis: 1=分类/X轴, 2=数值/Y轴。 |
| `Excel__set_chart_data_label_config` |  | 2 | 配置图表数据标签。可控制是否显示系列名/分类名/数值、分隔符、标签位置等。 |
| `Excel__set_chart_has_legend` |  | 2 | 设置图表是否显示图例。 |
| `Excel__set_chart_plot_by` |  | 2 | 设置图表系列方向。true表示按行，false表示按列。 |

### 数据透视表（4）

| 工具全名 | 确认 | 级别 | 说明 |
|---|---|---|---|
| `Excel__create_pivot_table` |  | 2 | 根据源数据创建数据透视表。 |
| `Excel__get_pivot_anchor` |  | 2 | 返回指定工作表上的数据透视表锚定单元格位置。 |
| `Excel__get_pivot_field_names` |  | 2 | 返回指定数据透视表可用字段名列表。 |
| `Excel__set_pivot_field_orientation` |  | 2 | 设置数据透视表字段方向。方向：Hidden、Row、Column、Page、Data。 |

### 数据处理工具（4）

| 工具全名 | 确认 | 级别 | 说明 |
|---|---|---|---|
| `Excel__goal_seek` |  | 2 | 目标值求解。反向求解changingRange单元格的值，使公式结果等于targetValue。 |
| `Excel__extract_data_to_new_sheet` |  | 1 | 提取数据到新工作表场景：从源范围提取数据并在新工作表中生成结构化表格。`sourceSheet` 支持工作表名称或索引（0 基）；`columns` 支持列字母或 0 基索引。另支持行筛选（filter）、按列排序（sortBy/sortOrder）、数字格式（numberFormats）、表头样式自定义。 |
| `Excel__validate_custom` |  | 2 | 在给定范围设置自定义公式数据验证。 |
| `Excel__validate_text_list` |  | 2 | 在给定范围设置列表型数据验证。 |

### 批处理、校验与保存（7）

| 工具全名 | 确认 | 级别 | 说明 |
|---|---|---|---|
| `Excel__begin_batch` |  | 1 | 开启批量操作事务。后续的多个操作将合并为一个事务，一次Ctrl+Z可全部撤销。必须与end_batch配对使用。不支持嵌套。执行批量生成… |
| `Excel__end_batch` |  | 1 | 结束批量操作事务，与begin_batch配对使用。结束后可通过一次Ctrl+Z撤销整个批量事务内的全部操作。 |
| `Excel__trigger_document_proofread` |  | 2 | 触发文档智能校对：显示 AI 助手工作区面板，切换到「智能校对」技能并启动文档校对流程。 |
| `Excel__set_document_read_only` |  | 2 | 设置当前文档是否只读。 |
| `Excel__save_document` | 确认 | 1 | 保存当前文档。不传path时直接保存当前文档；传入path(绝对路径)则另存为到指定路径，format可选（缺省从扩展名推断）。 |
| `Excel__undo_action` | 确认 | 1 | 撤销当前文档的上一步操作，相当于Ctrl+Z。 |
| `Excel__redo_action` | 确认 | 2 | 重做当前文档中被撤销的操作，相当于Ctrl+Y。 |

---

## 四、PowerPoint（37 个工具）

### 演示稿信息（只读）（8）

| 工具全名 | 确认 | 级别 | 说明 |
|---|---|---|---|
| `PowerPoint__get_path` |  | 1 | 获取当前文档本地存储完整路径。 |
| `PowerPoint__get_document_info` |  | 1 | 获取当前PPT文档的基础信息：文档ID、路径、幻灯片数量、是否为空。 |
| `PowerPoint__get_document_text` |  | 1 | 获取当前PPT演示文稿的全文内容。maxLength用于限制返回的最大字符数（小于等于0表示不限制）。 |
| `PowerPoint__get_ppt_outline` |  | 1 | 获取当前PPT文档的纯文本大纲。遍历所有幻灯片，提取每页文本内容，返回精简的层级列表，不含形状元数据。 |
| `PowerPoint__get_slide_count` |  | 2 | 获取当前PPT文档的幻灯片总数。 |
| `PowerPoint__get_slide_overview` |  | 2 | 获取当前PPT文档的幻灯片概览（含形状元数据）。遍历所有幻灯片，返回每张幻灯片的形状摘要（形状ID、类型、文本内容）和备注摘要。如只需纯… |
| `PowerPoint__get_slide_size` |  | 2 | 获取当前PPT文档的幻灯片尺寸（宽度和高度，单位英寸）。 |
| `PowerPoint__get_slide_layouts` |  | 2 | 获取当前PPT文档中所有可用的幻灯片布局（模板）列表。每项包含masterIndex、layoutIndex、name和type（Sli… |

### 幻灯片内容读取（5）

| 工具全名 | 确认 | 级别 | 说明 |
|---|---|---|---|
| `PowerPoint__get_slide_text` |  | 1 | 获取PPT文档中指定幻灯片的文本内容（含形状文本，默认也含演讲者备注）。 |
| `PowerPoint__get_slide_note_text` |  | 2 | 获取指定幻灯片的演讲者备注文本。 |
| `PowerPoint__find_text_in_slides` |  | 2 | 在当前PPT文档的所有幻灯片中搜索文本关键词（含形状文本与演讲者备注），返回匹配的页码、形状ID和匹配片段。 |
| `PowerPoint__get_shapes` |  | 2 | 获取指定幻灯片上的所有形状列表，包含id、类型、位置、尺寸、文本和子形状。 |
| `PowerPoint__get_shape_text` |  | 2 | 获取指定幻灯片中指定形状的文本内容。 |

### 选区获取（3）

| 工具全名 | 确认 | 级别 | 说明 |
|---|---|---|---|
| `PowerPoint__get_selected_slides` |  | 2 | 获取当前选中的幻灯片索引列表（0基准）。 |
| `PowerPoint__get_selected_shapes` |  | 2 | 获取当前活动幻灯片上选中的形状列表。 |
| `PowerPoint__get_selected_text_range` |  | 1 | 获取当前选中的文本范围信息（形状ID、文本、起始位置、长度），无选中时返回null。 |

### 选区设置（3）

| 工具全名 | 确认 | 级别 | 说明 |
|---|---|---|---|
| `PowerPoint__set_selected_slides` |  | 2 | 设置当前选中的幻灯片。 |
| `PowerPoint__set_selected_shapes` |  | 2 | 设置指定幻灯片上选中的形状。shapeIds为形状ID数组。 |
| `PowerPoint__set_selected_text_range` |  | 2 | 设置指定形状中的文本选区。 |

### 幻灯片增删与编排（5）

| 工具全名 | 确认 | 级别 | 说明 |
|---|---|---|---|
| `PowerPoint__insert_slides` |  | 1 | 插入一张或多张幻灯片。slides为数组（元素含 index[0基准]、layout[SlideLayoutType枚举名，默认Blan… |
| `PowerPoint__delete_slides` |  | 1 | 删除一张或多张幻灯片。 |
| `PowerPoint__organize_deck` |  | 1 | 整理演示文稿场景：移动、删除、复制幻灯片，应用布局模板。复制为整段复制，保留源页全部内容与备注。所有索引均为 0 基准且指操作前的原始文… |
| `PowerPoint__apply_slide_template` |  | 2 | 将指定布局（模板）重新应用到现有幻灯片。形状/文本内容保留，仅占位符框架发生变化。masterIndex/layoutIndex来自ge… |
| `PowerPoint__generate_deck` |  | 1 | 生成演示文稿场景：根据大纲批量创建幻灯片，每页含标题和正文。支持全局默认样式与逐页样式覆盖（字号/字体/颜色/位置）；每页还可用 blo… |

### 形状与文本写入（6）

| 工具全名 | 确认 | 级别 | 说明 |
|---|---|---|---|
| `PowerPoint__insert_shape` |  | 1 | 在指定幻灯片上插入一个形状。shapeType为ShapeType枚举名（Rectangle/Ellipse/Triangle等）。x/… |
| `PowerPoint__insert_text_boxes` |  | 1 | 插入一个或多个文本框。textBoxes为数组（元素含 slideIndex、text、可选x/y/w/h/fontSize/fontF… |
| `PowerPoint__delete_shapes` |  | 1 | 删除一个或多个形状。shapes为数组，每条含slideIndex和shapeId。 |
| `PowerPoint__set_shape_texts` |  | 1 | 设置一个或多个形状的文本内容。updates为数组（元素含slideIndex、shapeId、text）。 |
| `PowerPoint__set_shape_options` |  | 2 | 修改一个或多个形状的属性（位置、尺寸、填充颜色、边框线）。shapes为数组（元素含slideIndex、shapeId、可选x/y/w… |
| `PowerPoint__edit_selection` |  | 1 | 编辑选区内容场景：对当前选中的幻灯片形状进行文本修改、形状属性调整（填充色/位置/尺寸/边框）、备注编辑。支持按形状ID指定目标，或自动… |

### 备注（1）

| 工具全名 | 确认 | 级别 | 说明 |
|---|---|---|---|
| `PowerPoint__set_slide_notes` |  | 1 | 设置一张或多张幻灯片的演讲者备注文本。notes为数组，每条含slideIndex、text。 |

### 批处理、校验与保存（6）

| 工具全名 | 确认 | 级别 | 说明 |
|---|---|---|---|
| `PowerPoint__begin_batch` |  | 1 | 开启批量操作事务。后续的多个操作将合并为一个事务，一次Ctrl+Z可全部撤销。必须与end_batch配对使用。不支持嵌套。执行批量生成… |
| `PowerPoint__end_batch` |  | 1 | 结束批量操作事务，与begin_batch配对使用。结束后可通过一次Ctrl+Z撤销整个批量事务内的全部操作。 |
| `PowerPoint__trigger_document_proofread` |  | 2 | 触发文档智能校对：显示 AI 助手工作区面板，切换到「智能校对」技能并启动文档校对流程。 |
| `PowerPoint__save_document` | 确认 | 1 | 保存当前文档。不传path时直接保存当前文档；传入path(绝对路径)则另存为到指定路径，format可选（缺省从扩展名推断）。 |
| `PowerPoint__undo_action` | 确认 | 1 | 撤销当前文档的上一步操作，相当于Ctrl+Z。 |
| `PowerPoint__redo_action` | 确认 | 2 | 重做当前文档中被撤销的操作，相当于Ctrl+Y。 |

---

## 五、汇总

| 产品 | 工具数 | 需确认 | 级别 1 | 级别 2 |
|---|---|---|---|---|
| Word | 60 | 3 | 14 | 46 |
| Excel | 66 | 3 | 13 | 53 |
| PowerPoint | 37 | 3 | 20 | 17 |
| **合计** | **163** | | | |

> 三产品 `confirm_required=true` 的工具**完全一致**：`save_document`、`undo_action`、`redo_action`。
> 即只有「保存」和「撤销/重做」需要执行前确认，其余编辑类工具均直接执行（但写后应按 `SKILL.md` 提供撤销提示）。