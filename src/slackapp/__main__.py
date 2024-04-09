import time
import click
import logging

from slack_bolt.adapter.socket_mode import SocketModeHandler

from slackapp.start import APP, ASSISTANT
from slackapp._utils.logging import configure_logger

configure_logger()

LOG = logging.getLogger("slackapp")


@click.group()
def app() -> None:
    pass


@app.command()
def start() -> None:
    LOG.info("Starting the Slack app")
    SocketModeHandler(
        APP,
        ASSISTANT.config.interfaces.slack.tokens.app_token,
    ).start()


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
