from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET"],
    allow_headers=["Content-Type", "Authorization"],  # Authorization missing
)

@app.get("/users")
def get_users():
    return {"users": ["Alice", "Bob"]}

"""
Access to fetch at 'http://localhost:8000/users' from origin 'http://localhost:3000'
has been blocked by CORS policy: Response to preflight request doesn't pass access control
check: It does not have HTTP ok status.
"""