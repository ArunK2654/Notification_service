import inspect
import logging
import time
from collections.abc import Callable
from functools import wraps
from typing import Any

from notification_service.core.exceptions import ApplicationError

logger = logging.getLogger("notification_service")

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)


def log_execution(func: Callable[..., Any]) -> Callable[..., Any]:
    if inspect.iscoroutinefunction(func):

        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            logger.info("%s started", func.__name__)
            start = time.perf_counter()

            try:
                result = await func(*args, **kwargs)

            except ApplicationError as exc:
                logger.warning("%s failed: %s", func.__name__, exc)
                raise

            else:
                end = time.perf_counter()
                logger.info("%s finished in %.4f seconds", func.__name__, end - start)
                return result

        return async_wrapper

    @wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        logger.info("%s started", func.__name__)
        start = time.perf_counter()

        try:
            result = func(*args, **kwargs)

        except ApplicationError as exc:
            logger.warning("%s failed: %s", func.__name__, exc)
            raise

        else:
            end = time.perf_counter()
            logger.info("%s finished in %.4f seconds", func.__name__, end - start)
            return result

    return sync_wrapper
