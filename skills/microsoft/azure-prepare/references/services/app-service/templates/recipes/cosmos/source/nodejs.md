# Cosmos DB Recipe — Node.js — REFERENCE ONLY

## Cosmos SDK Setup

### npm Packages

```bash
npm install @azure/cosmos @azure/identity
```

### Database Module

Create `src/cosmosClient.js`:

```javascript
const { CosmosClient } = require("@azure/cosmos");
const { DefaultAzureCredential } = require("@azure/identity");

const client = new CosmosClient({
  endpoint: process.env.COSMOS_ENDPOINT,
  aadCredentials: new DefaultAzureCredential(),
});

const container = client
  .database(process.env.COSMOS_DATABASE_NAME)
  .container(process.env.COSMOS_CONTAINER_NAME);

module.exports = { container };
```

### CRUD Endpoints

Add to `src/index.js`:

```javascript
const { container } = require("./cosmosClient");

app.get("/api/items", async (req, res) => {
  const { resources } = await container.items.readAll().fetchAll();
  res.json(resources);
});

app.post("/api/items", async (req, res) => {
  const { resource } = await container.items.create(req.body);
  res.status(201).json(resource);
});
```

## Files to Modify

| File | Action |
|------|--------|
| `src/cosmosClient.js` | Create — Cosmos client + container reference |
| `src/index.js` | Modify — add CRUD endpoints |
| `package.json` | Modify — add @azure/cosmos, @azure/identity |
