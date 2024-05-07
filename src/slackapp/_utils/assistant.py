import os
from uuid import UUID

from firedust.assistant import Assistant
from firedust.utils.types.assistant import UserMessage
from slack_sdk.web.async_client import AsyncWebClient

from slackapp._utils.slack import format_slack_message


def load_assistant() -> Assistant:
    """
    Loads the assistant using the ASSISTANT_ID environment variable.

    Returns:
        Assistant: The assistant.
    """
    assistant_id = os.environ.get("ASSISTANT_ID")
    if assistant_id is None:
        raise RuntimeError("ASSISTANT_ID environment variable is not set.")

    assistant = Assistant.load(UUID(assistant_id))
    if assistant.config.interfaces.slack is None:
        raise RuntimeError("Slack interface is not configured.")

    return assistant


async def learn_message(
    client: AsyncWebClient,
    message: str,
    user_id: str,
    channel_id: str,
    timestamp: float,
) -> None:
    """
    Learns a message from a user in a channel.

    Args:
        client (AsyncWebClient): The Slack client.
        message (str): The message to learn.
        user_id (str): The user ID.
        channel_id (str): The channel ID.
        timestamp (float): The timestamp of the message.
    """
    assistant = load_assistant()
    formatted_message = await format_slack_message(
        client=client,
        message=message,
        user_id=user_id,
        channel_id=channel_id,
    )
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


async def reply_to_message(
    client: AsyncWebClient,
    message: str,
    user_id: str,
    channel_id: str,
) -> str:
    """
    Replies to a message in a channel.

    Args:
        client (AsyncWebClient): The Slack client.
        message (str): The message to reply with.
        user_id (str): The user ID.
        channel_id (str): The channel ID.

    Returns:
        str: The response message.
    """
    assistant = load_assistant()
    formatted_message = await format_slack_message(
        client=client,
        message=message,
        user_id=user_id,
        channel_id=channel_id,
    )
    response: str = assistant.chat.message(formatted_message, user_id=channel_id)
    return response
