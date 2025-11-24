"""
Claude Mac Manager - Comprehensive macOS System Management Toolkit

A safety-first system management tool for macOS with disk space analysis,
cleanup automation, and Claude Code integration.

Author: Vladimir K.S.
License: MIT
"""

__version__ = "0.0.1"
__author__ = "Vladimir K.S."
__license__ = "MIT"

from pathlib import Path

# Package-level constants
PACKAGE_NAME = "claude-mac-manager"
DATA_DIR = Path("/Users/Shared/_claude_mac_manager")
CONFIG_DIR = DATA_DIR / "config"
DATABASE_DIR = DATA_DIR / "data" / "disk"
DATABASE_PATH = DATABASE_DIR / "cache.db"

__all__ = [
    "__version__",
    "__author__",
    "__license__",
    "PACKAGE_NAME",
    "DATA_DIR",
    "CONFIG_DIR",
    "DATABASE_DIR",
    "DATABASE_PATH",
]
