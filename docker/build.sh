#!/bin/bash
set -e

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
IMAGE_TAG="coqui_ros2"

# Build Base image
docker build -t ${IMAGE_TAG} \
  --build-arg UBUNTU_MAJOR=${UBUNTU_MAJOR} \
  --build-arg UBUNTU_MINOR=${UBUNTU_MINOR} \
  --build-arg CUDA_MAJOR=${CUDA_MAJOR} \
  --build-arg CUDA_MINOR=${CUDA_MINOR} \
  --build-arg CUDA_PATCH=${CUDA_PATCH} \
  --build-arg ROS_DISTRO=${ROS_DISTRO} \
  -f $PARENT_DIR/docker/Dockerfile \
  $PARENT_DIR

docker build -t ${IMAGE_TAG} \
  --build-arg BASE_IMAGE=${IMAGE_TAG} \
  -f $PARENT_DIR/docker/Dockerfile \
  $PARENT_DIR
