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
import logging
import logging.handlers
import os

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
    StartTaskRequest,
    StartTaskResponse,
    TaskResponse,
)
from database import get_session, init_db
from services import PromptServices, AgentServices, ResponseService

# Configure logging
LOG_FILE = "app.log"
log_level = logging.DEBUG

logger = logging.getLogger(__name__)
logger.setLevel(log_level)

# Create formatters
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(log_level)
console_handler.setFormatter(formatter)

# File handler with rotation
file_handler = logging.handlers.RotatingFileHandler(
    LOG_FILE,
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=5
)
file_handler.setLevel(log_level)
file_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

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
    logger.info("=" * 60)
    logger.info("Application startup initiated")
    try:
        await init_db()
        logger.info("Database initialization completed successfully")
        logger.info("Application ready to accept requests")
        logger.info("=" * 60)
    except Exception as e:
        logger.error(f"Failed to initialize database during startup: {str(e)}", exc_info=True)
        raise
    
    yield
    
    logger.info("=" * 60)
    logger.info("Application shutdown initiated")
    logger.info("=" * 60)

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
    try:
        logger.debug(f"POST /create/prompt - Creating prompt: {request.name}")
        result = await service.create_prompt(**request.model_dump())
        logger.info(f"Prompt created successfully: {result.id}")
        return BaseResponse(data=result)
    except Exception as e:
        logger.error(f"Error creating prompt: {str(e)}", exc_info=True)
        raise

@app.get("/prompts", tags=["Prompt"])
async def get_all_prompts(
    service: Annotated[PromptServices, Depends()],
    params: Annotated[Params, Depends()],
) -> BaseResponse[Page[PromptResponse]]:
    try:
        logger.debug(f"GET /prompts - Fetching prompts with pagination: page={params.page}, size={params.size}")
        result = await service.get_all_prompts(params=params)
        logger.debug(f"Retrieved {len(result.items)} prompts from database")
        return BaseResponse(data=result)
    except Exception as e:
        logger.error(f"Error fetching prompts: {str(e)}", exc_info=True)
        raise 

@app.get("/prompt", tags=["Prompt"])
async def get_prompt(
    service: Annotated[PromptServices, Depends()],
    request: Annotated[GetPromptRequest, Query()],
) -> BaseResponse[PromptResponse]:
    try:
        logger.debug(f"GET /prompt - Searching for prompt with criteria: {request.model_dump()}")
        result = await service.get_prompt(**request.model_dump())
        logger.debug(f"Prompt found: {result.id}")
        return BaseResponse(data=result)
    except Exception as e:
        logger.error(f"Error fetching prompt: {str(e)}", exc_info=True)
        raise

@app.put("/prompt/{prompt_id}", tags=["Prompt"])
async def update_prompt(
    prompt_id: Annotated[UUID, Path()],
    service: Annotated[PromptServices, Depends()],
    request: Annotated[UpdatePromptRequest, Query()],
) -> BaseResponse[PromptResponse]:
    try:
        logger.info(f"PUT /prompt/{prompt_id} - Updating prompt")
        result = await service.update_prompt(prompt_id=prompt_id, prompt=request.prompt)
        logger.info(f"Prompt {prompt_id} updated to version {result.version}")
        return BaseResponse(data=result)
    except Exception as e:
        logger.error(f"Error updating prompt {prompt_id}: {str(e)}", exc_info=True)
        raise

@app.delete("/prompt/{unique_id}", tags=["Prompt"])
async def delete_prompt(
    service: Annotated[PromptServices, Depends()],
    unique_id: Annotated[UUID, Path()],
) -> BaseResponse[PromptResponse]:
    try:
        logger.warning(f"DELETE /prompt/{unique_id} - Deleting prompt")
        result = await service.delete_prompt(unique_id=unique_id)
        logger.info(f"Prompt deleted: {unique_id}")
        return BaseResponse(data=result)
    except Exception as e:
        logger.error(f"Error deleting prompt {unique_id}: {str(e)}", exc_info=True)
        raise

# -------------------------------------------------------------------------

@app.post("/create/agent", tags=["Agent"])
async def create_agent(
    service: Annotated[AgentServices, Depends()],
    request: Annotated[CreateAgentRequest, Query()],
) -> BaseResponse[AgentResponse]:
    try:
        logger.debug(f"POST /create/agent - Creating agent: {request.name}")
        result = await service.create_agent(**request.model_dump())
        logger.info(f"Agent created successfully: {result.id}")
        return BaseResponse(data=result)
    except Exception as e:
        logger.error(f"Error creating agent: {str(e)}", exc_info=True)
        raise

