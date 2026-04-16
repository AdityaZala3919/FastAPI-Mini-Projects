from fastapi import FastAPI, Depends, Body, Path, Security, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Annotated
from contextlib import asynccontextmanager
from uuid import uuid4, UUID
from sqlalchemy import select
from fastapi.security.api_key import APIKeyHeader

from db import Key, get_session, init_db

class ApiKeyRequest(BaseModel):
    id: UUID
    name: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_db()
    except Exception as e:
        raise
    yield

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

app = FastAPI(lifespan=lifespan)

async def open_lock(
    id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    api_key_header: str = Security(api_key_header),
):
    key_db = await session.scalar(select(Key.key).where(Key.id == id))
    print(f"DB Key: {key_db}, Header Key: {api_key_header}")
    if key_db and str(key_db) == api_key_header:
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not open lock"
    )

@app.get("/uuid")
def get_uuid():
    return uuid4()

@app.post("/create/key")
async def create_api_key(
    request: Annotated[ApiKeyRequest, Body()],
    session: Annotated[AsyncSession, Depends(get_session)]
):
    key_obj = Key(
        id = request.id,
        name = request.name,
        key = uuid4()
    )
    
    session.add(key_obj)
    await session.commit()
    await session.refresh(key_obj)
    return key_obj

@app.get("/unlock/treasure/{id}")
async def unlock_treasure(
    id: UUID = Path(),
    is_unlocked: UUID = Depends(open_lock)
):
    return {
        "message": "7 CRORE!!!!!"
    }