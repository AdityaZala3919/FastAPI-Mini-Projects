from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET", "DELETE"],   # DELETE not allowed
    allow_headers=["*"],
)

@app.delete("/users")
def delete_user():
    return {"message": "deleted"}

"""
Access to fetch at 'http://localhost:8000/users' from origin 'http://localhost:3000' has been blocked by CORS policy: Response to preflight request doesn't pass access control check: It does not have HTTP ok status.Understand this error
(index):64  PUT http://localhost:8000/users net::ERR_FAILED
updateUser @ (index):64
onclick @ (index):13Understand this error
(index):1 Access to fetch at 'http://localhost:8000/users' from origin 'http://localhost:3000' has been blocked by CORS policy: Response to preflight request doesn't pass access control check: It does not have HTTP ok status.Understand this error
(index):52  DELETE http://localhost:8000/users net::ERR_FAILED
"""