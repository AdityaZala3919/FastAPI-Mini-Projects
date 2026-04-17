from uuid import UUID, uuid4
from typing import Annotated
from fastapi import FastAPI, Path, Body, Query, Depends, HTTPException, status, Request, Header
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
import json
import sentry_sdk
from dotenv import load_dotenv

from models import Prompts, Agents, User
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
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
)
from database import get_session, init_db
from services import (
    PromptServices,
    AgentServices,
    ResponseService,
    UserService,
    WebhookService,
)
from security import (
    verify_password,
    create_access_token,
    get_current_user,
)

load_dotenv()

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    send_default_pii=True,
)

# Tags metadata for Swagger UI organization
tags_metadata = [
    {
        "name": "Prompt",
        "description": "Manage prompts - Create, retrieve, update, and delete prompts with version control",
    },
    {
        "name": "Agent",
        "description": "Manage agents - Create, retrieve, update, and delete AI agents with configured models and parameters",
    },
    {
        "name": "Response",
        "description": "Execute tasks and retrieve results - Queue LLM tasks and fetch their results asynchronously",
    },
]

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

app = FastAPI(
    title="Prompt Versioning API",
    description="A FastAPI application for managing prompts, agents, and running LLM tasks with version control and async task execution",
    version="1.0.0",
    lifespan=lifespan,
    openapi_tags=tags_metadata,
    swagger_ui_parameters={
        "deepLinking": False,
        "defaultModelsExpandDepth": -1,
        "displayRequestDuration": True,
        "requestSnippetsEnabled": True,
        "withCredentials": True,
        "persistAuthorization": True,
        "tryItOutEnabled": True,
    },
)

add_pagination(app)

@app.get("/")
def get_root():
    return RedirectResponse("/docs")

@app.get("/health")
def get_health():
    return {"status": "Ok"}

@app.post(
    "/create/prompt",
    tags=["Prompt"],
    summary="Create a new prompt",
    description="Create a new prompt with version 1. Each prompt is uniquely identified and can be updated to create new versions.",
    response_description="Successfully created prompt with unique ID and version",
)
async def create_prompt(
    service: Annotated[PromptServices, Depends()],
    request: Annotated[CreatePromptRequest, Body(description="Prompt details including name and content")],
) -> BaseResponse[PromptResponse]:
    """Create a new prompt.
    
    - **name**: Unique name for the prompt
    - **prompt**: The actual prompt content for the AI model
    """
    try:
        logger.debug(f"POST /create/prompt - Creating prompt: {request.name}")
        result = await service.create_prompt(**request.model_dump())
        logger.info(f"Prompt created successfully: {result.id}")
        return BaseResponse(data=result)
    except Exception as e:
        logger.error(f"Error creating prompt: {str(e)}", exc_info=True)
        raise

@app.get(
    "/prompts",
    tags=["Prompt"],
    summary="List all prompts",
    description="Retrieve all prompts with pagination support. Returns prompts sorted by version in descending order.",
    response_description="Paginated list of all prompts",
)
async def get_all_prompts(
    service: Annotated[PromptServices, Depends()],
    params: Annotated[Params, Depends()],
) -> BaseResponse[Page[PromptResponse]]:
    """Get all prompts with pagination.
    
    Query parameters:
    - **page**: Page number (default: 1)
    - **size**: Number of items per page (default: 50, max: 100)
    """
    try:
        logger.debug(f"GET /prompts - Fetching prompts with pagination: page={params.page}, size={params.size}")
        result = await service.get_all_prompts(params=params)
        logger.debug(f"Retrieved {len(result.items)} prompts from database")
        return BaseResponse(data=result)
    except Exception as e:
        logger.error(f"Error fetching prompts: {str(e)}", exc_info=True)
        raise 

@app.get(
    "/prompt",
    tags=["Prompt"],
    summary="Get a single prompt",
    description="Retrieve a single prompt by providing at least one search criterion: prompt_id, unique_id, or prompt_name.",
    response_description="Single prompt matching the search criteria",
)
async def get_prompt(
    service: Annotated[PromptServices, Depends()],
    request: Annotated[GetPromptRequest, Query(description="Search criteria for the prompt")],
) -> BaseResponse[PromptResponse]:
    """Get a single prompt.
    
    Provide at least one of:
    - **prompt_id**: UUID of the prompt
    - **unique_id**: Unique identifier of the prompt
    - **prompt_name**: Name of the prompt
    """
    try:
        logger.debug(f"GET /prompt - Searching for prompt with criteria: {request.model_dump()}")
        result = await service.get_prompt(**request.model_dump())
        logger.debug(f"Prompt found: {result.id}")
        return BaseResponse(data=result)
    except Exception as e:
        logger.error(f"Error fetching prompt: {str(e)}", exc_info=True)
        raise

