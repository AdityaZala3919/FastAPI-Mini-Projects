from uuid import UUID, uuid4
from typing import Annotated
from fastapi import FastAPI, Path, Body, Query, Depends, HTTPException, status
from fastapi_pagination import Page, add_pagination, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from models import Prompts, Agents
from schemas import (
    BaseResponse,
    PromptResponse,
    AgentResponse,
    PaginatedResponse,
    CreatePromptRequest,
    CreateAgentRequest,
    GetPromptRequest,
    GetAgentRequest,
    UpdatePromptRequest,
    UpdateAgentRequest,
)
from database import get_session, init_db
from services import PromptServices, AgentServices, ResponseService

def pagination_params(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
):
    return {
        "page": page,
        "size": size,
    }

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)

add_pagination(app)

@app.get("/")
def get_root():
    return RedirectResponse("/docs")

@app.post("/create/prompt", tags=["Prompt"])
async def create_prompt(
    service: Annotated[PromptServices, Depends()],
    request: Annotated[CreatePromptRequest, Body()],
) -> BaseResponse[PromptResponse]:
    return BaseResponse(data=await service.create_prompt(**request.model_dump()))

@app.get("/prompts", tags=["Prompt"])
async def get_all_prompts(
    service: Annotated[PromptServices, Depends()],
    params: Annotated[Params, Depends()],
) -> BaseResponse[Page[PromptResponse]]:
    return BaseResponse(data=await service.get_all_prompts(params=params)) 

@app.get("/prompt", tags=["Prompt"])
async def get_prompt(
    service: Annotated[PromptServices, Depends()],
    request: Annotated[GetPromptRequest, Query()],
) -> BaseResponse[PromptResponse]:
    return BaseResponse(data=await service.get_prompt(**request.model_dump()))

@app.put("/prompt/{prompt_id}", tags=["Prompt"])
async def update_prompt(
    prompt_id: Annotated[UUID, Path()],
    service: Annotated[PromptServices, Depends()],
    request: Annotated[UpdatePromptRequest, Query()],
) -> BaseResponse[PromptResponse]:
    return BaseResponse(data=await service.update_prompt(prompt_id=prompt_id, prompt=request.prompt))

@app.delete("/prompt/{unique_id}", tags=["Prompt"])
async def delete_prompt(
    service: Annotated[PromptServices, Depends()],
    unique_id: Annotated[UUID, Path()],
) -> BaseResponse[PromptResponse]:
    return BaseResponse(data=await service.delete_prompt(unique_id=unique_id))

# -------------------------------------------------------------------------

@app.post("/create/agent", tags=["Agent"])
async def create_agent(
    service: Annotated[AgentServices, Depends()],
    request: Annotated[CreateAgentRequest, Query()],
) -> BaseResponse[AgentResponse]:
    return BaseResponse(data=await service.create_agent(**request.model_dump()))

@app.get("/agents", tags=["Agent"])
async def get_all_agents(
    service: Annotated[AgentServices, Depends()],
    pagination: Annotated[dict, Depends(pagination_params)],
) -> BaseResponse[PaginatedResponse[AgentResponse]]:
    return BaseResponse(data=await service.get_all_agents(page=pagination["page"], size=pagination["size"]))

@app.get("/agent", tags=["Agent"])
async def get_agent_by_id(
    service: Annotated[AgentServices, Depends()],
    request: Annotated[GetAgentRequest, Query()],
) -> BaseResponse[AgentResponse]:
    return BaseResponse(data=await service.get_agent(**request.model_dump()))

@app.put("/agent/{agent_id}", tags=["Agent"])
async def update_agent(
    agent_id: Annotated[UUID, Path()],
    service: Annotated[AgentServices, Depends()],
    request: Annotated[UpdateAgentRequest, Query()],
) -> BaseResponse[AgentResponse]:
    return BaseResponse(data=await service.update_agent(agent_id=agent_id, **request.model_dump()))

@app.delete("/agent/{agent_id}", tags=["Agent"])
async def delete_agent(
    service: Annotated[AgentServices, Depends()],
    agent_id: Annotated[UUID, Path()],
) -> BaseResponse[AgentResponse]:
    return BaseResponse(data=await service.delete_agent(agent_id=agent_id))

# -------------------------------------------------------------------------

@app.get("/agent/response/{agent_id}", tags=["Response"])
async def get_response(
    agent_id: UUID = Path(...),
    user_input: str = Query(...),
):
    pass

@app.get("/test-prompt")
async def test_prompt(
    agent_id: UUID,
    service: Annotated[ResponseService, Depends()],
):
    return await service.get_agent_response(
        agent_id=agent_id,
        user_input="test input"
    )