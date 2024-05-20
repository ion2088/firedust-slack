# AI Slack Assistant

This is a simple implementation of an AI Slack Assistant using Firedust AI. The assistant can be added to your Slack workspace and channels to help you with various tasks. It can answer questions, provide information, and even recall old messages from the channel history. The assistant is built using Firedust AI, a powerful AI platform that enables you to create intelligent conversational agents for your applications.


## Quickstart

### 0. End Game
The quickest way to deploy the assistant on slack is to use Firedust interface deploy capabilities. You can set it up and running in a few minutes by following this example [Firedust AI Quickstarts](https://firedust.ai/quickstarts).

To deploy the assistant on your own server, follow the steps below.

### 1. Prerequisites
- Python 3.10+
- [Poetry](https://python-poetry.org/docs/)

### 2. Install Dependencies
```sh
poetry install
```

### 3. Create an assistant
Create an AI assistant on Firedust AI and note down the API key. You can create an assistant by following the instructions [here](https://firedust.ai/docs/quickstart).

### 4. Create a Slack App
Create a new Slack app and note down the signing secret and bot token. You can create a new app by following the instructions [here](https://api.slack.com/apps?new_app).

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