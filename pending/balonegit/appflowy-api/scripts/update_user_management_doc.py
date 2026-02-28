import argparse
import json
import doc_grid_lib as grid_lib

"""
update_user_management_doc.py
-----------------------------
这是一个示例型的“文档就地修正 + Grid 规划表生成”脚本：
1) 按规则删除文档中表头顺序错误的 simple_table，并在需要时连同标题一起删除；
2) 删除旧的 Grid 区块，重建一份新的 Grid（数据库视图）并写入“看起来真实”的计划数据；
3) 作为可复用模板：你可以替换标题、字段与行数据，快速复用到其他文档。
   脚本名虽然针对“用户管理系统”示例，但逻辑是通用的“就地修正 + 规划表落库”流程。
"""

from _common import build_client, print_json, resolve_token
from appflowy_client import AppFlowyError

TIMELINE_HEADER = ["产出", "工作内容", "阶段/周次"]
FIELD_HEADER = ["说明", "示例值", "字段类型"]

TIMELINE_HEADING = "详细工作内容及时间计划表"
GRID_OLD_HEADING = "复杂表格：字段类型示例（10+行）"
GRID_NEW_HEADING = "详细工作计划表格（Grid）"
LEGACY_HEADINGS_TO_DELETE = {
    "详细工作内容及时间计划表（修正表头顺序）",
    GRID_OLD_HEADING,
}


def fetch_doc_json(client, token: str, workspace_id: str, view_id: str) -> dict:
    return grid_lib.fetch_collab_json(
        client, token, workspace_id, view_id, grid_lib.DOC_COLLAB_TYPE
    )


def fetch_doc_state(client, token: str, workspace_id: str, view_id: str) -> tuple[list[int], list[int]]:
    return grid_lib.fetch_collab_state(
        client, token, workspace_id, view_id, grid_lib.DOC_COLLAB_TYPE
    )


def post_web_update(client, token: str, workspace_id: str, view_id: str, update: list[int]) -> dict:
    return grid_lib.post_web_update(
        client, token, workspace_id, view_id, grid_lib.DOC_COLLAB_TYPE, update
    )


def list_databases(client, token: str, workspace_id: str) -> dict:
    return grid_lib.list_databases(client, token, workspace_id)


def get_database_fields(client, token: str, workspace_id: str, database_id: str) -> dict:
    return grid_lib.get_database_fields(client, token, workspace_id, database_id)


def add_database_field(client, token: str, workspace_id: str, database_id: str, field: dict) -> str:
    return grid_lib.add_database_field(client, token, workspace_id, database_id, field)


def add_database_row(client, token: str, workspace_id: str, database_id: str, cells: dict) -> str:
    return grid_lib.add_database_row(client, token, workspace_id, database_id, cells)


def list_row_ids(client, token: str, workspace_id: str, database_id: str) -> list[str]:
    return grid_lib.list_row_ids(client, token, workspace_id, database_id)


def create_database_view(client, token: str, workspace_id: str, view_id: str, name: str) -> None:
    return grid_lib.create_database_view(client, token, workspace_id, view_id, name)


def append_grid_section(
    client, token: str, workspace_id: str, view_id: str, heading: str, db_id: str, db_view_id: str
) -> dict:
    return grid_lib.append_grid_section(
        client, token, workspace_id, view_id, heading, db_id, db_view_id
    )


def parse_table_rows(blocks: dict, children_map: dict, text_map: dict, table_id: str) -> list[list[str]]:
    return grid_lib.parse_table_rows(blocks, children_map, text_map, table_id)


def _block_text(blocks: dict, children_map: dict, text_map: dict, block_id: str) -> str:
    return grid_lib.block_text(blocks, children_map, text_map, block_id)


def _page_children_order(doc: dict) -> list[str]:
    return grid_lib.page_children_order(doc)


