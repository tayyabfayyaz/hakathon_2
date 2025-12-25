"""Structured logging with request context for the TodoList Pro API."""
import logging
import sys
import uuid
from contextvars import ContextVar
from typing import Any

from .config import get_settings

settings = get_settings()

# Context variable for request ID
request_id_var: ContextVar[str] = ContextVar("request_id", default="")


class StructuredFormatter(logging.Formatter):
    """Custom formatter that includes request context."""

    def format(self, record: logging.LogRecord) -> str:
        # Add request ID if available
        request_id = request_id_var.get()
        if request_id:
            record.request_id = request_id
        else:
            record.request_id = "-"

        # Add extra fields if present
        extra_fields = ""
        if hasattr(record, "extra"):
            extra = getattr(record, "extra", {})
            if extra:
                extra_fields = " | " + " ".join(
                    f"{k}={v}" for k, v in extra.items()
                )

        # Format: timestamp | level | request_id | logger | message | extra
        log_format = (
            f"%(asctime)s | %(levelname)-8s | %(request_id)s | "
            f"%(name)s | %(message)s{extra_fields}"
        )

        formatter = logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


def setup_logging() -> None:
    """Configure structured logging for the application."""
    # Get root logger
    root_logger = logging.getLogger()

    # Clear existing handlers
    root_logger.handlers.clear()

    # Set log level based on environment
    log_level = logging.DEBUG if settings.environment == "development" else logging.INFO
    root_logger.setLevel(log_level)

    # Console handler with structured formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(StructuredFormatter())
    root_logger.addHandler(console_handler)

    # Suppress noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.environment == "development" else logging.WARNING
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name."""
    return logging.getLogger(name)


def set_request_id(request_id: str | None = None) -> str:
    """Set the request ID for the current context."""
    if request_id is None:
        request_id = str(uuid.uuid4())[:8]
    request_id_var.set(request_id)
    return request_id


def log_with_context(
    logger: logging.Logger,
    level: int,
    message: str,
    **kwargs: Any,
) -> None:
    """Log a message with extra context fields."""
    extra = {"extra": kwargs} if kwargs else {}
    logger.log(level, message, extra=extra)


# Initialize logging on import
setup_logging()

# Create application logger
app_logger = get_logger("todolist_pro")
