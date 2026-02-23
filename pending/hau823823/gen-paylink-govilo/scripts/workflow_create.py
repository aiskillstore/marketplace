import argparse
import json
import sys
from pathlib import Path

from scripts.api_client import GoviloClient, ApiError
from scripts.config import load_config, ConfigError
from scripts.packager import package, PackageError


def _output(data: dict) -> None:
    print(json.dumps(data, ensure_ascii=False))


def _fail(error: str, code: int | None = None) -> None:
    out = {"ok": False, "error": error}
    if code is not None:
        out["code"] = code
    _output(out)
    sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload files and create Govilo unlock link")
    parser.add_argument("--input", required=True, action="append", dest="inputs", help="ZIP, folder, or file path (repeatable)")
    parser.add_argument("--title", required=True, help="Product title")
    parser.add_argument("--price", required=True, help="Price in USDC (e.g. 5.00)")
    parser.add_argument("--address", default=None, help="Seller EVM wallet address (overrides SELLER_ADDRESS env)")
    parser.add_argument("--description", default="", help="Product description")
    args = parser.parse_args()

    try:
        cfg = load_config(cli_api_key=None, cli_address=args.address)
    except ConfigError as e:
        _fail(str(e))

    try:
        zip_path = package(args.inputs)
    except PackageError as e:
        _fail(str(e))

    is_temp = zip_path not in [Path(p) for p in args.inputs]
    try:
        client = GoviloClient(api_key=cfg.api_key, base_url=cfg.base_url)

        try:
            presign_data = client.presign(cfg.seller_address)
            client.upload(presign_data["upload_url"], zip_path)
            item_data = client.create_item(
                session_id=presign_data["session_id"],
                title=args.title,
                price=args.price,
                description=args.description,
            )
        except ApiError as e:
            _fail(str(e), code=e.code)

        _output({
            "ok": True,
            "unlock_url": item_data["unlock_url"],
            "item_id": item_data["id"],
            "file_count": item_data["file_count"],
            "total_size": item_data["total_size"],
        })
    finally:
        if is_temp:
            zip_path.unlink(missing_ok=True)
