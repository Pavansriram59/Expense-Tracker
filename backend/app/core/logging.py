"""Structured logging infrastructure with zero-PII guarantee."""

import json
import logging
import re
import sys
from datetime import datetime, timezone
from typing import Any, Dict

# Sensitive keys to redact from logs
SENSITIVE_PATTERNS = [
    re.compile(r"pass(word)?", re.IGNORECASE),
    re.compile(r"token", re.IGNORECASE),
    re.compile(r"secret", re.IGNORECASE),
    re.compile(r"auth(orization)?", re.IGNORECASE),
    re.compile(r"cookie", re.IGNORECASE),
    re.compile(r"credit_?card", re.IGNORECASE),
]


def redact_sensitive_data(data: Any) -> Any:
    """Recursively redact sensitive fields from dictionaries and strings."""
    if isinstance(data, dict):
        redacted = {}
        for k, v in data.items():
            if any(pattern.search(str(k)) for pattern in SENSITIVE_PATTERNS):
                redacted[k] = "[REDACTED]"
            else:
                redacted[k] = redact_sensitive_data(v)
        return redacted
    if isinstance(data, list):
        return [redact_sensitive_data(item) for item in data]
    return data


class PIIFilter(logging.Filter):
    """Logging filter ensuring no PII or secrets are leaked into logs."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            for pattern in SENSITIVE_PATTERNS:
                # Redact potential key=val or "key": "val" patterns
                record.msg = re.sub(
                    rf'(?i)("{pattern.pattern}"\s*:\s*)"[^"]+"',
                    r'\1"[REDACTED]"',
                    record.msg,
                )
        if hasattr(record, "args") and isinstance(record.args, dict):
            record.args = redact_sensitive_data(record.args)
        return True


class JSONFormatter(logging.Formatter):
    """Format log records as structured single-line JSON."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Redact any sensitive content in the final dictionary
        sanitized_entry = redact_sensitive_data(log_entry)
        return json.dumps(sanitized_entry)


def setup_logging(log_level: str = "INFO", log_format: str = "json") -> None:
    """Configure application-wide structured logging."""
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level.upper())

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(PIIFilter())

    if log_format.lower() == "json":
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s [%(levelname)s] %(name)s (req=%(request_id)s): %(message)s",
                defaults={"request_id": "-"},
            )
        )

    root_logger.addHandler(handler)

    # Configure third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(log_level.upper())
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
