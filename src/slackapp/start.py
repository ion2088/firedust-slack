import logging
import os
from typing import Any, Dict

from firedust.utils.types.assistant import UserMessage
from slack_bolt.async_app import AsyncAck, AsyncApp, AsyncSay
from slack_bolt.context.async_context import AsyncBoltContext
from slack_sdk.errors import SlackApiError
from slack_sdk.models.views import View
from slack_sdk.web.async_client import AsyncWebClient

from slackapp._utils.assistant import load_assistant
from slackapp._utils.slack import (
    format_slack_message,
    get_bot_user_id,
    learn_channel_history_on_join,
)

APP = AsyncApp(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
)
LOG = logging.getLogger("slackapp")


@APP.event("app_home_opened")
async def update_home_tab(client: AsyncWebClient, event: Dict[str, Any]) -> None:
    assistant = load_assistant()
    assert assistant.config.interfaces.slack is not None  # make mypy happy
    try:
        view = View(
            type="home",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": assistant.config.interfaces.slack.description,
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
    await ack()

    assistant = load_assistant()
    formatted_message = await format_slack_message(
        client=client,
        message=event["text"],
        user_id=event["user"],
        channel_id=event["channel"],
    )
    response = assistant.chat.message(formatted_message, user_id=event["channel"])

    await say(response)


@APP.event("message")
async def message(
    client: AsyncWebClient, event: Dict[str, Any], context: AsyncBoltContext
) -> None:
    # Ignore messages written by the assistant or USLACKBOT
    assistant_bot_id = await client.auth_test()
    event_user_id = event.get("user") or event["message"].get("user")
    if event["user"] == assistant_bot_id or event["user"] == "USLACKBOT":
        return

    # Ignore messages that mention the assistant, these are handled by the app_mention event
    if f"<@{assistant_bot_id}>" in event["text"]:
        return

    LOG.info(f"\n\n Received message. Event: {event} \n\n Context: {context} \n\n")

    # Format the message and add it to the assistant's memory
    message = event.get("text") or event["message"].get("text")
    channel_id = str(event.get("channel"))
    timestamp = event.get("ts")
    formatted_message = await format_slack_message(
        client=client,
        message=message,
        user_id=event_user_id,
        channel_id=channel_id,
    )
    assistant = load_assistant()
    assistant.learn.chat_messages(
        messages=[
            UserMessage(
                assistant_id=assistant.config.id,
                user_id=channel_id,
                timestamp=timestamp,
                message=formatted_message,
            )
        ],
    )


@APP.event("member_joined_channel")
async def member_join(
    client: AsyncWebClient, event: Dict[str, Any], ack: AsyncAck
) -> None:
    # Acknowledge the incoming event immediately to meet Slack's requirement.
    await ack()

    # Check if the event is triggered by the assistant
    bot_id = await get_bot_user_id(client)
    is_assistant = event["user"] == bot_id

    # If assistant joined channel
    if is_assistant:
        LOG.info(f"Assistant joined channel {event}.")
        # Say hello and learn channel history
        assistant = load_assistant()
        await client.chat_postMessage(
            channel=event["channel"],
            text=f"Hello! I'm {assistant.config.name}, a helpful AI assistant. To interact with me, just mention my name or send me a direct message.",
        )
        try:
            await learn_channel_history_on_join(
                assistant=assistant, client=client, channel_id=event["channel"]
            )
        except SlackApiError as e:
            LOG.error(f"Error learning channel history: {e}")
            raise e


@APP.event("member_left_channel")
async def member_left(event: Dict[str, Any], say: AsyncSay) -> None:
    # Process member left events asynchronously
    LOG.info(f"\n\n Member channel left event: {event} \n\n")


@APP.event("channel_left")
async def channel_left(
    client: AsyncWebClient,
    event: Dict[str, Any],
    context: AsyncBoltContext,
    ack: AsyncAck,
) -> None:
    # Acknowledge the incoming event immediately to meet Slack's requirement.
    await ack()

    bot_id = await get_bot_user_id(client)
    is_assistant = context.get("bot_user_id", None) == bot_id

    # If assistant left channel
    if is_assistant:
        # Erase chat history
        assistant = load_assistant()
        assistant.memory.erase_chat_history(user_id=event["channel"])

    LOG.info(f"Assistant left channel {event}")


@APP.event("channel_deleted")
async def channel_deleted(
    client: AsyncWebClient, event: Dict[str, Any], ack: AsyncAck
) -> None:
    # Acknowledge the incoming event immediately to meet Slack's requirement.
    await ack()

    # Forget channel history
    assistant = load_assistant()
    assistant.memory.erase_chat_history(user_id=event["channel"])


@APP.event("group_left")
async def group_left(
    client: AsyncWebClient, event: Dict[str, Any], ack: AsyncAck
) -> None:
    # Acknowledge the incoming event immediately to meet Slack's requirement.
    await ack()

    # Forget channel history
    assistant = load_assistant()
    assistant.memory.erase_chat_history(user_id=event["channel"])


@APP.event("group_deleted")
async def group_deleted(
    client: AsyncWebClient, event: Dict[str, Any], ack: AsyncAck
) -> None:
    # Acknowledge the incoming event immediately to meet Slack's requirement.
    await ack()

    # Forget channel history
    assistant = load_assistant()
    assistant.memory.erase_chat_history(user_id=event["channel"])


@APP.event("app_uninstalled")
async def app_uninstalled(
    client: AsyncWebClient, event: Dict[str, Any], ack: AsyncAck
) -> None:
    # Forget history from all channels that the bot was a part of
    channels = await client.conversations_list(types="public_channel,private_channel")

    assistant = load_assistant()
    for channel in channels["channels"]:
        # Forget channel history
        assistant.memory.erase_chat_history(user_id=channel["id"])
