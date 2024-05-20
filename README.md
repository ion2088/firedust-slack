# AI Slack Assistant

A simple implementation of a Slack app connected to an AI assistant, created with [firedust](https://github.com/ion2088/firedust). It handles group chats, direct messages and learns the channel message history when added to a group. The conversations are kept private within individual groups and with specific users. The assistant has a persistent memory and recalls relevant information to respond to users. To customize the assistant and add your data to its memory see examples [here](https://github.com/ion2088/firedust/blob/master/examples/deploy_to_slack.py).


## Quickstart

### 0. End Game
The quickest way to deploy the assistant on Slack is to use [firedust](https://github.com/ion2088/firedust) interface deploy capabilities. You can set it up and running in a few minutes by following this [example](https://firedust.ai/quickstarts).

To deploy the app on your server, follow the steps below.

### 1. Prerequisites
- Python 3.10+
- [Poetry](https://python-poetry.org/docs/)

### 2. Install Dependencies
```sh
poetry install
```

### 3. Create an assistant
Create an AI assistant using [firedust](https://github.com/ion2088/firedust) and note down the API key. [Example](https://github.com/ion2088/firedust/tree/master/examples).

### 4. Create a Slack App
Create a new Slack app and note down the signing secret and bot token. [Example](https://api.slack.com/apps?new_app).

### 5. Environment Variables
Set up the following environment variables:
- `FIREDUST_API_KEY`: Your Firedust API key.
- `ASSISTANT_NAME`: Name of the AI assistant created with Firedust.
- `SLACK_SIGNING_SECRET`: Signing secret for your Slack app.
- `SLACK_BOT_TOKEN`: Bot token for your Slack app.

### 6. Run the App
```sh
poetry run python -m slackapp start
```

## Features

**Add To Channels:**
Add the assistant to your channels and easily interact with it within a group just by mentioning it in a message. When added to a group, it learns the message history and can recall even very old messages if they are relevant to the query. All conversations are private to a specific channel.

**Direct Messages:**
Send the assistant a direct message in Slack to interact with it. All private conversations with users are kept confidential.

**Train On Your Data:**
The assistant's memory can be enhanced with specialised data that it can recall, if relevant, to answer a specific query. For exmaples how to add your data to the assitant's memory see here: 


## WIP

- [ ] Add a license.
- [ ] Fix the urls in examples.
- [ ] Add commands support.
