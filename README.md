# Coqui TTS ROS2
A ROS 2 package that provides a ROS 2 interface for the [Coqui TTS](https://github.com/coqui-ai/TTS) text-to-speech engine.  
It supports multilingual, multi-speaker synthesis, speaker adaptation, emotions, and adjustable playback timing.  
The node exposes a TTS action server and publishes the TTS state.

## Overview

- **TTS Action:**
  - **Goal:**
    - `text` (string): Text to synthesize.
    - `speaker` (string): Optional speaker ID.
    - `language` (string): Optional language identifier.
    - `speaker_wav` (string): Path(s) to WAV file(s) for speaker adaptation. Separate multiple paths with `;`.
    - `emotion` (string): Optional emotion label (depends on model).
    - `speed` (float32): Speaking speed (1.0 = default). 0.0 uses default.
    - `dont_split_sentences` (bool): If true, disables sentence splitting.
    - `wait_before_speaking` (float32): Seconds to wait before playback starts.
  - **Feedback:**
    - `stage` (enum): One of `STARTED`, `GENERATED_AUDIO`, `WAIT_DONE`, `AUDIO_PLAYED`
  - **Result:**
    - `success` (bool): True if synthesis and playback were successful.
    - `message` (string): Status or error message.

- **TTS State Publisher:**  
  Publishes a `std_msgs/Bool` on `~/tts_state`.  
  - `True`: Synthesis or playback in progress.  
  - `False`: Idle.

## Parameters

- **model**:  
  The name or path of the Coqui TTS model to load.  
  _Example:_ `tts_models/en/ljspeech/glow-tts`

- **device**:  
  Device used for inference. Must be `cuda` or `cpu`.  
  _Example:_ `cuda`

## Installation

1. **Dependencies (host):**
   - Docker + Docker Compose
   - ALSA with aplay

2. **Build with Docker:**
   ```bash
   docker/build.sh
   ```

## Usage

Change ALSA_CARD in docker/compose.yaml, use aplay -l to find the card name.
```bash
docker compose -f docker/compose.yaml up
```

## Notes

- If using CUDA, ensure `nvidia-docker` is installed and GPU access is enabled in your container.
- If `speaker_wav` is used, it must point to WAV files on the container filesystem. (Use volume mounts.)

## Tested Models

- `tts_models/en/ljspeech/glow-tts`
- `tts_models/multilingual/multi-dataset/xtts_v2`