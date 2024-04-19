import logging
import os
from typing import Any, Dict
from uuid import UUID

from firedust.assistant import Assistant
from slack_bolt.async_app import AsyncAck, AsyncApp, AsyncSay
from slack_bolt.context.async_context import AsyncBoltContext
from slack_sdk.models.views import View
from slack_sdk.web.async_client import AsyncWebClient

from slackapp._utils.slack import (
    assistant_message,
    get_bot_user_id,
    get_channel_name,
    get_user_real_name,
)

ASSISTANT: Assistant = Assistant.load(assistant_id=UUID(os.environ.get("ASSISTANT_ID")))
if ASSISTANT.config.interfaces.slack is None:
    raise RuntimeError(
        f"Assistant {ASSISTANT.config.name} does not have a Slack interface."
    )
if ASSISTANT.config.interfaces.slack.tokens is None:
    raise RuntimeError(
        f"Assistant {ASSISTANT.config.name} does not have Slack tokens configured."
    )
if ASSISTANT.config.interfaces.slack.credentials is None:
    raise RuntimeError(
        f"Assistant {ASSISTANT.config.name} does not have Slack credentials configured."
    )

APP = AsyncApp(
    token=ASSISTANT.config.interfaces.slack.tokens.bot_token,
    signing_secret=ASSISTANT.config.interfaces.slack.credentials.signing_secret,
)
LOG = logging.getLogger("slackapp")


@APP.event("app_home_opened")
async def update_home_tab(
    client: AsyncWebClient, event: Dict[str, Any], context: AsyncBoltContext
) -> None:
    assert ASSISTANT.config.interfaces.slack is not None
    try:
        view = View(
            type="home",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": ASSISTANT.config.interfaces.slack.description,
                    },
                },
            ],
        )
        await client.views_publish(
            user_id=event["user"],
            view=view.to_dict(),
        )
    except Exception as e:
        LOG.error(f"Error publishing home tab: {e}")


@APP.command("/test")
async def hello_command(
    ack: AsyncAck,
    say: AsyncSay,
    context: AsyncBoltContext,
) -> None:
    LOG.info("Running /test command")
    await ack()
    await say(f"Hello, <@{context.user_id}>!")


@APP.event("app_mention")
async def mention_event(
    event: Dict[str, Any],
    say: AsyncSay,
    client: AsyncWebClient,
    ack: AsyncAck,
) -> None:
    # Acknowledge the incoming event immediately to meet Slack's requirement.
    await ack()

    # Extract the user ID and text from the event.
    user_name = await get_user_real_name(client, event["user"])
    channel_name = await get_channel_name(client, event["channel"])
    bot_user_id = await get_bot_user_id(client)
    text = event["text"].replace(f"<@{bot_user_id}>", ASSISTANT.config.name).strip()
    LOG.info(
        f"Received message from {user_name} in channel {channel_name}: {text[:50]}..."
    )

    # Formulate and send a response after processing the incoming message.
    response = assistant_message(
        assistant=ASSISTANT,
        text=text,
        user_name=user_name,
        user_id=event["user"],
        channel_name=channel_name,
    )
    await say(response)


@APP.event("message")
async def message_test(event: Dict[str, Any], context: AsyncBoltContext) -> None:
    # Process the message asynchronously
    pass


@APP.event("channel_joined")
async def channel_join(event: Dict[str, Any], say: AsyncSay) -> None:
    # Process channel join events asynchronously
    pass
