# middlewares/logging_middleware.py
from starlette.middleware.base import BaseHTTPMiddleware

class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.count = 0

    async def dispatch(self, request, call_next):
        self.count += 1
        print(f"\nRequest #{self.count}")
        print(f"Request: {request.method} {request.url}")
        response = await call_next(request)
        print(f"Response Status: {response.status_code}")
        return response