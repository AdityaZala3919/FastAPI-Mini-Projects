from typing import Annotated
from uuid import uuid4, UUID
import asyncio
import httpx
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq, AsyncGroq

from fastapi import Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_pagination import Page, add_pagination, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi.responses import RedirectResponse
from sqlalchemy import select, func

from database import get_session
from models import Prompts, Agents, Tasks
from schemas import (
    PromptResponse,
    StartTaskResponse,
    TaskResponse,
)
from security import generate_signature, verify_signature

load_dotenv()

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
        prompt_obj = Prompts(
            id=uuid4(),
            unique_id=uuid4(),
            name=name,
            prompt=prompt,
            version=1,
        )
        self.session.add(prompt_obj)
        try:
            await self.session.commit()
            await self.session.refresh(prompt_obj)
        except Exception as e:
            await self.session.rollback()
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
        query = select(Prompts).order_by(Prompts.version.desc())
        return await paginate(self.session, query=query, params=params)
    
    async def get_prompt(
        self,
        prompt_id: UUID,
        unique_id: UUID,
        prompt_name: str,
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
        result = await self.session.execute(query)
        prompt = result.scalar_one_or_none()
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt not found.")
        return prompt
    
    async def update_prompt(
        self,
        prompt_id: UUID,
        prompt: str,
    ):
        query = (
            select(Prompts)
            .where(Prompts.id == prompt_id)
            .order_by(Prompts.version.desc())
            .limit(1)
        )
        result = await self.session.execute(query)
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
        self.session.add(new_prompt_obj)
        try:
            await self.session.commit()
            await self.session.refresh(new_prompt_obj)
        except Exception as e:
            await self.session.rollback()
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
        query = (
            select(Prompts)
            .where(Prompts.unique_id == unique_id)
        )
        result = await self.session.execute(query)
        prompt = result.scalar_one_or_none()
        await self.session.delete(prompt)
        await self.session.commit()
        return prompt

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
        agent_obj = Agents(
            id=uuid4(),
            prompt_id=prompt_id,
            name=name,
            model_name=model_name,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        )
        self.session.add(agent_obj)
        try:
            await self.session.commit()
            await self.session.refresh(agent_obj)
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        return agent_obj
    
    async def get_all_agents(
        self,
        page: int,
        size: int,
    ):
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
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total+size-1)//size,
        }
        
    async def get_agent(
        self,
        agent_name: str,
        agent_id: UUID,
    ):
        query = select(Agents)
        if agent_id and agent_name:
            query = query.where(Agents.id == agent_id, Agents.name == agent_name)
        elif agent_id:
            query = query.where(Agents.id == agent_id)
        elif agent_name:
            query = query.where(Agents.name == agent_name)
        else:
            raise HTTPException(status_code=400, detail="Either agent_id or agent_name must be provided.")
        query = query.limit(1)
        result = await self.session.execute(query)
        agent = result.scalar_one_or_none()
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found.")
        return agent
    
    async def update_agent(
        self,
        agent_id: UUID,
        name: str,
        model_name: str,
        prompt_id: UUID,
        temperature: float,
        max_output_tokens: int,
    ):
        query = select(Agents).where(Agents.id == agent_id)
        result = await self.session.execute(query)
        agent = result.scalar_one_or_none()
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found.")
        
        if name is not None:
            agent.name = name
        if model_name is not None:
            agent.model_name = model_name
        if prompt_id is not None:
            agent.prompt_id = prompt_id
        if temperature is not None:
            agent.temperature = temperature
        if max_output_tokens is not None:
            agent.max_output_tokens = max_output_tokens
        
        try:
            await self.session.commit()
            await self.session.refresh(agent)
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

        return agent
    
    async def delete_agent(
        self,
        agent_id: UUID,
    ):
        query = (
            select(Agents)
            .where(Agents.id == agent_id)
        )
        result = await self.session.execute(query)
        agent = result.scalar_one_or_none()
        await self.session.delete(agent)
        await self.session.commit()
        return agent
    
class ResponseService():
    def __init__(self, session: Annotated[AsyncSession, Depends(get_session)]):
        self.session = session
    
    async def _get_latest_prompt_text(
        self,
        prompt_id: UUID,
    ):
        query = (
            select(Prompts)
            .where(Prompts.id == prompt_id)
            .order_by(Prompts.version.desc())
            .limit(1)
        )
        result = await self.session.execute(query)
        prompt = result.scalar_one_or_none()
        return prompt.prompt
    
    async def _get_agent_from_db(
        self,
        agent_id: UUID,
    ):
        query = (
            select(Agents)
            .where(Agents.id == agent_id)
        )
        result = await self.session.execute(query)
        agent = result.scalar_one_or_none()
        if agent is None:
            return None
        return agent
    
    async def _store_task_info(
        self,
        task_id: UUID,
        agent_id: UUID,
        status: str,
        result: str = None,
    ):
        task = await self.session.scalar(select(Tasks).where(Tasks.id == task_id))
        if task:
            task.status = status
            task.result = result
        else:
            task = Tasks(
                id=task_id,
                agent_id=agent_id,
                status=status,
                result=result,
            )
            self.session.add(task)
        await self.session.commit()
    
    async def _call_llm_worker(
        self,
        task_id: UUID,
        agent_id: UUID,
        user_input: str,
    ):
        agent = await self._get_agent_from_db(agent_id=agent_id)
        
        prompt_id = agent.prompt_id
        prompt = await self._get_latest_prompt_text(prompt_id)
                
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
        
        await self._store_task_info(
            agent_id=agent_id,
            task_id=task_id,
            status="success",
            result=result,
        )
        
        payload = {
            "task_id": str(task_id),
            "system_prompt": prompt,
            "user_input": user_input,
            "result": result,
        }
        async with httpx.AsyncClient() as webhook_client:
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
            
    async def start_llm_task(
        self,
        agent_id: UUID,
        task_id: UUID,
        user_input: str,
    ):
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

        return StartTaskResponse(
            task_id=task_id,
            status="processing"
        )
    
    async def get_task_info(
        self,
        task_id: UUID,
    ):
        query = (
            select(Tasks)
            .where(Tasks.id == task_id)
        )
        result = await self.session.execute(query)
        task = result.scalar_one_or_none()
        
        if task is None:
            return None
        
        return TaskResponse(
            id=task.id,
            agent_id=task.agent_id,
            status=task.status,
            result=task.result,
        )
        
"""
todo webhook endpoint
        
"""