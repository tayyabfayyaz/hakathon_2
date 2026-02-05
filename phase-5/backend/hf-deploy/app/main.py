"""FastAPI application entry point."""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import init_db, close_db
from app.api.routes import tasks, health, chat, voice
from app.mcp import get_mcp_server
from app.mcp.server import get_session_factory as get_mcp_session_factory
from app.services.kafka_service import kafka_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown."""
    # Startup
    logger.info("Starting TodoList Pro API...")
    await init_db()
    logger.info("Database initialized")

    # Initialize MCP server (Official SDK)
    mcp_server = get_mcp_server()
    logger.info(f"MCP Server initialized: {mcp_server.name}")

    # Pre-initialize MCP database session factory to avoid first-request latency
    get_mcp_session_factory()
    logger.info("MCP database session factory pre-initialized")

    # Initialize Kafka service for notifications
    try:
        kafka_service.connect()
        logger.info("Kafka service initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Kafka service: {e}")

    yield

    # Shutdown
    logger.info("Shutting down TodoList Pro API...")

    # Disconnect Kafka service
    try:
        kafka_service.disconnect()
        logger.info("Kafka service disconnected")
    except Exception as e:
        logger.error(f"Error disconnecting Kafka service: {e}")

    await close_db()
    logger.info("Database connection closed")


app = FastAPI(
    title="TodoList Pro API",
    description="RESTful API for managing tasks in TodoList Pro application.",
    version=settings.api_version,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests and their response times."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s"
    )
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# Register routers
app.include_router(tasks.router)
app.include_router(health.router)
app.include_router(chat.router)  # Phase-3: AI Chat endpoints
app.include_router(voice.router)  # Voice Assistant preferences


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "TodoList Pro API",
        "version": settings.api_version,
        "docs": "/docs",
    }
