import logging
import os
from typing import Any, Dict

from slack_bolt.async_app import AsyncAck, AsyncApp, AsyncSay
from slack_bolt.context.async_context import AsyncBoltContext
from slack_sdk.models.views import View
from slack_sdk.web.async_client import AsyncWebClient

from slackapp.utils.assistant import learn_message, load_assistant, reply_to_message
from slackapp.utils.errors import SlackAppError
from slackapp.utils.slack import get_bot_user_id, learn_channel_history_on_join

# Initialize the Slack AsyncApp with environment variables
app = AsyncApp(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
)
log = logging.getLogger("slackapp")


@app.event("app_mention")
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
        ack: Acknowledgement method to confirm event processing - required by slack.
    """
    try:
        await ack()
        await say("...")
        reply = await reply_to_message(
            client=client,
            message=event["text"],
            user=event["user"],
            channel_id=event["channel"],
        )
        await say(reply)
    except Exception as e:
        raise SlackAppError(message=str(e), client=client, channel_id=event["channel"])


@app.event("message")
async def message(
    client: AsyncWebClient,
    event: Dict[str, Any],
    say: AsyncSay,
    ack: AsyncAck,
) -> None:
    """
    Handle incoming messages:
        - direct messages: reply to the user.
        - channel messages that dont mention the assistant: add to memory.
        - messages from the assistant: ignore, they are processed by the mention_event.
        - messages from USLACKBOT: ignore.
        - empty messages: ignore.
        - messages that contain files: ignore, the assistant cannot process them yet.

    Args:
        client: Slack WebClient instance.
        event: Event data from Slack containing message details.
        say: Method to send messages in the current channel.
        ack: Acknowledgement method to confirm event processing.
    """
    try:
        await ack()
        user = event.get("user") or event.get("message", {}).get("user")
        bot_user_id = await get_bot_user_id(client)

        message = event.get("text")
        if message is None:
            message = event.get("message", {}).get("text")

        # Ignore empty messages
        if not message:
            return

        # Ignore messages written by the assistant or USLACKBOT
        if user == bot_user_id or user == "USLACKBOT":
            return

        # Ignore messages that mention the assistant directly, they are handled by the mention_event
        if f"<@{bot_user_id}>" in message:
            return

        # Reply to direct messages
        if event.get("channel_type") == "im":
            await say("...")
            response = await reply_to_message(
                client=client,
                message=message,
                user=user,
                channel_id=event["channel"],
            )
            if event.get("files"):
                response += "\nAlso, I see that you attached some files, but I'm not able to process them yet."
            await say(response)
            return

        # All other messages add to assistant memory
        await learn_message(
            client=client,
            message=message,
            user=user,
            channel_id=event["channel"],
            timestamp=float(event["ts"]),
        )

    except Exception as e:
        raise SlackAppError(message=str(e), client=client, channel_id=event["channel"])


@app.event("app_home_opened")
async def update_home_tab(client: AsyncWebClient, event: Dict[str, Any]) -> None:
    """
    Update the home tab with helpful information.

    Args:
        client: Slack WebClient instance.
        event: Event data from Slack containing user details.
    """
    try:
        assistant = await load_assistant()
        assert assistant.config.interfaces.slack is not None  # keep mypy happy
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
        raise SlackAppError(message=str(e))


@app.command("/test")
async def hello_command(
    ack: AsyncAck,
    say: AsyncSay,
) -> None:
    """
    Respond to the /test command. Commands are WIP and will be expanded in the future.

    Args:
        ack: Acknowledgement method to confirm command processing.
        say: Method to send messages in the current channel.
        context: Additional context data, including the user's ID.
    """
    try:
        await ack()
        await say("Testing, testing, 1, 2, 3!")
    except Exception as e:
        raise SlackAppError(message=str(e))


@app.event("member_joined_channel")
async def member_join(
    client: AsyncWebClient, event: Dict[str, Any], ack: AsyncAck
) -> None:
    """
    Handle member joining a channel. If its the assistant who joined, greet the channel and learn its message history.

    Args:
        client: Slack WebClient instance.
        event: Event data from Slack containing member and channel details.
        ack: Acknowledgement method to confirm event processing.
    """
    try:
        # Acknowledge the incoming event immediately to meet Slack's requirement.
        await ack()

        # Check if the event is triggered by the assistant
        bot_id = await get_bot_user_id(client)
        is_assistant = event["user"] == bot_id

        # If the assistant joined the channel
        if is_assistant:
            # Say hello and learn the channel's message history
            assistant = await load_assistant()
            assert assistant.config.interfaces.slack is not None  # keep mypy happy
            await client.chat_postMessage(
                channel=event["channel"],
                text=assistant.config.interfaces.slack.greeting,
            )
            await learn_channel_history_on_join(
                assistant=assistant, client=client, channel_id=event["channel"]
            )
    except Exception as e:
        raise SlackAppError(message=str(e))


@app.event("channel_left")
async def channel_left(
    client: AsyncWebClient,
    event: Dict[str, Any],
    context: AsyncBoltContext,
    ack: AsyncAck,
) -> None:
    """
    Handle member leaving a channel. If it's the assistant who left, erase the chat history.

    Args:
        client: Slack WebClient instance.
        event: Event data from Slack containing channel details.
        context: Additional context data about the bot's status.
        ack: Acknowledgement method to confirm event processing.
    """

    try:
        await ack()
        bot_id = await get_bot_user_id(client)
        is_assistant = context.get("bot_user_id", None) == bot_id

        # If the assistant left the channel
        if is_assistant:
            # Erase chat history
            assistant = await load_assistant()
            await assistant.memory.erase_chat_history(user=event["channel"])
    except Exception as e:
        raise SlackAppError(message=str(e))


@app.event("channel_deleted")
async def channel_deleted(
    client: AsyncWebClient,
    event: Dict[str, Any],
    context: AsyncBoltContext,
    ack: AsyncAck,
) -> None:
    """
    Handle the deletion of a channel, deleting its chat history from memory.

    Args:
        client: Slack WebClient instance.
        event: Event data from Slack containing channel details.
        context: Additional context data about the bot's status.
        ack: Acknowledgement method to confirm event processing.
    """
    try:
        await ack()
        bot_id = await get_bot_user_id(client)
        is_assistant = context.get("bot_user_id", None) == bot_id

        # If the assistant left the channel
        if is_assistant:
            # Erase chat history
            assistant = await load_assistant()
            await assistant.memory.erase_chat_history(user=event["channel"])
    except Exception as e:
        raise SlackAppError(message=str(e))


@app.event("group_left")
async def group_left(
    client: AsyncWebClient, event: Dict[str, Any], ack: AsyncAck
) -> None:
    """
    Handle member leaving a private group. If it's the assistant who left, erase the chat history.

    Args:
        event: Event data from Slack containing group details.
        ack: Acknowledgement method to confirm event processing.
    """
    try:
        await ack()
        bot_id = await get_bot_user_id(client)
        is_assistant = event["user"] == bot_id

        if is_assistant:
            assistant = await load_assistant()
            await assistant.memory.erase_chat_history(user=event["channel"])
    except Exception as e:
        raise SlackAppError(message=str(e))


@app.event("group_deleted")
async def group_deleted(
    client: AsyncWebClient, event: Dict[str, Any], ack: AsyncAck
) -> None:
    """
    Handle the deletion of a private group.

    Args:
        event: Event data from Slack containing group details.
        ack: Acknowledgement method to confirm event processing.
    """
    try:
        await ack()
        bot_id = await get_bot_user_id(client)
        is_assistant = event["user"] == bot_id

        if is_assistant:
            assistant = await load_assistant()
            await assistant.memory.erase_chat_history(user=event["channel"])
    except Exception as e:
        raise SlackAppError(message=str(e))
