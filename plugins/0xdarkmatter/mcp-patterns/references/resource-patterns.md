# MCP Resource Patterns

Patterns for exposing resources via MCP.

## Static Resource

```python
@app.list_resources()
async def list_resources():
    return [
        {
            "uri": "config://settings",
            "name": "Application Settings",
            "mimeType": "application/json"
        }
    ]

@app.read_resource()
async def read_resource(uri: str):
    if uri == "config://settings":
        return json.dumps({"theme": "dark", "lang": "en"})
    raise ValueError(f"Unknown resource: {uri}")
```

## Dynamic Resources

```python
@app.list_resources()
async def list_resources():
    # List available resources dynamically
    items = await get_all_items()
    return [
        {
            "uri": f"item://{item.id}",
            "name": item.name,
            "mimeType": "application/json"
        }
        for item in items
    ]

@app.read_resource()
async def read_resource(uri: str):
    if uri.startswith("item://"):
        item_id = uri.replace("item://", "")
        item = await get_item(item_id)
        return json.dumps(item.to_dict())
    raise ValueError(f"Unknown resource: {uri}")
```
