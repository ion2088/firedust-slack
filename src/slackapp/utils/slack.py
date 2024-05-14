import asyncio
import re
from typing import Dict, List, Tuple

from firedust._private._assistant import Assistant
from firedust.utils.types.assistant import UserMessage
from slack_sdk.web.async_client import AsyncWebClient

from slackapp.utils.decorators import retry

# A quick cache implementation to store frequently requested values
_expiration_time = float
_value = str
user_name_cache: Dict[str, Tuple[_value, _expiration_time]] = {}
channel_name_cache: Dict[str, Tuple[_value, _expiration_time]] = {}


@retry()
async def get_user_name(client: AsyncWebClient, user: str) -> str:
    """
    Get the name of a user.

    Args:
        client (AsyncWebClient): The Slack client.
        user (str): The user ID of the user.

    Returns:
        str: The name of the user.
    """
    # Check if the user name is already cached and not expired
    if user in user_name_cache:
        cached_value, expiration_time = user_name_cache[user]
        if expiration_time > asyncio.get_event_loop().time():
            return cached_value

    response = await client.users_info(user=user)
    assert isinstance(response.data, dict)

    user_name: str = response.data["user"].get("real_name") or response.data["user"][
        "profile"
    ].get("real_name")

    # Set expiration time to 10 minutes from now
    expiration_time = asyncio.get_event_loop().time() + 600

    # Cache the user name with expiration time
    user_name_cache[user] = (user_name, expiration_time)

    return user_name


@retry()
async def get_channel_name(client: AsyncWebClient, channel_id: str) -> str:
    """
    Get the name of a channel.

    Args:
        client (AsyncWebClient): The Slack client.
        channel_id (str): The ID of the channel.

    Returns:
        str: The name of the channel.
    """
    # Check if the channel name is already cached and not expired
    if channel_id in channel_name_cache:
        cached_value, expiration_time = channel_name_cache[channel_id]
        if expiration_time > asyncio.get_event_loop().time():
            return cached_value

    response = await client.conversations_info(channel=channel_id)
    assert isinstance(response.data, dict)

    channel_name: str = (
        response.data["channel"]["name"] or response.data["channel"]["id"]
    )

    # Set expiration time to 10 minutes from now
    expiration_time = asyncio.get_event_loop().time() + 600

    # Cache the channel name with expiration time
    channel_name_cache[channel_id] = (channel_name, expiration_time)

    return channel_name


@retry()
async def get_bot_user_id(client: AsyncWebClient) -> str:
    """
    Get the user ID of the bot user.

    Args:
        client (AsyncWebClient): The Slack client.

    Returns:
        str: The user ID of the bot user.
    """
    response = await client.auth_test()
    assert isinstance(response.data, dict)
    user: str = response.data["user_id"]
    return user


async def learn_channel_history_on_join(
    assistant: Assistant, client: AsyncWebClient, channel_id: str
) -> None:
    """
    Learn the channel history when the bot joins a channel.

    Args:
        assistant (Assistant): The assistant.
        client (AsyncWebClient): The Slack client.
        event (Dict[str, Any]): The event data.
    """
    await client.chat_postMessage(
        channel=channel_id,
        text="I'm learning the channel history. Give me a few moments to add past conversations to my memory.",
    )

    # Learn the channel history
    # Initialize the cursor for pagination and collect all messages
    cursor = None
    all_messages = []

    while True:
        # Fetch a page of message history
        response = await client.conversations_history(channel=channel_id, cursor=cursor)
        messages: List[Dict[str, str]] = response.get("messages", [])

        # Format and collect messages
        for message in messages:
            formatted_message = await format_slack_message(
                client=client,
                message=message["text"],
                user=message["user"],
                channel_id=channel_id,
            )
            all_messages.append(
                UserMessage(
                    assistant=assistant.config.name,
                    user=message["user"],
                    message=formatted_message,
                )
            )

        # Check if there are more pages to fetch
        if not response["has_more"]:
            break

        # Get the cursor for the next page
        cursor = response["response_metadata"]["next_cursor"]

    # Save messages to the assistant's memory
    assistant.learn.chat_messages(messages=all_messages)

    # Notify channel that the assistant has learned channel history
    await client.chat_postMessage(
        channel=channel_id,
        text="Done! I'm ready to assist you.",
    )


async def format_slack_message(
    client: AsyncWebClient,
    message: str,
    channel_id: str,
    user: str,
) -> str:
    """
    Format a Slack message for the AI Assistant:
        - Replace user ids with user names
        - Include the channel name
        - Include the user name of the author

    Args:
        client (AsyncWebClient): The Slack client.
        message (str): The message to format.
        user (str): The ID of the user who sent the message.
        channel_id (str): The ID of the channel where the message was sent.

    Returns:
        str: The formatted message.
    """
    channel_name = await get_channel_name(client, channel_id)
    user_name = await get_user_name(client, user)
    message = await replace_mentions_with_user_names(client, message)
    formatted_message = f"""
    Slack channel: {channel_name}.
    From {user_name}:

    {message}
    """
    return formatted_message


@retry()
async def replace_mentions_with_user_names(client: AsyncWebClient, message: str) -> str:
    """
    Replace user mentions with user names in a message.

    Args:
        client (AsyncWebClient): The Slack client.
        message (str): The message to format.

    Returns:
        str: The formatted message.
    """
    user_ids = re.findall(r"<@([UW][A-Za-z0-9]+)>", message)
    for _id in user_ids:
        name = await get_user_name(client, _id)
        message = message.replace(f"<@{_id}>", f"@{name}")
    return message
