import logging
import os
import sys
from logging.handlers import RotatingFileHandler

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

def setup_logger(name: str = "renewai"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Prevent double logging
    if logger.handlers:
        return logger

    # Force format to match the requirement of "proper logger"
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

    # File Handler
    file_handler = RotatingFileHandler(
        "logs/renewai.log", maxBytes=10485760, backupCount=5
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    return logger

# Singleton-like instance
logger = setup_logger()
