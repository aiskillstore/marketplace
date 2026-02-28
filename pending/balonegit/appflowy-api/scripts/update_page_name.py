import argparse

from _common import build_client, print_json, resolve_token


def main() -> int:
    parser = argparse.ArgumentParser(description="Update page/view name.")
    parser.add_argument("--workspace-id", required=True)
    parser.add_argument("--view-id", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--token", default=None)
    parser.add_argument("--email", default=None)
    parser.add_argument("--password", default=None)
    parser.add_argument("--config", default=None)
    parser.add_argument("--env", default=None)
    parser.add_argument("--base-url", default=None)
    parser.add_argument("--gotrue-url", default=None)
    parser.add_argument("--client-version", default=None)
    parser.add_argument("--device-id", default=None)
    args = parser.parse_args()

    client = build_client(args)
    token = resolve_token(args, client)
    base = client._require_base_url()
    resp = client._request_json(
        "POST",
        f"{base}/api/workspace/{args.workspace_id}/page-view/{args.view_id}/update-name",
        token=token,
        json_body={"name": args.name},
    )
    print_json(resp)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