def find_blocks_to_delete(doc_json: dict, rebuild_grid: bool = True) -> list[str]:
    doc = doc_json.get("data", {}).get("collab", {}).get("document", {})
    blocks = doc.get("blocks", {})
    meta = doc.get("meta", {})
    children_map = meta.get("children_map", {})
    text_map = meta.get("text_map", {})

    to_delete = set()
    for block_id, block in blocks.items():
        if not isinstance(block, dict) or block.get("ty") != "simple_table":
            continue
        rows = parse_table_rows(blocks, children_map, text_map, block_id)
        if not rows:
            continue
        if rows[-1] == TIMELINE_HEADER:
            to_delete.add(block_id)
            continue
        if rows[0] == FIELD_HEADER:
            to_delete.add(block_id)

    if rebuild_grid:
        for block_id, block in blocks.items():
            if isinstance(block, dict) and block.get("ty") == "grid":
                to_delete.add(block_id)

    # 规则：当标题下的内容被清空时，标题也删除
    ordered = _page_children_order(doc)
    heading_indices = []
    for idx, block_id in enumerate(ordered):
        block = blocks.get(block_id)
        if isinstance(block, dict) and block.get("ty") == "heading":
            title = _block_text(blocks, children_map, text_map, block_id)
            heading_indices.append((idx, block_id, title))

    for i, (idx, heading_id, title) in enumerate(heading_indices):
        if title in LEGACY_HEADINGS_TO_DELETE:
            to_delete.add(heading_id)
            continue
        if rebuild_grid and title == GRID_NEW_HEADING:
            to_delete.add(heading_id)
            continue
        next_idx = heading_indices[i + 1][0] if i + 1 < len(heading_indices) else len(ordered)
        section_blocks = [bid for bid in ordered[idx + 1 : next_idx] if bid]
        if title == TIMELINE_HEADING and section_blocks:
            to_delete.update(section_blocks)
        if not section_blocks:
            to_delete.add(heading_id)
            continue
        if all(bid in to_delete for bid in section_blocks):
            to_delete.add(heading_id)

    if not rebuild_grid:
        grid_sections = [
            s for s in grid_lib.find_grid_sections(doc_json) if s.get("heading_text") == GRID_NEW_HEADING
        ]
        if len(grid_sections) > 1:
            for section in grid_sections[:-1]:
                block_id = section.get("block_id")
                heading_id = section.get("heading_id")
                if block_id:
                    to_delete.add(block_id)
                if heading_id:
                    to_delete.add(heading_id)

    return list(to_delete)


def run_node_delete(doc_state: list[int], state_vector: list[int], delete_block_ids: list[str]) -> list[int]:
    return grid_lib.run_node_delete_doc_blocks(doc_state, state_vector, delete_block_ids)


def ensure_grid_database(
    client, token: str, workspace_id: str, view_id: str, grid_name: str
) -> tuple[str, str]:
    resp = client.create_page_view(
        token,
        workspace_id,
        {"parent_view_id": view_id, "layout": grid_lib.GRID_LAYOUT, "name": grid_name},
    )
    data = resp.get("data") if isinstance(resp, dict) else None
    if not isinstance(data, dict):
        raise AppFlowyError("Failed to create grid page view", response=resp)
    db_id = data.get("database_id")
    db_view_id = data.get("view_id")
    if not db_id or not db_view_id:
        raise AppFlowyError("Missing database_id/view_id in create page response", response=resp)
    return db_id, db_view_id


