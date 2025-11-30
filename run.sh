#!/usr/bin/env bash

IMAGE_NAME=recipe-tracker:latest

# Build the container
docker build -t $IMAGE_NAME .

# Run the container with volume mounts
docker run --rm \
    -p 5000:5000 \
    -v "$(pwd)/data":/app/data \
    -v "$(pwd)/uploads":/app/uploads \
    $IMAGE_NAME
