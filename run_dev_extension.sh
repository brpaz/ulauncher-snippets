#!/bin/bash
ln -sfn $PWD ~/.local/share/ulauncher/extensions/
VERBOSE=1 ULAUNCHER_WS_API=ws://127.0.0.1:5054/ulauncher-snippets PYTHONPATH=/usr/lib/python3/dist-packages /usr/bin/python3 $PWD/main.py
