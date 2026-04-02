# middlewares/timing_middleware.py
import time
from starlette.middleware.base import BaseHTTPMiddleware

class ProcessTimeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        response.headers["X-Process-Time"] = str(duration)
        print(f"Request took {duration:.4f} seconds")
        return response