import os
import click
import logging

from slack_bolt.adapter.socket_mode import SocketModeHandler

from slackapp.start import APP

LOG = logging.getLogger("slack-firedust")


@click.group()
def app() -> None:
    pass


@app.command()
def start() -> None:
    LOG.info("Starting the Slack app")
    SocketModeHandler(APP, os.environ["SLACK_APP_TOKEN"]).start()


@click.group(name="utils")
def utils() -> None:
    pass


app.add_command(utils)


if __name__ == "__main__":
    app()
