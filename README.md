# Coqui TTS ROS2

## Overview
This package implements a ROS2 node for text-to-speech conversion using the [Coqui TTS API](https://github.com/coqui-ai/TTS). The node accepts TTS goals via an action interface, synthesizes audio using a specified TTS model, and plays the generated audio with `aplay`.

## Features
- **Text-to-Speech Conversion:** Converts text to speech using Coqui TTS.
- **Device Flexibility:** Supports running on CUDA (GPU) or CPU.

## Dependencies
- Docker
- Docker Nvidia
- Alsa (aplay)

## Build
```bash
docker/build.sh
```

## Usage
Change ALSA_CARD in docker/compose.yaml, use aplay -l to find the card name.
```bash
docker compose -f docker/compose.yaml up
```