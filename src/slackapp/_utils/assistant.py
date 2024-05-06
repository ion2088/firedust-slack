import os
from uuid import UUID

from firedust.assistant import Assistant


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
