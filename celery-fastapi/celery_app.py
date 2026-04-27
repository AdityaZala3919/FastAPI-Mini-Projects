import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

# Redis configuration
# Use localhost:6379 for local development, redis:6379 for Docker
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "celery_fastapi",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,  # Track when task starts
)

# Auto-discover tasks from tasks module
from tasks import simulate_computation_task 