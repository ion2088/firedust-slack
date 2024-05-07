"""
AI Slack Assistant

This code implements a Slack application to interacat with an AI assistant. Created with Firedust and Slack Bolt SDK for Python. 
The assistant listens for various Slack events and commands to interact with users, 
provide automated responses, and maintains memory of past interactions.

Quickstart:
1. Create an AI assistant with Firedust: https://firedust.ai/quickstarts
2. Set the environment variables 
    - `FIREDUST_API_KEY`: The API key for the Firedust API. See: https://firedust.ai
    - `ASSISTANT_ID`: The ID of the AI assistant created with Firedust. See: https://firedust.ai/quickstarts
    - `SLACK_SIGNING_SECRET`: The signing secret for the Slack app. See: https://api.slack.com/apps
    - `SLACK_BOT_TOKEN`: The bot token for the Slack app. See: https://api.slack.com/apps
3. Run the app `poetry run python -m slackapp start`

Events Handled:
- Mention events: Responds to mentions with the bot's name.
- Message events: Replies to direct messages and learns from messages posted in channels where the assistant is present.
- Member join/leave: When the assistant joins a channel, it learns the channel history. When it leaves, the history is erased.
"""

import logging
import os
from typing import Any, Dict

from slack_bolt.async_app import AsyncAck, AsyncApp, AsyncSay
from slack_bolt.context.async_context import AsyncBoltContext
from slack_sdk.errors import SlackApiError
from slack_sdk.models.views import View
from slack_sdk.web.async_client import AsyncWebClient

from slackapp._utils.assistant import learn_message, load_assistant, reply_to_message
from slackapp._utils.decorators import catch_errors
from slackapp._utils.slack import get_bot_user_id, learn_channel_history_on_join

# Initialize the Slack AsyncApp with environment variables
app = AsyncApp(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
)
log = logging.getLogger("slackapp")


@app.event("app_mention")
@catch_errors()
async def mention_event(
    client: AsyncWebClient,
    event: Dict[str, Any],
    say: AsyncSay,
    ack: AsyncAck,
) -> None:
    """
    Handle @mentions of the bot.

    Args:
        event: Event data from Slack containing message details.
        say: Method to send messages in the current channel.
        client: Slack WebClient instance.
        ack: Acknowledgement method to confirm event processing.
    """
    # Acknowledge the incoming event immediately to meet Slack's requirement.
    await ack()

    await say("...")
    response = await reply_to_message(
        client=client,
        message=event["text"],
        user_id=event["user"],
        channel_id=event["channel"],
    )
    await say(response)


@app.event("message")
@catch_errors()
async def message(
    client: AsyncWebClient,
    event: Dict[str, Any],
    say: AsyncSay,
    ack: AsyncAck,
) -> None:
    """
    Handle incoming messages.
    If the message is a direct message, reply to the user.
    If the message is in a channel and doesn't mention the assistant, add it to memory.

    Args:
        client: Slack WebClient instance.
        event: Event data from Slack containing message details.
        say: Method to send messages in the current channel.
    """
    # Acknowledge the incoming event immediately to meet Slack's requirement.
    await ack()

    user_id = event.get("user") or event["message"].get("user")
    bot_user_id = await get_bot_user_id(client)
    message = event.get("text") or event["message"].get("text")

    # Ignore messages written by the assistant or USLACKBOT
    if user_id == bot_user_id or user_id == "USLACKBOT":
        return

    # Ignore messages that mention the assistant directly, they are handled by the mention_event
    if f"<@{bot_user_id}>" in message:
        return

    # On direct messages, reply to the user
    if event.get("channel_type") == "im":
        await say("...")
        response = await reply_to_message(
            client=client,
            message=message,
            user_id=user_id,
            channel_id=event["channel"],
        )
        await say(response)
        return

    # For all other messages, add to assistant memory
    await learn_message(
        client=client,
        message=message,
        user_id=user_id,
        channel_id=event["channel"],
        timestamp=float(event["ts"]),
    )


