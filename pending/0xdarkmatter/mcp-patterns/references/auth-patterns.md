# MCP Authentication Patterns

Patterns for handling authentication in MCP servers.

## Environment Variables

```python
import os

API_KEY = os.environ.get("MY_API_KEY")
if not API_KEY:
    raise ValueError("MY_API_KEY environment variable required")

async def make_api_call(endpoint: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.example.com/{endpoint}",
            headers={"Authorization": f"Bearer {API_KEY}"}
        )
        response.raise_for_status()
        return response.json()
```

## OAuth Token Refresh

```python
from datetime import datetime, timedelta

class TokenManager:
    def __init__(self):
        self.token = None
        self.expires_at = None

    async def get_token(self) -> str:
        if self.token and self.expires_at > datetime.now():
            return self.token

        # Refresh token
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://auth.example.com/token",
                data={"grant_type": "client_credentials", ...}
            )
            data = response.json()
            self.token = data["access_token"]
            self.expires_at = datetime.now() + timedelta(seconds=data["expires_in"] - 60)
            return self.token

token_manager = TokenManager()
```
