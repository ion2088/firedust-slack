# Base image for both development and production
FROM python:3 AS base

WORKDIR /workspaces/slackapp

# Set environment variables
ENV POETRY_VERSION=1.6 \
    APP="slackapp" \
    PYTHONPATH="${PYTHONPATH}:/workspaces/slackapp/src" \
    PATH="$PATH:/root/.poetry/bin"

# Install Poetry
RUN pip install poetry==$POETRY_VERSION

# Copy only the necessary files for installing dependencies
COPY pyproject.toml poetry.lock ./

# --------------------------------------------------
# Development image
# --------------------------------------------------
FROM base AS slackapp-dev

ENV PATH="/home/vscode/local/bin:$PATH" \
    ENV="local"

# Install development dependencies
RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/* && \
    poetry install

# Git configuration
RUN git config --global --add safe.directory /workspaces/slackapp && \
    git config --global user.email "$DEV_EMAIL" && \
    git config --global user.name "$DEV_NAME"

COPY . .

# --------------------------------------------------
# Production image
# --------------------------------------------------
FROM base AS slackapp-prod

ENV ENV="prod"

# Install production dependencies only
RUN poetry install --no-dev

COPY . .
COPY src/slackapp slackapp/

EXPOSE 8080

CMD ["poetry", "run", "uvicorn", "slackapp.api.main:slackapp", "--host", "0.0.0.0", "--port", "8080"]