def ensure_fields(client, token: str, workspace_id: str, db_id: str) -> dict:
    fields_resp = get_database_fields(client, token, workspace_id, db_id)
    fields = fields_resp.get("data", []) if isinstance(fields_resp, dict) else []
    by_name = {f.get("name"): f for f in fields}

    def add_field_if_missing(name: str, field_type: int, type_option_data: dict | None = None) -> str:
        if name in by_name and by_name[name].get("id"):
            return by_name[name]["id"]
        payload = {"name": name, "field_type": field_type}
        if type_option_data is not None:
            payload["type_option_data"] = type_option_data
        field_id = add_database_field(client, token, workspace_id, db_id, payload)
        fields_resp_local = get_database_fields(client, token, workspace_id, db_id)
        fields_local = fields_resp_local.get("data", []) if isinstance(fields_resp_local, dict) else []
        for f in fields_local:
            if f.get("id") == field_id:
                by_name[f.get("name")] = f
        return field_id

    primary_field = next((f for f in fields if f.get("is_primary")), None)
    primary_id = primary_field.get("id") if primary_field else None
    primary_name = primary_field.get("name") if primary_field else None

    def select_content(options: list[dict]) -> str:
        return json.dumps({"options": options}, ensure_ascii=False)

    phase_options = [
        {"id": "phase-plan", "name": "规划", "color": "Yellow"},
        {"id": "phase-design", "name": "设计", "color": "Blue"},
        {"id": "phase-dev", "name": "开发", "color": "Purple"},
        {"id": "phase-test", "name": "测试", "color": "Orange"},
        {"id": "phase-release", "name": "上线", "color": "Green"},
    ]
    status_options = [
        {"id": "status-todo", "name": "未开始", "color": "Purple"},
        {"id": "status-doing", "name": "进行中", "color": "Blue"},
        {"id": "status-done", "name": "已完成", "color": "Green"},
        {"id": "status-block", "name": "阻塞", "color": "Orange"},
    ]
    tag_options = [
        {"id": "tag-core", "name": "核心", "color": "Blue"},
        {"id": "tag-risk", "name": "风险", "color": "Orange"},
        {"id": "tag-security", "name": "安全", "color": "Purple"},
        {"id": "tag-ops", "name": "运维", "color": "Green"},
    ]

    relation_field_id = add_field_if_missing("依赖", 10, {"database_id": db_id})
    child_relation_id = add_field_if_missing("子项", 10, {"database_id": db_id})
    rollup_field_id = add_field_if_missing(
        "依赖计数",
        16,
        {
            "relation_field_id": relation_field_id,
            "target_field_id": primary_id or "",
            "calculation_type": 5,
            "show_as": 0,
            "condition_value": "",
        },
    )

    add_field_if_missing("负责人", 0)
    add_field_if_missing("说明", 0)
    add_field_if_missing("工时(人天)", 1)
    add_field_if_missing("开始日期", 2)
    add_field_if_missing("阶段", 3, {"content": select_content(phase_options)})
    add_field_if_missing("状态", 3, {"content": select_content(status_options)})
    add_field_if_missing("标签", 4, {"content": select_content(tag_options)})
    add_field_if_missing("里程碑", 5)
    add_field_if_missing("需求链接", 6)
    add_field_if_missing("子任务", 7)
    add_field_if_missing("最后编辑时间", 8, {"field_type": 8})
    add_field_if_missing("创建时间", 9, {"field_type": 9})
    add_field_if_missing("汇总", 11, {"auto_fill": False})
    add_field_if_missing("英文摘要", 12, {"auto_fill": False, "language": 1})
    add_field_if_missing("时间窗口", 13)
    add_field_if_missing("附件", 14, {"content": json.dumps({"hide_file_names": False})})
    add_field_if_missing(
        "人员",
        15,
        {
            "content": json.dumps(
                {
                    "is_single_select": True,
                    "fill_with_creator": False,
                    "disable_notification": True,
                    "persons": [],
                },
                ensure_ascii=False,
            )
        },
    )

    fields_resp = get_database_fields(client, token, workspace_id, db_id)
    fields = fields_resp.get("data", []) if isinstance(fields_resp, dict) else []
    by_name = {f.get("name"): f for f in fields}
    return {
        "primary_name": primary_name,
        "relation_field_id": relation_field_id,
        "rollup_field_id": rollup_field_id,
        "child_relation_id": child_relation_id,
        "phase_options": phase_options,
        "status_options": status_options,
        "tag_options": tag_options,
        "fields": by_name,
    }


