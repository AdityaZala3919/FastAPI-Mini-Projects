import os
import json
import asyncio
from dotenv import load_dotenv
from groq import Groq, AsyncGroq

from fastapi import FastAPI, Form
from fastapi.responses import StreamingResponse

load_dotenv()
client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

app = FastAPI()

async def chat(input: str):
    response = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": input}
        ],
        stream=True
    )
    async for chunk in response:
        content = chunk.choices[0].delta.content
        if not content:
            continue
        yield f"data: {content}\n\n" # .choices[0].delta.get("content")

@app.post("/stream/chat")
async def stream_chat(text: str = Form()):
    return StreamingResponse(chat(text), media_type="text/event-stream")

@app.get("/stream")
async def stream():
    async def generate():
        for i in range(10):
            await asyncio.sleep(1)  # Simulate delay
            yield str(i)
    return StreamingResponse(generate(), media_type="text/plain")