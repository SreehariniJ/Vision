#!/usr/bin/env bash
# Script to load offline Docker images on the RHEL VM.

set -euo pipefail

echo "=========================================================="
echo " Vision - Offline Docker Image Loader"
echo "=========================================================="

IMAGE_FILE="vision_images.tar"

if [[ ! -f "$IMAGE_FILE" ]]; then
    echo "ERROR: Could not find $IMAGE_FILE in the current directory."
    echo "Please transfer vision_images.tar from your internet-connected machine."
    exit 1
fi

echo "Loading images into Docker. This may take a few minutes..."
docker load -i "$IMAGE_FILE"

echo ""
echo "Images loaded successfully!"
echo "You can now run: make setup && make up"
