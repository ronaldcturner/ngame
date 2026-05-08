#!/usr/bin/env python3
"""
Canonical production entrypoint for NGAME Phase I data extraction.

Run from repo root (recommended):
  .venv/bin/python run_data_extraction.py

Or from any directory (script forces cwd to repo root):
  /path/to/NGAME-POC/.venv/bin/python /path/to/NGAME-POC/run_data_extraction.py
"""

import os
import sys

_REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
if os.getcwd() != _REPO_ROOT:
    os.chdir(_REPO_ROOT)

from ngame_data_extraction_agent import main

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
