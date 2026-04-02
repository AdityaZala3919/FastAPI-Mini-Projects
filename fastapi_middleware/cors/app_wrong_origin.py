from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:5173"],  # WRONG origin
    allow_origins=["http://localhost:3000"],  # WRONG origin
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/users")
def get_users():
    return {"users": ["Alice", "Bob"]}