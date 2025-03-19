#!/bin/bash
set -e

# License confirmation prompt
echo "> You must confirm the following:"
echo "| > \"I have purchased a commercial license from Coqui: licensing@coqui.ai\""
echo "| > \"Otherwise, I agree to the terms of the non-commercial CPML: https://coqui.ai/cpml\" - [y/n]"
read -r CONFIRMATION
if [ "$CONFIRMATION" != "y" ]; then
    echo "License not confirmed, exiting."
    exit 1
fi

# Get the directory of the script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"

# Local variables
UBUNTU_MAJOR=22
UBUNTU_MINOR=04
CUDA_MAJOR=12
CUDA_MINOR=6
CUDA_PATCH=3
ROS_DISTRO=humble
IMAGE_TAG="coqui_tts_ros2"
DOWNLOAD_MODELS=true

# Build Base image
docker build -t ${IMAGE_TAG} --target base \
  --build-arg UBUNTU_MAJOR=${UBUNTU_MAJOR} \
  --build-arg UBUNTU_MINOR=${UBUNTU_MINOR} \
  --build-arg CUDA_MAJOR=${CUDA_MAJOR} \
  --build-arg CUDA_MINOR=${CUDA_MINOR} \
  --build-arg CUDA_PATCH=${CUDA_PATCH} \
  --build-arg ROS_DISTRO=${ROS_DISTRO} \
  -f $PARENT_DIR/docker/Dockerfile \
  $PARENT_DIR

#Build TTS
docker build -t ${IMAGE_TAG} --target build_tts \
  --build-arg BASE_IMAGE=${IMAGE_TAG} \
  -f $PARENT_DIR/docker/Dockerfile \
  $PARENT_DIR

if $DOWNLOAD_MODELS; then
  docker build -t ${IMAGE_TAG} --target download_models \
    --build-arg BASE_IMAGE=${IMAGE_TAG} \
    -f $PARENT_DIR/docker/Dockerfile \
    $PARENT_DIR
fi

#Build  ros wrapper
docker build -t ${IMAGE_TAG} --target build_ros \
  --build-arg BASE_IMAGE=${IMAGE_TAG} \
  -f $PARENT_DIR/docker/Dockerfile \
  $PARENT_DIR