def build_plan_items() -> list[dict]:
    plan = [
        {
            "key": "req-clarify",
            "title": "需求澄清与范围定义",
            "phase": "规划",
            "status": "已完成",
            "tags": ["核心"],
            "owner": "产品经理/架构师",
            "start": "2026-03-01T09:00:00Z",
            "effort": 3,
            "milestone": False,
            "summary": "输出 PRD、范围清单、风险列表",
            "subtasks": ["访谈干系人", "竞品分析", "范围确认"],
        },
        {
            "key": "user-interview",
            "title": "用户画像与角色访谈",
            "phase": "规划",
            "status": "已完成",
            "tags": ["核心"],
            "owner": "产品经理",
            "start": "2026-03-03T09:00:00Z",
            "effort": 2,
            "milestone": False,
            "summary": "形成核心用户画像与关键场景",
            "subtasks": ["角色画像", "关键场景", "需求优先级"],
        },
        {
            "key": "role-design",
            "title": "权限模型与角色设计",
            "phase": "设计",
            "status": "已完成",
            "tags": ["安全"],
            "owner": "架构师",
            "start": "2026-03-05T09:00:00Z",
            "effort": 2,
            "milestone": False,
            "summary": "定义 RBAC 角色与资源边界",
            "subtasks": ["角色矩阵", "权限粒度", "资源命名规范"],
        },
        {
            "key": "data-model",
            "title": "用户数据模型与表结构",
            "phase": "设计",
            "status": "已完成",
            "tags": ["核心"],
            "owner": "后端负责人",
            "start": "2026-03-07T09:00:00Z",
            "effort": 2,
            "milestone": False,
            "summary": "确定用户/组织/租户表结构",
            "subtasks": ["数据字典", "索引设计", "迁移策略"],
        },
        {
            "key": "ui-prototype",
            "title": "管理端 UI 原型",
            "phase": "设计",
            "status": "已完成",
            "tags": ["核心"],
            "owner": "前端负责人",
            "start": "2026-03-08T09:00:00Z",
            "effort": 2,
            "milestone": False,
            "summary": "完成核心页面原型与交互流",
            "subtasks": ["列表原型", "详情原型", "权限配置原型"],
        },
        {
            "key": "auth-api",
            "title": "认证与登录接口",
            "phase": "开发",
            "status": "进行中",
            "tags": ["核心", "安全"],
            "owner": "后端负责人",
            "start": "2026-03-10T09:00:00Z",
            "effort": 4,
            "milestone": False,
            "summary": "实现登录、刷新、登出流程",
            "subtasks": ["登录接口", "Token 刷新", "安全审计"],
        },
        {
            "key": "user-crud",
            "title": "用户管理 CRUD",
            "phase": "开发",
            "status": "进行中",
            "tags": ["核心"],
            "owner": "后端/前端",
            "start": "2026-03-13T09:00:00Z",
            "effort": 5,
            "milestone": False,
            "summary": "完成用户增删改查与列表筛选",
            "subtasks": ["列表与搜索", "详情页", "批量操作"],
        },
        {
            "key": "org-team",
            "title": "组织与团队管理",
            "phase": "开发",
            "status": "未开始",
            "tags": ["核心"],
            "owner": "后端负责人",
            "start": "2026-03-17T09:00:00Z",
            "effort": 4,
            "milestone": False,
            "summary": "支持部门、团队、层级关系",
            "subtasks": ["组织结构", "成员维护", "导入导出"],
        },
        {
            "key": "permission-inherit",
            "title": "权限分配与继承规则",
            "phase": "开发",
            "status": "未开始",
            "tags": ["安全"],
            "owner": "架构师",
            "start": "2026-03-20T09:00:00Z",
            "effort": 3,
            "milestone": False,
            "summary": "支持角色授权、继承与审计",
            "subtasks": ["授权接口", "继承规则", "权限回收"],
        },
        {
            "key": "audit-log",
            "title": "审计日志与告警",
            "phase": "开发",
            "status": "未开始",
            "tags": ["安全", "运维"],
            "owner": "后端负责人",
            "start": "2026-03-23T09:00:00Z",
            "effort": 3,
            "milestone": False,
            "summary": "审计登录/权限变更/关键操作",
            "subtasks": ["日志结构", "检索接口", "告警规则"],
        },
        {
            "key": "integration-test",
            "title": "联调与回归测试",
            "phase": "测试",
            "status": "未开始",
            "tags": ["风险"],
            "owner": "QA",
            "start": "2026-03-28T09:00:00Z",
            "effort": 3,
            "milestone": False,
            "summary": "覆盖核心链路与异常流程",
            "subtasks": ["接口联调", "回归用例", "缺陷修复"],
        },
        {
            "key": "perf-security",
            "title": "性能与安全评估",
            "phase": "测试",
            "status": "未开始",
            "tags": ["风险", "安全"],
            "owner": "QA/安全",
            "start": "2026-03-30T09:00:00Z",
            "effort": 2,
            "milestone": True,
            "summary": "压力测试与安全扫描",
            "subtasks": ["性能压测", "安全扫描", "加固建议"],
        },
        {
            "key": "release",
            "title": "上线准备与灰度发布",
            "phase": "上线",
            "status": "未开始",
            "tags": ["运维"],
            "owner": "运维负责人",
            "start": "2026-04-02T09:00:00Z",
            "effort": 2,
            "milestone": True,
            "summary": "发布策略、回滚方案与监控",
            "subtasks": ["发布计划", "回滚预案", "监控告警"],
        },
        {
            "key": "milestone-plan",
            "title": "规划与设计里程碑",
            "phase": "规划",
            "status": "已完成",
            "tags": ["核心"],
            "owner": "项目负责人",
            "start": "2026-03-09T09:00:00Z",
            "effort": 1,
            "milestone": True,
            "summary": "规划+设计阶段验收",
            "subtasks": ["需求确认", "设计评审", "风险闭环"],
            "children": ["req-clarify", "user-interview", "role-design", "data-model", "ui-prototype"],
        },
        {
            "key": "milestone-dev",
            "title": "开发里程碑",
            "phase": "开发",
            "status": "进行中",
            "tags": ["核心"],
            "owner": "项目负责人",
            "start": "2026-03-26T09:00:00Z",
            "effort": 1,
            "milestone": True,
            "summary": "核心功能开发完成",
            "subtasks": ["后端完成", "前端完成", "接口联调"],
            "children": ["auth-api", "user-crud", "org-team", "permission-inherit", "audit-log"],
        },
        {
            "key": "milestone-release",
            "title": "测试与上线里程碑",
            "phase": "上线",
            "status": "未开始",
            "tags": ["风险"],
            "owner": "项目负责人",
            "start": "2026-04-05T09:00:00Z",
            "effort": 1,
            "milestone": True,
            "summary": "测试通过并进入发布阶段",
            "subtasks": ["测试通过", "上线评审", "发布窗口确认"],
            "children": ["integration-test", "perf-security", "release"],
        },
    ]
    for idx, item in enumerate(plan, start=1):
        if idx > 1 and "depends_on" not in item:
            item["depends_on"] = [plan[idx - 2]["key"]]
    return plan


