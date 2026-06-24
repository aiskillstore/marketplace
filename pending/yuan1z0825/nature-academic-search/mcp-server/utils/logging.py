"""Structured logging for academic search operations."""

import json
import logging
import sys
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "tool": getattr(record, "tool", None),
            "query": getattr(record, "query", None),
            "sources": getattr(record, "sources", None),
            "duration_ms": getattr(record, "duration_ms", None),
            "results_count": getattr(record, "results_count", None),
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps({k: v for k, v in log_data.items() if v is not None})


def setup_logging(level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger("academic-search")
    logger.setLevel(getattr(logging, level.upper()))
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)
    return logger
