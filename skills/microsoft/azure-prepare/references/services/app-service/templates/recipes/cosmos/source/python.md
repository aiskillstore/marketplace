# Cosmos DB Recipe — Python — REFERENCE ONLY

## Cosmos SDK Setup

### Requirements

Add to `requirements.txt`:

```
azure-cosmos>=4.7
azure-identity
```

### Database Module

Create `cosmos_client.py`:

```python
import os
from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = CosmosClient(os.environ["COSMOS_ENDPOINT"], credential)
database = client.get_database_client(os.environ["COSMOS_DATABASE_NAME"])
container = database.get_container_client(os.environ["COSMOS_CONTAINER_NAME"])
```

### CRUD Endpoints

Add to `main.py`:

```python
from cosmos_client import container

@app.get("/api/items")
async def list_items():
    items = list(container.read_all_items())
    return items

@app.post("/api/items", status_code=201)
async def create_item(item: dict):
    return container.create_item(body=item)
```

## Files to Modify

| File | Action |
|------|--------|
| `cosmos_client.py` | Create — Cosmos client + container reference |
| `main.py` | Modify — add CRUD endpoints |
| `requirements.txt` | Modify — add azure-cosmos, azure-identity |