@app.put(
    "/prompt/{prompt_id}",
    tags=["Prompt"],
    summary="Update a prompt",
    description="Update prompt content. A new version is automatically created while keeping the original version history.",
    response_description="Updated prompt with incremented version",
)
async def update_prompt(
    prompt_id: Annotated[UUID, Path(description="The UUID of the prompt to update")],
    service: Annotated[PromptServices, Depends()],
    request: Annotated[UpdatePromptRequest, Query(description="New prompt content")],
) -> BaseResponse[PromptResponse]:
    """Update a prompt and create a new version.
    
    - **prompt_id**: UUID of the prompt to update
    - **prompt**: New prompt content (replaces previous)
    """
    try:
        logger.info(f"PUT /prompt/{prompt_id} - Updating prompt")
        result = await service.update_prompt(prompt_id=prompt_id, prompt=request.prompt)
        logger.info(f"Prompt {prompt_id} updated to version {result.version}")
        return BaseResponse(data=result)
    except Exception as e:
        logger.error(f"Error updating prompt {prompt_id}: {str(e)}", exc_info=True)
        raise

@app.delete(
    "/prompt/{unique_id}",
    tags=["Prompt"],
    summary="Delete a prompt",
    description="Delete a prompt by its unique ID. This is a destructive operation and cannot be undone.",
    response_description="The deleted prompt",
)
async def delete_prompt(
    service: Annotated[PromptServices, Depends()],
    unique_id: Annotated[UUID, Path(description="The unique ID of the prompt to delete")],
) -> BaseResponse[PromptResponse]:
    """Delete a prompt.
    
    Warning: This operation is irreversible.
    - **unique_id**: Unique identifier of the prompt
    """
    try:
        logger.warning(f"DELETE /prompt/{unique_id} - Deleting prompt")
        result = await service.delete_prompt(unique_id=unique_id)
        logger.info(f"Prompt deleted: {unique_id}")
        return BaseResponse(data=result)
    except Exception as e:
        logger.error(f"Error deleting prompt {unique_id}: {str(e)}", exc_info=True)
        raise

# -------------------------------------------------------------------------

@app.post(
    "/create/agent",
    tags=["Agent"],
    summary="Create a new agent",
    description="Create a new AI agent with specified model, temperature, and token limits. The agent uses an associated prompt for system behavior.",
    response_description="Successfully created agent",
)
async def create_agent(
    service: Annotated[AgentServices, Depends()],
    request: Annotated[CreateAgentRequest, Query(description="Agent configuration details")],
) -> BaseResponse[AgentResponse]:
    """Create a new AI agent.
    
    - **name**: Agent name
    - **model_name**: LLM model (e.g., 'mixtral-8x7b-32768')
    - **prompt_id**: UUID of the associated prompt
    - **temperature**: Creativity level (0.0 to 1.0)
    - **max_output_tokens**: Maximum response length
    """
    try:
        logger.debug(f"POST /create/agent - Creating agent: {request.name}")
        result = await service.create_agent(**request.model_dump())
        logger.info(f"Agent created successfully: {result.id}")
        return BaseResponse(data=result)
    except Exception as e:
        logger.error(f"Error creating agent: {str(e)}", exc_info=True)
        raise

@app.get(
    "/agents",
    tags=["Agent"],
    summary="List all agents",
    description="Retrieve all AI agents with custom pagination. Returns agents sorted by creation.",
    response_description="Paginated list of all agents",
)
async def get_all_agents(
    service: Annotated[AgentServices, Depends()],
    pagination: Annotated[dict, Depends(pagination_params)],
) -> BaseResponse[PaginatedResponse[AgentResponse]]:
    """Get all agents with pagination.
    
    Query parameters:
    - **page**: Page number (default: 1)
    - **size**: Items per page (default: 50, max: 100)
    """
    try:
        logger.debug(f"GET /agents - Fetching agents with pagination: page={pagination['page']}, size={pagination['size']}")
        result = await service.get_all_agents(page=pagination["page"], size=pagination["size"])
        logger.debug(f"Retrieved {len(result['items'])} agents, total: {result['total']}")
        return BaseResponse(data=result)
    except Exception as e:
        logger.error(f"Error fetching agents: {str(e)}", exc_info=True)
        raise

