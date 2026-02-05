import logging
import sys
from typing import Optional


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Set up a logger with the specified name and level.

    Args:
        name: Logger name
        level: Logging level (default: INFO)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(handler)

    return logger


def log_exception(logger: logging.Logger, exc: Exception, context: str = "") -> None:
    """
    Log an exception with context.

    Args:
        logger: Logger instance
        exc: Exception to log
        context: Additional context information
    """
    logger.error(f"Exception in {context}: {str(exc)}", exc_info=True)


def log_event(logger: logging.Logger, event_type: str, details: dict) -> None:
    """
    Log a system event.

    Args:
        logger: Logger instance
        event_type: Type of event
        details: Event details as dictionary
    """
    logger.info(f"Event: {event_type} - Details: {details}")