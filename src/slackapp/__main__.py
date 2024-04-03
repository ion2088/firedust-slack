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


@utils.command()
def refresh_configuration_token() -> None:
    """
    The token expires after 12 hours, and has to be refreshed. To achieve this,
    we need the refresh token, which is also provided by Slack. This command
    refreshes the configuration token and updates the environment variables.
    
    See:
    - https://api.slack.com/apps
    - https://api.slack.com/authentication/token-types#config
    """
    # TODO: Set this up in a cron job, in app's dedicated container
    LOG.info("Refreshing the configuration token")
    response = APP.client.tooling_tokens_rotate(
        refresh_token=os.environ["SLACK_REFRESH_TOKEN"]
    )

    if not response.data["ok"]:
        LOG.error(f"Failed to refresh the configuration token: {response.data}")
        return

    os.environ["SLACK_CONFIGURATION_TOKEN"] = response.data["token"]
    os.environ["SLACK_REFRESH_TOKEN"] = response.data["refresh_token"]

    # TODO: Hit a starship endpoint to update config and refresh tokens


app.add_command(utils)


if __name__ == "__main__":
    app()