@app.get("/agents", tags=["Agent"])
async def get_all_agents(
    service: Annotated[AgentServices, Depends()],
    pagination: Annotated[dict, Depends(pagination_params)],
) -> BaseResponse[PaginatedResponse[AgentResponse]]:
    try:
        logger.debug(f"GET /agents - Fetching agents with pagination: page={pagination['page']}, size={pagination['size']}")
        result = await service.get_all_agents(page=pagination["page"], size=pagination["size"])
        logger.debug(f"Retrieved {len(result['items'])} agents, total: {result['total']}")
        return BaseResponse(data=result)
    except Exception as e:
        logger.error(f"Error fetching agents: {str(e)}", exc_info=True)
        raise

@app.get("/agent", tags=["Agent"])
async def get_agent_by_id(
    service: Annotated[AgentServices, Depends()],
    request: Annotated[GetAgentRequest, Query()],
) -> BaseResponse[AgentResponse]:
    try:
        logger.debug(f"GET /agent - Searching for agent with criteria: {request.model_dump()}")
        result = await service.get_agent(**request.model_dump())
        logger.debug(f"Agent found: {result.id}")
        return BaseResponse(data=result)
    except Exception as e:
        logger.error(f"Error fetching agent: {str(e)}", exc_info=True)
        raise

@app.put("/agent/{agent_id}", tags=["Agent"])
async def update_agent(
    agent_id: Annotated[UUID, Path()],
    service: Annotated[AgentServices, Depends()],
    request: Annotated[UpdateAgentRequest, Query()],
) -> BaseResponse[AgentResponse]:
    try:
        logger.info(f"PUT /agent/{agent_id} - Updating agent")
        result = await service.update_agent(agent_id=agent_id, **request.model_dump())
        logger.info(f"Agent {agent_id} updated successfully")
        return BaseResponse(data=result)
    except Exception as e:
        logger.error(f"Error updating agent {agent_id}: {str(e)}", exc_info=True)
        raise

@app.delete("/agent/{agent_id}", tags=["Agent"])
async def delete_agent(
    service: Annotated[AgentServices, Depends()],
    agent_id: Annotated[UUID, Path()],
) -> BaseResponse[AgentResponse]:
    try:
        logger.warning(f"DELETE /agent/{agent_id} - Deleting agent")
        result = await service.delete_agent(agent_id=agent_id)
        logger.info(f"Agent deleted: {agent_id}")
        return BaseResponse(data=result)
    except Exception as e:
        logger.error(f"Error deleting agent {agent_id}: {str(e)}", exc_info=True)
        raise

# -------------------------------------------------------------------------

@app.post("/agent/task/{agent_id}", tags=["Response"])
async def start_agent_task(
    service: Annotated[ResponseService, Depends()],
    agent_id: Annotated[UUID, Path()],
    request: Annotated[StartTaskRequest, Body()],
) -> BaseResponse[StartTaskResponse]:
    try:
        task_id = uuid4()
        logger.info(f"POST /agent/task/{agent_id} - Starting LLM task: task_id={task_id}")
        result = await service.start_llm_task(agent_id=agent_id, task_id=task_id, user_input=request.user_input)
        logger.info(f"LLM task queued successfully: task_id={task_id}, agent_id={agent_id}")
        return BaseResponse(data=result)
    except Exception as e:
        logger.error(f"Error starting LLM task for agent {agent_id}: {str(e)}", exc_info=True)
        raise

@app.get("/agent/result/{task_id}", tags=["Response"])
async def get_result(
    service: Annotated[ResponseService, Depends()],
    task_id: Annotated[UUID, Path()],
) -> BaseResponse[TaskResponse]:
    try:
        logger.debug(f"GET /agent/result/{task_id} - Retrieving task information")
        result = await service.get_task_info(task_id=task_id)
        if result is None:
            logger.warning(f"Task not found: {task_id}")
            raise HTTPException(status_code=404, detail="Task not found.")
        logger.debug(f"Task retrieved: {task_id}, status={result.status}")
        return BaseResponse(data=result)
    except Exception as e:
        logger.error(f"Error fetching task result {task_id}: {str(e)}", exc_info=True)
        raise