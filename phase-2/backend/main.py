from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from src.core.config import get_settings
from src.core.database import create_db_and_tables
from src.core.logging import setup_logging, get_logger
from src.api.v1.router import api_router
from src.api.exceptions import (
    validation_exception_handler,
    http_exception_handler,
    generic_exception_handler,
)
from src.api.middleware import RateLimitMiddleware

# Initialize logging
setup_logging()
logger = get_logger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown events."""
    # Startup
    logger.info("Starting TodoList Pro API")
    await create_db_and_tables()
    logger.info("Database tables initialized")
    yield
    # Shutdown
    logger.info("Shutting down TodoList Pro API")


app = FastAPI(
    title="TodoList Pro API",
    description="A simple and efficient todo list application API",
    version="1.0.0",
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

# Add rate limiting middleware for auth endpoints
app.add_middleware(RateLimitMiddleware)

# Register exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include API router
app.include_router(api_router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}
