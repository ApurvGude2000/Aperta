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
from agents import (
    qa_orchestrator,
    orchestrator,
    ContextUnderstandingAgent,
    PrivacyGuardianAgent,
    FollowUpAgent,
    CrossPollinationAgent
)

# Import services
from services.rag_context import RAGContextManager

# Import routers
from api.routes import qa, conversations, search, auth, dashboard

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
        context_agent = ContextUnderstandingAgent()
        privacy_agent = PrivacyGuardianAgent()
        followup_agent = FollowUpAgent()
        crosspoll_agent = CrossPollinationAgent()

        logger.info("All agents initialized")
        console_logger.log_info("All 4 core agents initialized", "Startup")

        # Register agents with orchestrator (using global instance)
        orchestrator.register_agent(context_agent)
        orchestrator.register_agent(privacy_agent)
        orchestrator.register_agent(followup_agent)
        orchestrator.register_agent(crosspoll_agent)
        logger.info("Orchestrator initialized with agents")
        console_logger.log_info("Orchestrator initialized with agents", "Startup")
    except Exception as e:
        logger.warning(f"Agent initialization failed: {e}")

    # Q&A Orchestrator is already initialized globally
    try:
        logger.info("Q&A orchestrator ready")
        console_logger.log_info("Q&A orchestrator ready", "Startup")
    except Exception as e:
        logger.warning(f"Q&A orchestrator setup failed: {e}")

    # Set components in route modules
    try:
        if orchestrator and rag_manager:
            qa.set_qa_components(qa_orchestrator, orchestrator, rag_manager)
        if orchestrator:
            conversations.set_conversation_orchestrator(orchestrator)
        logger.info("Route components configured")
        console_logger.log_info("Route components configured", "Startup")
    except Exception as e:
        logger.warning(f"Route configuration failed: {e}")

    # Sync data to GCS if enabled
    if settings.use_gcs_for_chroma and settings.gcp_bucket_name:
        try:
            from utils.gcs_storage import get_gcs_storage
            import os
            gcs = get_gcs_storage()
            if gcs:
                # Auto-restore database from GCS if missing locally
                db_file = "aperta.db"
                if not os.path.exists(db_file):
                    logger.info("Database not found locally, restoring from GCS...")
                    console_logger.log_info("Restoring database from GCS backup", "Startup")
                    try:
                        from google.cloud import storage
                        bucket = gcs.bucket
                        blob = bucket.blob(f'backups/{db_file}')
                        if blob.exists():
                            blob.download_to_filename(db_file)
                            logger.info("✓ Database restored from GCS")
                            console_logger.log_info("✓ Database restored from GCS", "Startup")
                        else:
                            logger.warning("No database backup found in GCS, will create new DB")
                    except Exception as e:
                        logger.error(f"Failed to restore database from GCS: {e}")
                # Sync ChromaDB
                if os.path.exists(settings.chroma_persist_dir):
                    logger.info("Syncing ChromaDB to GCS...")
                    console_logger.log_info("Syncing ChromaDB to GCS bucket", "Startup")
                    success = gcs.sync_to_gcs(settings.chroma_persist_dir, "chroma_db/")
                    if success:
                        logger.info("✓ ChromaDB synced to GCS")
                        console_logger.log_info("✓ ChromaDB synced to GCS", "Startup")

                # Backup SQLite database
                db_file = "aperta.db"
                if os.path.exists(db_file):
                    logger.info("Backing up database to GCS...")
                    console_logger.log_info("Backing up database to GCS", "Startup")
                    success = gcs.backup_database_file(db_file, f"backups/{db_file}")
                    if success:
                        logger.info("✓ Database backed up to GCS")
                        console_logger.log_info("✓ Database backed up to GCS", "Startup")
        except Exception as e:
            logger.error(f"Error syncing to GCS: {e}")
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
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.get_cors_methods_list(),
    allow_headers=settings.get_cors_headers_list(),
)

# Include routers
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(qa.router)
app.include_router(conversations.router)
app.include_router(search.router)


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
