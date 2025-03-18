#!/usr/bin/env python3

from TTS.utils.manage import ModelManager
from pathlib import Path

MODEL_FILE = "/root/TTS/TTS/.models.json"

import builtins
# Automatically confirm license prompt by returning 'y' for any input call.
builtins.input = lambda prompt='': 'y'

if __name__ == '__main__':
    import sys

    if len(sys.argv) != 2:
        print('Usage: ./clone_model.py <model>')
        sys.exit(1)

    model_name = sys.argv[1]
    manager =  ModelManager(models_file=MODEL_FILE, progress_bar=True, verbose=False)
    print(f"Downloading {model_name}")
    model_path, config_path, model_item = manager.download_model(model_name)
    if model_item.get("default_vocoder") is None:
        print("Done")
        exit(0)

    print(f"Downloading {model_item['default_vocoder']}")
    vocoder_path, vocoder_config_path, _ = manager.download_model(model_item["default_vocoder"])
    print("Done")
