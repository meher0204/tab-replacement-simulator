#!/bin/bash
# Double-click this file on macOS to launch the desktop simulator.
cd "$(dirname "$0")"
if [ -d ".venv" ]; then
  PYTHON=".venv/bin/python"
else
  PYTHON="python3"
fi
"$PYTHON" gui.py
