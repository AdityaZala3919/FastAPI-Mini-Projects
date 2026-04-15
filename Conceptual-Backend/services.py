from typing import Annotated
from uuid import uuid4, UUID
import asyncio
import httpx
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq, AsyncGroq
import logging

from fastapi import Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_pagination import Page, add_pagination, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi.responses import RedirectResponse
from sqlalchemy import select, func

from database import get_session
from models import Prompts, Agents, Tasks, User
from schemas import (
    PromptResponse,
    StartTaskResponse,
    TaskResponse,
    UserResponse,
)
from security import generate_signature, verify_signature, hash_password

load_dotenv()

logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = AsyncGroq(api_key=GROQ_API_KEY)

class PromptServices():
    def __init__(self, session: Annotated[AsyncSession, Depends(get_session)]):
        self.session = session
    
    async def create_prompt(
        self,
        name: str,
        prompt: str,
    ):
        try:
            logger.debug(f"Creating prompt: name={name}")
            prompt_obj = Prompts(
                id=uuid4(),
                unique_id=uuid4(),
                name=name,
                prompt=prompt,
                version=1,
            )
            self.session.add(prompt_obj)
            await self.session.commit()
            await self.session.refresh(prompt_obj)
            logger.info(f"Prompt created successfully: id={prompt_obj.id}, unique_id={prompt_obj.unique_id}, version={prompt_obj.version}")
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating prompt '{name}': {str(e)}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        return PromptResponse(
            id=str(prompt_obj.id),
            unique_id=str(prompt_obj.unique_id),
            name=prompt_obj.name,
            prompt=prompt_obj.prompt,
            version=prompt_obj.version,
            created_at=prompt_obj.created_at,
        )
    
    async def get_all_prompts(
        self,
        params: Params,
    ):
        try:
            logger.debug(f"Fetching all prompts: page={params.page}, size={params.size}")
            query = select(Prompts).order_by(Prompts.version.desc())
            result = await paginate(self.session, query=query, params=params)
            logger.debug(f"Retrieved {len(result.items)} prompts")
            return result
        except Exception as e:
            logger.error(f"Error fetching prompts: {str(e)}", exc_info=True)
            raise
    
    async def get_prompt(
        self,
        prompt_id: UUID,
        unique_id: UUID,
        prompt_name: str,
    ):
        try:
            logger.debug(f"Searching for prompt with criteria: prompt_id={prompt_id}, unique_id={unique_id}, prompt_name={prompt_name}")
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
                logger.warning("No search criteria provided for prompt query")
                raise HTTPException(status_code=400, detail="Either prompt_id or prompt_name must be provided.")
            query = query.order_by(Prompts.version.desc()).limit(1)
            result = await self.session.execute(query)
            prompt = result.scalar_one_or_none()
            if not prompt:
                logger.warning(f"Prompt not found with criteria: prompt_id={prompt_id}, unique_id={unique_id}, prompt_name={prompt_name}")
                raise HTTPException(status_code=404, detail="Prompt not found.")
            logger.debug(f"Prompt found: id={prompt.id}, version={prompt.version}")
            return prompt
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching prompt: {str(e)}", exc_info=True)
            raise
    
    async def update_prompt(
        self,
        prompt_id: UUID,
        prompt: str,
    ):
        try:
            logger.info(f"Updating prompt: id={prompt_id}")
            query = (
                select(Prompts)
                .where(Prompts.id == prompt_id)
                .order_by(Prompts.version.desc())
                .limit(1)
            )
            result = await self.session.execute(query)
            existing = result.scalar_one_or_none()
            if not existing:
                logger.warning(f"Prompt not found for update: id={prompt_id}")
                raise HTTPException(status_code=404, detail="Prompt not found.")
            
            new_prompt = prompt if prompt is not None else existing.prompt
            new_version = int(existing.version + 1)
            
            new_prompt_obj = Prompts(
                id=existing.id,
                unique_id=uuid4(),
                name=existing.name,
                prompt=new_prompt,
                version=new_version,
            )
            self.session.add(new_prompt_obj)
            await self.session.commit()
            await self.session.refresh(new_prompt_obj)
            logger.info(f"Prompt {prompt_id} updated to version {new_version}")
        except HTTPException:
            raise
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating prompt {prompt_id}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        return PromptResponse(
            id=str(new_prompt_obj.id),
            unique_id=str(new_prompt_obj.unique_id),
            name=new_prompt_obj.name,
            prompt=new_prompt_obj.prompt,
            version=new_prompt_obj.version,
            created_at=new_prompt_obj.created_at,
        )
    
    async def delete_prompt(
        self,
        unique_id: UUID,
    ):
        try:
            logger.warning(f"Deleting prompt: unique_id={unique_id}")
            query = (
                select(Prompts)
                .where(Prompts.unique_id == unique_id)
            )
            result = await self.session.execute(query)
            prompt = result.scalar_one_or_none()
            if not prompt:
                logger.error(f"Prompt not found for deletion: unique_id={unique_id}")
                raise HTTPException(status_code=404, detail="Prompt not found.")
            await self.session.delete(prompt)
            await self.session.commit()
            logger.info(f"Prompt deleted successfully: unique_id={unique_id}")
            return prompt
        except HTTPException:
            raise
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error deleting prompt {unique_id}: {str(e)}", exc_info=True)
            raise


