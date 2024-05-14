import logging
import time
import uuid
from typing import Any, Callable, Coroutine, Dict, TypeVar

from slack_sdk.web.async_client import AsyncWebClient

log = logging.getLogger("slackapp")


R = TypeVar("R")  # This will represent the return type of the decorated function
AsyncFunction = Callable[..., Coroutine[Any, Any, Any]]  # Type for async functions


def retry(
    max_retries: int = 3, delay: float = 0.5
) -> Callable[[Callable[..., R]], Callable[..., R]]:
    """
    A decorator to retry a function multiple times if it fails, with a delay between retries.
    """

    def decorator(func: Callable[..., R]) -> Callable[..., R]:
        def wrapper(*args: Any, **kwargs: Any) -> R:  # type: ignore
            for r in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if r == max_retries - 1:
                        raise e
                    else:
                        log.error(
                            f"Function {func.__name__} failed with error: {e}. Retrying..."
                        )
                        time.sleep(delay)

        return wrapper

    return decorator


def catch_errors() -> Callable[[AsyncFunction], AsyncFunction]:
    """
    A decorator to catch errors in slack async functions, assign a code for debugging and notify the user.
    """

    def decorator(func: AsyncFunction) -> AsyncFunction:
        async def wrapper(
            client: AsyncWebClient, event: Dict[str, Any], *args: Any, **kwargs: Any
        ) -> Any:
            try:
                return func(client, event, *args, **kwargs)
            except Exception as e:
                error_code = str(uuid.uuid4())[:8]  # Generate a short unique error code
                channel_id: str = event["channel"]
                log.error(
                    f"Error in function {func.__name__} with error code {error_code}: {e}"
                )
                error_message = f"Apologies, I encountered an unexpected issues. Please try again. Our team received a note about the error and is looking into it. For more details contact us at support@firedust.ai and mention error code `{error_code}`."
                await client.chat_postMessage(
                    channel=channel_id,
                    text=f"{error_message}",
                )
                raise e  # Re-raise the error to propagate it

        return wrapper

    return decorator
