import argparse
import subprocess
import sys
from pathlib import Path

COMMANDS = {
    "doctor": "doctor.py",
    "token": "get_token.py",
    "create-user-management-doc": "create_user_management_doc.py",
    "update-user-management-doc": "update_user_management_doc.py",
    "apply-grid": "apply_grid_template.py",
    "update-page-name": "update_page_name.py",
    "list-workspaces": "list_workspaces.py",
    "list-databases": "list_databases.py",
    "list-row-ids": "list_row_ids.py",
    "get-row-detail": "get_row_detail.py",
    "search": "search.py",
    "create-page-view": "create_page_view.py",
    "append-block": "append_block.py",
    "add-db-field": "add_db_field.py",
    "upsert-row": "upsert_row.py",
}


def _script_path(name: str) -> Path:
    return Path(__file__).resolve().parent / COMMANDS[name]


def _run_script(name: str, args: list[str]) -> int:
    script = _script_path(name)
    if not script.exists():
        print(f"脚本不存在：{script}", file=sys.stderr)
        return 1
    cmd = [sys.executable, str(script), *args]
    result = subprocess.run(cmd, check=False)
    return result.returncode


def _print_list() -> None:
    print("可用命令：")
    for key in sorted(COMMANDS.keys()):
        print(f"- {key}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="AppFlowy API 技能统一入口。使用 help 子命令查看具体脚本帮助。"
    )
    parser.add_argument(
        "command",
        help="子命令",
        choices=sorted(list(COMMANDS.keys()) + ["list", "help"]),
    )
    parser.add_argument("args", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    if args.command == "list":
        _print_list()
        return 0

    if args.command == "help":
        if not args.args:
            print("用法：appflowy_skill.py help <command>", file=sys.stderr)
            _print_list()
            return 1
        target = args.args[0]
        if target not in COMMANDS:
            print(f"未知命令：{target}", file=sys.stderr)
            _print_list()
            return 1
        return _run_script(target, ["--help"])

    rest = args.args[1:] if args.args[:1] == ["--"] else args.args
    return _run_script(args.command, rest)


if __name__ == "__main__":
    raise SystemExit(main())
