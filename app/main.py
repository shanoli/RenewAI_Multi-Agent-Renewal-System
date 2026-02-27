"""
RenewAI — Main FastAPI Application
Multi-agent renewal system for Suraksha Life Insurance
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.db.database import init_db
from app.rag.chroma_store import init_chroma
from app.api.auth import router as auth_router
from app.api.renewal import router as renewal_router
from app.api.dashboard import router as dashboard_router
from fastapi.staticfiles import StaticFiles
from app.utils.logger import logger
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting RenewAI...")
    os.makedirs("data", exist_ok=True)
    os.makedirs("static", exist_ok=True)
    await init_db()
    init_chroma()
    logger.info("✅ RenewAI ready — http://localhost:8000/docs")
    yield
    # Shutdown
    logger.info("🛑 RenewAI shutting down")


app = FastAPI(
    title="🛡️ RenewAI — Suraksha Life Insurance",
    description="""
## RenewAI Multi-Agent Renewal System

**Project RenewAI** is an agentic AI system managing the full policy renewal lifecycle 
for Suraksha Life Insurance across Email, WhatsApp, and Voice channels.

### Architecture
- **Orchestrator** → selects best channel
- **Critique A** → verifies channel selection with evidence  
- **Planner** → builds channel execution plan (RAG-powered)
- **Draft Agent** → generates channel-specific message
- **Greeting/Closing Agent** → culturally appropriate wrapping
- **Critique B** → compliance & quality check
- **Channel Agents** → Email / WhatsApp / Voice (modular)
- **Escalation Manager** → human queue with SLA

### Auth
Use `/auth/login` to get a JWT token, then click **Authorize** and enter: `Bearer <token>`
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth_router)
app.include_router(renewal_router)
app.include_router(dashboard_router)

# Mount Static Files
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", tags=["Health"])
async def root():
    return {
        "service": "RenewAI",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy", "service": "RenewAI"}
