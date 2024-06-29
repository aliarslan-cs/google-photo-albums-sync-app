import logging
import sys
from logging import Logger
from typing import Optional

def setup_logger(
    *,
    log_stream: Optional[object] = sys.stderr,
    log_file: Optional[str] = None,
    log_file_mode: str = 'a',
    log_level: int = logging.INFO,
    stream_log_level: Optional[int] = None,
    file_log_level: Optional[int] = None
) -> Logger:
    # Create a logger
    _logger = logging.getLogger(__name__)
    _logger.setLevel(log_level)
    _logger.propagate = False  # Prevent the log messages from being propagated to the root logger

    # Define the log format
    log_format = '%(asctime)s | %(filename)s:%(lineno)d | %(levelname)s | %(message)s'
    formatter = logging.Formatter(log_format)

    # Clear existing handlers, if any
    if _logger.hasHandlers():
        _logger.handlers.clear()

    # Add stream handler if log_stream is not None
    if log_stream is not None:
        stream_handler = logging.StreamHandler(log_stream)
        stream_handler.setFormatter(formatter)
        # Use stream_log_level if provided, otherwise fallback to the main log_level
        stream_handler.setLevel(stream_log_level if stream_log_level is not None else log_level)
        _logger.addHandler(stream_handler)

    # Add file handler if log_file is not None
    if log_file is not None:
        file_handler = logging.FileHandler(log_file, mode=log_file_mode)
        file_handler.setFormatter(formatter)
        # Use file_log_level if provided, otherwise fallback to the main log_level
        file_handler.setLevel(file_log_level if file_log_level is not None else log_level)
        _logger.addHandler(file_handler)

    return _logger

# Example usage:
# setup_logger(log_file='app.log', log_level=logging.DEBUG, stream_log_level=logging.WARNING, file_log_level=logging.DEBUG)
# module_logger.info("This is an info message")
# module_logger.warning("This is a warning message")
# module_logger.debug("This is a debug message")
