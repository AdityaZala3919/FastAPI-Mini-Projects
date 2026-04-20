from pydantic import BaseModel
from uuid import UUID, uuid4
from typing import TypeVar, Generic, Optional, List
from datetime import datetime
from fastapi import status

BaseDataField = TypeVar("BaseDataField")

class BaseResponse(BaseModel, Generic[BaseDataField]):
    message: str = "Success!"
    code: int = status.HTTP_200_OK
    data: Optional[BaseDataField] = None

class PaginatedResponse(BaseModel, Generic[BaseDataField]):
    items: List[BaseDataField]
    total: int
    page: int
    size: int
    pages: int

class PromptResponse(BaseModel):
    id: UUID
    unique_id: UUID
    name: str
    prompt: str
    version: int
    created_at: datetime
    
class AgentResponse(BaseModel):
    id: UUID
    prompt_id: UUID
    name: str
    model_name: str
    temperature: float
    max_output_tokens: int

class CreatePromptRequest(BaseModel):
    name: str
    prompt: str
    
class CreateAgentRequest(BaseModel):
    name: str
    model_name: str
    prompt_id: UUID
    temperature: Optional[float] = None
    max_output_tokens: Optional[int] = None

class UpdatePromptRequest(BaseModel):
    prompt: str
    
class UpdateAgentRequest(BaseModel):
    name: Optional[str] = None
    model_name: Optional[str] = None
    prompt_id: Optional[UUID] = None
    temperature: Optional[float] = None
    max_output_tokens: Optional[int] = None

class GetPromptRequest(BaseModel):
    prompt_id: Optional[UUID] = None
    prompt_name: Optional[str] = None
    unique_id: Optional[UUID] = None

class GetAgentRequest(BaseModel):
    agent_id: Optional[UUID] = None
    agent_name: Optional[str] = None

class StartTaskRequest(BaseModel):
    user_input: str
    
class StartTaskResponse(BaseModel):
    task_id: UUID
    status: str

class TaskResponse(BaseModel):
    id: UUID
    agent_id: UUID
    status: str
    result: Optional[str] = None

class UserRegisterRequest(BaseModel):
    username: str
    password: str

class UserLoginRequest(BaseModel):
    user_id: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

class UserRegisterResponse(BaseModel):
    user_id: UUID
    username: str
    password: str

class UserLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"