#!/usr/bin/env python3

if __name__ == '__main__':
    import sys

    if len(sys.argv) != 2:
        print('Usage: ./clone_model.py <model>')
        sys.exit(1)

    from TTS.api import TTS
    import builtins
    # Automatically confirm license prompt by returning 'y' for any input call.
    builtins.input = lambda prompt='': 'y'

    TTS(sys.argv[1])
    print("Done")
