from firedust.assistant import Assistant
from slack_sdk.web.async_client import AsyncWebClient


async def get_bot_user_id(client: AsyncWebClient) -> str:
    # Retrieve bot user ID from Slack.
    response = await client.auth_test()
    assert isinstance(response.data, dict)
    user_id: str = response.data["user_id"]
    return user_id


async def get_user_real_name(client: AsyncWebClient, user_id: str) -> str:
    # Fetch real name of the user from Slack.
    response = await client.users_info(user=user_id)
    assert isinstance(response.data, dict)
    user_name: str = response.data["user"]["real_name"]
    return user_name


async def get_channel_name(client: AsyncWebClient, channel_id: str) -> str:
    # Get the name of the channel where the mention occurred.
    response = await client.conversations_info(channel=channel_id)
    assert isinstance(response.data, dict)
    channel_name: str = response.data["channel"]["name"]
    return channel_name


def assistant_message(
    assistant: Assistant, text: str, user_name: str, user_id: str, channel_name: str
) -> str:
    # Process the message and formulate the response.
    message = f"""
    Slack channel: {channel_name}.

    Message from {user_name}:

    {text}
    """
    response: str = assistant.chat.complete(message, user_id=user_id)
    return response
