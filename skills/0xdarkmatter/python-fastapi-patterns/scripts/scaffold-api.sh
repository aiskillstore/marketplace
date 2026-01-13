#!/usr/bin/env bash
# Generate FastAPI endpoint boilerplate
#
# Usage: scaffold-api.sh <resource_name>
# Example: scaffold-api.sh user

set -euo pipefail

RESOURCE="${1:-}"

if [[ -z "$RESOURCE" ]]; then
    echo "Usage: scaffold-api.sh <resource_name>"
    echo "Example: scaffold-api.sh user"
    exit 1
fi

# Convert to different cases
RESOURCE_LOWER=$(echo "$RESOURCE" | tr '[:upper:]' '[:lower:]')
RESOURCE_UPPER=$(echo "$RESOURCE" | tr '[:lower:]' '[:upper:]')
RESOURCE_TITLE=$(echo "$RESOURCE_LOWER" | sed 's/\b\(.\)/\u\1/g')
RESOURCE_PLURAL="${RESOURCE_LOWER}s"

cat << EOF
# =============================================================================
# ${RESOURCE_TITLE} Models
# =============================================================================

from pydantic import BaseModel, Field
from datetime import datetime

class ${RESOURCE_TITLE}Create(BaseModel):
    """Create ${RESOURCE_LOWER} request."""
    name: str = Field(..., min_length=1, max_length=100)
    # Add more fields

class ${RESOURCE_TITLE}Update(BaseModel):
    """Update ${RESOURCE_LOWER} request (partial)."""
    name: str | None = None
    # Add more fields

class ${RESOURCE_TITLE}Response(BaseModel):
    """${RESOURCE_TITLE} response."""
    id: int
    name: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# =============================================================================
# ${RESOURCE_TITLE} Router
# =============================================================================

from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated

router = APIRouter(prefix="/${RESOURCE_PLURAL}", tags=["${RESOURCE_PLURAL}"])

@router.get("/", response_model=list[${RESOURCE_TITLE}Response])
async def list_${RESOURCE_PLURAL}(
    db: DB,
    skip: int = 0,
    limit: int = 10,
):
    """List all ${RESOURCE_PLURAL}."""
    result = await db.execute(
        select(${RESOURCE_TITLE}).offset(skip).limit(limit)
    )
    return result.scalars().all()

@router.post("/", response_model=${RESOURCE_TITLE}Response, status_code=201)
async def create_${RESOURCE_LOWER}(data: ${RESOURCE_TITLE}Create, db: DB):
    """Create a new ${RESOURCE_LOWER}."""
    ${RESOURCE_LOWER} = ${RESOURCE_TITLE}(**data.model_dump())
    db.add(${RESOURCE_LOWER})
    await db.commit()
    await db.refresh(${RESOURCE_LOWER})
    return ${RESOURCE_LOWER}

@router.get("/{${RESOURCE_LOWER}_id}", response_model=${RESOURCE_TITLE}Response)
async def get_${RESOURCE_LOWER}(${RESOURCE_LOWER}_id: int, db: DB):
    """Get a ${RESOURCE_LOWER} by ID."""
    ${RESOURCE_LOWER} = await db.get(${RESOURCE_TITLE}, ${RESOURCE_LOWER}_id)
    if not ${RESOURCE_LOWER}:
        raise HTTPException(status_code=404, detail="${RESOURCE_TITLE} not found")
    return ${RESOURCE_LOWER}

@router.patch("/{${RESOURCE_LOWER}_id}", response_model=${RESOURCE_TITLE}Response)
async def update_${RESOURCE_LOWER}(
    ${RESOURCE_LOWER}_id: int,
    data: ${RESOURCE_TITLE}Update,
    db: DB,
):
    """Update a ${RESOURCE_LOWER}."""
    ${RESOURCE_LOWER} = await db.get(${RESOURCE_TITLE}, ${RESOURCE_LOWER}_id)
    if not ${RESOURCE_LOWER}:
        raise HTTPException(status_code=404, detail="${RESOURCE_TITLE} not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(${RESOURCE_LOWER}, field, value)

    await db.commit()
    await db.refresh(${RESOURCE_LOWER})
    return ${RESOURCE_LOWER}

@router.delete("/{${RESOURCE_LOWER}_id}", status_code=204)
async def delete_${RESOURCE_LOWER}(${RESOURCE_LOWER}_id: int, db: DB):
    """Delete a ${RESOURCE_LOWER}."""
    ${RESOURCE_LOWER} = await db.get(${RESOURCE_TITLE}, ${RESOURCE_LOWER}_id)
    if not ${RESOURCE_LOWER}:
        raise HTTPException(status_code=404, detail="${RESOURCE_TITLE} not found")

    await db.delete(${RESOURCE_LOWER})
    await db.commit()

# =============================================================================
# Include in main app:
# from routers.${RESOURCE_PLURAL} import router as ${RESOURCE_PLURAL}_router
# app.include_router(${RESOURCE_PLURAL}_router, prefix="/api/v1")
# =============================================================================
EOF
