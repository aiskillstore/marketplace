"""
Production logging configuration for Python applications.

Usage:
    from logging_config import configure_logging
    configure_logging()
"""

import logging
import sys
from typing import Literal

import structlog


def configure_logging(
    log_level: str = "INFO",
    format: Literal["json", "console"] = "json",
    service_name: str = "app",
):
    """
    Configure structured logging for production.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        format: Output format - 'json' for production, 'console' for development
        service_name: Service name to include in logs
    """

    # Timestamper
    timestamper = structlog.processors.TimeStamper(fmt="iso")

    # Shared processors for structlog and stdlib
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        timestamper,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    # Add service name
    def add_service_name(_, __, event_dict):
        event_dict["service"] = service_name
        return event_dict

    shared_processors.insert(0, add_service_name)

    # Choose renderer based on format
    if format == "json":
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(
            colors=True,
            exception_formatter=structlog.dev.plain_traceback,
        )

    # Configure structlog
    structlog.configure(
        processors=shared_processors + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure stdlib logging
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.handlers = []
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)

    # Quiet noisy libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str = None):
    """Get a structlog logger."""
    return structlog.get_logger(name)


# Example usage
if __name__ == "__main__":
    # Development
    configure_logging(log_level="DEBUG", format="console", service_name="demo")

    logger = get_logger("example")

    logger.info("application_started", version="1.0.0")
    logger.debug("debug_message", data={"key": "value"})
    logger.warning("rate_limit_approaching", current=95, limit=100)

    try:
        raise ValueError("Something went wrong")
    except Exception:
        logger.exception("operation_failed")
