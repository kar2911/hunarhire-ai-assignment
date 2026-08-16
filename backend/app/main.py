from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routes.dashboard import router as dashboard_router
from app.routes.interviews import router as interviews_router
from app.routes.outreach import router as outreach_router
from app.routes.outreach_webhooks import router as outreach_webhooks_router
from app.routes.people import router as people_router
from app.routes.search import router as search_router
from app.routes.webhooks import router as webhooks_router
from app.services.hunar import HunarService

import app.models
import app.outreach_models


# Create database tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="HunarHire API",
    description="AI Hiring Assistant powered by Hunar Voice Agents",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(interviews_router)
app.include_router(webhooks_router)
app.include_router(dashboard_router)
app.include_router(search_router)
app.include_router(people_router)
app.include_router(outreach_router)
app.include_router(outreach_webhooks_router)


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