from fastapi import FastAPI

from app.database import Base, engine
from app.routes.dashboard import router as dashboard_router
from app.routes.interviews import router as interviews_router
from app.routes.webhooks import router as webhooks_router
from app.services.hunar import HunarService

import app.models


# Create database tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="HunarHire API",
    description="AI Hiring Assistant powered by Hunar Voice Agents",
    version="1.0.0",
)


app.include_router(interviews_router)
app.include_router(webhooks_router)
app.include_router(dashboard_router)


@app.get("/")
def root():
    return {
        "message": "HunarHire API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/api/agents")
def get_agents():
    hunar = HunarService()

    return hunar.list_agents()