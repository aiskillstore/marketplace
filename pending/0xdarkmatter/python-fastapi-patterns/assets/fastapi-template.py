"""
Production-ready FastAPI application template.

Usage:
    uvicorn main:app --reload  # Development
    uvicorn main:app --host 0.0.0.0 --port 8000  # Production
"""

from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


# =============================================================================
# Configuration
# =============================================================================

class Settings(BaseSettings):
    """Application settings from environment variables."""

    app_name: str = "My API"
    debug: bool = False
    database_url: str = "postgresql+asyncpg://user:pass@localhost/db"
    redis_url: str = "redis://localhost:6379/0"
    api_key: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


# Cache settings
from functools import lru_cache

@lru_cache
def get_settings() -> Settings:
    return Settings()


# =============================================================================
# Lifespan Management
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown."""
    settings = get_settings()

    # Startup
    # app.state.db = await create_db_pool(settings.database_url)
    # app.state.redis = await create_redis_client(settings.redis_url)
    print(f"Starting {settings.app_name}...")

    yield

    # Shutdown
    # await app.state.db.close()
    # await app.state.redis.close()
    print("Shutting down...")


# =============================================================================
# Application
# =============================================================================

app = FastAPI(
    title="My API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if get_settings().debug else ["https://myapp.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Error Handling
# =============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unhandled exceptions."""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# =============================================================================
# Dependencies
# =============================================================================

async def get_db():
    """Database session dependency."""
    # async with async_session() as session:
    #     yield session
    yield None  # Placeholder


DB = Annotated[None, Depends(get_db)]  # Replace None with actual type


# =============================================================================
# Models
# =============================================================================

class HealthResponse(BaseModel):
    status: str
    version: str


class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None


class ItemResponse(BaseModel):
    id: int
    name: str
    description: str | None

    model_config = {"from_attributes": True}


# =============================================================================
# Routes
# =============================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="healthy", version="1.0.0")


@app.get("/items", response_model=list[ItemResponse])
async def list_items(
    db: DB,
    skip: int = 0,
    limit: int = 10,
):
    """List all items."""
    # items = await db.execute(select(Item).offset(skip).limit(limit))
    # return items.scalars().all()
    return []


@app.post("/items", response_model=ItemResponse, status_code=201)
async def create_item(item: ItemCreate, db: DB):
    """Create a new item."""
    # db_item = Item(**item.model_dump())
    # db.add(db_item)
    # await db.commit()
    # await db.refresh(db_item)
    # return db_item
    return ItemResponse(id=1, name=item.name, description=item.description)


@app.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int, db: DB):
    """Get a single item."""
    # item = await db.get(Item, item_id)
    # if not item:
    #     raise HTTPException(status_code=404, detail="Item not found")
    # return item
    raise HTTPException(status_code=404, detail="Item not found")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
