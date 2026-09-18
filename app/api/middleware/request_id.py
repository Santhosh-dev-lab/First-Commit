import uuid
from contextvars import ContextVar

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

request_id_ctx_var: ContextVar[str] = ContextVar("request_id", default="")

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        req_id = request.headers.get("X-Request-ID")
        
        # Validate format (e.g., UUID-like length)
        if not req_id or len(req_id) > 64:
            req_id = str(uuid.uuid4())
            
        request_id_ctx_var.set(req_id)
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = req_id
        return response