@app.get(
    "/agent",
    tags=["Agent"],
    summary="Get a single agent",
    description="Retrieve a single agent by providing agent_id or agent_name.",
    response_description="Single agent matching the criteria",
)
async def get_agent_by_id(
    service: Annotated[AgentServices, Depends()],
    request: Annotated[GetAgentRequest, Query(description="Search criteria for the agent")],
) -> BaseResponse[AgentResponse]:
    """Get a single agent.
    
    Provide at least one of:
    - **agent_id**: UUID of the agent
    - **agent_name**: Name of the agent
    """
    try:
        logger.debug(f"GET /agent - Searching for agent with criteria: {request.model_dump()}")
        result = await service.get_agent(**request.model_dump())
        logger.debug(f"Agent found: {result.id}")
        return BaseResponse(data=result)
    except Exception as e:
        logger.error(f"Error fetching agent: {str(e)}", exc_info=True)
        raise

@app.put(
    "/agent/{agent_id}",
    tags=["Agent"],
    summary="Update an agent",
    description="Update one or more agent configuration parameters. All parameters are optional.",
    response_description="Updated agent",
)
async def update_agent(
    agent_id: Annotated[UUID, Path(description="The UUID of the agent to update")],
    service: Annotated[AgentServices, Depends()],
    request: Annotated[UpdateAgentRequest, Query(description="Agent fields to update")],
) -> BaseResponse[AgentResponse]:
    """Update an agent.
    
    - **agent_id**: UUID of the agent
    - **name**: Agent name (optional)
    - **model_name**: Model to use (optional)
    - **prompt_id**: Associated prompt UUID (optional)
    - **temperature**: Creativity level (optional)
    - **max_output_tokens**: Max response length (optional)
    """
    try:
        logger.info(f"PUT /agent/{agent_id} - Updating agent")
        result = await service.update_agent(agent_id=agent_id, **request.model_dump())
        logger.info(f"Agent {agent_id} updated successfully")
        return BaseResponse(data=result)
    except Exception as e:
        logger.error(f"Error updating agent {agent_id}: {str(e)}", exc_info=True)
        raise

@app.delete(
    "/agent/{agent_id}",
    tags=["Agent"],
    summary="Delete an agent",
    description="Delete an agent by its ID. This is a destructive operation and cannot be undone.",
    response_description="The deleted agent",
)
async def delete_agent(
    service: Annotated[AgentServices, Depends()],
    agent_id: Annotated[UUID, Path(description="The UUID of the agent to delete")],
) -> BaseResponse[AgentResponse]:
    """Delete an agent.
    
    Warning: This operation is irreversible.
    - **agent_id**: UUID of the agent
    """
    try:
        logger.warning(f"DELETE /agent/{agent_id} - Deleting agent")
        result = await service.delete_agent(agent_id=agent_id)
        logger.info(f"Agent deleted: {agent_id}")
        return BaseResponse(data=result)
    except Exception as e:
        logger.error(f"Error deleting agent {agent_id}: {str(e)}", exc_info=True)
        raise

# -------------------------------------------------------------------------

@app.post(
    "/agent/task/{agent_id}",
    tags=["Response"],
    summary="Queue an LLM task",
    description="Submit a user input to an agent and queue it for processing. The task runs asynchronously in the background.",
    response_description="Task queued successfully with status 'processing'",
)
async def start_agent_task(
    service: Annotated[ResponseService, Depends()],
    agent_id: Annotated[UUID, Path(description="The UUID of the agent to execute")],
    request: Annotated[StartTaskRequest, Body(description="User input to process")],
    current_user: Annotated[User, Depends(get_current_user)]
) -> BaseResponse[StartTaskResponse]:
    """Queue a new LLM task for an agent.
    
    This endpoint creates a task and queues it for background processing.
    Use the returned task_id to poll for results using /agent/result/{task_id}
    
    - **agent_id**: UUID of the agent to use
    - **user_input**: The input text for the LLM to process
    """
    try:
        task_id = uuid4()
        logger.info(f"POST /agent/task/{agent_id} - Starting LLM task: task_id={task_id}")
        result = await service.start_llm_task(agent_id=agent_id, task_id=task_id, user_input=request.user_input)
        logger.info(f"LLM task queued successfully: task_id={task_id}, agent_id={agent_id}")
        return BaseResponse(data=result)
    except Exception as e:
        logger.error(f"Error starting LLM task for agent {agent_id}: {str(e)}", exc_info=True)
        raise

