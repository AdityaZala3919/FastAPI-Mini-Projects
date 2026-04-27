from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from celery.result import AsyncResult
from celery.app.control import Inspect
import redis
from celery_app import celery_app
from tasks import simulate_computation_task

# Initialize FastAPI app
app = FastAPI(
    title="Celery Learning Project",
    description="A mini-project to learn Celery background tasks with FastAPI",
    version="1.0.0"
)

# Redis connection for health checks
# Try localhost first (local development), then Docker hostname
redis_client = None
REDIS_AVAILABLE = False

for host in ["localhost", "redis"]:
    try:
        redis_client = redis.Redis(host=host, port=6379, db=0, decode_responses=True)
        redis_client.ping()
        REDIS_AVAILABLE = True
        print(f"Connected to Redis at {host}:6379")
        break
    except Exception as e:
        continue

if not REDIS_AVAILABLE:
    print("Warning: Could not connect to Redis on localhost or redis host")


@app.get("/", tags=["Root"])
async def root():
    """Welcome endpoint with project information"""
    return {
        "message": "Welcome to Celery Learning Project",
        "endpoints": {
            "start_task": "POST /task/start",
            "task_status": "GET /task/{task_id}/status",
            "health": "GET /health",
            "docs": "GET /docs"
        }
    }


@app.post("/task/start", tags=["Tasks"])
async def start_task(duration: int = 60):
    """
    Trigger a background task.
    
    Args:
        duration: Duration in seconds for the task to run (default: 60)
    
    Returns:
        dict: Task ID and status
    """
    if duration < 1 or duration > 300:
        raise HTTPException(
            status_code=400,
            detail="Duration must be between 1 and 300 seconds"
        )
    
    # Send task to Celery
    task = simulate_computation_task.delay(duration=duration)
    
    return {
        "task_id": task.id,
        "status": "Task queued for execution",
        "duration": duration,
        "check_status_at": f"/task/{task.id}/status"
    }


@app.get("/task/{task_id}/status", tags=["Tasks"])
async def get_task_status(task_id: str):
    """
    Get the status of a background task.
    
    Args:
        task_id: The ID of the task to check
    
    Returns:
        dict: Task state, progress, and result (if available)
    """
    task_result = AsyncResult(task_id, app=celery_app)
    
    if task_result.state == "PENDING":
        response = {
            "task_id": task_id,
            "state": task_result.state,
            "message": "Task is waiting to be processed"
        }
    elif task_result.state == "PROGRESS":
        response = {
            "task_id": task_id,
            "state": task_result.state,
            "progress": task_result.info
        }
    elif task_result.state == "SUCCESS":
        response = {
            "task_id": task_id,
            "state": task_result.state,
            "result": task_result.result
        }
    elif task_result.state == "FAILURE":
        response = {
            "task_id": task_id,
            "state": task_result.state,
            "error": str(task_result.info)
        }
    else:
        response = {
            "task_id": task_id,
            "state": task_result.state,
            "info": task_result.info
        }
    
    return response


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Check health status of the application and its dependencies.
    
    Returns:
        dict: Health status of app, Celery, and Redis
    """
    celery_status = "unhealthy"
    redis_status = "unhealthy"
    
    try:
        # Check Redis connection
        if REDIS_AVAILABLE and redis_client:
            redis_client.ping()
            redis_status = "healthy"
    except Exception as e:
        print(f"Redis health check failed: {e}")
    
    try:
        # Check if Celery workers are connected
        inspect = Inspect(app=celery_app)
        stats = inspect.stats()
        if stats:  # If stats() returns data, at least one worker is connected
            celery_status = "healthy"
    except Exception as e:
        print(f"Celery health check failed: {e}")
    
    overall_status = "healthy" if (celery_status == "healthy" and redis_status == "healthy") else "degraded"
    
    return {
        "status": overall_status,
        "celery": celery_status,
        "redis": redis_status
    }