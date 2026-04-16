#!/usr/bin/env python3
import argparse
import base64
import json
import mimetypes
import os
import sys
from pathlib import Path
from typing import Any
from urllib import error, request


DEFAULT_BASE_URL = "https://api.scanlume.com"


class ScanlumeScriptError(RuntimeError):
    pass


def resolve_base_url(explicit: str | None) -> str:
    value = explicit or os.environ.get("SCANLUME_BASE_URL") or DEFAULT_BASE_URL
    return value.rstrip("/")


def require_api_key(explicit: str | None) -> str:
    value = explicit or os.environ.get("SCANLUME_API_KEY")
    if not value:
        raise ScanlumeScriptError(
            "SCANLUME_API_KEY is required. Pass --api-key or set the environment variable. / "
            "SCANLUME_API_KEY e obrigatoria. Use --api-key ou defina a variavel de ambiente."
        )
    return value


def infer_mime_type(path: Path, explicit: str | None) -> str:
    if explicit:
        return explicit
    guessed, _ = mimetypes.guess_type(path.name)
    if not guessed:
        raise ScanlumeScriptError(
            "Could not infer MIME type. Pass --mime-type explicitly. / "
            "Nao foi possivel inferir o MIME type. Passe --mime-type explicitamente."
        )
    return guessed


def ensure_public_image_input(path: Path, mime_type: str) -> None:
    suffix = path.suffix.lower()
    if suffix == ".pdf" or mime_type == "application/pdf":
        raise ScanlumeScriptError(
            "The public API behind https://www.scanlume.com/ currently exposes image OCR only. "
            "PDF OCR API remains beta-gated. / A API publica do https://www.scanlume.com/ "
            "atualmente expoe apenas OCR de imagem. A API de OCR para PDF continua beta-gated."
        )


def build_data_url(path: Path, mime_type: str) -> str:
    raw = path.read_bytes()
    encoded = base64.b64encode(raw).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def build_payload(mode: str, data_url: str) -> dict[str, str]:
    return {
        "mode": mode,
        "base64": data_url,
    }


def perform_request(base_url: str, api_key: str, payload: dict[str, str], timeout: int) -> dict[str, Any]:
    endpoint = f"{base_url}/v1/api/ocr"
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        endpoint,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        data=body,
    )

    try:
        with request.urlopen(req, timeout=timeout) as response:
            data = response.read().decode("utf-8")
            return json.loads(data)
    except error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise ScanlumeScriptError(
            f"API request failed with HTTP {exc.code}: {details} / "
            f"A requisicao da API falhou com HTTP {exc.code}: {details}"
        ) from exc
    except error.URLError as exc:
        raise ScanlumeScriptError(
            f"Network error while calling the Scanlume API: {exc.reason} / "
            f"Erro de rede ao chamar a API do Scanlume: {exc.reason}"
        ) from exc


def resolve_output_name(mode: str, explicit: str | None) -> str:
    if explicit:
        return explicit
    return "txt" if mode == "simple" else "md"


def render_output(response_json: dict[str, Any], mode: str, output_name: str) -> str:
    if output_name == "json":
        return json.dumps(response_json, ensure_ascii=False, indent=2)

    result = response_json.get("result")
    if not isinstance(result, dict):
        raise ScanlumeScriptError(
            "API response does not include a result object. / "
            "A resposta da API nao inclui um objeto result."
        )

    if output_name == "txt":
        value = result.get("txt")
    elif output_name == "md":
        value = result.get("md")
    elif output_name == "html":
        value = result.get("html")
    elif output_name == "preview":
        value = result.get("preview")
    else:
        raise ScanlumeScriptError(
            f"Unsupported output selector: {output_name} / Seletor de saida nao suportado: {output_name}"
        )

    if value is None:
        raise ScanlumeScriptError(
            f"Output '{output_name}' is not available for mode '{mode}'. / "
            f"A saida '{output_name}' nao esta disponivel para o modo '{mode}'."
        )
    if not isinstance(value, str):
        raise ScanlumeScriptError(
            f"Output '{output_name}' is not a string. / A saida '{output_name}' nao e uma string."
        )
    return value


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Call the public Scanlume OCR image API for a local file. / Chame a API publica de OCR de imagem do Scanlume para um arquivo local."
    )
    parser.add_argument(
        "input_path",
        help="Local image path. Public API currently rejects PDF OCR through this helper. / Caminho local da imagem. A API publica atualmente rejeita OCR de PDF por este helper.",
    )
    parser.add_argument("--mode", choices=["simple", "formatted"], required=True, help="OCR mode to use. / Modo de OCR.")
    parser.add_argument("--output", choices=["txt", "md", "html", "preview", "json"], help="Which response field to print. / Campo de saida para imprimir.")
    parser.add_argument("--api-key", help="Override SCANLUME_API_KEY.")
    parser.add_argument("--base-url", help="Override SCANLUME_BASE_URL. Default / Padrao: https://api.scanlume.com")
    parser.add_argument("--mime-type", help="Override inferred MIME type. / Sobrescreve o MIME type inferido.")
    parser.add_argument("--timeout", type=int, default=60, help="HTTP timeout in seconds. Default / Padrao: 60.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    path = Path(args.input_path).expanduser().resolve()
    if not path.exists():
        raise ScanlumeScriptError(f"Input file not found: {path} / Arquivo de entrada nao encontrado: {path}")
    if not path.is_file():
        raise ScanlumeScriptError(f"Input path is not a file: {path} / O caminho de entrada nao e um arquivo: {path}")

    api_key = require_api_key(args.api_key)
    base_url = resolve_base_url(args.base_url)
    mime_type = infer_mime_type(path, args.mime_type)
    ensure_public_image_input(path, mime_type)

    data_url = build_data_url(path, mime_type)
    payload = build_payload(args.mode, data_url)
    response_json = perform_request(base_url, api_key, payload, args.timeout)
    output_name = resolve_output_name(args.mode, args.output)
    rendered = render_output(response_json, args.mode, output_name)
    sys.stdout.write(rendered)
    if not rendered.endswith("\n"):
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ScanlumeScriptError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