def build_cells(primary_name: str, item: dict, idx: int) -> dict:
    checklist_options = [
        {"id": f"ck-{idx}-1", "name": item["subtasks"][0], "color": "Pink"},
        {"id": f"ck-{idx}-2", "name": item["subtasks"][1], "color": "Orange"},
        {"id": f"ck-{idx}-3", "name": item["subtasks"][2], "color": "Green"},
    ]
    base_created = 1769000000
    return {
        primary_name: item["title"],
        "负责人": item["owner"],
        "说明": item["summary"],
        "工时(人天)": item["effort"],
        "开始日期": item["start"],
        "阶段": item["phase"],
        "状态": item["status"],
        "标签": item["tags"],
        "里程碑": item["milestone"],
        "需求链接": f"https://example.com/plan/{idx}",
        "子任务": {
            "options": checklist_options,
            "selected_option_ids": [checklist_options[0]["id"]],
        },
        "最后编辑时间": base_created + idx * 3600,
        "创建时间": base_created + idx * 1800,
        "汇总": item["summary"],
        "英文摘要": "User management plan",
        "时间窗口": 36000 + idx * 600,
        "附件": {
            "files": [
                {
                    "id": f"media-{idx}",
                    "name": f"plan-{idx}.pdf",
                    "url": "https://example.com/assets/plan.pdf",
                    "upload_type": 1,
                    "file_type": 3,
                }
            ]
        },
        "人员": {},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Update the user management doc in-place.")
    parser.add_argument("--config", default=None)
    parser.add_argument("--env", default=None)
    parser.add_argument("--base-url", default=None)
    parser.add_argument("--gotrue-url", default=None)
    parser.add_argument("--client-version", default=None)
    parser.add_argument("--device-id", default=None)
    parser.add_argument("--token", default=None)
    parser.add_argument("--email", default=None)
    parser.add_argument("--password", default=None)
    parser.add_argument("--workspace-id", default=None, required=True)
    parser.add_argument("--view-id", default=None, required=True)
    parser.add_argument("--grid-name", default="UserManagementPlanGrid")
    parser.add_argument("--grid-heading", default=GRID_NEW_HEADING)
    parser.add_argument("--clean-only", action="store_true", help="Only clean invalid blocks/rows.")
    parser.add_argument(
        "--rebuild-grid",
        action="store_true",
        help="Force rebuild grid section (delete existing grid blocks).",
    )
    args = parser.parse_args()

    client = build_client(args)
    token = resolve_token(args, client)

    doc_json = fetch_doc_json(client, token, args.workspace_id, args.view_id)
    blocks_to_delete = find_blocks_to_delete(doc_json, rebuild_grid=args.rebuild_grid)

    if blocks_to_delete:
        doc_state, state_vector = fetch_doc_state(client, token, args.workspace_id, args.view_id)
        update = run_node_delete(doc_state, state_vector, blocks_to_delete)
        post_web_update(client, token, args.workspace_id, args.view_id, update)

    grid_section = grid_lib.select_grid_section(
        grid_lib.find_grid_sections(doc_json), heading_text=args.grid_heading
    )

    db_id = None
    db_view_id = None
    if grid_section:
        db_id = grid_section.get("parent_id")
        db_view_id = grid_section.get("view_id")

    if not db_id or not db_view_id:
        if args.clean_only:
            print_json(
                {
                    "workspace_id": args.workspace_id,
                    "view_id": args.view_id,
                    "blocks_deleted": blocks_to_delete,
                    "default_rows_removed": [],
                    "rows_added": 0,
                    "existing_rows_before": 0,
                    "note": "clean-only mode: grid not found, skipped creation",
                }
            )
            return 0
        db_id, db_view_id = ensure_grid_database(
            client, token, args.workspace_id, args.view_id, args.grid_name
        )
        append_grid_section(
            client, token, args.workspace_id, args.view_id, args.grid_heading, db_id, db_view_id
        )

    removed_default_rows = grid_lib.cleanup_default_rows(
        client, token, args.workspace_id, db_id, max_remove=3
    )

    if args.clean_only:
        print_json(
            {
                "workspace_id": args.workspace_id,
                "view_id": args.view_id,
                "grid_database_id": db_id,
                "grid_view_id": db_view_id,
                "blocks_deleted": blocks_to_delete,
                "default_rows_removed": removed_default_rows,
                "rows_added": 0,
                "existing_rows_before": 0,
            }
        )
        return 0

    field_info = ensure_fields(client, token, args.workspace_id, db_id)
    primary_name = field_info.get("primary_name") or "Title"
    grid_lib.repair_select_field_options(
        client,
        token,
        args.workspace_id,
        db_id,
        [
            {"name": "阶段", "options": field_info.get("phase_options", [])},
            {"name": "状态", "options": field_info.get("status_options", [])},
            {"name": "标签", "options": field_info.get("tag_options", [])},
        ],
    )

    existing_row_ids = list_row_ids(client, token, args.workspace_id, db_id)
    plan_items = build_plan_items()
    row_id_by_key: dict[str, str] = {}
    row_ids = []

    for idx, item in enumerate(plan_items, start=1):
        cells = build_cells(primary_name, item, idx)
        pre_hash = f"{args.grid_name}:{item['key']}"
        row_id = grid_lib.upsert_database_row(
            client, token, args.workspace_id, db_id, pre_hash, cells
        )
        row_id_by_key[item["key"]] = row_id
        row_ids.append(row_id)

    for item in plan_items:
        rel_cells = {}
        depends = item.get("depends_on") or []
        if depends:
            dep_ids = [row_id_by_key[key] for key in depends if key in row_id_by_key]
            if dep_ids:
                rel_cells["依赖"] = {"row_ids": dep_ids}
        child_keys = item.get("children") or []
        if child_keys:
            child_row_ids = [row_id_by_key[key] for key in child_keys if key in row_id_by_key]
            if child_row_ids:
                rel_cells["子项"] = {"row_ids": child_row_ids}
        if rel_cells:
            pre_hash = f"{args.grid_name}:{item['key']}"
            grid_lib.upsert_database_row(
                client, token, args.workspace_id, db_id, pre_hash, rel_cells
            )

    print_json(
        {
            "workspace_id": args.workspace_id,
            "view_id": args.view_id,
            "grid_database_id": db_id,
            "grid_view_id": db_view_id,
            "blocks_deleted": blocks_to_delete,
            "default_rows_removed": removed_default_rows,
            "rows_added": len(row_ids),
            "existing_rows_before": len(existing_row_ids),
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
