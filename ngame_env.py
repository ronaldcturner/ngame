#!/usr/bin/env python3
"""
Load local environment variables from `.env` at the repository root.

Uses python-dotenv when installed (already listed in requirements.txt).
Existing process environment wins unless override=True.
"""

from __future__ import annotations

import os
from pathlib import Path


def repo_root() -> str:
    """Absolute path to the NGAME repo root (directory containing this file)."""
    return str(Path(__file__).resolve().parent)


def load_ngame_dotenv(*, override: bool = False) -> bool:
    """
    Load ``.env`` from the repo root if python-dotenv is available.

    Returns True if dotenv was imported and load_dotenv was invoked (the file may be absent).
    Returns False if python-dotenv is not installed (no error; workflow unchanged).
    """
    try:
        from dotenv import load_dotenv
    except ImportError:
        return False
    path = os.path.join(repo_root(), ".env")
    load_dotenv(path, override=override)
    return True
