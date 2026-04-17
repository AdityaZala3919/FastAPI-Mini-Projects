# import time
# from fastapi import FastAPI
# from fastapi.responses import StreamingResponse
# from fastapi.requests import Request
# from fastapi.websockets import WebSocket

# app = FastAPI()

# def generate_data(): # no need for async
#     for i in range(10):  # Simulate a data stream.
#         yield f"data: {i}\n\n"
#         time.sleep(1)

# @app.get("/stream/")
# def stream_data():
#     return StreamingResponse(generate_data(), media_type="text/plain")

# @app.post("/upload/") # no need for async
# async def upload_data(request: Request):
#     async for chunk in request.stream():
#         process_chunk(chunk)  # Process the chunk of data.