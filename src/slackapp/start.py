import os
import logging

from slack_bolt import App
from slack_bolt.oauth.oauth_settings import OAuthSettings
from slack_sdk.oauth.installation_store import FileInstallationStore
from slack_sdk.oauth.state_store import FileOAuthStateStore


# oauth_settings = OAuthSettings(
#     client_id=os.environ["SLACK_CLIENT_ID"],
#     client_secret=os.environ["SLACK_CLIENT_SECRET"],
#     scopes=["chat:write", "commands"],
#     installation_store=FileInstallationStore(base_dir="./data/installations"),
#     state_store=FileOAuthStateStore(expiration_seconds=600, base_dir="./data/states"),
# )

# APP = App(
#     signing_secret=os.environ["SLACK_SIGNIN_SECRET"], oauth_settings=oauth_settings
# )
APP = App(token="xoxb-6800962808624-6929532365808-6MKUetgV4JR0hE7xcmkJuAUc")
LOG = logging.getLogger("slackapp")


@APP.event("app_home_opened")
def update_home_tab(client, event, logger):
    LOG.info("Updating home tab")
    try:
        # Call views.publish with the built-in client
        client.views_publish(
            # Use the user ID associated with the event
            user_id=event["user"],
            # Home tabs must be enabled in your app configuration
            view={
                "type": "home",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*Wilkomen home, <@" + event["user"] + "> :house:*",
                        },
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "Learn how home tabs can be more useful and interactive <https://api.slack.com/surfaces/tabs/using|*in the documentation*>.",
                        },
                    },
                ],
            },
        )
    except Exception as e:
        LOG.error(f"Error publishing home tab: {e}")


@APP.command("/hello-bolt-python")
def hello_command(ack, body):
    ack(f"Hi <@{body['user_id']}>!")


@APP.message(":wave:")
def say_hello(message, say):
    LOG.info("Saying hello")
    user = message["user"]
    say(f":wave: <@{user}>!")


@APP.message("hello")
def say_hello2(message, say):
    LOG.info("Saying hello2")
    user = message["user"]
    say(f"Hi there, <@{user}>!")
