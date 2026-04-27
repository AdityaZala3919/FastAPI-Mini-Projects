# Celery Learning Project

A mini-project to learn **background task execution with Celery**, message queuing with **Redis**, and async programming with **FastAPI**. This project demonstrates how to build scalable, asynchronous task processing pipelines.

## 📚 Learning Objectives

After completing this project, you will understand:

- ✅ How to configure Celery with a message broker (Redis)
- ✅ How to define and execute asynchronous tasks
- ✅ How to track task state and progress
- ✅ How to integrate Celery with FastAPI
- ✅ How to use Redis as a message broker and result backend
- ✅ How to containerize and orchestrate services with Docker Compose

## 🏗️ Project Architecture

```
┌─────────────────┐
│   FastAPI App   │ (Port 8000)
│  (HTTP Requests)│
└────────┬────────┘
         │
         ▼
    ┌─────────────┐
    │    Redis    │ (Port 6379)
    │   Broker &  │
    │   Backend   │
    └────┬────┬───┘
         │    │
    ┌────▼┐  ┌▼─────┐
    │Task │  │Task  │
    │Queue│  │Results
    └────┬┐  └┬──────┘
         │└───┤
    ┌────▼────▼──┐
    │   Celery   │
    │   Worker   │
    │(Executes)  │
    └────────────┘
```

## 📁 Project Structure

```
celery-fastapi/
├── app.py                    # FastAPI application with endpoints
├── celery_app.py             # Celery configuration and Redis setup
├── tasks.py                  # Background task definitions
├── requirements.txt          # Python dependencies
├── docker-compose.yml        # Multi-container orchestration
├── Dockerfile                # Container image definition
├── .env                      # Environment variables
└── README.md                 # This file
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.8+ (for local development)
- Redis (for local development without Docker)

### Option 1: Docker Compose (Recommended)

```bash
# Navigate to the project directory
cd celery-fastapi

# Build and start all services
docker-compose up --build

# In another terminal, test the API
curl http://localhost:8000
```

### Option 2: Local Development

#### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 2. Start Redis

```bash
# Using Docker
docker run -d -p 6379:6379 redis:7-alpine

# OR using a local Redis installation
redis-server
```

#### 3. Start Celery Worker

```bash
celery -A celery_app worker --loglevel=info
```

#### 4. Start FastAPI Server

```bash
# In another terminal
uvicorn app:app --reload
```

The API will be available at `http://localhost:8000`

## 📡 API Endpoints

### 1. Welcome Endpoint

```
GET /
```

Returns information about the project and available endpoints.

**Response:**
```json
{
  "message": "Welcome to Celery Learning Project",
  "endpoints": {
    "start_task": "POST /task/start",
    "task_status": "GET /task/{task_id}/status",
    "health": "GET /health",
    "docs": "GET /docs"
  }
}
```

### 2. Start a Background Task

```
POST /task/start?duration=60
```

Triggers a new background task that runs for the specified duration.

**Parameters:**
- `duration` (optional, default: 60): Duration in seconds (1-300)

**Response:**
```json
{
  "task_id": "abc-123-def-456",
  "status": "Task queued for execution",
  "duration": 60,
  "check_status_at": "/task/abc-123-def-456/status"
}
```

### 3. Check Task Status

```
GET /task/{task_id}/status
```

Polls the task's current state and progress.

**Response Examples:**

#### Pending:
```json
{
  "task_id": "abc-123-def-456",
  "state": "PENDING",
  "message": "Task is waiting to be processed"
}
```

#### In Progress:
```json
{
  "task_id": "abc-123-def-456",
  "state": "PROGRESS",
  "progress": {
    "current": 30,
    "total": 60,
    "status": "Progress: 30/60 seconds"
  }
}
```

#### Completed:
```json
{
  "task_id": "abc-123-def-456",
  "state": "SUCCESS",
  "result": {
    "status": "completed",
    "duration": 60,
    "message": "Task completed successfully after 60 seconds",
    "task_id": "abc-123-def-456"
  }
}
```

### 4. Health Check

```
GET /health
```

Checks the health of the application and its dependencies.

**Response:**
```json
{
  "status": "healthy",
  "celery": "healthy",
  "redis": "healthy"
}
```

### 5. Documentation

```
GET /docs
```

Returns API usage examples and workflow documentation.

## 🔄 Workflow Example

### Using cURL