@app.get(
    "/agent/result/{task_id}",
    tags=["Response"],
    summary="Get task result",
    description="Retrieve the current status and result of a queued task. Poll this endpoint until status is 'success' or 'failed'.",
    response_description="Task information including current status and result (if available)",
)
async def get_result(
    service: Annotated[ResponseService, Depends()],
    task_id: Annotated[UUID, Path(description="The UUID of the task to check")],
    current_user: Annotated[User, Depends(get_current_user)],
) -> BaseResponse[TaskResponse]:
    """Get task result and status.
    
    Possible status values:
    - **processing**: Task is still running
    - **success**: Task completed with a result
    - **failed**: Task encountered an error
    
    - **task_id**: UUID returned from /agent/task/{agent_id}
    """
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
    
@app.post(
    "/llm-webhook",
    tags=["Response"],
    summary="Webhook for LLM task updates",
    description="Receive webhook notifications for completed LLM tasks with signature verification for security",
    response_description="Webhook payload processed successfully",
)
async def llm_webhook(
    service: Annotated[WebhookService, Depends()],
    request: Request,
    x_signature: str = Header(None, description="HMAC signature for request verification"),
    x_timestamp: str = Header(None, description="Timestamp used for signature generation"),
) -> BaseResponse[dict]:
    """Process LLM webhook notifications.
    
    This endpoint receives webhook callbacks from the LLM system containing task results.
    All requests are verified using HMAC-SHA256 signature validation.
    
    - **x_signature**: HMAC signature header for request verification
    - **x_timestamp**: Timestamp header used in signature generation
    """
    try:
        logger.info("POST /llm-webhook - Webhook request received")
        logger.debug(f"Webhook signature header: {bool(x_signature)}")
        logger.debug(f"Webhook timestamp header: {bool(x_timestamp)}")
        logger.debug(f"Request content-type: {request.headers.get('content-type', 'Not set')}")
        logger.debug(f"Request headers: {dict(request.headers)}")
        
        raw = await request.body()
        logger.debug(f"Received raw body size: {len(raw)} bytes")
        logger.debug(f"Received raw body (first 500 chars): {raw[:500]}")
        
        result = await service.process_webhook(raw=raw, x_signature=x_signature, x_timestamp=x_timestamp)
        
        logger.info("Webhook endpoint response sent successfully")
        
        # Store webhook response as JSON
        webhook_dir = "webhook_responses"
        os.makedirs(webhook_dir, exist_ok=True)
        
        timestamp_filename = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        webhook_file = os.path.join(webhook_dir, f"webhook_{timestamp_filename}.json")
        
        webhook_data = {
            "timestamp": datetime.now().isoformat(),
            "signature": x_signature,
            "payload": json.loads(raw),
            "response": result,
        }
        
        with open(webhook_file, "w") as f:
            json.dump(webhook_data, f, indent=2, default=str)
        
        logger.info(f"Webhook response stored: {webhook_file}")
        
        return BaseResponse(data=result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in webhook endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to process webhook")

# -------------------------------------------------------------------------

@app.post("/register", tags=["User"])
async def register_user(
    service: Annotated[UserService, Depends()],
    request: Annotated[UserRegisterRequest, Body()],
) -> BaseResponse[UserResponse]:
    try:
        logger.info(f"Registration request received: username={request.username}")
        result = await service.create_user(**request.model_dump())
        logger.info(f"User registration completed successfully: username={request.username}")
        return BaseResponse(data=result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during user registration: username={request.username}, error={str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Registration failed")

@app.post("/login", tags=["User"])
async def login_user(
    service: Annotated[UserService, Depends()],
    request: Annotated[UserLoginRequest, Body()],
):
    try:
        logger.info(f"Login request received: username={request.username}")
        user = await service.get_user(username=request.username)
        
        if not user or not verify_password(request.password, user.password):
            logger.warning(f"Login attempt failed: invalid credentials for username={request.username}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        logger.debug(f"User credentials verified: username={request.username}, user_id={user.user_id}")
        token = await create_access_token(user_id=str(user.user_id))
        
        logger.info(f"User logged in successfully: username={request.username}, user_id={user.user_id}")
        return {
            "access_token": token,
            "token_type": "bearer"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during user login: username={request.username}, error={str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed")