import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.middleware.csrf import CsrfMiddleware
from app.api.middleware.request_id import RequestIDMiddleware
from app.api.routes import (
    agents,
    auth,
    autonomy,
    connectivity,
    dashboard,
    devices,
    execution,
    experiments,
    health,
    onboarding,
    resources,
    simulation,
    twin,
    virtual_farm,
)

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="PHYSICA Application Service",
    description="Local API Gateway connecting Dashboard, Agents, and Deterministic Simulation.",
    version="0.1.0"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = "default-src 'self'; connect-src 'self' http://localhost:8000; frame-ancestors 'none';"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["X-Frame-Options"] = "DENY"
        return response

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(CsrfMiddleware)
app.add_middleware(RequestIDMiddleware)

env = os.getenv("PHYSICA_ENV", "development")
# CORS configuration
allowed_origins_str = os.getenv("PHYSICA_ALLOWED_ORIGINS", "http://localhost:3000")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]

if env == "production" and "*" in allowed_origins:
    raise RuntimeError("Wildcard CORS origins (*) are strictly prohibited in production. Set PHYSICA_ALLOWED_ORIGINS to a specific domain.")

data_mode = os.getenv("PHYSICA_DATA_MODE", "LOCAL")
if data_mode == "AWS" and (not os.getenv("AWS_IOT_ENDPOINT") or not os.getenv("AWS_IOT_THING_NAME")):
    raise RuntimeError("AWS Configuration missing. AWS_IOT_ENDPOINT and AWS_IOT_THING_NAME must be set when PHYSICA_DATA_MODE=AWS.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(twin.router, prefix="/api", tags=["twin"])
app.include_router(autonomy.router, prefix="/api/autonomy", tags=["autonomy"])
app.include_router(agents.router, prefix="/api", tags=["agents"])
app.include_router(simulation.router, prefix="/api", tags=["simulation"])
app.include_router(execution.router, prefix="/api", tags=["execution"])
app.include_router(resources.router, prefix="/api", tags=["resources"])
app.include_router(dashboard.router, prefix="/api", tags=["dashboard"])
app.include_router(auth.router, tags=["auth"])
app.include_router(onboarding.router, tags=["onboarding"])
app.include_router(connectivity.router, prefix="/api", tags=["connectivity"])
app.include_router(devices.router, prefix="/api", tags=["devices"])
app.include_router(virtual_farm.router, prefix="/api", tags=["virtual_farm"])
app.include_router(experiments.router, prefix="/api/experiments", tags=["experiments"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
