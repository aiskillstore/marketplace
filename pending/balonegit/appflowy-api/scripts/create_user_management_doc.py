import argparse
import json
from pathlib import Path

from _common import build_client, print_json, resolve_token
from appflowy_client import AppFlowyError


def load_template(path: str) -> list[dict]:
    template_path = Path(path)
    if not template_path.exists():
        raise AppFlowyError(f"Template file not found: {template_path}")
    payload = json.loads(template_path.read_text(encoding="utf-8"))
    blocks = payload.get("blocks")
    if not isinstance(blocks, list) or not blocks:
        raise AppFlowyError("Template must contain non-empty 'blocks' array")
    return blocks


def pick_workspace_id(client, token: str, workspace_id: str | None) -> str:
    if workspace_id:
        return workspace_id
    data = client.list_workspaces(token)
    items = data.get("data") if isinstance(data, dict) else None
    if not items:
        raise AppFlowyError("No workspace found")
    return items[0].get("workspace_id") or items[0].get("id")


def pick_parent_view_id(client, token: str, workspace_id: str, parent_view_id: str | None) -> str:
    if parent_view_id:
        return parent_view_id
    folder = client._request_json(
        "GET",
        f"{client._require_base_url()}/api/workspace/{workspace_id}/folder",
        token=token,
        params={"depth": 1},
    )
    children = folder.get("data", {}).get("children", [])
    for child in children:
        if child.get("name") == "General":
            return child.get("view_id")
    if children:
        return children[0].get("view_id")
    return workspace_id


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a user management doc page (test).")
    parser.add_argument("--config", default=None, help="Path to config JSON (optional).")
    parser.add_argument("--env", default=None, help="Path to .env file (optional, opt-in).")
    parser.add_argument("--base-url", default=None)
    parser.add_argument("--gotrue-url", default=None)
    parser.add_argument("--client-version", default=None)
    parser.add_argument("--device-id", default=None)
    parser.add_argument("--token", default=None)
    parser.add_argument("--email", default=None)
    parser.add_argument("--password", default=None)
    parser.add_argument("--workspace-id", default=None)
    parser.add_argument("--parent-view-id", default=None)
    parser.add_argument(
        "--title",
        default="用户管理系统开发文档（测试）-UTF8",
        help="Page title to create.",
    )
    parser.add_argument(
        "--template",
        default="skills/appflowy-api/references/templates/user_management_doc.json",
        help="Path to UTF-8 JSON template with blocks.",
    )
    args = parser.parse_args()

    client = build_client(args)
    token = resolve_token(args, client)
    workspace_id = pick_workspace_id(client, token, args.workspace_id)
    parent_view_id = pick_parent_view_id(client, token, workspace_id, args.parent_view_id)

    page_payload = {
        "parent_view_id": parent_view_id,
        "layout": 0,
        "name": args.title,
    }
    page_resp = client.create_page_view(token, workspace_id, page_payload)
    view_id = None
    if isinstance(page_resp, dict):
        data = page_resp.get("data") or page_resp
        if isinstance(data, dict):
            view_id = data.get("view_id")
    if not view_id:
        raise AppFlowyError("Failed to create page view (missing view_id)")

    blocks = load_template(args.template)
    append_payload = {"blocks": blocks}
    append_resp = client.append_block(token, workspace_id, view_id, append_payload)

    print_json(
        {
            "workspace_id": workspace_id,
            "parent_view_id": parent_view_id,
            "view_id": view_id,
            "create_page_response": page_resp,
            "append_block_response": append_resp,
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
