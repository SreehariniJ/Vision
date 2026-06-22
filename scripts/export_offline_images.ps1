# Script to download, build, and package all Vision Docker images for offline transfer.
# Run this on your Windows machine with internet access.

Write-Host "=========================================================="
Write-Host " Vision - Offline Docker Image Packager"
Write-Host "=========================================================="
Write-Host "Building and pulling all Docker images (this requires internet)..."

# Build all local images (backend, celery, etc.)
docker compose build

# Pull all remote images (mysql, redis, etc.)
docker compose pull

Write-Host "`nSuccessfully built and pulled all images."
Write-Host "Saving images to a single offline tar file. This may take 10-20 minutes and result in a 10GB+ file..."

# Get all images referenced by the compose file
$images = docker compose config --images
$images_str = $images -join " "

# Save them to a tar file
$output_file = "vision_images.tar"
Invoke-Expression "docker save -o $output_file $images_str"

Write-Host "`n=========================================================="
Write-Host " SUCCESS!"
Write-Host " Created $output_file"
Write-Host " Transfer this file to your offline RHEL VM."
Write-Host "=========================================================="
