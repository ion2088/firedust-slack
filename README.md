# Slack AI Assistant

A straightforward implementation of a Slack app connected to a [firedust](https://github.com/ion2088/firedust) AI assistant. It supports group chats, direct messages, and learns the channel's message history when added to a group. Conversations are private within groups and with individual users. The assistant has persistent memory and recalls relevant information to respond effectively. To customize the assistant and add data to its memory, see examples [here](https://github.com/ion2088/firedust/tree/master/examples/assistant).


## Quickstart

### 0. Overview
Deploy the assistant on Slack quickly using firedust's capabilities. Follow [this](https://github.com/ion2088/firedust/blob/master/examples/assistant/deploy_on_slack.py) example for a quick setup.

To deploy the app on your server, follow the steps below:

### 1. Prerequisites
- Python 3.10+
- [Poetry](https://python-poetry.org/docs/)

### 2. Install Dependencies
```sh
poetry install
```

### 3. Create an assistant
Use [firedust](https://github.com/ion2088/firedust) to create an AI assistant and note the API key. See [this example](https://github.com/ion2088/firedust/blob/master/examples/assistant/quickstart.py).

### 4. Create a Slack App
Create a new Slack app and note the signing secret and bot token. Get [started here](https://api.slack.com/apps?new_app).

### 5. Environment Variables
Configure the following environment variables:
- `FIREDUST_API_KEY`: Your Firedust API key.
- `ASSISTANT_NAME`: The name of your AI assistant.
- `SLACK_SIGNING_SECRET`: Your Slack app's signing secret.
- `SLACK_BOT_TOKEN`: Your Slack app's bot token.

### 6. Run the App
```sh
poetry run python -m slackapp start
```

## Features

**Add To Channels:**
Invite the assistant to your channels and interact in a group by @mentioning it in messages. It learns the message history and can recall old messages if relevant. All conversations remain private to the specific channel.

**Direct Messages:**
Interact with the assistant via direct messages in Slack. These conversations are as well confidential.

**Train On Your Data:**
Enhance the assistant's memory with specialized data for more accurate responses. For examples on adding data to the assistant's memory, see here: [Firedust Examples](https://github.com/ion2088/firedust/tree/master/examples/assistant).
