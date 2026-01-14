"""
Structured logging configuration for CalibreMCP.

Implements the monitoring standards from central docs:
- JSON-formatted logs for easy parsing
- Correlation IDs for request tracing
- Consistent field names across services
- All significant operations and errors logged
"""

import json
import logging
import logging.config
import uuid
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


def _is_mcp_server() -> bool:
    """Check if we're running as an MCP server (stdio transport)."""
    # MCP servers use stdio, so stdout must be clean
    # Check if stdin is being used (indicating stdio transport)
    return hasattr(sys.stdin, "isatty") and not sys.stdin.isatty()


class CorrelationIDFilter(logging.Filter):
    """Add correlation ID to log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        # Generate correlation ID if not present
        if not hasattr(record, "correlation_id"):
            record.correlation_id = str(uuid.uuid4())[:8]
        return True


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        # Extract structured data from record
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": getattr(record, "correlation_id", "unknown"),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add extra fields if present
        if hasattr(record, "operation"):
            log_data["operation"] = record.operation
        if hasattr(record, "book_id"):
            log_data["book_id"] = record.book_id
        if hasattr(record, "library_name"):
            log_data["library_name"] = record.library_name
        if hasattr(record, "duration"):
            log_data["duration"] = record.duration
        if hasattr(record, "status"):
            log_data["status"] = record.status
        if hasattr(record, "error_code"):
            log_data["error_code"] = record.error_code

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info),
            }

        return json.dumps(log_data, ensure_ascii=False)


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    enable_console: Optional[bool] = None,
) -> None:
    """
    Setup structured logging configuration.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for log output
        enable_console: Whether to enable console output.
                      If None, auto-detects (disabled for MCP servers, enabled otherwise)
    """
    # Auto-detect MCP server mode and disable console logging
    if enable_console is None:
        enable_console = not _is_mcp_server()

    # CRITICAL: For MCP servers, console logging must be EXPLICITLY disabled
    # to prevent any output from breaking the JSON-RPC stdio stream.
    if _is_mcp_server():
        enable_console = False

    # Create logs directory if it doesn't exist
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)

    # Configure handlers
    handlers = {}

    # For MCP servers: stderr logging is OK (stdout reserved for JSON-RPC protocol)
    # MCP spec allows stderr for logging/debugging, stdout must be clean for JSON-RPC
    if enable_console:
        handlers["console"] = {
            "class": "logging.StreamHandler",
            "level": level,
            "formatter": "structured",
            "stream": "ext://sys.stderr",  # stderr is safe for MCP servers
            "filters": ["correlation_id"],
        }

    if log_file:
        handlers["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": level,
            "formatter": "structured",
            "filename": str(log_file),
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "filters": ["correlation_id"],
        }

    # Configure logging
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "correlation_id": {
                "()": CorrelationIDFilter,
            }
        },
        "formatters": {
            "structured": {
                "()": StructuredFormatter,
            }
        },
        "handlers": handlers,
        "loggers": {
            "calibremcp": {
                "level": level,
                "handlers": list(handlers.keys()),
                "propagate": False,
            },
            "calibre_mcp": {
                "level": level,
                "handlers": list(handlers.keys()),
                "propagate": False,
            },
        },
        "root": {"level": level, "handlers": list(handlers.keys())},
    }

    logging.config.dictConfig(logging_config)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with structured logging capabilities."""
    return logging.getLogger(name)


def log_operation(
    logger: logging.Logger, operation: str, level: str = "INFO", **kwargs: Any
) -> None:
    """
    Log an operation with structured data.

    Args:
        logger: Logger instance
        operation: Operation name
        level: Log level
        **kwargs: Additional structured data
    """
    extra = {"operation": operation, **kwargs}

    if level.upper() == "DEBUG":
        logger.debug(f"Operation: {operation}", extra=extra)
    elif level.upper() == "INFO":
        logger.info(f"Operation: {operation}", extra=extra)
    elif level.upper() == "WARNING":
        logger.warning(f"Operation: {operation}", extra=extra)
    elif level.upper() == "ERROR":
        logger.error(f"Operation: {operation}", extra=extra)
    elif level.upper() == "CRITICAL":
        logger.critical(f"Operation: {operation}", extra=extra)


def log_api_call(
    logger: logging.Logger,
    operation: str,
    book_id: Optional[str] = None,
    library_name: Optional[str] = None,
    duration: Optional[float] = None,
    status: Optional[str] = None,
    error_code: Optional[str] = None,
    **kwargs: Any,
) -> None:
    """
    Log an API call with structured data.

    Args:
        logger: Logger instance
        operation: API operation name
        book_id: Book ID if applicable
        library_name: Library name if applicable
        duration: Request duration in seconds
        status: Request status (success, error, etc.)
        error_code: Error code if applicable
        **kwargs: Additional structured data
    """
    extra = {
        "operation": operation,
        "book_id": book_id,
        "library_name": library_name,
        "duration": duration,
        "status": status,
        "error_code": error_code,
        **kwargs,
    }

    level = "ERROR" if status == "error" else "INFO"
    logger.log(getattr(logging, level.upper()), f"API call: {operation}", extra=extra)


def log_error(
    logger: logging.Logger,
    operation: str,
    error: Exception,
    book_id: Optional[str] = None,
    library_name: Optional[str] = None,
    **kwargs: Any,
) -> None:
    """
    Log an error with structured data.

    Args:
        logger: Logger instance
        operation: Operation that failed
        error: Exception that occurred
        book_id: Book ID if applicable
        library_name: Library name if applicable
        **kwargs: Additional structured data
    """
    extra = {
        "operation": operation,
        "book_id": book_id,
        "library_name": library_name,
        "status": "error",
        "error_code": type(error).__name__,
        **kwargs,
    }

    logger.error(f"Error in {operation}: {str(error)}", exc_info=True, extra=extra)


# Initialize structured logging on import
def initialize_logging() -> None:
    """Initialize structured logging with default configuration."""
    # Auto-disable console for MCP servers (stdio transport)
    setup_logging(
        level="INFO",
        log_file=Path("logs/calibremcp.log"),
        enable_console=None,  # Auto-detect based on MCP server mode
    )


# Auto-initialize if not already configured
if not logging.getLogger().handlers:
    initialize_logging()