class AgentServices():
    def __init__(self, session: Annotated[AsyncSession, Depends(get_session)]):
        self.session = session
    
    async def create_agent(
        self,
        name: str,
        model_name: str,
        prompt_id: UUID,
        temperature: float,
        max_output_tokens: int,
    ):
        try:
            logger.debug(f"Creating agent: name={name}, model={model_name}")
            agent_obj = Agents(
                id=uuid4(),
                prompt_id=prompt_id,
                name=name,
                model_name=model_name,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
            )
            self.session.add(agent_obj)
            await self.session.commit()
            await self.session.refresh(agent_obj)
            logger.info(f"Agent created successfully: id={agent_obj.id}, name={name}, model={model_name}")
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating agent '{name}': {str(e)}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        return agent_obj
    
    async def get_all_agents(
        self,
        page: int,
        size: int,
    ):
        try:
            logger.debug(f"Fetching all agents: page={page}, size={size}")
            offset = (page-1)*size
            base_query = select(Agents)
            
            total_query = select(func.count()).select_from(base_query.subquery())
            total = await self.session.scalar(total_query)
            
            query = (
                base_query
                .offset(offset)
                .limit(size)
            )
            result = await self.session.execute(query)
            items = result.scalars().all()
            
            pages = (total + size - 1) // size
            logger.debug(f"Retrieved {len(items)} agents, total: {total}, pages: {pages}")
            
            return {
                "items": items,
                "total": total,
                "page": page,
                "size": size,
                "pages": pages,
            }
        except Exception as e:
            logger.error(f"Error fetching agents: {str(e)}", exc_info=True)
            raise
        
    async def get_agent(
        self,
        agent_name: str,
        agent_id: UUID,
    ):
        try:
            logger.debug(f"Searching for agent: agent_id={agent_id}, agent_name={agent_name}")
            query = select(Agents)
            if agent_id and agent_name:
                query = query.where(Agents.id == agent_id, Agents.name == agent_name)
            elif agent_id:
                query = query.where(Agents.id == agent_id)
            elif agent_name:
                query = query.where(Agents.name == agent_name)
            else:
                logger.warning("No search criteria provided for agent query")
                raise HTTPException(status_code=400, detail="Either agent_id or agent_name must be provided.")
            query = query.limit(1)
            result = await self.session.execute(query)
            agent = result.scalar_one_or_none()
            if not agent:
                logger.warning(f"Agent not found with criteria: agent_id={agent_id}, agent_name={agent_name}")
                raise HTTPException(status_code=404, detail="Agent not found.")
            logger.debug(f"Agent found: id={agent.id}, name={agent.name}")
            return agent
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching agent: {str(e)}", exc_info=True)
            raise
    
    async def update_agent(
        self,
        agent_id: UUID,
        name: str,
        model_name: str,
        prompt_id: UUID,
        temperature: float,
        max_output_tokens: int,
    ):
        try:
            logger.info(f"Updating agent: id={agent_id}")
            query = select(Agents).where(Agents.id == agent_id)
            result = await self.session.execute(query)
            agent = result.scalar_one_or_none()
            if not agent:
                logger.warning(f"Agent not found for update: id={agent_id}")
                raise HTTPException(status_code=404, detail="Agent not found.")
            
            changes = []
            if name is not None:
                agent.name = name
                changes.append(f"name={name}")
            if model_name is not None:
                agent.model_name = model_name
                changes.append(f"model={model_name}")
            if prompt_id is not None:
                agent.prompt_id = prompt_id
                changes.append(f"prompt_id={prompt_id}")
            if temperature is not None:
                agent.temperature = temperature
                changes.append(f"temperature={temperature}")
            if max_output_tokens is not None:
                agent.max_output_tokens = max_output_tokens
                changes.append(f"max_output_tokens={max_output_tokens}")
            
            logger.debug(f"Agent update changes: {', '.join(changes) if changes else 'none'}")
            
            await self.session.commit()
            await self.session.refresh(agent)
            logger.info(f"Agent {agent_id} updated successfully")
        except HTTPException:
            raise
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating agent {agent_id}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

        return agent
    
    async def delete_agent(
        self,
        agent_id: UUID,
    ):
        try:
            logger.warning(f"Deleting agent: id={agent_id}")
            query = (
                select(Agents)
                .where(Agents.id == agent_id)
            )
            result = await self.session.execute(query)
            agent = result.scalar_one_or_none()
            if not agent:
                logger.error(f"Agent not found for deletion: id={agent_id}")
                raise HTTPException(status_code=404, detail="Agent not found.")
            await self.session.delete(agent)
            await self.session.commit()
            logger.info(f"Agent deleted successfully: id={agent_id}")
            return agent
        except HTTPException:
            raise
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error deleting agent {agent_id}: {str(e)}", exc_info=True)
            raise
    