@app.event("app_home_opened")
async def update_home_tab(client: AsyncWebClient, event: Dict[str, Any]) -> None:
    """
    Update the home tab with helpful information.

    Args:
        client: Slack WebClient instance.
        event: Event data from Slack containing user details.
    """
    assistant = load_assistant()
    assert assistant.config.interfaces.slack is not None  # keep mypy happy
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
        log.error(f"Error publishing home tab: {e}")


@app.command("/test")
async def hello_command(
    ack: AsyncAck,
    say: AsyncSay,
) -> None:
    """
    Respond to the /test command.

    Args:
        ack: Acknowledgement method to confirm command processing.
        say: Method to send messages in the current channel.
        context: Additional context data, including the user's ID.
    """
    log.info("Running /test command")
    await ack()
    await say("Testing, testing, 1, 2, 3!")


@app.event("member_joined_channel")
@catch_errors()
async def member_join(
    client: AsyncWebClient, event: Dict[str, Any], ack: AsyncAck
) -> None:
    """
    Handle member joining a channel.

    Args:
        client: Slack WebClient instance.
        event: Event data from Slack containing member and channel details.
        ack: Acknowledgement method to confirm event processing.
    """
    # Acknowledge the incoming event immediately to meet Slack's requirement.
    await ack()

    # Check if the event is triggered by the assistant
    bot_id = await get_bot_user_id(client)
    is_assistant = event["user"] == bot_id

    # If the assistant joined the channel
    if is_assistant:
        # Say hello and learn the channel's message history
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
            log.error(f"Error learning channel history: {e}")
            raise e


@app.event("channel_left")
async def channel_left(
    client: AsyncWebClient,
    event: Dict[str, Any],
    context: AsyncBoltContext,
    ack: AsyncAck,
) -> None:
    """
    Handle the bot leaving a channel.

    Args:
        client: Slack WebClient instance.
        event: Event data from Slack containing channel details.
        context: Additional context data about the bot's status.
        ack: Acknowledgement method to confirm event processing.
    """
    await ack()

    bot_id = await get_bot_user_id(client)
    is_assistant = context.get("bot_user_id", None) == bot_id

    # If the assistant left the channel
    if is_assistant:
        # Erase chat history
        assistant = load_assistant()
        assistant.memory.erase_chat_history(user_id=event["channel"])


@app.event("channel_deleted")
async def channel_deleted(event: Dict[str, Any], ack: AsyncAck) -> None:
    """
    Handle the deletion of a channel.

    Args:
        event: Event data from Slack containing channel details.
        ack: Acknowledgement method to confirm event processing.
    """
    await ack()

    # Forget channel history
    assistant = load_assistant()
    assistant.memory.erase_chat_history(user_id=event["channel"])


@app.event("group_left")
async def group_left(event: Dict[str, Any], ack: AsyncAck) -> None:
    """
    Handle the bot leaving a private group.

    Args:
        event: Event data from Slack containing group details.
        ack: Acknowledgement method to confirm event processing.
    """
    await ack()

    # Forget group history
    assistant = load_assistant()
    assistant.memory.erase_chat_history(user_id=event["channel"])


@app.event("group_deleted")
async def group_deleted(event: Dict[str, Any], ack: AsyncAck) -> None:
    """
    Handle the deletion of a private group.

    Args:
        event: Event data from Slack containing group details.
        ack: Acknowledgement method to confirm event processing.
    """
    await ack()

    # Forget group history
    assistant = load_assistant()
    assistant.memory.erase_chat_history(user_id=event["channel"])


@app.event("app_uninstalled")
async def app_uninstalled(client: AsyncWebClient, ack: AsyncAck) -> None:
    """
    Handle the uninstallation of the app.

    Args:
        client: Slack WebClient instance.
    """
    await ack()

    # Forget history from all channels that the bot was a part of
    channels = await client.conversations_list(types="public_channel,private_channel")

    assistant = load_assistant()
    for channel in channels["channels"]:
        # Forget channel history
        assistant.memory.erase_chat_history(user_id=channel["id"])
