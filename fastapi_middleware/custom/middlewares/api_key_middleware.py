# middlewares/api_key_middleware.py
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse

class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        api_key = request.headers.get("x-api-key")
        if api_key != "secret123":
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid API Key"}
            )
        response = await call_next(request)
        return response