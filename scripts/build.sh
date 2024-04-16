#!/bin/bash

APP="firedust-slack"

# Set env variables
IMAGE=$(aws ecr describe-repositories --repository-names "$APP" --query 'repositories[0].repositoryUri' --output text)

# Retrieve spells
docker_wizard=$(aws secretsmanager get-secret-value --secret-id docker/wizard --query SecretString --output text)
docker_spell=$(aws secretsmanager get-secret-value --secret-id docker/spell --query SecretString --output text)

# Login to docker
docker login -u="${docker_wizard}" -p="${docker_spell}"

# Build and push docker image
docker build --target slackapp-prod . -t "$IMAGE":latest
aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin "$IMAGE"
docker push "$IMAGE":latest

