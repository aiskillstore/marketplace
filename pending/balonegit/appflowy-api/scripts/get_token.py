import argparse
from _common import build_client, print_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch GoTrue access token.")
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--config", default=None, help="Path to config JSON (optional).")
    parser.add_argument("--env", default=None, help="Path to .env file (optional, opt-in).")
    parser.add_argument("--base-url", default=None)
    parser.add_argument("--gotrue-url", default=None)
    parser.add_argument("--client-version", default=None)
    parser.add_argument("--device-id", default=None)
    args = parser.parse_args()

    client = build_client(args)
    token = client.login_password(args.email, args.password)
    print_json(token)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
