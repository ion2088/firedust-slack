import asyncio
import logging
import time

import click
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

from slackapp._utils.assistant import load_assistant
from slackapp._utils.logging import configure_logger
from slackapp.start import app

configure_logger()

log = logging.getLogger("slackapp")


@click.group()
def rocket() -> None:
    pass


@rocket.command()
def start() -> None:
    log.info("Starting the Slack app")
    assistant = load_assistant()
    assert assistant.config.interfaces.slack is not None
    assert assistant.config.interfaces.slack.tokens is not None
    handler = AsyncSocketModeHandler(
        app, assistant.config.interfaces.slack.tokens.app_token
    )
    loop = asyncio.get_event_loop()
    loop.run_until_complete(handler.start_async())


@rocket.command()
def launch() -> None:
    log.info("3")
    time.sleep(1)
    log.info("2")
    time.sleep(1)
    log.info("1")
    time.sleep(1)
    log.info("Blast off!")
    time.sleep(1)
    log.info("Run the slack app with `poetry run python -m slackapp start`")


@click.group(name="utils")
def utils() -> None:
    pass


rocket.add_command(utils)


if __name__ == "__main__":
    rocket()
