#!/bin/bash
# Consultant fallback: start NGAME dashboard if LaunchAgent / Task Scheduler is not used.
# Double-click in Finder (macOS). FRP should use a browser bookmark only — not this script.
cd "$(dirname "$0")"
if [ -f .venv/bin/activate ]; then
  source .venv/bin/activate
fi
cd ngame_ui
exec python3 app-simple.py
