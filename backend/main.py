# ABOUTME: FastAPI backend for NetworkingApp web interface with full agent integration.
# ABOUTME: Provides API endpoints for Q&A, conversation management, and AI analysis.

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import settings
from db.session import init_db, close_db
from utils.logger import setup_logger
import utils.console_logger as console_logger

# Import agents
from agents.intelligent_router import IntelligentRouter
from agents.orchestrator import AgentOrchestrator
from agents.perception import PerceptionAgent
from agents.context_understanding import ContextUnderstandingAgent
from agents.privacy_guardian import PrivacyGuardianAgent
from agents.strategic_networking import StrategicNetworkingAgent
from agents.follow_up import FollowUpAgent

# Import services
from services.rag_context import RAGContextManager

# Import routers
from api.routes import qa, conversations, audio

logger = setup_logger(__name__)


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting NetworkAI backend...")
    console_logger.log_section("NetworkAI Backend Startup")

    # Initialize database (with graceful fallback)
    try:
        await init_db()
        logger.info("Database initialized")
        console_logger.log_info("Database initialized", "Startup")
    except Exception as e:
        logger.warning(f"Database initialization failed: {e}")
        logger.warning("Server will run without database (audio processing still works)")
        console_logger.log_info(f"Database unavailable - running in offline mode", "Startup")
    
    # Initialize RAG context manager
    try:
        rag_manager = RAGContextManager()
        logger.info("RAG context manager initialized")
        console_logger.log_info("RAG context manager initialized", "Startup")
    except Exception as e:
        logger.warning(f"RAG context manager failed: {e}")
        rag_manager = None
    
    # Initialize agents (with graceful fallback)
    try:
        perception_agent = PerceptionAgent()
        context_agent = ContextUnderstandingAgent()
        privacy_agent = PrivacyGuardianAgent()
        strategic_agent = StrategicNetworkingAgent()
        followup_agent = FollowUpAgent()

        logger.info("All agents initialized")
        console_logger.log_info("All 5 agents initialized", "Startup")

        # Initialize orchestrator
        agents = {
            "PerceptionAgent": perception_agent,
            "ContextUnderstandingAgent": context_agent,
            "PrivacyGuardianAgent": privacy_agent,
            "StrategicNetworkingAgent": strategic_agent,
            "FollowUpAgent": followup_agent
        }

        orchestrator = AgentOrchestrator(agents)
        logger.info("Orchestrator initialized")
        console_logger.log_info("Orchestrator initialized", "Startup")
    except Exception as e:
        logger.warning(f"Agent initialization failed: {e}")
        orchestrator = None

    # Initialize intelligent router (with graceful fallback)
    try:
        router = IntelligentRouter()
        logger.info("Intelligent router initialized")
        console_logger.log_info("Intelligent router initialized", "Startup")
    except Exception as e:
        logger.warning(f"Intelligent router failed: {e}")
        router = None

    # Set components in route modules
    try:
        if router and orchestrator:
            qa.set_qa_components(router, orchestrator, rag_manager)
        if orchestrator:
            conversations.set_conversation_orchestrator(orchestrator)
        logger.info("Route components configured")
        console_logger.log_info("Route components configured", "Startup")
    except Exception as e:
        logger.warning(f"Route configuration failed: {e}")
    
    console_logger.log_section("NetworkAI Backend Ready")
    logger.info("NetworkAI backend started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down NetworkAI backend...")
    console_logger.log_section("NetworkAI Backend Shutdown")
    await close_db()
    logger.info("NetworkAI backend shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)

# Include routers
app.include_router(qa.router)
app.include_router(conversations.router)
app.include_router(audio.router)


@app.get("/")
def root():
    """Root endpoint with API information."""
    return {
        "message": f"{settings.app_name} API",
        "version": settings.app_version,
        "status": "running",
        "endpoints": {
            "qa": "/qa",
            "conversations": "/conversations",
            "docs": "/docs",
            "health": "/health"
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
