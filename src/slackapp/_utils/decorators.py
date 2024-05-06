import asyncio
import logging
from typing import Any, Callable

LOG = logging.getLogger("slackapp")


def retry(
    max_retries: int = 3, delay: float = 0.5
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Retry a function a number of times with a delay between each retry.
    Add @retry() above an async function.

    Args:
        max_retries (int): The number of times to retry the function.
        delay (float): The delay between each retry.

    Returns:
        The decorator.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            for r in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if r == max_retries - 1:
                        raise e
                    else:
                        LOG.error(
                            f"Async function {func.__name__} failed with error: {e}. Retrying..."
                        )
                        await asyncio.sleep(delay)

        return wrapper

    return decorator
