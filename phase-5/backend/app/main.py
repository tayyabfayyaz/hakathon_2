"""FastAPI application entry point."""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import init_db, close_db
from app.api.routes import tasks, health, chat, notifications, websocket
from app.mcp import get_mcp_server
from app.services.kafka_producer import start_producer, stop_producer
from app.services.notification_consumer import start_consumer, stop_consumer
from app.services.deadline_scheduler import start_scheduler, stop_scheduler

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

    # Initialize Kafka producer (only if enabled)
    if settings.kafka_enabled:
        kafka_producer = await start_producer()
        if kafka_producer.is_ready:
            logger.info("Kafka producer initialized and ready")
        else:
            logger.warning("Kafka producer failed to connect")

        # Start notification consumer
        notification_consumer = await start_consumer()
        if notification_consumer.is_ready:
            logger.info("Notification consumer initialized and ready")
        else:
            logger.warning("Notification consumer failed to start")
    else:
        logger.info("Kafka is disabled (KAFKA_ENABLED=false)")

    # Start deadline scheduler (always runs, independent of Kafka)
    deadline_scheduler = await start_scheduler()
    logger.info("Deadline scheduler started")

    yield

    # Shutdown
    logger.info("Shutting down TodoList Pro API...")
    await stop_scheduler()
    logger.info("Deadline scheduler stopped")
    await stop_consumer()
    logger.info("Notification consumer stopped")
    await stop_producer()
    logger.info("Kafka producer stopped")
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
app.include_router(notifications.router)  # Phase-7: Notification endpoints
app.include_router(websocket.router)  # Phase-7: WebSocket for real-time notifications


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "TodoList Pro API",
        "version": settings.api_version,
        "docs": "/docs",
    }
