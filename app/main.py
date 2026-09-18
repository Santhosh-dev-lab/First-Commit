import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import agents, execution, health, resources, simulation, twin

app = FastAPI(
    title="PHYSICA Application Service",
    description="Local API Gateway connecting Dashboard, Agents, and Deterministic Simulation.",
    version="0.1.0"
)

# CORS configuration for local Next.js dashboard development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(twin.router, prefix="/api", tags=["twin"])
app.include_router(agents.router, prefix="/api", tags=["agents"])
app.include_router(simulation.router, prefix="/api", tags=["simulation"])
app.include_router(execution.router, prefix="/api", tags=["execution"])
app.include_router(resources.router, prefix="/api", tags=["resources"])

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
