#!/usr/bin/env bash
IMAGE_NAME=recipe-tracker:local
docker build -t $IMAGE_NAME .
docker run --rm -p 5000:5000 -v "$(pwd)/data":/app/data $IMAGE_NAME
