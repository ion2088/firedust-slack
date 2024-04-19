import hashlib
import logging
import os
from uuid import UUID

LOG: logging.Logger = logging.getLogger("slackapp")


def configure_logger() -> None:
    LOG.setLevel(logging.DEBUG)

    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Generate hashed API key
    api_key = UUID(os.environ.get("FIREDUST_API_KEY"))
    if api_key is None:
        raise RuntimeError("FIREDUST_API_KEY environment variable is not set.")
    hashed_key = hash_api_key(api_key)

    assistant_id = os.environ.get("ASSISTANT_ID")
    if assistant_id is None:
        raise RuntimeError("ASSISTANT_ID environment variable is not set.")

    # Update the formatter of existing handlers
    formatter = logging.Formatter(
        f"{hashed_key}: {assistant_id}: Slack App: [%(asctime)s - %(name)s - %(levelname)s] - %(message)s"
    )
    console_handler.setFormatter(formatter)

    # Add the handlers to the LOG
    LOG.addHandler(console_handler)


def hash_api_key(api_key: UUID) -> str:
    hasher = hashlib.sha256()
    hasher.update(api_key.bytes)
    return hasher.hexdigest()
