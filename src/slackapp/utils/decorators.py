import asyncio
import logging
from typing import Any, Callable, Coroutine, TypeVar

log = logging.getLogger("slackapp")

R = TypeVar("R")  # This will represent the return type of the decorated function


def retry(
    max_retries: int = 3, delay: float = 0.5
) -> Callable[
    [Callable[..., Coroutine[Any, Any, R]]], Callable[..., Coroutine[Any, Any, R]]
]:
    """
    A decorator to retry an async function multiple times if it fails, with a delay between retries.
    """

    def decorator(
        func: Callable[..., Coroutine[Any, Any, R]]
    ) -> Callable[..., Coroutine[Any, Any, R]]:
        async def wrapper(*args: Any, **kwargs: Any) -> R:
            for r in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if r == max_retries - 1:
                        raise e
                    else:
                        log.error(
                            f"Function {func.__name__} failed with error: {e}. Retrying..."
                        )
                        await asyncio.sleep(delay)
            raise RuntimeError("Retry failed unexpectedly")

        return wrapper

    return decorator