class ResponseService():
    def __init__(self, session: Annotated[AsyncSession, Depends(get_session)]):
        self.session = session
    
    async def _get_latest_prompt_text(
        self,
        prompt_id: UUID,
    ):
        try:
            logger.debug(f"Fetching latest prompt text: prompt_id={prompt_id}")
            query = (
                select(Prompts)
                .where(Prompts.id == prompt_id)
                .order_by(Prompts.version.desc())
                .limit(1)
            )
            result = await self.session.execute(query)
            prompt = result.scalar_one_or_none()
            if not prompt:
                logger.error(f"Prompt not found for LLM task: prompt_id={prompt_id}")
                raise ValueError(f"Prompt {prompt_id} not found")
            logger.debug(f"Latest prompt retrieved: version={prompt.version}")
            return prompt.prompt
        except Exception as e:
            logger.error(f"Error fetching prompt text: {str(e)}", exc_info=True)
            raise
    
    async def _get_agent_from_db(
        self,
        agent_id: UUID,
    ):
        try:
            logger.debug(f"Fetching agent from database: agent_id={agent_id}")
            query = (
                select(Agents)
                .where(Agents.id == agent_id)
            )
            result = await self.session.execute(query)
            agent = result.scalar_one_or_none()
            if agent is None:
                logger.error(f"Agent not found for LLM task: agent_id={agent_id}")
                return None
            logger.debug(f"Agent retrieved: name={agent.name}, model={agent.model_name}")
            return agent
        except Exception as e:
            logger.error(f"Error fetching agent: {str(e)}", exc_info=True)
            raise
    
    async def _store_task_info(
        self,
        task_id: UUID,
        agent_id: UUID,
        status: str,
        result: str = None,
    ):
        try:
            logger.debug(f"Storing task info: task_id={task_id}, agent_id={agent_id}, status={status}")
            task = await self.session.scalar(select(Tasks).where(Tasks.id == task_id))
            if task:
                logger.debug(f"Updating existing task: task_id={task_id}, new_status={status}")
                task.status = status
                task.result = result
            else:
                logger.debug(f"Creating new task record: task_id={task_id}")
                task = Tasks(
                    id=task_id,
                    agent_id=agent_id,
                    status=status,
                    result=result,
                )
                self.session.add(task)
            await self.session.commit()
            logger.debug(f"Task info stored successfully: task_id={task_id}")
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error storing task info: task_id={task_id}, status={status}, error={str(e)}", exc_info=True)
            raise
    
    async def _call_llm_worker(
        self,
        task_id: UUID,
        agent_id: UUID,
        user_input: str,
    ):
        try:
            logger.info(f"LLM task started: task_id={task_id}, agent_id={agent_id}")
            
            agent = await self._get_agent_from_db(agent_id=agent_id)
            if not agent:
                logger.error(f"Cannot start LLM task: agent not found (agent_id={agent_id})")
                await self._store_task_info(
                    agent_id=agent_id,
                    task_id=task_id,
                    status="failed",
                    result="Agent not found",
                )
                return
            
            prompt_id = agent.prompt_id
            prompt = await self._get_latest_prompt_text(prompt_id)
            
            logger.debug(f"Calling Groq LLM API: task_id={task_id}, model={agent.model_name}, temp={agent.temperature}")
            
            response = await client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": prompt,
                    },
                    {
                        "role": "user",
                        "content": user_input,
                    }
                ],
                model=agent.model_name,
                temperature=agent.temperature,
                max_tokens=agent.max_output_tokens
            )
            result = response.choices[0].message.content
            logger.info(f"LLM API response received: task_id={task_id}, result_length={len(result) if result else 0}")
            
            if not result or len(result.strip()) == 0:
                logger.warning(f"LLM returned empty result: task_id={task_id}")
            
            await self._store_task_info(
                agent_id=agent_id,
                task_id=task_id,
                status="success",
                result=result,
            )
            
            # Send webhook notification
            payload = {
                "task_id": str(task_id),
                "system_prompt": prompt,
                "user_input": user_input,
                "result": result,
            }
            
            logger.debug(f"Sending webhook notification: task_id={task_id}")
            
            async with httpx.AsyncClient() as webhook_client:
                try:
                    timestamp = datetime.now()
                    signature = generate_signature(
                        payload=json.dumps(payload),
                        timestamp=timestamp,
                    )
                    headers = {
                        "Content-Type": "application/json",
                        "X-Signature": signature,
                        "X-Timestamp": str(timestamp),
                    }
                    await webhook_client.post(
                        url="https://webhook.site/e03c6176-ed2e-495a-8564-c3d67d494a43",
                        content=json.dumps(payload),
                        headers=headers,
                    )
                    logger.info(f"Webhook notification sent successfully: task_id={task_id}")
                except Exception as webhook_error:
                    logger.error(f"Failed to send webhook notification: task_id={task_id}, error={str(webhook_error)}", exc_info=True)
                    # Continue gracefully - webhook failure shouldn't fail the task
        
        except Exception as e:
            logger.error(f"Error in LLM worker: task_id={task_id}, agent_id={agent_id}, error={str(e)}", exc_info=True)
            try:
                await self._store_task_info(
                    agent_id=agent_id,
                    task_id=task_id,
                    status="failed",
                    result=f"Error: {str(e)}",
                )
            except Exception as store_error:
                logger.error(f"Failed to store failed task info: task_id={task_id}, error={str(store_error)}", exc_info=True)
            
    async def start_llm_task(
        self,
        agent_id: UUID,
        task_id: UUID,
        user_input: str,
    ):
        try:
            logger.info(f"Task queued: task_id={task_id}, agent_id={agent_id}")
            
            await self._store_task_info(
                agent_id=agent_id,
                task_id=task_id,
                status="processing",
            )
            
            asyncio.create_task(
                self._call_llm_worker(
                    task_id=task_id,
                    agent_id=agent_id,
                    user_input=user_input,
                )
            )
            
            logger.debug(f"Background worker task created: task_id={task_id}")

            return StartTaskResponse(
                task_id=task_id,
                status="processing"
            )
        except Exception as e:
            logger.error(f"Error queuing LLM task: task_id={task_id}, agent_id={agent_id}, error={str(e)}", exc_info=True)
            raise
    
    async def get_task_info(
        self,
        task_id: UUID,
    ):
        try:
            logger.debug(f"Retrieving task info: task_id={task_id}")
            query = (
                select(Tasks)
                .where(Tasks.id == task_id)
            )
            result = await self.session.execute(query)
            task = result.scalar_one_or_none()
            
            if task is None:
                logger.warning(f"Task not found: task_id={task_id}")
                return None
            
            logger.debug(f"Task retrieved: task_id={task_id}, status={task.status}")
            
            return TaskResponse(
                id=task.id,
                agent_id=task.agent_id,
                status=task.status,
                result=task.result,
            )
        except Exception as e:
            logger.error(f"Error retrieving task info: task_id={task_id}, error={str(e)}", exc_info=True)
            raise
   

