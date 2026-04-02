from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_headers=["*"],
    allow_methods=["*"]
)

@app.get("/users")
def get_users():
    return {"users": ["Alice", "Bob"]}