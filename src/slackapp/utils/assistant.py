import os

import firedust
from firedust.types import AsyncAssistant, Message
from slack_sdk.web.async_client import AsyncWebClient

from slackapp.utils.slack import format_slack_message

"""
Note:   Firedust keeps messages private between users by default. To facilitate group conversations,
        we use the channel ID as the user ID and apply special message formatting to 
        differentiate between users in the same channel.
"""


async def load_assistant() -> AsyncAssistant:
    """
    Loads the AI assistant, using the ASSISTANT_NAME environment variable.

    Returns:
        Assistant: The assistant.
    """
    assistant_name = os.environ.get("ASSISTANT_NAME")
    if assistant_name is None:
        raise RuntimeError("ASSISTANT_NAME environment variable is not set.")

    assistant = await firedust.assistant.async_load(assistant_name)
    if assistant.config.interfaces.slack is None:
        raise RuntimeError("Slack interface is not configured.")

    return assistant


async def learn_message(
    client: AsyncWebClient,
    message: str,
    user: str,
    channel_id: str,
    timestamp: float,
) -> None:
    """
    Learns a message from a user in a channel.

    Args:
        client (AsyncWebClient): The Slack client.
        message (str): The message to learn.
        user (str): The user ID.
        channel_id (str): The channel ID.
        timestamp (float): The timestamp of the message.
    """
    assistant = await load_assistant()
    formatted_message = await format_slack_message(
        client=client,
        message=message,
        user=user,
        channel_id=channel_id,
    )
    await assistant.memory.add_chat_history(
        messages=[
            Message(
                assistant=assistant.config.name,
                user=channel_id,
                timestamp=timestamp,
                message=formatted_message,
                author="user",
            )
        ],
    )


async def reply_to_message(
    client: AsyncWebClient,
    message: str,
    user: str,
    channel_id: str,
) -> str:
    """
    Generates a reply to a message from a user in a channel.

    Args:
        client (AsyncWebClient): The Slack client.
        message (str): The message to reply with.
        user (str): The user ID.
        channel_id (str): The channel ID.

    Returns:
        str: The response message.
    """
    assistant = await load_assistant()
    formatted_message = await format_slack_message(
        client=client,
        message=message,
        user=user,
        channel_id=channel_id,
    )
    response = await assistant.chat.message(formatted_message, user=channel_id)
    reply: str = response.message
    return reply
