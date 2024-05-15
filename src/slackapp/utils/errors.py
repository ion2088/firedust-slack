import logging
from uuid import uuid4

from slack_sdk.web.async_client import AsyncWebClient

log = logging.getLogger("slackapp")


class SlackErrorNotifier(Exception):
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

    async def notify(self) -> None:
        # Log the error
        log.error(f"Error code {self.error_code}: {self}")

        # Notify the user if client and channel_id are provided
        if self.client and self.channel_id:
            error_message = f"""
            Apologies, I encountered an unexpected error. Our team received a note about this and is looking into it. For more details, please, contact us at support@firedust.io and mention error code `{self.error_code}`.
            """
            await self.client.chat_postMessage(
                channel=self.channel_id, text=error_message
            )
