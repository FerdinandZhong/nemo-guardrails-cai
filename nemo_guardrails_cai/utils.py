"""Utility functions for NeMo Guardrails CAI integration."""

import logging
import time
from typing import Callable, TypeVar, Any
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
) -> Callable:
    """Decorator for retrying functions with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        backoff_factor: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch

    Returns:
        Decorated function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            delay = initial_delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}: {e}. "
                            f"Retrying in {delay}s..."
                        )
                        time.sleep(delay)
                        delay *= backoff_factor
                    else:
                        logger.error(
                            f"All {max_retries} retry attempts failed for {func.__name__}"
                        )

            raise last_exception

        return wrapper
    return decorator


def validate_config_path(config_path: str) -> bool:
    """Validate that a guardrails configuration path exists and has required files.

    Args:
        config_path: Path to guardrails configuration directory

    Returns:
        True if valid, False otherwise
    """
    from pathlib import Path

    path = Path(config_path)

    if not path.exists():
        logger.error(f"Config path does not exist: {config_path}")
        return False

    if not path.is_dir():
        logger.error(f"Config path is not a directory: {config_path}")
        return False

    # Check for required files
    required_files = ["config.yml"]
    for file in required_files:
        if not (path / file).exists():
            logger.warning(f"Required file not found: {file}")

    return True


def setup_logging(log_level: str = "INFO", log_file: str = None) -> None:
    """Setup logging configuration.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional path to log file
    """
    handlers = [logging.StreamHandler()]

    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers
    )

    logger.info(f"Logging configured at {log_level} level")