class UserService():
    def __init__(self, session: Annotated[AsyncSession, Depends(get_session)]):
        self.session = session
        
    async def create_user(
        self,
        username: str,
        password: str,
    ):
        try:
            logger.debug(f"Creating new user: username={username}")
            user_obj = User(
                id=uuid4(),
                username=username,
                hashed_password=hash_password(password)
            )
            self.session.add(user_obj)
            await self.session.commit()
            await self.session.refresh(user_obj)
            logger.info(f"User created successfully: user_id={user_obj.id}, username={username}")
            return UserResponse(
                user_id=user_obj.id,
                username=user_obj.username,
                password=password,
            )
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating user: username={username}, error={str(e)}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
    async def get_user(
        self,
        username: str = None,
        user_id: str = None,
    ):
        try:
            logger.debug(f"Fetching user: username={username}, user_id={user_id}")
            query = select(User)
            if user_id:
                query = query.where(User.id == user_id)
                logger.debug(f"Querying user by user_id={user_id}")
            elif username:
                query = query.where(User.username == username)
                logger.debug(f"Querying user by username={username}")
            result = await self.session.execute(query)
            user = result.scalar_one_or_none()
            if not user: 
                logger.warning(f"User not found: username={username}, user_id={user_id}")
                raise HTTPException(status_code=404, detail="User not found.")
            logger.info(f"User retrieved successfully: user_id={user.id}, username={user.username}")
            return UserResponse(
                user_id=user.id,
                username=user.username,
                password=user.hashed_password,
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching user: username={username}, user_id={user_id}, error={str(e)}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        
    
"""
todo webhook endpoint
        
"""