```bash
# Step 1: Start a task (duration: 30 seconds)
curl -X POST "http://localhost:8000/task/start?duration=30"

# Output:
# {
#   "task_id": "a1b2c3d4-e5f6-g7h8-i9j0",
#   "status": "Task queued for execution",
#   "duration": 30
# }

# Step 2: Check task status (repeat every few seconds)
curl "http://localhost:8000/task/a1b2c3d4-e5f6-g7h8-i9j0/status"

# Output (PROGRESS):
# {
#   "task_id": "a1b2c3d4-e5f6-g7h8-i9j0",
#   "state": "PROGRESS",
#   "progress": {
#     "current": 10,
#     "total": 30,
#     "status": "Progress: 10/30 seconds"
#   }
# }

# Step 3: Wait for completion and check final status
curl "http://localhost:8000/task/a1b2c3d4-e5f6-g7h8-i9j0/status"

# Output (SUCCESS):
# {
#   "task_id": "a1b2c3d4-e5f6-g7h8-i9j0",
#   "state": "SUCCESS",
#   "result": {
#     "status": "completed",
#     "duration": 30,
#     "message": "Task completed successfully after 30 seconds"
#   }
# }
```

### Using Python Requests

```python
import requests
import time

BASE_URL = "http://localhost:8000"

# Start a task
response = requests.post(f"{BASE_URL}/task/start", params={"duration": 30})
task_data = response.json()
task_id = task_data["task_id"]
print(f"Task started with ID: {task_id}")

# Poll for completion
while True:
    status_response = requests.get(f"{BASE_URL}/task/{task_id}/status")
    status_data = status_response.json()
    
    state = status_data["state"]
    print(f"Task state: {state}")
    
    if state == "SUCCESS":
        print(f"Task completed! Result: {status_data['result']}")
        break
    elif state == "FAILURE":
        print(f"Task failed! Error: {status_data['error']}")
        break
    
    time.sleep(2)  # Check every 2 seconds
```

## 🔍 Monitoring and Debugging

### View Logs (Docker)

```bash
# View FastAPI app logs
docker logs celery_fastapi_app

# View Celery worker logs
docker logs celery_worker

# View Redis logs
docker logs celery_redis
```

### View Logs (Local Development)

Logs will appear in the terminal where you started each service.

### Common Issues

**Issue: "Connection refused" error**
- Ensure Redis is running
- For Docker Compose, check: `docker-compose ps`
- For local, check: `redis-cli ping`

**Issue: Task stuck in PENDING state**
- Verify Celery worker is running
- Check Celery worker logs for errors
- Ensure Redis connection is configured correctly

**Issue: Port 8000 or 6379 already in use**
- Docker: Change port mapping in `docker-compose.yml`
- Local: Modify port in `uvicorn` or `redis-server` commands

## 📊 Celery Task States

Understanding task state transitions is key to working with Celery:

| State | Description |
|-------|-------------|
| PENDING | Task is queued, waiting to be picked up by a worker |
| RECEIVED | Worker has acknowledged the task |
| STARTED | Worker has started executing the task |
| PROGRESS | Task is in progress (custom state in this project) |
| RETRY | Task is being retried after failure |
| SUCCESS | Task completed successfully |
| FAILURE | Task execution failed |

## 🛠️ Configuration Details

### Redis Broker vs Result Backend

- **Broker**: Message queue where tasks are sent (`redis://redis:6379/0`)
- **Result Backend**: Where task results are stored after execution (`redis://redis:6379/0`)

Both use the same Redis instance in this project for simplicity.

### Celery Settings

Located in `celery_app.py`:
- `task_serializer`: JSON (human-readable, compatible)
- `task_track_started`: True (enables PROGRESS updates)
- `timezone`: UTC (recommended for distributed systems)

## 🧪 Testing Multiple Concurrent Tasks

```bash
# Terminal 1: Start monitoring
watch -n 1 'curl -s http://localhost:8000/health | python -m json.tool'

# Terminal 2: Start multiple tasks
for i in {1..5}; do
  curl -X POST "http://localhost:8000/task/start?duration=30" | python -m json.tool
done

# Terminal 3: Poll status for all tasks
# (use the task IDs from the responses)
curl "http://localhost:8000/task/{task_id}/status" | python -m json.tool
```

## 📚 Advanced Topics (Next Steps)

1. **Task Retries**: Add automatic retry logic for failed tasks
2. **Task Timeouts**: Set time limits for task execution
3. **Task Priority**: Implement task routing based on priority
4. **Scheduled Tasks**: Use Celery Beat for periodic tasks
5. **Error Handling**: Advanced error handling and callbacks
6. **Scaling**: Run multiple Celery workers for parallel processing
7. **Monitoring**: Add Flower UI for real-time task monitoring

## 🔗 Useful Resources

- [Celery Documentation](https://docs.celeryproject.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Redis Documentation](https://redis.io/documentation)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

## 📝 Summary

This project teaches the fundamentals of distributed task processing:

1. **Decoupling**: Separate long-running tasks from HTTP request-response cycle
2. **Asynchronous Processing**: Handle tasks without blocking the web server
3. **Scalability**: Add more workers to process tasks in parallel
4. **Monitoring**: Track task execution and retrieve results
5. **Containerization**: Package and deploy as microservices

By completing this project, you have a solid foundation for building production-grade async applications!

---

**Created**: April 2026 | **Version**: 1.0.0
