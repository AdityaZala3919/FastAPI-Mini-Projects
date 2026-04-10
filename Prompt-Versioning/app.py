from uuid import UUID, uuid4
from fastapi import FastAPI, Path, Form, Query, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from models import Prompts, Agents
from database import get_session, init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
def get_root():
    return RedirectResponse("/docs")

@app.post("/create/prompt", tags=["Prompt"])
async def create_prompt(
    name: str,
    prompt: str,
    session: AsyncSession = Depends(get_session),
):
    prompt_obj = Prompts(
        id=uuid4(),
        unique_id=uuid4(),
        name=name,
        prompt=prompt,
        version=1,
    )
    session.add(prompt_obj)
    try:
        await session.commit()
        await session.refresh(prompt_obj)
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    return {
        "message": "Prompt created successfully",
        "id": str(prompt_obj.id),
        "unique_id": str(prompt_obj.unique_id),
        "name": prompt_obj.name,
        "prompt": prompt_obj.prompt,
        "version": prompt_obj.version,
        "created_at": prompt_obj.created_at,
    }

@app.get("/prompts", tags=["Prompt"])
async def get_all_prompts(
    session: AsyncSession = Depends(get_session),
):
    query = select(Prompts)
    query = query.order_by(Prompts.version.desc())
    result = await session.execute(query)
    return list(result.scalars().all())

@app.get("/prompt", tags=["Prompt"])
async def get_prompt_by_id_or_name(
    prompt_id: UUID = Query(None),
    prompt_name: str = Query(None),
    unique_id: UUID = Query(None),
    session: AsyncSession = Depends(get_session),
):
    query = select(Prompts)
    if prompt_id and prompt_name and unique_id:
        query = query.where(Prompts.id == prompt_id, Prompts.name == prompt_name, Prompts.unique_id == unique_id)
    elif prompt_id:
        query = query.where(Prompts.id == prompt_id)
    elif prompt_name:
        query = query.where(Prompts.name == prompt_name)
    elif unique_id:
        query = query.where(Prompts.unique_id == unique_id)
    else:
        raise HTTPException(status_code=400, detail="Either prompt_id or prompt_name must be provided.")
    query = query.order_by(Prompts.version.desc()).limit(1)
    result = await session.execute(query)
    prompt = result.scalar_one_or_none()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found.")
    return prompt

@app.put("/prompt/{prompt_id}", tags=["Prompt"])
async def update_prompt(
    prompt_id: UUID = Path(...),
    prompt: str = None,
    session: AsyncSession = Depends(get_session),
):
    query = (
        select(Prompts)
        .where(Prompts.id == prompt_id)
        .order_by(Prompts.version.desc())
        .limit(1)
    )
    result = await session.execute(query)
    existing = result.scalar_one_or_none()
    if not existing:
        raise HTTPException(status_code=404, detail="Prompt not found.")
    
    new_prompt = prompt if prompt is not None else existing.prompt
    
    new_prompt_obj = Prompts(
        id=existing.id,
        unique_id=uuid4(),
        name=existing.name,
        prompt=new_prompt,
        version=int(existing.version+1),
    )
    session.add(new_prompt_obj)
    try:
        await session.commit()
        await session.refresh(new_prompt_obj)
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    return {
        "message": "Prompt updated successfully",
        "id": str(new_prompt_obj.id),
        "unique_id": str(new_prompt_obj.unique_id),
        "name": new_prompt_obj.name,
        "prompt": new_prompt_obj.prompt,
        "version": new_prompt_obj.version,
        "created_at": new_prompt_obj.created_at,
    }

@app.delete("/prompt/{unique_id}", tags=["Prompt"])
async def delete_prompt(
    unique_id: UUID = Path(...),
    session: AsyncSession = Depends(get_session),
):
    query = (
        select(Prompts)
        .where(Prompts.unique_id == unique_id)
    )
    result = await session.execute(query)
    prompt = result.scalar_one_or_none()
    await session.delete(prompt)
    await session.commit()
    return prompt

# -------------------------------------------------------------------------

@app.post("/create/agent", tags=["Agent"])
async def create_agent(
    name: str,
    model_name: str,
    prompt_id: UUID,
    temperature: float,
    max_output_tokens: int,
    session: AsyncSession = Depends(get_session),
):
    agent_obj = Agents(
        id=uuid4(),
        prompt_id=prompt_id,
        name=name,
        model_name=model_name,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
    )
    session.add(agent_obj)
    try:
        await session.commit()
        await session.refresh(agent_obj)
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    return {
        "message": "Agent created successfully",
        "id": str(agent_obj.id),
        "prompt_id": str(agent_obj.prompt_id),
        "agent_name": agent_obj.name,
        "model_name": agent_obj.model_name,
        "temperature": agent_obj.temperature,
        "max_output_tokens": agent_obj.max_output_tokens,
    }
    

@app.get("/agents", tags=["Agent"])
async def get_all_agents():
    pass

@app.get("/agent", tags=["Agent"])
async def get_agent_by_id(
    agent_id: UUID = Query(None),
    agent_name: str = Query(None),
):
    pass

@app.put("/agent/{agent_id}", tags=["Agent"])
async def update_agent(
    agent_id: UUID = Path(...),
):
    pass

@app.delete("/agent/{agent_id}", tags=["Agent"])
async def delete_agent(
    agent_id: UUID = Path(...),
):
    pass

# -------------------------------------------------------------------------

@app.get("/agent/response/{agent_id}", tags=["Response"])
async def get_response(
    agent_id: UUID = Path(...),
    user_input: str = Query(...),
):
    pass