import asyncio
import logging
import time

import click
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

from slackapp._utils.assistant import load_assistant
from slackapp._utils.logging import configure_logger
from slackapp.start import APP

configure_logger()

LOG = logging.getLogger("slackapp")


@click.group()
def app() -> None:
    pass


@app.command()
def start() -> None:
    LOG.info("Starting the Slack app")
    assistant = load_assistant()
    assert assistant.config.interfaces.slack is not None
    assert assistant.config.interfaces.slack.tokens is not None
    handler = AsyncSocketModeHandler(
        APP, assistant.config.interfaces.slack.tokens.app_token
    )
    loop = asyncio.get_event_loop()
    loop.run_until_complete(handler.start_async())


@app.command()
def launch() -> None:
    LOG.info("3")
    time.sleep(1)
    LOG.info("2")
    time.sleep(1)
    LOG.info("1")
    time.sleep(1)
    LOG.info("Blast off!")


@click.group(name="utils")
def utils() -> None:
    pass


app.add_command(utils)


if __name__ == "__main__":
    app()
