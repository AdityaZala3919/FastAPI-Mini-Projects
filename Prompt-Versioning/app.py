from uuid import UUID
from fastapi import FastAPI, Path, Form, Query
from fastapi.responses import RedirectResponse

app = FastAPI()

@app.get("/")
def get_root():
    return RedirectResponse("/docs")

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from models import Prompts
from database import get_session
from uuid import uuid4
from datetime import datetime

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
        created_at=datetime.now(),
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
        "name": prompt_obj.name,
        "prompt": prompt_obj.prompt,
        "version": prompt_obj.version,
        "created_at": prompt_obj.created_at,
    }

@app.get("/prompts", tags=["Prompt"])
async def get_all_prompts():
    pass

@app.get("/prompt/{prompt_id}", tags=["Prompt"])
async def get_prompt_by_id(
    prompt_id: UUID = Path(...),
):
    pass

@app.get("/prompt/{prompt_name}", tags=["Prompt"])
async def get_prompt_by_name(
    prompt_name: str = Path(...),
):
    pass

@app.put("/prompt/{prompt_id}", tags=["Prompt"])
async def update_prompt(
    prompt_id: UUID = Path(...),
):
    pass

@app.delete("/prompt/{prompt_id}", tags=["Prompt"])
async def delete_prompt(
    prompt_id: UUID = Path(...),
):
    pass

# -------------------------------------------------------------------------

@app.post("/create/agent", tags=["Agent"])
async def create_agent(
    name: str,
    model_name: str,
    prompt_id: UUID,
    temperature: float,
    max_output_tokens: int,
):
    pass

@app.get("/agents", tags=["Agent"])
async def get_all_agents():
    pass

@app.get("/agent/{agent_id}", tags=["Agent"])
async def get_agent_by_id(
    agent_id: UUID = Path(...),
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