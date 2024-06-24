import asyncio
import logging

import click
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

from slackapp.start import app
from slackapp.utils.assistant import load_assistant
from slackapp.utils.logging import configure_logger

configure_logger()

log = logging.getLogger("slackapp")


@click.group()
def rocket() -> None:
    pass


@rocket.command()
def start() -> None:
    async def async_start() -> None:
        log.info("Starting the Slack app")
        assistant = await load_assistant()
        assert assistant.config.interfaces.slack is not None
        assert assistant.config.interfaces.slack.tokens is not None
        handler = AsyncSocketModeHandler(
            app, assistant.config.interfaces.slack.tokens.app_token
        )
        await handler.start_async()

    asyncio.run(async_start())


if __name__ == "__main__":
    rocket()
