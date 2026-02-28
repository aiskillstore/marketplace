import argparse
import json

import doc_grid_lib as grid_lib
from _common import build_client, load_json_payload, print_json, resolve_token
from appflowy_client import AppFlowyError


def load_template(path_or_payload: str | None, payload_file: str | None) -> dict:
    if path_or_payload or payload_file:
        return load_json_payload(path_or_payload, payload_file)
    raise AppFlowyError("Missing template payload. Use --template or --template-file.")


def ensure_fields_from_template(client, token, workspace_id: str, db_id: str, fields: list[dict]) -> None:
    existing = grid_lib.get_database_fields(client, token, workspace_id, db_id)
    field_list = existing.get("data", []) if isinstance(existing, dict) else []
    by_name = {f.get("name"): f for f in field_list if isinstance(f, dict)}
    for field in fields or []:
        name = field.get("name")
        if not name:
            continue
        if name in by_name and by_name[name].get("id"):
            continue
        payload = dict(field)
        type_option_data = payload.get("type_option_data")
        if (
            isinstance(type_option_data, dict)
            and type_option_data.get("database_id") == "<db_id_placeholder>"
        ):
            payload["type_option_data"] = {**type_option_data, "database_id": db_id}
        grid_lib.add_database_field(client, token, workspace_id, db_id, payload)


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply a grid template to an existing document.")
    parser.add_argument("--config", default=None)
    parser.add_argument("--env", default=None)
    parser.add_argument("--base-url", default=None)
    parser.add_argument("--gotrue-url", default=None)
    parser.add_argument("--client-version", default=None)
    parser.add_argument("--device-id", default=None)
    parser.add_argument("--token", default=None)
    parser.add_argument("--email", default=None)
    parser.add_argument("--password", default=None)
    parser.add_argument("--workspace-id", required=True)
    parser.add_argument("--view-id", required=True)
    parser.add_argument("--template", default=None, help="Template JSON string")
    parser.add_argument("--template-file", default=None, help="Template JSON file")
    parser.add_argument("--clean-only", action="store_true", help="Only clean invalid blocks/rows.")
    args = parser.parse_args()

    client = build_client(args)
    token = resolve_token(args, client)
    template = load_template(args.template, args.template_file)

    grid_cfg = template.get("grid", {})
    grid_heading = grid_cfg.get("heading") or "Grid"
    grid_name = grid_cfg.get("name") or "Grid"
    clean_default_rows = bool(template.get("rules", {}).get("clean_default_rows", True))
    max_default_rows = int(template.get("rules", {}).get("max_default_rows", 3))

    doc_json = grid_lib.fetch_collab_json(
        client, token, args.workspace_id, args.view_id, grid_lib.DOC_COLLAB_TYPE
    )
    grid_section = grid_lib.select_grid_section(
        grid_lib.find_grid_sections(doc_json), heading_text=grid_heading
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
                    "note": "clean-only mode: grid not found, skipped creation",
                }
            )
            return 0
        resp = client.create_page_view(
            token,
            args.workspace_id,
            {"parent_view_id": args.view_id, "layout": grid_lib.GRID_LAYOUT, "name": grid_name},
        )
        data = resp.get("data") if isinstance(resp, dict) else None
        if not isinstance(data, dict):
            raise AppFlowyError("Failed to create grid page view", response=resp)
        db_id = data.get("database_id")
        db_view_id = data.get("view_id")
        if not db_id or not db_view_id:
            raise AppFlowyError("Missing database_id/view_id in create page response", response=resp)
        grid_lib.append_grid_section(
            client, token, args.workspace_id, args.view_id, grid_heading, db_id, db_view_id
        )

    removed_default_rows = []
    if clean_default_rows:
        removed_default_rows = grid_lib.cleanup_default_rows(
            client, token, args.workspace_id, db_id, max_remove=max_default_rows
        )

    if args.clean_only:
        print_json(
            {
                "workspace_id": args.workspace_id,
                "view_id": args.view_id,
                "grid_database_id": db_id,
                "grid_view_id": db_view_id,
                "default_rows_removed": removed_default_rows,
            }
        )
        return 0

    fields = template.get("fields") or []
    ensure_fields_from_template(client, token, args.workspace_id, db_id, fields)
    select_fields = []
    for field in fields:
        if field.get("field_type") in (3, 4) and field.get("type_option_data"):
            content = field.get("type_option_data", {}).get("content")
            data = None
            if isinstance(content, str):
                try:
                    data = json.loads(content)
                except json.JSONDecodeError:
                    data = None
            elif isinstance(content, dict):
                data = content
            if isinstance(data, dict):
                options = data.get("options") or []
                if options:
                    select_fields.append(
                        {
                            "name": field.get("name"),
                            "options": options,
                            "disable_color": data.get("disable_color", False),
                        }
                    )
    status_field = next((item for item in select_fields if item.get("name") == "状态"), None)
    if status_field and not any(item.get("name") == "Type" for item in select_fields):
        select_fields.append(
            {
                "name": "Type",
                "options": status_field.get("options") or [],
                "disable_color": status_field.get("disable_color", False),
            }
        )
    grid_lib.repair_select_field_options(
        client, token, args.workspace_id, db_id, select_fields
    )

    rows = template.get("rows") or []
    row_id_by_key: dict[str, str] = {}
    row_ids = []
    for row in rows:
        key = row.get("key")
        cells = row.get("cells") or {}
        if not key or not cells:
            continue
        pre_hash = f"{grid_name}:{key}"
        row_id = grid_lib.upsert_database_row(
            client, token, args.workspace_id, db_id, pre_hash, cells
        )
        row_id_by_key[key] = row_id
        row_ids.append(row_id)

    for row in rows:
        key = row.get("key")
        if not key:
            continue
        rel_cells = {}
        depends_on = row.get("depends_on") or []
        children = row.get("children") or []
        if depends_on:
            rel_cells["依赖"] = {
                "row_ids": [row_id_by_key[k] for k in depends_on if k in row_id_by_key]
            }
        if children:
            rel_cells["子项"] = {
                "row_ids": [row_id_by_key[k] for k in children if k in row_id_by_key]
            }
        if rel_cells:
            pre_hash = f"{grid_name}:{key}"
            grid_lib.upsert_database_row(
                client, token, args.workspace_id, db_id, pre_hash, rel_cells
            )

    print_json(
        {
            "workspace_id": args.workspace_id,
            "view_id": args.view_id,
            "grid_database_id": db_id,
            "grid_view_id": db_view_id,
            "default_rows_removed": removed_default_rows,
            "rows_upserted": len(row_ids),
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
