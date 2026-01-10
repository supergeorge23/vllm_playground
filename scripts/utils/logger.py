#!/usr/bin/env python3
"""
Unified logging configuration for RAG prefill-decode asymmetry study.

Provides structured logging that outputs to both console and file,
suitable for cloud execution and remote monitoring.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


def setup_logger(
    name: str,
    log_dir: Optional[Path] = None,
    log_file: Optional[str] = None,
    level: int = logging.INFO,
    console: bool = True,
) -> logging.Logger:
    """
    Setup a logger with both file and console handlers.
    
    Args:
        name: Logger name (typically __name__)
        log_dir: Directory for log files (default: ./logs)
        log_file: Log file name (default: auto-generated from name and timestamp)
        level: Logging level (default: INFO)
        console: Whether to output to console (default: True)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Clear any existing handlers
    logger.handlers = []
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        fmt='%(levelname)-8s | %(message)s'
    )
    
    # File handler
    if log_dir is None:
        log_dir = Path("logs")
    
    log_dir.mkdir(parents=True, exist_ok=True)
    
    if log_file is None:
        # Generate log file name: <name>_<timestamp>.log
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"{name.split('.')[-1]}_{timestamp}.log"
    
    log_path = log_dir / log_file
    
    file_handler = logging.FileHandler(log_path, mode='a', encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)
    
    # Console handler (simpler format)
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(simple_formatter)
        logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get an existing logger or create a new one with default settings.
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    
    # If logger already has handlers, return it
    if logger.handlers:
        return logger
    
    # Otherwise, setup with defaults
    return setup_logger(name)


def log_separator(logger: logging.Logger, char: str = "=", width: int = 60):
    """Log a separator line."""
    logger.info(char * width)


def log_header(logger: logging.Logger, title: str, char: str = "=", width: int = 60):
    """Log a header with title and separator."""
    logger.info(char * width)
    logger.info(title)
    logger.info(char * width)


def log_subheader(logger: logging.Logger, title: str, char: str = "-", width: int = 60):
    """Log a subheader."""
    logger.info(char * width)
    logger.info(title)
    logger.info(char * width)
