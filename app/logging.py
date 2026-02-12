"""
Centralized logging configuration for Chloé API
Provides structured logging with emojis for better visibility
"""

import logging
import sys
from typing import Optional


# Emoji mapping for different log levels and events
class LogEmoji:
    """Emojis for visual log categorization"""

    # Log levels
    DEBUG = "🔍"
    INFO = "ℹ️ "
    WARNING = "⚠️ "
    ERROR = "❌"
    CRITICAL = "🔥"

    # Application lifecycle
    STARTUP = "🚀"
    SHUTDOWN = "🛑"
    READY = "✅"

    # HTTP & API
    REQUEST = "📥"
    RESPONSE = "📤"
    SUCCESS = "✅"
    FAILED = "❌"

    # Database
    DB_CONNECT = "🔌"
    DB_QUERY = "🗄️ "
    DB_ERROR = "💥"

    # Authentication
    AUTH_SUCCESS = "🔓"
    AUTH_FAILED = "🔒"

    # Agent & AI
    AGENT_START = "🤖"
    AGENT_STEP = "⚙️ "
    AGENT_COMPLETE = "🎯"
    AI_THINKING = "💭"

    # External services
    API_CALL = "🌐"
    SCRAPING = "🕷️ "

    # Performance
    TIMER = "⏱️ "
    SLOW = "🐌"
    FAST = "⚡"

    # Data
    PROCESSING = "⚙️ "
    TRANSFORM = "🔄"
    VALIDATION = "✓"


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors and emojis"""

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m",  # Reset
    }

    EMOJI_MAP = {
        "DEBUG": LogEmoji.DEBUG,
        "INFO": LogEmoji.INFO,
        "WARNING": LogEmoji.WARNING,
        "ERROR": LogEmoji.ERROR,
        "CRITICAL": LogEmoji.CRITICAL,
    }

    def format(self, record):
        # Add emoji based on level
        emoji = self.EMOJI_MAP.get(record.levelname, "")

        # Add color in development
        if hasattr(record, "color_enabled") and record.color_enabled:
            color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
            reset = self.COLORS["RESET"]
            record.levelname = f"{color}{record.levelname}{reset}"

        # Add emoji to message
        original_msg = record.getMessage()
        record.msg = f"{emoji} {original_msg}"
        record.args = ()

        return super().format(record)


class RequestIdFilter(logging.Filter):
    """Add request ID to log records"""

    def filter(self, record):
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        return True


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    enable_colors: bool = True,
    json_format: bool = False,
) -> logging.Logger:
    """
    Setup centralized logging configuration

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for file logging
        enable_colors: Enable colored output (disable for production)
        json_format: Use JSON formatting for structured logging

    Returns:
        Configured logger instance
    """
    # Get root logger
    logger = logging.getLogger("chloe_api")
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))

    if json_format:
        # JSON formatter for production
        formatter = logging.Formatter(
            '{"time":"%(asctime)s","level":"%(levelname)s","request_id":"%(request_id)s",'
            '"module":"%(name)s","message":"%(message)s"}'
        )
    else:
        # Human-readable formatter
        formatter = ColoredFormatter(
            fmt="%(asctime)s | %(levelname)-8s | [%(request_id)s] %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    console_handler.setFormatter(formatter)
    console_handler.addFilter(RequestIdFilter())

    # Enable/disable colors
    for record_factory in logger.handlers:
        if hasattr(record_factory, "color_enabled"):
            record_factory.color_enabled = enable_colors

    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # Log everything to file
        file_formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | [%(request_id)s] %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        file_handler.addFilter(RequestIdFilter())
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a module"""
    return logging.getLogger(f"chloe_api.{name}")


# Convenience logging functions with emojis
def log_startup(logger: logging.Logger, message: str):
    """Log application startup"""
    logger.info(f"{LogEmoji.STARTUP} {message}")


def log_shutdown(logger: logging.Logger, message: str):
    """Log application shutdown"""
    logger.info(f"{LogEmoji.SHUTDOWN} {message}")


def log_ready(logger: logging.Logger, message: str):
    """Log application ready state"""
    logger.info(f"{LogEmoji.READY} {message}")


def log_request(logger: logging.Logger, method: str, path: str, request_id: str = "-"):
    """Log incoming HTTP request"""
    logger.info(f"{LogEmoji.REQUEST} {method} {path}", extra={"request_id": request_id})


def log_response(
    logger: logging.Logger, status_code: int, duration_ms: float, request_id: str = "-"
):
    """Log HTTP response"""
    emoji = LogEmoji.SUCCESS if status_code < 400 else LogEmoji.FAILED
    speed_emoji = (
        LogEmoji.FAST
        if duration_ms < 1000
        else LogEmoji.SLOW if duration_ms > 5000 else LogEmoji.TIMER
    )
    logger.info(
        f"{emoji} {speed_emoji} Status: {status_code} | Duration: {duration_ms:.2f}ms",
        extra={"request_id": request_id},
    )


def log_auth(
    logger: logging.Logger, success: bool, message: str, request_id: str = "-"
):
    """Log authentication attempt"""
    emoji = LogEmoji.AUTH_SUCCESS if success else LogEmoji.AUTH_FAILED
    level = logging.INFO if success else logging.WARNING
    logger.log(level, f"{emoji} {message}", extra={"request_id": request_id})


def log_db_operation(
    logger: logging.Logger, operation: str, success: bool = True, request_id: str = "-"
):
    """Log database operation"""
    emoji = LogEmoji.DB_QUERY if success else LogEmoji.DB_ERROR
    logger.info(f"{emoji} Database: {operation}", extra={"request_id": request_id})


def log_agent_event(
    logger: logging.Logger, event: str, message: str, request_id: str = "-"
):
    """Log agent-related events"""
    emoji_map = {
        "start": LogEmoji.AGENT_START,
        "step": LogEmoji.AGENT_STEP,
        "complete": LogEmoji.AGENT_COMPLETE,
        "thinking": LogEmoji.AI_THINKING,
    }
    emoji = emoji_map.get(event, LogEmoji.PROCESSING)
    logger.info(f"{emoji} Agent: {message}", extra={"request_id": request_id})


def log_external_call(
    logger: logging.Logger, service: str, message: str, request_id: str = "-"
):
    """Log external API/service calls"""
    emoji_map = {
        "apify": LogEmoji.SCRAPING,
        "scraping": LogEmoji.SCRAPING,
        "api": LogEmoji.API_CALL,
    }
    emoji = emoji_map.get(service.lower(), LogEmoji.API_CALL)
    logger.info(f"{emoji} {service}: {message}", extra={"request_id": request_id})


def log_performance(
    logger: logging.Logger, operation: str, duration_ms: float, request_id: str = "-"
):
    """Log performance metrics"""
    if duration_ms < 100:
        emoji = LogEmoji.FAST
        level = logging.DEBUG
    elif duration_ms < 1000:
        emoji = LogEmoji.TIMER
        level = logging.INFO
    else:
        emoji = LogEmoji.SLOW
        level = logging.WARNING

    logger.log(
        level,
        f"{emoji} Performance: {operation} took {duration_ms:.2f}ms",
        extra={"request_id": request_id},
    )


def log_validation(
    logger: logging.Logger, success: bool, message: str, request_id: str = "-"
):
    """Log validation results"""
    emoji = LogEmoji.VALIDATION if success else LogEmoji.ERROR
    level = logging.INFO if success else logging.WARNING
    logger.log(
        level, f"{emoji} Validation: {message}", extra={"request_id": request_id}
    )


# Configure default logger on module import
default_logger = setup_logging(level="INFO", enable_colors=True, json_format=False)
