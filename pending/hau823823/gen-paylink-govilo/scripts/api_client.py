from pathlib import Path

import requests


class ApiError(Exception):
    def __init__(self, message: str, code: int | None = None):
        super().__init__(message)
        self.code = code


class GoviloClient:
    def __init__(self, api_key: str, base_url: str):
        self._base_url = base_url.rstrip("/")
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def _check_response(self, resp: requests.Response) -> dict:
        body = resp.json()
        if body.get("code", 0) != 0:
            raise ApiError(body.get("msg", "unknown error"), body.get("code"))
        return body["data"]

    def presign(self, seller_address: str) -> dict:
        resp = requests.post(
            f"{self._base_url}/api/v1/bot/uploads/presign",
            headers=self._headers,
            json={"seller_address": seller_address},
        )
        return self._check_response(resp)

    def upload(self, upload_url: str, zip_path: Path) -> None:
        with open(zip_path, "rb") as f:
            resp = requests.put(
                upload_url,
                headers={"Content-Type": "application/zip"},
                data=f,
            )
        if resp.status_code != 200:
            raise ApiError(f"Upload failed: HTTP {resp.status_code}")

    def create_item(
        self,
        session_id: str,
        title: str,
        price: str,
        description: str = "",
    ) -> dict:
        resp = requests.post(
            f"{self._base_url}/api/v1/bot/items",
            headers=self._headers,
            json={
                "session_id": session_id,
                "title": title,
                "price": price,
                "description": description,
            },
        )
        return self._check_response(resp)
