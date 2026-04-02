from faker import Faker
import random
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from middlewares.logging_middleware import LoggingMiddleware
from middlewares.timing_middleware import ProcessTimeMiddleware
from middlewares.api_key_middleware import APIKeyMiddleware

app = FastAPI()
fake = Faker()

app.add_middleware(LoggingMiddleware)
app.add_middleware(ProcessTimeMiddleware)
app.add_middleware(APIKeyMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time"]
)

@app.get("/users")
def get_users():
    length = random.randint(1, 10)
    time.sleep(length*0.1)
    return {"users": [fake.name() for _ in range(length)]}

@app.get("/products")
def get_products():
    return {"products": ["Laptop", "Phone"]}