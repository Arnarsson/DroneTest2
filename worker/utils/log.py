import logging
import os
import sys

def get_logger(name="worker"):
    """Configure and return logger instance"""
    lvl = logging.DEBUG if os.getenv("ENV", "dev") == "dev" else logging.INFO
    fmt = "[%(asctime)s] %(levelname)s %(name)s :: %(message)s"
    logging.basicConfig(stream=sys.stdout, level=lvl, format=fmt)

    # Quiet some noisy loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    return logging.getLogger(name)