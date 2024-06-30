import asyncio
import logging
from uuid import uuid4

from slack_sdk.web.async_client import AsyncWebClient

log = logging.getLogger("slackapp")


class SlackAppError(Exception):
    """
    A custom error handler that logs the error and notifies the user with a message in Slack.
    """

    def __init__(
        self,
        message: str,
        client: AsyncWebClient | None = None,
        channel_id: str | None = None,
    ) -> None:
        super().__init__(message)
        self.client = client
        self.channel_id = channel_id
        self.error_code = str(uuid4())[:8]  # Generate a short unique error code
        self.message = message
        self._log_error_and_notify()  # Call the notify method

    async def _notify(self) -> None:
        # Notify the user if client and channel_id are provided
        if self.client and self.channel_id:
            error_message = f"""
            Apologies, I encountered an unexpected error. Our team received a note about this and is looking into it. For more details, please contact us at firedvst@gmail.com and mention error code `{self.error_code}`.
            """
            await self.client.chat_postMessage(
                channel=self.channel_id, text=error_message
            )

    def _log_error_and_notify(self) -> None:
        # Log the error
        log.error(f"Error code {self.error_code}: {self}")

        # TODO: Add a db entry and a ticket for the error

        # Since we cannot await in the __init__, ensure that notification happens asynchronously.
        if self.client and self.channel_id:
            asyncio.create_task(self._notify())
