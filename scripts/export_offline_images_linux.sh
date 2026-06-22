#!/usr/bin/env bash
# Script to download, build, and package all Vision Docker images for offline transfer.
# Run this on your INTERNET-CONNECTED RHEL machine.

set -euo pipefail

echo "=========================================================="
echo " Vision - Offline Docker Image Packager (Linux)"
echo "=========================================================="
echo "Building and pulling all Docker images (this requires internet)..."

# Build all local images (backend, celery, etc.)
docker compose build

# Pull all remote images (mysql, redis, etc.)
docker compose pull

echo -e "\nSuccessfully built and pulled all images."
echo "Saving images to a single offline tar file. This may take 10-20 minutes and result in a 15GB+ file..."

# Get all images referenced by the compose file
IMAGES=$(docker compose config --images)

# Save them to a tar file
OUTPUT_FILE="vision_images.tar"
docker save -o "$OUTPUT_FILE" $IMAGES

echo -e "\n=========================================================="
echo " SUCCESS!"
echo " Created $OUTPUT_FILE"
echo " Transfer this file to your OFFLINE RHEL VM."
echo "=========================================================="
