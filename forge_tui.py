#!/usr/bin/env python3
"""Ancien point d'entree TUI. Le menu est maintenant un script bash SSH."""
import os
from pathlib import Path

os.execv("/bin/bash", ["bash", str(Path(__file__).resolve().parent / "setup-grok-forge")])
